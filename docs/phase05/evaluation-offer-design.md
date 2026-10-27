# Phase 05 structured evaluation, offers and approvals

Scope authorization: complete user prompt in prompt.md (22 sections). It states
Phase 04 is conditionally approved and authorizes Phase 05 only. Original problem
statement and both official PDFs are challenge/submission evidence; they do not
authorize publishing or contacting people. No schema migration or new dependency.
Python 3.14.5 stdlib/SQLite 3.53.1 and existing 24-table v2 schema remain.

## Architecture and public operations

`evaluation.py` owns create_scorecard, set_scorecard_item, submit_scorecard,
review_application and reject_evaluated_application; computed_card and
evaluate_application are read-only decision functions. The general workflow
transition_application(...,"reviewed") delegates to the actual review operation;
the old deferred-review stub is replaced. Direct reviewed→offer/offer→hired calls
raise OFFER_OPERATION_REQUIRED: use the corresponding offer operation.

`offers.py` owns create_offer, submit_offer, decide_offer, send_offer, accept_offer.
`send_offer` changes only a local synthetic status; it never sends a message or
contacts a candidate/recruiter. All mutations own BEGIN IMMEDIATE from prerequisite
checks through projection, child and event writes to commit; any exception rolls
back. No nesting, asynchronous service, ORM, generic repository or paid provider.

`evaluation_generation.py` composes those public operations deterministically.
`evaluation_checks.py` independently recomputes weighted scores, decisions and
approval/band relationships, adding to phase-aware scheduling/master checks.
Shared schema/canonical serializer/initializer and prior tests are retained.
The generator only publishes its private scratch DB after all final checks and
master preservation succeed. Existing paths and unknown schemas are never reset.

## Rubric, requirement version and reviewer eligibility

| Value | Meaning |
| ---: | --- |
| 0 | No evidence; explanation of absence still recorded |
| 1 | Below expectations |
| 2 | Partially meets expectations |
| 3 | Meets expectations |
| 4 | Exceeds expectations |

Criterion scores are relative to role-specific stored min_proficiency, not a
replacement for CandidateSkill levels. Booleans/floats/out-of-range scores are
rejected as INVALID_RUBRIC_VALUE. Every scored item needs nonblank evidence;
pending items may have NULL score/evidence. No real personal evaluation evidence.

The effective rubric is the highest rubric_version with active requirements
covering the complete interview interval. That version must have required
criteria and weights summing exactly 10000; no fallback to an older/incomplete
version. Scorecard uses that version and pre-creates every criterion as pending.
A criterion ID from another requisition/version/effective interval is rejected.
Weights are copied from the applicable requirement; submission rechecks them.

Only completed interviews with recorded completion history may have scorecards.
Only Staff assigned as reviewer in immutable InterviewParticipant may author;
actor_id must equal reviewer_staff_id. Observer, arbitrary HR/operator, inactive
or ineffective reviewer and cancelled/scheduled interview are rejected. Reviewers
may edit only their own draft/incomplete card while the app is interviewing and
candidate active. Evaluation time follows recorded interview completion.

Canonical identity is `SCORE-<interview-id>-<Staff.staff_id>`; Staff is the reviewer
identity actually supported by the schema. Duplicate interview/reviewer is rejected.
No new Reviewer entity, enum or arbitrary identifier is invented.

## Exact score arithmetic and completeness

All applicable criteria, including those marked optional, must be scored with
evidence to submit. Optional means no individual minimum for eligibility, not
permission to drop its weight. Missing values never receive zero or renormalize
the remaining weights. This is an explicit conservative synthetic policy.

Let N=sum(persisted item.score_value * applicable requirement.weight_basis_points).
Each item's stored weight must equal its requirement, and total weights=10000.

`total_score_milli = (N + 5) // 10`

This rounds N/10 half up, equivalent to normalized 0–4 times 1000. No binary floating
point. The independent validator recomputes `(N*1000+5000)//10000` from joined
source items/requirements. Editable cards have NULL total/submitted_at, even if
all items are filled; only submission computes the total. Submitted cards cannot
be edited/resubmitted by public operations. There is no silent correction or
new duplicate SCORE ID: a formal correction policy would need future review.

