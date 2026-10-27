# YottaFlex AI — PHASE 04: INTERVIEW SCHEDULING, CALENDARS, STAGE GATES & LIFECYCLE OPERATIONS

You are continuing our existing YottaFlex AI 72-Hour Code Challenge.

**Phase 03 has been reviewed and conditionally approved for progression.**

Deadline: October 29, 2026, 1:52:35 PM IST.

Your responsibility is to implement a reliable, deterministic interview scheduling and recruitment lifecycle engine on top of the existing Phase 03 database.

This is a business-critical phase. Focus on correct scheduling, enforceable stage transitions, append-only history, transactional consistency and exactly 2,000 full-scale interviews.

Do not sacrifice correctness for extra features.

## 1. Mandatory repository inspection

Before changing code:

1. Read `AGENTS.md` and `README.md`.
2. Read the complete original problem statement and both official PDFs.
3. Read all Phase 01–03 handoff reports.
4. Review the 75-row requirements matrix.
5. Inspect `schema.sql`, `db.py`, `generate.py`, `generation_config.py`, `generation_checks.py`, `canonical.py`, and related modules.
6. Inspect the actual SQL schema, allowed status values, field-level constraints and event-history design.
7. Review the existing tests and generation commands.
8. Inspect Git status, branch and recent commits.

Preserve the completed foundation.

**Do not assume field names, enum values or relationships without checking the implemented schema.**

If a schema change is genuinely necessary, document the exact reason and add regression tests. Prefer reusing the existing 24-table design.

## 2. Scope and mandatory output

Extend the existing deterministic generator and implement actual scheduling/lifecycle business operations.

The FULL profile must contain exactly:

- 200 requisitions.
- 5,000 candidates.
- 8,000 applications.
- 2,000 interviews.

The STARTER profile should use a configurable smaller interview target, initially 40 interviews if feasible.

The same generator architecture must support both profiles.

Preserve all previously generated master IDs and causal history.

Phase 04 must implement:

- Interviewer Staff identities.
- Interview panels.
- Effective-dated panel membership.
- Interviewer availability calendars.
- Calendar conflict detection.
- Panel scheduling.
- Interview rescheduling.
- Interview cancellation.
- Candidate withdrawal and booking cancellation.
- Valid application stage transitions.
- Review-dependent stage gates.
- Append-only event history.
- Deterministic scheduling.
- Domain validation and focused tests.

Do not implement actual rubric scorecard collection or offer generation in this phase. Those belong to Phase 05.

## 3. Define explicit lifecycle rules

Create a documented transition policy consistent with the existing database enums.

For every permitted transition, define:

- Source stage.
- Target stage.
- Actor/authorization assumptions.
- Required conditions.
- Relevant dependent records.
- Recorded event type.
- Expected failure code when rejected.

At minimum, support a coherent path from application submission to interview scheduling and appropriate later review stages.

Do not invent stage values that contradict the schema.

A candidate must not advance through a review-completion gate without the required completed evaluations.

Because real scorecards are deferred to Phase 05, do not advance Phase 04 applications to stages requiring completed evaluations.

Document which transitions Phase 04 implements and which remain pending.

Reject invalid transitions atomically.

A rejected transition must not partially change the application or append a misleading successful-state event.

## 4. Interview panel generation

Generate realistic panels for approved requisitions.

Requirements:

- Every panel references a valid requisition.
- Every participating interviewer references existing Staff.
- Effective panel memberships have valid time intervals.
- Different roles may require different panel sizes.
- Preserve stable panel identity.
- No duplicate simultaneous membership for the same panel/member.
- Panel configuration remains compatible with the interview stage and requisition requirements.

Generate additional synthetic Staff only when needed.

Do not alter existing HiringManager/Staff identifiers.

Distinguish panel members from assigned interview participants.

InterviewParticipant records must represent immutable snapshots of the actual staff assigned at scheduling time.

Future panel membership changes must not rewrite an existing interview's participant history.

## 5. Generate interviewer calendars

Implement deterministic Availability generation.

Each availability record must include:

- Valid interviewer reference.
- Valid start/end time.
- Positive interval.
- UTC timestamp representation.
- Coherent calendar chronology.

Use half-open intervals:

[start, end)

Back-to-back interviews must be permitted when:

previous.end == next.start

An overlap exists when:

existing.start < proposed.end
AND proposed.start < existing.end

Apply conflict checks only to bookings whose statuses occupy calendar capacity.

Cancelled historical bookings must not remain active blockers.

Document scheduling windows, working-day assumptions, interview duration and any gap/buffer policy.

Use deterministic local business rules without third-party calendar integrations.

## 6. Implement a conflict-free scheduling engine

Create reusable domain operations rather than inserting arbitrary interview rows.

A schedule operation must verify:

1. Application exists.
2. Requisition is approved and eligible.
3. Application is in an eligible lifecycle stage.
4. Candidate is not withdrawn.
5. Requested panel belongs to the application requisition.
6. Panel is effective at the requested time.
7. Assigned interviewer memberships are valid at the interview time.
8. Every assigned interviewer has sufficient availability.
9. No assigned interviewer is double-booked.
10. The candidate has no overlapping active interview.
11. Scheduling interval is valid and positive.
12. Required actor/decision metadata is present.

