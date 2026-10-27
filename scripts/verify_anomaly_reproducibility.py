"""Independent Phase06 bundles, every canonical observed row and byte comparisons."""
import argparse
from contextlib import ExitStack
from itertools import zip_longest
import json
from pathlib import Path
from time import perf_counter

from yottaflex.anomalies import build_bundle
from yottaflex.canonical import ordered_records,table_names
from yottaflex.generate import generate_database
from yottaflex.generation_config import GenerationConfig
from yottaflex.observations import reference,projected,load_document


def verify(directory, profiles=('starter','full'), seed=20261022):
    started=perf_counter();directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    evidence={'seed':seed,'profiles':{}}
    for profile in profiles:
        baseline=directory/f'{profile}-clean.sqlite3'
        generated=generate_database(baseline,GenerationConfig(profile),phase='evaluations')
        paths=[directory/f'{profile}-{i}' for i in (1,2)]
        results=[build_bundle(baseline,path,profile,seed=seed) for path in paths]
        comparisons={};sentinel=object()
        with ExitStack() as stack:
            sources=[stack.enter_context(reference(path/'input/baseline.sqlite3')) for path in paths]
            views=[stack.enter_context(projected(source,load_document(path/'input/observations.json')))[0] for source,path in zip(sources,paths)]
            for table in table_names(views[0]):
                count,equal=0,True
                for a,b in zip_longest(ordered_records(views[0],table),ordered_records(views[1],table),fillvalue=sentinel):
                    count+=1
                    if a is sentinel or b is sentinel or tuple(a)!=tuple(b):equal=False;break
                comparisons[table]={'records_compared':count,'equal':equal}
        file_equality={name:(paths[0]/name).read_bytes()==(paths[1]/name).read_bytes() for name in results[0][0]['file_sha256']}
        same=results[0][0]==results[1][0]
        matched=same and all(file_equality.values()) and all(value['equal'] for value in comparisons.values())
        evidence['profiles'][profile]={'passed':matched,'canonical_clean':generated.canonical,
            'clean_generation_seconds':generated.elapsed_seconds,'summaries_equal':same,'records':comparisons,
            'files_equal':file_equality,'summary':results[0][0],'runs':[{'timing':result[1]} for result in results]}
        if not matched:raise ValueError(f'Anomaly replay mismatch for {profile}')
    evidence['passed']=all(value['passed'] for value in evidence['profiles'].values())
    evidence['elapsed_seconds']=perf_counter()-started
    (directory/'reproducibility.json').write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
    return evidence


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--profile',choices=('starter','full','both'),default='both');parser.add_argument('--seed',type=int,default=20261022)
    args=parser.parse_args();profiles=('starter','full') if args.profile=='both' else (args.profile,)
    evidence=verify(args.directory,profiles,args.seed)
    for profile,value in evidence['profiles'].items():print(profile,'passed=',value['passed'],'input SHA256=',value['summary']['canonical_input_sha256'],'metrics=',value['summary']['evaluation'])
    print('Real replay seconds:',evidence['elapsed_seconds'])
