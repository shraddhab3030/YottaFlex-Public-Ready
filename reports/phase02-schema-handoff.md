> Publication-copy notice: private home-path identifiers are replaced by `<private-home>/`. Technical results remain historical evidence. Every redaction is logged in docs/publication-preparation/redaction-log.json; the original private report/history is unchanged.

# YottaFlex Phase 02 - schema handoff

**Assessment: PASS for Phase 02 schema/dictionary/integrity deliverables.**
Human Phase 02 review is pending. Phase 03 has not started. No full generator,
workflow implementation, scheduling/scoring engine, injection, exporter, API,
frontend, publication, recruiter contact or submission was performed.

## Executive summary and continuation context

Individual Associate AI Forward Deployed Engineer 72-hour Code Challenge.
Project: <private-home>/Documents/Personal/Projects/Assignment/YottaFlex.
Deadline: October 29, 2026, 1:52:35 PM IST (2026-10-29T13:52:35+05:30).
Preserved branch: codex/phase-01-foundation. Existing commits: 7e5a77b (completed
Phase 01), baafb55 (initial missing-source foundation). User explicitly approved
Phase 01 progression in the full Phase 02 attachment; this authorizes only schema,
dictionary and structural tests. Stop for review after Phase 02. Keep everything
local; eventual public repo only after complete-project review. No secrets or real
candidate information. Produce a downloadable handoff after every task.

Implemented Python stdlib/SQLite relational foundation: 24 STRICT tables, all
11 mandatory core entities, 207 documented fields, 45 FK groups/51 FK column links,
42 protection triggers. Focused tests use 24 literal fixture rows plus metadata
in isolated memory/temp-file databases, not a full synthetic dataset generator.
Final suite: 33 tests passed. Dictionary freshness, CLI fresh/repeat initialization
and existing foundation/source/privacy checks passed; evidence is below.

## Source and prompt verification

Re-read AGENTS.md, README.md, all Phase 01 architecture/requirements/model/risk
files, entire problem statement and complete text of both one-page official PDFs.
Sources remain unchanged/ignored and match the prior SHA256 manifest. Candidate-
supplied problem transcription remains specification by user direction; PDFs
supplement submission requirements. No authenticated portal access, network call,
external dataset, paid service or third-party runtime dependency was introduced.
Existing deadline/channel/round-label questions remain release-time risks.

The complete Phase 02 attachment is stored byte-for-byte at docs/phase02/prompt.md
and linked as P004 in docs/phase01/journal.md; SHA256:
e7959933c14de0ee5e2bda549573dd05100df53a2f89631bbfc137e5b27d1693.
User message accompanying it: `here is next`. Earlier prompts/history preserved.

## Files created and modified

Created (10):

- src/yottaflex/__init__.py - package boundary, no workflow functionality.
- src/yottaflex/schema.sql - explicit static DDL, keys/checks/indexes/triggers.
- src/yottaflex/db.py - FK-enabled connections and safe initialization/verification CLI.
- tests/fixtures.py - tiny literal synthetic integrity fixtures only.
- tests/test_schema.py - 33 unittest methods, many field/FK/range subtests.
- scripts/build_data_dictionary.py - SQL annotations + SQLite introspection renderer/checker.
- docs/data-dictionary.md - all 207 fields, all required metadata and exact DDL.
- docs/phase02/prompt.md - complete user prompt, unchanged bytes.
- docs/phase02/schema-design.md - design choices and structural/business boundary.
- reports/phase02-schema-handoff.md - this standalone handoff.

Modified (5): AGENTS.md (authorized scope/commands); README.md (current state/setup);
pyproject.toml (description/source execution, still zero dependencies);
docs/phase01/requirements.md (status overlay only; all 75 original rows unchanged);
docs/phase01/journal.md (P004, progression approval, AI work/tests/failed-run disclosure).

Preserved: branch/prior commits, original source files and source manifest,
Phase 01 architecture/model/risk snapshots, all old reports, .gitignore,
.python-version (3.14.5), shell/runtime/privacy smoke scripts. No unrelated refactor.
Ignored scratch includes static-DDL authoring script and two metadata-only smoke
SQLite files under tmp/. The earlier smoke file records an earlier in-progress
schema and is not reset; the final one is tmp/phase02-final-schema-smoke.sqlite3.
No scratch or database file belongs in Git.