Every create, item edit/reset and submit appends ScorecardEvent with complete
before/after card/items snapshots. Initial state draft; first/subsequent item
edits set/retain incomplete; complete submission sets submitted and timestamp.
An unfilled draft and a partially filled incomplete card are legitimate baseline
states. Rejected submission does not append a fake completion event.

## Required review, aggregation and decisions

Consider every noncancelled interview for an application. At least one must exist;
all must be completed, with every assigned reviewer submitting an audited complete
card. No majority/quorum bypass, missing-card substitution or ignored low review.
Current submitted snapshot must match immutable submission history and source
arithmetic; decision time must be >= all submission times. Relevant requirements,
versions, items and weights are rechecked.

Each reviewer/card has equal weight across the application. Round arithmetic mean
of card totals half up to integer thousandths. Record scorecard IDs, card totals,
aggregate, required-item minimum, reviewer spread, evidence time and policy version
in the ApplicationEvent decision snapshot. All can be independently recomputed.

- Review eligibility: aggregate>=2500, every required item in every required card
  >=2, and max reviewer total minus min<=1000.
- Conflicting evaluations beyond that spread fail review; no arbitrary tie-break.
- Offer eligibility is separate: review eligible, aggregate>=3000 AND every
  required item in every required card>=3. Optional item scores affect weighted
  total but not the individual required minimum.
- Complete but negative review can use reject_evaluated_application from
  interviewing; reviewed but below offer policy can also be explicitly rejected.
  Positive evaluations cannot be arbitrarily rejected by that operation.
- Baseline generation leaves reviewed/below-offer applications reviewed rather
  than forcing a negative label. Missing/incomplete evaluations stay interviewing.

These thresholds are proposed synthetic policies, not employer-prescribed values.
Actual outcome distribution is measured; no employer-mandated Scorecard/Offer
counts are invented. Final decisions derive from recorded items and approvals.

## Compensation, offers and approval authority

create_offer requires reviewed state, active candidate, complete offer-eligible
recorded evaluation, approved/open effective requisition and causal approval.
It captures the latest approved RequisitionEvent with nonnull compensation bands
as of creation, with exact requisition/currency linkage. Current requisition band
must reconcile to that event. Subsequent offer operations require the same current
authorization; band changes need an explicit new-offer policy, not silent mutation.

Amounts are positive integer minor units. Both band endpoints inclusive; below,
above, currency mismatch, bool/fraction and unapproved role reject atomically.
Default amount is derived, with integer floor to a minor unit:

`lower + (upper-lower) * clamp(aggregate_milli-3000, 0, 1000) // 1000`

Authorized HR/admin/owning manager may propose another in-band amount, with reason.
All generated offers use the derived amount. Every offer is_final=1. Application
creation advances reviewed→offer atomically. One incompatible active final offer
per candidate (across applications), including draft/pending/approved/sent/accepted;
this is stricter than the schema's per-application partial unique index.

submit_offer appends a separate offer-specific Approval with requisition_id=NULL,
offer_id set, appointed effective HR/admin and explicit request time. Requisition
Approvals remain unchanged and distinct. A creator or requester may not be the
approver. No unsupported multi-level approval chain is introduced.

One-level synthetic budget policy: amount <= lower + floor(70% of band width)
is approved; otherwise rejected, even though both can be within the legal band.
The decision API enforces that result rather than accepting arbitrary approval
booleans. Equality at the budget limit is allowed. This policy provides auditable
positive and negative decisions without random outcomes or altering band history.
Only the appointed active HR/admin may decide, within Approval effective dates,
after request. Approval/Offer events and application outcome commit together.

Approved offers may become sent (local row state only), then accepted. HR/admin
records synthetic candidate acceptance with optional candidate-origin FK. Accepted
requires causal independent approval, coherent band/evaluation and no other
incompatible offer. Rejected approval sets both Offer and Application rejected.
All generated approved offers are deterministically accepted; no random candidate
accept/decline label is invented. Decline/expiry/advanced withdrawal operations are
not implemented simply because their enums exist.

