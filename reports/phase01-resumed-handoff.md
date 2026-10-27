> Publication-copy notice: private home-path identifiers are replaced by `<private-home>/`. Technical results remain historical evidence. Every redaction is logged in docs/publication-preparation/redaction-log.json; the original private report/history is unchanged.

# YottaFlex - resumed Phase 01 handoff report

**Phase 01 assessment: PASS - analysis and local foundation ready for human review.**
Human approval is PENDING. This does not mean the application is complete, does
not resolve external release ambiguities, and does not authorize Phase 02.
All supplied source sections mapped in 75 unique requirement/scope rows; domain
implementation/test coverage is intentionally zero at this phase.

## Continuation context

Individual Associate AI Forward Deployed Engineer 72-hour challenge. Project:
<private-home>/Documents/Personal/Projects/Assignment/YottaFlex.
Deadline: October 29, 2026, 1:52:35 PM IST (2026-10-29T13:52:35+05:30).
Current branch: codex/phase-01-foundation; prior commit baafb55. Work locally.
No push, merge, submission, Phase 02, paid services or real candidate information.
Public repository intended only after whole project completion and user review.
After each task provide a downloadable cross-chat handoff report. AGENTS.md
persists these constraints. Initial missing-source report remains historical.

## Source verification and authority

The three files were inside the supplied Downloads ZIP, not yet extracted in the
project. Only exact expected members were extracted, with conflict checks and
no arbitrary archive extraction. All now exist, are readable and fully read.
Problem statement is the candidate-supplied portal/email transcription accepted
as specification per user; PDFs are official supplied additional requirements.
Both PDFs are one page, all text read and both page images visually inspected.
Source requirements are evidence, not authority to publish, contact or submit.
No authenticated portal access or external source retrieval occurred.

| Source | Bytes | Pages | SHA256 |
| --- | --- | --- | --- |
| P: problem-statement.md | 7735 | Markdown, full text | 8faefed019161bb66ce6ea274accd7fdf6500622ea2fb71fc6f3d756de133ace |
| F: YottaFlex AI Candidate Project-FAQ.pdf | 14827 | 1 | b3486be5674d00a911e2998f1d89d79904629f8a1fac99bc58b62e37d2a21c7a |
| G: YottaFlex AI Candidate Project Submission Guidelines.pdf | 14753 | 1 | e26107381e39c901af6a92a0a89a7178604851291eaaf2f3016e146da6532e73 |

Complete reading coverage and archive checksum: docs/phase01/sources.json.

## Changes and preservation

Modified: AGENTS.md; README.md; docs/assignment/README.md;
docs/phase01/requirements.md; docs/phase01/architecture.md;
docs/phase01/journal.md; scripts/smoke.sh.

Created: .python-version; pyproject.toml; docs/phase01/sources.json;
docs/phase01/model.md; docs/phase01/risks-and-decisions.md;
scripts/check_foundation.py; reports/phase01-resumed-handoff.md.

Local ignored additions: three raw assignment files; PDF text/images in tmp/pdfs;
virtual environment if created during verification. No raw source tracked.
Preserved unchanged: .gitignore, .gitattributes, historical initial handoff and
prior Git history. Existing root/privacy/IO smoke checks retained and extended.
No src package, domain schema/generator/workflow/validator or dataset generated.

## Architecture and trade-offs

Choose CPython 3.14.5, stdlib only, local SQLite and CLI. Observed SQLite 3.53.1.
No pip package, build backend, ORM, frontend, paid service, hosted LLM or container.
Local SQL transactions/FKs support the moderate relational volumes; temporal and
stage rules need explicit transactional Python guards. CLI gives reproducible
execution; a web interface/hosted demo is not mandated. Synthetic-only original
inputs avoid licensing/privacy uncertainty but require honest distribution limits.

Planned package modules: db/schema, workflow, generate, validate, export, evaluate,
CLI. Ordinary functions/direct SQL, no generic architectural framework. Generation
uses normal rules for clean baseline, explicit separate injection for negatives.
Validator receives no ground truth; evaluator joins labels only after findings.
All mutation commands atomically update projection and append history. Member
snapshots prevent later panel changes from rewriting historical bookings.

Eleven core entities: Requisition, HiringManager, Candidate, Application,
SkillRequirement, InterviewPanel, Availability, Interview, Scorecard, Offer,
Approval. Conceptual PK/FK/cardinality/lifecycle/effective-date model is complete
in model.md; field-level dictionary and SQL schema are Phase 02, not claimed done.

Main joins: manager 1:N requisition; candidate N:M requisition via Application;
requisition 1:N criteria/panels; panel N:M Staff via effective PanelMember; Staff
1:N Availability; application/panel 1:N Interview; Interview N:M Staff via snapshot;
Interview 1:N Scorecard with unique reviewer pair; Scorecard N:M criteria via items;
Application 1:N Offer with at most one active final; Approval targets exactly one
requisition or offer. Typed append-only events preserve FK-enforced history.
Supporting Staff resolves interviewer/reviewer/approver identities, not a twelfth
claimed core entity. No authentication subsystem inferred from actor roles.

