> Publication-copy notice: private home-path identifiers are replaced by `<private-home>/`. Technical results remain historical evidence. Every redaction is logged in docs/publication-preparation/redaction-log.json; the original private report/history is unchanged.

# YottaFlex Phase 05 — structured evaluation, offers and approvals handoff

**PASS for Phase 05 only. STOP before Phase 06. Human review pending.**
Prepared locally on 2026-10-27. Project root: `<private-home>/Documents/Personal/Projects/Assignment/YottaFlex`.
Branch: `codex/phase-01-foundation`. Deadline: **October 29, 2026, 13:52:35 IST**
(`2026-10-29T13:52:35+05:30`). No push, merge, remote configuration, publication,
recruiter contact or submission. This downloadable Markdown report is intended
for pasting into a future ChatGPT chat; preserve this status and phase boundary.

## 1. Assessment and continuation context

User said `here is next` and supplied the complete 22-section Phase 05 prompt.
It states Phase 04 was reviewed/conditionally approved and authorizes Phase 05
only. Source documents describe the challenge/submission requirements, not
permission to publish or start future phases. User approval of the proposed
synthetic thresholds or personal test execution is not assumed.

Actual structured evaluation and offer workflow now runs end-to-end through
hired/rejected states with source-derived scores/amounts, independent approval,
atomic history and sibling cleanup. Existing full 200/5000/8000/2000 counts remain.
All 148 tests passed in 80.699s, including all 99 prior tests. Both final profiles
passed all 99 validation checks with zero violations. Two independent starter and
two independent full generations matched every ordered row/count/table hash,
aggregate hash and deterministic summary. No remaining technical Phase 05 blocker
identified. The full challenge remains unfinished: five labelled anomalies,
separate ground truth/anomaly evaluation, final CSV/JSON/SQL exporters and release.

## 2. Exact created/modified files and architecture

| File | Change |
| --- | --- |
| docs/phase05/prompt.md | Created |
| docs/phase05/evaluation-offer-design.md | Created |
| docs/phase05/reproducibility-evidence.json | Created |
| src/yottaflex/evaluation.py | Created |
| src/yottaflex/offers.py | Created |
| src/yottaflex/evaluation_generation.py | Created |
| src/yottaflex/evaluation_checks.py | Created |
| tests/test_evaluation.py | Created |
| tests/test_evaluation_generation.py | Created |
| reports/phase05-evaluation-offer-handoff.md | Created |
| AGENTS.md | Modified |
| README.md | Modified |
| docs/phase01/journal.md | Modified |
| docs/phase01/requirements.md | Modified |
| pyproject.toml | Modified |
| scripts/verify_generation_reproducibility.py | Modified |
| src/yottaflex/generate.py | Modified |
| src/yottaflex/generation_checks.py | Modified |
| src/yottaflex/ids.py | Modified |
| src/yottaflex/workflow.py | Modified |
| src/yottaflex/workflow_checks.py | Modified |

Ignored local products: `output/phase05/` databases/replay JSON,
`tmp/phase05-*` test/validation logs and `output/reports/phase05-evaluation-offer-handoff.md`
final downloadable closure copy. No raw assignment/PDF, DB, scratch log or secret
is tracked. Historical phase reports remain unchanged.

Architecture: same local stdlib/SQLite project, no new dependencies/services.
`evaluation` supplies create/edit/submit cards, read-only arithmetic/decisions and
review/rejection. `offers` supplies band/amount policies and create/submit/decide/
send/accept operations. `evaluation_generation` composes public operations;
`evaluation_checks` independently reconciles persisted source arithmetic and
approval/history/state rules, adding to prior scheduling checks. Existing
BEGIN IMMEDIATE writer serialization and scratch/no-overwrite publication remain.
No ORM, production concurrency, UI, external calendar or paid service.

## 3. Schema and prior-work preservation

**No schema change or migration.** Existing schema v2, 24 tables, 209 fields,
45 FK groups and 42 protection triggers retained. Dictionary freshness passes.
schema.sql byte-identical to pre-phase HEAD; source SHA256
`75c10e0264a798ff36e6ffae4c076483dc04247e9c8a5051eead036cacab1c6f`.
Initializer refuses unknown/v1/drifted files without resetting them.

