# Phase 04 interview workflow design

Scope: valid deterministic scheduling baseline and reusable local operations.
Original specification and both official PDFs were re-read; Phase 04 user prompt
is the scope authorization, not permission inferred from submission documents.
No original requirement is removed. Human Phase 04 review is pending.

## Architecture and storage

Retain Python 3.14.5 stdlib, SQLite, all 24 v2 tables, 209 fields, existing indexes,
45 FK groups, 42 protection triggers and initializer. No migration or new runtime
dependency. `generate_database(..., phase="master")` remains the default Phase 03
path. `phase="interviews"` first constructs/validates that same master baseline,
captures its canonical hash and immutable-source fingerprint, then adds workflow
data using `interview_generation` and the public `workflow` operations.

`workflow_checks` independently checks overlapping reservations and audit chains,
and shares the slot-policy checker for calendar/member acceptance. This avoids
drifting scheduling rules; corruption tests independently exercise validation.
`canonical` is unchanged: declared-PK row ordering, stable JSON, per-table and
aggregate SHA256. Timings are outside deterministic content. Existing schema SQL,
dictionary and structural tests remain untouched.

An owned scratch database is published with atomic no-overwrite hard-link only
after final validation and master preservation pass. Partial commits inside this
private scratch file never publish on failure. Every existing target is refused.
No general repository/service abstraction, ORM, web/API, distributed service,
cache, calendar integration, or production threading is needed at this scale.

## Actor and decision policy

Every operation requires existing effective active Staff, integer logical UTC
decision time and nonblank reason. HR/admin may operate across requisitions;
owning manager may operate on their requisition. An assigned reviewer may mark
their own interview complete after its end. Global withdrawal requires HR/admin.
Candidate-origin withdrawals are recorded by an authorized Staff actor with the
candidate's optional actor FK. This is a local actor policy, not authentication
or evidence of a real candidate request. No real candidate information is used.

Missing identity: `APPLICATION_NOT_FOUND`, `CANDIDATE_NOT_FOUND`,
`INTERVIEW_NOT_FOUND`, `PANEL_NOT_FOUND`, `ACTOR_NOT_FOUND` as applicable.
Metadata/clock/role failures: `METADATA_REQUIRED`, `INVALID_TIMESTAMP`,
`ACTOR_UNAUTHORIZED`, `EVENT_TIME_INVALID`, `HISTORY_MISMATCH`.
Nested caller transactions are rejected as `TRANSACTION_ACTIVE`; use the public
operation's transaction. Foreign-key-disabled connections are refused.

## Transition policy matrix

| Source → target | Operation / authorized actor | Conditions and dependencies | Successful events | Rejection |
| --- | --- | --- | --- | --- |
| applied → screening | transition_application / HR/admin/owner | active candidate; approved/open effective requisition with actual approved Approval and approved RequisitionEvent | Application status_changed | REQUISITION_NOT_APPROVED, REQUISITION_INEFFECTIVE, CANDIDATE_WITHDRAWN |
| applied or screening → rejected | transition_application / same | same eligibility; terminal within this phase | Application status_changed | INVALID_TRANSITION for other source |
| screening → interviewing | schedule_interview / same | all slot conditions below; application, candidate, requisition, panel/member/calendar joins valid | Interview created + Application status_changed; immutable participants | APPLICATION_STAGE_INELIGIBLE, INTERVIEW_REQUIRED for direct stage bypass |
| interviewing → interviewing | schedule/reschedule/cancel/complete / same; assigned reviewer for completion | eligible operation; schedule creates additional meeting only when requested | Interview created/rescheduled/cancelled/status_changed + Application revised | INTERVIEW_STATE_INVALID, INTERVIEW_STARTED, NO_SCHEDULE_CHANGE, INTERVIEW_NOT_ENDED |
| applied/screening/interviewing → withdrawn | withdraw_application / HR/admin/owner | legal history; cancel all scheduled interviews atomically | Interview cancelled events + Application withdrawn | INVALID_TRANSITION for terminal/advanced source |
| Candidate active → withdrawn | withdraw_candidate / HR/admin | withdraw all nonterminal applications; reviewed/offer require future policy; hired/rejected preserved | child cancellations/withdrawals + Candidate withdrawn | CANDIDATE_WITHDRAWN, PHASE05_REQUIRED |
| interviewing → reviewed | deferred guard only | every noncancelled interview completed; all assigned reviewers submitted nonnull totals and required criterion items scored | NONE in Phase 04 | REVIEW_GATE_INCOMPLETE when missing/incomplete; PHASE05_REQUIRED even if ready |
| reviewed → offer → hired | deferred | future complete evaluation, band, approval/offer policy | NONE | PHASE05_REQUIRED |
| any other edge | rejected | no silently invented state or bypass | NONE | INVALID_TRANSITION |

