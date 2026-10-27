# YOTTAFLEX AI — PHASE 08: INDEPENDENT FINAL AUDIT, PRIVACY REVIEW & PUBLICATION READINESS

You are continuing the YottaFlex AI 72-Hour Code Challenge.

Phase 07 has been reviewed and conditionally approved for progression.

You are authorized to conduct the Phase 08 final audit and publication preparation only.

HARD DEADLINE:
October 29, 2026, 1:52:35 PM IST.

IMPORTANT:
DO NOT push, publish, configure GitHub remotes, rewrite existing Git history, merge, submit on the recruitment portal, contact recruiters or send emails.

All publication and submission actions require separate explicit user authorization.

PRIMARY GOAL:
Independently assess the complete project against every original requirement, resolve publication-readiness issues, preserve all working functionality, and produce an evidence-backed GO/NO-GO recommendation.

Do not create unnecessary features or refactor validated code.

## 1. READ AND INSPECT ALL PROJECT SOURCES

Before changing anything, read:

- AGENTS.md.
- README.md.
- Original complete problem statement.
- Both official recruitment PDFs.
- All Phase 01–07 handoff reports.
- docs/phase01/requirements.md.
- docs/phase07/requirements-acceptance.md.
- docs/data-dictionary.md.
- Every relevant architecture and business-rule document.
- Every source file in src/yottaflex.
- All test modules.
- All relevant CLI scripts.
- Artifact manifest, provenance, validation and anomaly reports.
- AI prompt-history journal and phase prompt files.
- Current Git branch, status, commits, tracked files and history.

Do not rely solely on previous handoff reports.

Inspect actual source code and actual artifacts.

Do not silently assume that a previously reported PASS means no defect exists.

## 2. INDEPENDENT REQUIREMENTS AUDIT

Audit all 75 original requirements.

For each requirement, verify:

1. Exact original requirement.
2. Implemented source file/function.
3. Relevant stored data or generated artifact.
4. Actual test or verification command.
5. Observed result.
6. Missing or partial behavior.
7. Severity of any gap.
8. Whether the requirement is mandatory, conditional or optional.

Use:

PASS
PARTIAL
FAIL
NOT_APPLICABLE

Do not mark a requirement PASS solely because earlier Codex documentation says it passed.

Create:

docs/phase08/final-requirements-audit.md

Preserve historical requirement wording and prior overlays.

## 3. SOURCE CODE QUALITY REVIEW

Review actual implementation for:

- Correct relational relationships.
- Foreign-key integrity.
- SQL injection risks.
- Transaction boundaries.
- Unsafe implicit commits.
- Error handling.
- Input validation.
- Race conditions.
- Event/projection inconsistencies.
- Deterministic generation.
- Unseeded randomness.
- Incorrect timestamp semantics.
- Currency and score arithmetic.
- Scheduling conflicts.
- Stage-gate bypasses.
- Incorrect approval authority.
- Ground-truth leakage.
- Inaccurate anomaly evaluation.
- Export/import data loss.
- File overwrite vulnerabilities.
- Unnecessary dependencies.
- Hardcoded machine-specific paths.
- Dead code or unreachable required behavior.

Classify findings:

P0 = submission blocker or major integrity/security failure.
P1 = important correctness or maintainability concern.
P2 = optional quality improvement.

For every confirmed defect, provide exact file/line evidence and a reproduction test.

Do not report hypothetical concerns as confirmed defects.

## 4. VERIFY BUSINESS WORKFLOWS

Independently verify the complete end-to-end path:

Approved requisition
-> Candidate/application
-> Screening
-> Interview scheduling
-> Completed interview
-> Structured scorecards
-> Evaluation decision
-> Reviewed application
-> Offer creation
-> Approval
-> Accepted offer
-> Hired application

Verify:

- Correct stages.
- Correct actors.
- Valid timing.
- Every required gate.
- Appropriate approvals.
- Immutable history.
- Derived values.
- No forbidden transitions.
- Consistent final projections.

