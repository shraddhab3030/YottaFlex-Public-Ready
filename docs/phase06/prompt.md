# YOTTAFLEX AI — PHASE 06: CONTROLLED ANOMALIES, ISOLATED GROUND TRUTH & INDEPENDENT EVALUATION

You are continuing the YottaFlex AI 72-Hour Code Challenge for the Associate AI Forward Deployed Engineer position.

Phase 05 has been reviewed and conditionally approved for progression.

You are authorized to implement Phase 06 only.

HARD DEADLINE:
October 29, 2026, 1:52:35 PM IST.

Our objective is to satisfy all five mandatory negative scenarios through deterministic, controlled anomaly generation, independently detect violations using real domain rules, preserve relational integrity and event traceability, and measure anomaly-detection quality against separate ground truth.

Prioritize business correctness, label integrity, reproducibility and explainable results.

Do not build unnecessary infrastructure.

## 1. INSPECT THE EXISTING IMPLEMENTATION FIRST

Before modifying code:

1. Read AGENTS.md and README.md.
2. Read the complete original problem statement and both official PDFs.
3. Read all Phase 01–05 handoff reports.
4. Review the original 75 requirements and current implementation overlay.
5. Inspect schema.sql, db.py and the complete data dictionary.
6. Inspect generate.py, generation_config.py, ids.py and canonical.py.
7. Inspect workflow.py, evaluation.py and offers.py.
8. Inspect workflow_checks.py, evaluation_checks.py and all supporting validation modules.
9. Inspect all relevant tests and reproducibility evidence.
10. Inspect the Git branch, commits, current changes and ignored output paths.

Never assume a column, event type, enum, field or relationship exists without verifying the actual schema.

Preserve previous legitimate work and all existing acceptance tests.

## 2. REQUIRED DELIVERABLES

Implement:

1. An immutable valid-baseline reference.
2. A deterministic anomaly-injection subsystem.
3. Five mandatory negative scenario types.
4. Controlled semantically invalid records or observations.
5. Separate ground_truth.csv and ground_truth.json.
6. An independent anomaly detector.
7. Detailed findings with affected IDs and rule explanations.
8. Precision, recall and F1 evaluation.
9. Clean-versus-anomalous comparison.
10. Structural integrity checks.
11. Fixed-seed replay and checksum verification.
12. Automated anomaly tests.
13. Updated documentation, prompt history and requirements status.

Do not implement the final generalized CSV/JSON/SQL exporter, complete release manifest or dashboard in this phase.

Exception: the required ground-truth CSV/JSON files and detection/evaluation reports are explicitly within scope.

## 3. BASELINE PRESERVATION

Use the existing validated Phase 05 FULL dataset as the foundation.

Maintain exactly:

- 200 requisitions.
- 5,000 candidates.
- 8,000 applications.
- 2,000 interviews.

Preserve the existing legitimate scorecards, offers, approvals, reviewer assignments and histories.

The baseline must pass the existing Phase 05 validation unchanged.

Never mutate the source baseline database in place.

Create a separately identifiable anomaly dataset from a fresh deterministic generation or a verified baseline copy.

Record the input baseline's canonical checksum and the anomalous dataset's checksum.

Do not accidentally introduce nondeterminism through SQLite ordering or filesystem paths.

## 4. DESIGN THE ANOMALY ARCHITECTURE

Implement an explicit separation between:

A. Valid canonical baseline.
B. Anomalous evaluation inputs.
C. Ground-truth labels.
D. Independent detector findings.
E. Post-detection evaluation metrics.

Document the separation clearly.

Normal workflow APIs must continue enforcing their existing safeguards.

Controlled anomaly creation may use a dedicated test-only or generation-only injection mechanism, but this must never be exposed as an ordinary production workflow operation.

Do not disable global foreign-key integrity, delete history, or weaken validation merely to permit anomaly injection.

Prefer business-semantic anomalies that remain structurally valid.

If an existing schema trigger prevents direct mutation, use an isolated staging/observation representation or a defensible, narrowly scoped fixture-generation approach.

If direct SQLite mutation would require compromising append-only history or FK constraints, DO NOT force the mutation into canonical tables.

Instead create a separate anomaly observation table/file with explicit entity references, timestamps and before/after observations, and make the detector analyze that source alongside the canonical data.

The chosen approach must produce genuinely detectable anomaly inputs, not only expected labels.

Record exactly which representation is used for each case.

## 5. FIVE REQUIRED ANOMALIES

Implement each of the following using deterministic, documented rules.

### N01 — STAGE ADVANCEMENT WITHOUT REQUIRED REVIEW

Create an observation showing an application advancing to a review-dependent stage despite missing required completed evaluations.