Original master IDs/fields, skills/criteria, managers/original Staff,
requisition approvals/events and candidate/application creation events remain
unchanged. Master fingerprint now scopes Approval/history to requisition subjects
so new offer approvals are additive, not falsely treated as master corruption.
Candidate/application projections legitimately append later lifecycle changes.
Original default `--phase master` and `--phase interviews` modes preserved;
regression tests compare their archived canonical content exactly. Before new
augmentation, recorded parent hashes equal prior evidence:

| Baseline | Starter SHA256 | Full SHA256 |
| --- | --- | --- |
| Phase 03 master | d2e32228ceff587d4bbe36d944a78e902baa0d596fa447a15337d33fb157456d | 131e6d27738e28c29b6b79374cf5b9ad24e5d16d704fd01ff826e68f71b0385d |
| Phase 04 interviews | 994beef9ac1b45745e423810c08ff58ea589921a69067c4aeeb6c423bfba3b4e | a5294a1fdc94b676a821d16406524d343966c1b485dddf717a0c7559c48b1e4f |

## 4. Exact structured-data and all-table counts

| Table | STARTER | FULL |
| --- | ---: | ---: |
| Application | 160 | 8,000 |
| ApplicationEvent | 312 | 14,843 |
| Approval | 17 | 429 |
| ApprovalEvent | 34 | 858 |
| Availability | 320 | 2,680 |
| Candidate | 100 | 5,000 |
| CandidateEvent | 102 | 5,083 |
| CandidateSkill | 522 | 27,061 |
| HiringManager | 2 | 20 |
| Interview | 40 | 2,000 |
| InterviewEvent | 62 | 3,147 |
| InterviewPanel | 10 | 200 |
| InterviewParticipant | 96 | 5,000 |
| Offer | 7 | 229 |
| OfferEvent | 33 | 957 |
| PanelMember | 24 | 500 |
| Requisition | 10 | 200 |
| RequisitionEvent | 40 | 800 |
| SchemaMetadata | 1 | 1 |
| Scorecard | 24 | 1,122 |
| ScorecardEvent | 132 | 6,066 |
| ScorecardItem | 96 | 4,488 |
| SkillRequirement | 40 | 800 |
| Staff | 14 | 91 |

Required full counts are exactly 200 requisitions, 5000 candidates, 8000 applications,
2000 interviews; starter 10/100/160/40. All 11 core entities are populated in evaluation
mode. Scorecard/offer counts are chosen synthetic coverage, not employer-mandated
volumes. `SCORE-<Interview.interview_id>-<Staff.staff_id>` uses assigned Staff reviewer
identity. Offer counters start OFF-2026-000001. No prior ID rewritten.

## 5. Complete/incomplete scorecards and completion cohorts

| Metric | Starter | Full |
| --- | ---: | ---: |
| Scorecards total | 24 | 1122 |
| Submitted (complete) | 21 | 960 |
| Incomplete (unsubmitted) | 1 | 48 |
| Draft | 2 | 114 |
| Unsubmitted total | 3 | 162 |
| Completed interviews before this phase | 2 | 98 |
| Additional valid completions | 8 | 375 |
| Final completed interviews | 10 | 473 |
| Final scheduled /cancelled | 20 /10 | 953 /574 |

Additional zero-based interview-ID cohort modulo10 in{5,6} completes only still
scheduled meetings after their end through the existing operation; no existing
completed/cancelled history is changed, no interview row added. This increases
coverage while retaining exact40/2000 rows and withdrawal/rescheduling diversity.
Draft cohort completion-index modulo10=8; partial cohort9 leaves last reviewer's
first required item pending. Final two completed interviews also provide these
small-profile cases when there are at least4. Actual counts above are measured.
All legitimate drafts/partial cards have valid references/versions/items, NULL
total/submitted_at and remain unable to authorize review. No fake scorecards or
anomaly-labelled rows created merely to satisfy a gate.

## 6. Actual rubric and scoring example

Rubric: 0 no evidence,1 below,2 partially meets,3 meets,4 exceeds expectations.
Absence can be explained qualitatively; every scored item requires nonblank
synthetic evidence. Only assigned reviewer may author; only completed interview.
Highest applicable effective requirement version covering the whole interview;
weights must sum10000. All applicable criteria, even optional, must be scored
before submission; optional items do not have individual eligibility minima.
No missing-value zero substitution or partial-weight renormalization.

