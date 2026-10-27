# Future publishing commands — NOT EXECUTED / NOT AUTHORIZED NOW

First personally review/test this candidate, add complete available original
ChatGPT user prompts with privacy review, confirm tools inventory, decide project
license/redistribution status, and confirm official challenge deadline/channel.
Read reports/publication-preparation-handoff.md and resolve every stated gate.
Do not run Git commands here before separate initialization approval: Git may
otherwise discover an unrelated ancestor repository. Never point a Git remote
at the private original project or copy its .git/history/bundles/reflogs here.

## After explicit permission to initialize a new local repository

Choose/approve public name/email and branch before these commands. Variables
below are placeholders to supply after approval, not real credentials or defaults.
A reviewed GitHub noreply email may avoid disclosing a personal email; do not
inherit the original machine/global Git identity without review. Commands use
candidate-local config only and never change the original repository.

```sh
test "$(basename "$PWD")" = YottaFlex-Public-Ready
test ! -e .git
# Proposed branch main; user may choose another before initialization.
git init --initial-branch=main .
test "$(git rev-parse --show-toplevel)" = "$PWD"
: "${APPROVED_PUBLIC_NAME:?Set the reviewed public name first}"
: "${APPROVED_PUBLIC_EMAIL:?Set the reviewed public email first}"
git config --local user.useConfigOnly true
git config --local user.name "$APPROVED_PUBLIC_NAME"
git config --local user.email "$APPROVED_PUBLIC_EMAIL"
git add -- .gitattributes .gitignore .python-version AGENTS.md README.md pyproject.toml src tests scripts artifacts docs reports
git diff --cached --stat
git diff --cached --name-only
```

Before commit: inspect every staged file and approved public identity, verify68
artifacts/manifest and privacy, ensure no private inputs/local environment/results.
Do not stage raw account exports or unrelated chats. Recorded prompts retain
source fidelity; intentional original whitespace is not automatically rewritten.
Do not forge original development timestamps or claim imported code is newly
handwritten. An honest initial import plus preserved/redacted phase evidence is
more accurate than fabricated historical commits. The original local development
repo/history remains private and unchanged.

Only after reviewed staging and metadata approval:

```sh
git commit -m "chore: import reviewed YottaFlex publication candidate"
git status --porcelain
git remote -v
```

No remote should exist yet. Source provenance commit hashes refer to the private
original runtime snapshot; all actual source/artifact SHA values remain verifiable.
Historical audit reports still describe that earlier private repository, not a
claim those old personal values were copied into this new history.

## After separate permission to create/push the public GitHub repository

Create/approve the exact user-owned empty repository URL and visibility through
the user's chosen GitHub workflow. No repository name/owner/URL is invented here.
Then, only with explicit remote/push authorization:

```sh
: "${APPROVED_GITHUB_URL:?Set the reviewed user-owned repository URL first}"
git remote add origin "$APPROVED_GITHUB_URL"
git remote -v
git push -u origin main
```

Do not use force push or attach/push the private original history. After separate
visibility-check approval, verify anonymous/private-browser access and a fresh
clone/run; keep repository available/editable through the supplied deadline.
Portal submission/email/recruiter contact remain separately authorized actions.
This preparation performs none of them and claims no recruiter acceptance.
