"""Two fresh complete baseline/export/import/anomaly packages and exact comparison."""
import argparse
from itertools import zip_longest
import json
from pathlib import Path
from time import perf_counter

from yottaflex.deliverables import build_package
from yottaflex.exports import _read_rows,file_info
from yottaflex.generation_config import GenerationConfig


def verify(directory,profile='full',seed=20261022):
    started=perf_counter();directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    paths=[directory/f'run-{i}' for i in (1,2)]
    results=[build_package(path,GenerationConfig(profile,seed)) for path in paths]
    files={str(path.relative_to(paths[0])) for path in paths[0].rglob('*') if path.is_file()}
    other={str(path.relative_to(paths[1])) for path in paths[1].rglob('*') if path.is_file()}
    if files!=other:raise ValueError('Two-run artifact inventories differ')
    compared={name:{'equal':file_info(paths[0]/name)==file_info(paths[1]/name) and (paths[0]/name).read_bytes()==(paths[1]/name).read_bytes(),'bytes':(paths[0]/name).stat().st_size,
        'sha256':file_info(paths[0]/name)['sha256']} for name in sorted(files)}
    if not all(value['equal'] for value in compared.values()):raise ValueError('Two-run file byte digests differ')
    catalogues=[json.loads((path/'baseline/catalog.json').read_text()) for path in paths]
    rows={};sentinel=object()
    for table in sorted(catalogues[0]['tables']):
        count=0
        for a,b in zip_longest(*(_read_rows(path/'baseline',catalogue,table,'json') for path,catalogue in zip(paths,catalogues)),fillvalue=sentinel):
            if a is sentinel or b is sentinel or len(a)!=len(b) or any(type(x) is not type(y) or x!=y for x,y in zip(a,b)):
                raise ValueError(f'Two-run canonical row/type mismatch: {table}, row {count+1}')
            count+=1
        rows[table]={'rows_compared':count,'equal':True}
    same=results[0][0]==results[1][0]
    if not same:raise ValueError('Stable manifest sections differ')
    evidence={'passed':True,'profile':profile,'seed':seed,'canonical':results[0][0]['canonical'],
        'manifest_equal':same,'records':rows,'files':compared,'runs':[{'timing':result[1]} for result in results],
        'elapsed_seconds':perf_counter()-started,'comparison_policy':'Every artifact file SHA256/size including compressed files and manifest; every JSON relational scalar type/value. Imports independently validated/compared to original in each build; timings excluded from package.'}
    (directory/'reproducibility.json').write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
    return evidence


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--profile',choices=('starter','full'),default='full');parser.add_argument('--seed',type=int,default=20261022)
    args=parser.parse_args();evidence=verify(args.directory,args.profile,args.seed)
    print('PASS:',evidence['canonical']['sha256'],'rows=',sum(v['rows_compared'] for v in evidence['records'].values()),'files=',len(evidence['files']),'seconds=',evidence['elapsed_seconds'])
