# YOTTAFLEX AI — PHASE 07: COMPLETE DATA EXPORTS, ROUND-TRIP VERIFICATION, REPRODUCIBILITY & SUBMISSION ARTIFACTS

You are continuing our YottaFlex AI 72-Hour Code Challenge.

Phase 06 has been reviewed and conditionally approved for progression.

You are authorized to implement Phase 07 only.

HARD DEADLINE:
October 29, 2026, at 1:52:35 PM IST.

PRIMARY OBJECTIVE:
Produce a complete, portable, deterministic, independently verifiable dataset and submission artifact package.

This phase must satisfy the original assignment's CSV/JSON/SQL export, field dictionary, fixed-seed reproducibility, source manifest, validation summary and ground-truth requirements.

Do not push, publish, submit or contact recruiters. Final release remains a separate user-controlled phase.

## 1. INSPECT EVERYTHING BEFORE IMPLEMENTATION

Read:

- AGENTS.md and README.md.
- Original assignment and both official PDFs.
- All Phase 01–06 handoff reports.
- All 75 original requirements and status overlays.
- Actual SQLite schema and data dictionary.
- Data generator, scheduling, evaluation and offer modules.
- Phase 06 anomaly injection/detection/evaluation modules.
- Existing canonical serializer, reproducibility scripts and validators.
- Existing tests.
- Git status, commits and current branch.

Do not assume existing modules have particular functions or CLI options without inspecting them.

Preserve all previous behavior and deterministic identifiers.

## 2. FINAL DATASET REQUIREMENTS

FULL must contain exactly:

- 200 Requisitions.
- 5,000 Candidates.
- 8,000 Applications.
- 2,000 Interviews.

Preserve actual dependent records:

- Staff and HiringManager.
- CandidateSkill.
- SkillRequirement.
- InterviewPanel.
- PanelMember.
- Availability.
- InterviewParticipant.
- Scorecard.
- ScorecardItem.
- Offer.
- Approval.
- All implemented event-history tables.

Export every one of the existing 24 SQLite tables, including bridge and event tables.

The exported dataset must represent the completed, valid Phase 05 canonical baseline, not an accidentally corrupted anomaly projection.

The Phase 06 observed anomalies must remain separate and clearly linked to that baseline.

## 3. IMPLEMENT DETERMINISTIC CSV EXPORTS

Create a CSV file for every table.

Requirements:

- Stable filenames.
- Stable table ordering.
- Exact schema-column ordering.
- Rows sorted by declared primary keys.
- Explicit header row.
- Consistent CSV quoting/escaping.
- Deterministic UTF-8 encoding.
- No machine-dependent timestamps.
- Correct Unicode and special-character handling.
- Unambiguous representation of NULL versus empty strings.
- Exact preservation of integer monetary amounts and timestamps.
- Documented representation of booleans and JSON-object text fields.

Do not silently convert large integers to floating-point values.

Ensure CSV round-trip import can reconstruct the original types and values using the data dictionary/schema.

Do not export computed anomaly labels into normal baseline tables.

## 4. IMPLEMENT DETERMINISTIC JSON EXPORTS

Export every table to machine-readable JSON.

Requirements:

- All database columns represented.
- Correct integer, string and null types.
- Stable ordering and serialization.
- Deterministic encoding.
- No unnecessary runtime metadata mixed into row content.
- Preserve JSON-valued columns according to a documented representation policy.
- Reconstruct the exact source values during import.

CSV and JSON must encode equivalent relational records.

Do not replace required source tables with aggregate summaries.

## 5. IMPLEMENT SQL SEED EXPORT

Produce portable SQLite-compatible SQL deliverables.

Include:

- Versioned schema DDL.
- SQL seed INSERT statements for all tables.
- Safe FK-respecting insertion order.
- Proper escaping and NULL representation.
- Correct event-history insertion order.
- Required initialization metadata without conflicting schema-initializer behavior.

The SQL seed must restore the final canonical dataset into a fresh SQLite database.

IMPORTANT:
Inspect append-only triggers, SchemaMetadata and schema fingerprint validation before designing the SQL import.

Do not disable protection triggers or foreign keys casually.

If the existing schema requires a specific safe import procedure, implement and document it transparently.

Do not silently omit event history because triggers complicate imports.

Do not corrupt schema fingerprints or circumvent initialization safety.

## 6. ROUND-TRIP IMPORT VERIFICATION

Implement independent verification for all three formats.

