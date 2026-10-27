> Publication-copy notice: private home-path identifiers are replaced by `<private-home>/`. Technical results remain historical evidence. Every redaction is logged in docs/publication-preparation/redaction-log.json; the original private report/history is unchanged.

# YottaFlex Phase 03 - deterministic generation handoff

**Assessment: PASS for Phase 03. Human review is PENDING; Phase 04 unstarted.**
This is a valid master/requisition-approval/candidate/application baseline, NOT
completion of the full recruitment dataset or end-to-end challenge.

## Executive context for a new chat

Individual Associate AI Forward Deployed Engineer 72-hour challenge. Root:
<private-home>/Documents/Personal/Projects/Assignment/YottaFlex.
Deadline: October 29, 2026, 1:52:35 PM IST (2026-10-29T13:52:35+05:30).
User's complete Phase 03 prompt explicitly approves Phase 02 progression.
Continue existing branch codex/phase-01-foundation, preserve prior commits.
Work locally, no paid services/new runtime dependencies, real candidate data or
secrets. Do not push/merge/publish/contact recruiters/submit. Public repo intended
only after whole project completion/review. Downloadable self-contained report
required after every task. Stop now for Phase 03 review before any next phase.

## Inspection and source authority

Read existing instructions/README, full assignment and both one-page PDFs, prior
reports/requirements/model/architecture/dictionary, SQL/initializer and tests/
fixtures. Earlier repeated large outputs were truncated; source files were read
and relevant sections inspected separately. Dictionary DDL appendix was verified
identical to schema bytes. Original 75 requirement rows preserved verbatim.
Raw assignment sources, private paths and previous reports untouched. PDFs add
submission requirements, not permission to execute release actions. Prior round/
submission-channel/send-timestamp ambiguity remains a final release concern.

Full Phase 03 prompt: docs/phase03/prompt.md (all 20 sections, exact bytes), SHA256
433e6e2449bab6a456f980c7c914c6e6e75910770078615700930618b4908166.
User accompanying text: `here is next step`. P005 in existing AI journal links it.

## Delivered architecture and schema correction

CPython 3.14.5, observed SQLite 3.53.1, stdlib only. One deterministic generator,
explicit config/catalogue/IDs, actual-record skill matching, focused generation
validation/summary and streaming canonical proof. No new services/frameworks.

Two genuine v1 gaps were corrected, not arbitrary generation simplification:
Candidate.experience_years INTEGER NOT NULL 0..50 and
SkillRequirement.min_proficiency INTEGER NOT NULL 0..4. No fit-score column or
extra relation. Schema v2 now 24 tables/209 fields, same PK/FK/immutability design.
V1 databases refused unchanged; no automatic migration/backfill/reset. Old v1
schema/report recoverable from previous commits. Regression tests cover new
ranges/nullability and v1 data preservation; all old schema test cases retained
with only required fixture/version/field-count updates.

Generator structure:
- generation_config.py: frozen profiles, catalogue, numeric policy, logical clock.
- ids.py: exact phase-required patterns/counters/immutable parent-derived app IDs.
- matching.py: fit exclusively from stored skill/requirement records.
- generate.py: dependency-ordered causal baseline and safe atomic publication.
- generation_checks.py: actual Phase 03 integrity/history checks and metrics.
- canonical.py: ordered streaming records and SHA256, not an export engine.
- scripts/verify_generation_reproducibility.py: real independent pair replay.

## Files created / modified

Created (12):

- docs/phase03/data-generation-design.md
- docs/phase03/prompt.md
- docs/phase03/reproducibility-evidence.json
- reports/phase03-data-generation-handoff.md
- scripts/verify_generation_reproducibility.py
- src/yottaflex/canonical.py
- src/yottaflex/generate.py
- src/yottaflex/generation_checks.py
- src/yottaflex/generation_config.py
- src/yottaflex/ids.py
- src/yottaflex/matching.py
- tests/test_generation.py

Modified (13):