Preserve valid candidate/application/interview references.

Detector logic must identify:

- Current or observed application stage.
- Required completed review policy.
- Actual submitted scorecard state.
- Missing reviewer or required rubric evidence.
- Unsupported advancement.

Ground-truth issue_type:

stage_gate_missing_review

Expected finding:
Illegal advancement due to incomplete required review.

Do not use ground truth to decide that the stage is invalid.

### N02 — INTERVIEWER DOUBLE-BOOKING

Create two overlapping capacity-occupying interview observations assigned to at least one common interviewer.

Use actual valid interviewer identities and interview references.

The overlap rule must use half-open intervals:

a.start < b.end AND b.start < a.end

Both interviews must occupy capacity for the overlap to be invalid.

Cancelled bookings must not be reported as double-booked.

Adjacent interviews where a.end == b.start must not be reported.

Ground-truth issue_type:

interviewer_double_booked

Include both interview IDs and the shared interviewer ID.

Expected finding:
Two active bookings overlap for one interviewer.

### N03 — OFFER EXCEEDS APPROVED BAND

Create an offer observation exceeding the upper bound of its valid, applicable, historically approved compensation band.

Use the correct requisition, offer, application and currency relationships.

Ground-truth issue_type:

offer_exceeds_band

Expected finding:
Observed offer amount > approved maximum.

Do not corrupt currency, FKs or unrelated approval records just to create this issue.

Include the applicable approved compensation snapshot, observed amount, and difference in minor currency units.

Test both exact-upper-bound valid behavior and above-bound invalid behavior.

### N04 — WITHDRAWN CANDIDATE REMAINS SCHEDULED

Create an observation with an active scheduled interview linked to an application or candidate whose withdrawal is effective before the booking remains active.

Use valid identities and a coherent timeline.

Ground-truth issue_type:

withdrawn_still_scheduled

Expected finding:
An interview remains scheduled after the applicable withdrawal.

Do not flag completed or historically cancelled interviews solely because withdrawal occurred later.

Document candidate-wide versus application-level withdrawal semantics.

### N05 — EVALUATION USES IRRELEVANT CRITERIA

Create a scorecard evaluation observation referencing an existing skill requirement that is not applicable to its interview's requisition or effective rubric version.

All referenced identities must exist.

Ground-truth issue_type:

irrelevant_evaluation_criterion

Expected finding:
Scorecard uses a criterion outside the applicable requisition/version.

Do not use an orphaned criterion ID.

Maintain structural integrity while violating semantic applicability.

## 6. SCENARIO COUNTS AND COVERAGE

At least one genuine detected occurrence of every mandatory anomaly type is required.

For stronger evaluation, aim for multiple deterministic cases per type while preserving meaningful clean controls.

If feasible, create a modest, documented mix such as 5–10 cases per type; these are internal coverage goals, not employer-mandated counts.

Include:

- Normal valid records.
- Boundary-valid records.
- Deliberately invalid records.
- Records that resemble anomalies but are actually valid.

Examples of valid controls:

- Adjacent non-overlapping interviews.
- Cancelled bookings that no longer occupy capacity.
- Offer exactly at the approved upper band.
- Draft scorecard that does not advance an application.
- Correct criterion from the applicable requisition.
- Historical completed interview before subsequent withdrawal.

Avoid overlapping injected anomalies unless explicitly intended and fully represented in ground truth.

Every deliberate violation must have a deterministic affected-record key.

## 7. GROUND-TRUTH DESIGN

Generate:

ground_truth.csv
ground_truth.json

Ground truth should contain at least:

- scenario_id
- issue_type
- affected_entity_type
- affected_entity_id
- related_entity_ids
- expected_decision
- rule_id
- observed_violation
- severity
- applicable_timestamp
- deterministic_seed

Include extra structured fields where necessary.

All labels must derive from documented business rules and known controlled interventions.

Never assign anomaly labels independently at random.

Never include ground_truth, issue_type, expected_decision or equivalent answers in detector input features.

Never make the detector discover scenario records by inspecting ground-truth identifiers, injection-only metadata, filenames, injection order or precomputed labels.

Use scenario IDs only for post-detection matching if they cannot influence detection.

Preserve both human-readable and machine-readable representations.

CSV/JSON truth records must agree exactly.

## 8. INDEPENDENT DETECTOR

Implement a detector that reads business records and/or anomaly observations, not expected labels.

For each detected violation, return:

- Finding ID.
- Rule ID.
- Issue type.
- Primary affected entity.
- Related entity references.
- Actual observed values.
- Expected invariant.
- Explanation.
- Evidence timestamps.
- Severity.