For persisted N=sum(score_value*applicable weight_basis_points),
`total_score_milli=(N+5)//10`: integer half-up rounding. Editable cards keep NULL
computed total; submitted cards lock against further public edits/resubmission.
Independent validator joins requirements/items and recomputes
`(N*1000+5000)//10000`. No independently random total.

Actual full example `SCORE-INT-2026-000147-STAFF-000047`, version 1, submitted:

| Criterion | Stored score | Basis-point weight | Product |
| --- | ---: | ---: | ---: |
| api_integration /SKILL-000585 | 3 | 4160 | 12480 |
| backend /SKILL-000586 | 3 | 2571 | 7713 |
| cloud /SKILL-000587 | 3 | 2384 | 7152 |
| problem_solving /SKILL-000588 | 4 | 885 | 3540 |

Weights 10000; N=30885; `(30885+5)//10=3089` (3.089 rubric points).
Evidence records stored skill level, role minimum and seeded observation
adjustment. These items have level 2, required target 2 (optional target 1), and
adjustment 0. All three reviewers of this interview scored 3089; aggregate 3089,
required minimum 3, spread 0. These are actual queried source rows/decisions.

Synthetic generation formula: clamp(3+CandidateSkill.level-criterion.min_proficiency,
0,4), then bounded -1 observation when first4 SHA256 bytes of
seed|interview|reviewer|criterion modulo11=0. Actual items/evidence are persisted
first; totals, decisions and offer amounts are calculated from those rows.
No independently random outcome/truth label. Policies are explicit AI proposals.

## 7. Derived evaluation decisions

Every noncancelled interview must be completed and each assigned reviewer must
submit the entire applicable rubric. Submission history must match current
source evidence. Equal reviewer/card mean, rounded half up to integer thousandths.

- Review: aggregate>=2500; every required item>=2; reviewer spread<=1000.
- Offer: separately require review eligibility, aggregate>=3000 and every
  required item>=3. Optional items still contribute weighted total.
- Conflicting/low complete reviews fail review; explicit negative decision may
  reject the application. Incomplete reviews remain interviewing.
- Baseline retains reviewed/below-offer cases rather than inventing rejections.

| Decision at evaluation time | Starter | Full |
| --- | ---: | ---: |
| Incomplete gate | 2 | 96 |
| Review eligible and offer eligible | 7 | 243 |
| Reviewed, below separate offer policy | 1 | 134 |
| Complete evaluation rejected by review policy | 0 | 0 |

No complete baseline evaluation happened to fail the review threshold in this
selected pool; tests exercise actual low-score/conflicting/gate failures. Negative
baseline outcomes also include94 rejected offers. Do not invent rejected-review
counts. Later accepted offers can withdraw already-reviewed sibling applications,
so final states differ from review-time decisions.

## 8. Review-stage transitions and final projections

Actual interviewing→reviewed transitions: starter 8/full 377. Applications reach
reviewed only after complete audited source evaluations and deterministic policy.
Every decision event preserves card IDs/totals/aggregate/minimum/spread/time.
Direct stage calls route to the actual review gate; direct offer/hired bypasses
raise OFFER_OPERATION_REQUIRED. Low-score rejection is an explicit audited API.

| Final application state | Starter | Full |
| --- | ---: | ---: |
| applied | 111 | 5687 |
| interviewing | 24 | 1132 |
| reviewed | 1 | 116 |
| rejected | 1 | 94 |
| hired | 6 | 135 |
| withdrawn | 17 | 836 |

Candidate schema remains active/withdrawn; no invented candidate hired enum.
Requisition remains open because no headcount/fill rule is specified. On hiring,
withdraw other applied/screening/interviewing/reviewed apps and cancel scheduled
children atomically, retaining every completed/scorecard/historical record.
No final hired candidate has active scheduled bookings in the validated baseline.

## 9. Offers created, approved, rejected and accepted

| Metric | Starter | Full |
| --- | ---: | ---: |
| Offers created | 7 | 229 |
| Approved offer decisions /Approval records | 6 | 135 |
| Rejected offer decisions /Approval records | 1 | 94 |
| Final accepted offers /hired apps | 6 | 135 |
| Current pending/draft offers | 0 | 0 |
| Final rejected offers | 1 | 94 |

