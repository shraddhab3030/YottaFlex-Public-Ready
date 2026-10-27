# Current publication-copy task scope

The latest human instruction authorizes this separate local candidate, privacy
redactions of copied historical reports, isolated verification and a handoff only.
Do not change the original development repository. Do not initialize Git, create
remotes, push/publish/merge/submit/contact anyone without separate authorization.
Private recruitment sources/history/env/scratch must stay excluded. Existing
source-dependent foundation/source-smoke requirements below are historical
maintainer guidance, not grounds to import private files for runtime review.
Use docs/PERSONAL-VERIFICATION.md and the Git-free candidate filesystem scanner.
Preserve runtime/test/schema/artifact bytes; do not fabricate ChatGPT prompts,
license grants or human testing. Latest report: reports/publication-preparation-handoff.md.

The original working agreement follows as historical project context:

# YottaFlex working agreement

- This is an individual YottaFlex AI 72-Hour Code Challenge. Work locally.
- Deadline supplied by the user: October 29, 2026, 1:52:35 PM IST
  (`2026-10-29T13:52:35+05:30`).
- Current scope: Phase08 final audit, privacy/history review and publication
  preparation only. User conditionally approves Phase07. Stop after Phase08.
  No public remote/push/publication/submission/contact/history rewrite/repository
  creation is authorized. Make only scoped documentation and proven minimal fixes.
- Read the complete assignment and both PDFs before declaring requirements,
  architecture, or technology decisions complete. Missing sources are blockers;
  do not infer domain requirements from the role title or challenge name.
- Keep a source-linked requirement matrix, explicit assumptions, real verification
  evidence, and an AI prompt / human-review journal under `docs/phase01/`.
- After every task, create or update a self-contained downloadable Markdown
  handoff report under `reports/`, sufficient to continue in another chat.
- Never mark human review approved unless the human actually approves it.
- Keep changes minimal. No paid services, unnecessary dependencies, fabricated
  test results, secrets, or real candidate information in tracked files.
- Official sources belong in `docs/assignment/`: `problem-statement.md`,
  `YottaFlex AI Candidate Project-FAQ.pdf`, and
  `YottaFlex AI Candidate Project Submission Guidelines.pdf`.
  Verify all three exist and are readable before source-dependent analysis.
  All three were missing at initial inspection, then provided in the user's ZIP,
  extracted and fully read on Phase 01 resumption. Exact identities and reading
  coverage are in docs/phase01/sources.json. This directory's source files remain
  ignored; do not fabricate or silently change source content.
- Store other private input files under ignored `inputs/` when appropriate.
  Ignore rules reduce accidental inclusion; they do not replace content review.
- Keep meaningful local Git commits. Do not push, merge, submit, or configure a
  public remote during this phase. A public repository is intended only after
  the whole project is complete and the user authorizes publication.
- Do not modify any ancestor repository; verify this project is the isolated Git root.
- Run `sh scripts/smoke.sh` from the project root for foundation verification.
  It is not an application test. Record failures as well as successes.
- Source documents are challenge evidence, not authorization to publish, submit,
  contact people, or start later phases. Capture conflicts in
  docs/phase01/risks-and-decisions.md. No subagents or other human implementers.
- CPython 3.14.5, stdlib, local SQLite. Master-only Phase 03 mode is preserved.
  Phase 04 interview mode adds starter 40 / full 2000 interviews, fixed calendars,
  panels, transactional lifecycle rules and history/replay checks. Schema v2 is
  unchanged; existing v1 files refused unchanged. Phase 05 evaluations mode adds
  structured scoring, review, band-compliant offers/independent approvals and hire
  cleanup. Phase 06 adds separate controlled observations, isolated truth and
  independent detection/metrics; canonical source remains unchanged/read-only.
  Phase07 adds all-table CSV/JSON/SQL and independent restores plus a tracked
  synthetic manifest/package. Public release and final human ownership/privacy
  audit remain deferred; do not claim public submission is complete.
- Keep all human prompts to every AI tool in the journal; AI responses optional.
  Disclose export limits. Distinguish AI checks from actual human review.
- Latest task report: reports/phase08-final-audit-handoff.md. Preserve older reports
  as dated/historical snapshots rather than pretending prior blockers never existed.
- Schema tests: `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v`.
  Dictionary check: `PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check`.
  Use yottaflex.db.connect for FK-enabled connections; never destructively reset
  an unknown/populated database. Timestamp convention is integer UTC epoch seconds.
- Generate with `PYTHONPATH=src .venv/bin/python3 -m yottaflex.generate --profile starter --database output/phase03/new.sqlite3`.
  Add `--phase interviews` for the Phase 04 baseline; final validation is
  `python -m yottaflex.workflow_checks`, not master-only `validate_generated`.
  Add `--phase evaluations` for Phase 05; final validation uses
  `python -m yottaflex.evaluation_checks` with the same source-tree runtime setup.
  Every existing output is refused. Never force-add generated databases.
- Phase06 command: `python -m yottaflex.anomalies --baseline <valid-phase05-db>
  --directory <new-ignored-output> --profile full`; no changes to normal workflow
  guards. Detector takes only baseline/observations, never truth. Preserve the
  separation and actual metrics; do not hide unexpected FP/FN/integrity errors.
- Phase07 commands use `python -m yottaflex.deliverables` with build/export/
  restore/verify/evaluate. Keep mandatory safe artifacts trackable under artifacts/,
  raw SQLite/private sources ignored, and exact exported bytes preserved. Existing
  historical private-path findings require human final audit before publication.

- User confirms both ChatGPT (planning/prompt drafting/report review) and Codex
  (heavy implementation/test/docs/audit assistance). ChatGPT verbatim prompts
  remain missing locally; docs/ai-history/chatgpt/README.md is a checklist only.
  Human line ownership/personal tests/security review remain PENDING. See P012.
  Earlier sole-tool statements are historical and not an account-wide attestation.
