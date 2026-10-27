#!/bin/sh
# Phase 01 foundation verification; no challenge functionality tested.
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$project_root"

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }
pass() { printf 'PASS: %s\n' "$1"; }

actual_root=$(git rev-parse --show-toplevel)
[ "$actual_root" = "$project_root" ] || fail 'Git root is not this project'
pass 'isolated project Git root'

for path in README.md AGENTS.md .gitignore .gitattributes \
    docs/phase01/requirements.md docs/phase01/architecture.md \
    docs/phase01/journal.md docs/phase01/model.md docs/phase01/sources.json \
    docs/phase01/risks-and-decisions.md .python-version pyproject.toml \
    scripts/check_foundation.py reports/phase01-resumed-handoff.md; do
    [ -s "$path" ] || fail "missing or empty foundation file: $path"
done
pass 'required foundation documents exist'

for path in inputs/private-source.pdf 'docs/assignment/problem-statement.md' \
    'docs/assignment/YottaFlex AI Candidate Project-FAQ.pdf' \
    'docs/assignment/YottaFlex AI Candidate Project Submission Guidelines.pdf' \
    data/private-record.csv output/generated.txt \
    tmp/probe.txt .env .env.local .venv/probe node_modules/probe secret.pem local.sqlite3; do
    git check-ignore -q -- "$path" || fail "private/generated path is not ignored: $path"
done
if git check-ignore -q -- .env.example; then
    fail '.env.example should remain trackable'
fi
pass 'private inputs, common credentials, and generated paths are ignored'

# Exercise local IO while keeping generated material outside tracked paths.
mkdir -p tmp
smoke_dir=$(mktemp -d "$project_root/tmp/smoke.XXXXXX")
trap 'rm -f "$smoke_dir/input.txt" "$smoke_dir/output.txt"; rmdir "$smoke_dir"' EXIT
printf 'foundation smoke fixture: synthetic\n' > "$smoke_dir/input.txt"
cat "$smoke_dir/input.txt" > "$smoke_dir/output.txt"
cmp -s "$smoke_dir/input.txt" "$smoke_dir/output.txt" || fail 'local IO round-trip mismatch'
pass 'synthetic local write/read round-trip'

python_bin=${PYTHON_BIN:-python3}
"$python_bin" "$project_root/scripts/check_foundation.py"
printf 'Foundation smoke passed: 4 shell checks + 3 Python groups. Application checks remain pending.\n'