Approved is a cumulative decision, not current Offer status after acceptance.
Full243 offer-eligible reviews produced229 offers after deterministic sibling
resolution; additional reviewed candidates below offer policy remain without an
offer. Earlier hires may resolve/withdraw other evaluated applications. No
arbitrary offer quota/random accept-or-reject label. Generated approved offers
are deterministically accepted through explicit operations.

## 10. Compensation and approval reconciliation

Offer creation requires active candidate, reviewed state, offer-eligible actual
reviews, approved/open effective requisition and approved compensation event.
Currency/reference must match the historical event; current band must still
reconcile. All amounts positive integer minor units, inclusive lower/upper bounds.
Generated default amount:

`lower + (upper-lower)*clamp(aggregate_milli-3000,0,1000)//1000`

Authorized proposals may choose another in-band amount with reason; baseline
uses the formula. Test exact endpoints; below/above/currency/fraction/bool reject.
Original compensation history is never edited to pass an invalid proposal.

One offer-specific Approval per request, requisition_id=NULL. Independent effective
appointed HR/admin must differ from creator AND requester. One-level synthetic
budget rule approves amount<=lower+floor(70% of band width); higher in-band amount
is legitimately rejected. Decision API enforces that policy and effective dates;
request/decision time and reason retained. No invented multi-level workflow.

All 99 validation checks include zero offer band/currency, arithmetic, eligibility,
actor/separation, budget, chronology and final-state violations. FK integrity and
all four active/capacity interviewer/candidate overlap counts are zero. No
incompatible active final offer per candidate; schema's per-app index preserved.

## 11. Actual end-to-end positive path

Full `APP-CAND-000031-REQ-2026-000147` followed:

`applied → screening → interviewing → reviewed → offer → hired`

ApplicationEvent sequences 1–10 retain submission, selection, reservation, recorded
completion, review, proposal, approval request, approval, local presentation and
candidate acceptance. Interview INT-2026-000147 has three assigned reviewer cards,
each 3089, required min3. Actual approved band REQEV-000587: INR 90456200..118806200
minor units. Derived amount 92979350, since width 28350000 *89//1000=2523150 above
lower. Offer `OFF-2026-000003` accepted. Offer-specific `APR-000203` appointed
STAFF-000002; request 1783475397, approval 1783475398, followed by sent/accepted
states. App hired only after approval, with sibling cleanup in the same transaction.

`send_offer` only records local synthetic sent status. It sends no email/network
message and does not contact any candidate/recruiter. All examples use synthetic IDs.

## 12. Rejected operations actually demonstrated

Default generated summaries record these rejected calls without state changes:

| Business error | Starter attempts | Full attempts |
| --- | ---: | ---: |
| DUPLICATE_SCORECARD | 1 | 1 |
| SCORECARD_INCOMPLETE submission | 1 | 48 |
| REVIEW_GATE_INCOMPLETE | 2 | 96 |
| OFFER_OUTSIDE_BAND | 1 | 1 |

Unit tests additionally execute invalid reviewer/actor/criterion/version/value,
missing evidence/review, expired approval/self-approval/unappointed approver,
currency/band endpoint failures, duplicate active offer, policy mismatch, invalid
hired transition, withdrawn/rejected candidate/app rejection, submitted edits,
backdating and partial-mutation failures. Failed operations compare complete
canonical data before/after to confirm rollback/no fictitious success events.
Isolated malformed fixtures verify guards/validator; no production anomaly dataset
or truth labels are implemented.

## 13. Event-history validation and transactions

Existing BEGIN IMMEDIATE lock/rollback strategy preserved. Each scorecard item
change, submission, review, offer, approval and acceptance appends appropriate
explicit events atomically with projection/child writes. Per-entity sequences and
status continuity, before/after snapshots, actor/effective times, source references,
approval chronology and final projection agree. Submitted evidence/current offer
snapshots are checked against latest history before further operations.

Full event counts: 6066 ScorecardEvent, 957 OfferEvent, 858 ApprovalEvent
(400 requisition +458 offer), 14843 ApplicationEvent, 3147 InterviewEvent.
No history UPDATE/DELETE/REPLACE permitted by existing triggers. Public submitted
card edits are blocked; full child snapshots preserve every editable change.
Acceptance failure rolls back sibling withdrawals/cancellations too.

