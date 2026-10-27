# YOTTAFLEX AI — PHASE 05: STRUCTURED EVALUATION, SCORECARDS, OFFERS & APPROVALS

You are continuing our existing YottaFlex AI 72-Hour Code Challenge.

Phase 04 has been reviewed and conditionally approved for progression. You are authorized to implement Phase 05 only.

DEADLINE: October 29, 2026, at 1:52:35 PM IST.

Our objective is to complete the actual end-to-end recruiting workflow through structured interview evaluation, review-stage decisions, compensation-band-compliant offers, approvals, and auditable outcomes.

Prioritize correctness, traceability, reproducibility and explainability over extra features.

## 1. REQUIRED INSPECTION BEFORE IMPLEMENTATION

Read and inspect:

- AGENTS.md and README.md.
- Original assignment problem statement and both official PDFs.
- All Phase 01–04 handoff reports.
- Existing requirements matrix and data dictionary.
- Actual schema.sql and db.py.
- workflow.py and interview_generation.py.
- generate.py and generation_config.py.
- workflow_checks.py and generation_checks.py.
- Existing event models, status enums and tests.
- Current Git branch, commit history and working tree.

DO NOT assume the database supports an enum or column without inspecting the actual implementation.

Preserve all previous valid work, identifiers, schema constraints, tests and deterministic generation behavior.

## 2. PHASE 05 SCOPE

Implement working operations for:

1. Rubric-based structured scorecards.
2. Scorecard items tied to relevant skill requirements.
3. Reviewer eligibility and assignment.
4. Scorecard submission and completion.
5. Deterministic weighted evaluation.
6. Required-review completion gates.
7. Application progression to reviewed state.
8. Evaluation-derived offer eligibility.
9. Compensation-band-compliant offer creation.
10. Offer approval/rejection decisions.
11. Final application outcomes supported by the schema.
12. Transactional history and audit validation.
13. Deterministic Phase 05 generation for STARTER and FULL.
14. Automated tests and two-run reproducibility.

Do not implement the five deliberately injected anomaly datasets, separate ground-truth labels, final exporters or dashboard. Those are later phases.

## 3. REVIEWER AND RUBRIC POLICY

Use the existing Scorecard and ScorecardItem entities.

Each scorecard must:

- Reference an existing completed interview.
- Reference a valid assigned interview participant.
- Reference the correct requisition's requirements.
- Use the applicable effective requirement version.
- Use valid rubric scores.
- Preserve qualitative evidence/reason where the schema supports it.
- Have a deterministic, unique scorecard ID.
- Have an explicit lifecycle status.

Use the original required naming pattern:

SCORE-<interview-id>-<reviewer-id>

Inspect the schema to determine the exact canonical reviewer identifier.

Do not create evaluations for cancelled interviews.

Do not allow arbitrary reviewers or criteria from unrelated requisitions.

Document a clear rubric, for example:

0 = No evidence
1 = Below expectations
2 = Partially meets expectations
3 = Meets expectations
4 = Exceeds expectations

The exact policy must agree with the existing schema and synthetic design documentation.

## 4. WEIGHTED SCORE CALCULATION

Calculate scorecard totals from actual persisted ScorecardItem values and applicable SkillRequirement weights.

Use deterministic integer arithmetic, avoiding floating-point rounding inconsistencies.

The existing design uses:

- Criterion weights in basis points.
- Rubric values in the 0–4 range.
- Normalized totals in thousandths where applicable.

Inspect and preserve those existing conventions.

Define:

- Weight normalization.
- Rounding behavior.
- Required versus optional criteria.
- Missing-criterion handling.
- Completion requirements.
- Minimum acceptable score.
- Reviewer aggregation rules.
- Treatment of incomplete or conflicting evaluations.

All derived scores must be independently recomputable from persisted source records.

Never generate an independent random total score.

Ensure scorecard outcomes are correlated with the synthetic candidate's existing skills and role requirements through documented evaluation policy.

If controlled measurement variation is necessary, derive it from seeded scenario inputs and document it. The final score must always be computed from the actual stored rubric items.

## 5. SCORECARD STATE CHANGES

Implement transactional operations for:

