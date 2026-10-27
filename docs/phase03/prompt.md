# YottaFlex AI — PHASE 03: DETERMINISTIC SYNTHETIC DATA GENERATION

You are continuing the YottaFlex AI 72-Hour Code Challenge for the Associate AI Forward Deployed Engineer position.

**Phase 02 is approved for progression based on its submitted handoff report.**

The hard deadline is October 29, 2026, at 1:52:35 PM IST.

We must build a correct, deterministic, reproducible and explainable synthetic recruitment dataset using the existing SQLite schema.

Prioritize correctness and assignment compliance over unnecessary features.

## 1. Mandatory initial inspection

Before implementing anything:

1. Read `AGENTS.md` and `README.md`.
2. Read the complete assignment and both supporting PDFs from `docs/assignment/`.
3. Read the Phase 01 and Phase 02 reports.
4. Review `docs/phase01/requirements.md`, `docs/phase01/model.md`, `docs/phase01/architecture.md`, and `docs/data-dictionary.md`.
5. Inspect `src/yottaflex/schema.sql` and `src/yottaflex/db.py`.
6. Read the existing schema tests and fixtures.
7. Inspect the current Git branch, commits and working tree.

Preserve all valid previous work.

Do not alter the relational schema just to simplify generation. If genuine schema incompatibilities are found, identify and explain them and apply only the minimum necessary corrections with regression tests.

## 2. Primary objective

Implement a deterministic synthetic data generator for recruitment master data, role requirements and valid candidate applications.

This phase must generate:

- Hiring managers and other necessary synthetic Staff records.
- Approved requisitions with valid approval history.
- Requisition-specific skill requirements.
- Synthetic candidate profiles.
- Candidate skills.
- Valid applications.
- Required creation/approval/application history records.
- Deterministic IDs and timestamps.
- Coherent candidate-to-role relationships.
- Repeatable starter and full-scale generation.

The full profile must produce exactly:

- 200 Requisition records.
- 5,000 Candidate records.
- 8,000 Application records.

Reserve the remaining challenge target of 2,000 interviews for the scheduling phase.

Do not claim the overall dataset is complete until interviews, scorecards, offers, approvals and all required negative scenarios have been generated and validated.

## 3. Deterministic configuration

Use the default fixed seed:

`20261022`

Support at least two named profiles:

STARTER:
- 10 requisitions.
- 100 candidates.
- 160 applications.

FULL:
- 200 requisitions.
- 5,000 candidates.
- 8,000 applications.

Both profiles must use the same generator implementation with scale controlled through configuration.

Use a deterministic logical time origin, not wall-clock timestamps.

Ensure every synthetic date and historical event is consistent with the declared logical timeline.

Avoid direct dependence on:

- Current time.
- Random UUIDs.
- Unseeded randomness.
- Filesystem iteration order.
- Python hash randomization.
- Database implicit row ordering.
- Machine-specific absolute paths.

Use independent, explicitly seeded random streams for major generation domains where helpful.

A repeat run with identical configuration must produce identical canonical records, not merely identical row counts.

## 4. Exact ID conventions

Implement deterministic allocation for:

- `REQ-2026-000001`
- `CAND-000001`
- `APP-<candidate-id>-<req-id>`

Preserve the database's existing required identifier rules.

Document deterministic formats for supporting tables, events and staff.

Ensure:

- All IDs are unique.
- IDs remain immutable.
- Child references resolve exactly.
- Counters are zero-padded.
- There are no duplicates.
- The same seed/configuration produces the same ordered IDs.

Future interview, scorecard and offer identifiers must remain compatible with the original assignment formats.

Do not allocate future entity IDs unnecessarily in this phase.

## 5. Generate dependency-ordered master data

Follow the actual foreign-key dependency graph.

Generate data in a valid order, such as:

1. Synthetic Staff identities.
2. HiringManager profiles.
3. Requisitions in a valid initial lifecycle state.
4. Required requisition approvals and corresponding approval/transition events.
5. SkillRequirement records.
6. Candidate records.
7. CandidateSkill records.
8. Application records.
9. Required creation/submission history.

Adjust this order only when the actual schema requires it, and document why.

Every generated record must satisfy the current schema's structural constraints.

Approved requisitions must have evidence of valid approval decisions. Do not set approved status independently from its causal events.

Do not create events with unsupported status transitions.

## 6. Realistic and meaningful synthetic distributions

Generate varied, coherent synthetic recruitment data.

Requisitions should vary by:
- Role/title.
- Seniority.
- Hiring manager.
- Required skills.
- Required skill proficiency.
- Skill importance/weight.
- Compensation band.
- Currency, where sensible.
- Opening date and lifecycle attributes.

