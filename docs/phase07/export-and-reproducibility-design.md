# Phase 07 export/import and reproducibility design

P010 authorizes complete portable artifacts, independent restores and tracked
safe synthetic data. Earlier source/runtime/phase behavior stays unchanged.
No schema migration, UI, external service, new dependency, public remote, push or
submission. Schema v2/24 tables/209 fields/45 FK groups/42 protection triggers.

## Architecture and encodings

exports.py owns codecs, actual-schema catalog, FK dependency order, fresh-file
restore and first-difference comparison. deliverables.py composes build/export/
restore/verify/evaluate commands. privacy.py checks candidate provenance and
publication patterns. Existing generation/workflow/detection/metric functions
remain unchanged; the package always uses the valid Phase05 baseline and linked
Phase06 observations, never a corrupted projection as the baseline seed.

CSV: UTF-8/no BOM, LF record separators, every cell/header quoted with standard
CSV escaping; embedded CR/LF/quotes/Unicode/NUL preserved. Null is the unique `\N`
cell. TEXT beginning with backslash receives one extra leading backslash, undone
on import; empty text remains empty, distinct from NULL and literal `\N`.
INTEGER cells use exact canonical decimal, no whitespace/leading-zero/float or
scientific coercion. Schema INTEGER booleans remain0/1. Int64 parsed by Python,
never spreadsheet/floating point. Schema-required nulls fail actual SQLite checks.

JSON: per-table object with table, columns and rows. Every row is a schema-column-
ordered object with all columns. Numbers are integers, optional values null,
strings exact. Opaque JSON-valued TEXT columns (snapshot_json) remain strings;
no parsing/reformatting their embedded objects. Duplicate keys, wrong fields/order
or booleans in INTEGER columns reject. Exports stream rows; JSON import loads
one table at a time. Maximum table memory, not a Cartesian materialization.

SQL: exact versioned schema.sql plus INSERT statements with explicit columns,
PK order and topologically FK-safe table order. Standard single-quote doubling,
NULL and exact decimal integers. Text containing NUL uses CAST(X'UTF8hex' AS TEXT),
which preserves content without embedding illegal NUL in SQL statement text.
No label fields are added to baseline exports. Events/bridges are not omitted.

Files at least4MiB raw are losslessly gzip-compressed (level9,mtime0,no filename).
Smaller files stay readable text. Compression threshold is deterministic, recorded
in catalog; actual raw/stored sizes and SHA256 are measured. This keeps generated
artifacts comfortably in the single repository, no external hosting. Gzip is
transparently opened by CLI; standard decompression also yields portable files.
Same verified runtime/library build is the byte-replay scope, not a blanket claim
of compressed-byte identity across arbitrary zlib/SQLite versions.

## Metadata, protection and import order

Actual PRAGMA foreign_key_list determines acyclic dependency order; stable lexical
order breaks ties. Each table's exact column descriptors/PK order and canonical
row count/hash are in catalog.json. Import into an existing path/symlink is refused.
Owned scratch restores publish with exclusive hard link only after validation.

CSV/JSON: call the normal initializer, which creates exact DDL and singleton
SchemaMetadata. Imported metadata row must equal that existing row byte-for-value;
verify it, do not insert/replace it again. Every other row inserted with FK and
recursive triggers ON in one BEGIN IMMEDIATE transaction. Required PK order,
row counts, types, uniqueness, FK/scalars and fingerprint are checked.

SQL: fresh EMPTY database only. Execute exact schema.sql first (no initializer
metadata insertion), then seed. Seed enables FK/recursive triggers, begins one
transaction, sets user_version2, inserts every table including SchemaMetadata
exactly once and commits. Then the normal initializer verifies exact existing
metadata/catalog/fingerprint and FK integrity. No triggers or FK checks disabled.
A raw compatible SQLite client can do the same two-step restoration; the CLI
implements it directly. Calling the initializer before the seed would duplicate
append-only metadata and correctly fails. Arbitrary untrusted SQL execution is
not a security boundary; hashes provide integrity, not signed authenticity.

## Independent verification and diagnostics

Each format restores into a different fresh SQLite file. Restored canonical
hashes must equal original/catalog. Every restore runs PRAGMA FK/integrity, all
99 Phase05 domain checks, type/null/key/count/history/rubric/band/stage/calendar
validation. A separate original-versus-restored comparator streams all24 tables
by declared PK, comparing each scalar's Python type/value. First difference
reports table, primary key and field/type; missing rows report their PK. Success
is never inferred from a command exit code or hash alone.

Additional machine-readable validation categories measure enum violations from
actual DDL IN constraints and unique-key duplicates from SQLite indexes, including
partial indexes. WITHOUT ROWID implicit indexes may have no sqlite_schema row;
they still receive PK/uniqueness checks. Full detailed checks remain, so aggregate
categories do not hide errors. Aggregate categories may overlap; they are not a
count of unique bad entities.

The package copies observations, both truth files and every report from one
actual Phase06 execution. It excludes its redundant binary SQLite copy. Packaged
JSON-restored baseline plus observations must recreate findings/structure; only
after detection does the evaluator load agreed CSV/JSON truth and reproduce
metrics. Baseline canonical fingerprint must match the anomaly reference.
Baseline validity, structurally valid observations, expected semantic findings,
unexpected findings/misses remain separate classifications.