- Creating a valid scorecard.
- Adding/changing rubric items while the scorecard is editable.
- Submitting/completing a scorecard.
- Rejecting incomplete scorecards.
- Rejecting invalid reviewer identities.
- Rejecting irrelevant criteria.
- Rejecting out-of-range rubric values.
- Rejecting duplicate interview/reviewer scorecards.

Every successful change must update its current projection and append the required event history atomically.

Do not overwrite audit history.

A submitted scorecard should not be silently modified. Use a documented correction/revision policy only if supported by existing schema and requirements.

## 6. REQUIRED REVIEW GATE

Implement the actual transition:

interviewing -> reviewed

using the real schema's status values.

A candidate may advance only when:

- At least one relevant interview was completed.
- Every required evaluation has been submitted.
- Required reviewers have provided complete scorecards.
- All mandatory rubric criteria are present.
- No required evaluation is incomplete.
- The application is not withdrawn/rejected.
- The evaluation belongs to the correct application/requisition.
- The calculated review decision satisfies the documented policy.

Use a clear, deterministic decision policy.

For example, define review eligibility using a documented weighted aggregate threshold and required-criterion minimums.

Do not conflate application lifecycle eligibility with offer eligibility.

Failed review attempts must leave projections and success-event history unchanged.

Record accepted stage transitions and supporting decision references.

## 7. INCOMPLETE SCORECARD COVERAGE

The problem explicitly requires incomplete scorecards.

Create some legitimate incomplete/draft scorecards in the valid baseline.

Ensure they:

- Have valid reviewers and references.
- Have valid existing item values.
- Are not marked completed incorrectly.
- Do not satisfy the required-review gate.
- Remain distinguishable from malformed or deliberately injected anomaly records.

Include deterministic variation in complete and incomplete evaluations.

Document exact counts in the final report.

## 8. OFFER ELIGIBILITY

Create offers only for applications that satisfy all documented prerequisites.

Eligibility should consider:

- Valid reviewed application state.
- Required completed evaluations.
- Derived evaluation outcome.
- Valid approved requisition.
- Appropriate candidate/application lifecycle state.
- No incompatible active offer.
- Current or historical compensation authorization as defined in the schema.
- Permitted manager/HR/approver actor.

Do not randomly mark applications as offer-eligible.

Offer eligibility must be derived from recorded data and explicit business policies.

## 9. COMPENSATION BANDS

Use the requisition's existing approved compensation snapshot.

Maintain:

- Consistent currency.
- Integer minor currency units.
- Approved lower and upper boundaries.
- Correct requisition/offer association.
- Explicit offer amounts derived from documented policy.

Normal offer creation MUST reject:

- Below-band amounts, unless explicitly allowed by documented policy.
- Above-band amounts.
- Currency mismatches.
- Offers against unapproved roles.
- Invalid application stages.
- Duplicate active final offers.

Test exact band boundaries.

Generate meaningful but fully synthetic offer values within approved ranges.

Never manipulate compensation history to force an invalid offer to pass.

## 10. OFFER APPROVAL WORKFLOW

Use the existing Offer, Approval, OfferEvent and ApprovalEvent schema.

Implement:

- Offer creation.
- Submission for approval.
- Approval.
- Rejection.
- Finalization where supported.
- Appropriate application lifecycle progression.

Define actor authority explicitly.

At minimum, an approval must:

- Reference the correct offer.
- Have a valid approver.
- Follow the documented approval policy.
- Preserve decision time and reason.
- Be auditable through explicit events.
- Respect the approved compensation band.

Do not allow a requester to approve their own offer if the defined synthetic policy requires separation of duties.

Do not confuse requisition approvals with offer approvals.

Each must have distinct subject references and histories.

Avoid inventing unsupported multi-level approval requirements.

## 11. FINAL APPLICATION OUTCOMES

Complete the end-to-end workflow through final supported lifecycle states.

For example:

applied -> screening -> interviewing -> reviewed -> offer -> hired

Only use stages that actually exist in the schema.

Ensure:

