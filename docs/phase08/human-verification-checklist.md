> Publication-candidate note: personal checks remain unsigned. For commands that
> work before Git initialization and keep scratch outside this directory, use
> ../PERSONAL-VERIFICATION.md. The historical Git-history command below requires
> an explicitly initialized repository and is not part of current preparation.

# Candidate's personal verification — ALL PENDING

Codex executed the technical evidence. This checklist does not transfer those
checks to the candidate. User P012 confirms report reading/progression decisions,
not independent source/test/privacy verification. Leave boxes unchecked until
personally performed; record date, command, exit code, observed hash and any issue.
Use a new output path each time. No publication/submission/contact in these steps.

## Execute locally

```sh
python3 --version
python3 -m venv .venv
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/human-review
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format sql --database output/human-restored.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.evaluation_checks --database output/human-restored.sqlite3 --profile full --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/human-restored.sqlite3 --observations artifacts/anomalies/input/observations.json
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables evaluate --database output/human-restored.sqlite3 --directory artifacts/anomalies
PYTHONPATH=src .venv/bin/python3 scripts/audit_dataset.py --database output/human-restored.sqlite3 --observations artifacts/anomalies/input/observations.json --truth artifacts/anomalies/truth/ground_truth.json --output output/human-dataset-audit.json
PYTHONPATH=src .venv/bin/python3 scripts/verify_deliverable_reproducibility.py --profile full --seed 20261022 --directory output/human-replay
PYTHONPATH=src .venv/bin/python3 scripts/audit_repository_privacy.py --output output/human-privacy-review.json
```

- [ ] Confirm Python3.14.5 and SQLite3.53.1 tested runtime; do not assume3.11/3.12.
- [ ] Personally run211 tests and inspect failures/warnings rather than copying
  Codex's result. Count includes208 original tests plus3 audit regressions.
- [ ] Personally restore/validate/compare all formats and inspect canonical hash
  7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb.
- [ ] Personally regenerate two FULL packages; inspect records/bytes/hashes.
- [ ] Inspect one actual approved-role→hired chain and blocked operations in the
  SQL audit output; explain the actor/timing/arithmetic/rollback evidence.
- [ ] Inspect original anomaly before/after rows and related IDs, five rules,
 30TP/0FP/0FN controlled results and zero clean findings. Explain limits.

## Read and explain

- [ ] Read every implementation file and dependency, schema, all75 requirements,
  current audit findings, tests and unsupported-policy limitations.
- [ ] Explain transactions, scheduling, required reviews, weighted arithmetic,
  independent approval and isolated truth without relying on this checklist.
- [ ] Complete interview-walkthrough.md questions with source navigation.
- [ ] Agree or challenge AI-proposed synthetic policies; record actual changes
  and rerun affected verification if changing behavior/data.

## Privacy, history and AI records

- [ ] Personally inspect all intended public content, current tree and Git metadata/
  historical blobs; understand why a clean current file alone does not clean history.
- [ ] Choose/explicitly authorize a publication-history strategy after reviewing
  privacy-and-publication-review.md. Nothing has been rewritten or published.
- [ ] Add actual original ChatGPT user prompts per docs/ai-history/chatgpt/README.md.
  Disclose exact unavailable records/redactions; never relabel summaries as originals.
- [ ] Audit other tools/chats and confirm a truthful complete inventory or list gaps.
- [ ] Record what you personally reviewed/changed/tested in the AI disclosure.

## Administrative gates — require later separate authorization

- [ ] Verify original invitation send timestamp/timezone/window and actual round.
- [ ] Confirm authenticated final submission instructions/channel and once-final
  rule; keep supplied deadline October29,2026,13:52:35 IST.
- [ ] Review release-readiness-checklist.md and resolve all P0 blockers.
- [ ] Explicitly authorize any later repository creation/history strategy/public
  remote/push/visibility check/submission/email action individually within scope.

No item above is marked complete by creating this file or passing an AI-run test.
