"""Lossless deterministic relational codecs and verified fresh-file restoration."""

from contextlib import contextmanager,closing
import csv
import gzip
import hashlib
from itertools import zip_longest
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from time import perf_counter

from .canonical import dataset_digest,ordered_records,primary_keys,table_names,stable_json
from .db import connect,initialize,SCHEMA_PATH,SCHEMA_VERSION,_statements
from .evaluation_checks import validate_evaluations
from .generation_config import GenerationConfig
from .observations import reference

COMPRESS_AT = 4*1024*1024
NULL = '\\N'


@contextmanager
def new_directory(target):
    target=Path(target)
    if target.exists() or target.is_symlink():raise FileExistsError(f'Refusing existing output: {target.name}')
    target.parent.mkdir(parents=True,exist_ok=True)
    lock=target.parent/('.'+target.name+'.publication-lock')
    descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(descriptor)
    scratch=None
    try:
        if target.exists() or target.is_symlink():raise FileExistsError('Output already claimed')
        scratch=Path(tempfile.mkdtemp(prefix='.export-',dir=target.parent))
        yield scratch
        if target.exists() or target.is_symlink():raise FileExistsError('Output appeared during generation')
        os.rename(scratch,target);scratch=None
    finally:
        if scratch is not None:shutil.rmtree(scratch)
        lock.unlink()


def write_json(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='')