Full profile: exactly 200 requisitions, 5,000 candidates, 8,000 applications,
2,000 interviews. Same generator starter proposed 10/100/160/40. Fixed default
seed 20261022, logical epoch, stable counters/order, immutable required ID patterns.
All core/bridge/event tables exported CSV/JSON/SQL, ground truth CSV+JSON separate,
source/config/validation summaries present. Two independent full runs compare
canonical counts/checksums, not SQLite binary files. None of these domain runs
has happened in Phase 01.

Mandatory negative cases: forward without required review; interviewer double-
booked; offer over band; withdrawal still scheduled; irrelevant evaluation
criteria. Valid baseline first, isolated semantic injections retain structural
integrity/counts and separate issue labels. Normal workflow rejects each invalid
operation. Incomplete scorecards/rescheduling/withdrawals also explicitly covered.

## Conflicts, assumptions and remaining risks

- Exact supplied deadline is retained; original send timestamp not independently
  verified. ZIP arrival never restarts challenge clock.
- Portal says Round 2, email Round 3: unresolved label, no scope guess.
- FAQ recruitment-email link vs portal once/final submission: human must confirm
  release channel. No email/portal action authorized or performed.
- Editable repo until deadline vs final submission: possible link/content
  distinction is an inference only; do not rely on it unverified.
- Scheduling prevention vs deliberately invalid data reconciled via strict normal
  operations and separate injection; issue labels isolated outside features.
- CSV/JSON/SQL interpreted inclusively; all three planned. Full counts mandatory
  despite Suggested heading; no reduction to starter-only deliverable.
- Stages, rubric scale, review thresholds, band distributions and starter size are
  declared synthetic design choices; source supplies no fixed numerical SLA.
- Ground-truth leakage, runtime/order/clock drift, event reconciliation and exact
  full exports are highest implementation risks. Relevant tests remain future.
- Raw sources stay ignored; final synthetic exports must be reviewed and included
  under artifacts/ rather than silently omitted because scratch output is ignored.
- Prompt completeness across other chats/tools and human understanding still need
  human audit. No AI-run command is claimed as personal human verification.

## AI prompt history / human review

journal.md preserves all available human task prompts P001-P003, including original
instruction, path clarification and latest resumed request; AI clarification Q001
also retained. Only wrapping/trailing whitespace normalized. Codex is the only
AI tool used here, no subagents or other-person implementation. AI generated the
analysis, design, foundation checks and report and executed checks. Heavy reliance
is disclosed. Responses optional per FAQ; account-wide raw export unavailable,
so user must add any other tools/chats and disclose limitations before release.
System/developer instructions/private reasoning are not project user prompts.
Human design/code/ownership review is PENDING, not fabricated as approved.

## Actual command/tool ledger

1. git status --short --branch; git log -2 --oneline; git remote -v; rg --files:
   exit 0, clean dedicated branch at baafb55, no remote; inspected current files.
2. cat AGENTS.md, requirements, architecture, smoke, .gitignore: exit 0, reviewed
   existing foundation. ls docs/assignment showed only README; unzip -l showed
   exactly three source files plus directory entries in supplied archive.
3. Read PDF SKILL.md and loaded bundled runtime paths (read-only tool calls).
4. Python stdlib ZipFile exact-member extraction/hash + full Markdown print:
   exit 0; all three readable, exact sizes/hashes above; entire statement read.
5. Bundled Python import discovery: pypdf/pdfplumber/pypdfium2 available; fitz absent;
   bundled Poppler binaries found. No dependencies installed.
6. Bundled Python pypdf full layout extraction: exit 0; one unencrypted page each;
   complete FAQ Q1-Q12 and Guidelines window/01-04/footer read; texts saved ignored.
7. Bundled pdftoppm -scale-to 1500 -png on PDFs: repeated font/config/cache errors;
   process interrupted via write_stdin Ctrl-C, exit 130. Not a successful render.
   Second chained render did not run. Bundled pypdfium2 render then exited 0 for
   both page images; view_image inspected both full pages successfully.
8. python3 --version and sqlite3 feature probe: exit 0, CPython 3.14.5 / SQLite
   3.53.1; FK enablement confirmed. Read README/journal/source README in full.
9. Initial combined delete/add apply_patch for same paths rejected atomically;
   corrected sequential patches succeeded. Other file patches/manifest generation
   succeeded. No business functionality implemented by those patches.

10. python3 -m venv .venv: exit 0, local CPython 3.14.5 environment created with
    no third-party package installation or network download.
11. PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh: exit 0; all four shell checks
    and three Python groups passed. Source hash/readability, SQLite FK/rollback,
    runtime pin and 17 publication candidates verified.
12. sh -n scripts/smoke.sh plus .venv/bin/python3 inline ast/json/tomllib checks:
    exit 0; shell/Python syntax, exact runtime/TOML agreement, zero dependency list,
    three full-read source entries and PDF page counts [1,1] confirmed.
13. git diff --check; git status --short --branch; git diff --stat;
    git ls-files docs/assignment: exit 0, no whitespace errors in tracked diff;
    only assignment README tracked, all raw sources excluded. New files receive
    substantive staged whitespace review before commit.
14. From /private/tmp:
    PYTHON_BIN=<private-home>/Documents/Personal/Projects/Assignment/YottaFlex/.venv/bin/python3 sh <private-home>/Documents/Personal/Projects/Assignment/YottaFlex/scripts/smoke.sh
    exit 0, same four shell checks and three Python groups passed.
15. Python inline matrix-ID audit: exit 0, 75 unique IDs, complete groups F=12,
    D=22, N=5, V=12, S=17, C=3, O=4. This is document-structure verification,
    not proof that any domain requirement is implemented.
16. cat source manifest; git diff -- scripts/smoke.sh AGENTS.md;
    cat scripts/check_foundation.py: exit 0, source metadata and executable
    foundation changes reviewed.

Actual smoke output (both runs):

```text
PASS: isolated project Git root
PASS: required foundation documents exist
PASS: private inputs, common credentials, and generated paths are ignored
PASS: synthetic local write/read round-trip
PASS: pinned Python 3.14.5; SQLite 3.53.1 FK and rollback
PASS: all three sources readable and match recorded SHA256/size/signatures
PASS: 17 tracked/untracked publication candidates exclude private paths/keys
Foundation Python checks passed: 3 groups. No application validation executed.
Foundation smoke passed: 4 shell checks + 3 Python groups. Application checks remain pending.
```

Limits: privacy checks enforce filenames/path exclusions/private-key markers;
they are not an exhaustive secret or personal-data detector. Content review
remains required. No domain tests, data generation, full-volume validation,
model evaluation, full exports or two-run reproducibility executed.

17. git add [the fourteen explicitly listed Phase 01 files]; git diff --cached
    --check; git diff --cached --stat; git diff --cached --name-only: authorized
    local index write, exit 0; fourteen intended files only, no whitespace errors.
18. git diff --cached -- README.md docs/assignment/README.md .python-version
    pyproject.toml docs/phase01/sources.json docs/phase01/model.md
    docs/phase01/risks-and-decisions.md; git diff --cached --numstat;
    .venv/bin/python3 scripts/check_foundation.py: exit 0, reviewed design/setup
    changes and reran privacy/runtime/source checks after final report edits;
    all three Python groups passed for 17 publication candidates.

19. git add reports/phase01-resumed-handoff.md; git diff --cached --check;
    git -c user.name=Codex -c user.email=codex@local.invalid -c commit.gpgsign=false
    commit -m 'chore: complete phase 01 requirements and local foundation';
    git status --short --branch; git log -2 --oneline; git remote -v:
    authorized local operation, exit 0. Scoped commit succeeded, fourteen files,
    clean working tree confirmed, baafb55 preserved, no remote.

Commit message used:
`chore: complete phase 01 requirements and local foundation`.
The observed commit result is consolidated into this same local commit. Its own
hash is not embedded in this tracked report; resolve final identity with git log
-1 --oneline. Final reply confirms consolidation and final status. No push, merge,
submission or Phase 02 implementation occurred.

## Phase 01 acceptance decision

PASS for requested source analysis, architecture/model, documented risks and
necessary local foundation; real smoke/privacy checks passed. Human acceptance
and understanding review are PENDING. Submission channel/send-time/round-label
questions remain release risks, not missing technical requirements. Full field
dictionary, domain implementation, full datasets/exports/validation/evaluation
and two-run replay are intentionally future work. No overall project-complete
or domain-test-pass claim is made.

## Recommended Phase 02 after human review

1. Confirm/accept versioned synthetic policy assumptions and architecture.
2. Complete actual per-field dictionary, explicit SQLite schema/bridges/events.
3. Implement deterministic config/IDs and clean starter generation in parent order.
4. Implement transactional workflow guards/history; same generator to full counts.
5. Inject five labelled cases separately; independent validation then evaluation.
6. Full CSV/JSON/SQL exports, isolated truth, manifests and two full-run replay.
7. Record actual evidence/prompts/reviews and meaningful local commits; no release
   until final separate user authorization and channel/privacy/access review.

## Full source requirements matrix

The following is a snapshot of the complete current matrix. All domain targets
are planned, not implemented. It is included so this report can be pasted into
another chat without losing requirement scope.

# Reconciled requirements traceability matrix

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