## Database table inventory

All have explicit PK and STRICT storage; optional lifecycle status applies where
meaningful. Immutable event/assignment/metadata rows do not have a mutable status
column merely for uniformity. Event previous/new status are typed subject enums.

| Table | Fields | Primary key | Purpose |
| --- | --- | --- | --- |
| SchemaMetadata | 4 | singleton | Singleton version and schema fingerprints; no domain data |
| Staff | 6 | staff_id | Synthetic staff/system actors and interviewers |
| HiringManager | 6 | hiring_manager_id | Manager profile with one Staff identity |
| Candidate | 6 | candidate_id | Synthetic candidate profiles; no real candidate records |
| CandidateSkill | 4 | candidate_id, skill_key | Structured candidate skill levels |
| Requisition | 10 | requisition_id | Role, compensation band and lifecycle projection |
| SkillRequirement | 10 | skill_requirement_id | Versioned requisition criteria and rubric weights |
| Application | 6 | application_id | Candidate/requisition relationship and stage projection |
| InterviewPanel | 6 | panel_id | Requisition-specific panel definition |
| PanelMember | 5 | panel_id, staff_id, valid_from | Effective panel/staff many-to-many membership |
| Availability | 5 | availability_id | Interviewer calendar intervals, not scheduling algorithm |
| Interview | 7 | interview_id | Scheduled interview projection linked consistently to application and panel |
| InterviewParticipant | 4 | interview_id, staff_id | Immutable snapshot of assigned interview members |
| Scorecard | 8 | scorecard_id | One structured scorecard per assigned reviewer/interview |
| ScorecardItem | 6 | scorecard_id, skill_requirement_id | Structured rubric evidence and criterion score |
| RequisitionEvent | 16 | event_id | Append-only Requisition audit history |
| Offer | 10 | offer_id | Offer projection; scalar amount validated, band eligibility remains business rule |
| Approval | 10 | approval_id | Decision record targeting exactly one requisition or offer |
| ApplicationEvent | 13 | event_id | Append-only Application audit history |
| InterviewEvent | 13 | event_id | Append-only Interview audit history |
| OfferEvent | 13 | event_id | Append-only Offer audit history |
| ApprovalEvent | 13 | event_id | Append-only Approval audit history |
| ScorecardEvent | 13 | event_id | Append-only Scorecard audit history |
| CandidateEvent | 13 | event_id | Append-only Candidate audit history |

## Eleven-entity coverage matrix

I = structural implementation, T = actual integrity tests, D = complete dictionary.
These flags do not mean the corresponding business workflow is implemented.

| Required core entity | I / T / D | Main structural evidence |
| --- | --- | --- |
| Requisition | yes / yes / yes | Manager FK, deterministic ID, lifecycle/band/currency/effective checks |
| HiringManager | yes / yes / yes | Unique Staff profile FK, effective dates, active/inactive |
| Candidate | yes / yes / yes | Immutable ID, synthetic optional contact, withdrawal timestamps |
| Application | yes / yes / yes | Candidate/requisition FKs, unique pair, exact composite ID |
| SkillRequirement | yes / yes / yes | Role FK, natural version key, weights/required flag/rubric bounds |
| InterviewPanel | yes / yes / yes | Role FK, effective dates and membership bridge |
| Availability | yes / yes / yes | Staff FK, natural calendar key, positive UTC interval |
| Interview | yes / yes / yes | Same-role application/panel composite FKs, positive duration |
| Scorecard | yes / yes / yes | Exact ID, unique reviewer pair, assigned-participant FK, scalar total range |
| Offer | yes / yes / yes | Exact ID, positive amount, matching band-snapshot currency/role, one active final |
| Approval | yes / yes / yes | Exactly one requisition/offer target, approver FK and decision dates |

## FK relationship summary

Every group below has invalid-reference rejection coverage; delete/update actions
are RESTRICT. Composite groups are single relationships with multiple columns.
PK/natural uniqueness and join controls are also independently inspected/tested.