- .gitattributes
- AGENTS.md
- README.md
- docs/data-dictionary.md
- docs/phase01/journal.md
- docs/phase01/requirements.md
- pyproject.toml
- scripts/build_data_dictionary.py
- src/yottaflex/__init__.py
- src/yottaflex/db.py
- src/yottaflex/schema.sql
- tests/fixtures.py
- tests/test_schema.py

Original private sources/source manifest, Phase 01/02 reports and architecture/model
snapshots preserved. Only current requirement-status overlays appended. SQL LF
rule added for stable source fingerprints. Generated DBs/replay scratch remain
ignored under output/phase03/. No scratch SQLite files are included in commits.
Measured JSON evidence contains aggregates/hashes/timings, not real candidate data.

## Exact generated counts (both runs of each profile)

| Table | STARTER A=B | FULL A=B |
| --- | --- | --- |
| Application | 160 | 8000 |
| ApplicationEvent | 160 | 8000 |
| Approval | 10 | 200 |
| ApprovalEvent | 20 | 400 |
| Availability | 0 | 0 |
| Candidate | 100 | 5000 |
| CandidateEvent | 100 | 5000 |
| CandidateSkill | 522 | 27061 |
| HiringManager | 2 | 20 |
| Interview | 0 | 0 |
| InterviewEvent | 0 | 0 |
| InterviewPanel | 0 | 0 |
| InterviewParticipant | 0 | 0 |
| Offer | 0 | 0 |
| OfferEvent | 0 | 0 |
| PanelMember | 0 | 0 |
| Requisition | 10 | 200 |
| RequisitionEvent | 40 | 800 |
| SchemaMetadata | 1 | 1 |
| Scorecard | 0 | 0 |
| ScorecardEvent | 0 | 0 |
| ScorecardItem | 0 | 0 |
| SkillRequirement | 40 | 800 |
| Staff | 6 | 24 |

Full target in this phase: 200 requisitions, 5,000 candidates, 8,000 applications.
The remaining 2,000 interviews are intentionally NOT generated. Eleven scheduling/
review/offer-related tables remain empty. Approved authorization count is 200
(full)/10 (starter); current requisition projection is open after a real approval
chain, not independently randomized approved status. Applications all applied.

## Synthetic distributions and assumptions

Four families: Backend Engineer, Data Analyst, Integration Engineer, Applied AI
Engineer; four criteria each from eight-skill catalogue. Full categories 50 each;
Junior/Mid/Senior counts 68/68/64. Required minimum proficiency 2/3/4, optional one
less; base role weights perturbed +/-300 basis points and exactly normalized to
10,000 via largest remainder. Currency INR/USD, synthetic annual bands with seniority/
role correlation. No external personal data/licensed corpus or real salary claim.

Candidate experience cycles 0..2 /3..6 /7..15 years with seeded variation; skill
specialization cycles roles, four main skills plus 35% inclusion of extras.
Primary proficiency grows with experience; extra skills are shallower. These are
designed synthetic correlations, not observed hiring population distributions.

| Metric | Starter | Full |
| --- | --- | --- |
| Derived application fit categories | {"borderline": 55, "excellent": 48, "weak": 57} | {"borderline": 2800, "excellent": 3200, "weak": 2000} |
| Experience/skill depth (mean in milli-points) | {"early": {"candidates": 34, "mean_level_milli": 1312, "skills": 179}, "experienced": {"candidates": 33, "mean_level_milli": 3228, "skills": 171}, "mid": {"candidates": 33, "mean_level_milli": 2250, "skills": 172}} | {"early": {"candidates": 1667, "mean_level_milli": 1238, "skills": 9055}, "experienced": {"candidates": 1666, "mean_level_milli": 3243, "skills": 8983}, "mid": {"candidates": 1667, "mean_level_milli": 2233, "skills": 9023}} |
| Annual compensation by currency, integer minor units | {"INR": {"max_upper_minor": 322143500, "mean_lower_minor": 138120575, "mean_upper_minor": 181226825, "min_lower_minor": 84226700, "requisitions": 8}, "USD": {"max_upper_minor": 20980300, "mean_lower_minor": 14261050, "mean_upper_minor": 18236050, "min_lower_minor": 12041800, "requisitions": 2}} | {"INR": {"max_upper_minor": 444831700, "mean_lower_minor": 183474504, "mean_upper_minor": 238908698, "min_lower_minor": 77167000, "requisitions": 155}, "USD": {"max_upper_minor": 23604700, "mean_lower_minor": 10582220, "mean_upper_minor": 13752553, "min_lower_minor": 5290400, "requisitions": 45}} |
| Applications per requisition histogram | {"16": 10} | {"40": 200} |

