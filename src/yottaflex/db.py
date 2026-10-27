"""SQLite connections and non-destructive versioned initialization only."""

from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3


SCHEMA_VERSION = 2
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class SchemaError(RuntimeError):
    """An existing database requires explicit investigation or migration."""


def _configure(connection: sqlite3.Connection) -> None:
    if connection.in_transaction:
        raise SchemaError("Cannot initialize/configure during an active transaction")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA recursive_triggers = ON")
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise SchemaError("SQLite foreign-key enforcement could not be enabled")


def connect(path: str | Path = ":memory:") -> sqlite3.Connection:
    """Open a database with FK checks on; caller must close the connection."""
    if sqlite3.sqlite_version_info < (3, 38, 0):
        raise SchemaError("SQLite 3.38+ is required for STRICT tables and built-in JSON validation")
    connection = sqlite3.connect(str(path))
    try:
        connection.row_factory = sqlite3.Row
        _configure(connection)
    except Exception:
        connection.close()
        raise
    return connection


def _catalog_digest(connection: sqlite3.Connection) -> str:
    objects = connection.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_schema "
        "WHERE name NOT GLOB 'sqlite_*' ORDER BY type, name"
    ).fetchall()
    data = json.dumps([tuple(row) for row in objects], separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


def _statements(sql: str):
    """Split static DDL using SQLite's own statement-completeness parser."""
    pending = ""
    for line in sql.splitlines(keepends=True):
        pending += line
        if sqlite3.complete_statement(pending):
            yield pending
            pending = ""
    if pending.strip():
        raise SchemaError("Incomplete statement in schema.sql")


def initialize(connection: sqlite3.Connection) -> None:
    """Create a fresh schema or verify an identical existing one; never reset."""
    _configure(connection)
    schema = SCHEMA_PATH.read_bytes()
    source_digest = hashlib.sha256(schema).hexdigest()
    # Acquire the writer lock BEFORE checking version/emptiness. No executescript:
    # it would implicitly commit a caller's transaction and complicate rollback.
    connection.execute("BEGIN IMMEDIATE")
    try:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        objects = connection.execute(
            "SELECT name FROM sqlite_schema WHERE name NOT GLOB 'sqlite_*'"
        ).fetchall()
        if version == 0 and not objects:
            for statement in _statements(schema.decode("utf-8")):
                connection.execute(statement)
            connection.execute(
                "INSERT INTO SchemaMetadata VALUES (1, ?, ?, ?)",
                (SCHEMA_VERSION, source_digest, _catalog_digest(connection)),
            )
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        elif version == SCHEMA_VERSION:
            metadata = connection.execute(
                "SELECT schema_version, source_sha256, catalog_sha256 "
                "FROM SchemaMetadata WHERE singleton = 1"
            ).fetchone()
            expected = (SCHEMA_VERSION, source_digest, _catalog_digest(connection))
            if metadata is None or tuple(metadata) != expected:
                raise SchemaError("Schema fingerprint mismatch; explicit migration required")
        else:
            raise SchemaError(
                f"Refusing unknown/populated database at version {version}; no reset performed"
            )
        if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise SchemaError("Existing database contains foreign-key violations")
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def main() -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Initialize/verify YottaFlex schema; no data generation")
    parser.add_argument("database", help="Local SQLite path; parent directory must already exist")
    args = parser.parse_args()
    try:
        with closing(connect(args.database)) as connection:
            initialize(connection)
    except (OSError, sqlite3.Error, SchemaError) as error:
        print(f"Schema initialization failed: {error}", file=sys.stderr)
        return 1
    print(f"Schema version {SCHEMA_VERSION} initialized/verified; no domain rows generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