## Transition and cleanup matrix

| Source → target | Operation / actor | Prerequisites | Event |
| --- | --- | --- | --- |
| Scorecard none→draft | create / assigned reviewer | completed interview, correct rubric/assignment | created |
| draft/incomplete→incomplete | set item / same reviewer | editable, relevant criterion/value/evidence | revised |
| draft/incomplete→submitted | submit / same reviewer | every criterion complete; source weights/total | status_changed |
| interviewing→reviewed | review / HR/admin/owning manager | completed audited reviews and review thresholds | decision_recorded |
| interviewing/reviewed→rejected | evaluated rejection / same | complete negative policy decision | decision_recorded |
| reviewed→offer | create_offer / HR/admin/owner | distinct offer threshold, band, no active offer | Offer created + App status_changed |
| Offer draft→pending_approval | submit / HR/admin/owner | independent appointed HR/admin | Approval created + Offer status_changed + App revised |
| pending→approved/rejected | decide / appointed HR/admin | time, separation, band and budget policy | Approval/Offer decision_recorded; App revised/rejected |
| approved→sent | send / HR/admin/owner | actual approved decision | Offer status_changed + App revised |
| sent→accepted; App offer→hired | accept / HR/admin | independent approval/evaluation/band, candidate active | Offer/App status_changed; sibling withdrawal/cancellation events |
| Other app reviewed→withdrawn | acceptance cleanup / HR/admin | another app for same candidate hired in this transaction | withdrawn |

Prior application screening/scheduling/reschedule/cancel/complete/withdraw paths
remain. Direct hired/offer transitions cannot bypass records/gates. On acceptance,
withdraw all other applied/screening/interviewing/reviewed applications; cancel
scheduled child meetings and append their events in the SAME transaction. Preserve
completed/cancelled history and all scorecards. Other offer/hired sibling state
must be explicitly resolved; no hidden competing offer cancellation.

Candidate has only active/withdrawn schema states; no invented hired candidate
state. Global withdrawal after hire is rejected pending explicit post-hire policy;
reviewed/offer global withdrawal also requires a future explicit policy. Regular
pre-review withdrawal remains supported. Requisition stays open because no
headcount/fill requirement is defined; original master history remains preserved.

## Failures and audit guarantees

Stable codes include INTERVIEW_NOT_COMPLETED, REVIEWER_INELIGIBLE,
DUPLICATE_SCORECARD, IRRELEVANT_CRITERION, INVALID_RUBRIC_VALUE, EVIDENCE_REQUIRED,
RUBRIC_UNAVAILABLE/INVALID/VERSION_INVALID, WEIGHT_MISMATCH, SCORECARD_INCOMPLETE,
SCORECARD_LOCKED, REVIEW_GATE_INCOMPLETE, SCORE_RECONCILIATION_FAILED,
REVIEW_DECISION_FAILED, OFFER_INELIGIBLE, OFFER_OUTSIDE_BAND, CURRENCY_MISMATCH,
INVALID_AMOUNT, COMPENSATION_SNAPSHOT_MISMATCH, INCOMPATIBLE_ACTIVE_OFFER,
SELF_APPROVAL_FORBIDDEN, APPROVER_UNAUTHORIZED, APPROVAL_POLICY_MISMATCH,
APPROVAL_INEFFECTIVE/REQUIRED, OFFER_STATE_INVALID, OFFER_OPERATION_REQUIRED.
Common actor/history/metadata/time/stage errors retain existing codes.

Events contain stable counter ID, contiguous subject sequence, previous/new
state, actor, logical occurrence/record time, reason/correlation and full snapshots.
Approval events distinguish offer/requester/decision actors. Source items and
accepted review/offer decision references remain visible. No issue_type,
ground_truth, expected_decision or anomaly_label fields are emitted.