## Manifest and provenance

manifest.json records profile, current generator Git commit, exporter version and
all runtime Python source SHA256; later data/doc commits do not require a circular
regeneration. Configuration+SHA256, fixed seed/logical origin, schema version/SHA,
runtime requirements, every table count/hash, eleven core entities/FK dependencies,
formats, provenance and validation/anomaly/replay references are included.
Every artifact file has relative path, size and SHA256; manifest excludes ONLY
itself. Replay evidence is external under docs/phase07, deliberately outside the
package inventory to avoid a circular hash. Catalog's format-file hashes exclude
its own metadata/reports; the package manifest inventories those too.

All candidate identities and recruitment records are synthetic. No real resumes,
scraped profiles, confidential records or external personal datasets were used.
external_datasets and vendored_dependencies are empty; no invented source URL,
license or retrieval date. Runtime uses the locally supplied CPython standard
library/SQLite, not copied third-party core code. Private assignment identities
are referenced by the existing source manifest; PDFs/text remain excluded.

Verification checks exact inventory, file SHA/size, config/schema/catalog/canonical
consistency, tool-source fingerprints, privacy and all restores. Git -text on
artifacts preserves exact bytes, including CR/LF and gzip, without indiscriminate
unignoring of databases/private files. Existing code/prompts/history retained.

## Reproduction and reviewer commands

See README Quick Start for local venv/test/verify commands. No private assignment
PDF or internet service is needed to review/restore/run the packaged data.
The optional maintainer source-smoke still requires the exact ignored PDFs and
fails honestly if absent. No pip install or bundled large framework.

    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables build --profile full --seed 20261022 --directory output/new-package
    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/new-verification
    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format sql --database output/new-restored.sqlite3
    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables evaluate --directory artifacts/anomalies --database output/new-restored.sqlite3
    PYTHONPATH=src .venv/bin/python3 scripts/verify_deliverable_reproducibility.py --profile full --seed 20261022 --directory output/new-two-run-replay

Each full replay run independently regenerates its own clean baseline, exports,
all three restores, original row comparisons and Phase06 bundle. Cross-run replay
compares every artifact byte (CSV/JSON/SQL/gzip/labels/findings/metrics/manifest),
logical rows/types, counts and table/aggregate hashes. Timings and host paths stay
outside deterministic artifacts. Actual evidence is copied unchanged from tool
output; file inventory/sizes and component timings are in the current handoff.

## Limits and release review

Initial prototypes found a WITHOUT ROWID index metadata handling bug; it was
corrected and regressed. Early test-only connection warnings were corrected with
explicit closes. Final results supersede checkpoints; no fabricated outputs.

Public dataset scanners cover credentials/tokens/private paths/personal links,
forbidden binaries and actual generated synthetic identities/email domains.
They cannot guarantee privacy. Historical private-path references in prior local
handoffs are retained as honest history and separately flagged for human review;
no new artifact contains them. Do not publish until final audit resolves inherited
privacy/ownership/channel/window questions. Report these findings, do not hide
or silently rewrite original user prompts/history. No push/remotes/submission.

Directory publication uses cooperative exclusive locks/complete rename; unowned
outputs/locks refused and owned failure scratch cleaned. It is not a hostile OS
security boundary. Restores use fresh exclusive hard links. Exact pinned runtime
is tested; other compatible SQLite builds need verification. JSON per-table
memory and gzip CPU are acceptable at measured scale; peak RSS is not fabricated.
No UI/hosting/model service is needed. STOP after Phase07 for user review.

## Executed FULL measurements

Both fresh packages passed every restore/row/file/anomaly check. Seed20261022,
CPython3.14.5/SQLite3.53.1, implementation50bbcfe. Two-run elapsed101.976450s.
These are local measurements, not an external performance benchmark.

| Operation (seconds) | Run1 | Run2 |
| --- | ---: | ---: |
| Baseline generation | 22.608130 | 21.222815 |
| CSV export | 0.757764 | 0.767186 |
| JSON export | 0.736905 | 0.621944 |
| SQL export | 0.771164 | 0.646020 |
| Baseline validation | 1.872102 | 1.909334 |
| Anomaly generation/detection/evaluation | 8.657549 | 8.314350 |
| Package total | 51.379010 | 49.860275 |
| CSV import | 2.886281 | 2.993617 |
| CSV validation | 1.768199 | 1.773389 |
| JSON import | 3.177406 | 2.797624 |
| JSON validation | 1.969666 | 1.776268 |
| SQL import | 3.917775 | 4.541973 |
| SQL validation | 1.767461 | 2.158403 |

Stored package68 files/25495764 bytes; largest stored file2281185 bytes.
Five deterministic gzip files preserve raw texts4620952/14698874/7485702/
15857529/39261537 bytes, documented in catalog/inventory. Actual replay evidence
is in reproducibility-evidence.json; final reviewer commands in
reviewer-verification.json and the handoff. Peak memory was not measured.