## 14. Actual commands and test outcomes

Executed from project root with pinned .venv interpreter. Read-only inspection
used pwd/git status/branch/log, rg/cat/sed/Python over AGENTS/README/old handoffs/
requirements/dictionary/schema/modules/tests, and bundled pypdf for both complete
one-page PDFs. Source SHA256/size matched manifest. Some large tool output was
truncated; relevant schema/enum/approval/history sections inspected separately.
No external code/paid dependency downloaded.

| Actual command | Observed outcome |
| --- | --- |
| `PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase evaluations --profile starter --database output/phase05/initial-starter.sqlite3` | exit 0;24 cards/7 offers; initial94-check validation passed |
| same generator `--profile full --database output/phase05/initial-full.sqlite3` | exit 0;1122 cards/229 offers;18.486553s initial run |
| `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v` before new test modules | all 99 prior tests passed,27.063s |
| `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -p test_evaluation.py -v` | initial37 operation tests passed,0.893s |
| same targeted module `-q` checkpoint | passed before final additional boundary tests |
| full unittest command expanded checkpoint | 144 tests passed,64.347s |
| full unittest command after final guards/tests, log `tmp/phase05-final-tests-148.log` | **148 tests passed,80.699s, OK, exit 0** |
| `PYTHONPATH=src .venv/bin/python3 scripts/verify_generation_reproducibility.py --phase evaluations --directory output/phase05/repro-final-20261022 --profile both --seed 20261022` | exit 0; two independent generations/profile; every row/count/hash/summary equal |
| `cp output/phase05/repro-final-20261022/reproducibility.json docs/phase05/reproducibility-evidence.json` | success; byte equality separately verified |
| `PYTHONPATH=src .venv/bin/python3 -m yottaflex.evaluation_checks --database output/phase05/repro-final-20261022/starter-1.sqlite3 --profile starter --seed 20261022` | exit 0;99 checks zero; matches replay summary |
| same evaluation_checks command with `full-1.sqlite3 --profile full` | exit 0;99 checks zero; matches replay summary |
| `PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check` | exit 0; every field/constraint matches actual schema/metadata |
| `PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh` | exit 0;4 shell checks +3 Python groups; local runtime/source identity/privacy passed |
| `git diff --check` | exit 0; no whitespace errors |
| Python prompt/schema/matrix/evidence assertions | exact prompt bytes, unchanged schema and original75 rows, unedited measured evidence verified |

A 147-test checkpoint also passed in64.206s before adding an explicit conflicting-
reviewer spread test. The final 148 suite includes that test.
No actual unit-test/generation failure occurred in this phase. Earlier checkpoint
runs are not substituted for final 148 tests/99 checks. Deliberate error-code tests
are expected rejections, not fabricated passing output.

Tests cover all 33 requested topics:41 operation methods cover cards/reviewers/
criteria/0–4 boundaries/required+optional omissions/duplicates/source arithmetic/
locked edits/versions/gates/incomplete interviews/withdrawn-rejected states,
separate review vs offer policy, exact band endpoints/currency/roles/separation/
expiration/duplicates/budget decisions/approved+rejected audits/hired paths/cleanup,
partial-write rollback, chronology/tampering and immutable events. Eight generation
methods exercise starter/full counts, all-row replay, old hashes/schema, actual
variety, independent score/band recomputation, semantic corruption detection,
phase-scoped validators and no-overwrite preservation. All 99 old tests remain.

## 15. All validation check counts

Each final generated run and both standalone CLI validations returned passed=true.
All 99 checks below have measured zero violations; no hardcoded PASS rows.

