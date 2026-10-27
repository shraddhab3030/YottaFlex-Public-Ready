# YottaFlex recruiting workflow and reproducible synthetic data

This is **YottaFlex-Public-Ready**, a separate local publication candidate. The
private development repository/history is preserved unchanged. No Git repository
or remote has been initialized here. Seven copied historical reports have logged
privacy redactions; every source/test/schema/artifact byte is preserved.

Start with [personal CLI testing](docs/PERSONAL-VERIFICATION.md),
[AI disclosure](docs/AI-DISCLOSURE.md), [license status](docs/LICENSE-STATUS.md)
and the [current preparation handoff](reports/publication-preparation-handoff.md).
Original ChatGPT user prompts and personal review remain pending. This copy is
not authorized for publication, and historical Phase08 findings refer to the
original private tree/history; current candidate findings are reported separately.

Individual72-hour Associate AI Forward Deployed Engineer challenge. User-supplied
deadline: **October29,2026,13:52:35 IST**. Work stays local. Overall public release is **NO-GO** pending original ChatGPT
prompt inclusion, personal technical/content review, license decision and explicit
publication authorization. This preparation scans the separate candidate; prior
Phase08 history findings describe the original private development repository.

The application tracks approved roles, candidates, interviews, structured reviews
and independently approved offers. It generates a valid synthetic baseline,
retains audit history, then evaluates five deliberately invalid observations
against isolated ground truth. A reviewer can restore every relational record
from CSV, JSON or SQL and reproduce the findings/metrics without an online service.

## Quick start — review the included artifacts offline

Prerequisites: CPython **3.14.5** with venv/sqlite3, SQLite3.38+ (verified3.53.1),
POSIX filesystem utilities. Git is optional for archive builds; source fingerprints
identify an archive when Git metadata is unavailable. No project dependencies or API keys; no pip
installation. The Python pin must already be available locally. Only CPython3.14.5 with
SQLite3.53.1 on macOS was tested;3.38 is the SQLite feature floor, not a tested
minimum runtime. Python3.11/3.12/other versions and Windows/Linux are unverified.

```sh
python3 --version
python3 -m venv .venv
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/review-verification
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
```

Use a **new output path** for each run. Verification checks the manifest/files,
restores all three formats, runs99 domain checks on each, compares all24 tables,
and reproduces anomaly detection before comparing its findings to separate truth.
Artifact gzip files are transparently supported. The included dictionary is
`artifacts/data-dictionary.md`; `artifacts/manifest.json` inventories every file.
Private assignment PDFs are intentionally excluded and are **not needed** for
these runtime/tests/verification commands. The maintainer-only foundation smoke
checks their recorded identities and will fail honestly if they are absent.

Restore one format and run detection/evaluation separately:

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format json --database output/restored.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.evaluation_checks --database output/restored.sqlite3 --profile full --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/restored.sqlite3 --observations artifacts/anomalies/input/observations.json
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables evaluate --database output/restored.sqlite3 --directory artifacts/anomalies
```

Use `--format csv` or `--format sql` for other restorations. SQL procedure: in a
fresh empty SQLite database, execute `baseline/sql/schema.sql`, then decompressed
`seed.sql` (possibly `.gz`). Do not initialize metadata before the SQL seed.
The CLI implements this safe procedure; triggers and FK checks remain enabled.
`send_offer` records a synthetic local state and never sends messages.

## Regenerate and prove reproducibility

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables build --profile full --seed 20261022 --directory output/regenerated-package
PYTHONPATH=src .venv/bin/python3 scripts/verify_deliverable_reproducibility.py --profile full --seed 20261022 --directory output/two-full-packages
```

Build creates a fresh valid baseline, all CSV/JSON/SQL exports, independent imports
and row comparisons, the linked anomaly package, provenance, privacy checks and a
manifest. Two-run replay compares every artifact byte and every relational scalar,
with measured timings kept outside deterministic content. Starter uses the same
implementation (`--profile starter`). Existing outputs/symlinks are refused.

Export an already validated baseline:

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables export --baseline output/my-full.sqlite3 --profile full --seed 20261022 --directory output/exports-only
```

Existing generator modes remain supported:

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase master --profile starter --seed 20261022 --database output/master.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase interviews --profile starter --seed 20261022 --database output/interviews.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase evaluations --profile full --seed 20261022 --database output/my-full.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.anomalies --baseline output/my-full.sqlite3 --profile full --seed 20261022 --directory output/observations-only
```

## Entities, data and rules

Eleven core entities: Requisition, HiringManager, Candidate, Application,
SkillRequirement, InterviewPanel, Availability, Interview, Scorecard, Offer and
Approval. Staff, skills, panel memberships, participant snapshots, rubric items
and typed events bring the actual schema to24 tables/209 fields. Every table,
including SchemaMetadata and all event/bridge tables, is exported.

FULL: **200 requisitions,5000 candidates,8000 applications,2000 interviews**.
Starter:10/100/160/40. Scorecard/offer counts derive from explicit synthetic
coverage/policies, not employer-prescribed quotas. All candidate identities and
recruitment records are synthetic; contacts use example.invalid. No real resumes,
scraped profiles, confidential records or external personal dataset.

- Requisitions need approved criteria and compensation before scheduling.
- Half-open interview intervals permit back-to-back bookings; every assigned
  interviewer must be available/effective. Shared Staff and candidate conflicts
  are rejected atomically. Cancelled reservations release capacity.
