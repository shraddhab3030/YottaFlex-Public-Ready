"""Cohesive local package build/export/restore/verify CLI; no publication actions."""

from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import tempfile
from time import perf_counter

from .anomalies import build_bundle
from .anomaly_evaluation import evaluate
from .anomaly_truth import read_csv
from .canonical import dataset_digest,stable_json,table_names
from .detector import detect
from .evaluation_checks import validate_evaluations
from .exports import (compare_records,export_database,file_info,new_directory,restore_database,write_json)
from .generate import generate_database
from .generation_config import GenerationConfig
from .observations import reference,load_document
from .privacy import scan_files,synthetic_identity_check

ROOT=Path(__file__).resolve().parents[2]
CORE=('Requisition','HiringManager','Candidate','Application','SkillRequirement','InterviewPanel','Availability','Interview','Scorecard','Offer','Approval')


def validation_summary(connection,config):
    domain=validate_evaluations(connection,config,2000 if config.profile=='full' else 40)
    checks={row['check']:row['violations'] for row in domain['checks']}
    enum_errors=natural_errors=0
    for table in table_names(connection):
        names={row['name'] for row in connection.execute(f'PRAGMA table_info("{table}")')}
        ddl=connection.execute("SELECT sql FROM sqlite_schema WHERE type='table' AND name=?",(table,)).fetchone()[0]
        for name,values in re.findall(r'\b(\w+)\s+IN\s*\(([^()]+)\)',ddl):
            if name not in names:continue
            tokens=[token.strip() for token in values.split(',')]
            if not all(re.fullmatch(r"'(?:[^']|'')*'|-?[0-9]+",token) for token in tokens):continue
            allowed=[token[1:-1].replace("''","'") if token.startswith("'") else int(token) for token in tokens]
            enum_errors+=connection.execute(f'SELECT COUNT(*) FROM "{table}" WHERE "{name}" IS NOT NULL AND "{name}" NOT IN ('+','.join('?' for _ in allowed)+')',allowed).fetchone()[0]
        for index in connection.execute(f'PRAGMA index_list("{table}")'):
            if not index['unique']:continue
            columns=[row['name'] for row in connection.execute(f'PRAGMA index_info("{index["name"]}")')]
            if any(name is None for name in columns):continue
            definition=connection.execute('SELECT sql FROM sqlite_schema WHERE type=\'index\' AND name=?',(index['name'],)).fetchone()
            sql=definition[0] if definition is not None else None
            where=' WHERE '+sql.split(' WHERE ',1)[1] if sql and ' WHERE ' in sql else ''
            group=','.join('"'+name+'"' for name in columns)
            natural_errors+=connection.execute(f'SELECT COUNT(*) FROM (SELECT {group} FROM "{table}"'+where+f' GROUP BY {group} HAVING COUNT(*)>1)').fetchone()[0]
    categories={'foreign_key_violations':len(list(connection.execute('PRAGMA foreign_key_check'))),
        'integrity_errors':sum(row[0]!='ok' for row in connection.execute('PRAGMA integrity_check')),
        'primary_key_duplicates':checks['primary_keys'],'natural_or_unique_key_duplicates':natural_errors,'invalid_enums':enum_errors,
        'invalid_chronology':sum(value for key,value in checks.items() if any(word in key for word in ('chronology','time_bounds','event_time'))),
        'illegal_stage_transitions':checks['legal_transitions'],'interviewer_conflicts':checks['capacity_interviewer_overlaps'],
        'candidate_conflicts':checks['capacity_candidate_overlaps'],
        'review_gate_violations':sum(value for key,value in checks.items() if key.startswith('review_') or key=='advanced_stage_support'),
        'score_arithmetic_errors':checks['independent_score_arithmetic'],
        'offer_band_violations':checks['offer_band_currency_amount']+checks['offer_band_snapshot'],
        'approval_history_errors':sum(value for key,value in checks.items() if 'approval' in key or key.startswith('history_')),
        'ground_truth_leakage':checks['workflow_truth_leakage']+checks['evaluation_truth_leakage']}
    return {'classification':'valid_canonical_baseline' if domain['passed'] and not any(categories.values()) else 'unexpected_validation_failure',
        'passed':domain['passed'] and not any(categories.values()),'categories':categories,'domain':domain,'canonical':dataset_digest(connection),
        'category_note':'Categories aggregate measured checks and may overlap; all detailed domain checks are retained.'}


