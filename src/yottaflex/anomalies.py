"""Dedicated Phase06 experiment command; clean generator defaults stay untouched."""

from collections import Counter
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from time import perf_counter

from .anomaly_evaluation import evaluate
from .anomaly_injection import inject
from .anomaly_truth import write_truth,read_csv
from .canonical import dataset_digest,stable_json
from .db import connect
from .detector import detect
from .evaluation_checks import validate_evaluations
from .generation_config import GenerationConfig
from .observations import reference,projected


def _write(path,data):
    path.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')


def build_bundle(baseline, directory, profile, *, seed=20261022, baseline_seed=20261022, cases=None):
    started=perf_counter(); config=GenerationConfig(profile,baseline_seed)
    cases=cases if cases is not None else (5 if profile=='full' else 1)
    directory=Path(directory)
    if directory.exists() or directory.is_symlink():raise FileExistsError('Refusing existing experiment directory')
    directory.parent.mkdir(parents=True,exist_ok=True)
    lock=directory.parent/('.'+directory.name+'.publication-lock')
    descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(descriptor)
    scratch=None
    try:
        if directory.exists() or directory.is_symlink():raise FileExistsError('Experiment output already claimed')
        scratch=Path(tempfile.mkdtemp(prefix='.phase06-',dir=directory.parent))
        inputs=scratch/'input';inputs.mkdir(); reports=scratch/'reports';reports.mkdir()
        validation_started=perf_counter()
        with reference(baseline) as source:
            before=dataset_digest(source)
            validation=validate_evaluations(source,config,2000 if profile=='full' else 40)
            if not validation['passed']:raise ValueError('Source baseline must pass unchanged Phase05 domain validation')
            with closing(connect(inputs/'baseline.sqlite3')) as destination:source.backup(destination)
            after=dataset_digest(source)
            if before!=after:raise ValueError('Input baseline changed during verified copy')
        validation_seconds=perf_counter()-validation_started
        database=inputs/'baseline.sqlite3'
        injection_started=perf_counter()
        with reference(database) as source:
            if dataset_digest(source)!=before:raise ValueError('Canonical baseline copy mismatch')
            document,truth,controls=inject(source,seed,cases)
            with projected(source,document) as (view,structure):
                anomalous_digest=dataset_digest(view)
        injection_seconds=perf_counter()-injection_started
        _write(inputs/'observations.json',document)
        # Detector completes before truth is serialized, then only evaluator reads labels.
        detection_started=perf_counter()
        clean=detect(database)
        anomalous=detect(database,document)
        detection_seconds=perf_counter()-detection_started
        if clean['findings']:raise ValueError('Unexpected clean-baseline findings; investigate before publication')
        write_truth(scratch/'truth',truth)
        reloaded=json.loads((scratch/'truth/ground_truth.json').read_text())
        if read_csv(scratch/'truth/ground_truth.csv')!=reloaded:raise ValueError('CSV/JSON truth mismatch')
        evaluation=evaluate(anomalous['findings'],reloaded,clean_findings=clean['findings'])
        # Metrics are retained honestly, including FP/FN; coverage is not a fake PASS.
        if set(row['rule_id'] for row in truth)!={'R01','R02','R03','R04','R05'}:
            raise ValueError('Incomplete mandatory intervention coverage')
        _write(reports/'clean-validation.json',{'baseline_canonical':before,'phase05_domain':validation,'detection':clean})
        _write(reports/'observation-structure.json',structure)
        _write(reports/'findings.json',anomalous)
        _write(reports/'evaluation.json',evaluation)
        _write(reports/'controls.json',controls)
        with reference(baseline) as source:
            if dataset_digest(source)!=before:raise ValueError('Source baseline was mutated')
        hashes={str(path.relative_to(scratch)):hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(scratch.rglob('*')) if path.is_file() and path.suffix!='.sqlite3'}
        observations_sha=hashes['input/observations.json']
        summary={'profile':profile,'baseline_seed':baseline_seed,'anomaly_seed':seed,'interventions_per_rule':cases,
            'baseline_canonical':before,'anomalous_projection_canonical':anomalous_digest,
            'canonical_input_sha256':hashlib.sha256(stable_json({'baseline':before['sha256'],'observations':observations_sha}).encode()).hexdigest(),
            'source_preserved':True,'structure':structure,'clean_findings':len(clean['findings']),
            'semantic_valid':anomalous['semantic_valid'],'findings_by_rule':anomalous['counts_by_rule'],
            'truth_by_type':dict(sorted(Counter(row['issue_type'] for row in truth).items())),
            'evaluation':evaluation,'file_sha256':hashes,'controls':controls}
        _write(reports/'experiment.json',summary)
        database.chmod(0o444)
        if directory.exists() or directory.is_symlink():raise FileExistsError('Experiment destination appeared during generation')
        # Same-host cooperating writers serialize via exclusive publication lock.
        os.rename(scratch,directory);scratch=None
    finally:
        if scratch is not None:shutil.rmtree(scratch)
        lock.unlink()
    return summary,{'total_seconds':perf_counter()-started,'baseline_validation_copy_seconds':validation_seconds,
        'injection_structure_hash_seconds':injection_seconds,'detection_seconds':detection_seconds}


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--profile',choices=('starter','full'),required=True)
    parser.add_argument('--seed',type=int,default=20261022)
    parser.add_argument('--baseline-seed',type=int,default=20261022)
    parser.add_argument('--cases',type=int)
    args=parser.parse_args()
    summary,timing=build_bundle(args.baseline,args.directory,args.profile,seed=args.seed,baseline_seed=args.baseline_seed,cases=args.cases)
    print(json.dumps({'summary':summary,'timing':timing},sort_keys=True,indent=2))


if __name__=='__main__':main()