Perform checks and mutations in one safe database transaction.

Use SQLite transactional locking appropriate for preventing race conditions.

Scheduling must atomically create:

- Interview projection.
- InterviewParticipant snapshots.
- InterviewEvent.
- Relevant ApplicationEvent and stage projection changes.

Preserve existing identifiers.

Do not silently bypass conflicts to hit the required dataset count.

## 7. Exactly 2,000 interviews

Generate exactly 2,000 full-scale Interview records using the scheduling business operation.

Requirements:

- Stable IDs: INT-2026-000001 onward.
- Valid application and requisition references.
- Valid panels and interviewers.
- No active interviewer double-booking.
- No active candidate double-booking.
- All active bookings covered by interviewer availability.
- Valid interview chronology.
- Meaningful variation in panel composition, duration and schedule dates.

Use deterministic candidate/application selection.

You may use stored skill requirements and derived candidate fit to select a plausible interview pool, but do not assign outcomes independently at random.

If sufficient eligible scheduling capacity does not exist, fail with an actionable diagnostic. Do not fabricate availability, bypass checks or change the required count silently.

Document the distinction between the number of Interview rows and the number of scheduling attempts.

Do not generate extra Interview rows solely to represent rescheduling if the intended schema models rescheduling as state changes and events.

## 8. Rescheduling behavior

Implement a proper reschedule operation.

It must:

- Validate the target interview.
- Check permitted current status.
- Validate the replacement time.
- Recheck all interviewer and candidate conflicts.
- Respect calendar coverage and effective panel membership.
- Exclude the interview's own old reservation when checking conflicts.
- Preserve the original interview ID.
- Preserve old scheduling information in append-only events.
- Update the current schedule projection transactionally.
- Avoid partially updating records on failure.

Include successful and failed rescheduling examples.

Changing a schedule must not silently erase the original booking history.

## 9. Candidate withdrawal

Implement a candidate/application withdrawal operation consistent with the existing schema.

Define the withdrawal scope explicitly:

- Candidate-wide withdrawal, if supported.
- Individual application withdrawal.

If the existing schema supports only one scope, document it and avoid inventing unsupported semantics.

Withdrawing an application must:

- Update its lifecycle projection legally.
- Append a withdrawal event.
- Cancel its active scheduled interviews in the same transaction.
- Append corresponding InterviewEvents.
- Preserve completed and historical records.
- Release occupied scheduling capacity.
- Prevent new interviews for withdrawn applications.

A withdrawal with an active interview must never leave a valid baseline with an active booking.

That invalid situation will be deliberately injected and labelled in a later phase.

## 10. Include realistic lifecycle variation

Include:

- Successfully scheduled interviews.
- Successful reschedules.
- Cancelled bookings.
- Candidate/application withdrawals.
- Unsuitable applications that remain at their initial stage.
- Eligible applications advanced only through legal transitions.
- Rejected attempts with appropriate business error codes.

Use documented, deterministic proportions rather than independently randomized outcomes.

The complete baseline must remain valid.

Important: a legitimately incomplete scorecard can exist later, but it must not allow advancement through a completed-review gate.

If Phase 04 has no scorecard records yet, do not create fake scorecards to satisfy progression.

## 11. Event and audit requirements

Use the existing event tables.

For every successful state-changing operation, record:

- Event identity.
- Affected entity.
- Actor.
- Previous/current state where applicable.
- Event type.
- Logical occurrence time.
- Reason or decision code.
- Correlation ID when relevant.
- Relevant before/after schedule snapshots.

Ensure:

- Per-entity event sequences are consistent.
- Historical events cannot be overwritten.
- Projection and final event agree.
- Mutations are transactional.
- Failed operations do not produce fictitious success events.

If retaining rejected decisions as auditable attempts, distinguish attempts from successful domain events without pretending an invalid transition was committed.

Do not include ground-truth labels in workflow features or events.

## 12. Validation engine for Phase 04

Implement focused checks for:

- Exact master-data and interview counts.
- Foreign-key integrity.
- Primary-key uniqueness.
- Natural-key duplicates.
- Valid panel/requisition relationships.
- Active panel memberships at interview time.
- Interviewer calendar coverage.
- Active interviewer overlaps.
- Active candidate overlaps.
- Valid interview timestamps.
- Legal stage transitions.
- Candidate withdrawal consistency.
- Cancelled interview behavior.
- Reschedule history consistency.
- Participant snapshot integrity.
- Event ordering and continuity.
- Current state versus last event reconciliation.
- Absence of unsupported advanced review states.
- No ground-truth label leakage.

Extend the existing Phase 03 validation carefully.

The Phase 03 `validate_generated` function assumes downstream tables are empty. Do not continue using that assumption as final acceptance after Phase 04.

Preserve Phase 03's ability to validate a master-only baseline separately.