A. CSV:
- Import into a fresh compatible database.
- Verify column types and nulls.
- Verify all rows and relationships.
- Compare canonical hashes against original.

B. JSON:
- Import into a separate fresh compatible database.
- Verify all rows.
- Compare canonical hashes against original.

C. SQL:
- Execute the seed in a fresh compatible SQLite database.
- Verify all rows.
- Compare canonical hashes against original.

Every format must reconstruct the SAME baseline records.

For each import, perform:

- PRAGMA foreign_key_check.
- SQLite integrity_check.
- Primary-key uniqueness.
- Expected table counts.
- Exact required entity counts.
- Business/domain validation.
- Event-history consistency.
- Score arithmetic reconciliation.
- Approved compensation-band reconciliation.
- Active scheduling conflict checks.
- Canonical row-by-row comparison.

Do not declare an import successful solely because the SQL command returned exit code zero.

## 7. CROSS-FORMAT EQUIVALENCE

Prove:

Original SQLite baseline == CSV-restored database
Original SQLite baseline == JSON-restored database
Original SQLite baseline == SQL-restored database

Compare all 24 tables.

Use:

- Exact row counts.
- Field-level type/value comparison.
- Stable primary-key order.
- Per-table SHA-256.
- Aggregate SHA-256.

Preserve every original ID.

Report the first differing table, primary key and field if a mismatch occurs.

No unexplained differences are acceptable.

## 8. PHASE 06 ARTIFACT PACKAGING

Include the genuine measured Phase 06 output:

- input/observations.json.
- truth/ground_truth.csv.
- truth/ground_truth.json.
- findings.json.
- evaluation.json.
- Clean validation report.
- Structural validation report.
- Relevant scenario/control evidence.

Do not regenerate different truth labels independently of the packaged inputs.

Ensure all files belong to the same seed/configuration/baseline.

Record the baseline checksum referenced by the anomaly observations.

Verify that detector execution against the packaged baseline and observations recreates the packaged findings.

Verify that evaluation against the packaged truth recreates the packaged TP/FP/FN and precision/recall/F1.

Do not give the detector access to ground truth.

## 9. DATA PROVENANCE AND SOURCE MANIFEST

Create a complete source/provenance manifest.

Include:

- Dataset profile.
- Generator version or Git commit.
- Fixed seed.
- Logical time origin.
- Schema version.
- Python/SQLite requirements.
- Configuration fingerprint.
- Synthetic-only provenance declaration.
- Record counts for every table.
- Dependencies between main entities.
- Canonical dataset checksum.
- Individual file SHA-256.
- File sizes.
- Export formats.
- Validation result references.
- Anomaly input/truth/findings references.
- Reproducibility evidence references.

State clearly:

All candidate identities and recruitment records are synthetic.

No real candidate data, scraped profiles, confidential records or external personal datasets were used.

Because external datasets are not used, do not invent URLs, licenses, retrieval dates or third-party attribution.

If public reference material or dependencies were actually used, record their genuine provenance and license information separately.

Avoid self-referential manifest hashing.

Define and document whether manifest hashes exclude the manifest itself.

## 10. DATA DICTIONARY AND SCHEMA CONSISTENCY

Preserve the existing complete dictionary.

Verify every schema field matches its documented:

- Name.
- Type.
- Required/optional status.
- Allowed values.
- Units.
- Uniqueness.
- FK/PK.
- Validation rule.
- Lifecycle semantics.

Document export/import representation where necessary, including NULL, JSON fields, currencies and epoch timestamps.

Do not manually rewrite existing dictionary data if it is already generated accurately from SQL.

Run the dictionary freshness check.

## 11. COMPLETE VALIDATION SUMMARY

Produce a final machine-readable validation report.

Include actual:

- Entity counts.
- Foreign-key violations.
- Primary-key duplicates.
- Natural-key duplicates.
- Invalid enums.
- Invalid chronology.
- Illegal stage transitions.
- Interviewer conflicts.
- Candidate scheduling conflicts.
- Incomplete required-review gate violations.
- Rubric/score arithmetic errors.
- Offer-band violations.
- Approval/history errors.
- Ground-truth leakage checks.
- Baseline and observed anomaly classifications.

Clearly distinguish:

1. Valid canonical baseline.
2. Structurally valid anomalous observations.
3. Expected semantic anomaly findings.
4. Unexpected validation failures.

Never make an anomalous projection appear fully business-valid merely to achieve a green summary.

