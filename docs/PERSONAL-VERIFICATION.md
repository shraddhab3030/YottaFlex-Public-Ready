# Personal verification — candidate execution remains unconfirmed

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
export PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
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
python3 scripts/audit_repository_privacy.py --output "$PREP_WORK/work/personal-privacy-review.json"
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
- [ ] Personally confirm public access and approve any later commit/push or submission action.

This repository now has its own .git and origin. Verify the Git root before
repository commands; no history/remote change is part of personal verification.
The Git-aware privacy audit above scans tracked files/history and reports findings.
Its conservative metadata policy may flag public author names/email: inspect every
finding and explicitly decide whether exposure is intentional; exit0 is not a
privacy PASS. The Git-free audit_publication_candidate.py instead targets an
export without .git/local scratch and would flag .git in this checkout. Private
assignment inputs remain excluded; the maintainer foundation smoke is not a
reviewer runtime prerequisite. No personal-review checkbox is signed by Codex.

## Inspect actual restored records

After the commands above, run this against the new SQL restore. It opens read-only
and prints actual counts and the first accepted-offer application history.

```sh
python3 - "$PREP_WORK/work/sql.sqlite3" <<'PYCODE'
import sqlite3,sys
from pathlib import Path
with sqlite3.connect(Path(sys.argv[1]).resolve().as_uri()+'?mode=ro',uri=True) as db:
    for table in ('Requisition','Candidate','Application','Interview'):
        print(table, db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
    identity=db.execute("SELECT application_id FROM Offer WHERE status='accepted' ORDER BY offer_id LIMIT 1").fetchone()[0]
    print('Application', identity)
    for row in db.execute('SELECT sequence,previous_status,new_status,actor_staff_id,occurred_at FROM ApplicationEvent WHERE application_id=? ORDER BY sequence',(identity,)):
        print(row)
PYCODE
```

Expected counts: 200 / 5000 / 8000 / 2000. For the fixed package the chain is
APP-CAND-000031-REQ-2026-000147; it reaches hired through applied, screening,
interviewing, reviewed and offer. Same-stage audit events can occur. Open the
new personal-data-review.json: inspect successful_path Requisition/Interview/Offer/
Approval histories and submitted scorecards, independent_sql zero arithmetic/
band errors, all 30 independently_checked_truth_issues, and seven actual rejected
operations (including two reviewer-specific irrelevant-criterion rejections).
Expected rejection codes include INTERVIEWER_CONFLICT, REVIEW_GATE_INCOMPLETE,
IRRELEVANT_CRITERION, OFFER_OUTSIDE_BAND, SELF_APPROVAL_FORBIDDEN and APPLICATION_WITHDRAWN;
all_rows_unchanged must be true. These execute isolated temporary operations and
do not modify the canonical database. Explain why each rule rejected the action.

- [ ] Run all 211 tests; investigate any failure rather than copying expected output.
- [ ] Verify all 68 artifacts and three restorations; inspect real SQL counts above.
- [ ] Follow one approved requisition through its candidate/application to hired.
- [ ] Inspect schedules and actual conflict rejection; explain half-open intervals.
- [ ] Recompute one scorecard from item weights; inspect independent offer approval.
- [ ] Run the detector without truth; then compare against separate CSV/JSON truth.
- [ ] Read src/yottaflex/schema.sql, db.py, workflow.py, evaluation.py, offers.py,
  generate.py, detector.py, observations.py, anomaly_evaluation.py and exports.py;
  inspect pyproject.toml and all remaining source/test lines and policy assumptions.
- [ ] Inspect every intended public file, expanded artifacts and Git metadata.
- [ ] Explain ChatGPT/Codex contributions and distinguish your decisions from AI checks.

Record date, actual commands/output and what you personally changed/reviewed.
Do not tick items merely because Codex ran the same command. Use the
[five-minute demonstration guide](final-submission/FIVE-MINUTE-DEMO.md) after study.
