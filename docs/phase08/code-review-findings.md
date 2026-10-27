# Final source review — confirmed findings and boundaries

Audit source base: d497c20; all runtime modules/tests/scripts and schema inspected,
with AST/DDL/field inventory and actual independent execution. Same Codex agent,
not a separate human assessor or external penetration test. No subagents used.
Original sources, prior reports/prompts and all75 original requirement rows stay
preserved. Review metadata is in inspection-inventory.json; numerical evidence
comes from new executions, not prior PASS claims.

## P1-01 — confirmed archive build/test failure, corrected

Original src/yottaflex/deliverables.py:162 unconditionally ran git rev-parse HEAD.
A Git archive outside any repository, no private files or existing venv, failed
PackageTests.setUpClass. Actual201 tests ran91.889s; errors1; seven package tests
were not executed because class setup failed. Original workspace208 tests passed
97.424s. The old Phase07 archive was nested inside the development repository
and only package verification was run there, so it did not expose this dependency.

Regression-first: tests/test_audit_regressions.py ran3 tests before the fix,
errors3 in1.050s. One reproduces real package build without Git; two cover an
unrelated ancestor repository and missing Git executable. Corrected14 lines in
deliverables.py: optional source_revision verifies Git root equals code root;
errors/unavailable Git return null; a stable aggregate generator_source_sha256
always identifies actual runtime source files. Verification checks that hash.
No stale package commit is impersonated and no unrelated Git revision is claimed.
No Git repository is created as a workaround. Source archive manifests legitimately
have null generator_git_commit; repository builds retain actual local revision.

Focused3 tests passed1.469s after correction. Full211 tests passed95.085s before
final full replay. Final clean-copy/package/replay evidence is in the handoff.
No business-policy/schema/canonical-row changes. Manifest/code provenance changes
require regenerated artifacts; all old/new hashes are recorded transparently.

## P1-02 — stale final dictionary narrative, corrected

Original scripts/build_data_dictionary.py HEADER (lines40–76) described implemented
workflow rules as future work and stated no anomaly fixtures/detector existed.
The freshness test could pass because it checks generated dictionary equality,
not narrative truth. Corrected only the generated narrative to identify current
runtime gates and isolated anomaly engine; no field/constraint/DDL rows changed.
Regenerated docs/data-dictionary.md and package copy. Schema SHA and baseline
canonical SHA remain unchanged. Existing structural/dictionary test and --check
actually rerun; this is a documentation correction, not a data/schema migration.

## P0-PRIV — confirmed public-release blocker, not silently corrected

Current seven reports contain user-specific paths. History additionally contains
an old AGENTS.md private ancestor path,14 flagged blob/path versions across eight
paths, and personal author/committer names and emails in two commits. See privacy-history-evidence.json
for safe locations, commits/lines; matched values are never copied into new files.
No secret/token/real-candidate finding was detected by this scan; that is not an
absolute security guarantee. User explicitly forbids history rewriting/repository
creation. Existing history remains private/local. StrategyB is recommended only;
no deletion/redaction/history rewrite/publication was executed.

## P0-HISTORY / P0-HUMAN — confirmed release gates

User P012 confirms ChatGPT use and no local complete verbatim export, plus
unconfirmed personal tests/line understanding. Original reports' broad sole-AI
claims are corrected by an authoritative journal addendum and current README,
not by altering the original prompt records. A checklist is not a recovered
transcript. No automatic human signoff or final GO is claimed.

## P2 observations — documented, no feature/refactor work

Dense formatting in newer small modules raises review effort. JSON import loads
one table; publication locks coordinate cooperative processes but do not promise
a hostile filesystem boundary. SQL seed is trusted reviewed input; hashes do not
prove publisher authenticity. Legacy master/configuration editing and advanced
withdrawal/correction policies remain explicitly limited. These are not newly
confirmed integrity failures at required scale; no speculative rewrite made.
Phase07 prose implying R02 count10 is for both affected interviews was imprecise:
there are five overlapping pairs and two shared Staff per pair, hence10 distinct
staff-specific issues. Current audit records actual pair/staff evidence.

## Review conclusions by concern

- Relational keys/joins/STRICT/checks: source DDL, all FK tests and restored data.
- Injection: values use bound parameters; dynamic table/column identifiers come
  from actual verified schema/internal constants or strict observation allowlists.
  Arbitrary SQL seed execution is a documented trusted-content operation.
- Transactions: BEGIN IMMEDIATE before read/check/write, no executescript inside
  production mutation transactions; explicit rollback and injected failure tests.
- History: append-only/no-replace triggers and full old/new snapshots; independent
  chronology/projection/source arithmetic validation, actual successful chain.
- Scheduling: half-open intervals; every shared Staff/candidate checked under
  writer lock; actual two-writer race regression. Cancelled intervals release slots.
- Stage/approval: actual completed assigned reviews, source-derived thresholds,
  distinct HR/admin approver and current approved band snapshot. No truth inputs.
- Determinism: explicit seeded Random instances, logical epochs and stable sorted
  IDs/rows; no wall-clock values in canonical records. Fresh full replay required.
- Detector: transitive AST dependency graph excludes truth/injection/evaluator;
  poisoned-label/serialization-order tests and independent SQL check of30 issues.
- Metrics: identity keyed TP/FP/FN, duplicates count FP; undefined denominators
  null; no TN/accuracy universe or real-world generalization claim.
- IO: fresh-output refusal, exclusive hard-link publication, owned cleanup,
  actual codec/corruption/failure tests; no confirmed overwrite/data-loss defect.
- Dependencies/runtime: stdlib only; pinned actually tested interpreter, no cloud,
  external dataset, credentials or network service needed. No broad compatibility
  promise for untested operating systems/interpreters.

Additional actual audit checkpoints: extending Git-field scanning initially passed
str to the byte scanner and raised AttributeError; UTF8 conversion corrected it
and a complete16-commit/227-blob rerun succeeded. The first temporary curation
preview was rejected for a remaining home path without trailing slash; copy-only
redaction was broadened and rescanned before successful clean reviewer commands.
These failed audit checkpoints are recorded in pre-correction-evidence.json, not
reported as application failures or hidden as green tests.