Completed interviews retain interviewing applications awaiting evaluations.
Cancellation alone retains interviewing state; rebooking is permitted.
Cancellation can explicitly resolve any still-scheduled booking, including a
past unrecorded session. Completion requires decision time >= scheduled end.
Reschedule requires decision time <= old start and new start >= decision time.
No-show is a schema state occupying capacity; no no-show mutation is implemented.

## Panels, effective membership and snapshots

One stable `PANEL-000001` onward per approved requisition, purpose
`technical:<role-category>`. Backend/data minimum two reviewers; integration/AI
minimum three; maximum four. Generated panels use that minimum and rotate through
a seed-shuffled shared pool, exposing meaningful cross-panel staff conflicts.
Membership interval is `[origin+150d, origin+190d)`. Existing Staff/manager IDs are
unchanged. New synthetic interviewer identities follow existing Staff counters.

Active duplicate overlapping intervals for the same panel/staff are rejected
even when an overlap is outside the proposed interview. Adjacent membership
intervals may jointly cover the complete interview. Staff must be active and
have interviewer/manager role and effective dates covering the complete slot.
Purpose, requisition and panel interval must also match. Main failures are
`PANEL_REQUISITION_MISMATCH`, `PANEL_CONFIGURATION_INVALID`, `PANEL_INEFFECTIVE`,
`PANEL_MEMBERSHIP_OVERLAP`, `MEMBERSHIP_INEFFECTIVE`, `INTERVIEWER_INELIGIBLE`.

`PanelMember` is current effective configuration. `InterviewParticipant` is an
immutable scheduling-time snapshot, with reviewer assignment and assigned_at.
Rescheduling retains those exact participants and rechecks their replacement
slot membership; it does not replace them with newer panel members. Membership
edits do not rewrite historical assignments. If a future change invalidates an
active booking, validation reports it; changing configuration is not an
implemented lifecycle operation. Cancel/recreate is available where needed.

## Calendar and conflict policy

- UTC integer seconds everywhere; fixed origin 2026-01-01T00:00:00Z, independent
  of wall-clock execution date. No DST/timezone dependency.
- Default calendar: 20 Monday–Friday days starting on/after origin+160d
  (2026-06-10 through 2026-07-07). Weekends excluded; no holiday data assumed.
- Nominal 09:00–17:00 UTC; alternating staff start 09:00/09:30 and every third
  staff end 16:30. Explicit 12:00–12:45 blocked intervals override availability.
  Calendar rows are generated once before any scheduling attempt.
- Staff count is declared upfront as max(8,min(80,ceil(requisitions/3))): starter
  8, full 67. Effective staff interval is origin+150d..190d. Test configuration
  can reduce pool/day/hours to exercise honest insufficiency failure.
- Durations Junior 30 / Mid 45 / Senior 60 minutes. Domain operations accept only
  those positive whole-second intervals (`INVALID_INTERVAL`). Planner scans a
  15-minute grid; public operations need not start on that grid. Zero buffer.
- Availability is the union of available rows; cancelled rows do not cover time.
  Any overlapping blocked row rejects the slot (`INTERVIEWER_UNAVAILABLE`).
- Every interval is half-open `[start,end)`. Overlap iff existing.start < new.end
  and new.start < existing.end. End == next.start is permitted, including the
  exact calendar/panel/member effective end for a slot ending there.
- `scheduled`, `completed`, `no_show` occupy capacity; `cancelled` never blocks.
  Completed meetings retain historical occupancy. Check every participant
  across panels, and candidate across all applications. Failures are
  `INTERVIEWER_CONFLICT` / `CANDIDATE_CONFLICT`. Reschedule excludes its own ID.

For each booking, check application existence/stage, active candidate,
requisition approval/history and effectivity, panel relation/purpose/effectivity,
member roles/effectivity, calendars, staff overlaps and candidate overlaps.
Booking cannot precede its decision (`INTERVIEW_IN_PAST`). No silent force path.

## Transaction and audit boundaries

Each public mutation owns `BEGIN IMMEDIATE` from validation through write/commit.
SQLite's single-writer lock prevents two check-then-insert writers from both
reserving capacity. Connections use FK and recursive triggers ON. Default
SQLite busy timeout applies: a long-held writer may raise sqlite3.OperationalError;
no unbounded retry is hidden. The generator is single-threaded. A focused isolated
two-writer race test verifies exactly one booking succeeds and one conflicts.

Schedule commits Interview, participants, InterviewEvent and Application
projection/event together. Reschedule changes the same ID, preserving original
and subsequent start/end in event before/after snapshots. Cancel/complete append
Interview and Application events. App withdrawal cancels all its scheduled
bookings and appends withdrawal in one transaction; candidate-wide withdrawal
does this for every nonterminal app plus Candidate event. Completed/cancelled
history remains, and released capacity is available to other bookings.

