# Phase 03 deterministic master/application data

Scope: Staff/HiringManager, approved/open requisitions and criteria, candidate
profiles/skills, initial applications and causal history. No interview/calendar/
panel generation, scheduling, evaluations, offers, anomalies/truth/evaluator,
complete exporters, web/API or hosted services. These are synthetic assumptions,
not real hiring policies or empirical population distributions.

## Configuration and necessary schema correction

| Profile | Requisitions | Candidates | Applications | Interviews |
| --- | --- | --- | --- | --- |
| starter | 10 | 100 | 160 | 0, deferred |
| full | 200 | 5,000 | 8,000 | 0, deferred |

Same generate_database/_populate implementation, frozen GenerationConfig, default
seed 20261022, logical origin 1767225600 = 2026-01-01T00:00:00Z. Tiny Python-only
custom scales test boundaries; named CLI profile counts cannot be overridden.
Seed range 0..2^63-1; custom counts must fit pair and six-digit identity capacity.

The v1 schema had no candidate experience or role minimum-proficiency fields.
Only required Candidate.experience_years (INTEGER 0..50) and
SkillRequirement.min_proficiency (INTEGER 0..4) added: schema v2, 24 tables/209
fields. They store genuine requested input attributes, not redundant fit scores.
Seniority/category use readable title/catalogue, no extra columns. Existing v1
databases are refused unchanged; no migration/backfill/reset was run or added.
Old schema/reports remain in Git. Regression tests cover v1 preservation and
new ranges/nullability; dictionary regenerated/checked against actual SQL.

## Randomness, IDs and ordering

SHA256 of `yottaflex:phase03:v1:<seed>:<domain>` seeds independent random.Random
streams for requisitions, candidates and applications. Explicit catalogue and
PK sorting, stable tie-breaks and LF SQL source avoid hash/filesystem/SQL implicit
order dependence. No wall clock, absolute path or UUID goes into generated rows.

Required IDs: REQ-2026-000001, CAND-000001, literal APP-<candidate-id>-<req-id>.
Supporting: STAFF-/HM-/SKILL-/APR-/REQEV-/APREV-/CANEV-/APPEV- plus independent
positive six-digit counters. Per-entity history sequences start at 1. Staff first
four = system/HR/operations/admin, then managers. No future INT/SCORE/OFF/panel/
availability IDs allocated. Future phases can append after existing maxima.

## Dependency order and causal approval/history

1. Staff (valid from origin minus one day), then manager profiles. Manager count
   min(R,max(2,min(20,ceil(R/10)))): starter 2, full 20.
2. Requisition draft at seeded time within first 90 days; creation event contains
   category/seniority and generator config. Four criteria at creation +60 seconds.
3. At +1h, draft -> pending_approval, create pending Approval and request event.
   Criteria precede approval intentionally because policy inspects stored facts.
4. Actual policy: pending role, active manager, independent active HR approver,
   positive coherent currency band below cap, four active criteria with required
   skills, weights exactly 10,000. INR cap 500,000,000 minor units; USD 25,000,000.
5. At +2h, approved Approval/ApprovalEvent and RequisitionEvent with immutable band
   snapshot. At +3h, approved -> open with event. Current open status is separate
   from approved authorization; decisions are never independently randomized.
6. Candidate profiles, then skills/events, creation within first 120 days.
7. Applications at max(candidate creation, role opening) +60 seconds..30 days,
   always applied with one created/submitted event. No invented submitted enum,
   advanced stages or missing review prerequisites. Projections agree with events.

Every event retains owner/actor FKs, reason/correlation, sequence, deterministic
occurrence/recording time and before/after status snapshots. Master approval is
the bounded generation policy requested here, not a general workflow engine.

## Catalogue, distributions and correlations

Eight skills: python, sql, backend, cloud, api_integration, data_analysis,
ml_fundamentals, problem_solving. Each role uses four, not all skills.

| Role | Criteria and base percentage (optional marked) |
| --- | --- |
| Backend Engineer | backend 35, python 30, api_integration 20, sql 15 optional |
| Data Analyst | sql 35, data_analysis 35, python 20 optional, problem_solving 10 |
| Integration Engineer | api_integration 40, backend 25, cloud 25, problem_solving 10 optional |
| Applied AI Engineer | python 35, ml_fundamentals 35, sql 20, cloud 10 optional |

Categories cycle in catalogue order; Junior/Mid/Senior cycle by groups of four.
Required minimums 2/3/4; optional minimum one less. Weights receive seeded +/-300
basis-point perturbation, then integer largest-remainder normalization to exactly
10,000; catalogue order breaks ties.

