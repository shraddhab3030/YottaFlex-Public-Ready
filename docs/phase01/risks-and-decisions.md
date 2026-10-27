# Reconciliation, assumptions, priorities and acceptance

## Source tensions and explicit decisions

| ID | Evidence / unclear point | Decision or remaining action |
| --- | --- | --- |
| A01 | F Q1/G: 72h from send time; P/user deadline Oct 29 2026 13:52:35 IST, portal minute precision | Preserve exact supplied deadline; don't restart on archive arrival. Original invitation timestamp not independently available; human verifies before release |
| A02 | P portal Round 2 / invitation Round 3 | Unresolved administrative label; no technical scope change guessed; verify authenticated source later |
| A03 | F Q3 recruitment email channel / P once-final portal submission | Capture both. No contact/submission authorized now. Human confirms exact official channel before release |
| A04 | F Q2 editable repo until deadline / P final submission once | Final link versus editable code is a possible inference, not verified. Do not rely on later changes without confirmation |
| A05 | P prevent conflicts/enforce gates / required invalid cases | Strict normal operations; separate labelled fixture injection for independent detection/evaluation |
| A06 | P issue_type/ground_truth / never leak labels into input features | Labels live only in separately keyed truth artifact; no truth input to workflow/validator |
| A07 | P heading Suggested Volume but Granular.4/user full exact counts | Mandatory full 200/5,000/8,000/2,000, not optional starter-only scope |
| A08 | P CSV/JSON/SQL and truth.csv/json slash notation | Inclusive plan: all three table formats, both truth formats; avoids omitting SQL/full exports |
| A09 | F no hosted demo/full suite / P validation and replay / user smoke | Hosting/full generic suite optional; specified checks and reproducibility mandatory |
| A10 | P generic totals/balances/scores/statuses/dates | Derive applicable recruiting values; document irrelevant balance category, don't invent accounting domain |
| A11 | P valid joins / deliberate negative scenarios | Keep FKs/types valid; inject semantic violations, never unrelated corruption |
| A12 | P unspecified exact stages/rubric/bands/distributions/support counts | Document versioned configurable synthetic choices; no invented real policy, SLA or prevalence |
| A13 | F AI tools allowed including cloud / user local-only | Application/data/execution local, no network services/paid inference; explicitly authorized Codex assistance recorded |
| A14 | P candidate transcription with private application link | Accept as specification per user; no authenticated portal claim and no publication of raw identifier |
| A15 | F complete prompt history / no raw export in this workflow | Preserve all available human prompts in this chat; no other AI tool used; disclose export/other-tool audit limits; no private system/developer text or reasoning exported |

## Risks and priorities

| Risk | Priority / impact | Mitigation / gate |
| --- | --- | --- |
| Deadline/send timestamp or channel/finality ambiguity | P0 delivery | Exact supplied deadline; verify invitation/channel before release; don't contact/submit now |
| Full eleven-entity/event/export workload | P0 delivery | Critical path schema/dictionary -> valid baseline -> workflow guards -> negatives -> validation/exports/replay; skip optional UI |
| Ground-truth leakage | P0 correctness | Separate paths and API signatures; evaluator only after findings; test no labels in feature exports |
| Weakening scheduler/gates for anomaly fixtures | P0 correctness | Dedicated injection only; transaction/rollback tests for ordinary operations |
| Clocks/order/runtime make repeat generation diverge | P0 correctness | Pin interpreter/config/logical time; seeded RNG; canonical serialization; two full runs and hashes |
| Derived scores/projections/history inconsistent | P0 integrity | Shared domain rules + independent reconciliation; typed events and enforced FK joins |
| Private source/prompt/candidate/credential publication | P0 privacy | Source docs ignored, synthetic-only samples; tracked-file checks and human staged review; never copy private portal URL |
| All-tools prompt record incomplete or human understanding unverified | P0 submission | Current-chat prompts recorded; human audits other tools and explains each line/design/rule before release |
| CPython 3.14.5/SQLite differs on reviewer system | P1 setup/replay | Document exact runtime, no third-party deps; record SQLite version, compare text exports rather than .db bytes |
| Synthetic realism/evaluation targets unspecified | P1 review | Declare distributions/limits; measured counts/metrics only, no fake numerical accuracy/performance claims |
| PDF font tooling issue | Resolved for source analysis | Poppler attempt stopped after font/cache errors; bundled pypdfium2 rendered both pages and both were visually checked |

## Finished-challenge acceptance plan (not test results)

1. Eleven core entities plus necessary bridges/events with full per-field
   dictionary; PK/FK/enum/date/duplicate constraints pass in all exports.
2. Exact full counts, shared starter/full generator, baseline validated before
   mutation, scenario fixture preserves counts/structural integrity.
3. Valid workflow commands succeed; bad schedule/stage/score/offer/withdrawal
   actions reject atomically; audit events preserve actor/reason/old/new values.
4. Each N01-N05 appears at least once and is labelled separately; independent
   findings expose planted anomalies. Report misses/additional findings and metrics.
5. Applicable derived values reconcile; CSV/JSON/SQL import equivalently; README,
   schema/dictionary/commands/seed/source manifests/validation summaries complete.
6. Two full runs, same seed/config/runtime, equal canonical counts/hashes; actual
   performance/reproducibility evidence recorded, no fabricated success.
7. Complete available prompt history/AI-human disclosure, license/provenance and
   privacy review, clear setup and limitations; no secrets/real candidate records.
8. Only after user authorization: public dedicated repo, private-browser access
   check, required artifacts in one repo, confirmed channel and one final link
   submission before deadline; repo remains available through deadline.

## Recommended Phase 02 scope (not permission to start)

After human Phase 01 review: implement complete field dictionary/schema, then
deterministic configuration/ID helpers and clean starter generation in dependency
order. Expand same generator to full volumes; implement transactional workflow
guards/events, isolated negatives, validation/truth/evaluation, full exports and
two-run replay. Keep meaningful local commits and prompt/review logs. Publish and
submit only at a separate final user-controlled gate.