Events allocate monotonically zero-padded IDs under the writer lock, with
per-subject contiguous sequence, previous/new state, actor, reason, logical
occurred_at/recorded_at and correlation ID. Interview snapshots include the
sorted participant IDs and old/new slot. Both timestamps equal logical decision
time for generated operations, not execution wall time. No label/truth keys.
Triggers reject event and participant UPDATE/DELETE/REPLACE.

Rollback covers every projection/child/event on error. Rejected demonstration
attempts appear in deterministic diagnostic summaries, never fake successful
domain events; rejected operations create no attempt table. Runtime errors after
partial writes and child-withdrawal failures are explicitly tested for rollback.

## Deterministic selection and variations

Within each requisition rank actual stored weighted skill fit, then candidate
ID/application ID; round-robin requisitions/rank until target reached. Original
master creation records/IDs are never rewritten. Many weak applications remain
applied; no independent random hiring outcomes are assigned. One interview row
per selected application in the baseline; explicit additional-booking operations
are supported but do not inflate this target. FULL target fixed 2000; starter
positive configurable target, default 40, subject to finite capacity.

Control decisions start origin+151d with monotonic seconds; meetings occur later.
Successful booking cohort positions modulo 20 choose: 0 reschedule, 1 individual
withdrawal, 2 candidate-wide withdrawal, 3 direct cancellation, 4 complete if still
scheduled. Thus nominal 5% each; candidate reuse/global propagation changes actual
counts and deduplicates repeated candidate withdrawal. Reschedules and direct
cancellations happen before all withdrawals; completions happen last at end+60s.
No random scorecards/offers. Actual variations, skipped cascades and final states
are measured from DB rather than assumed to equal nominal proportions.

The planner uses deterministic preferred day/grid order and finite scans.
Probes are read-only; the successful public operation rechecks under lock. If no
slot is found it raises `INSUFFICIENT_CAPACITY` with target, placed count, pool,
window and probes. This means the deterministic planner cannot place the request,
not a mathematical proof that no alternative global arrangement exists. It does
not enlarge calendars, relax conflicts or publish a partial database.

Initial full experiment with 40 interviewers failed at 1,470; it was not published.
The default was deliberately revised to 67 before subsequent generation. The
runtime algorithm itself never adjusts its declared capacity. This limitation
and failed experiment are retained in the handoff, not reported as a pass.

## Acceptance, reproducibility and known limits

`validate_generated(...,phase="master")` retains the original empty-downstream
acceptance. Workflow final validation uses phase-aware master counts/creation
histories, deferred scoring/offer emptiness, FK/integrity/PK/null/natural keys,
time/ID/enum checks, role/panel/calendar policy, independent staff/candidate
overlap queries, current withdrawal/state checks, legal event chains and
projection/time/slot/participant reconciliation. Original immutable master
fingerprint covers requisitions, criteria, skills, approvals, manager/original
Staff, candidate/application identity fields and their creation events.
Master-only canonical digest is retained and checked against Phase03 evidence.

The validator enforces this Phase04 valid baseline, not future labelled anomaly
acceptance or exported data equivalence. Historical slots are reconciled to their
immutable event/participant history; current calendar/member coverage checks apply
to scheduled bookings so later configuration changes do not rewrite history.
For generated static calendars, all bookings were checked at creation/reschedule.
Readiness checks are conservative guards; full scoring/total/version/evidence
reconciliation and offer eligibility remain Phase05 work. No caller can advance
reviewed/offer/hired through a Phase04 operation, even if fixture scorecards exist.

Use new paths for each command:

```sh
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase interviews --profile starter --database output/phase04/new-starter.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --phase interviews --profile full --database output/phase04/new-full.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.workflow_checks --database output/phase04/new-starter.sqlite3 --profile starter
PYTHONPATH=src .venv/bin/python3 -m yottaflex.workflow_checks --database output/phase04/new-full.sqlite3 --profile full
PYTHONPATH=src .venv/bin/python3 scripts/verify_generation_reproducibility.py --phase interviews --directory output/phase04/new-replay --profile both --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh
```

Replay independently generates twice per profile and compares every PK-ordered
row across all 24 tables, row counts, summaries, per-table and aggregate SHA256.
Binary SQLite hashes are not used as evidence. Actual measured results and
durations live in reproducibility-evidence.json and the task report. Diagnostics
are not complete CSV/JSON/SQL dataset exporters. Schema constraints remain
unchanged. All data local/synthetic; public release and actual human ownership
review remain pending. STOP before Phase05.