Demonstrate at least one actual successful path from the generated dataset.

Demonstrate important rejected operations and why they fail.

Do not create fake outputs.

## 5. FULL DATASET AUDIT

Verify the canonical FULL dataset contains exactly:

- 200 requisitions.
- 5,000 candidates.
- 8,000 applications.
- 2,000 interviews.

Audit all other required entities and supporting tables.

Check:

- PK uniqueness.
- FK integrity.
- Valid joins.
- Enum compliance.
- Chronology.
- Duplicate natural keys.
- Arithmetic consistency.
- Event history.
- Scorecards.
- Compensation bands.
- Offer approvals.
- Withdrawals.
- Rescheduling.
- Incomplete scorecards.
- Reproducibility.

Verify dataset variation and disclose synthetic realism limitations.

Do not change valid existing data to create artificially favorable metrics.

## 6. FIVE NEGATIVE SCENARIOS

Independently inspect actual anomaly inputs, not only findings.json.

Verify all five cases:

1. Missing required review during advancement.
2. Interviewer double-booking.
3. Offer exceeding approved band.
4. Withdrawn candidate still scheduled.
5. Irrelevant rubric criteria.

For each:

- Inspect the before/after observation.
- Verify parent references.
- Verify why it violates the actual business rule.
- Verify independent detector output.
- Verify matching ground truth.
- Verify no unrelated corruption.

Re-run detection without passing truth to the detector.

Inspect the dependency graph to ensure detector logic cannot consume ground truth or injection-only metadata.

Verify actual TP, FP, FN, precision, recall and F1.

Document that controlled-case perfection is not real-world accuracy.

## 7. EXPORT AND RESTORATION AUDIT

Inspect actual:

artifacts/baseline/csv/
artifacts/baseline/json/
artifacts/baseline/sql/
artifacts/anomalies/
artifacts/manifest.json

Verify:

- Every one of 24 tables exported.
- Complete SQL seed.
- Deterministic row order.
- Correct NULL/type handling.
- All required records included.
- Actual file hashes match manifest.
- Ground truth separately packaged.
- No private or accidental scratch files.
- All formats restore without loss.

Run the existing package verification from a clean, independent work directory.

Verify all restored databases reproduce the expected canonical hash.

Do not rely solely on a recorded earlier check.

## 8. REPRODUCIBILITY AUDIT

Run the documented independent same-seed verification.

Confirm:

- Same seed 20261022.
- Same configuration.
- Same mandatory counts.
- Same records.
- Same per-table checksums.
- Same aggregate checksum.
- Same exported file bytes.
- Same anomaly observations.
- Same separate ground truth.
- Same findings and metrics.

Report any differences accurately.

Do not compare SQLite database-file bytes as the primary reproducibility evidence.

Keep transient duration and filesystem paths outside deterministic artifacts.

## 9. CRITICAL PUBLIC-REPOSITORY PRIVACY AUDIT

The Phase 07 report identified seven older tracked reports with private local filesystem paths.

Audit the ENTIRE tracked repository and relevant Git history, including:

- Reports.
- Documentation.
- Git commit messages.
- Prompt-history files.
- Configuration.
- Generated artifacts.
- Scripts.
- Test fixtures.
- README.
- Previous committed versions of files.

Look for:

- Absolute user-specific filesystem paths.
- Usernames or machine identifiers.
- Personal email addresses.
- Recruitment application identifiers or private URLs.
- Credentials, tokens, keys and secrets.
- Sensitive information.
- Actual candidate records.
- Unauthorized proprietary content.
- Accidental logs, temporary files or binaries.

IMPORTANT:
Do not automatically rewrite or delete historical commits.

First determine whether problematic content exists only in the current tree or also in earlier commits.

Provide a comparison of publication strategies:

A. Publish existing Git history after reviewed cleanup.
B. Create a new curated public repository history while preserving the original local development repository.
C. Another minimally disruptive, transparently documented alternative.

For each, document:

- What information would remain publicly visible.
- Effect on meaningful development history.
- Effect on required AI disclosure.
- Privacy implications.
- Reviewer experience.
- Risks and limitations.

Recommend the safest accurate strategy.

Do not execute history rewriting, repository creation or publication yet.

## 10. AI PROMPT HISTORY COMPLETENESS

The official FAQ requires all prompts sent to every AI tool.

Audit the existing AI journal and prompt files.

Determine exactly which prompts are stored, which tools were used, and which prompt records may be missing.

Distinguish:

- Complete verbatim prompts.
- Partial preserved prompts.
- Reconstructed descriptions.
- Unavailable historical prompts.

Do not invent missing prompts.

Do not claim that Codex alone was used if ChatGPT was used to plan or review the project.

Explicitly account for ChatGPT planning/review prompts and any other genuinely used AI tool.

Prepare a public-safe AI disclosure explaining:

1. Where AI accelerated implementation.
2. Where AI assistance was heavily relied upon.
3. Which decisions were proposed by AI.
4. What the candidate personally reviewed.
5. What tests Codex executed.
6. What tests the candidate personally executed.
7. Which limitations or unavailable prompt records remain.

DO NOT fabricate candidate review or personal validation.

Where historical ChatGPT prompts are not available locally, create an exact missing-history checklist for the user to complete.

Only record recovered prompt text as verbatim when it actually matches the source.

## 11. README AND REVIEWER EXPERIENCE

Audit the README from the perspective of a recruiter who has never seen this project.

It must clearly explain:

- Project purpose.
- Business problem.
- Technology choices.
- Architecture.
- Eleven core entities.
- Business workflows.
- Synthetic generation.
- Required dataset volumes.
- Deterministic seed.
- Scheduling.
- Scorecards.
- Offers and approvals.
- Five negative scenarios.
- Separate ground truth.
- How to run and test.
- How to verify exports.
- How to restore data.
- How to reproduce results.
- Known limitations.
- AI transparency.

Make sure all commands work from a fresh checkout.

Do not link to absolute local filesystem paths.

Avoid overly long or promotional descriptions.

Keep wording accurate, technical and reviewer-friendly.

## 12. CLEAN CHECKOUT VERIFICATION

Create a temporary clean working copy from the intended publication content.

Do not include:

- .git history unless explicitly required for the test.
- Existing .venv.
- Private recruitment documents.
- Existing scratch databases.
- Local temporary logs.
- Machine-specific files.

From the clean copy:

1. Verify interpreter prerequisites.
2. Run package verification.
3. Restore the SQL dataset.
4. Run domain validation.
5. Run anomaly detection.
6. Evaluate detected findings against truth.
7. Run the complete automated test suite.
8. Verify required artifacts exist.
9. Confirm no network access or secret configuration is required.

Record actual commands, exit codes and outcomes.

Do not treat successful tests in the original workspace as proof of fresh-checkout success.

## 13. PERFORMANCE AND PORTABILITY

Review Python and SQLite prerequisites.

Document:

- Minimum genuinely tested versions.
- Recommended runtime.
- Exact setup commands.
- Unsupported versions.
- Any platform-dependent assumptions.
- Compression and file-system assumptions.

If Python 3.11/3.12 compatibility is not tested, do not claim compatibility.

Do not introduce broad compatibility refactors unless genuinely necessary.

Measure meaningful existing execution times.

Do not invent benchmarks.

## 14. HUMAN EXPLAIN-BACK PREPARATION

Create:

docs/phase08/interview-walkthrough.md

Prepare concise explanations for:

1. Why Python and SQLite were selected.
2. Why the database has 24 tables.
3. Master versus dependent records.
4. Deterministic IDs and seeds.
5. Lifecycle transitions.
6. Scheduling conflict prevention.
7. Transactional event history.
8. Weighted rubric scores.
9. Compensation approval policy.
10. Independent anomaly detection.
11. Why ground truth is isolated.
12. Evaluation metrics.
13. CSV/JSON/SQL reproducibility.
14. Architecture limitations and trade-offs.
15. How AI was used and verified.

Use actual source-code references.

Include 10–15 realistic reviewer questions with concise, technically accurate answers.

Do not claim this document proves the candidate understands the implementation.

## 15. MINIMAL CORRECTIONS POLICY

If you find a genuine P0 or P1 defect:

- Record the finding and evidence.
- Add a regression test first where practical.
- Make the smallest correct change.
- Avoid unrelated refactoring.
- Re-run all affected tests.
- Re-run full reproducibility if deterministic outputs change.
- Update checked-in artifacts and manifest only when genuinely required.
- Record actual old/new checksums.
- Document the correction.

Do not silently alter committed generated data or previous findings.

If an issue requires a risky architecture rewrite, report the trade-off before proceeding.

P2 improvements should not delay mandatory release readiness.

## 16. FULL TESTING

Re-run:

- Existing 208 tests.
- Dictionary consistency.
- Package manifest verification.
- Three-format restore/equivalence.
- Canonical domain validation.
- Anomaly detector.
- Ground-truth evaluator.
- Two-run full reproducibility.
- Clean checkout verification.
- Privacy/source-content audit.

Report exact commands, actual results and any failures.

No fake PASS results.

## 17. TRACEABILITY AND DOCUMENTATION

Create or update:

docs/phase08/final-requirements-audit.md
docs/phase08/interview-walkthrough.md
docs/phase08/privacy-and-publication-review.md
docs/phase08/ai-history-audit.md
docs/phase08/release-readiness-checklist.md

Preserve previous reports and original requirements.

Mark requirements as:

PASS
PARTIAL
FAIL
NOT_APPLICABLE

Separate technical readiness from human verification and release authorization.

Do not mark final publication gates complete.

## 18. GIT SAFETY

Preserve the current local repository and earlier commits.

Do not push.
Do not merge.
Do not force-push.
Do not rewrite history.
Do not publish.
Do not create a remote.
Do not submit.
Do not email recruiters.

Make only scoped audit/documentation changes and minimal necessary fixes.

Use meaningful local commits after verification.

Do not make the repository public merely because the technical tests pass.

## 19. FINAL GO/NO-GO CRITERIA

Provide separate assessments:

A. Technical requirements readiness.
B. Artifact completeness.
C. Privacy/publication safety.
D. AI-history compliance.
E. Human walkthrough readiness.
F. GitHub publication readiness.
G. Portal submission readiness.

For each:

- PASS.
- PARTIAL.
- FAIL.
- BLOCKED.

Explain each decision with evidence.

If any critical privacy or submission blocker remains, the overall release status must not be GO.

Never claim recruiter acceptance or a guaranteed score.

## 20. FINAL HANDOFF REPORT

Create:

reports/phase08-final-audit-handoff.md

Include:

1. Executive assessment.
2. Final requirement matrix summary.
3. Source code review findings.
4. Verified dataset counts.
5. Actual test outcomes.
6. Export/import results.
7. Reproducibility evidence.
8. All five anomaly results.
9. Privacy findings, including Git history.
10. Recommended publication-history strategy.
11. AI prompt-history gaps.
12. README/reviewer setup results.
13. Human walkthrough checklist.
14. Confirmed defects and corrections.
15. Remaining blockers.
16. Git working-tree and commit state.
17. Exact next steps for final public GitHub publication.
18. Final GO/NO-GO recommendation.

Make the report independently reviewable.

STOP after Phase 08 audit.

Do not publish or submit anything.

The user will review the final report and may provide the complete project ZIP for independent assessment.

The goal is a technically complete, explainable and publicly safe project—not simply another passing test report.