def verify_roundtrips(database,baseline_directory,work):
    results={};timing={};restored={}
    for kind in ('csv','json','sql'):
        target=Path(work)/(kind+'.sqlite3')
        result,measured=restore_database(baseline_directory,kind,target)
        with reference(database) as source,reference(target) as actual:
            comparison=compare_records(source,actual)
        if not comparison['passed']:raise ValueError('Round-trip first difference: '+stable_json(comparison['first_difference']))
        result['row_comparison']=comparison;results[kind]=result;timing[kind]=measured;restored[kind]=target
    return results,timing,restored


def _verify_anomalies(database,directory):
    directory=Path(directory)
    expected_baseline=json.loads((directory/'reports/clean-validation.json').read_text())['baseline_canonical']
    with reference(database) as source:
        if dataset_digest(source)!=expected_baseline:raise ValueError('Anomaly package baseline reference mismatch')
    observed=detect(database,load_document(directory/'input/observations.json'))
    expected=json.loads((directory/'reports/findings.json').read_text())
    if observed!=expected:raise ValueError('Packaged detector findings differ from business inputs')
    clean=detect(database)
    labels=json.loads((directory/'truth/ground_truth.json').read_text())
    if read_csv(directory/'truth/ground_truth.csv')!=labels:raise ValueError('Packaged truth CSV/JSON differ')
    measured=evaluate(observed['findings'],labels,clean_findings=clean['findings'])
    if measured!=json.loads((directory/'reports/evaluation.json').read_text()):raise ValueError('Packaged metrics differ from findings/truth')
    return {'baseline_classification':'valid_canonical_baseline','observed_structure':observed['structure'],
        'observation_classification':'structurally_valid_intentional_semantic_violations','semantic_valid':observed['semantic_valid'],
        'expected_findings':len(labels),'actual_findings':len(observed['findings']),'clean_findings':len(clean['findings']),
        'unexpected_findings':measured['FP'],'missed_expected_findings':measured['FN'],'evaluation':measured}


def tool_fingerprints():
    return {str(path.relative_to(ROOT)):file_info(path)['sha256'] for path in sorted((ROOT/'src/yottaflex').glob('*.py'))}


def source_revision():
    """Optional Git provenance; source archives must not inherit an unrelated repo."""
    try:
        top=subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
        if Path(top).resolve()!=ROOT.resolve():return None
        return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):
        return None


