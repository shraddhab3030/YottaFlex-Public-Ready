# Candidate walkthrough preparation — understanding not yet verified

This is an AI-prepared study/navigation guide, not proof the candidate understands
any line. Personal explain-back and executions remain PENDING under P012.

## Actual implementation in15 points

1. Python/SQLite: standard library, modest relational scale, explicit FK constraints
   and transactions without a hosted dependency. Exact Python3.14.5 tested;
   db.connect/initialize in src/yottaflex/db.py enforce schema/runtime boundaries.
2. 24 tables:11 core,5 support bridges/Staff/rubric items/skills,7 typed event
   tables and SchemaMetadata. See src/yottaflex/schema.sql and generated dictionary.
3. Masters/dependents: generate._populate creates Staff/managers, requisitions/
   criteria/approval history, candidates/skills, then applications. Dependent
   scheduling/evaluation/offers reference these actual keys in later operations.
4. Determinism: generate.domain_random derives isolated RNG streams by SHA256;
   generation_config defines seed20261022/logical epoch; ids.numbered_id and
   application_id create immutable six-digit/literal-composite identities.
5. Lifecycles: workflow.transition_application, schedule_interview,
   evaluation.review_application and offers operations own legal stage changes.
   An enum alone does not authorize advancement. workflow_checks.APP_EDGES and
   evaluation_checks independently check stored histories/projections.
6. Scheduling: workflow.check_slot checks all assigned Staff and candidate
   half-open interval overlaps, calendars and effective memberships. Public
   schedule/reschedule operations recheck under BEGIN IMMEDIATE, not only in planner.
7. Event history: workflow.write_transaction and _append_event persist projection
   plus old/new snapshots/actor/time/reason atomically. Schema triggers reject
   UPDATE/DELETE/REPLACE of histories/participants/metadata; rollback tests inject
   failures after writes. A hostile DB owner is outside this protection boundary.
8. Scores: evaluation.computed_card derives (sum(score*weight)+5)//10 from0–4
   items with10000 total basis points, yielding0–4000 milli-points. All applicable
   criteria need evidence; required minima/mean/spread gate progression. SQL
   validator recomputes independently. Missing review differs from negative score.
9. Compensation: offers.approved_band links immutable approved event/currency;
   proposed_amount derives an in-band integer amount from actual aggregate.
   submit_offer/decide_offer require an appointed independent HR/admin. A declared
   synthetic70%-of-band-width budget rule decides approval, not an employer policy.
10. Detection: detector.detect_records checks business facts across the entire
    projected view; observations.projected strictly validates before/after shape,
    identity/types/FKs and exact intended modifications, retaining clean history.
11. Truth isolation: detector imports no injection/truth/evaluator module and
    accepts no truth argument. Injection labels are independent; evaluator reads
    truth only after findings. Poisoned-label and import-closure tests exercise it.
12. Metrics: anomaly_evaluation.match_key matches actual rule/entity/related keys;
    TP/FP/FN yield conventional precision/recall/F1. Duplicate findings are FP,
    undefined denominators null.30/0/0 on controlled data is not real-world accuracy.
13. Exports: exports.py uses schema/PK order, CSV unique null/escape policy,
    exact JSON scalar types/opaque snapshots, FK-safe SQL with metadata once.
    canonical.py hashes logical records; replay compares bytes and actual typed
    rows. SQLite file bytes are not the reproducibility contract.
14. Trade-offs: explicit SQL/functions, pinned runtime, per-table JSON memory,
    deterministic gzip and cooperative output locks. No UI/cloud/auth service
    mandated; raw SQL import is trusted reviewed input. Some advanced withdrawal/
    correction/configuration workflows need explicit future policy.
15. AI: ChatGPT interpreted/planned/drafted prompts/reviewed reported evidence;
    Codex heavily generated implementation/tests/docs and ran technical checks.
    Candidate directed phases/read reports. Personal technical verification and
    complete original ChatGPT prompt inclusion remain PENDING. See ai-history-audit.md.

## Twelve realistic reviewer questions

| Question | Concise answer and source navigation |
| --- | --- |
| Why use a database instead of JSON lists? | FK-enforced relationships, unique joins, atomic multi-row changes and efficient calendar queries at required scale; db.py/schema.sql. |
| Why doesn't calling status=reviewed suffice? | Normal API routes to review_application; evaluate_application checks completed interviews, every assigned submitted card, source totals and thresholds. |
| Can two different panels double-book one interviewer? | They share Staff IDs through InterviewParticipant; check_slot checks staff reservations across every panel under writer lock. |
| Are adjacent bookings conflicts? | No; half-open overlap is startA<endB and startB<endA. Cancelled bookings do not occupy capacity. |
| Why retain participant snapshots? | Later membership edits must not change who was booked or who can author the historical evaluation. |
| How do you avoid money/score rounding errors? | Integer minor currency units, basis points and milli-points; explicit integer half-up score math and independent recomputation. |
| What if review is complete but offer threshold fails? | Review eligibility2500/required2/spread1000 is distinct from offer3000/required3; do not equate complete evidence with favorable hiring outcome. |
| Can the offer creator approve it? | No; appointed HR/admin must differ from creator/requester; actual rejection tests and ApprovalEvent retain evidence. |
| Why are anomalies not invalid rows in canonical exports? | Clean baseline must remain valid; typed observations represent controlled semantic failures without forging normal history or weakening normal guards. |
| What caused10 double-booking findings? | Five overlapping pairs each share two Staff: two distinct staff-specific issue keys per pair, not duplicate credit for both interview IDs. |
| What survives a SQL restore? | All24 tables/IDs/values/events/metadata with exact canonical hash; DDL first, seed once, normal initializer verifies afterward; FK/triggers remain on. |
| What prevents final release today? | Historical private paths/personal commit emails, missing original ChatGPT prompts and unconfirmed personal technical ownership; no publication/submission authority. |

The candidate should navigate the actual functions, inspect a stored chain in
phase08/dataset-audit-evidence.json and personally run human-verification-checklist.md.
Do not present memorizing these answers as independent review or code ownership.
