# Reconciled requirements traceability matrix

> Current scope: P010 conditionally approves Phase06 and authorizes Phase07 only.
> The per-ID Phase07 acceptance overlay is docs/phase07/requirements-acceptance.md.
> Export/restore code tests passed; final full package/replay evidence is recorded
> at phase closure. Original75 source rows remain unchanged. No release authority.

> Current status: user P009 conditionally approves Phase05 and authorizes Phase06.
> The final Phase06 overlay is current; original75 source rows remain preserved.
> Phase07/export/publication/submission work remains unauthorized.

> Latest status: user P007 conditionally approves Phase04 progression and
> authorizes Phase05. The final Phase05 overlay is current. Original75 source
> rows and historical assessments remain preserved. No Phase06/public release.

> Current status: user P006 conditionally approves Phase03 progression and
> authorizes Phase04. The final Phase04 overlay is authoritative; the original
> 75 source rows and historical phase assessments remain below unchanged.
> Phase05 and public release are not authorized.

> Historical Phase03 status: user P005 approves Phase 02 progression; Phase 03 generation
> overlay at the end supersedes earlier phase snapshots. Original 75 requirement
> rows remain intact. Only master/approval/candidate/application generation is
> authorized now; no Phase 04 or public release.

> Current update: the user's Phase 02 prompt approves Phase 01 progression and
> authorizes schema/dictionary/integrity tests only. The original 75 rows and
> Phase 01 assessment below are preserved as the coverage baseline and historical
> status. The appended **Phase 02 implementation overlay** is authoritative for
> current implemented/tested/documented/deferred state. No baseline IDs changed.

User task instructions govern this phase: local analysis/foundation only; stop
for review; no Phase 02, push, merge, contact, or submission. Source documents
describe challenge requirements to plan, not permission to execute later work.