Application fit uses actual stored CandidateSkill and SkillRequirement: sum each
`weight * min(level,minimum) // minimum` (minimum zero contributes full weight).
Missing skill =0. Excellent requires all required minima and >=8500 basis points;
remaining >=6000 borderline, rest weak. Fit categories are reports, not persisted
input labels, random hiring outcomes or anomaly truth. No hired/rejected statuses.

Per-role target 40% excellent/35% borderline/rest weak, sampled without replacement
from derived pools. Small pools fall back deterministically to other unselected
candidates. Starter actual 48/55/57; full 3200/2800/2000. Do not claim starter hit
nominal quotas. Some candidates can have multiple/zero applications; no requirement
for every candidate to apply. Exact experience/proficiency histograms and all
metrics are in the versioned reproducibility-evidence.json.

## IDs, parents, chronology and causal history evidence

Required REQ-2026-000001 /CAND-000001 /literal APP-<candidate-id>-<req-id> used,
unique immutable IDs and no duplicate pairs. Six-digit positive counters for Staff,
managers, criteria, approvals and REQEV/APREV/CANEV/APPEV. No future INT/SCORE/OFF/
panel/calendar IDs allocated. Full supporting Staff=24, managers=20, criteria=800.
Future phases can append after maxima and consume this DB without regenerating
or changing existing parents.

Seed 20261022, logical origin 1767225600 (2026-01-01 UTC). Independent SHA256-derived
random streams for requisitions/candidates/apps; sorted catalogue/PK iteration,
no current time, random UUID, implicit row order or machine path in canonical data.
Temporary random filenames are IO safety only, not generated content.

Causal order: Staff -> managers -> draft role -> four criteria -> pending role/
Approval at +1h -> stored-fact policy decision at +2h -> open at +3h. Policy checks
active manager, independent HR, pending request, coherent capped INR/USD band,
required active criteria and total weights=10000. Every approval follows actual
facts; no fake history merely satisfying FK. Four RequisitionEvents and two
ApprovalEvents per role, monotonic sequences and correct actor/time/snapshots.
Approved event retains the exact historical compensation snapshot for future offers.

Candidate creation occurs within first 120 logical days, with CandidateEvent.
Apps follow max(candidate creation, role opening)+60 seconds..30 days, one
created/submitted event with actual candidate origin and system recorder, updated
projection matches applied timestamp. No unsupported submitted enum/advanced
review/offer stage invented. All changes commit with history atomically.

## Storage safety and measured validation

Every existing output refused, including empty/initialized files/symlinks. Own
private sibling scratch DB initialized, populated under BEGIN IMMEDIATE, validated/
measured/hashed then committed/closed. Same-directory hard link publishes a new
path atomically without overwriting a competing writer; owned scratch removed.
Failure rolls back and never publishes a partial output. No force/reset option.

Final generation checks (22), each measured from actual SQL/records, zero violations
on both independent runs of both profiles:

- exact_populated_counts: 0 violations
- deferred_tables_empty: 0 violations
- foreign_keys: 0 violations
- sqlite_integrity: 0 violations
- primary_keys: 0 violations
- required_fields: 0 violations
- logical_time_bounds: 0 violations
- deterministic_identity_formats: 0 violations
- application_pair_uniqueness: 0 violations
- initial_lifecycle_states: 0 violations
- active_staff_and_managers: 0 violations
- application_chronology: 0 violations
- approval_subjects: 0 violations
- requisition_approval_histories: 0 violations
- requirement_weights_ranges_and_approval_bands: 0 violations
- candidate_skill_ranges: 0 violations
- candidate_skill_coverage: 0 violations
- synthetic_contacts: 0 violations
- CandidateEvent_creation_history: 0 violations
- ApplicationEvent_creation_history: 0 violations
- candidate_experience_history: 0 violations
- snapshot_states_times_actors_and_no_truth_labels: 0 violations

