# Eleven-entity conceptual model

Core names are from P Entities/Granular.1. Proposed fields, states, policies and
supporting tables are design choices for review, not additional assignment facts.
This is a conceptual dictionary. The full field-level type/nullability/allowed
values/units/uniqueness/validation dictionary and executable schema are Phase 02.

Every entity has immutable text PK. Timestamps are UTC ISO 8601. Effective dates
use [valid_from,valid_to) with optional open end. Recorded-at and effective-at
are distinct when needed; state changes retain explicit historical events.

## All eleven mandatory entities

| Entity | PK / essential proposed fields and FKs | Lifecycle and effective dates |
| --- | --- | --- |
| Requisition | requisition_id REQ-2026-000001; hiring_manager_id; role/title; approved band_min_minor, band_max_minor, currency, criteria/policy version | draft -> pending_approval -> approved/open -> filled/closed/cancelled; approval/open/close dates and effective band/criteria |
| HiringManager | hiring_manager_id HM-000001; staff_id unique FK; synthetic department/team | active/inactive; valid_from/to; ownership history retained |
| Candidate | candidate_id CAND-000001; synthetic name/contact at example.invalid; structured skills/profile | active/withdrawn; created_at, optional withdrawn_at; global vs per-application withdrawal distinguished |
| Application | application_id literal APP-<candidate-id>-<req-id>; candidate_id, requisition_id FKs; unique candidate/requisition pair; current stage projection | applied -> screening -> interviewing -> reviewed -> offer -> hired; rejected/withdrawn terminals; applied_at + events |
| SkillRequirement | skill_requirement_id SKILL-000001; requisition_id FK; criterion/skill, required flag, weight/rubric version | active/retired; valid_from/to; preserve criteria version used in old reviews |
| InterviewPanel | panel_id PANEL-000001; requisition_id FK; purpose/stage | active/inactive; effective dates, effective bridge members |
| Availability | availability_id AVAIL-000001; staff_id FK; start_at/end_at and display timezone | available/blocked/cancelled; ordered interval and effective validity |
| Interview | interview_id INT-2026-000001; application_id, panel_id FKs; current scheduled_start/end | scheduled -> completed/cancelled/no_show; reschedule records old/new intervals in events, never changes ID |
| Scorecard | scorecard_id literal SCORE-<interview-id>-<reviewer-id>; interview_id, reviewer_staff_id FKs; rubric/version, derived total, completion | draft/incomplete/submitted; submitted_at, historical revisions |
| Offer | offer_id OFF-2026-000001; application_id FK; amount_minor/currency, approved_requisition_event_id FK identifying approved band version | draft -> pending_approval -> approved -> sent -> accepted/declined/expired; rejected/withdrawn; effective dates/events |
| Approval | approval_id APR-000001; requisition_id OR offer_id FK (exactly one); approver_staff_id FK, decision/reason | pending -> approved/rejected; requested_at/decided_at, effective dates and supersession history |

HiringManager/Staff and supporting prefixes are local choices; the six supplied
patterns are mandatory. Score scale 0-4, rounding/weights, exact stages/review
counts and band/distribution choices must be configurable/versioned assumptions.
P does not specify real-company policies. Currency and integer minor units avoid
floating band errors. Historical criteria/bands cannot be overwritten in a way
that changes the meaning of existing scorecards/offers.

## Supporting tables (not extra claimed core entities)

| Table | Keys / why needed |
| --- | --- |
| Staff | staff_id STAFF-000001; synthetic actor role(s): manager, HR, IT/operations, administrator, interviewer. Resolves reviewer IDs, calendars, approvals and ownership with FKs |
| PanelMember | (panel_id,staff_id,valid_from) PK/FKs, valid_to; effective panel/staff N:M |
| InterviewParticipant | (interview_id,staff_id) PK/FKs; booked membership snapshot survives later panel changes |
| ScorecardItem | (scorecard_id,skill_requirement_id) PK/FKs; structured score/weight/evidence and applicability |
| CandidateSkill | (candidate_id,skill_key) key; structured synthetic skill levels; skill_key may be documented enum |
| ApplicationEvent, InterviewEvent, RequisitionEvent, OfferEvent, ScorecardEvent, CandidateEvent, ApprovalEvent | event_id PK, explicit owner FK, sequence, old/new state or value, effective_at, recorded_at, actor FK/reason. Other mutable masters retain effective versions or typed events as needed; explicit tables preserve enforceable FKs |

System events explicitly use actor_kind=system. Human-actor events require the
appropriate staff or candidate FK, with XOR actor rules; no fictitious person
is attributed to an AI verification result. Approval decisions retain previous
decisions via events/versions. Public samples contain synthetic identities only.

## Cardinalities, optionality and relationship rules

| Relationship | Cardinality / condition |
| --- | --- |
| Staff -> HiringManager | 1:0..1; manager requires exactly one Staff |
| HiringManager -> Requisition | 1:0..N; requisition requires exactly one manager |
| Requisition -> SkillRequirement | 1:1..N before approval/open; draft can have zero |
| Candidate -> Application <- Requisition | each parent 1:0..N; application is N:M bridge with unique candidate/requisition pair |
| Requisition -> InterviewPanel | 1:0..N; panel has one requisition |
| InterviewPanel <-> Staff | N:M through effective PanelMember; active panel needs >=1 member |
| Staff -> Availability | 1:0..N; each interval has one staff owner |
| Application -> Interview <- InterviewPanel | each parent 1:0..N; interview requires both, same requisition |
| Interview <-> Staff | N:M through participant snapshot; all current participants checked for conflicts |
| Interview -> Scorecard <- Staff | each parent 1:0..N; unique interview/reviewer pair; reviewer participates |
| Scorecard <-> SkillRequirement | N:M through ScorecardItem; criteria apply to correct requisition/rubric |
| Application -> Offer | 1:0..N, revisions retained; at most one active final offer |
| Requisition OR Offer -> Approval | 1:0..N each; target XOR; no dangling approvals; workflow requires appropriate decision |
| Staff -> Approval | 1:0..N; each decision has one approver with allowed synthetic role |
| Entity -> own typed events | 1:0..N; every persisted lifecycle change appends sequenced evidence |

Candidate/employee self-service, manager requisition ownership, HR scoring/offer
coordination, IT/operations execution support and administrator configuration are
actor responsibilities. No passwords, login service, external HR integration or
role-based web authorization is required by the supplied actor list.

## History and isolated truth

Projection and event append occur transactionally. Rescheduling retains old
slots; withdrawal retains interview cancellations; changed bands/criteria retain
effective versions. Validator checks projection/events for agreement.

Proposed truth fields: truth_id, scenario_type/issue_type, rule_id, primary entity
type/id, related_ids, expected_decision and injection description. Truth is a
separate CSV and JSON, not entity/feature columns. Ordinary validator accepts no
truth; evaluator reads it only after findings exist. This reconciles required
labels and no leakage. Fixtures preserve structural integrity and isolate semantic
failures (e.g. criterion FK exists but belongs to a different requisition).