| Child | Foreign key -> parent |
| --- | --- |
| HiringManager | (staff_id) -> Staff (staff_id) |
| CandidateSkill | (candidate_id) -> Candidate (candidate_id) |
| Requisition | (hiring_manager_id) -> HiringManager (hiring_manager_id) |
| SkillRequirement | (requisition_id) -> Requisition (requisition_id) |
| Application | (requisition_id) -> Requisition (requisition_id) |
| Application | (candidate_id) -> Candidate (candidate_id) |
| InterviewPanel | (requisition_id) -> Requisition (requisition_id) |
| PanelMember | (staff_id) -> Staff (staff_id) |
| PanelMember | (panel_id) -> InterviewPanel (panel_id) |
| Availability | (staff_id) -> Staff (staff_id) |
| Interview | (panel_id, requisition_id) -> InterviewPanel (panel_id, requisition_id) |
| Interview | (application_id, requisition_id) -> Application (application_id, requisition_id) |
| InterviewParticipant | (staff_id) -> Staff (staff_id) |
| InterviewParticipant | (interview_id) -> Interview (interview_id) |
| Scorecard | (interview_id, reviewer_staff_id) -> InterviewParticipant (interview_id, staff_id) |
| Scorecard | (reviewer_staff_id) -> Staff (staff_id) |
| Scorecard | (interview_id) -> Interview (interview_id) |
| ScorecardItem | (skill_requirement_id) -> SkillRequirement (skill_requirement_id) |
| ScorecardItem | (scorecard_id) -> Scorecard (scorecard_id) |
| RequisitionEvent | (actor_candidate_id) -> Candidate (candidate_id) |
| RequisitionEvent | (actor_staff_id) -> Staff (staff_id) |
| RequisitionEvent | (requisition_id) -> Requisition (requisition_id) |
| Offer | (approved_requisition_event_id, requisition_id, currency) -> RequisitionEvent (event_id, requisition_id, currency) |
| Offer | (application_id, requisition_id) -> Application (application_id, requisition_id) |
| Approval | (approver_staff_id) -> Staff (staff_id) |
| Approval | (offer_id) -> Offer (offer_id) |
| Approval | (requisition_id) -> Requisition (requisition_id) |
| ApplicationEvent | (actor_candidate_id) -> Candidate (candidate_id) |
| ApplicationEvent | (actor_staff_id) -> Staff (staff_id) |
| ApplicationEvent | (application_id) -> Application (application_id) |
| InterviewEvent | (actor_candidate_id) -> Candidate (candidate_id) |
| InterviewEvent | (actor_staff_id) -> Staff (staff_id) |
| InterviewEvent | (interview_id) -> Interview (interview_id) |
| OfferEvent | (actor_candidate_id) -> Candidate (candidate_id) |
| OfferEvent | (actor_staff_id) -> Staff (staff_id) |
| OfferEvent | (offer_id) -> Offer (offer_id) |
| ApprovalEvent | (actor_candidate_id) -> Candidate (candidate_id) |
| ApprovalEvent | (actor_staff_id) -> Staff (staff_id) |
| ApprovalEvent | (approval_id) -> Approval (approval_id) |
| ScorecardEvent | (actor_candidate_id) -> Candidate (candidate_id) |
| ScorecardEvent | (actor_staff_id) -> Staff (staff_id) |
| ScorecardEvent | (scorecard_id) -> Scorecard (scorecard_id) |
| CandidateEvent | (actor_candidate_id) -> Candidate (candidate_id) |
| CandidateEvent | (actor_staff_id) -> Staff (staff_id) |
| CandidateEvent | (candidate_id) -> Candidate (candidate_id) |

Cardinalities: HiringManager 1:N Requisition; Candidate N:M Requisition through
Application; requisition 1:N criteria/panels; panel N:M Staff through effective
PanelMember; Staff 1:N Availability; application/panel 1:N Interview; Interview
N:M Staff through immutable participant snapshots; interview 1:N Scorecard with
unique assigned reviewer pair; scorecard 1:N items; application 1:N Offer with
at most one active final; requisition/offer each 1:N Approval with target XOR.
Entity 1:N typed events; required Staff recording actor, optional Candidate origin.

## Design decisions, initialization and trade-offs

- CPython 3.14.5 / local SQLite 3.53.1 observed, SQLite 3.38+ required for STRICT
  and built-in JSON. No third-party runtime/test dependency, ORM or framework.
- Static SQL and a small module using direct sqlite3 functions, not a generic
  repository/DI/migration framework. Source-tree execution: PYTHONPATH=src.
