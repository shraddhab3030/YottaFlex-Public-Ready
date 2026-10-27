# Personal application testing — not yet performed by the candidate

All recorded automatic results were executed by Codex. Leave the checks below
pending until you personally run/inspect them. Run from YottaFlex-Public-Ready.
Use CPython3.14.5; SQLite3.53.1 is the genuinely tested build. Other versions and
platforms need their own verification. No API keys/pip downloads/service needed.
The application is a local CLI, not a browser UI; send_offer is a local state only.

Keep environment/results outside this publication tree:

```sh
python3 --version
PREP_WORK=$(mktemp -d /private/tmp/yottaflex-personal.XXXXXX)
python3 -m venv "$PREP_WORK/venv"
export PATH="$PREP_WORK/venv/bin:$PATH"
export PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1
mkdir "$PREP_WORK/work"
python3 -m unittest discover -s tests -v
python3 scripts/build_data_dictionary.py --check
python3 -m yottaflex.deliverables verify --directory artifacts --work "$PREP_WORK/work/package-check"
python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format csv --database "$PREP_WORK/work/csv.sqlite3"
python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format json --database "$PREP_WORK/work/json.sqlite3"
python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format sql --database "$PREP_WORK/work/sql.sqlite3"
python3 -m yottaflex.evaluation_checks --database "$PREP_WORK/work/sql.sqlite3" --profile full --seed 20261022
python3 -m yottaflex.detector --database "$PREP_WORK/work/sql.sqlite3" --observations artifacts/anomalies/input/observations.json
python3 -m yottaflex.deliverables evaluate --database "$PREP_WORK/work/sql.sqlite3" --directory artifacts/anomalies
python3 scripts/audit_dataset.py --database "$PREP_WORK/work/sql.sqlite3" --observations artifacts/anomalies/input/observations.json --truth artifacts/anomalies/truth/ground_truth.json --output "$PREP_WORK/work/personal-data-review.json"
python3 scripts/audit_publication_candidate.py --output "$PREP_WORK/work/personal-privacy-review.json"
```

Every output path must be new. Expected canonical hash:
7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb.
Expected mandatory counts200/5000/8000/2000,24 tables/89575 records;211 tests.
Controlled anomalies30TP/0FP/0FN across5 types; clean0 findings. These are expected
reference results, not claims you have personally reproduced them. Inspect actual
output and investigate any mismatch. Source/dictionary/artifact bytes should stay
unchanged. Use the stored successful chain/rejected-operation evidence to study
actor/time/rubric/band/history behavior; see phase08/interview-walkthrough.md.

- [ ] Personally execute and save actual commands/exit codes/results/date.
- [ ] Inspect all3 restores, counts/joins/hashes/events and actual anomaly inputs.
- [ ] Review every implementation line/dependency/policy; explain decisions/limits.
- [ ] Review this candidate's privacy/redaction inventory and intended public files.
- [ ] Add original ChatGPT prompts; confirm the complete tools/chats inventory.
- [ ] Decide license/redistribution status and confirm official submission process.
- [ ] Explicitly approve any later Git initialization/remote/push/visibility actions.

No .git exists in this directory. Avoid Git commands here until separate approval:
Git could otherwise discover an unrelated ancestor. The historic Git-history
scanner and maintainer source smoke are repository/private-input tools, not the
Git-free filesystem scan above. No personal-review checkbox is signed by Codex.
