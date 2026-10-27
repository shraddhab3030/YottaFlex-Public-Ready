# AI prompt-history audit and public disclosure

Status: **PARTIAL / PENDING**. User P012 explicitly confirms ChatGPT and Codex.
No original ChatGPT user-prompt transcript is available in the local repository.
A drafted phase prompt copied from a ChatGPT answer into Codex is a Codex input;
it does not recover the user prompt originally sent to ChatGPT.

## Tool inventory supported by evidence

| Tool | Actual use | Original prompt record | Limits |
| --- | --- | --- | --- |
| OpenAI ChatGPT | October2026, particularly October27: requirements interpretation, strategy/phasing, drafting Phase01–08 instructions and reviewing Phase01–07 reports | PENDING; user says conversation available in their account, no local export supplied | Report/document-based reviews; no independent full-repo inspection/application/test execution in those reviews |
| OpenAI Codex, this chat | Heavy schema/code/generator/workflow/scoring/offers/anomalies/export/tests/docs/audit generation and actual command execution | Known P001–P012 plus Q001/Q002 in journal/linked files | Available-chat record, not an account-wide raw export; exact normalization and attachment matches below |
| Other AI tools/chats | None further identified in currently available evidence | User account audit PENDING | Do not assert none were used without the user's exhaustive record confirmation |

No subagents/other human implementers were used by this Codex session. Deterministic
Python/SQLite/Git/PDF extraction tools are not additional generative AI services.
They were used locally. This does not attest to unseen account activity.

## Exactly what is preserved

- P001: complete available initial Phase01 task, whitespace normalized; not a
  byte-for-byte account-export claim. It includes report-per-task/local-only intent.
- P002: complete available source-path clarification text in journal; line wrapping
  normalized. Q001 stores the original missing-source clarification.
- P003: complete available resumed task text/attachment identity, wrapping normalized.
- P004–P007: original Phase02–05 prompt attachments stored byte-identically in
  docs/phase02–05/prompt.md, with the short human wrapper messages in journal.
- P008: complete short human follow-up `is phase5 completed? if not them complete`.
- P009/P010: complete Phase06/07 attachments, byte-identical; human wrappers recorded.
- P011: complete Phase08 attachment, byte-identical, and wrapper `here is next step`.
  SHA256 e5ca02c03207379ccc4cf01ab357d64b1fc2b2ed51c10bd8be12fc87aaf54e73.
- Q002: full current AI-tools/personal-review question in journal. P012: full user
  answer text in human-ai-disclosure.md; source is the visible conversation answer,
  not an account export. No unavailable historical text has been reconstructed.

Actual phase02–08 source-attachment byte comparisons all passed; sizes/SHA in
prompt-and-dependency-evidence.json. P001–P003 are complete normalized available
text, not partial summaries, but raw account-export fidelity cannot be attested.
There is no recovered ChatGPT user prompt, partial or full, at present. The
ChatGPT checklist is explicitly a reconstructed task checklist, never a transcript.
Historical statements about sole Codex use are superseded by the authoritative
P012 journal addendum; original prompt text/history is not silently rewritten.

## Exact missing-history checklist

See docs/ai-history/chatgpt/README.md. Recover all original ChatGPT user inputs for:
assignment/PDF interpretation; strategy/architecture/phasing; each Phase01–08
instruction drafting request; every Phase01–07 report review, gap analysis,
acceptance-criteria request, follow-up and correction. Preserve complete pasted
reports/source inputs or exact attachment references and actual ordering/chat/date
metadata. Audit other chats/tools. User reports availability but has not exported;
do not call these unavailable/lost merely because they are not locally supplied.
If records truly cannot be recovered, identify exact gaps/reasons and provide a
reasonable record with disclosed limits; do not invent verbatim content.

## Public-safe disclosure (current, accurate wording)

This project involved substantial AI assistance. ChatGPT helped interpret the
assignment, plan the phased strategy, draft implementation instructions and review
reported Codex progress. Those ChatGPT reviews did not independently execute the
application/test suite or inspect the complete source repository. Codex heavily
assisted with schema and code generation, implementation, tests, deterministic
data, local verification and documentation, including this final audit.

AI proposed Python/SQLite, explicit transaction/history design, synthetic role/
calendar/rubric/approval policies, isolated observations/truth, export encodings
and source fingerprints. The candidate provided requirements/documents, directed
phases, read completion summaries and used ChatGPT to assess reported progress.
These are project decisions/report review, not independent technical verification.
Personal tests, complete every-line review/understanding, manual workflow testing,
privacy inspection and restore/reproducibility confirmation remain unconfirmed.
Codex's actual tests are recorded as AI-run executions. Complete original ChatGPT
prompt inclusion and exhaustive other-tool inventory remain pending.

No claim is made that the candidate independently wrote all code, personally ran
Codex's checks, or has completed walkthrough readiness. Human verification and
all-tools history compliance are release gates. Responses are optional; original
user prompts are required. Private unrelated account data/system instructions/
private reasoning are not project user prompts and are not exported.
