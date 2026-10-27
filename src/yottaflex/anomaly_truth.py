"""Isolated truth serialization for post-detection evaluation, not input features."""

import csv
import json
from pathlib import Path
from .canonical import stable_json

FIELDS = ('scenario_id','issue_type','affected_entity_type','affected_entity_id','related_entity_ids',
    'expected_decision','rule_id','observed_violation','severity','applicable_timestamp','deterministic_seed')
STRUCTURED = ('related_entity_ids','observed_violation')


def write_truth(directory, rows):
    directory = Path(directory); directory.mkdir(exist_ok=True)
    rows = sorted(rows,key=lambda row:row['scenario_id'])
    if any(set(row)!=set(FIELDS) for row in rows):
        raise ValueError('Truth fields must match the documented schema')
    (directory/'ground_truth.json').write_text(json.dumps(rows,sort_keys=True,indent=2)+'\n')
    with (directory/'ground_truth.csv').open('w',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=FIELDS,lineterminator='\n');writer.writeheader()
        for row in rows:
            writer.writerow(row | {key:stable_json(row[key]) for key in STRUCTURED})


def read_csv(path):
    with Path(path).open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key in STRUCTURED:
            row[key] = json.loads(row[key])
        for key in ('applicable_timestamp','deterministic_seed'):
            row[key] = int(row[key])
    return rows