- Withdrawal cancels scheduled bookings; rescheduling keeps the same interview ID
  and old/new snapshots. Events/participants cannot be silently overwritten.
- Assigned reviewers use relevant effective0–4 rubrics. Complete weighted totals
  use integer arithmetic; missing/incomplete required reviews cannot authorize
  progression. Reviewed and offer eligibility have separate thresholds.
- Offers use approved same-currency band snapshots and independent HR/admin
  approval. Hiring resolves sibling applications/reservations transactionally.

Actual synthetic policies/thresholds and limits are in the phase designs. They
are not claims about an employer's real recruiting decisions or empirical fairness.

## Five negatives and isolated truth

The canonical baseline stays valid/read-only. Separate typed before/after
observations represent missing-review advancement, shared-interviewer overlap,
over-band offer, withdrawn-but-scheduled booking and irrelevant rubric criterion.
All references/structure remain valid. Detector scans business records with the
same clean/anomalous engine. It receives **no truth or injection hints**.
Only the later evaluator reads ground_truth.csv/json for identity matching and
TP/FP/FN/precision/recall/F1. Duplicate detections do not earn repeated credit.
Controls include adjacent/cancelled interviews, exact upper band, relevant
criteria, incomplete cards without advancement and completed history before
later withdrawal. Expected semantic findings remain visible; they are not
misrepresented as a fully business-valid projection.

See `artifacts/anomalies/reports/evaluation.json` for actual measured metrics.
Perfect results on controlled cases do not establish generalization or accuracy
on unknown data. No TN universe is invented.

## Formats, architecture and artifact layout

```text
src/yottaflex/             # explicit business operations/generation/validation
artifacts/
  baseline/csv/           # every table, optional deterministic .gz
  baseline/json/          # every table, optional deterministic .gz
  baseline/sql/           # exact schema + complete seed
  baseline/catalog.json   # column/format/import/hash contract
  baseline/validation-summary.json
  baseline/round-trip-verification.json
  anomalies/input/observations.json
  anomalies/truth/ground_truth.csv + ground_truth.json
  anomalies/reports/      # actual findings/metrics/structure/control evidence
  data-dictionary.md
  provenance.json + privacy-scan.json + manifest.json
```

Python stdlib + local SQLite; no ORM, service, cloud, UI or paid dependency.
Operations use BEGIN IMMEDIATE with FK/protection triggers; unknown database
versions are refused without reset. Export/import follows actual schema and FK
order. CSV null=`\N`; literal leading backslashes are doubled; empty strings stay
empty. Every CSV field is quoted. JSON values retain integer/string/null types;
JSON-valued database text stays exact text. SQL literals are escaped without
float conversion; text NUL uses UTF-8 hex/CAST. All rows are PK-ordered.
Large text exports use deterministic gzip with fixed headers; all deliverables
remain inside this repository, with measured size/hash inventory. Manifest omits
its own hash and references external replay evidence to avoid circular hashing.
See the export design for limits, trusted-input policy and exact import procedure.

## Verification, transparency and remaining release work

```sh
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
# Maintainer source/foundation smoke (requires private assignment inputs):
PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh
```

Substantial AI assistance: ChatGPT helped interpret requirements, plan phases,
draft instructions and review Codex handoff reports; those ChatGPT reviews did
not execute the application or inspect the complete repository. Codex generated
code/tests/docs and executed the recorded technical checks. The candidate supplied
requirements/documents, directed phases and read reported progress. Personal
tests, every-line understanding and final security/privacy review are unconfirmed.
ChatGPT original user prompts are not yet included: follow docs/ai-history/chatgpt/README.md.
Known Codex prompts and honest export limitations are preserved in the journal.
Other-tool absence is not attested. See docs/phase08/ai-history-audit.md.

Privacy scans reduce accidental disclosure; they cannot guarantee privacy.
Generated artifacts are synthetic and scanned separately. In this candidate, copied historical report paths have explicit redaction markers
and a complete occurrence log; no original Git history/author metadata is present.
Original historical findings/reports remain as disclosed evidence, not a claim
that those private values remain in this candidate. Personal content review and
all-tools prompt completeness still precede publication. Original invitation
send time/round naming and portal-versus-email channel questions remain release
items. Nothing is pushed or submitted. Stop after this local publication-copy preparation
for review. No Git initialization or public history/publication was performed.

- [Current export/import design](docs/phase07/export-and-reproducibility-design.md)
- [Actual two-full-run evidence](docs/phase07/reproducibility-evidence.json)
- [Final audit handoff](reports/phase08-final-audit-handoff.md)
- [Final75-requirement audit](docs/phase08/final-requirements-audit.md)
- [Privacy/history strategy](docs/phase08/privacy-and-publication-review.md)
- [Personal verification checklist](docs/phase08/human-verification-checklist.md)
- [Walkthrough preparation](docs/phase08/interview-walkthrough.md)
- [Previous export handoff](reports/phase07-export-deliverables-handoff.md)
- [75 original requirements and phase overlays](docs/phase01/requirements.md)
- [Per-requirement current evidence](docs/phase07/requirements-acceptance.md)
- [Full prompt and human-review journal](docs/phase01/journal.md)
- [Schema dictionary](docs/data-dictionary.md)
- [Scheduling policy](docs/phase04/interview-workflow-design.md)
- [Evaluation/offer policy](docs/phase05/evaluation-offer-design.md)
- [Anomaly/matching policy](docs/phase06/anomaly-design.md)