Checks are generated from measured counts/query results, not hardcoded PASS.
Tests deliberately corrupt isolated savepoint fixtures to verify detection and
restore them; this is NOT a mandatory-anomaly injection/ground-truth feature.
Failure tests verify real policy rejection, rollback cleanup, existing-file/symlink
preservation, competing publication, CLI nonzero/no success output. All sources,
PK/FK/ranges/enums, required fields and approved/application histories covered.

## Actual tests, commands and results

1. Full source/Git/doc/test inspection: clean at fd8cb4e, branch preserved, sources
   read without alteration. Some large repetitive outputs truncated and relevant
   sections inspected separately; dictionary exact DDL verified against schema.
2. Prompt byte copy/hash succeeded; dictionary regeneration after two-field v2
   change succeeded. `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -p test_schema.py -q`:
   exit 0, 35 schema tests in 0.805s (33 retained +2 minimal-correction regressions).
3. Initial temporary starter API run: exact counts, 21 checks zero violations,
   actual canonical d2e32228...; subsequent full combined suite passed 57 in 6.353s.
   Additional metadata/experience-history checks were then added, so these earlier
   results are historical checkpoints, not substituted for final verification.
4. Final command:

```sh
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
```

Exit 0: **57 tests in 6.492s, OK**, dictionary exactly matches actual v2 SQL/209
fields. Includes 35 schema and 22 generation test methods with many subtests.
Tests independently create starter and full pairs, compare every ordered row,
counts/summaries/hashes; change seeds/working directory/PYTHONHASHSEED; verify
weighted math, required criteria, chronology, histories, ranges and failures.
No failed unittest run occurred in Phase 03. A documentation patch-context mismatch
was rejected atomically then corrected; it was not a test or a code success claim.

5. Recorded standalone replay command:

```sh
PYTHONPATH=src .venv/bin/python3 scripts/verify_generation_reproducibility.py --directory output/phase03/repro-final-20261022 --profile both --seed 20261022
```

Exit 0; four genuinely separate DB generations. A preliminary replay at
output/phase03/repro-20261022 also matched before final checks were tightened.
Final measured JSON copied unchanged to docs/phase03/reproducibility-evidence.json;
no SQLite file copied into tracked paths.

6. `PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh`: exit 0, four shell +three
Python groups (runtime/SQLite FK rollback/source identity/privacy) passed. Last
pre-report run inspected 38 publication candidates. Final report-inclusive run
also exited 0, inspecting 39 candidates; all four shell and three Python groups
passed with unchanged source identities and no private/generated candidates. `git diff --check` exit 0. Python audit compared
all 75 baseline requirement rows against fd8cb4e and verified full P005 SHA256;
exit 0, rows unchanged and prompt exact. Existing source PDFs/statement still
match original source manifest. No dependencies installed or network used.

## Exact two-run reproducibility and performance

Canonical protocol: sorted table names, rows in declared PK order. Compact ASCII
sorted-key JSON header {table,columns}+LF, each schema-column row array+LF. SHA256
per table. Aggregate hash = SHA256 compact sorted-key JSON table->{rows,sha256}.
No SQLite binary-file hash or elapsed/wall-clock/path data in proof. Compare every
ordered record as well as counts/hashes and deterministic summaries.

| Profile | Run A SHA256 = Run B SHA256 | Records compared | Seconds A / B |
| --- | --- | --- | --- |
| starter | d2e32228ceff587d4bbe36d944a78e902baa0d596fa447a15337d33fb157456d | 1171 | 0.046130167 / 0.039505416 |
| full | 131e6d27738e28c29b6b79374cf5b9ad24e5d16d704fd01ff826e68f71b0385d | 55506 | 2.407750334 / 2.546991000 |

