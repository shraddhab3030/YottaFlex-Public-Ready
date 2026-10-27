"""Run real independent starter/full replays and compare canonical records."""

import argparse
from contextlib import closing
from itertools import zip_longest
import json
from pathlib import Path
from time import perf_counter

from yottaflex.canonical import ordered_records, table_names
from yottaflex.db import connect
from yottaflex.generate import generate_database
from yottaflex.generation_config import DEFAULT_SEED, GenerationConfig


def verify(directory: Path, profiles, seed, *, phase="master", interview_target=None):
    started = perf_counter()
    from yottaflex.interview_generation import SchedulingConfig
    configurations = {profile:GenerationConfig(profile=profile,seed=seed) for profile in profiles}
    scheduling = {profile:SchedulingConfig.for_profile(config,interview_target) if phase!="master" else None
                  for profile,config in configurations.items()}
    if interview_target is not None and phase == "master":
        raise ValueError("Interview target requires interviews mode")
    for profile,options in scheduling.items():
        if options is not None:
            options.validate_for(configurations[profile])
    directory.mkdir(parents=True,exist_ok=False)
    evidence = {"seed":seed,"profiles":{}}
    for profile in profiles:
        paths = [directory/f"{profile}-{index}.sqlite3" for index in (1,2)]
        results = [generate_database(path,configurations[profile],phase=phase,scheduling=scheduling[profile]) for path in paths]
        comparisons = {}
        sentinel = object()
        with closing(connect(paths[0])) as left,closing(connect(paths[1])) as right:
            for table in table_names(left):
                rows, equal = 0, True
                for a,b in zip_longest(ordered_records(left,table),ordered_records(right,table),fillvalue=sentinel):
                    rows += 1
                    if a is sentinel or b is sentinel or tuple(a)!=tuple(b):
                        equal = False
                        break
                comparisons[table] = {"records_compared":rows,"equal":equal}
        summaries_equal = results[0].summary==results[1].summary
        canonical_equal = results[0].canonical==results[1].canonical
        passed = summaries_equal and canonical_equal and all(item["equal"] for item in comparisons.values())
        evidence["profiles"][profile] = {"passed":passed,"summaries_equal":summaries_equal,
            "canonical_equal":canonical_equal,"records":comparisons,"summary":results[0].summary,
            "runs":[{"elapsed_seconds":result.elapsed_seconds,"canonical":result.canonical} for result in results]}
        if phase != "master":
            for run,result in zip(evidence["profiles"][profile]["runs"],results):
                run["timings"] = result.timings
        if not passed:
            raise ValueError(f"Reproducibility failed for {profile}")
    evidence["passed"] = all(value["passed"] for value in evidence["profiles"].values())
    if phase == "evaluations":
        evidence["reproducibility_elapsed_seconds"] = perf_counter()-started
    (directory/"reproducibility.json").write_text(json.dumps(evidence,sort_keys=True,indent=2)+"\n")
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory",type=Path,required=True,help="New ignored scratch directory; existing directories refused")
    parser.add_argument("--profile",choices=("starter","full","both"),default="both")
    parser.add_argument("--seed",type=int,default=DEFAULT_SEED)
    parser.add_argument("--phase",choices=("master","interviews","evaluations"),default="master")
    parser.add_argument("--interviews",type=int)
    args = parser.parse_args()
    profiles = ("starter","full") if args.profile=="both" else (args.profile,)
    # Validate before creating any directory or database.
    for profile in profiles:
        GenerationConfig(profile=profile,seed=args.seed)
    evidence = verify(args.directory,profiles,args.seed,phase=args.phase,interview_target=args.interviews)
    for profile, value in evidence["profiles"].items():
        print(f"{profile}: passed={value['passed']}; canonical_sha256={value['runs'][0]['canonical']['sha256']}; "
              f"seconds={[round(run['elapsed_seconds'],6) for run in value['runs']]}")
    print(f"Detailed measured evidence: {args.directory/'reproducibility.json'}")


if __name__ == "__main__":
    main()
