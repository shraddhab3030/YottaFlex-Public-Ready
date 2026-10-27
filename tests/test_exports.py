"""Independent codec, import, package, privacy and corruption regressions."""
from contextlib import closing
from copy import deepcopy
import csv
import gzip
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from yottaflex.canonical import dataset_digest,ordered_records,table_names
from yottaflex.db import connect,initialize
from yottaflex.deliverables import build_package,verify_package,validation_summary
from yottaflex.evaluation_checks import validate_evaluations
from yottaflex.exports import (csv_cell,parse_csv_cell,sql_value,export_database,restore_database,
    compare_records,file_info,text_input,import_order,compress_large,write_json)
from yottaflex.generate import generate_database
from yottaflex.generation_config import GenerationConfig
from yottaflex.observations import reference
from yottaflex.privacy import scan_files,synthetic_identity_check


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace=tempfile.TemporaryDirectory(prefix='yottaflex-exports-');cls.directory=Path(cls.workspace.name)
        cls.database=cls.directory/'source.sqlite3';cls.generated=generate_database(cls.database,GenerationConfig(),phase='evaluations')
        cls.exports=cls.directory/'exports';cls.catalogue,_=export_database(cls.database,cls.exports,GenerationConfig())
        cls.restored={}
        for kind in ('csv','json','sql'):
            target=cls.directory/(kind+'.sqlite3');result,_=restore_database(cls.exports,kind,target)
            cls.restored[kind]=(target,result)

    @classmethod
    def tearDownClass(cls):cls.workspace.cleanup()

    def test_all24_tables_csv_json_headers_schema_column_order_and_pk_order(self):
        self.assertEqual(len(self.catalogue['tables']),24)
        with reference(self.database) as source:
            for table,info in self.catalogue['tables'].items():
                names=[row['name'] for row in source.execute(f'PRAGMA table_info("{table}")')]
                with text_input(self.exports/info['csv']['path']) as stream:
                    rows=list(csv.reader(stream));self.assertEqual(rows[0],names)
                    decoded=[tuple(parse_csv_cell(value,column['type']) for value,column in zip(row,info['columns'])) for row in rows[1:]]
                original=[tuple(row) for row in ordered_records(source,table)]
                self.assertEqual(decoded,original)
                with text_input(self.exports/info['json']['path']) as stream:document=json.load(stream)
                self.assertEqual(document['columns'],names)
                self.assertEqual([tuple(row[name] for name in names) for row in document['rows']],original)

    def test_null_empty_literal_backslash_and_unicode_csv_escaping(self):
        values=[None,'','\\N','\\literal','雪🙂',"quote' and \"comma,",'line\nnext','only\rCR','CRLF\r\nnext','\x00']
        stream=io.StringIO(newline='');csv.writer(stream,lineterminator='\n',quoting=csv.QUOTE_ALL).writerow([csv_cell(value) for value in values])
        stream.seek(0);encoded=next(csv.reader(stream));self.assertEqual([parse_csv_cell(v,'TEXT') for v in encoded],values)
        self.assertNotEqual(csv_cell(None),csv_cell(''));self.assertNotEqual(csv_cell(None),csv_cell('\\N'))

    def test_exact_int64_and_json_null_integer_types(self):
        for value in (0,1,9007199254740993,9223372036854775807,-9223372036854775808):
            self.assertEqual(parse_csv_cell(csv_cell(value),'INTEGER'),value)
            self.assertIs(type(json.loads(json.dumps({'v':value}))['v']),int)
            with closing(sqlite3.connect(':memory:')) as db:self.assertEqual(db.execute('SELECT '+sql_value(value)).fetchone()[0],value)
        self.assertIsNone(parse_csv_cell(csv_cell(None),'INTEGER'))
        for value in ('+1','01','1.0',' 1','1e3'):
            with self.assertRaises(ValueError):parse_csv_cell(value,'INTEGER')

    def test_sql_escaping_unicode_nul_quotes_newlines_and_null(self):
        for value in (None,"O'Reilly",'雪🙂\r\nsecond; -- text','A\x00B','\\N',''):
            with closing(sqlite3.connect(':memory:')) as db:self.assertEqual(db.execute('SELECT '+sql_value(value)).fetchone()[0],value)

    def test_json_text_snapshot_not_parsed_or_reformatted(self):
        table='ScorecardEvent'
        with text_input(self.exports/self.catalogue['tables'][table]['json']['path']) as stream:rows=json.load(stream)['rows']
        self.assertIsInstance(rows[0]['snapshot_json'],str)
        with reference(self.database) as source:
            expected=source.execute('SELECT snapshot_json FROM ScorecardEvent ORDER BY event_id LIMIT 1').fetchone()[0]
        self.assertEqual(rows[0]['snapshot_json'],expected)

    def test_all_formats_restore_all_rows_types_ids_hashes_and_history(self):
        with reference(self.database) as source:
            for kind,(target,result) in self.restored.items():
                self.assertEqual(result['canonical'],self.generated.canonical)
                with reference(target) as actual:
                    self.assertTrue(compare_records(source,actual)['passed'])
                    self.assertTrue(validate_evaluations(actual,GenerationConfig(),40)['passed'])
                    self.assertEqual(list(actual.execute('PRAGMA foreign_key_check')),[])
                    self.assertEqual(actual.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                    for table in table_names(source):
                        self.assertEqual([tuple(row) for row in ordered_records(source,table)],[tuple(row) for row in ordered_records(actual,table)],(kind,table))

    def test_sql_is_fresh_database_seed_not_double_initializer_metadata(self):
        with closing(connect()) as db:
            db.executescript((self.exports/'sql/schema.sql').read_text())
            with text_input(self.exports/self.catalogue['sql']['seed']) as stream:db.executescript(stream.read())
            initialize(db)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM SchemaMetadata').fetchone()[0],1)
            self.assertEqual(db.execute('PRAGMA foreign_keys').fetchone()[0],1)
            self.assertEqual(db.execute('PRAGMA recursive_triggers').fetchone()[0],1)
            self.assertEqual(dataset_digest(db),self.generated.canonical)
            with self.assertRaises(sqlite3.IntegrityError):db.execute("UPDATE ScorecardEvent SET reason_code='changed'")

    def test_dependency_order_matches_every_foreign_key(self):
        with reference(self.database) as source:
            order=import_order(source);positions={table:i for i,table in enumerate(order)}
            for table in order:
                for key in source.execute(f'PRAGMA foreign_key_list("{table}")'):
                    self.assertLess(positions[key['table']],positions[table])

    def test_first_difference_identifies_table_pk_field(self):
        with closing(connect()) as mutated,reference(self.database) as source:
            source.backup(mutated)
            with mutated:mutated.execute("UPDATE Staff SET display_name='Synthetic changed' WHERE staff_id='STAFF-000001'")
            difference=compare_records(source,mutated)
            self.assertFalse(difference['passed']);self.assertEqual(difference['first_difference'],{'table':'Staff','primary_key':{'staff_id':'STAFF-000001'},'field':'display_name','expected_type':'str','actual_type':'str'})

    def test_unicode_control_chars_real_schema_roundtrip_all_formats(self):
        fixture=self.directory/'unicode-source.sqlite3'
        with reference(self.database) as source,closing(connect(fixture)) as changed:
            source.backup(changed)
            with changed:changed.execute('UPDATE Staff SET display_name=? WHERE staff_id=?',('Synthetic 雪🙂 O\'Reilly, "quoted"\r\nnext\x00end','STAFF-000001'))
        directory=self.directory/'unicode-exports';export_database(fixture,directory,GenerationConfig())
        for kind in ('csv','json','sql'):
            target=self.directory/('unicode-'+kind+'.sqlite3');restore_database(directory,kind,target)
            with reference(fixture) as source,reference(target) as actual:self.assertTrue(compare_records(source,actual)['passed'])

    def test_gzip_is_lossless_deterministic_without_filename_or_wallclock(self):
        outputs=[];payload=('雪🙂\r\n'+('x'*200)).encode()*10
        for index in (1,2):
            path=self.directory/f'gzip-{index}.txt';path.write_bytes(payload)
            with patch('yottaflex.exports.COMPRESS_AT',1):encoded,size=compress_large(path)
            self.assertEqual(size,len(payload));self.assertEqual(gzip.decompress(encoded.read_bytes()),payload);outputs.append(encoded.read_bytes())
        self.assertEqual(outputs[0],outputs[1]);self.assertEqual(outputs[0][4:8],b'\0\0\0\0')

    def test_existing_output_and_symlink_refused_without_mutation(self):
        before=(self.exports/'catalog.json').read_bytes()
        with self.assertRaises(FileExistsError):export_database(self.database,self.exports,GenerationConfig())
        self.assertEqual((self.exports/'catalog.json').read_bytes(),before)
        target=self.directory/'dangling.sqlite3';target.symlink_to(self.directory/'no-file')
        with self.assertRaises(FileExistsError):restore_database(self.exports,'csv',target)
        self.assertTrue(target.is_symlink())

    def test_failed_export_discards_owned_scratch(self):
        target=self.directory/'failed-export'
        with patch('yottaflex.exports.compress_large',side_effect=RuntimeError('injected write failure')),self.assertRaises(RuntimeError):export_database(self.database,target,GenerationConfig())
        self.assertFalse(target.exists());self.assertEqual(list(self.directory.glob('.export-*')),[])
        self.assertFalse((self.directory/'.failed-export.publication-lock').exists())

    def test_checksum_corrupted_import_rejected_and_no_partial_database(self):
        import shutil
        bad=self.directory/'bad-checksum';shutil.copytree(self.exports,bad)
        file=bad/self.catalogue['tables']['Candidate']['csv']['path'];file.write_bytes(file.read_bytes()+b'bad\n')
        target=self.directory/'bad-checksum.sqlite3'
        with self.assertRaisesRegex(ValueError,'checksum'):restore_database(bad,'csv',target)
        self.assertFalse(target.exists());self.assertEqual(list(self.directory.glob('.restore-*')),[])

    def test_corruption_with_updated_hash_still_hits_actual_fk_constraints(self):
        import shutil
        bad=self.directory/'bad-fk';shutil.copytree(self.exports,bad);catalogue=deepcopy(self.catalogue)
        relative=catalogue['tables']['Availability']['csv']['path'];path=bad/relative
        with path.open(newline='') as stream:rows=list(csv.reader(stream))
        rows[1][rows[0].index('staff_id')]='STAFF-999999'
        with path.open('w',newline='') as stream:csv.writer(stream,lineterminator='\n',quoting=csv.QUOTE_ALL).writerows(rows)
        catalogue['files'][relative]=file_info(path);write_json(bad/'catalog.json',catalogue)
        target=self.directory/'bad-fk.sqlite3'
        with self.assertRaises(sqlite3.IntegrityError):restore_database(bad,'csv',target)
        self.assertFalse(target.exists())

    def test_json_boolean_type_corruption_rejected_even_if_checksum_updated(self):
        import shutil
        bad=self.directory/'bad-json';shutil.copytree(self.exports,bad);catalogue=deepcopy(self.catalogue)
        relative=catalogue['tables']['Candidate']['json']['path'];path=bad/relative;document=json.loads(path.read_text());document['rows'][0]['experience_years']=True
        path.write_text(json.dumps(document));catalogue['files'][relative]=file_info(path);write_json(bad/'catalog.json',catalogue)
        with self.assertRaisesRegex(ValueError,'scalar type'):restore_database(bad,'json',self.directory/'bad-json.sqlite3')

    def test_sql_duplicate_metadata_still_hits_append_only_protection(self):
        import shutil
        bad=self.directory/'bad-sql';shutil.copytree(self.exports,bad);catalogue=deepcopy(self.catalogue)
        relative=catalogue['sql']['seed'];path=bad/relative
        self.assertFalse(path.name.endswith('.gz')) # Isolated starter fixture is below compression threshold.
        with path.open('a') as stream:stream.write('INSERT INTO SchemaMetadata SELECT * FROM SchemaMetadata;\n')
        catalogue['files'][relative]=file_info(path);write_json(bad/'catalog.json',catalogue)
        target=self.directory/'bad-sql.sqlite3'
        with self.assertRaises(sqlite3.IntegrityError):restore_database(bad,'sql',target)
        self.assertFalse(target.exists());self.assertEqual(list(self.directory.glob('.restore-*')),[])

    def test_validation_counts_cover_unique_without_rowid_internal_index(self):
        with reference(self.database) as source:report=validation_summary(source,GenerationConfig())
        self.assertTrue(report['passed']);self.assertTrue(all(value==0 for value in report['categories'].values()))
        self.assertEqual(len(report['domain']['checks']),99)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace=tempfile.TemporaryDirectory(prefix='yottaflex-packages-');cls.directory=Path(cls.workspace.name)
        cls.paths=[cls.directory/f'package-{i}' for i in (1,2)]
        cls.results=[build_package(path,GenerationConfig()) for path in cls.paths]

    @classmethod
    def tearDownClass(cls):cls.workspace.cleanup()

    def test_two_independent_complete_packages_match_every_byte_and_manifest(self):
        self.assertEqual(self.results[0][0],self.results[1][0])
        names={str(p.relative_to(self.paths[0])) for p in self.paths[0].rglob('*') if p.is_file()}
        self.assertEqual(names,set(self.results[0][0]['file_inventory'])|{'manifest.json'})
        for name in names:self.assertEqual((self.paths[0]/name).read_bytes(),(self.paths[1]/name).read_bytes(),name)

    def test_manifest_provenance_full_file_hashes_sizes_and_no_self_reference(self):
        manifest=self.results[0][0]
        self.assertNotIn('manifest.json',manifest['file_inventory']);self.assertEqual(manifest['seed'],20261022)
        self.assertEqual(len(manifest['canonical']['tables']),24);self.assertEqual(len(manifest['core_entities']),11)
        self.assertEqual(manifest['provenance']['external_datasets'],[])
        for name,metadata in manifest['file_inventory'].items():self.assertEqual(file_info(self.paths[0]/name),metadata)

    def test_packaged_detector_and_evaluator_recreate_actual_findings_metrics(self):
        report,_=verify_package(self.paths[0],self.directory/'verification')
        self.assertTrue(report['passed']);self.assertEqual(report['anomalies']['actual_findings'],6)
        self.assertEqual((report['anomalies']['evaluation']['TP'],report['anomalies']['evaluation']['FP'],report['anomalies']['evaluation']['FN']),(6,0,0))
        self.assertFalse(report['anomalies']['semantic_valid']);self.assertEqual(report['anomalies']['unexpected_findings'],0)
        self.assertTrue(all(result['row_comparison']['passed'] for result in json.loads((self.paths[0]/'baseline/round-trip-verification.json').read_text()).values()))

    def test_artifact_has_no_scratch_sqlite_private_paths_credentials_or_real_names(self):
        self.assertTrue(scan_files(self.paths[0])['passed'])
        self.assertFalse(list(self.paths[0].rglob('*.sqlite3')))
        self.assertTrue(self.results[0][0]['provenance']['synthetic_only']['passed'])

    def test_manifest_rejects_unlisted_or_corrupted_file(self):
        marker=self.paths[0]/'unexpected.txt';marker.write_text('unexpected')
        try:
            with self.assertRaisesRegex(ValueError,'inventory'):verify_package(self.paths[0],self.directory/'bad-package-verify')
        finally:marker.unlink()

    def test_package_failure_cleanup_no_partial_artifacts(self):
        target=self.directory/'failed-package'
        with patch('yottaflex.deliverables._verify_anomalies',side_effect=RuntimeError('injected report failure')),self.assertRaises(RuntimeError):build_package(target,GenerationConfig())
        self.assertFalse(target.exists());self.assertEqual(list(self.directory.glob('.export-*')),[])

    def test_privacy_scanner_finds_tokens_paths_links_and_private_binaries(self):
        fixture=self.directory/'unsafe';fixture.mkdir()
        (fixture/'token.txt').write_text('sk-'+'X'*32)
        (fixture/'path.txt').write_text('/'+'Users/'+'privateperson/file')
        (fixture/'link.txt').write_text('/careers/my/'+'application/'+'123')
        (fixture/'private.pdf').write_bytes(b'%PDF-not-a-real-document')
        report=scan_files(fixture);self.assertFalse(report['passed'])
        self.assertTrue({'credential_token','private_path','personal_application_link','private_or_binary_filename'}<={f['kind'] for f in report['findings']})


if __name__=='__main__':unittest.main()