All 24 tables compared, including empty downstream tables and schema metadata.
Durations measure real local whole operation: initialization/population/validation/
summary/hash/publication. They are diagnostics, not deterministic fields or a
performance SLA. Memory is O(candidate skills +requirements +one candidate pool),
not Cartesian-product storage; batch <=256 profiles/apps and their dependents.
Observed CPython 3.14.5 /SQLite 3.53.1; other engine builds not empirically certified.

### Per-table checksum proof

Rows and SHA below are identical in A/B of the named profile; equality also verified
by streaming each record, not inferred only from digest equality.

| Table | Starter rows / SHA256 | Full rows / SHA256 |
| --- | --- | --- |
| Application | 160 / b30fcf94bcb8dd540c47fd9ba7cccba3d4d089d86fb189975cbf8d788efc6b0d | 8000 / 46cf59cc12c363a1cec6a7e46fa0b447ed5f1b7e1610b52c11c20eee19310530 |
| ApplicationEvent | 160 / d0fc5f99927a75845dc6b1b723639c8ac0630bb404c7eff087242124b6509aeb | 8000 / f0c3200bc6f065042a3dbd8568ddcaae76f62f681603f98a66dc28b691528144 |
| Approval | 10 / fd1fd7d96608610008fbd86f68b60128d6f435e669b0a1bcae056058460f840f | 200 / a3a579ad35aa7836aab0d96f5a3b66e5fe69996e2689557a2d7e94f6a572077f |
| ApprovalEvent | 20 / ba6ce882cdbedf8ca8ee3f6d2cf72c23797b2005d9a8dc8ec6a9de1f30b1f56f | 400 / 250fc6a96bd50ba8d51c438d07c94f20867277face9b62fe1331cee303008a0a |
| Availability | 0 / da4835012134d0999e5dec6d5413085eed696e907db3404433c5d652b3718c78 | 0 / da4835012134d0999e5dec6d5413085eed696e907db3404433c5d652b3718c78 |
| Candidate | 100 / c5eadef0eb07d508d531fa88e2e7884ac6ffce13423c29b08cc9e8e3da1cc744 | 5000 / 6e0126303bf7fdfbf50c5207964f54ea9156f42cbcb64013f5af518ae3b1cbcc |
| CandidateEvent | 100 / da887c2fad0adae82d40e40c6077d8ac77ec1061a2a89495f0ffbf257420f162 | 5000 / 88ab6bc473b5013e9a6861e02b9689efe843c2db7003df4060595c07a64dfebc |
| CandidateSkill | 522 / 58e3a9dd37be8f7da4a39c3ca75db484e549b10cedd07345507a57738df0e81b | 27061 / 84f680161b39946ec98664e061764da3392242b2a29bb218383591e93a6f93ec |
| HiringManager | 2 / 900b09eae8c98cdae49da417e1641c413f7934cb95f47cec02c08e879847bd76 | 20 / 9a939034d2dc9a78cb800e0cddd908772f9f07b99905d58279e3084b47330e90 |
| Interview | 0 / 889a53b2e153cb73bb20b6fe37d569e0718074a4da58f3a3150b401ab7646014 | 0 / 889a53b2e153cb73bb20b6fe37d569e0718074a4da58f3a3150b401ab7646014 |
| InterviewEvent | 0 / 20c01964c482daf46ee7e8f910ac46433e75b7a198086497c8418ffc7fb4a086 | 0 / 20c01964c482daf46ee7e8f910ac46433e75b7a198086497c8418ffc7fb4a086 |
| InterviewPanel | 0 / 677d218df04dc58471305c01b0fd71927ff17462f14273b8aca858d19b588da1 | 0 / 677d218df04dc58471305c01b0fd71927ff17462f14273b8aca858d19b588da1 |
| InterviewParticipant | 0 / f39a562ce7ee03f3fbedd1707448346489ff6d78e24a5107507c5b30a45cb831 | 0 / f39a562ce7ee03f3fbedd1707448346489ff6d78e24a5107507c5b30a45cb831 |
| Offer | 0 / 8ea460ed068c61cf6f033b1aa70292e6c0023c491e41fe66994a6b4143af7bbb | 0 / 8ea460ed068c61cf6f033b1aa70292e6c0023c491e41fe66994a6b4143af7bbb |
| OfferEvent | 0 / 3ad5ceb0648316f55107f82e2272fca5b3e9108333bce05d7510367c52623cbe | 0 / 3ad5ceb0648316f55107f82e2272fca5b3e9108333bce05d7510367c52623cbe |
| PanelMember | 0 / 220213504eb5cbbce336bc20a49594e1e2c16a00b9d040eef59373dce7b337d7 | 0 / 220213504eb5cbbce336bc20a49594e1e2c16a00b9d040eef59373dce7b337d7 |
| Requisition | 10 / 44ac8cab5fe22a83d9c880f03e34b7717b6ac8f2a1d20dfd07319987f6b7dbfb | 200 / 0a02fb0494b420f5f26fa34c41d708d3970d74cfe8f4c7c7c6d49a4b4c1bd494 |
| RequisitionEvent | 40 / 6caa3f0f93fa0bce34d018d685e38574791e391acf2002733bf65f3fa010d5d5 | 800 / aaf1b0baab13e8c7888f82ed2124b314528baf5e8d6016d33a5799b5e255c156 |
| SchemaMetadata | 1 / 9541dcc0d5c87cf7b709276469debb2a46a8acb8ebe59f94467202082ba19162 | 1 / 9541dcc0d5c87cf7b709276469debb2a46a8acb8ebe59f94467202082ba19162 |
| Scorecard | 0 / 78db10b7894750684e5258cd73a6a4c3c6f6d5b6e54898490353a4aa3c73b3a5 | 0 / 78db10b7894750684e5258cd73a6a4c3c6f6d5b6e54898490353a4aa3c73b3a5 |
| ScorecardEvent | 0 / 0b2a4007c687d97ed73b5c168265cb0737e7fd3785923d8b123f509c252d1e04 | 0 / 0b2a4007c687d97ed73b5c168265cb0737e7fd3785923d8b123f509c252d1e04 |
| ScorecardItem | 0 / f35bd6e64fa348639004984cdbc1fbce6131fe74b968972731a118a6bdad79ef | 0 / f35bd6e64fa348639004984cdbc1fbce6131fe74b968972731a118a6bdad79ef |
| SkillRequirement | 40 / 882e9ab27d892efdfe0461847e5ea78948105810196982d0929856b745964da4 | 800 / 9e74559cbc4b648d05f133b93ac516395352a189866ffa61659bc2edd56fc284 |
| Staff | 6 / 229d171c6444248f47177802f92408a8a40043c04161358c114ba2b4e2ca958e | 24 / dd2d65696197acaf16b8cb0bedfca66e06dea7a55cec41b9e025c08341ec1983 |