## 12. TWO-RUN FINAL REPRODUCIBILITY

Run two independent full end-to-end generations with seed 20261022.

Each run must include:

- Complete legitimate baseline.
- All 24 relational tables.
- CSV exports.
- JSON exports.
- SQL seed.
- Phase 06 anomaly observations.
- Separate truth files.
- Findings and evaluation metrics.
- File checksums.

Compare:

- Exact table counts.
- Every canonical row.
- Per-table checksums.
- Aggregate checksum.
- CSV bytes.
- JSON bytes.
- SQL seed bytes.
- Ground truth bytes.
- Observation bytes.
- Findings and evaluation outputs.

Stable manifest sections must match.

Exclude measured elapsed time, absolute paths, temporary directory names and unrelated environment diagnostics from deterministic comparisons.

Any mismatch must be investigated and documented rather than ignored.

## 13. PERFORMANCE AND RESOURCE USAGE

Measure:

- Complete baseline generation.
- CSV export.
- JSON export.
- SQL export.
- Each independent import.
- Validation.
- Anomaly evaluation.
- Total end-to-end execution.

Use actual measurements.

Do not fabricate performance statistics or claim external benchmark results.

The required scale is modest; prefer simple streaming/batched operations and standard library tools.

Do not introduce cloud services, paid dependencies, data warehouses or unnecessary frameworks.

## 14. REVIEWER EXPERIENCE

A reviewer should be able to clone the repository and follow straightforward commands to:

1. Create a local Python environment.
2. Initialize/generate the dataset.
3. Run tests.
4. Export all formats.
5. Restore at least one format.
6. Validate imported data.
7. Run anomaly detection.
8. Compare findings to ground truth.
9. Inspect reproducibility evidence.

Document exact tested commands.

Prefer a small cohesive CLI over numerous undocumented scripts.

Preserve existing CLI commands; extend only where necessary.

Make failures actionable with clear error messages and nonzero exit codes.

Avoid requiring internet access after cloning.

## 15. GENERATED ARTIFACT DIRECTORY

Create a clearly identifiable tracked directory such as:

artifacts/
  baseline/
    csv/
    json/
    sql/
    validation-summary.json
  anomalies/
    input/
    truth/
    reports/
  manifest.json

The exact layout may be refined to fit existing conventions.

CRITICAL:

The final public repository must contain all problem-statement-required generated artifacts, not only code that could theoretically create them.

Current .gitignore excludes generated data locations. Do not mistakenly leave mandatory deliverables ignored.

Make the reviewed synthetic CSV/JSON/SQL/ground-truth artifacts intentionally trackable under artifacts/.

Do not indiscriminately unignore scratch SQLite files or private documents.

Check the total artifact size before committing.

If any required artifact is unusually large, report the measured size and choose a lossless, clearly documented distribution method within the single GitHub repository.

Do not substitute untracked local files or external hosting for required deliverables.

## 16. PRIVACY AND PUBLICATION SAFETY

Before staging artifacts:

- Scan for credentials and tokens.
- Scan for private local filesystem paths.
- Verify synthetic email domains and identities.
- Verify no actual candidate resumes/contacts.
- Verify no private recruitment PDFs.
- Verify no personal application links or identifiers.
- Check tracked and newly generated files.
- Check large unexpected binaries.
- Confirm source data lawful provenance.

Do not claim a scanner guarantees absolute privacy.

Report any suspicious file requiring human review.

## 17. TEST COVERAGE

Add automated tests for:

1. All 24 tables exported.
2. Exact headers and fields.
3. Stable row ordering.
4. Null/string distinction.
5. Unicode and CSV escaping.
6. JSON type preservation.
7. Large integer preservation.
8. SQLite-compatible SQL escaping.
9. Fresh SQL import.
10. Fresh CSV import.
11. Fresh JSON import.
12. PK/FK integrity after imports.
13. Source/restored row equality.
14. Per-table hash equality.
15. Aggregate hash equality.
16. Exact required entity volumes.
17. Event history preservation.
18. Score/offer reconciliation after import.
19. Anomaly input/ground-truth consistency.
20. Detector does not read truth.
21. Packaged detector reproduces findings.
22. Packaged evaluator reproduces metrics.
23. Two-run complete reproducibility.
24. Manifest correctness and file hashes.
25. No private sources/secrets.
26. Refusal to overwrite existing files unsafely.
27. Interrupted/failed export cleanup.
28. Invalid/corrupted import rejection.
29. All 183 existing tests remain passing.