Candidates should vary by:
- Experience.
- Skill combinations.
- Proficiency levels.
- Relevant background attributes supported by the schema.
- Availability or other permitted synthetic attributes where applicable.

Applications should vary by:
- Requisition.
- Candidate suitability.
- Creation/submission date.
- Candidate-to-role skill match.
- Supported valid lifecycle states, where history can be represented correctly.

Do not generate every candidate as equally qualified.

Introduce plausible correlations:

- More senior roles generally require higher proficiency.
- Highly experienced candidates may have deeper skills.
- Some applicants should be excellent matches.
- Some should be borderline matches.
- Others should be weak matches.

These are synthetic modeling assumptions, not claims about real candidate populations.

Use only fully synthetic data.

Do not use actual candidate identities, scraped profiles, external personal information or unlicensed datasets.

## 7. Skills and role matching

Define a small, documented synthetic skill catalogue suitable for the assignment.

For example, roles may require combinations of:
- Python.
- SQL.
- Backend development.
- Cloud fundamentals.
- API integration.
- Data analysis.
- AI/ML fundamentals.
- Problem solving.

Do not assume every role requires every skill.

Generate candidate proficiency independently of application outcomes, but with documented correlations appropriate to the candidate's synthetic profile.

If computing candidate-role fit:

- Derive it from actual CandidateSkill and SkillRequirement records.
- Define the scoring formula transparently.
- Use deterministic arithmetic.
- Respect weights and required criteria.
- Do not create independently randomized fit scores.
- Do not silently label candidates hired or rejected using random choices.

If the schema has no column for a derived fit score, compute it as a report or query rather than adding a redundant field.

Do not introduce ground-truth anomaly labels in the input schema.

## 8. Valid applications and lifecycle history

Generate exactly 8,000 unique candidate/requisition applications in FULL mode.

Requirements:

- Every application references an existing candidate.
- Every application references an existing approved requisition.
- No duplicate candidate/requisition pair.
- Application IDs follow the exact required composite format.
- Application creation/submission dates are chronologically valid.
- Stage values are valid according to the existing schema.
- Meaningful state changes have corresponding event records.
- Current-state projections must be consistent with their recorded events.

At this phase, prefer valid initial/submitted application states.

Do not generate advanced interview/review/offer stages before the corresponding workflow events and dependent records exist.

If a transition requires a scorecard, interview or approval that has not yet been generated, defer that transition to a later phase.

## 9. Historical integrity

The existing schema contains append-only event tables.

Generate required event history with:

- Deterministic event IDs.
- Correct referenced entity IDs.
- Valid actor identities.
- Explicit event types.
- Ordered per-entity sequence numbers.
- Coherent previous and new statuses.
- Deterministic occurrence timestamps.
- Documented reasons/decision codes.
- Valid structured snapshots when needed.

Do not overwrite event records.

Ensure projections agree with their actual history.

Do not insert fabricated approval history merely to satisfy foreign keys. Approval decisions must follow the documented synthetic approval policy.

## 10. Database generation and safety

Use the existing database initialization and connection utilities.

Implement a clear local command-line interface.

Expected behavior:

- Generate STARTER data into a new local SQLite database.
- Generate FULL data into a separate new database.
- Accept an explicit seed.
- Accept an explicit output database path.
- Show resulting counts and basic diagnostics.
- Refuse unsafe overwrites of an existing populated database unless an explicit safe replacement mechanism has been documented and authorized.
- Never modify unrelated database files.

Generation must run inside appropriate transactions.

On failure, avoid leaving a partially populated database that appears successful.

Keep generated SQLite databases in ignored scratch/output paths, not inside tracked source files.

## 11. Generation metrics

Produce a deterministic generation summary including:

- Seed.
- Profile.
- Logical time origin.
- Schema version.
- Counts for all populated tables.
- Number of approved requisitions.
- Number of skill requirements.
- Number of candidate skills.
- Number of applications.
- Application count per requisition distribution.
- Experience/proficiency distributions.
- Role categories and compensation distributions.
- Validity and integrity-check results.

Identify any metrics that cannot yet be computed until interviews or offers exist.

Do not invent missing downstream metrics.

## 12. Focused validation

Implement and execute tests verifying:

1. Starter counts are exact.
2. Full counts are exact.
3. Every generated primary key is unique.
4. All foreign keys resolve.
5. No duplicate candidate/requisition application pairs.
6. Correct deterministic ID formats.
7. Zero invalid required fields.
8. Correct lifecycle enums.
9. Chronological consistency.
10. Valid requisition approval events.
11. Valid application event history.
12. No unexplained projection/history mismatch.
13. Proper skill requirement ranges.
14. Proper candidate skill ranges.
15. Valid compensation ranges.
16. Valid weighted requirement configuration.
17. No unsupported advanced application stages.
18. Database generation failure does not leave misleading partial results.
19. Starter and full use the same generation code path.
20. Different seeds change relevant synthetic attributes.
21. Identical seeds produce identical canonical records.
22. Previous Phase 01 and Phase 02 tests still pass.

