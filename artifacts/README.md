# Reviewed synthetic dataset package

All candidate identities and recruitment records are synthetic. No real candidate
records, scraped profiles, resumes, confidential data or external personal datasets.
Baseline exports are the valid canonical Phase05 data; anomalies are separate.

From the repository root with Python3.14.5 and no dependency downloads:

    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/verify-artifacts
    PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format json --database output/restored.sqlite3
    PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/restored.sqlite3 --observations artifacts/anomalies/input/observations.json

Use new restore/work paths. The verify command restores all formats and reproduces
anomaly findings/metrics from business inputs before reading truth for scoring.
CSV null is backslash-N; leading text backslashes double; empty string stays empty.
JSON text columns remain strings; INTEGER booleans remain0/1. Schema-column/PK
order is stable. Gzip files are lossless with fixed header, transparently read by
CLI; large files are compressed to keep this repository modest. SQL: execute
sql/schema.sql in an empty DB, then decompressed seed.sql (possibly .gz), without
running the initializer first. Both FK and all triggers remain enabled. Never
execute arbitrary untrusted SQL; hashes prove integrity, not publisher authenticity.

See docs/phase07/export-and-reproducibility-design.md for exact encodings/policies,
manifest exclusions, runtime requirements and limitations. Manifest hashes exclude
manifest.json itself. Reproduction evidence is in docs/phase07/ outside this
inventory to avoid circular/self-referential hashes. No publication is authorized.