- Every successful transition has a valid predecessor.
- Every stage gate is satisfied.
- Relevant records exist before dependent transitions.
- Offer approval precedes final accepted/hired state.
- Rejected/withdrawn candidates cannot be hired.
- Active incompatible interviews or offers are resolved consistently.
- Historical events are never deleted or silently rewritten.

Make final outcomes derived from the stored evaluation and offer approval policies.

Document why each outcome occurred.

## 12. SYNTHETIC FULL-DATA GENERATION

Extend the existing phase-based deterministic generator.

Preserve:

FULL:
- 200 Requisitions
- 5,000 Candidates
- 8,000 Applications
- 2,000 Interviews

STARTER:
- Existing configured counts.

Generate scorecards and offers using existing eligible interview/application records.

The Phase 04 full dataset currently reports 98 completed interviews.

Do not assume this is sufficient or insufficient without examining the intended evaluation/offer coverage and actual schema.

If necessary, make a small, deterministic, justified adjustment to valid interview completion cohorts while preserving:

- Exactly 2,000 Interview records.
- All stage/scheduling rules.
- Withdrawal and cancellation coverage.
- Previous master identifiers.
- Event consistency.
- Full reproducibility.

Do not modify completed interviews arbitrarily or manufacture scores detached from real records.

Choose and document meaningful evaluation and offer volumes. The problem statement does not prescribe exact Scorecard or Offer counts, so do not invent employer-mandated targets.

Include sufficient positive and negative decision variety to demonstrate a working process.

## 13. TRANSACTIONAL CONSISTENCY

Every successful public workflow operation must:

1. Begin a safe transaction.
2. Validate all prerequisites.
3. Make the intended projection change.
4. Insert related child records.
5. Append explicit history events.
6. Commit atomically.

On failure, roll back completely.

Do not produce partially approved offers, incomplete history, or inconsistent application stages.

Preserve existing BEGIN IMMEDIATE writer-serialization strategy unless a tested reason requires modification.

## 14. PHASE 05 VALIDATION

Extend the validator with independent checks for:

- Scorecard and reviewer identity.
- Relevant requisition criteria.
- Criterion versions/effective dates.
- Required rubric coverage.
- Completed scorecard correctness.
- Draft/incomplete scorecard legitimacy.
- Derived score arithmetic.
- Review-gate enforcement.
- Final application stage correctness.
- Approved compensation snapshots.
- Offer currency/band compliance.
- Offer approval authority.
- Approval chronology.
- Offer/event reconciliation.
- Application/event reconciliation.
- Final hired/rejected lifecycle consistency.
- Foreign-key integrity.
- Primary-key uniqueness.
- Historical immutability.
- No input-label or ground-truth leakage.
- Preservation of all previous scheduling and master-data invariants.

Do not modify validation to conceal real violations.

## 15. REQUIRED AUTOMATED TESTS

Add actual tests covering:

1. Valid scorecard creation.
2. Invalid reviewer rejection.
3. Invalid requisition criterion rejection.
4. Rubric boundary values.
5. Required-criterion omission.
6. Duplicate scorecard rejection.
7. Valid weighted-score calculation.
8. Independent score recomputation.
9. Incomplete scorecard blocks review.
10. Completed required scorecards allow review.
11. Review denied if interview incomplete.
12. Review denied for withdrawn/rejected application.
13. Valid offer creation.
14. Offer below lower band rejected.
15. Offer exactly at lower band accepted.
16. Offer exactly at upper band accepted.
17. Above-band offer rejected.
18. Currency mismatch rejected.
19. Unapproved requisition rejected.
20. Invalid offer actor rejected.
21. Approval actor authorization.
22. Duplicate/incompatible active offer rejected.
23. Offer rejection audit trail.
24. Approved offer audit trail.
25. Valid final application outcome.
26. Invalid direct hired transition rejected.
27. Rollback on partial mutation failure.
28. Event sequence/chronology consistency.
29. No inappropriate active scheduling after terminal outcomes.
30. STARTER phase05 generation.
31. FULL phase05 generation.
32. Same-seed deterministic reproduction.
33. All previous tests remain passing.

Use existing unittest tooling and temporary local databases.

Do not hardcode artificial PASS outputs.

## 16. FULL REPRODUCIBILITY

Run two independent STARTER generations and two independent FULL generations with the same fixed seed.