Add tests for realistic boundary conditions.

Use the existing Python standard-library testing framework.

No fake tests or hardcoded PASS outputs.

## 13. Reproducibility

Run two independent STARTER generations with the same seed.

Compare:

- Table counts.
- Canonical ordered records.
- Stable checksums.

Also run two independent FULL generations with the same seed.

Compare the same outputs.

Do not compare SQLite binary-file hashes as the primary reproducibility proof.

Canonicalize records in deterministic primary-key order and use stable serialization before SHA-256 hashing.

Record actual checksums and results.

If reproducibility fails, identify the exact source of nondeterminism and correct it before claiming success.

## 14. Performance and simplicity

The data volume is moderate.

Prioritize:

- Clear Python modules.
- Simple direct SQLite operations.
- Bounded memory usage.
- Efficient batched inserts when appropriate.
- Deterministic transaction order.
- Understandable functions and small units of logic.

Measure the actual generation duration.

Do not introduce multiprocessing, distributed systems, paid infrastructure, message queues, hosted AI calls, ORMs or unnecessary dependencies.

Do not optimize prematurely.

## 15. Strict exclusions

Do NOT implement in Phase 03:

- Interview scheduling or conflict detection.
- Interview rescheduling.
- Scorecard generation or reviewer evaluations.
- Offer creation or final offer approvals.
- Required anomaly injection.
- Ground-truth labels.
- Ground-truth evaluator.
- Complete CSV/JSON/SQL exporters.
- Web frontend, REST API or hosted demo.

These are separate remaining phases.

However, ensure your generated records can support them without requiring a wholesale regeneration or breaking existing identifiers.

## 16. Documentation and requirement updates

Update the relevant README and requirement-status tracking.

Create a data-generation design document explaining:

- Generator configuration.
- Source/seed policy.
- Logical time.
- Deterministic ID allocation.
- Parent-child dependency order.
- Synthetic attribute distributions.
- Correlation assumptions.
- Lifecycle/event creation rules.
- Reproducibility methodology.
- Known limitations.

Include the exact commands required to run STARTER and FULL generation.

Preserve the complete original problem requirements.

Do not mark future interview, scoring, offering, anomaly or export requirements complete.

## 17. AI prompt history

Record this complete Phase 03 prompt in the project's existing AI journal, preserving the full original text.

Record any additional user prompts sent during implementation.

Disclose the work Codex implemented, tests it executed and any design assumptions it introduced.

Do not claim human review or human execution unless explicitly confirmed.

## 18. Git safety

Continue on the existing project branch unless there is a documented reason not to.

Do not rewrite previous commits.

Make only necessary changes.

Do not push, merge, publish or submit.

Do not commit private PDFs, real candidate information, secrets, scratch databases or other unsuitable public-repository content.

After actual testing, create meaningful local commits.

## 19. Phase 03 acceptance criteria

Phase 03 is successful only if:

- FULL generates exactly 200 requisitions.
- FULL generates exactly 5,000 candidates.
- FULL generates exactly 8,000 applications.
- STARTER generates the configured smaller dataset.
- Parent-child integrity is valid.
- Approved requisitions have correct approval history.
- Applications have consistent valid lifecycle records.
- All required ID conventions used in this phase are respected.
- Synthetic variation is meaningful and documented.
- No unrelated records are corrupted.
- Both STARTER and FULL reproduce exactly under the same seed.
- Generation tests pass.
- Previous tests remain green.
- No prohibited later-phase work was started.

## 20. Final report

Create:

`reports/phase03-data-generation-handoff.md`

Include:

1. Overall assessment: PASS/PARTIAL/FAIL.
2. Files created/modified.
3. Architecture and generation design decisions.
4. Exact starter/full row counts.
5. Synthetic distributions and assumptions.
6. ID allocation and relationship verification.
7. Approval and application history evidence.
8. Actual test commands and outcomes.
9. Two-run starter and full reproducibility checksums.
10. Performance measurements.
11. Known limitations.
12. Updated requirement coverage.
13. AI usage and pending human review.
14. Local Git commit hashes and working-tree status.
15. Recommended Phase 04 implementation order.

Include enough implementation detail for an independent reviewer to evaluate Phase 03 without relying on Codex's final chat message.

**STOP after Phase 03. Do not implement Phase 04 without my review.**

Remember that the ultimate objective is a reliable end-to-end recruitment workflow with 2,000 interviews, rubric scorecards, offer approvals, five labelled negative scenarios, separate ground truth, independent validation and reproducible CSV/JSON/SQL exports. Phase 03 must establish a correct foundation for those remaining requirements.