## 13. Required tests

Add automated tests covering:

1. Eligible interview scheduled successfully.
2. Unapproved requisition rejected.
3. Missing application rejected.
4. Withdrawn application rejected.
5. Panel/requisition mismatch rejected.
6. Unavailable interviewer rejected.
7. Overlapping interviewer bookings rejected.
8. Back-to-back bookings accepted.
9. Same candidate overlapping bookings rejected.
10. Calendar effective-date boundaries.
11. Invalid interview duration rejected.
12. Successful rescheduling.
13. Rescheduling conflict rejected.
14. Reschedule retains original ID.
15. Old schedule preserved in history.
16. Candidate withdrawal cancels active interviews.
17. Cancelled booking releases capacity.
18. Historical completed interview preserved.
19. Illegal application transition rejected.
20. Review-dependent progression blocked without completed reviews.
21. Successful mutations append valid events.
22. Rejected operations remain atomic.
23. Interview participants remain immutable.
24. Exactly 40 STARTER interviews, if configured.
25. Exactly 2,000 FULL interviews.
26. Zero baseline active scheduling conflicts.
27. Deterministic calendar and interview generation.
28. Existing Phase 01–03 tests still pass.
29. No weakening of prior schema integrity constraints.

Use `unittest` and temporary isolated databases.

Do not fabricate PASS output.

## 14. Reproducibility

Run two independent STARTER generations with the same seed.

Run two independent FULL generations with the same seed.

Compare:

- Every canonical ordered record.
- Row counts across all tables.
- Per-table SHA-256.
- Overall canonical SHA-256.

Verify all 2,000 interviews remain deterministic.

Do not use SQLite binary hashes as the primary evidence.

Include actual results in the handoff report.

Preserve the original Phase 03 master-data generation mode for regression checks.

If the complete database hashes differ, identify whether the difference is legitimate new content or nondeterministic behavior.

## 15. Performance and resource usage

Measure:

- Full dataset generation duration.
- Scheduling duration.
- Conflict-check behavior for meaningful candidate/interviewer volumes.
- Validation duration.

The required scale is moderate.

Avoid unnecessary threading, distributed infrastructure, caching, external calendars, ORMs, or paid services.

Use indexes and simple SQL where justified.

Optimize only genuine bottlenecks.

## 16. Documentation

Create:

`docs/phase04/interview-workflow-design.md`

Include:

- Scheduling architecture.
- Transition policy matrix.
- Calendar assumptions.
- Panel membership policy.
- Scheduling conflict algorithm.
- Transaction boundaries.
- Withdrawal semantics.
- Rescheduling semantics.
- Event history.
- Determinism strategy.
- Known limitations.
- Commands to generate and validate STARTER/FULL data.

Update the README and 75-row requirements-status overlay accurately.

Do not mark scorecards, offers or anomaly detection complete.

## 17. AI transparency and Git safety

Preserve this complete prompt verbatim in the AI prompt-history journal.

Document actual AI involvement, implementation and verification.

Do not fabricate human review.

Preserve existing commits and current branch.

Make focused local commits after successful verification.

Do not push, merge, publish, contact recruiters or submit.

Keep private assignment documents, secrets and database scratch files out of tracked files.

## 18. Phase 04 acceptance criteria

Phase 04 is PASS only if:

- Existing Phase 03 counts are unchanged.
- FULL contains exactly 2,000 interviews.
- STARTER generates its configured interview count.
- Valid panels and calendars exist.
- No active interviewer double-booking exists.
- No active candidate double-booking exists.
- Availability coverage and effective memberships are valid.
- Withdrawals cancel active scheduled interviews.
- Rescheduling retains immutable history.
- Illegal stage transitions are rejected.
- Review gates cannot be bypassed.
- Every successful mutation is auditable.
- No unrelated corruption occurs.
- Actual scheduling tests pass.
- Full same-seed reproducibility passes.
- Existing tests remain green.
- No later-phase features are claimed complete.

## 19. Handoff report

Create:

`reports/phase04-interview-workflow-handoff.md`

The report must include:

1. PASS/PARTIAL/FAIL assessment.
2. Files created/modified.
3. Schema changes, if any.
4. Business rule matrix.
5. Exact STARTER/FULL row counts.
6. Interviewer and candidate conflict counts.
7. Rescheduling and withdrawal statistics.
8. Examples of accepted and rejected operations.
9. Audit/history reconciliation results.
10. Test commands and actual outcomes.
11. Same-seed reproducibility results/checksums.
12. Performance measurements.
13. Known limitations and remaining risks.
14. Updated requirement coverage.
15. AI usage and human-review status.
16. Local Git commit hashes and working-tree status.
17. Recommended Phase 05 implementation scope.

Make the handoff self-contained and suitable for independent review in another ChatGPT session.

**STOP after Phase 04. Do not implement Phase 05 without my approval.**

Remember: our objective is not just to insert 2,000 records. It is to demonstrate a legitimate recruitment scheduling workflow that enforces rules, preserves history, rejects invalid actions and remains reproducible.