Detector rules must be based on actual domain constraints already implemented or documented.

Reuse pure business predicates where reasonable, but avoid blindly accepting the generator's expected labels.

Do not change detector behavior to hardcode the known injected records.

Detector must work against clean baseline input and anomalous input using the same logic.

A clean dataset should produce zero unexplained findings.

## 9. FINDING-TO-TRUTH MATCHING

Define deterministic matching semantics.

A true positive requires the correct:

- Rule or issue type.
- Affected entity identity.
- Relevant related identity, where necessary.

For double-booking, matching must identify the overlapping interview pair and interviewer without depending on arbitrary pair ordering.

For irrelevant criteria, matching must identify the scorecard and offending criterion.

For salary violations, matching must identify the offer and applicable band.

Define whether repeated detections of one issue count as duplicates.

Do not credit the same ground-truth issue multiple times.

Do not ignore unexpected findings.

## 10. METRICS

Calculate from actual detector findings and independent truth:

- True positives (TP).
- False positives (FP).
- False negatives (FN).
- Precision.
- Recall.
- F1 score.
- Counts by anomaly type.
- Detection coverage by rule.
- Clean-baseline false-positive count.

Use conventional formulas:

Precision = TP / (TP + FP)

Recall = TP / (TP + FN)

F1 = 2 * Precision * Recall / (Precision + Recall)

Define and document zero-denominator behavior.

Do not report accuracy unless a defensible true-negative universe is explicitly defined.

Keep the evaluation process independent of the detection process.

Report false positives and false negatives honestly.

Perfect metrics are not mandatory; trustworthy measured metrics are.

If the detector finds additional legitimate violations not intentionally injected, investigate them rather than hiding them to improve precision.

## 11. PRESERVE HISTORY AND STRUCTURAL INTEGRITY

After anomaly injection:

- All required parent identifiers must remain valid.
- All primary keys remain unique.
- Foreign-key integrity remains intact.
- Valid enum and scalar constraints remain intact where applicable.
- No unrelated rows change.
- Existing master data remains unchanged.
- Historical source events remain intact unless the anomaly representation explicitly documents an isolated observed deviation.
- Expected anomalies are semantic business-rule failures, not silent structural corruption.

Validate structural integrity independently from domain-rule violations.

Do not treat a deliberately injected semantic anomaly as a failed structural baseline.

However, do not conceal unexpected integrity errors.

## 12. DETERMINISM AND REPRODUCIBILITY

Use fixed seed 20261022 by default.

Generate two independent anomaly datasets from equivalent validated baselines.

Compare:

- Canonical input row counts.
- Canonical input content.
- Canonical input checksums.
- Ground-truth CSV/JSON contents.
- Detector findings.
- Detection metric reports.

Identical inputs and seed must produce identical outputs.

Ensure the existing Phase 05 generator continues reproducing its previous clean hashes.

Do not include wall-clock timing, absolute paths or temporary filenames in deterministic content.

## 13. AUTOMATED TESTING

Write actual tests for:

1. Clean baseline produces no anomaly findings.
2. Every mandatory issue type is generated.
3. Every issue type is independently detected.
4. Detector never imports/reads ground_truth.
5. Valid adjacent interviews are not double-booked.
6. Cancelled bookings do not create false conflicts.
7. Above-band offers are detected.
8. Exact-upper-bound offers are accepted.
9. Wrong-requisition criterion is detected.
10. Applicable criterion is accepted.
11. Incomplete review alone is not anomalous.
12. Advancement despite incomplete review is anomalous.
13. Withdrawn active booking is detected.
14. Cancelled booking after withdrawal is valid.
15. All anomaly references resolve.
16. PK/FK checks remain valid.
17. Baseline checksum is unchanged by injection.
18. No unrelated records mutate.
19. Truth CSV and JSON agree.
20. No ground-truth label leakage.
21. Correct TP/FP/FN matching.
22. Duplicate finding handling.
23. Correct precision/recall/F1.
24. Clean and anomalous detector use the same engine.
25. Same-seed anomaly replay matches.
26. Different seeds alter appropriate synthetic attributes.
27. Injection failures do not publish partial outputs.
28. All previous 148 tests remain passing.

Add additional boundary tests where needed.

Use existing unittest and local SQLite infrastructure.

Do not fabricate results or hardcode expected metric successes.

## 14. VALIDATION REPORTS

Produce separate reporting for:

A. Clean baseline structural/domain validation.
B. Anomalous input structural validation.
C. Anomalous input semantic findings.
D. Ground-truth records.
E. Detector-versus-truth evaluation.

Never collapse all results into one PASS flag.

Expected injected business violations must remain visible.