Candidate experience buckets cycle 0..2 /3..6 /7..15 years; years vary by seed.
Primary specialization cycles roles. Four primary skills have levels bucket+1
or bucket+2; each extra skill has 35% inclusion and shallower level. Thus depth
correlates with experience. Placeholder names and example.invalid contacts only.
No real identities, external datasets, scraping or licensed corpus.

Currency expected 80% INR/20% USD; actual distribution reported. Annual junior/
mid/senior bases: INR 900,000/1,700,000/2,800,000; USD 60,000/100,000/150,000 major
units. Role multipliers 100/95/105/115%; lower +/-10%, upper adds 30% of role base.
Store integer minor units, 100 minor/major. These are arbitrary synthetic bands.

## Fit and allocation

Inputs queried from actual CandidateSkill/SkillRequirement. For weight w,
minimum m and candidate level l (missing=0), contribute `w*min(l,m)//m`, or w if
m=0. Sum gives 0..10,000 basis points; floor per criterion. Count missing required
criteria. Excellent = no missing required and score>=8,500; borderline = remaining
score>=6,000; weak = rest. Descriptive report categories, not hiring outcomes or
anomaly truth; no fit column or ground-truth label persisted in input records.

Applications evenly allocated (starter 16/role, full 40/role). Target mix 40%
excellent/35% borderline/rest weak, sampled without replacement from derived
pools. Scarce pools deterministically fall back to unselected candidates; actual
mix reported. Candidates may apply to several roles or none. No random hires/
rejections. Candidate profiles/skills do not depend on application outcomes.

## Safety, validation, reproducibility and performance

Every existing output is refused, even empty/initialized files and dangling
symlinks. No force option. An owned private sibling scratch DB is initialized,
populated under BEGIN IMMEDIATE, validated/measured/hashed, committed and closed;
same-directory hard link atomically publishes without replacing another writer.
Failures roll back/remove owned scratch and never publish partial results.
Random scratch filenames are IO safety only, not data/IDs. Local filesystem hard
link support required. Parent directories created, unrelated files never reset.

Measured checks: counts/deferred emptiness, every PK/FK/required field, SQLite
integrity, IDs/pairs, logical/causal dates, initial enums, weights/ranges/catalogue,
approval/actor/projection/history/snapshot consistency and no truth-label keys.
Focused Phase 03 checks, not future anomaly or end-to-end workflow validation.
Summary includes seed/profile/origin/schema, all counts/approvals, application
density, experience/proficiency/role/seniority/currency/compensation and fit metrics.
Unavailable scheduling/review/offer/anomaly metrics are named, not invented.

Canonical streaming: sorted table names, declared PK order; compact sorted-key
ASCII JSON {table,columns} header +LF, schema-column row arrays +LF. SHA256 per
table; dataset SHA256 of compact sorted-key JSON table->{rows,sha256}. Compare two
runs' counts, every ordered record, summaries and hashes. Never SQLite binary
hashes. perf_counter operation duration is separate, excluded from canonical data
and deterministic summary. It includes initialization/generation/validation/
summary/hash/publication. Recorded runtime portability beyond observed environment
is not claimed.

Matching O(R*C*4), memory candidate/skill/requirement maps and one role's candidate
pool, not Cartesian-product storage. Batches <=256 candidates/apps plus dependents.
No multiprocessing, distributed service, network, ORM or new dependencies.

## Commands (new output paths/directories only)

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --profile starter --seed 20261022 --database output/phase03/my-starter.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --profile full --seed 20261022 --database output/phase03/my-full.sqlite3
PYTHONPATH=src .venv/bin/python3 scripts/verify_generation_reproducibility.py --directory output/phase03/my-replay --profile both --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh
```

CLI stdout = deterministic summary/canonical proof plus separate elapsed_seconds.
Replay writes diagnostics/proof JSON and scratch DBs, not complete data exporters.
Measured evidence retained in reproducibility-evidence.json and final handoff.

validate_generated deliberately enforces Phase 03's applied-only/empty-downstream
scope. After later augmentation, use phase-aware/composed validation rather than
interpreting this initial-scope check as finished-workflow acceptance.

Limits: designed synthetic balance, tiny-scale scarcity and exact runtime context.
Not a complete challenge dataset: 2,000 interviews, calendars/panels, scorecards,
offers/offer approvals, withdrawals/rescheduling, negatives/truth/evaluation and
CSV/JSON/SQL exports remain later. Stop for review before Phase 04.