## Requirement coverage and remaining scope

Original 75 source rows unchanged. Phase 03 overlay documents I/T/Doc vs deferred:
F01/F02 master/approval/candidate/app generation; F03 initial stages only; F07
requisition approvals only, NO offer workflow; F12 causal immutable history.
D06-D11 IDs/dependencies/seed/profiles and 3 exact target counts implemented; D12
valid Phase 03 baseline, not finished baseline/anomalies. D14/D15 derived fit/
approval decisions only, no scorecard/ground truth. D17-D18 declared variation and
focused tests; D20 generator docs/evidence; D21 real starter/full replay of this
subset only; D22/V01-V07 measured baseline integrity/history. S01/S03-S09 setup,
full prompts/AI disclosure, commits/review status. All other requirements remain.

**NOT complete:** 2,000 interviews, panels/calendars/conflict prevention/rescheduling,
advanced stage/review gates, structured scorecards/calculation, offers/offer
approvals, withdrawals/incomplete review variants, all five labelled negatives,
separate truth/evaluator, full CSV/JSON/SQL export engines and complete end-to-end
replay/evaluation. No user approval for these later features has been inferred.
Current fit buckets are descriptive derived metrics, not anomaly labels or hiring
outcomes. Unavailable downstream metrics explicitly named in summary.