def build_package(directory,config):
    started=perf_counter();timing={}
    with tempfile.TemporaryDirectory(prefix='yottaflex-package-') as workname,new_directory(directory) as scratch:
        work=Path(workname);database=work/'canonical.sqlite3'
        generated=generate_database(database,config,phase='evaluations');timing['baseline_generation_seconds']=generated.elapsed_seconds
        catalog,export_timing=export_database(database,scratch/'baseline',config);timing.update(export_timing)
        imports,import_timing,restored=verify_roundtrips(database,scratch/'baseline',work)
        timing['imports']=import_timing;write_json(scratch/'baseline/round-trip-verification.json',imports)
        validation_started=perf_counter()
        with reference(database) as source:
            validation=validation_summary(source,config);identities=synthetic_identity_check(source)
            dependencies={table:sorted({row['table'] for row in source.execute(f'PRAGMA foreign_key_list("{table}")')}) for table in table_names(source)}
        if not validation['passed'] or not identities['passed']:raise ValueError('Canonical domain/provenance validation failed')
        write_json(scratch/'baseline/validation-summary.json',validation);timing['validation_seconds']=perf_counter()-validation_started
        anomaly_started=perf_counter()
        bundle,_=build_bundle(database,work/'phase06',config.profile,seed=config.seed,baseline_seed=config.seed)
        shutil.copytree(work/'phase06/input',scratch/'anomalies/input',ignore=shutil.ignore_patterns('*.sqlite3'))
        shutil.copytree(work/'phase06/truth',scratch/'anomalies/truth');shutil.copytree(work/'phase06/reports',scratch/'anomalies/reports')
        verification=_verify_anomalies(restored['json'],scratch/'anomalies')
        if bundle['baseline_canonical']!=catalog['canonical']:raise ValueError('Packaged anomaly baseline link mismatch')
        write_json(scratch/'anomalies/reports/package-verification.json',verification)
        timing['anomaly_evaluation_seconds']=perf_counter()-anomaly_started
        shutil.copyfile(ROOT/'docs/data-dictionary.md',scratch/'data-dictionary.md')
        (scratch/'README.md').write_text('''# Reviewed synthetic dataset package

All candidate identities and recruitment records are synthetic. No real candidate
records, scraped profiles, resumes, confidential data or external personal datasets.
Baseline exports are the valid canonical Phase05 data; anomalies are separate.

From the repository root with Python3.14.5 and no dependency downloads:

    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/verify-artifacts
    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format json --database output/restored.sqlite3
    PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/restored.sqlite3 --observations artifacts/anomalies/input/observations.json

Use new restore/work paths. The verify command restores all formats and reproduces
anomaly findings/metrics from business inputs before reading truth for scoring.
CSV null is backslash-N; leading text backslashes double; empty string stays empty.
JSON text columns remain strings; INTEGER booleans remain0/1. Schema-column/PK
order is stable. Gzip files are lossless with fixed header, transparently read by
CLI; large files are compressed to keep this repository modest. SQL: execute
sql/schema.sql in an empty DB, then decompressed seed.sql (possibly .gz), without
running the initializer first. Both FK and all triggers remain enabled. Never
execute arbitrary untrusted SQL; hashes prove integrity, not publisher authenticity.

See docs/phase07/export-and-reproducibility-design.md for exact encodings/policies,
manifest exclusions, runtime requirements and limitations. Manifest hashes exclude
manifest.json itself. Reproduction evidence is in docs/phase07/ outside this
inventory to avoid circular/self-referential hashes. No publication is authorized.
''',encoding='utf-8')
        provenance={'synthetic_only':identities,'external_datasets':[],'vendored_dependencies':[],
            'runtime_provenance':'Uses the locally supplied CPython standard library and its SQLite module; no third-party project code or dataset is bundled.',
            'source_requirements_reference':'docs/phase01/sources.json (identity/provenance only; private assignment files excluded)',
            'AI_disclosure':'Codex-generated implementation and AI-run verification; independent human review/ownership still pending.'}
        write_json(scratch/'provenance.json',provenance)
        privacy=scan_files(scratch)
        if not privacy['passed']:raise ValueError('Generated artifact privacy review failed: '+stable_json(privacy['findings']))
        write_json(scratch/'privacy-scan.json',privacy)
        inventory={str(path.relative_to(scratch)):file_info(path) for path in sorted(scratch.rglob('*')) if path.is_file()}
        revision=source_revision()
        manifest={'manifest_version':1,'profile':config.profile,'generator_git_commit':revision,'exporter_version':1,
            'generator_source_sha256':hashlib.sha256(stable_json(tool_fingerprints()).encode()).hexdigest(),
            'tool_source_sha256':tool_fingerprints(),'seed':config.seed,'logical_time_origin':config.logical_origin,
            'configuration':config.as_dict(),'configuration_sha256':hashlib.sha256(stable_json(config.as_dict()).encode()).hexdigest(),
            'schema_version':catalog['schema_version'],'schema_sha256':catalog['schema_sha256'],
            'runtime':{'python_requirement':'==3.14.5','sqlite_minimum':'3.38.0','verified_sqlite':sqlite3.sqlite_version,'dependencies':[]},
            'provenance':provenance,'core_entities':list(CORE),'dependencies':dependencies,
            'canonical':catalog['canonical'],'formats':['csv','json','sql'],
            'validation_references':['baseline/validation-summary.json','baseline/round-trip-verification.json','anomalies/reports/package-verification.json'],
            'anomaly_baseline_sha256':bundle['baseline_canonical']['sha256'],'anomaly_references':{'input':'anomalies/input/observations.json','truth':['anomalies/truth/ground_truth.csv','anomalies/truth/ground_truth.json'],'findings':'anomalies/reports/findings.json','evaluation':'anomalies/reports/evaluation.json'},
            'reproducibility_evidence_reference':'docs/phase07/reproducibility-evidence.json','file_inventory':inventory,
            'hash_policy':'SHA256 exact file bytes; inventory excludes manifest.json itself and external replay diagnostics. Canonical hashes cover logical ordered records, never SQLite binary files.'}
        write_json(scratch/'manifest.json',manifest)
    timing['total_seconds']=perf_counter()-started
    return manifest,timing