| Check | Starter violations | Full violations |
| --- | ---: | ---: |
| exact_populated_counts | 0 | 0 |
| deferred_tables_empty | 0 | 0 |
| foreign_keys | 0 | 0 |
| sqlite_integrity | 0 | 0 |
| primary_keys | 0 | 0 |
| required_fields | 0 | 0 |
| logical_time_bounds | 0 | 0 |
| deterministic_identity_formats | 0 | 0 |
| application_pair_uniqueness | 0 | 0 |
| phase04_lifecycle_states | 0 | 0 |
| active_staff_and_managers | 0 | 0 |
| application_chronology | 0 | 0 |
| approval_subjects | 0 | 0 |
| requisition_approval_histories | 0 | 0 |
| requirement_weights_ranges_and_approval_bands | 0 | 0 |
| candidate_skill_ranges | 0 | 0 |
| candidate_skill_coverage | 0 | 0 |
| synthetic_contacts | 0 | 0 |
| CandidateEvent_creation_history | 0 | 0 |
| ApplicationEvent_creation_history | 0 | 0 |
| candidate_experience_history | 0 | 0 |
| snapshot_states_times_actors_and_no_truth_labels | 0 | 0 |
| exact_interview_count | 0 | 0 |
| active_interviewer_overlaps | 0 | 0 |
| active_candidate_overlaps | 0 | 0 |
| capacity_interviewer_overlaps | 0 | 0 |
| capacity_candidate_overlaps | 0 | 0 |
| panel_requisition_joins | 0 | 0 |
| membership_overlap | 0 | 0 |
| active_membership_calendar_participants | 0 | 0 |
| active_withdrawal_or_stage_mismatch | 0 | 0 |
| global_withdrawal_consistency | 0 | 0 |
| intervals_and_states | 0 | 0 |
| interview_event_actors | 0 | 0 |
| interview_support_id_formats | 0 | 0 |
| application_interview_audit_link | 0 | 0 |
| application_projection_time | 0 | 0 |
| application_time_snapshots | 0 | 0 |
| candidate_withdrawal_history | 0 | 0 |
| completion_chronology | 0 | 0 |
| event_chronology | 0 | 0 |
| event_continuity | 0 | 0 |
| event_sequence | 0 | 0 |
| history_intervals | 0 | 0 |
| legal_transitions | 0 | 0 |
| participant_recording_time | 0 | 0 |
| participant_snapshots | 0 | 0 |
| projection_status | 0 | 0 |
| reschedule_history | 0 | 0 |
| schedule_history | 0 | 0 |
| schedule_projection | 0 | 0 |
| status_snapshots | 0 | 0 |
| workflow_truth_leakage | 0 | 0 |
| approval_authority_separation | 0 | 0 |
| approval_budget_decision | 0 | 0 |
| approval_decision_actor_time | 0 | 0 |
| approval_effectivity | 0 | 0 |
| approval_precedes_offer_decision | 0 | 0 |
| approval_request_chronology | 0 | 0 |
| approval_request_link | 0 | 0 |
| criterion_weight_snapshot | 0 | 0 |
| editable_scorecard_legitimacy | 0 | 0 |
| history_actor_time | 0 | 0 |
| history_continuity | 0 | 0 |
| history_edges | 0 | 0 |
| history_full_snapshots | 0 | 0 |
| history_projection | 0 | 0 |
| history_sequence | 0 | 0 |
| history_snapshot_states | 0 | 0 |
| history_time | 0 | 0 |
| independent_score_arithmetic | 0 | 0 |
| offer_actor_authority | 0 | 0 |
| offer_application_projection | 0 | 0 |
| offer_approval_state | 0 | 0 |
| offer_band_currency_amount | 0 | 0 |
| offer_band_snapshot | 0 | 0 |
| offer_candidate_lifecycle | 0 | 0 |
| offer_creation_audit | 0 | 0 |
| offer_creation_decision | 0 | 0 |
| offer_evaluation_gate | 0 | 0 |
| review_decision_chronology | 0 | 0 |
| review_decision_reconciliation | 0 | 0 |
| review_threshold_enforcement | 0 | 0 |
| reviewer_role_effectivity | 0 | 0 |
| scorecard_criteria_version_coverage | 0 | 0 |
| scorecard_event_author | 0 | 0 |
| scorecard_identity_reviewer | 0 | 0 |
| scorecard_interview_chronology | 0 | 0 |
| submission_chronology | 0 | 0 |
| submission_event_time | 0 | 0 |
| submitted_rubric_completion | 0 | 0 |
| incompatible_candidate_offers | 0 | 0 |
| hired_candidate_scheduling | 0 | 0 |
| advanced_stage_support | 0 | 0 |
| advanced_application_actor | 0 | 0 |
| ScorecardEvent_ids | 0 | 0 |
| OfferEvent_ids | 0 | 0 |
| Offer_ids | 0 | 0 |
| evaluation_truth_leakage | 0 | 0 |

## 16. Independent same-seed checksum evidence

