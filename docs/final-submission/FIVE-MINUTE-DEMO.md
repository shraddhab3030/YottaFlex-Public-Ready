# Five-minute interviewer demonstration — preparation, not personal signoff

Use the environment and actual SQL restore from
[personal verification](../PERSONAL-VERIFICATION.md). Run the longer checks before
the conversation and keep their actual output available. This is a navigation
plan for the real implementation, not a claim the candidate has mastered it.

| Time | Show / explain | Real implementation and evidence |
| --- | --- | --- |
| 0:00–0:40 | Recruiting decisions, 11 core entities, 24 relational tables; why local Python/SQLite | README entity list; src/yottaflex/schema.sql; docs/data-dictionary.md; FK bridges, explicit transactions, no cloud/API/paid dependency. |
| 0:40–1:30 | A stored approved requisition to hired application | Personal SQL snippet; APP-CAND-000031-REQ-2026-000147, REQ-2026-000147, INT-2026-000147, OFF-2026-000003. Inspect successful_path in your newly executed audit_dataset output, not just historical screenshots. |
| 1:30–2:15 | Calendars and safe state changes | workflow.check_slot/schedule_interview, BEGIN IMMEDIATE, effective Staff/panel membership, half-open intervals, immutable typed events. Show INTERVIEWER_CONFLICT and unchanged-row rejection evidence. |
| 2:15–3:00 | Rubric score and approved compensation | evaluation.computed_card: (sum(score_value*weight_basis_points)+5)//10; fixed example scorecards 3089 milli-points. Offer amount 92979350 INR minor units; offers.approved_band and independent approval STAFF-000002. Creator/requester differs; show SELF_APPROVAL_FORBIDDEN. |
| 3:00–4:00 | Five anomalies and honest metrics | Run the detector command below, then evaluate. R01=5, R02=10, R03=5, R04=5, R05=5; clean zero; TP30/FP0/FN0; precision/recall/F1=1.0 only on controlled cases. Explain five double-booking pairs share two staff each. |
| 4:00–4:35 | Exports and reproducibility | Show real package verification: CSV/JSON/SQL, 24 tables/89575 typed rows, 99 domain checks per restore and equal canonical hash. Two fresh fixed-seed builds compare all artifact bytes/typed rows; timing is excluded. |
| 4:35–5:00 | Ownership, assistance and limits | Substantial ChatGPT planning/prompt/report help and Codex implementation/tests/audits; personal study still required. Original ChatGPT inputs missing. Explain no UI/auth service, pinned runtime, trusted SQL input and controlled-data limits. |

```sh
python3 -m yottaflex.detector --database "$PREP_WORK/work/sql.sqlite3" --observations artifacts/anomalies/input/observations.json
python3 -m yottaflex.deliverables evaluate --database "$PREP_WORK/work/sql.sqlite3" --directory artifacts/anomalies
```

The first command receives no truth input. Only evaluation reads separately
stored ground truth. A valid baseline is not weakened to simulate failures:
strictly typed external observations expose controlled semantic violations.
Know how missing/incomplete reviews block progression, withdrawals release booked
capacity, integer arithmetic avoids rounding drift, and event snapshots preserve
historical decisions. Do not equate memorizing this guide with every-line review.