The overall challenge can consider controlled anomaly generation successful even though the anomalous input intentionally fails business-rule validation.

Distinguish expected anomaly failures from unexpected failures.

## 15. INTEGRATION WITH EXISTING GENERATION

Prefer extending the existing phase-based generator with an explicit anomalies phase or dedicated scenario-generation command.

Preserve:

--phase master
--phase interviews
--phase evaluations

If adding:

--phase anomalies

make its behavior explicit and documented.

The anomaly phase must first obtain a valid Phase 05 dataset, then produce isolated controlled observations and ground truth.

Do not silently modify the default clean generator mode.

Do not weaken ordinary workflow functions to make anomalies easier to generate.

Avoid unnecessary architectural refactoring.

## 16. EXECUTION AND QUALITY

Run:

- All previous automated tests.
- New anomaly tests.
- Baseline validation.
- Anomaly structural validation.
- All five detection rules.
- Independent ground-truth evaluation.
- Two-run anomaly reproducibility.
- Dictionary freshness and privacy checks.

Measure actual execution duration.

Maintain appropriate zero-copy/streaming approaches if helpful, but do not introduce unnecessary dependencies.

The required dataset scale remains manageable locally.

## 17. DOCUMENTATION

Create:

docs/phase06/anomaly-design.md

Document:

- The five business violations.
- Injection representation.
- Why each anomaly is invalid.
- Ground-truth separation.
- Detector independence.
- Rule definitions.
- Matching methodology.
- Evaluation metric formulas.
- Clean controls and boundaries.
- Structural versus semantic validation.
- Input/output directory layout.
- Exact commands.
- Known limitations.
- Reproducibility methodology.

Update README and the 75-row requirements overlay.

Explicitly state which challenge requirements remain incomplete.

## 18. AI TRANSPARENCY

Preserve this complete Phase 06 prompt verbatim in the AI history.

Record any additional prompts.

Document what Codex generated, executed and verified.

Do not attribute AI-executed tests to human review.

Preserve previous AI disclosure and historical prompt records.

## 19. GIT SAFETY

Work on the current branch and preserve prior commits.

Do not push, merge, configure a remote, publish, contact recruiters or submit.

Do not commit private source PDFs, credentials, real candidate data or scratch databases.

Commit only necessary code, tests, documentation and safe reproducibility evidence.

Generated anomaly artifacts may remain ignored during this phase, but document precisely how they will be included in the final public deliverables during Phase 07.

Make meaningful local commits after successful verification.

## 20. PHASE 06 ACCEPTANCE CRITERIA

Phase 06 is PASS only if:

- The clean Phase 05 baseline remains valid.
- All four mandatory full-scale count targets are preserved.
- All five anomalies are actually represented as detectable input violations.
- Every anomaly has independently derived ground truth.
- Ground truth CSV and JSON exist and agree.
- The detector does not rely on ground truth or injection-specific hints.
- Each anomaly type has actual detector findings.
- Finding-to-truth matching is well-defined.
- TP, FP, FN, precision, recall and F1 are calculated.
- Structural integrity remains valid.
- No unrelated baseline rows are corrupted.
- Clean control cases behave correctly.
- Same-seed anomaly generation is reproducible.
- All previous tests remain passing.
- New automated tests pass.
- No mandatory future exporter work is falsely claimed complete.

## 21. HANDOFF REPORT

Create:

reports/phase06-anomaly-ground-truth-handoff.md

Include:

1. Phase result: PASS/PARTIAL/FAIL.
2. Exact files created/modified.
3. Anomaly architecture.
4. Structural versus semantic design decisions.
5. All five scenario types and actual occurrence counts.
6. Exact injected/observed records for at least one example per type.
7. Ground-truth CSV/JSON file locations.
8. Ground-truth isolation proof.
9. Detector findings count by rule.
10. TP/FP/FN and precision/recall/F1.
11. Clean-baseline false-positive findings.
12. Structural integrity results.
13. Baseline preservation evidence.
14. Test commands and actual results.
15. Same-seed checksums and replay evidence.
16. Performance measurements.
17. Known limitations and risks.
18. Requirements coverage changes.
19. AI disclosure and human-review status.
20. Local Git commit hashes and working-tree state.
21. Clear Phase 07 recommendations.

The report must be self-contained for independent evaluation in another ChatGPT conversation.

STOP after Phase 06.

Do not implement generalized CSV/JSON/SQL dataset exporters, SQL re-import verification, final publication manifest, public GitHub setup or portal submission.

Remember that five rejected API calls are NOT sufficient. We need five genuine, separately labelled, detector-visible violation types and meaningful evaluation evidence.