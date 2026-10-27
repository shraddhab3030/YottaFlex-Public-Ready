"""Strict business observations over a read-only canonical reference; no labels."""

from contextlib import contextmanager, closing
import hashlib
import json
from pathlib import Path
import sqlite3

from .canonical import primary_keys, table_names, table_digest
from .db import connect, SCHEMA_PATH, SCHEMA_VERSION, _catalog_digest


EDITABLE = {"Application":{"status","updated_at"},"Candidate":{"status","withdrawn_at"},
    "Interview":{"start_at","end_at","status"},"Offer":{"amount_minor"},
    "ScorecardItem":{"score_value","weight_basis_points","evidence","status"}}


@contextmanager
def reference(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError("Baseline must already exist")
    with closing(sqlite3.connect(path.resolve().as_uri()+"?mode=ro",uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA recursive_triggers=ON")
        connection.execute("PRAGMA query_only=ON")
        meta = connection.execute("SELECT schema_version,source_sha256,catalog_sha256 FROM SchemaMetadata").fetchone()
        expected = (SCHEMA_VERSION,hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),_catalog_digest(connection))
        if meta is None or tuple(meta)!=expected or connection.execute("PRAGMA user_version").fetchone()[0]!=SCHEMA_VERSION:
            raise ValueError("Unknown or drifted baseline schema")
        yield connection


def entity_identity(connection, table, row):
    return "|".join(str(row[key]) for key in primary_keys(connection,table))


def document_time(connection):
    return max(connection.execute(f'SELECT COALESCE(MAX(occurred_at),0) FROM "{table}"').fetchone()[0]
        for table in table_names(connection) if table.endswith("Event"))


def empty_document(connection):
    return {"format_version":1,"as_of":document_time(connection),"observations":[]}


def load_document(path):
    return json.loads(Path(path).read_text())


@contextmanager
def projected(source, document=None):
    """Apply only explicit observations to an owned in-memory structural fixture."""
    document = empty_document(source) if document is None else document
    if set(document)!={"format_version","as_of","observations"} or type(document["format_version"]) is not int or document["format_version"]!=1:
        raise ValueError("Unknown observation envelope or forbidden input metadata")
    as_of = document["as_of"]
    if type(as_of) is not int or not document_time(source)<=as_of<=253402300799 or not isinstance(document["observations"],list):
        raise ValueError("Observation snapshot time/list invalid")
    with closing(connect()) as view:
        source.backup(view)
        seen = set()
        before_counts = {table:source.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] for table in table_names(source)}
        for entry in document["observations"]:
            if not isinstance(entry,dict) or set(entry)!={"entity_type","entity_id","observed_at","before","after"}:
                raise ValueError("Observation fields must contain business snapshots only")
            table, identity, when = entry["entity_type"],entry["entity_id"],entry["observed_at"]
            if table not in EDITABLE or not isinstance(identity,str) or (table,identity) in seen:
                raise ValueError("Unknown or duplicate observed identity")
            seen.add((table,identity))
            if type(when) is not int or not 0<=when<=as_of:
                raise ValueError("Invalid observation timestamp")
            after = entry["after"]
            columns = list(source.execute(f'PRAGMA table_info("{table}")'))
            if not isinstance(after,dict) or set(after)!={row["name"] for row in columns}:
                raise ValueError("Observation must have exactly the actual schema columns")
            for column in columns:
                value = after[column["name"]]
                if value is not None and ((column["type"]=="INTEGER" and type(value) is not int) or (column["type"]=="TEXT" and not isinstance(value,str))):
                    raise ValueError("Observation scalar type differs from schema")
            if entity_identity(source,table,after)!=identity:
                raise ValueError("Observed identity disagrees with primary key")
            keys = primary_keys(source,table)
            predicate = " AND ".join(f'"{key}"=?' for key in keys)
            parameters = tuple(after[key] for key in keys)
            row = source.execute(f'SELECT * FROM "{table}" WHERE {predicate}',parameters).fetchone()
            before = dict(row) if row is not None else None
            if entry["before"]!=before:
                raise ValueError("Before snapshot does not match immutable baseline")
            if before is None:
                if table!="ScorecardItem":
                    raise ValueError("New core identities are not permitted")
                names = list(after)
                view.execute(f'INSERT INTO "{table}" ({",".join(names)}) VALUES ({",".join("?" for _ in names)})',tuple(after[name] for name in names))
            else:
                if any(after[name]!=before[name] for name in after if name not in EDITABLE[table]):
                    raise ValueError("Unrelated/identity field mutation forbidden")
                names = sorted(EDITABLE[table])
                view.execute(f'UPDATE "{table}" SET '+",".join(f'"{name}"=?' for name in names)+f' WHERE {predicate}',tuple(after[name] for name in names)+parameters)
            for name in ("updated_at","withdrawn_at"):
                if name in after and after[name] is not None and after[name]>when:
                    raise ValueError("Business change cannot follow its observation")
        view.commit()
        checks = {"foreign_key_violations":len(list(view.execute("PRAGMA foreign_key_check"))),
            "integrity_errors":sum(row[0]!="ok" for row in view.execute("PRAGMA integrity_check")),
            "primary_key_duplicates":0,"changed_core_counts":0,"historical_rows_changed":0,"unrelated_table_changes":0}
        counts = {}
        for table in table_names(view):
            keys = ",".join(f'"{key}"' for key in primary_keys(view,table))
            checks["primary_key_duplicates"] += view.execute(f'SELECT COUNT(*) FROM (SELECT {keys} FROM "{table}" GROUP BY {keys} HAVING COUNT(*)>1)').fetchone()[0]
            counts[table] = view.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            if table!="ScorecardItem":
                checks["changed_core_counts"] += abs(counts[table]-before_counts[table])
            if table not in EDITABLE:
                changed = table_digest(source,table)!=table_digest(view,table)
                checks["unrelated_table_changes"] += int(changed)
                if table.endswith("Event") or table=="InterviewParticipant":
                    checks["historical_rows_changed"] += int(changed)
        if any(checks.values()):
            raise ValueError(f"Observation structural validation failed: {checks}")
        yield view,{"passed":True,"checks":checks,"counts":counts,"observations":len(seen),
            "constraints":"actual unchanged STRICT/CHECK/FK/unique constraints applied with FK/recursive triggers ON"}
