# Recruiting workflow architecture proposal

Source-backed Phase 01 design awaiting human review. All application paths and
commands below are **planned, not implemented**. Existing local Git, Markdown,
privacy rules and shell smoke are retained. See requirements.md for source IDs.

## Technology decisions

| Choice | Rationale | Trade-off |
| --- | --- | --- |
| CPython 3.14.5, standard library only | random/csv/json/hashlib/sqlite3/argparse/unittest cover required deterministic generation, exports, rules, metrics | Exact runtime pin improves replay; write explicit validation/serialization |
| Local SQLite through sqlite3 | FK/UNIQUE/CHECK, transactions, SQL seeds; required volumes need no server | Temporal overlaps/stage policy need transactional Python rules, not CHECK alone |
| CLI `python -m yottaflex` | Working local end-to-end interface and reproducible commands; no mandated web UI | Less visual; provide scenario walkthrough and readable decision/audit output |
| One package, SQL and ordinary functions | Easy to inspect/understand in individual challenge | Keep IO/rules boundaries clear; no ORM, DI, generic repository or microservices |
| Original synthetic inputs, rule-derived outcomes | Lawful/local, fixed-seed generation, no paid inference/external data | Distributions/policy are documented assumptions, not empirical company facts |
| Canonical CSV + JSON + SQL, separate truth | Full exports/replay/evaluation without leakage | More serialization checks; evaluator is the only module allowed truth input |
| Markdown + local Git | Portable prompt/design/verification evidence, meaningful evolution | Raw assignment sources private; publish locators/checksums, not application portal identifiers |

No third-party runtime dependencies, hosted service, frontend build chain,
container, external dataset or application LLM selected. AI tooling is permitted,
not a required product feature. No numeric latency/accuracy/SLA invented.

## Planned layout and dependencies

```text
src/yottaflex/
  __init__.py, __main__.py  CLI and dispatch
  schema.sql, db.py         explicit tables, constraints and transactions
  workflow.py              stage/schedule/score/offer/withdrawal rules and events
  generate.py              dependency-ordered valid baseline, isolated injection
  validate.py              independent structural/semantic checks, NO truth input
  export.py                canonical table exports and manifests
  evaluate.py              compare findings to truth AFTER validation
tests/                     focused rules, boundaries, rollback, import/replay
docs/data-dictionary.md    every actual field's required metadata (Phase 02)
artifacts/exports/<profile>/ reviewed synthetic input tables in all three formats
artifacts/truth/<profile>/   ground_truth.csv and .json, not input features
artifacts/reports/<profile>/ counts, validation/evaluation/checksum manifests
```

CLI -> direct functions; generation calls shared normal workflow rules; validation
independently recomputes key checks. Explicit fixture-only injection can create
semantic anomalies; normal commands cannot bypass guards. Only evaluation reads
truth, after findings exist, so truth cannot influence decisions or detection.
SQLite is shared through small explicit helpers, no framework abstractions.

`data/`, `tmp/`, `output/` remain ignored scratch. Final synthetic exports must
eventually be reviewed and explicitly staged under artifacts/; ignore rules do
not excuse omission of required deliverables. Original docs stay ignored.

## Dependency-ordered generation plan

1. Fixed config/seed 20261022, logical epoch, full/starter counts, role/skill/stage
   distributions, currency/bands and versioned policies.
2. Staff -> HiringManager -> Requisition/SkillRequirement and requisition Approval;
   Candidate -> Application after both candidate and requisition exist. P calls
   Application master data but its FKs still require this ordering.
3. InterviewPanel -> effective PanelMember -> staff Availability.
4. Interview/InterviewParticipant snapshots/events -> Scorecard/ScorecardItem.
5. Offer derived from application/requisition band -> offer Approval/history.
6. Derive projections/scores/dates, strictly validate clean baseline.
7. Copy clean baseline and inject all five deterministic labelled negatives,
   preserving required entity counts, valid FKs/types and unrelated records.
8. Export all tables, isolated truth and source/config/validation manifests;
   validate input artifacts alone, then evaluate against truth.
9. Generate twice independently using same seed/config/runtime; compare canonical
   counts/hashes and record real duration/metrics.

Full = exactly 200 requisitions / 5,000 candidates / 8,000 applications / 2,000
interviews. Proposed starter = 10/100/160/40, same code path and all scenarios.
Supporting counts are deterministic and reported; the assignment gives no exact
targets for them. Clean and injected full snapshots both retain core totals.

## Workflows and transaction boundaries

| Operation | Preconditions -> state/event effects |
| --- | --- |
| Approve/open requisition | Valid manager/band/criteria -> Approval plus requisition history |
| Apply/transition | Valid candidate + approved open role; unique pair; versioned allowed stage/review gates -> ApplicationEvent |
| Schedule/reschedule | Active application, effective panel, availability, no overlapping booking for ANY shared interviewer -> interval + participant snapshot + old/new interval event |
| Withdraw | Candidate/global or application-specific withdrawal -> terminal stage and cancel future bookings, retain cancellation history |
| Score | Participant reviewer, correct role/rubric and allowed values -> structured items, derived total/completion; revisions keep history |
| Offer/approve | Eligible stage/reviews, approved band/currency -> Offer/Approval and decision/actor/reason events |
| Validate/export/evaluate | Read-only independent findings -> separate evaluator consumes truth -> transparent reports |

Each mutating command validates, changes projection and appends history in one
transaction. Booking uses a write transaction across checking and reservation;
reject invalid operations without partial changes. Half-open [start,end) intervals
allow adjacent slots; check actual participant snapshots across different panels.

## Determinism, isolation and metrics

- Explicit seeded random.Random; fixed logical epoch, stable iteration/counters,
  given immutable ID patterns, no random UUIDs or wall time in generated data.
- UTF-8/LF, declared column ordering, sorted rows/JSON keys, deterministic SQL,
  integer compensation minor units with currency, documented rubric rounding.
- UTC-aware timestamps; supplied deadline/display IST. Effective criteria/bands
  are versioned; prior reviews/offers do not inherit later changed rules.
- Seed/config/schema/generator/environment versions in manifest. Canonical text
  exports are hashed; SQLite binary bytes are not a portability/replay oracle.
- Baseline zero structural/semantic errors; injected fixture keeps structural
  integrity while independent checks expose known semantic failures. Report
  additional real findings, never silently whitelist with ground truth.
- Metrics: entity/stage/outcome counts, scenario/rule coverage, findings and
  unexpected errors, known-anomaly precision/recall, invalid-operation rejection,
  incomplete-review rate, replay hashes/counts and measured duration. Thresholds
  not supplied; detecting all planted scenario families is a declared test goal.

## Foundation now and next gate

`.python-version` pins 3.14.5; pyproject.toml declares zero runtime dependencies.
`python3 -m venv .venv` uses the installed interpreter with no downloads/install.
Observed environment: CPython 3.14.5 / SQLite 3.53.1. Bundled pypdf/pypdfium2 are
source-review tooling only, not application requirements.

The current smoke checks setup, local IO, private paths, source identities,
runtime/SQLite transactions and tracked-file privacy. No schema, generator,
workflow, validator or domain tests are implemented. After human review, Phase 02
should start with complete field dictionary/schema and clean starter generation.