Seed 20261022; logical origin 2026-01-01 UTC. Two separate DB generations/profile,
not copies. Stream all 24 tables by declared primary keys; compare every record,
row counts, table SHA256, aggregate SHA256 and deterministic summaries including
scores/amounts/approval decisions/final lifecycle. No binary SQLite proof.

| Profile | Rows compared per pair | Equal aggregate SHA256 |
| --- | ---: | --- |
| starter | 2198 | d58886c7f9758d7fb03139416493ff94bba6577d63097ecf3e623365f70d2cfe |
| full | 89575 | 7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb |

Per-table counts/hashes and every comparison are in
`docs/phase05/reproducibility-evidence.json`, copied unchanged from actual output.
Old master/interview digests match archived files (section3). New complete hashes
differ legitimately because scorecards/offers/approvals and lawful lifecycle
records were added; no nondeterministic content difference remains. Separate
standalone validation summaries matched replay checks exactly.

## 17. Actual performance

Local CPython 3.14.5/SQLite 3.53.1. Seconds are measured diagnostics, excluded from
canonical rows and deterministic summary. Not a performance guarantee. Evaluation
includes extra recorded completions/cards/reviews; offer duration includes
proposal/approval/acceptance/sibling cleanup. Final validation includes composed
master/scheduling/evaluation/history checks. Total includes earlier generation,
checks, summaries/hashes and atomic publication.

| Profile/run | Total seconds | Evaluation seconds | Offers seconds | Final validation seconds |
| --- | ---: | ---: | ---: | ---: |
| starter 1 | 0.358727 | 0.103607 | 0.040046 | 0.026667 |
| starter 2 | 0.309430 | 0.096239 | 0.034932 | 0.025928 |
| full 1 | 17.745425 | 5.155598 | 1.344735 | 1.630975 |
| full 2 | 18.101667 | 5.002994 | 1.725341 | 1.634652 |

Complete standalone reproducibility execution: **37.771052s**.
Detailed scheduling/Phase 04-validation component times retained in evidence.
Existing indexes/simple SQL suffice; no caching/concurrency/framework optimization
added without a measured need. Peak RSS was not measured or fabricated.

## 18. Known limitations and risks

- Review/rubric/offer/approval thresholds and deterministic acceptance are explicit
  synthetic assumptions. Human policy/design/line ownership review is pending.
- Submitted-card corrections, decline/expiry and advanced/post-hire withdrawal
  need explicit future policies; no silent destructive revision. Generic stage
  changes cannot bypass supported operations. Current compensation authorization
  must match historical snapshot; band revisions require a separate policy.
- Only local Staff authorization, not authentication/security boundary. A raw SQL
  owner can bypass business operations; tested semantic corruption is detected
  by validators and immutable histories. SQLite default busy timeout can surface
  lock errors. Supported FK-enabled connector is required.
- Existing greedy calendar planner can fail fixed capacity despite alternative
  arrangements; no runtime capacity extension. Prior Phase 04 failed experiment
  remains historically documented; default validated modes still match archives.
- All data/distributions are synthetic; no empirical fairness/real-world validity
  claim. No requirement for fixed employer Scorecard/Offer count invented.
- No deliberate five-negative artifacts/truth/anomaly evaluator/precision-recall
  or full exports yet. Current JSON is diagnostics/evidence, not complete dataset
  CSV/JSON/SQL exporter. Existing invalid fixtures are tests only.
- Privacy smoke checks source identity/filenames/private-key patterns, not every
  possible sensitive value. Final human content/release review and all-tools
  prompt audit still required; private sources/DBs remain local and ignored.
- Original invitation send-time/round-label and portal-vs-email submission-channel
  uncertainty persists. Deadline above preserved; no submission/contact action.
- Same runtime/schema/config verified; no blanket cross-engine compatibility
  or arbitrary-scale/performance guarantee. No destructive reset/migration.

## 19. Requirement coverage updates

All 75 original source rows unchanged; appended current Phase 05 overlay in
`docs/phase01/requirements.md`. All previous historical reports/overlays retained.

