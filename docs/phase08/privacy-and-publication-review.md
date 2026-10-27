# Privacy, Git history and publication strategy

**Publication safety: FAIL; overall release NO-GO.** This is a local audit and
preparation, not publication permission. No history rewrite, repository creation,
remote, push, merge, submission, contact or email action was performed.

## Confirmed findings and exact scope

Initial audit base d497c20:151 tracked files,15 reachable commits,214 unique file
blobs. scripts/audit_repository_privacy.py reads every tracked current file and
all unique blobs reachable from all refs, decompresses gzip, and checks commit
messages/author/committer fields. It reports filenames, lines, blob/commit IDs and
categories without matched private values. Full safe evidence:
privacy-history-evidence.json. Updated actual scan after the minimal-fix commit:
158 tracked files,16 reachable commits,227 unique blobs; author/committer names
and email fields explicitly checked separately. The evidence records its exact
audited revision/counts. Final new files are separately staged/content reviewed.

Current tree: seven historical reports contain both private paths and embedded
user identifiers (14 category findings across seven files). History:14 flagged
blob/path versions across eight paths, including an old AGENTS.md ancestor-path
reference. Two commits contain personal author and committer names/emails:
c215e4db4f2d8552f9d1eaf368fe283f816175f4 and
4c567e7eae9302d170b85f0b2ae239a67ee35fd4. No matched address/path is copied here.
Current report paths: phase01-handoff, phase01-resumed-handoff, phase02-schema-
handoff, phase03-data-generation-handoff, phase04-interview-workflow-handoff,
phase05-evaluation-offer-handoff and phase06-anomaly-ground-truth-handoff, all
under reports/. Exact first flagged lines/versions are in the evidence JSON.

No credential/token/key, real candidate/resume, private recruitment PDF/portal
URL or unexpected binary finding was detected within this scanner's coverage.
Public employer contact addresses and explicit synthetic test examples are
allowlisted; those exceptions are documented in the script. Synthetic candidate
identities/contact policy was independently checked. Findings are not an absolute
privacy guarantee: arbitrary sensitive prose/unknown identifiers may escape
patterns. Dangling/unreachable objects/account-wide unrelated data were not an
intended publication export and are not claimed completely audited. Never copy
.git, reflogs, raw bundles, logs, existing venv or private inputs into public content.

## Strategy comparison

| Strategy | Publicly visible information | Development-history effect | AI disclosure | Privacy/reviewer trade-off |
| --- | --- | --- | --- | --- |
| A. Existing history after current-tree cleanup | Old paths/user identifiers and two author emails remain visible in historical commits; deleting/editing HEAD does not erase them | Preserves all original commits and timestamps | Could preserve prompt records, but does not fill missing ChatGPT inputs | NOT RECOMMENDED. Cannot claim privacy-safe without consent or a separately authorized history rewrite, which user currently forbids |
| B. New curated public history; original local repo preserved | Only explicitly reviewed curated tree/commits; omit .git/original private metadata, redact private paths with a transparent redaction log | Original15+ local commits preserved privately; public scope commits honestly import implementation/data/docs, without pretending to replay original development dates | Preserve all actual project prompts/decision evidence with explicit privacy redactions; add original ChatGPT prompts first | RECOMMENDED, after human review and separate creation/publication authorization. Meaningful new import scopes + a safe evolution summary give reviewers context; provenance commit hashes may reference private local history without making it public |
| C. Current-tree cleanup as preparation, defer all publication | No public data until separately authorized; old local history stays private | Minimal disruption and fully preserves local history | Complete missing prompts/disclosure locally while resolving privacy | Safe immediate course while blocked, but not itself a compliant public-repository submission; delay must respect deadline |

Recommendation: C now (remain local), then B if the user approves the reviewed
curation/history decision. No new repository or history strategy has been executed.
Do not publish existing history just because tests pass. Do not silently rewrite
old prompt text or historical reports. No permission inferred from Phase08 scope.

## Intended-content clean-copy test boundary

For the required reviewer test, an ephemeral directory outside this repository
is populated only from tracked files, without .git/history/private sources/venv/
scratch/logs. User-specific paths in historical report copies are replaced with
explicit private-path markers; a safe redaction manifest records original/new
SHA and changed line numbers, never private values. Original local files/commits
remain untouched. This is a disposable publication-content preview for testing,
not a created public repository, an approved final curation or a history rewrite.
All runtime/artifact bytes remain exact. Missing ChatGPT originals/human gates
are still missing; preview cleanliness does not make release GO.

## Required next privacy decisions

User reviews current/historical findings and strategyB; reviews every redaction
and prompt-completeness/privacy conflict; adds real ChatGPT history safely; performs
personal content/ownership review; then explicitly authorizes the chosen new
repository/history/remote/publication steps. Final content/history scans and
anonymous visibility/submission checks belong to that separately authorized
release step. No real personal data should be copied to new public history.