def verify_package(directory,work):
    started=perf_counter();directory=Path(directory);work=Path(work)
    manifest=json.loads((directory/'manifest.json').read_text())
    if manifest['manifest_version']!=1 or manifest['configuration_sha256']!=hashlib.sha256(stable_json(manifest['configuration']).encode()).hexdigest():raise ValueError('Manifest version/configuration fingerprint mismatch')
    if manifest['tool_source_sha256']!=tool_fingerprints():raise ValueError('Package tool provenance differs from this code version')
    if manifest.get('generator_source_sha256')!=hashlib.sha256(stable_json(tool_fingerprints()).encode()).hexdigest():raise ValueError('Generator source fingerprint mismatch')
    catalog=json.loads((directory/'baseline/catalog.json').read_text())
    if catalog['canonical']!=manifest['canonical'] or catalog['schema_sha256']!=manifest['schema_sha256']:raise ValueError('Manifest/catalog canonical or schema mismatch')
    actual_files={str(path.relative_to(directory)) for path in directory.rglob('*') if path.is_file()}
    if actual_files!=set(manifest['file_inventory'])|{'manifest.json'}:raise ValueError('Artifact inventory differs from manifest')
    for name,expected in manifest['file_inventory'].items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or (directory/path).is_symlink() or file_info(directory/path)!=expected:raise ValueError(f'Manifest checksum/path mismatch: {name}')
    if not scan_files(directory)['passed']:raise ValueError('Package privacy check failed')
    with new_directory(work) as scratch:
        results={};timing={}
        for kind in ('csv','json','sql'):results[kind],timing[kind]=restore_database(directory/'baseline',kind,scratch/(kind+'.sqlite3'))
        with reference(scratch/'csv.sqlite3') as left:
            for kind in ('json','sql'):
                with reference(scratch/(kind+'.sqlite3')) as right:
                    comparison=compare_records(left,right)
                if not comparison['passed']:raise ValueError('Cross-format difference: '+stable_json(comparison['first_difference']))
        anomalies=_verify_anomalies(scratch/'json.sqlite3',directory/'anomalies')
        for result in results.values():
            if result['canonical']!=manifest['canonical']:raise ValueError('Restored canonical data differs from manifest')
        report={'passed':True,'formats':results,'anomalies':anomalies,'manifest_files_verified':len(manifest['file_inventory'])}
        write_json(scratch/'verification.json',report)
    return report,{'total_seconds':perf_counter()-started,'imports':timing}


def main():
    import argparse
    import sys
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    build=commands.add_parser('build');build.add_argument('--directory',type=Path,required=True);build.add_argument('--profile',choices=('starter','full'),default='full');build.add_argument('--seed',type=int,default=20261022)
    export=commands.add_parser('export');export.add_argument('--baseline',type=Path,required=True);export.add_argument('--directory',type=Path,required=True);export.add_argument('--profile',choices=('starter','full'),required=True);export.add_argument('--seed',type=int,default=20261022)
    restore=commands.add_parser('restore');restore.add_argument('--directory',type=Path,required=True);restore.add_argument('--format',choices=('csv','json','sql'),required=True);restore.add_argument('--database',type=Path,required=True)
    verify=commands.add_parser('verify');verify.add_argument('--directory',type=Path,required=True);verify.add_argument('--work',type=Path,required=True)
    evaluator=commands.add_parser('evaluate');evaluator.add_argument('--directory',type=Path,required=True);evaluator.add_argument('--database',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=='build':result,timing=build_package(args.directory,GenerationConfig(args.profile,args.seed))
        elif args.command=='export':result,timing=export_database(args.baseline,args.directory,GenerationConfig(args.profile,args.seed))
        elif args.command=='restore':result,timing=restore_database(args.directory,args.format,args.database)
        elif args.command=='verify':result,timing=verify_package(args.directory,args.work)
        else:
            started=perf_counter();result=_verify_anomalies(args.database,args.directory);timing={'evaluation_seconds':perf_counter()-started}
    except (ValueError,OSError,sqlite3.Error,KeyError,TypeError,OverflowError) as error:
        print('Deliverable operation failed: '+str(error),file=sys.stderr);return 1
    print(json.dumps({'result':result,'timing':timing},sort_keys=True,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