Compare:

- Every row in every table.
- Row counts.
- Per-table canonical SHA-256.
- Aggregate canonical SHA-256.
- Deterministic evaluation summaries.
- Derived scores.
- Offer decisions and amounts.
- Final lifecycle projections.

Use the existing canonical serializer.

Do not compare SQLite binary file hashes as the primary reproducibility evidence.

Report real results and failures.

## 17. PERFORMANCE

Measure actual:

- Total FULL generation duration.
- Evaluation generation duration.
- Offer generation duration.
- Validation duration.
- Reproducibility execution.

Avoid unnecessary architectural complexity, concurrency, frameworks, hosted services or new dependencies.

Optimize only measured bottlenecks.

## 18. DOCUMENTATION

Create:

docs/phase05/evaluation-offer-design.md

Include:

- Rubric definitions.
- Score computation formula.
- Required evaluation policy.
- Interview completion policy.
- Stage-transition matrix.
- Evaluation decision thresholds.
- Offer eligibility policy.
- Compensation policy.
- Approval actor rules.
- Event and audit model.
- Boundary and failure scenarios.
- Synthetic distribution assumptions.
- Determinism/reproducibility.
- Known limitations.

Update README and the existing 75-row requirements status overlay.

Do not claim mandatory anomaly injection or export completeness yet.

## 19. AI PROMPT HISTORY

Preserve this complete prompt verbatim in the project AI history.

Record additional prompts, if any.

Clearly distinguish:

- Code generated with Codex.
- Tests executed by Codex.
- Decisions proposed by AI.
- Human decisions actually confirmed.
- Human review still pending.

Do not fabricate personal manual testing or code ownership evidence.

## 20. GIT SAFETY

Preserve the existing branch and commits.

Do not overwrite completed work.

Do not push, merge, configure remotes, publish, contact recruitment or submit.

Make small, relevant changes.

Never include private assignment PDFs, credentials, real candidate data or scratch databases in Git.

After actual test execution, make meaningful local commits.

## 21. ACCEPTANCE CRITERIA

Phase 05 is PASS only if:

- Actual structured scorecards exist.
- Required-review gates work.
- Missing/incomplete evaluations cannot authorize progression.
- Score calculations reconcile exactly.
- Relevant criteria and valid reviewers are enforced.
- Applications successfully reach reviewed status through valid transitions.
- Actual eligible offers exist.
- Offer amounts respect approved bands.
- Approved and rejected offers have auditable history.
- At least one legitimate positive final outcome is demonstrated.
- Invalid final-state transitions are rejected.
- All existing full-scale parent/interview counts remain exact.
- Every required state change has valid history.
- No unexpected FK/scheduling conflicts exist.
- All new and previous tests pass.
- Same-seed starter/full replay matches.
- Documentation and prompt history are complete for the phase.
- No future anomaly/truth/export functionality is falsely claimed complete.

## 22. HANDOFF REPORT

Create:

reports/phase05-evaluation-offer-handoff.md

Include:

1. PASS/PARTIAL/FAIL.
2. Exact files created/modified.
3. Schema changes, if any.
4. Structured scorecard counts.
5. Complete/incomplete scorecard counts.
6. Actual rubric/scoring example.
7. Derived evaluation decision distribution.
8. Review-stage transition results.
9. Offer created/approved/rejected counts.
10. Compensation-band reconciliation results.
11. Demonstrated successful end-to-end recruiting path.
12. Demonstrated rejected operations.
13. Event-history validation summary.
14. Actual test commands/results.
15. All validation check counts.
16. Independent same-seed checksum evidence.
17. Performance measurements.
18. Known limitations.
19. Requirement coverage updates.
20. AI involvement disclosure.
21. Git commit hashes/working-tree state.
22. Recommended Phase 06 scope.

The report must be self-contained for independent review in a future ChatGPT conversation.

STOP after Phase 05.

Do not implement the five deliberate negative scenarios, ground-truth output, evaluation metrics, CSV/JSON/SQL export engine, web UI or deployment without separate authorization.

Remember: the objective is a working, auditable recruitment workflow—not merely generating Scorecard and Offer rows.