Add practical additional tests where necessary.

Do not hardcode success results.

## 18. DOCUMENTATION

Create:

docs/phase07/export-and-reproducibility-design.md

Document:

- Export architecture.
- File-format encoding.
- Null/JSON handling.
- Dependency-based import order.
- SQL seed restoration.
- Checksum algorithm.
- Full schema/row equivalence.
- Manifest specification.
- Synthetic provenance.
- Full-data generation commands.
- Validation commands.
- Anomaly evaluation commands.
- Performance results.
- Known limitations.
- Reproduction instructions.

Update README with a simple QUICK START.

The README should explain the entire project in understandable language:

- Business problem.
- Solution overview.
- Architecture.
- All eleven core entities.
- Full dataset volumes.
- Business rules.
- Five negative cases.
- Why ground truth is separate.
- How to execute and test.
- How to regenerate.
- How to interpret results.
- AI-assisted development disclosure.
- Design trade-offs and limitations.

Do not falsely claim human testing or review.

## 19. AI PROMPT HISTORY

Preserve this complete Phase 07 prompt verbatim.

Preserve all previous user prompts.

Record any additional AI prompts used.

Keep history of:

- AI-generated work.
- Human-provided requirements.
- Human-confirmed decisions.
- AI-run tests.
- Human tests still pending.

Do not mark the user's independent verification complete without evidence.

## 20. REQUIREMENTS TRACEABILITY

Update the existing 75-row requirement matrix.

Each mandatory item should have:

- Current implementation status.
- Relevant source file.
- Test or validation evidence.
- Documentation or artifact reference.
- Remaining limitation, if any.

Do not delete or rewrite the original requirement text.

Do not mark a requirement satisfied merely because the README claims it.

Explicitly report any remaining incomplete acceptance criterion.

## 21. GIT AND CHANGE MANAGEMENT

Preserve current branch and prior commits.

Do not push, merge, configure remotes, publish or submit.

Make only Phase 07-related changes.

Do not refactor validated business logic without a real demonstrated defect.

Commit generated safe artifacts intentionally, not scratch files.

Review staged files, file sizes and privacy checks before committing.

Use meaningful scoped local commits.

Run all relevant tests and full replay against final code before reporting PASS.

## 22. PHASE 07 ACCEPTANCE CRITERIA

Phase 07 is PASS only if:

- The original valid dataset remains correct.
- All four mandatory full counts remain exact.
- Every table is exported to CSV and JSON.
- A complete SQL seed export exists.
- CSV imports reproduce source data.
- JSON imports reproduce source data.
- SQL imports reproduce source data.
- All imported IDs and joins are correct.
- Source/imported canonical hashes match.
- Historical events are retained and valid.
- Score/offer arithmetic still reconciles.
- Five mandatory anomalies are packaged separately.
- Ground truth CSV and JSON are included.
- Detector outputs and metrics reproduce from packaged inputs.
- Source manifest is complete.
- Documentation/dictionary is current.
- Two full end-to-end independent runs match deterministically.
- Mandatory generated artifacts are included in the repository.
- All previous tests remain green.
- New export tests pass.
- No private or unsafe files are committed.
- No optional UI or publication work was substituted for required exports.

## 23. FINAL HANDOFF

Create:

reports/phase07-export-deliverables-handoff.md

Include:

1. Phase 07 PASS/PARTIAL/FAIL.
2. Exact files created and modified.
3. Complete artifact file inventory.
4. Artifact sizes.
5. All 24 table counts.
6. CSV/JSON/SQL export evidence.
7. Independent import test results.
8. Canonical source-versus-imported hashes.
9. Anomaly package content.
10. Truth/detection/metrics reconciliation.
11. Two-run full reproducibility checksums.
12. Manifest verification.
13. Actual test commands and results.
14. Validation results.
15. Performance measurements.
16. Source and privacy checks.
17. Updated 75-requirement coverage summary.
18. AI-use and human-review status.
19. Remaining issues and risks.
20. Local Git commits and working-tree status.
21. Final Phase 08 audit recommendations.

The handoff must be self-contained and detailed enough for independent project evaluation in another ChatGPT conversation.

STOP after Phase 07.

DO NOT push to GitHub, configure a public remote, submit to the portal, contact recruiters or perform final publication without explicit separate user authorization.

The goal is an independently runnable, reproducible and auditable submission package, not just successful local generation.