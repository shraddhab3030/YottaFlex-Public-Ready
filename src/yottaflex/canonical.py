"""Streaming canonical record comparison/hashes; not a CSV/JSON/SQL exporter."""

import hashlib
import json


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def table_names(connection):
    return [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_schema WHERE type='table' AND name NOT GLOB 'sqlite_*' ORDER BY name")]


def primary_keys(connection, table):
    rows = list(connection.execute(f'PRAGMA table_info("{table}")'))
    return [row["name"] for row in sorted(rows, key=lambda row: row["pk"]) if row["pk"]]


def ordered_records(connection, table):
    if table not in table_names(connection):
        raise ValueError("Unknown canonical table")
    keys = primary_keys(connection, table)
    if not keys:
        raise ValueError("Canonicalization requires an explicit primary key")
    order = ", ".join(f'"{key}"' for key in keys)
    yield from connection.execute(f'SELECT * FROM "{table}" ORDER BY {order}')


def table_digest(connection, table):
    columns = [row["name"] for row in connection.execute(f'PRAGMA table_info("{table}")')]
    digest = hashlib.sha256()
    digest.update((stable_json({"table": table, "columns": columns})+"\n").encode("utf-8"))
    count = 0
    for row in ordered_records(connection, table):
        digest.update((stable_json(list(row))+"\n").encode("utf-8"))
        count += 1
    return {"rows": count, "sha256": digest.hexdigest()}


def dataset_digest(connection):
    tables = {name: table_digest(connection, name) for name in table_names(connection)}
    return {"tables": tables, "sha256": hashlib.sha256(stable_json(tables).encode("utf-8")).hexdigest()}
