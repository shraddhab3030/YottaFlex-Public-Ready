"""Check runtime/source identity/publication candidates; no domain implementation."""

from pathlib import Path
import hashlib
import json
import re
import sqlite3
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def check_runtime() -> None:
    expected = (ROOT / ".python-version").read_text().strip()
    actual = ".".join(map(str, sys.version_info[:3]))
    if actual != expected:
        raise ValueError(f"Python {expected} required; found {actual}")
    with sqlite3.connect(":memory:") as db:
        db.execute("PRAGMA foreign_keys = ON")
        if db.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            raise ValueError("SQLite foreign keys unavailable")
        db.execute("CREATE TABLE foundation_parent (id INTEGER PRIMARY KEY)")
        db.execute("CREATE TABLE foundation_child (id INTEGER PRIMARY KEY, parent_id INTEGER REFERENCES foundation_parent(id))")
        db.execute("INSERT INTO foundation_parent VALUES (1)")
        db.commit()
        try:
            with db:
                db.execute("INSERT INTO foundation_child VALUES (1, 1)")
                db.execute("INSERT INTO foundation_child VALUES (2, 99)")
        except sqlite3.IntegrityError:
            pass
        else:
            raise ValueError("SQLite failed to reject invalid foreign key")
        if db.execute("SELECT COUNT(*) FROM foundation_child").fetchone()[0]:
            raise ValueError("SQLite failed to roll back transaction")
    print(f"PASS: pinned Python {actual}; SQLite {sqlite3.sqlite_version} FK and rollback")


def check_sources() -> None:
    sources = json.loads((ROOT / "docs/phase01/sources.json").read_text())
    expected = {
        "problem-statement.md",
        "YottaFlex AI Candidate Project-FAQ.pdf",
        "YottaFlex AI Candidate Project Submission Guidelines.pdf",
    }
    entries = sources["documents"]
    if len(entries) != 3 or {Path(item["path"]).name for item in entries} != expected:
        raise ValueError("Source manifest must contain exactly the three official inputs")
    for item in entries:
        relative = Path(item["path"])
        if relative.parent != Path("docs/assignment"):
            raise ValueError("Source path outside official directory")
        content = (ROOT / relative).read_bytes()
        if len(content) != item["bytes"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ValueError(f"Missing/changed source identity: {relative}")
        if relative.suffix == ".pdf" and not content.startswith(b"%PDF-"):
            raise ValueError(f"Invalid PDF signature: {relative}")
        if relative.suffix == ".md":
            content.decode("utf-8")
    print("PASS: all three sources readable and match recorded SHA256/size/signatures")


def check_publication_candidates() -> None:
    # Includes untracked nonignored files so newly created files are checked too.
    result = subprocess.run(
        ["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True,
    )
    files = sorted(set(result.stdout.decode().split("\0")) - {""})
    forbidden = ("inputs/", "data/", "output/", "tmp/", ".venv/", "node_modules/")
    sensitive_suffixes = {".pem", ".key", ".p12", ".pfx", ".db", ".sqlite", ".sqlite3"}
    private_key = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
    for name in files:
        path = Path(name)
        if name.startswith(forbidden) or (name.startswith("docs/assignment/") and name != "docs/assignment/README.md"):
            raise ValueError(f"Private/generated file eligible for publication: {name}")
        if path.suffix.lower() in sensitive_suffixes or (path.name.startswith(".env") and path.name != ".env.example"):
            raise ValueError(f"Credential/database filename eligible for publication: {name}")
        # Never print matching file contents: they could be sensitive.
        if private_key.search((ROOT / path).read_bytes()):
            raise ValueError(f"Private-key content in publication candidate: {name}")
    print(f"PASS: {len(files)} tracked/untracked publication candidates exclude private paths/keys")


def main() -> int:
    try:
        check_runtime()
        check_sources()
        check_publication_candidates()
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Foundation Python checks passed: 3 groups. No application validation executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