- Timestamp refinement: UTC whole-second epoch INTEGER 0..253402300799, not the
  earlier proposed ISO text; allowed by explicit Phase 02 instructions. No floats,
  date strings or implicit wall-clock defaults. Half-open intervals and optional
  open-ended valid_to. Future display conversion may use IST.
- Amounts integer minor currency units, synthetic convention 100 minor/major unit.
  Currency three uppercase letters (not externally verified currency catalogue).
  Offer joins its immutable band snapshot on requisition/currency; comparing its
  amount with that band remains a business rule. Weights basis points 1..10000,
  raw rubric integer 0..4, optional total thousandths 0..4000; no scorer exists.
- Composite FK join keys in Interview/Offer are intentional constrained redundancy.
  Scorecards require existing assigned participants, criteria must exist; reviewer
  eligibility and role/rubric applicability remain future checks.
- All PKs immutable. Typed events and InterviewParticipant/SchemaMetadata reject
  UPDATE, DELETE and duplicate replacement inserts, even when recursive DELETE
  triggers are disabled. This protects normal use, not a malicious database owner.
- Typed events retain identity/subject/sequence/type/previous/new status, actor,
  occurred/recorded time, reason/correlation and JSON object snapshots for changed
  non-key slots/items/etc. SQL checks JSON shape, not payload meaning. No truth
  labels or undeclared FK relationships should be hidden in snapshots.
- SQLite INTEGER PRIMARY KEY initially accepted explicit NULL via implicit rowid
  allocation. A new test caught it for metadata. Final SchemaMetadata is STRICT
  WITHOUT ROWID, requiring explicit singleton 1 and valid version/hash fields.
- initialize uses BEGIN IMMEDIATE before version/emptiness checks and executes
  complete DDL statements transactionally. Fresh v0 only, repeat identical v1 is
  safe/no-op verification of fingerprints and FK integrity. Unknown/populated
  unversioned databases, active caller transactions and drift are refused.
- Metadata source/catalog hashes and PRAGMA user_version=1 detect accidental drift.
  No reset/migration command. Future schema changes need explicit versioned
  migration/tests; even annotation changes alter source fingerprint. No populated
  database is silently cleared, upgraded or repaired. Database files stay ignored.

Final schema SHA256:
ca0f9f3588c1e653877de2b7c0d5afa80bf4e5068da5b45151fcc143daa9fa3e.
Complete field-level dictionary and exact trigger/index DDL: docs/data-dictionary.md.

## Database constraints vs deferred business rules

| Enforced/tested storage | Deferred rules / future tests (not claimed passing) |
| --- | --- |
| Keys/FKs/types/nullability/natural uniqueness | Generated full-volume/cross-export joins and duplicate detection |
| ID patterns, immutable keys | Seeded counters, deterministic full generation, replay/checksums |
| Epoch ranges/positive intervals/same-row dates | Double booking, calendar coverage, effective members, rescheduling/withdrawal cancellation |
| Enum membership and timestamp-state consistency | Legal stage/role transitions and required-review gates |
| Band shape, integer amount/rubric ranges, currency snapshot link | Actual offer eligibility/band comparison, approval authority, score calculations/reconciliation |
| Assigned participant FK, existing criterion FK, unique reviewer | Rubric relevance/version, required criteria, completion gates |
| Append-only events, per-subject sequence uniqueness, JSON object snapshots | Sequence continuity, payload meaning, event/projection agreement and atomic mutations |
| Structural storage supporting known anomaly types | All five injections, truth isolation/evaluation, exports and metrics |

No generator, full 200/5,000/8,000/2,000 data, workflow operations, schedule/scorer,
negative-case injection, export engine, web/API or automated submission exists.

## Exact verification commands and actual results

Run from project root unless stated. PYTHONPATH points at local source; no install.

1. `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v`
   - Initial suite: exit 0, 30 tests in 0.653s, OK.
   - Expanded metadata coverage: exit 1, 31 tests in 1.301s, one failure:
     metadata singleton NULL insertion did not raise IntegrityError. Disclosed,
     fixed using WITHOUT ROWID; no result fabricated or failure hidden.
   - After correction: exit 0, 31 tests in 0.772s, OK.
   - Snapshot coverage: exit 0, 32 tests in 0.799s, OK.
   - Staged review found SQL LIKE underscore wildcard could hide a populated
     sqliteXuser table from initialization checks. Switched both catalog filters
     to exact GLOB sqlite_* and added a preservation regression.
   - Final suite: exit 0, 33 tests in 0.792s, OK.