def file_info(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while chunk:=stream.read(1024*1024):digest.update(chunk)
    return {'bytes':Path(path).stat().st_size,'sha256':digest.hexdigest()}


@contextmanager
def text_input(path):
    path=Path(path)
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8',newline='') as stream:yield stream


def compress_large(path):
    path=Path(path);raw_size=path.stat().st_size
    if raw_size<COMPRESS_AT:return path,raw_size
    destination=path.with_suffix(path.suffix+'.gz')
    with path.open('rb') as source,destination.open('wb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=9) as target:
            shutil.copyfileobj(source,target)
    path.unlink()
    return destination,raw_size


def csv_cell(value):
    if value is None:return NULL
    if type(value) is int:return str(value)
    if isinstance(value,str):return '\\'+value if value.startswith('\\') else value
    raise ValueError('Only schema INTEGER/TEXT/NULL values are supported')


def parse_csv_cell(value,kind):
    if value==NULL:return None
    if kind=='INTEGER':
        if not value or value.strip()!=value or value not in (str(int(value)),):raise ValueError('Noncanonical integer cell')
        result=int(value)
        if not -(2**63)<=result<2**63:raise ValueError('Integer outside SQLite int64')
        return result
    if kind!='TEXT':raise ValueError('Unsupported schema scalar type')
    if value.startswith('\\\\'):return value[1:]
    if value.startswith('\\'):raise ValueError('Noncanonical text escape')
    return value


def sql_value(value):
    if value is None:return 'NULL'
    if type(value) is int:return str(value)
    if not isinstance(value,str):raise ValueError('Unsupported SQL value type')
    if '\x00' in value:return "CAST(X'"+value.encode('utf-8').hex()+"' AS TEXT)"
    return "'"+value.replace("'","''")+"'"


def import_order(connection):
    pending=set(table_names(connection));result=[]
    dependencies={table:{row['table'] for row in connection.execute(f'PRAGMA foreign_key_list("{table}")') if row['table']!=table} for table in pending}
    while pending:
        ready=sorted(table for table in pending if not(dependencies[table]&pending))
        if not ready:raise ValueError('Foreign-key dependency cycle needs explicit import policy')
        result.extend(ready);pending.difference_update(ready)
    return result


def columns(connection,table):
    return [{'name':row['name'],'type':row['type'],'required':bool(row['notnull']),'pk_position':row['pk']}
        for row in connection.execute(f'PRAGMA table_info("{table}")')]


def _export_tables(connection,directory,config):
    directory=Path(directory)
    for name in ('csv','json','sql'):(directory/name).mkdir(parents=True)
    catalogue={'format_version':1,'profile':config.profile,'seed':config.seed,'logical_origin':config.logical_origin,
        'schema_version':SCHEMA_VERSION,'schema_sha256':hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),
        'canonical':dataset_digest(connection),'import_order':import_order(connection),'tables':{},'files':{},
        'representation':{'csv_null':'\\N','csv_text_escape':'prefix one extra backslash on any leading backslash',
            'json_text_columns':'retain exact strings, including snapshot_json; never parse/reformat nested JSON',
            'booleans':'schema INTEGER 0/1, not JSON booleans','encoding':'UTF-8, no BOM, LF records',
            'compression':'files >=4194304 raw bytes use gzip level9, mtime0, no filename'}}
    timings={}
    for kind in ('csv','json','sql'):
        started=perf_counter()
        if kind in ('csv','json'):
            for table in table_names(connection):
                metadata=columns(connection,table);names=[row['name'] for row in metadata]
                path=directory/kind/(table+'.'+kind)
                with path.open('w',encoding='utf-8',newline='') as stream:
                    if kind=='csv':
                        writer=csv.writer(stream,lineterminator='\n',quoting=csv.QUOTE_ALL);writer.writerow(names)
                        for row in ordered_records(connection,table):writer.writerow([csv_cell(value) for value in row])
                    else:
                        stream.write('{"table":'+json.dumps(table)+',"columns":'+json.dumps(names,separators=(',',':'))+',"rows":[\n')
                        first=True
                        for row in ordered_records(connection,table):
                            if not first:stream.write(',\n')
                            stream.write(json.dumps(dict(zip(names,row)),ensure_ascii=False,separators=(',',':')));first=False
                        stream.write('\n]}\n')
                path,raw_size=compress_large(path)
                entry=catalogue['tables'].setdefault(table,{'columns':metadata})
                entry[kind]={'path':str(path.relative_to(directory)),'raw_bytes':raw_size}
        else:
            schema=directory/'sql/schema.sql';schema.write_bytes(SCHEMA_PATH.read_bytes())
            seed=directory/'sql/seed.sql'
            with seed.open('w',encoding='utf-8',newline='') as stream:
                stream.write('PRAGMA foreign_keys=ON;\nPRAGMA recursive_triggers=ON;\nBEGIN IMMEDIATE;\nPRAGMA user_version='+str(SCHEMA_VERSION)+';\n')
                for table in catalogue['import_order']:
                    names=[row['name'] for row in columns(connection,table)]
                    prefix='INSERT INTO "'+table+'" ('+','.join('"'+name+'"' for name in names)+') VALUES ('
                    for row in ordered_records(connection,table):stream.write(prefix+','.join(sql_value(value) for value in row)+');\n')
                stream.write('COMMIT;\n')
            seed,raw_size=compress_large(seed)
            catalogue['sql']={'schema':'sql/schema.sql','seed':str(seed.relative_to(directory)),'seed_raw_bytes':raw_size,
                'procedure':'fresh empty database: execute schema.sql, then seed; do not initialize metadata first'}
        timings[kind+'_export_seconds']=perf_counter()-started
    for path in sorted(directory.rglob('*')):
        if path.is_file():catalogue['files'][str(path.relative_to(directory))]=file_info(path)
    write_json(directory/'catalog.json',catalogue)
    return catalogue,timings


def export_database(database,directory,config):
    with reference(database) as connection:
        validation=validate_evaluations(connection,config,2000 if config.profile=='full' else 40)
        if not validation['passed']:raise ValueError('Only a valid canonical evaluation baseline can be exported')
        with new_directory(directory) as scratch:
            catalogue,timings=_export_tables(connection,scratch,config)
            write_json(scratch/'validation-summary.json',{'classification':'valid_canonical_baseline','domain':validation,'canonical':catalogue['canonical']})
    return catalogue,timings


def _safe_file(directory,name,inventory):
    path=Path(name)
    if path.is_absolute() or '..' in path.parts or name not in inventory:raise ValueError('Unknown or unsafe export file reference')
    target=Path(directory)/path
    if target.is_symlink() or not target.is_file() or file_info(target)!=inventory[name]:raise ValueError(f'Export checksum/size mismatch: {name}')
    return target


def _read_rows(directory,catalogue,table,kind):
    metadata=catalogue['tables'][table]['columns'];names=[row['name'] for row in metadata]
    path=_safe_file(directory,catalogue['tables'][table][kind]['path'],catalogue['files'])
    with text_input(path) as stream:
        if kind=='csv':
            csv.field_size_limit(1024*1024*1024);reader=csv.reader(stream)
            if next(reader,None)!=names:raise ValueError(f'CSV header mismatch: {table}')
            for index,row in enumerate(reader,1):
                if len(row)!=len(names):raise ValueError(f'CSV field count mismatch: {table} row {index}')
                yield tuple(parse_csv_cell(value,column['type']) for value,column in zip(row,metadata))
        else:
            def unique_object(pairs):
                result=dict(pairs)
                if len(result)!=len(pairs):raise ValueError('Duplicate JSON field')
                return result
            document=json.load(stream,object_pairs_hook=unique_object)
            if set(document)!={'table','columns','rows'} or document['table']!=table or document['columns']!=names or not isinstance(document['rows'],list):raise ValueError(f'JSON envelope mismatch: {table}')
            for row in document['rows']:
                if not isinstance(row,dict) or list(row)!=names:raise ValueError(f'JSON fields/order mismatch: {table}')
                values=tuple(row[name] for name in names)
                for value,column in zip(values,metadata):
                    if value is not None and ((column['type']=='INTEGER' and type(value) is not int) or (column['type']=='TEXT' and not isinstance(value,str))):raise ValueError(f'JSON scalar type mismatch: {table}.{column["name"]}')
                yield values


def _sql_statements(stream):
    pending=''
    for line in stream:
        pending+=line
        if sqlite3.complete_statement(pending):yield pending;pending=''
    if pending.strip():raise ValueError('Incomplete SQL seed statement')


def restore_database(directory,kind,target):
    started=perf_counter();directory=Path(directory);target=Path(target)
    if kind not in ('csv','json','sql'):raise ValueError('Unknown import format')
    if target.exists() or target.is_symlink():raise FileExistsError('Refusing existing restore output')
    catalogue=json.loads((directory/'catalog.json').read_text(encoding='utf-8'))
    if catalogue['format_version']!=1 or catalogue['schema_version']!=SCHEMA_VERSION or catalogue['schema_sha256']!=hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest():raise ValueError('Incompatible export schema/version')
    config=GenerationConfig(catalogue['profile'],catalogue['seed'],catalogue['logical_origin'])
    target.parent.mkdir(parents=True,exist_ok=True)
    descriptor,name=tempfile.mkstemp(prefix='.restore-',suffix='.sqlite3',dir=target.parent);os.close(descriptor);scratch=Path(name)
    try:
        with closing(connect(scratch)) as connection:
            if kind=='sql':
                schema=_safe_file(directory,catalogue['sql']['schema'],catalogue['files'])
                if schema.read_bytes()!=SCHEMA_PATH.read_bytes():raise ValueError('SQL DDL differs from versioned schema')
                for statement in _statements(schema.read_text(encoding='utf-8')):connection.execute(statement)
                with text_input(_safe_file(directory,catalogue['sql']['seed'],catalogue['files'])) as stream:
                    for statement in _sql_statements(stream):connection.execute(statement)
                if connection.in_transaction:raise ValueError('SQL seed did not commit completely')
                initialize(connection) # Verify existing exact metadata/catalog; no duplicate insertion.
            else:
                initialize(connection)
                if set(catalogue['tables'])!=set(table_names(connection)) or catalogue['import_order']!=import_order(connection):raise ValueError('Incomplete table set or FK order')
                with connection:
                    connection.execute('BEGIN IMMEDIATE')
                    for table in catalogue['import_order']:
                        if catalogue['tables'][table]['columns']!=columns(connection,table):raise ValueError(f'Schema column descriptor mismatch: {table}')
                        names=[row['name'] for row in columns(connection,table)]
                        keys=primary_keys(connection,table);positions=[names.index(key) for key in keys]
                        previous=None;count=0;batch=[]
                        for row in _read_rows(directory,catalogue,table,kind):
                            key=tuple(row[position] for position in positions)
                            if previous is not None and key<=previous:raise ValueError(f'Non-PK-ordered/duplicate input: {table}')
                            previous=key;count+=1
                            if table=='SchemaMetadata':
                                if count!=1 or tuple(connection.execute('SELECT * FROM SchemaMetadata').fetchone())!=row:raise ValueError('Initializer metadata mismatch')
                                continue
                            batch.append(row)
                            if len(batch)==256:
                                connection.executemany('INSERT INTO "'+table+'" VALUES ('+','.join('?' for _ in names)+')',batch);batch.clear()
                        if batch:connection.executemany('INSERT INTO "'+table+'" VALUES ('+','.join('?' for _ in names)+')',batch)
                        if count!=catalogue['canonical']['tables'][table]['rows']:raise ValueError(f'Imported row count mismatch: {table}')
            if connection.execute('PRAGMA foreign_keys').fetchone()[0]!=1 or connection.execute('PRAGMA recursive_triggers').fetchone()[0]!=1:raise ValueError('SQL import weakened connection protections')
            validation_started=perf_counter()
            validation=validate_evaluations(connection,config,2000 if config.profile=='full' else 40)
            canonical=dataset_digest(connection)
            validation_seconds=perf_counter()-validation_started
            if not validation['passed'] or canonical!=catalogue['canonical']:raise ValueError('Restored domain/content does not match exported canonical reference')
        os.link(scratch,target) # Exclusive fresh-file publication.
    finally:scratch.unlink(missing_ok=True)
    return {'format':kind,'canonical':canonical,'domain':validation,'protections':{'foreign_keys':1,'recursive_triggers':1}}, {'import_seconds':perf_counter()-started,'validation_seconds':validation_seconds}


def compare_records(left,right):
    sentinel=object();comparisons={}
    if table_names(left)!=table_names(right):return {'passed':False,'first_difference':{'table_set':True},'tables':comparisons}
    for table in table_names(left):
        names=[row['name'] for row in columns(left,table)];keys=primary_keys(left,table);count=0
        if columns(left,table)!=columns(right,table):return {'passed':False,'first_difference':{'table':table,'field':'schema'},'tables':comparisons}
        for a,b in zip_longest(ordered_records(left,table),ordered_records(right,table),fillvalue=sentinel):
            count+=1
            if a is sentinel or b is sentinel:
                present=b if a is sentinel else a
                return {'passed':False,'first_difference':{'table':table,'field':'row_count','primary_key':{key:present[key] for key in keys}},'tables':comparisons}
            for name,expected,actual in zip(names,a,b):
                if type(expected) is not type(actual) or expected!=actual:
                    return {'passed':False,'first_difference':{'table':table,'primary_key':{key:a[key] for key in keys},'field':name,
                        'expected_type':type(expected).__name__,'actual_type':type(actual).__name__},'tables':comparisons}
        comparisons[table]={'rows_compared':count,'equal':True}
    return {'passed':True,'first_difference':None,'tables':comparisons}