P = full problem-statement.md (candidate-supplied portal/email transcription,
accepted as specification at user's direction). F = FAQ PDF p1 Q1-Q12. G =
Submission Guidelines PDF p1 window/01-04. All three read completely; both PDFs
also visually inspected. Exact identities/reading coverage are in sources.json.
All source sections, F questions, and G sections are covered below. The original
45 instruction rows remain historically available in commit baafb55; the current
user-scope assessment is at the end. No missing-source assumption remains active.

M = mandatory, C = conditional mandatory, O = optional, R = permission/advice.
P0 = integrity/core/delivery gate; P1 = other required work; P2 = optional.
**All rows are analyzed; application implementation and acceptance tests are
planned, not completed.** Phase 01 docs/foundation are distinguished explicitly.
Targets below refer to future modules in architecture.md: schema, workflow,
generate, validate, export, evaluate, CLI, tests and reviewed artifacts.

## Functional scope

| ID | Source / requirement | Class/priority | Implementation plan and acceptance evidence |
| --- | --- | --- | --- |
| F01 | P Context/Workflow.3: track and approve requisitions, role criteria | M/P0 | schema/workflow/CLI; unapproved role blocked, criteria and bands linked |
| F02 | P Workflow.3: synthetic candidates and applications | M/P0 | generate; synthetic profiles, valid candidate/requisition joins |
| F03 | P Workflow.3/Acceptance: define/enforce stage transitions/gates | M/P0 | workflow/tests; missing required completed review rejects progression atomically |
| F04 | P Workflow.3: interviewer calendars | M/P0 | Availability, Staff and effective panel memberships; ordered valid intervals |
| F05 | P Workflow.3/Acceptance: schedule panels without conflicts | M/P0 | workflow; all participating interviewers available, overlapping bookings rejected |
| F06 | P Workflow.3/Acceptance: structured rubric scorecards | M/P0 | Scorecard/ScorecardItem; relevant criteria, valid rubric values, derived totals |
| F07 | P Workflow.3/Acceptance: offers within approved compensation bands, approvals/history auditable | M/P0 | workflow/Approval/events; band/currency/gate enforced, actor/reason retained |
| F08 | P Objective: working end-to-end workflow, multiple related entities, conditional rules, exceptions | M/P0 | CLI demonstration from approved role to final offer plus rejection paths |
| F09 | P Objective: key decisions/exceptions visible, traceability, measurable outputs/meaningful metrics | M/P1 | event/audit CLI, validation/evaluation reports; rule and related IDs, counts and metrics |
| F10 | P Actors: employee/candidate, manager, HR, IT/operations, administrator | M/P1 | model.md responsibilities and synthetic actor IDs; authentication is not specified |
| F11 | P Granular.4/Suggested: withdrawals, rescheduling, conflicting interviewers, incomplete scorecards | M/P0 | generator/fixtures; each variation counted with state and event evidence |
| F12 | P Workflow.4/Entities: explicit state records/events, no overwritten history | M/P0 | typed append-only events plus state projections in same transaction; audit/replay checks |

## Data, schema, exports and reproducibility

| ID | Source / requirement | Class/priority | Implementation plan and acceptance evidence |
| --- | --- | --- | --- |
| D01 | P Entities/Granular.1: all eleven core entities | M/P0 | model.md lists all eleven; future schema verifies names, keys and links |
| D02 | P Granular.1: every field's type, required/optional, allowed values, units, uniqueness, validation | M/P1 | future complete docs/data-dictionary.md compared to schema; conceptual model now is not final field dictionary |
| D03 | P Entities: PK every entity, FK every relationship, validate all joins | M/P0 | schema/validate; zero duplicate PK/null identity/orphans, including bridges/events |
| D04 | P Entities: cardinalities, optional links, effective dates, lifecycle states | M/P0 | model.md design now; schema/rule/date/cardinality checks later |
| D05 | P Entities: N:M bridge tables | M/P0 | PanelMember/InterviewParticipant/ScorecardItem and Application as relation; no embedded ID lists |
| D06 | P Workflow.1-2/Granular.2: master/parent records before children/events using valid parent IDs | M/P0 | dependency order in architecture.md; candidates and requisitions before applications |
| D07 | P IDs/Granular.3: REQ-2026-000001, CAND-000001, APP-<candidate-id>-<req-id>, INT-2026-000001, SCORE-<interview-id>-<reviewer-id>, OFF-2026-000001 | M/P0 | generate/tests; exact six patterns, zero-padding and literal composite IDs |
| D08 | P Granular.3: immutable IDs, zero-padded counters, exact references across files | M/P0 | stable allocation and sorted exports; ID equality and references in every format |
| D09 | P Granular.4/Suggested + user: 200 requisitions, 5,000 candidates, 8,000 applications, 2,000 interviews | M/P0 | full profile exact counts in baseline and injected snapshots and each export |
| D10 | P Granular.4: fixed seed (example 20261022) | M/P0 | chosen default 20261022; explicit config and manifest; example is not a prescribed seed |
| D11 | P Granular.4: parameterized scale, starter/full same generator | M/P1 | one generator code path; proposed starter 10/100/160/40 (design choice) |
| D12 | P Granular.5: valid baseline first, then labelled edge injection | M/P0 | clean baseline strict validation; deterministic mutations preserve unrelated rows and core counts |
| D13 | P Entities: deliberate anomalies have issue_type/ground_truth, no unrelated corruption | M/P0 | separate keyed truth/scenario manifest with affected IDs; preserve FK/type integrity |
| D14 | P Workflow.5/Granular.6: outcomes and totals/balances/scores/statuses/dates from rules/source records | M/P0 | deterministic derivation and independent recomputation; recruiting-inapplicable balance category documented |
| D15 | P Workflow.5: labels from documented rules, not independent random outcomes | M/P0 | truth rule catalog, expected decision and linked entities; RNG only creates synthetic inputs |
| D16 | P Granular.7/Review(f): separate ground_truth.csv/json; never input features | M/P0 | both truth CSV/JSON isolated; validator/workflow accept no truth; evaluator reads after findings |
| D17 | P Review(a): realistic distributions, meaningful variation | M/P1 | explicit synthetic distribution config/report, cross-entity coherence; no empirical realism claim |
| D18 | P Review(e): normal/boundary/failure/exception coverage | M/P1 | targeted tests and coverage counts; adjacent slots/band endpoints/incomplete reviews and five negatives |
| D19 | P Granular.9: CSV/JSON/SQL seed data | M/P0 | all three formats for all core, bridge and event tables; equivalent import/count/FK tests |
| D20 | P Granular.9: README, schema/dictionary, generator command, seed, source manifest, validation summary | M/P1 | complete reviewed export bundle; assignment-source manifest now, generated-data manifest later |
| D21 | P Granular.10/Review(g): regenerate twice same seed, compare counts/checksums | M/P0 | two separate full runs; canonical text export hashes and counts equal; no run claimed now |
| D22 | P Review(b-d): consistent joins/dependencies/lifecycles, derived reconciliation | M/P0 | independent validate checks; expected semantic anomalies distinguished after validation |

## All five mandatory negative scenarios

| ID | Source / scenario | Class/priority | Planned injection / expected result |
| --- | --- | --- | --- |
| N01 | P Granular.5/Negatives.1: candidate forward without required review | M/P0 | Advance existing application with missing required completed scorecard; stage_gate_missing_review flagged; ordinary workflow blocks |
| N02 | P Negatives.2: interviewer double-booked | M/P0 | Overlap two active interviews sharing staff member, even on different panels; interviewer_double_booked with both IDs; ordinary scheduler blocks |
| N03 | P Negatives.3: offer exceeds band | M/P0 | Above same-currency approved upper band; offer_exceeds_band; ordinary offer command blocks |
| N04 | P Negatives.4: withdrawn candidate remains scheduled | M/P0 | Withdrawal leaves existing active interview; withdrawn_still_scheduled; ordinary withdrawal cancels bookings |
| N05 | P Negatives.5: evaluation includes irrelevant criteria | M/P0 | Valid FK to another requisition's criterion; irrelevant_evaluation_criterion; ordinary scoring blocks |

Each must appear at least once (chosen acceptance floor, no specified frequency),
with separate truth. Isolate fixtures where possible; disclose any additional
legitimate findings. Normal guards stay strict. Incomplete scorecard is a valid
intermediate state; progressing without a required completed review is a failure.

## Validation, quality and provenance

| ID | Source / requirement | Class/priority | Implementation plan and acceptance evidence |
| --- | --- | --- | --- |
| V01 | P Granular.8: PK uniqueness | M/P0 | schema/validate; all core/support keys unique and non-null |
| V02 | P Granular.8: FK integrity | M/P0 | all joins resolve even in anomaly fixture |
| V03 | P Granular.8: allowed enums | M/P0 | configured state/category enum membership |
| V04 | P Granular.8: date ordering | M/P0 | ordered intervals, causal dates and effective memberships |
| V05 | P Granular.8: arithmetic reconciliation | M/P0 | recomputed weighted scores, applicable totals, integer monetary values |
| V06 | P Granular.8: lifecycle transitions | M/P0 | event sequence, allowed transitions and projection agreement |
| V07 | P Granular.8: duplicates | M/P0 | natural-key duplicate checks distinct from PK checks, unique candidate/requisition pair |
| V08 | P Acceptance: schedule/stage/rubric/offer audit | M/P0 | positive/negative operation checks with atomic failure and retained history |
| V09 | P Review/F Q9/G 01/04: demonstrate actual verification, environment/limitations | M/P1 | README/real reports; counts, findings, anomaly precision/recall, reproducibility; no fake benchmark |
| V10 | F Q8/user: suitable stack, free or local services; avoid huge/slow deps where possible | M/P0; size R/P1 | Python stdlib/SQLite local CLI; no hosted inference/cost/dependency downloads |
| V11 | P Lawful Use/F Q12/user: no secrets, credentials, confidential/personal/sensitive/unauthorized proprietary data | M/P0 | synthetic-only samples, ignored sources/local config, tracked-file scan and staged human review |
| V12 | P Review(g): lawful provenance | M/P1 | synthetic generation identified, source manifest includes provenance, no unsourced external corpus |

## Documentation, AI history and submission

| ID | Source / requirement | Class/priority | Plan / evidence / current state |
| --- | --- | --- | --- |
| S01 | G 01/F Q9/P Before Submit: executable code, install/config/run/verify instructions, environment/limits | M/P0 | README foundation now; application CLI and full run evidence later |
| S02 | G 02/F Q3/P Submission: new dedicated public GitHub repository | M/P0 delivery | dedicated local repo exists; public remote/push deferred by user |
| S03 | F Q4/Q6/G 03: ALL prompts to EVERY AI tool; responses optional | M/P0 | journal P001-P003 preserves human project prompts, tool inventory; ongoing requirement |
| S04 | F Q6: if no export, reasonable record and disclosed limits | C/P0 | journal limitation statement; human all-tools audit before release |
| S05 | G 03: AI acceleration/heavy reliance, human reviewed/changed/validated work | M/P0 | explicit AI vs human activity and pending human reviews; never attribute AI checks to human |
| S06 | G 04/F Q11: reasoning, problem, assumptions, decisions/trade-offs, tests, limits, incomplete work/deviations/next steps | M/P1 | architecture/model/risks/report now; ongoing updates |
| S07 | G 02: meaningful commits, understandable evolution/supporting context | M/P1 | retain baafb55 and scoped Phase 01 follow-up; no squash away original status |
| S08 | F Q7: individual, AI/public resources allowed, no other-person implementation help | M/P0 | no subagents/human implementation collaborators used; human ownership pending review |
| S09 | F Q5/Q7/G footer/P email: understand logic/design/deps/limits/every line; walkthrough readiness | M/P0 | human review and explain-back gate remains PENDING |
| S10 | F Q1/G window: 72 hours from send timestamp/timezone, artifact timestamps verify window | M/P0 delivery | preserve exact supplied Oct 29 2026 13:52:35 IST deadline; actual invitation timestamp unverified |
| S11 | F Q2: early allowed, repo public/editable through deadline, latest version evaluated | M/P0 delivery; early R | release checklist later, no current publication |
| S12 | F Q3: link from same recruitment email, follow instructions | M/P0 delivery | unresolved channel difference with portal; no message authorized now |
| S13 | P Submission: build locally, submit portal repo link before deadline once/final | M/P0 delivery | no submission now; user confirms exact process before one final submission |
| S14 | P email: one repository has code/all requested; public visibility tested in private browser | M/P0 delivery | all reviewed synthetic artifacts/docs/prompts eventually together; incognito check deferred |
| S15 | F Q4: identifiable code/prompt/support directories; format not prescribed | M/P1 | planned src/, docs/, reports/, artifacts/; Markdown valid |
| S16 | F Q10: standard deps/small snippets allowed; no complete/core imported solution; licenses/attribution | M/P0 | original implementation, license record if reused; no imported core solution |
| S17 | F Q12: safe samples, local config, README setup | M/P0 | synthetic samples only; ignored credentials; exact foundation setup now |

## Conditional and optional scope

| ID | Source / scope | Classification | Disposition / acceptance |
| --- | --- | --- | --- |
| C01 | P Lawful Use: external data optional | O/P2 | choose synthetic only; no scraping/download needed |
| C02 | P Lawful Use: external source URL/version/date/license/terms/attribution/transforms/discarded fields and redistribution rights | C/P0 | mandatory if external data introduced; not triggered now |
| C03 | P Lawful Use: no access-control bypass or confidential/personal collection; uncertain suitability -> synthetic/schema inspiration | M/P0 | no bypass or external corpus, source docs kept private |
| O01 | F Q9 hosted demo not mandatory | O/P2 | no hosting/UI/deployment required |
| O02 | F Q9 automated suite not generally mandatory | O/P2 generally | user's smoke and P's explicit validation/replay still mandatory; focused tests proposed |
| O03 | F Q5/Q8 any AI tool/stack permitted | R/P2 | no mandated LLM inside application; deterministic rules selected |
| O04 | No source mandates web/auth/microservices/dashboard | O/P2 improvement only | CLI proposed, no invented infrastructure requirement |

## User-scope and Phase 01 acceptance

All original constraints remain: exact deadline, individual/local work, complete
source reading, mandatory/optional traceability, architecture/stack/entities,
assumptions/risks/priorities/acceptance, minimal foundation, complete prompts and
honest human-review log, reproducible setup/actual smoke, no later phases,
fake results, paid/unneeded dependencies, secrets/real candidate data, push/merge/
submission; meaningful commits and downloadable cross-chat report every task.
Latest prompt P003 adds all counts/five negatives/history/truth/exports/replay,
source reconciliation and Phase 02 recommendations. All appear above or in the
linked design/report. Earlier missing-source conclusions are historical only.

| Phase 01 gate | Evidence / state |
| --- | --- |
| Verify/read/reconcile all sources and separate authority | DONE; sources.json and risks-and-decisions.md |
| Complete mandatory/optional traceability with source locators | DONE as analysis; all P sections/F Q1-Q12/G window/01-04 mapped |
| Eleven entities/relationships/lifecycles/dependencies | DONE as proposal; model.md; full field dictionary/schema later |
| Architecture/stack/workflows/assumptions/risks/acceptance | DONE as proposal; architecture.md and risks-and-decisions.md |
| Necessary foundation only | No generator/schema/domain validator/CLI implemented |
| Prompts/AI use/human review | journal.md updated; current-chat record; other-tool completeness needs human audit |
| Reproducible setup, actual smoke/privacy and local Git/report | Actual outcomes in reports/phase01-resumed-handoff.md |
| User approves before Phase 02 | PENDING, next gate; not an AI-claimed approval |

Analysis coverage is complete for supplied sources. Application implementation
coverage is intentionally zero. Domain acceptance tests/data generation have not
run. Remaining external uncertainties and assumptions are explicit; final
PASS/PARTIAL/FAIL follows actual checks in the current report.


## Phase 02 implementation overlay

I = implemented, T = tested with actual schema tests, Doc = documented.
Structural support does not satisfy a whole workflow/data-generation requirement.
All relevant source clauses were checked against the original statement/PDFs.
No technical Phase 02 blocker remains after verification; human Phase 02 review
and release-channel/send-time/round-label issues remain open. Actual run history,
including a caught/fixed test failure, is in reports/phase02-schema-handoff.md.

| Baseline requirement(s) | Implemented / tested / documented now | Deferred portion (not satisfied by schema alone) |
| --- | --- | --- |
| `F01` | I/T/Doc requisition/criteria/band/Approval storage | Approval/opening operations and criteria gates |
| `F02` | I/T/Doc Candidate/Application/skills structures | Synthetic profile/application generation |
| `F03` | I/T/Doc stage enum, timestamps, ApplicationEvent | Legal transition graph and required-review gates |
| `F04` | I/T/Doc calendar owner FK and positive intervals | Calendar generation/coverage logic |
| `F05` | I/T/Doc panel/member/participant/interview links | Conflict detection/prevention and scheduling algorithms |
| `F06` | I/T/Doc structured items, ranges, assigned reviewer FK | Weight/total calculation, criterion relevance/version/completion |
| `F07` | I/T/Doc valid band ranges, currency/snapshot FKs, approval XOR, one active final offer | Offer amount-vs-band, actor authorization and workflow eligibility |
| `F08`, `F09` | I/T/Doc traceable relational audit structure | End-to-end operations, decision UI/CLI, metrics |
| `F10` | I/T/Doc synthetic staff/system/candidate actor relationships | Actor-specific workflow behavior and human ownership review |
| `F11` | I/T/Doc lifecycle/history storage supports variants | Withdraw/reschedule operations and all generated variations |
| `F12` | I/T/Doc append-only events and immutable participant snapshots | Atomic projection/history business mutations and reconciliation |
| `D01` | I/T/Doc all eleven core tables plus justified support | No claim of complete business application |
| `D02` | I/T/Doc complete 207-field dictionary from actual SQL/metadata, freshness test | Future fields require explicit schema/dictionary updates |
| `D03` | I/T/Doc all 24 tables have PKs, 45 FK groups exercised | Full dataset/export join validation |
| `D04` | I/T/Doc cardinalities, nullable links, enum states, effective intervals | Legal lifecycles and cross-record temporal consistency |
| `D05` | I/T/Doc N:M bridges and composite keys | Generated relationships and workflow usage |
| `D06` | Doc parent order; initializer creates empty structure | Parent/child data generation |
| `D07`, `D08` | I/T/Doc exact ID CHECK patterns/composites and immutable keys | Deterministic counters/allocation and cross-file identity replay |
| `D18` | I/T/Doc focused structural normal/boundary/failure fixtures | Full scenario/exception workflow coverage |
| `D20` | I/T/Doc schema/dictionary/setup/init/test commands | Generator/export commands, generated source manifests, full summaries |
| `D22` | I/T/Doc structural key/range/join consistency | Derived values, lifecycle reconciliation and full-scale checks |
| `V01`, `V02` | I/T/Doc PK uniqueness and every FK group; invalid-reference tests | Validation engine over generated exports |
| `V03`, `V04` | I/T/Doc enums, strict epoch storage, same-row date/interval checks | Cross-record causal/temporal validation |
| `V05`, `V06` | I/T/Doc monetary/rubric scalar ranges and event state/sequence shape | Arithmetic reconciliation, legal transitions, sequence continuity |
| `V07` | I/T/Doc natural/composite uniqueness and duplicates | Export-level duplicate detection |
| `V08` | I/T/Doc structural audit/approval/rubric/calendar support | Scheduling/stage/offer business acceptance |
| `V09` | T/Doc actual schema commands/results and honest limits | Full core workflow verification, metrics/benchmarks |
| `V10`, `V11` | I/T/Doc stdlib-only local design, safe fixtures, source/privacy smoke | Exhaustive privacy review before any public release |
| `S01` | I/T/Doc executable initialization and reproducible tests/setup | Complete recruiting workflow run |
| `S03`, `S04`, `S05` | Doc complete Phase 02 prompt P004, AI reliance/tests/review status | Other-tool prompt audit and actual human line-by-line verification |
| `S06`, `S07`, `S15` | Doc design/trade-offs/limits, identifiable src/tests/docs; scoped local commit after tests | Final release narrative/artifacts and future commit history |
| `S08`, `S09` | Doc individual/AI assistance and explicit progression approval | Phase 02 human review and walkthrough readiness |
| `N01`-`N05` | Doc storage vs five semantic anomaly boundaries | All injection/detection/decisions deliberately DEFERRED |

All other baseline requirements remain at their prior planned/deferred state:
full-scale generation, ground truth, exports, two-run replay, metrics, external
provenance if introduced, optional UI/hosting, publication/submission. They were
not rewritten, dropped, blocked by the schema, or falsely marked complete.


## Phase 03 generation implementation overlay

Original 75 baseline rows and historical overlays preserved. I/T/Doc below is
Phase 03 evidence, not full challenge completion. Actual commands/results and
same-seed proof are in reports/phase03-data-generation-handoff.md; complete prompt
P005 and human-review state are in journal.md and docs/phase03/prompt.md.

| Baseline requirements | Current implemented/tested/documented portion | Still deferred |
| --- | --- | --- |
| `F01`, `F02` | Synthetic managers/criteria/candidates/applications; causal requisition approval policy/history | General interactive workflow/role operations |
| `F03` | Valid initial applied state, actual creation history and no advanced unsupported stages | Interview/review gates and later legal transitions |
| `F07`, `F12` | Requisition-only approvals and atomic event/projection generation | Offer logic/approval, other workflow mutations/history |
| `F09`, `F10` | Measured generation diagnostics, rule-derived fit and system/HR/manager/support actors | Finished workflow decisions/metrics/actor interactions |
| `D01`-`D05` | v2 retains 24 tables/joins, dictionary 209 fields; two justified input-field corrections tested | No claim every core table is populated |
| `D06`-`D08` | Dependency-ordered generation, actual immutable IDs/parent links/events and counters | Future INT/SCORE/OFF allocation, final cross-format exports |
| `D09` | Exact full 200 requisitions /5,000 candidates /8,000 applications; tests and actual runs | 2,000 interviews, complete challenge dataset |
| `D10`, `D11` | Fixed seed 20261022, starter/full same implementation, explicit configuration/logical epoch | Future profile-dependent downstream generation |
| `D12` | Phase 03 valid baseline and measured integrity checks | Finished baseline with downstream tables; all labelled injections |
| `D14`, `D15` | Integer criterion weights, actual-data-derived fit, causal rule-based approvals/history | Scorecard/outcome calculations and anomaly labels |
| `D16` | No ground truth created or leaked into current input fields/JSON | Separate truth CSV/JSON and evaluator |
| `D17`, `D18` | Declared role/experience/proficiency/currency/match variation, actual summaries and focused boundary/failure tests | Finished workflow normal/boundary/exception coverage |
| `D20` | Generator commands/config/seed/source schema fingerprint, measured summaries/replay evidence | Complete CSV/JSON/SQL data/manifest/export bundle |
| `D21` | Two independent starter AND full Phase 03 runs: equal counts, EVERY ordered record and canonical SHA256 | Reproducibility of all later challenge entities/exports |
| `D22`, `V01`-`V07` | Measured keys/FKs/nullability/IDs/enums/causal dates/ranges/weights/initial histories | Full workflow/derived-score/state reconciliation and export validator |
| `V09`-`V12` | Real tests, durations/checksums, stdlib/local synthetic provenance and prior privacy checks | End-to-end benchmarks and final human privacy review |
| `S01`, `S03`-`S08`, `S15`, `S17` | Runnable generator/CLI, full P005 preserved, AI disclosure, local commits and honest handoff | Human Phase 03 acceptance/ownership and final delivery |
| `F04`-`F06`, `F08`, `F11`, `N01`-`N05`, `D19`, `V08` | No new implementation claimed in this phase | Scheduling/calendars/reviews/offers/withdrawals/rescheduling, anomalies/truth/evaluation, complete exporters |

Source-required public repository/submission/deadline/other administrative gates
remain unchanged and deferred. No pushes, merges, hosting, recruiter contact or
submission. Human Phase 03 review is pending; Phase 04 is not authorized.


## Phase 04 workflow implementation overlay (current)

User P006 conditionally approves Phase03 progression and explicitly authorizes
this phase. The prior 75 source rows and all historical overlays above are
unchanged snapshots. I/T/Doc means implemented with actual verification and
documented at the Phase04 boundary; no whole-project completion is claimed.

| Baseline requirements | Current implemented/tested/documented portion | Remaining portion |
| --- | --- | --- |
| F01, F02 | Existing exact master counts, IDs, approvals and original creation history preserved; requisition eligibility gates used for scheduling | General approval revision UI/CLI remains outside this phase |
| F03 | Explicit legal transition matrix, atomic screening/scheduling/withdrawal; review guard rejects missing/incomplete evaluations, no reviewed/offer/hired bypass | Actual review completion/offer/hire workflow Phase05 |
| F04, F05 | Synthetic Staff/panels, effective membership, immutable participants, UTC fixed availability, blocked calendar override, half-open conflict checking and transactional scheduling | No external calendars/authentication needed or claimed |
| F06, F07 | Existing score/offer schema retained; scoring/offer tables remain empty | Scorecard collection/derived totals, offer bands/approval/history remain Phase05 |
| F08, F09, F10 | Reusable schedule/reschedule/cancel/complete/withdraw operations; actor assumptions, real audit/history/diagnostics and conflict-probe metrics | End-to-end final-offer demonstration, finished metrics and human ownership |
| F11, F12 | Actual withdrawals/cancellations/reschedules/completions; failed attempts rejected without successful events; original slots/participants retained; projection/history and rollback tests | Legitimate incomplete scorecard generation deferred; no labelled anomaly production |
| D01–D05 | All 24 v2 tables, 209 fields, 45 FK groups and 42 protection triggers unchanged; panels/calendars/interviews/bridges now populated consistently | Scorecard/offer core entities remain empty; no claim all 11 entities have generated data |
| D06–D08 | Dependency-ordered operations and stable INT-2026-000001 onward; original master fingerprint and exact Phase03 canonical digest preserved | SCORE/OFF allocation and equivalent cross-format export references later |
| D09 | All four FULL target counts now exactly 200/5000/8000/2000; starter 10/100/160/40 verified | Counts in anomaly variants and all final exports remain unverified/deferred |
| D10, D11 | Same seed/profile implementation, configurable starter interview count, FULL fixed 2000; deterministic UTC time/panels/calendars/selection | Complete downstream generation/replay later |
| D12, D14, D15, D17 | Valid baseline, source-derived skill pool and documented deterministic cohorts; measured real variation, finite capacity failure | Rule-derived scoring/offers and labelled negative scenarios later |
| D13, D16, N01–N05 | No truth fields/leakage; ordinary missing-review, overlap and withdrawal guards enforced; isolated corruption tests only | All five injection/labels/detection, separate truth CSV/JSON and evaluator remain DEFERRED |
| D18, V08 | Actual normal/boundary/failure/race/atomicity tests for scheduling and stage gates | Rubric/offer acceptance and complete scenario coverage remain later |
| D19, D20 | Current schema/dictionary/README, generation+validation commands, measured JSON summary/canonical evidence | Full CSV/JSON/SQL exports, round-trip imports and delivery manifest remain DEFERRED |
| D21 | Two independent starter and full workflow generations compare every ordered row/count/table hash/aggregate hash; original master mode retained | Finished score/offer/anomaly/export reproducibility later |
| D22, V01–V04, V06, V07 | Phase-aware counts/keys/FKs/natural duplicates/time/IDs/states, membership/availability/overlaps, withdrawal and event/participant/projection reconciliation | Export equivalence and future lifecycle/derived score reconciliation later |
| V05 | Prior input weight/band checks preserved; no invented score/offer arithmetic | Full structured score and offer calculation validation later |
| V09–V12, S01, S06 | Actual 99-test suite, measured generation/scheduling/validation, local stdlib/privacy/source checks, reproducible instructions and candid limitations | End-to-end benchmark/anomaly metrics and final privacy review later |
| S03–S05, S08, S09 | Complete P006 preserved byte-for-byte; actual AI work and conditional progression authorization recorded | Human Phase04 review/line understanding and all-tools prompt audit pending |
| S07, S15, S17 | Focused local commits, identifiable source/test/docs/report files; no generated DB/private source staged | Final artifact/release narrative later |
| C01–C03 | Synthetic-only data, no external corpus or access-control bypass; source documents kept private | External provenance obligations apply if later data sources are introduced |
| S02, S10–S14, S16, O01–O04 | Prior administrative, deadline, lawful-use and optional-feature treatment unchanged | No push/merge/publication/submission/contact; release-channel uncertainty retained |

Actual test/replay commands and checksums: reports/phase04-interview-workflow-handoff.md
and docs/phase04/reproducibility-evidence.json. Stop for Phase04 review before
Phase05. Source-required five negatives remain explicitly tracked, not silently
excluded by implementing a valid baseline first.


## Phase 05 evaluation/offer implementation overlay (current)

User P007 explicitly authorizes Phase05 only after conditional Phase04 approval.
Original75 source rows remain unchanged. I/T/Doc below is actual current scope,
not a claim the complete challenge/delivery is finished. No requirement removed.

| Requirements | Implemented/tested/documented now | Remaining |
| --- | --- | --- |
| F01–F05 | Prior master/approval/scheduling/calendar/panel rules, exact counts and immutable source histories preserved | General configuration-change workflows; no external calendar needed |
| F06 | Actual assigned-reviewer Scorecard/ScorecardItem create/edit/submit; effective versions, relevant criteria, 0–4 rubric, source-weighted integer total, submitted locks and audit | Formal submitted-card correction/version policy outside current supported operations |
| F03, F07, F08 | Real interviewing→reviewed guard, separate offer eligibility; approved snapshot bands/currency, independent offer approval/rejection and accepted/hired path; atomic sibling cleanup | Complete exported/anomaly scenario demonstration and final challenge acceptance later |
| F09–F12 | Persisted policy/decision references, actual draft/incomplete/submitted variants, rejected operations, full score/offer/approval snapshots, final reconciliation and real metrics | Human ownership review; future anomaly/evaluation metrics |
| D01–D08 | All11 core entities populated in evaluation mode; schema v2/24 tables/209 fields/constraints unchanged; Staff-based SCORE composite, stable OFF counters, distinct offer/requisition approvals | Final cross-format identity/export verification |
| D09–D11 | FULL remains200/5000/8000/2000; starter10/100/160/40; all modes preserved with archived master/interview digests; deterministic Phase05 composition | Complete later artifact/profile equivalence |
| D12–D15, D17, D18 | Valid scoring/offer baseline, source-derived items/totals/thresholds/amounts/budget decisions; documented synthetic cohorts, boundary/failure/rollback/terminal tests | Deliberate labelled mutations and full negative scenario coverage remain later |
| D16, N01–N05 | No truth leakage; ordinary missing-review/overlap/over-band/withdrawn-schedule/irrelevant-criterion guards now exist | Allfive injected datasets/labels, separate truth CSV/JSON and anomaly evaluator remain DEFERRED |
| D19, D20 | README/design/schema/dictionary/prompt/source manifest and actual generation/validation/replay evidence | Full CSV/JSON/SQL exporters, import round-trips and delivery manifest remain DEFERRED |
| D21, D22, V01–V09 | Independent every-row starter/full replay; actual source score arithmetic, legal histories, actors/approvals/bands/times/IDs/joins/terminal cleanup and prior scheduling invariants verified | Finished anomaly/export reconciliation and final evaluation metrics later |
| V10–V12, S01, S06 | Local stdlib, safe synthetic provenance, explicit assumptions/limits; actual tests/smoke/privacy/runtime evidence | Final human privacy/release review and walkthrough |
| S03–S05, S08, S09 | Full22-section P007 preserved verbatim; actual AI-generated code/AI-run tests vs conditional human progression approval recorded | Human Phase05 review/personal verification/line understanding and all-tools audit pending |
| S07, S15–S17 | Focused local commits, identifiable code/prompt/evidence/report files, no imported core solution/new deps/private artifacts staged | Final release narrative and artifact preparation |
| S02, S10–S14, C01–C03, O01–O04 | Existing deadline/channel/lawful-use/conditional/optional requirements remain tracked unchanged | No push/merge/remotes/publication/submission/contact; external uncertainties remain |

Actual measured tests/counts/checksums/performance and known limits are recorded
in reports/phase05-evaluation-offer-handoff.md and
docs/phase05/reproducibility-evidence.json. STOP after Phase05 for human review.
Anomaly injection, ground-truth output, anomaly metrics and full exporters are
not complete and not authorized in this phase.


## Phase 06 controlled-anomaly implementation overlay (current)

User P009 authorizes Phase06 only. Original75 rows and historical snapshots are
unchanged. Actual commands/counts/findings/metrics/replay in current handoff.

| Requirements | Implemented/tested/documented now | Still incomplete |
| --- | --- | --- |
| N01–N05 | Allfive genuine detector-visible observations, existing references, independently derived per-issue truth, targeted boundary/near-miss controls and independent detector findings | Final exported/public delivery of these artifacts later |
| F03–F07, F11, F12 | Normal review/calendar/rubric/band/withdraw guards preserved; append-only history untouched; semantic observations kept outside ordinary APIs | No new generic lifecycle/configuration UI required |
| F01, F02, F08–F10 | Complete existing clean workflow preserved; measurable decisions/exceptions plus explicit semantic findings with linked IDs/evidence/rules | Final packaged end-to-end challenge review and human ownership |
| D01–D11 | v2/24 tables/209 fields and all IDs/counts/master data unchanged; full200/5000/8000/2000 preserved in observed view | Complete equivalent cross-format exports/imports |
| D12, D13 | Verified valid baseline first, separately controlled generation-only observations; exact before/after and structural protections; no unrelated/history corruption | Final bundle inclusion under separately approved Phase07 |
| D14–D18 | Labels derive from actual controlled rule violations; truth CSV/JSON isolated/agreed, input schema denies label metadata; normal/boundary/invalid/near-miss tests | No claim of broad real-world accuracy/generalization |
| D19, D20 | Required truth CSV/JSON and detection/evaluation reports, documented commands/config/checksums/source/evidence | Generalized CSV/JSON/SQL seed exporters, re-import, final release manifest DEFERRED |
| D21, D22 | Two independent anomaly bundles/profile, canonical rows/counts/hash/file/metric equality, preserved Phase05 hashes and independent matching | Final cross-format full challenge reproducibility later |
| V01–V08 | Actual PK/FK/enums/scalars/parent counts/uneditable table-history hashes; business findings separated from structural errors; five rule checks independent | Full generalized export validators later |
| V09–V12 | Actual tests/timing/TP/FP/FN/precision/recall/F1, per-rule/type/coverage/clean FP; local stdlib/synthetic data/privacy and lawful provenance | Final human release/privacy checks and all-tools audit |
| S01, S03–S09, S15–S17 | Executable commands/design, full P009 preserved, AI vs human disclosure and meaningful local code/report commits | Human Phase06 personal verification/understanding; final release narrative |
| S02, S10–S14, C01–C03, O01–O04 | Prior deadlines/admin/conditional/optional/lawful-use tracking unchanged | No push/merge/remotes/public setup/contact/submission; channel/window ambiguities retained |

Observation controls are rule-specific; canonical Phase05 retains all99 clean
checks. Expected findings remain visible, not relabelled as a fully valid observed
business state. Stop for Phase06 review. No generalized exporter/re-import/final
publication manifest/dashboard/public GitHub/portal submission implemented.


## Phase 07 completed export/delivery-data overlay (current)

P010 conditionally approves Phase06 and authorizes Phase07 only. Every original
source row above remains unchanged. Per-ID implementation, test, artifact and
limit evidence for all75 IDs is in docs/phase07/requirements-acceptance.md.

| Requirements | Actual current evidence | Remaining |
| --- | --- | --- |
| F01–F12, D01–D18, D22 | Existing eleven-entity end-to-end behavior preserved; all24 tables/89575 records/IDs/joins/events exact after CSV/JSON/SQL restores; all99 domain checks per restore | Human ownership/policy review; observation representation limits disclosed |
| D19, D20 | Complete24-table CSV+JSON, full FK-safe SQL schema+seed; dictionary/catalog/manifest/provenance/validation and genuine linked Phase06 artifacts tracked in artifacts/ | Five large text files losslessly gzip-compressed; compatible pinned runtime required |
| D21 | Two independent FULL seed20261022 builds each generate/export/restore/evaluate; all68 artifact bytes,89575 typed rows, table/aggregate hashes and manifests identical | Reproducibility scoped to verified runtime; elapsed diagnostics excluded |
| N01–N05 | Allfive separately packaged;30TP,0FP,0FN, precision/recall/F1=1.0; clean0 findings;41 controlled observations retain structural integrity and expose semantic violations | Controlled examples do not prove real-world generalization; truth stays out of detector |
| V01–V10,V12,S01,S06,S07,S15–S17,C03 | Actual independent import/validation,208 tests (183 prior+25 new), dictionary/source smoke, measured sizes/timings, local stdlib, synthetic provenance and scoped commits | Reviewer interpreter must be available; source PDFs only needed by maintainer source-smoke |
| V11 | New artifact privacy/identity checks pass; seven inherited private-path report references safely flagged in repository-privacy-review.json | Human final publication/content review PENDING; whole repository not declared public-safe |
| S03–S05,S08,S09 | Complete known P001–P010 preserved, human conditional progress approvals separated from AI code/test work; no other implementers/subagents | Human personal testing/line understanding/all-tools prompt audit PENDING |
| S02,S10–S14 | Dedicated local repository and deadline preserved; public/release/channel/window requirements retained | No remote/push/publication/submission/contact authorized; final human process later |
| C01,C02,O01–O04 | Synthetic-only; external data condition untriggered; optional hosted UI/auth/application LLM absent; actual automated tests provided | No optional infrastructure substituted for required exports |

57 IDs IMPLEMENTED_VERIFIED,6 IMPLEMENTED_HUMAN_REVIEW_PENDING,6 USER_RELEASE_GATE,
1 CONDITIONAL_NOT_TRIGGERED,5 OPTIONAL_OR_PERMISSION. Technical Phase07 PASS;
final public submission/human acceptance remain incomplete by explicit scope.
Actual commands/checksums/timings in docs/phase07/reproducibility-evidence.json,
reviewer-verification.json and reports/phase07-export-deliverables-handoff.md.
STOP before Phase08.


## Phase08 final independent audit overlay (current)

All75 original source rows and prior overlays preserved. New authoritative per-ID
source/function/artifact/command/result/gap/severity/classification audit:
docs/phase08/final-requirements-audit.md (plus machine-readable JSON).
58PASS,11PARTIAL,1FAIL,5NOT_APPLICABLE. V11 privacy/publication FAIL because current
paths and historical paths/personal Git metadata remain; S03–S05/S08/S09 human
history/ownership and S02/S10–S14 release/admin actions PARTIAL. Optional/conditional
C01/C02/O01/O03/O04 NOT_APPLICABLE; optional O02 suite actually provided and PASS.
All runtime business/data/export requirements passed new actual checks, not just
prior reports. Proven archive-build dependency corrected; all211 tests pass both
workspace and clean copy; full two-run bytes/records match; canonical unchanged.
User P012 explicitly confirms both ChatGPT and Codex, missing original ChatGPT
prompt inclusion and unconfirmed personal technical testing/line understanding.
Do not interpret earlier sole-tool statements or progression approval as final
human acceptance. Overall release NO-GO. No public/history/submission actions
authorized or performed. Stop after Phase08 for review.