## Known limitations and human review

- Two minimal schema input fields require version 2/new databases. Existing v1
  data deliberately not upgraded; real migrations would need separate review/tests.
- Fully synthetic designed distributions/bands/caps/weights/time/stages, not
  external/company policy; starter quotas can be scarce and fall back honestly.
- Requisitions all approved/open and apps initial applied by scope; no claim of
  full lifecycle diversity until corresponding workflows exist.
- validate_generated is deliberately Phase 03-specific: applied-only and empty
  downstream tables. After augmentation use phase-aware/composed checks, not this
  unchanged initial-scope checker as finished-workflow acceptance.
- Whole challenge remains incomplete; finishing remaining target/interviews and
  exception paths is still required before public release/submission.
- Atomic publication needs same-filesystem hard-link support; exact same runtime/
  schema/config proven, no blanket cross-engine compatibility claim. No reset.
- SQLite owner can disable protections; supported connector required. Privacy
  checks are a baseline, not a universal secret/person detector. Final staged/
  human release review still needed; source documents and scratch DBs stay ignored.
- Prior administrative round/email-vs-portal/send-timestamp uncertainties remain
  release risks; exact supplied deadline retained, no submission/contact action.

Codex implemented code/tests/docs and executed all recorded verification; heavy AI
reliance disclosed. No subagents or other human implementation help. Complete
P005 saved; P001-P004 and export limitations preserved. Human Phase 02 progression
approved in the supplied prompt; human Phase 03 independent execution/design/code/
assumptions/ownership review is PENDING. No fabricated human review or test claims.
Other-tools prompt completeness still needs user audit before final submission.

## Local Git status / finalization

Baseline: fd8cb4e and 2a180d5 (Phase 02), 7e5a77b/baafb55 (Phase 01), preserved.
Implementation commit: **fc1423a** - `feat: generate deterministic master data and applications`.

Actual finalization commands/results:
- Explicit git add of the 24 implementation/docs/test/evidence files, excluding
  this report/private sources/databases: exit 0.
- git diff --cached --check/--stat/--name-only: exit 0, intended scope only.
- Targeted schema/initializer/dictionary diff review; git diff --exit-code -- src
  tests scripts: exit 0, no unstaged code changes.
- git ls-files docs/assignment: only README tracked; raw sources remain ignored.
- Python audit: exactly 24 staged implementation files, no .pdf/.sqlite/.sqlite3/
  .db, current schema SHA matches both measured profiles; exit 0.
- git -c user.name=Codex -c user.email=codex@local.invalid -c commit.gpgsign=false
  commit -m 'feat: generate deterministic master data and applications': exit 0.
  Prior commits preserved. Immediately afterward only this report was untracked;
  implementation working tree clean, no remote configured.

No push/merge/remote creation/publication/contact/submission. Report gets a separate
local documentation commit. Downloadable ignored-output copy records post-commit
hashes/clean-state so no tracked file must contain its own commit ID.

## Recommended Phase 04 order (not authorization)

1. Human review/accept Phase 03 and its two schema corrections/assumptions.
2. Consume existing v2 baseline, preserve IDs; define valid stage and calendar/
   interviewer/panel policies and deterministic future random domains.
3. Add required Staff reviewers, panels/effective memberships, calendar availability,
   then schedule exactly 2,000 interviews with transactional conflict guards/history.
4. Only within next confirmed scope add valid rescheduling/withdrawal paths;
   structured reviews, offer workflows, five anomalies/truth/evaluation/export/
   final replay require their own authorized stages. Do not implement them now.
5. Keep actual tests/metrics, full prompt/review journal and scoped local commits;
   publication/submission remain separate final human-controlled gates.

**STOP: Phase 03 complete for its authorized subset. Await review before Phase 04.**