```text
Ran 33 tests in 0.792s
OK
```

2. `PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py`
   - Exit 0 after each intentional DDL/dictionary refinement; generated complete
     final 207-field dictionary from SQL+SQLite, no dataset generated.
3. `PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check`
   - Exit 0, final dictionary exactly matches all annotated fields and constraints.
4. Final-file CLI verification (both exit 0):

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.db tmp/phase02-final-schema-smoke.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.db tmp/phase02-final-schema-smoke.sqlite3
```

```text
Schema version 1 initialized/verified; no domain rows generated
Schema version 1 initialized/verified; no domain rows generated
```

5. Inline Python reopened final file through connect/initialize: exit 0,
   24 tables, 207 fields, zero domain rows; actual schema SHA256 recorded above.
   A prior preliminary CLI file was initialized/repeated successfully too, before
   the final audit-snapshot refinement; not reset or misreported as final schema.
6. `PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh`
   - Existing Phase 01 four shell + three Python groups passed at earlier
     checkpoints (25 then 26 publication candidates as files were added). Final
     report-inclusive run exited 0 with 27 candidates, all four shell checks and
     three Python groups passed. A subsequent dictionary --check also exited 0.

```text
PASS: isolated project Git root
PASS: required foundation documents exist
PASS: private inputs, common credentials, and generated paths are ignored
PASS: synthetic local write/read round-trip
PASS: pinned Python 3.14.5; SQLite 3.53.1 FK and rollback
PASS: all three sources readable and match recorded SHA256/size/signatures
PASS: 27 tracked/untracked publication candidates exclude private paths/keys
Foundation Python checks passed: 3 groups. No application validation executed.
Foundation smoke passed: 4 shell checks + 3 Python groups. Application checks remain pending.
```

7. `git diff --check`: exit 0 for tracked changes; final staged whitespace and
   content review follows after report creation. No raw source/database staged.
8. Inline Python compared exact 75 original matrix rows against
   `git show 7e5a77b:docs/phase01/requirements.md`: exit 0, all unchanged. It also
   verified full Phase 02 prompt SHA256 and zero domain rows in CLI smoke file.
9. Source inspection commands: git status/log, rg file inventory, cat all relevant
   docs/full statement; bundled pypdf extraction of both entire PDFs: exit 0.
   Initial combined output was truncated; requirements/model/risk files were read
   again separately. Existing branch clean at start. No remote configured.
10. Staged index/content review: git add of fourteen exact Phase 02 implementation
    files, git diff --cached --check/--stat/--name-only and targeted staged diff:
    exit 0, intended scope only. Raw assignment/database files remain untracked/
    ignored; final report deliberately reserved for a separate documentation commit.
    rg scan for stale field-count/runtime strings returned exit 1 (no matches),
    so its chained status command did not execute; later explicit status did.
11. Schema authoring helper under ignored tmp/ wrote only static SQL: exit 0;
    fresh/repeat in-memory initialization and catalog/FK probes exited 0.
    File edits used apply_patch/Python; one documentation patch-context mismatch
    was rejected without changes, then corrected. No such tool failure was a test.

## Requested test coverage map

All are actual structural tests, not domain acceptance or full-scale claims.

| Requested check | Evidence |
| --- | --- |
| 1-2 all eleven core tables / PK each | inventory and PK/STRICT metadata test covers all 24 tables |
| 3-4 required FKs / invalid references | exact FK graph test and missing-reference subtests for all 45 groups |
| 5 duplicate PKs | every table, including protected history/metadata |
| 6 duplicate application pair | natural UNIQUE index and duplicate/composite-ID rejection |
| 7 invalid statuses | every domain/support status and event enum |
| 8 compensation | negative/reversed bands, integer storage, matching currency link |
| 9 rubric bounds | level/item/total/weight/version/flag ranges and positive endpoints |
| 10 date/intervals | all time fields reject text/fraction/negative/out-of-range, zero/reversed intervals, causal dates |
| 11 unique reviewer pair | UNIQUE pair + exact ID + assigned-participant FK |
| 12 approval targets | neither/both invalid; either single valid subject accepted |
| 13 empty initialization | memory and local file, deterministic metadata |
| 14 safe repeat | populated literal fixture dump unchanged; reopening temp file preserves row |
| 15 event history | required audit fields, actor FKs, unique sequence, immutable update/delete/replace; JSON snapshots |
| 16 cross-table references | full candidate/application/role/interview/scorecard/offer join and FK/integrity checks |
| 17 isolated databases | memory per test, isolated temporary files, corruption/drift rollback tests |
| 18 original smoke | four shell plus three runtime/source/privacy groups, recorded separately |
| Additional safeguards | caller transaction preservation, unknown DB/version refusal, source/catalog drift, atomic failed DDL, dictionary freshness/all fields |

## Traceability changes

All 75 original requirement rows preserved verbatim, with an appended Phase 02
I/T/Doc/deferred overlay. D01/D02 structural schema/dictionary implemented and
tested; D03-D05/D07-D08 and V01-V04/V07 have structural coverage. F01-F12,
D18/D20/D22, V05/V06/V08-V11 and S01/S03-S09/S15 receive partial structural or
process evidence, not whole-workflow completion. N01-N05, all generation/truth/
exports/replay/metrics/release requirements remain deferred. No unrelated source
requirement was removed or silently relabelled complete.

## AI usage / human review

Codex wrote implementation, fixtures/tests, dictionary tooling/docs, status overlay
and report, then executed commands. Heavy AI reliance is disclosed. No subagents
or other human implementation help. Complete Phase 02 prompt retained; previous
prompts/limitations unchanged. Agent cannot attest to other user chats/tools;
human must audit/add them before release. No fabricated human test/review claims.
The user's attachment explicitly authorizes Phase 01 progression; Phase 02
code/design/ownership review and independent human execution remain PENDING.

## Limitations and risks

- Cross-record business rules and all five anomaly workflows remain future work;
  enum/range/FK support is not completed recruiting behavior.
- Future mutation code must validate payloads, preserve effective master versions,
  atomically append events, and keep truth labels out of all input fields/JSON.
- SQLite owner can alter PRAGMAs/triggers; append-only controls aren't a tamperproof
  security boundary. Use the supported FK-enabled connection API.
- No automatic migrations; source changes require explicit safe evolution. SQLite
  3.38+ JSON support and pinned CPython needed; full installable package not added.
- Currency scale=100 and rubric scale/weights/lifecycle policy are documented
  synthetic design choices needing human review, not empirical hiring policies.
- Raw source/prompt/publication review still required; baseline privacy scanner
  cannot certify every possible secret/person record. Only synthetic test names
  and non-routable contacts used; no real candidate data introduced.
- Deadline send timestamp, round mismatch and exact email-vs-portal submission
  procedure remain earlier release risks, not technical schema blockers.

## Phase 02 acceptance

All eleven core tables, justified supports/bridges, explicit PKs/FKs/checks,
life/effective-time conventions, append-only history, full 207-field dictionary,
safe initialization and focused passing tests are present. Existing source/privacy
foundation checks pass. Complete prompt/journal/docs updated. No prohibited later
phase work implemented. Assessment PASS for requested Phase 02 deliverables;
human acceptance and Phase 03 authorization pending.

## Local Git state / finalization

Implementation commit: **2a180d5** - `feat: add recruiting schema and integrity tests`.
Actual commit command (after passing tests/staged checks):

```sh
git -c user.name=Codex -c user.email=codex@local.invalid -c commit.gpgsign=false commit -m 'feat: add recruiting schema and integrity tests'
```

Exit 0; fourteen implementation/docs/test files committed. Existing baseline
hashes 7e5a77b and baafb55 preserved. Immediately afterward only this final report
was untracked; no implementation changes remained. Branch codex/phase-01-foundation
retained, no remote/push/merge/submission. Report delivery uses a separate local
documentation commit. A downloadable copy receives post-commit Git metadata under
ignored output/reports/ so it can include final commit hashes and clean-state
verification without putting a commit's own hash inside its tracked contents.

## Recommended Phase 03 (not authorization)

After user review, define fixed config/logical epoch and deterministic ID counter
allocation; implement dependency-ordered valid starter generation against this
schema, then scale the same generator to exact full counts. Validate structural
integrity and document generation assumptions. Workflow guard/atomic history,
negative fixtures/truth/evaluation/full exports/replay require their own confirmed
scope. Keep prompts/tests/reviews and meaningful local commits. Do not proceed
until the user approves the next phase.