BEGIN IMMEDIATE serialization and existing FK/triggers prevent write races and
history UPDATE/DELETE/REPLACE. Failed prerequisites and injected mid-write failures
roll back projections/items/approvals/events. Read-only rejected demonstrations
appear in diagnostic summaries without fictitious domain events. Direct SQL is
not a multi-user security boundary; independent validators detect tested semantic
corruptions. Submitted-card immutability is enforced by public operations plus
audit reconciliation; the existing schema is not silently weakened or expanded.

## Deterministic generation and coverage

Original master and interview modes remain unchanged, including their canonical
row hashes. New `--phase evaluations` builds/verifies the same Phase 04 baseline,
records that digest, then augments it. Additional scheduled interviews with
zero-based ID cohort modulo 10 in {5,6} are legitimately completed after their end
via public operation; existing completed/cancelled rows are never rewritten.
This increases coverage from 2/98 completed to 10/473 in the observed default runs,
while preserving 40/2000 rows, scheduling rules, withdrawals and all old IDs.

Scoring base is clamp(3 + stored candidate skill level - stored role minimum,0,4).
A controlled downward observation adjustment of 1 occurs when SHA256 of
`seed|interview|reviewer|criterion` (first 4 bytes as big-endian integer) modulo11=0.
This models bounded reviewer measurement variation from seeded inputs. Persist
actual item/evidence first; all totals/decisions subsequently derive from those
rows. No independent random total, offer amount, eligibility or anomaly label.

Process completed interviews by ID, reviewers by Staff ID and requirements by
criterion ID. For zero-based completion index modulo 10=8 leave drafts;9 leave
last reviewer's first required item pending. Also reserve final two interviews
for these cases when >=4 completions, ensuring small starter coverage. Other
cards submit normally. Observe exact counts from DB, never infer nominal quotas.
Evaluation decisions start logical origin+188days after calendar end; monotonic
seconds, independent of execution wall time. Reviewers remain effective until 190d.

Evaluate all eligible completed apps before offers. Process reviewed apps in
application-ID order; earlier legitimate hires may withdraw sibling apps, which
are skipped. Approved offers deterministically accepted; over-budget in-band
proposals rejected. Diagnostics separately count review-time decisions vs final
projections after cleanup. No scoring/offer volume is claimed prescribed by source.

## Independent validation, commands and limits

Evaluation acceptance composes previous FK/PK/enums/natural-key/time/master/
scheduling checks with independent rubric coverage/version/source arithmetic,
draft legitimacy, full event/child snapshot reconciliation, review decisions,
compensation band/currency, approved/rejected budget/actors/request chronology,
separation of duties, offer/application projections, hired scheduling cleanup,
advanced-stage support and no truth leakage. Earlier scope validators remain
strict for their modes; Phase 05 is not accepted by pretending downstream empty.

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase evaluations --profile starter --seed 20261022 --database output/phase05/new-starter.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase evaluations --profile full --seed 20261022 --database output/phase05/new-full.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.evaluation_checks --database output/phase05/new-full.sqlite3 --profile full --seed 20261022
PYTHONPATH=src .venv/bin/python3 scripts/verify_generation_reproducibility.py --phase evaluations --directory output/phase05/new-replay --profile both --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh
```

Use new output paths. Default starter40/full2000 interview target; master-only
remains default mode. Replays compare every PK-ordered row/count/table hash,
aggregate SHA256, deterministic scores/decisions/amounts/final states/summaries.
Timings are separate diagnostics (including evaluation, offer, final validation
and total replay execution); no binary SQLite hash proof. Same runtime/schema/
config verified; no blanket cross-engine or empirical realism claim.

No five injected anomaly datasets, separate truth, anomaly evaluation metrics,
CSV/JSON/SQL exporter, UI, network service or deployment. Isolated invalid tests
are not production anomaly artifacts. Human review of policies, implementation,
ownership and other-tool prompt completeness remains pending. Exact measured
counts/checksums/timings/tests and actual failures in current report/evidence.
STOP after Phase 05.