| Group | Coverage now | Deferred |
| --- | --- | --- |
| F01–F05,F09–F12 | preserved parents/scheduling/calendars/stages, actual events/variants/actors/metrics | final human ownership/end-to-end artifact review |
| F03,F06–F08 | real source-based structured evaluations, review gate, compliant offer/approval/hire/reject path | full challenge scenario/export demonstration |
| D01–D11 | all 11 entities populated, unchanged schema/relationships, stable IDs/counts/profiles/old hashes | equivalent final export identities/imports |
| D12–D18,N01–N05 | valid baseline, derived calculations/decisions, legitimate incomplete reviews, ordinary anomaly-prevention guards | all five labelled injections/truth isolation/evaluator |
| D19–D22,V01–V09 | actual independent keys/joins/time/arithmetic/history/approval/band/state checks and replay | final CSV/JSON/SQL/export/anomaly reconciliation/metrics |
| V10–V12,S01,S03–S09,S15–S17 | local stdlib/synthetic provenance, exact prompt history, AI disclosure/tests/design/scoped Git | independent human understanding, all-tools/release/privacy review |
| S02,S10–S14,C01–C03,O01–O04 | deadline/lawful/conditional/optional/admin tracking preserved | public repository/submission/channel/access checks later; no action now |

## 20. AI involvement and human-review status

Codex generated the implementation/tests/docs and executed every reported check.
No subagents, other-person implementers, additional generative tool, paid service,
new dependency or imported core solution. PDF skill used read-only for official
source review. An additional status/persistence prompt is preserved verbatim as journal P008;
no extra AI tool was introduced.

Complete22-section user prompt retained verbatim in `docs/phase05/prompt.md`,
SHA256 `0bdf78c7fca17e48239934daf8f6dc57e418b1c4efc0eec7d3376fb00930fc38`.
Journal P007/H022–H025 records conditional Phase 04 approval and proposed AI policies
separately from actual AI work. Human Phase 05 personal testing/design/code review,
line-by-line understanding and walkthrough ownership remain PENDING. Prior prompt
records/export limitations preserved; human must audit any other AI tools/chats.
No AI-run test is attributed to human validation. Responses optional per sources.

## 21. Local Git commits and working-tree state

Initial HEAD `4c567e7` (Phase 04 handoff), preserved branch/history.
Implementation commit: `c96974c20ac547e6e2f50c411f0b61fbfb55e8d0`.
Implementation message: `feat: add structured evaluation and auditable offer approvals`.
Handoff message: `docs: record phase 05 evaluation evidence and handoff`.
Implementation commit succeeded after explicit staging/review of20 files.
Immediately afterward only this report remained untracked; all source changes
were committed. Only reviewed explicit paths were staged; no .pdf/.zip/.sqlite3/.db/private
assignment or ignored-output path. Report is a separate commit after tested code.
Its own commit hash/clean-state evidence appears in the ignored downloadable
closure copy, avoiding a self-referential tracked-file commit loop.
No push/merge/remotes/publish/contact/submission. Existing commits not rewritten.

## 22. Phase 06 recommendations and stop boundary

**Phase 05 PASS:** actual cards and legitimate incomplete variants; complete-review
and separate offer gates; exact independent score reconciliation; valid relevant
reviewers/criteria/versions; real reviewed apps and compliant offers; independent
approved/rejected histories;135 legitimate full hires; invalid transitions blocked;
all parent/interview counts exact; all 148 tests and99 checks pass; all-row replay
matches; previous content/schema constraints preserved; full prompt/docs retained.

Next human action: review this report/design/code and run the documented commands
personally, especially proposed policy thresholds/authority/cleanup assumptions.
No Phase 06 implementation has started. After explicit scope approval, recommended
next work is deterministic isolated mutation of a validated baseline for all five
mandatory scenarios (missing review, staff overlap, over-band offer, withdrawn
still scheduled, irrelevant criterion), separate keyed truth, independent findings
and genuine anomaly metrics. Full exporters/import checks/delivery manifest and
public release require their own authorized scope. Do not infer authorization
from this recommendation or the official submission documents.

**STOP after Phase 05. Await human review and explicit next-phase authorization.**


Actual Git finalization commands so far: explicit `git add` of20 intended source/
test/documentation/evidence files; `git diff --cached --check` and staged file/
prompt/schema/matrix/privacy assertions passed. Implementation commit succeeded
with generic Codex local identity. Precommit smoke passed all4 shell +3 Python
check groups for58 publication candidates. The report gets its own focused local
commit; final hashes/clean-state closure follows in downloadable copy.
