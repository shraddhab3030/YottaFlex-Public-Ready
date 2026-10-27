# Phase 07 — complete exports and reproducible deliverables handoff

Date: 2026-10-27 (Asia/Kolkata). Individual YottaFlex AI 72-Hour Code Challenge,
Associate AI Forward Deployed Engineer. Deadline supplied by user:
**October 29, 2026, 13:52:35 IST**.

## 1. Assessment and continuation state

**Phase 07: PASS for the authorized technical scope.** The valid Phase05 FULL
baseline is preserved; all24 tables are included in CSV, JSON and SQL seed;
every format restores exactly. Two independent full packages match every byte
and relational scalar. Required synthetic artifacts are intentionally committed.
All208 tests passed, including183 existing tests and25 new export tests.

This is not final public-submission acceptance. Human personal testing, code/line
ownership, all-tools prompt audit and final publication privacy review are still
pending. Seven inherited report references to private local paths require human
review before release; none is introduced by the Phase07 changes/artifacts.
No remote was configured, nothing pushed/merged/published/submitted, and nobody
contacted. Phase08 was not started. **STOP and await user review.**

For another ChatGPT chat: Phases01–06 are preserved. User P010 conditionally
approved Phase06 and authorized Phase07 only. Continue by reviewing this report,
not by silently starting Phase08 or publication. All executions below were by
Codex; they are not claims of independent human verification.

## 2. Architecture, entities and trade-offs

Python3.14.5 standard library, local SQLite3.53.1 (schema requires3.38+), no
project third-party dependencies, ORM, cloud, paid service, application LLM or UI.
The provided local Python interpreter must already be installed. No pip download
or network access is needed after cloning when that prerequisite is available.

Existing business modules remain unchanged: explicit transactional operations,
strict local schema, append-only event history, deterministic generation,
independent domain validation, isolated anomaly injection/detection/evaluation.
New exports.py owns exact codecs/catalog/dependency order/fresh restores/first
row difference; deliverables.py composes build/export/restore/verify/evaluate;
privacy.py adds actual synthetic identity and content checks. The replay script
composes the same functions twice, rather than implementing another generator.

Eleven core entities and relationships:

- HiringManager is a Staff role and owns Requisitions; SkillRequirements belong
  to approved role versions and compensation policies.
- Candidates have CandidateSkills and Applications. Application joins one
  Candidate and one Requisition, with a unique pair and lifecycle audit.
- InterviewPanel belongs to the role; PanelMember joins effective Staff members.
  Availability belongs to Staff. Interview links Application and panel, with
  actual InterviewParticipant snapshots used for calendar conflict checks.
- Scorecard links an assigned Interview/reviewer; ScorecardItems refer to relevant
  SkillRequirements and derive the exact weighted integer result.
- Offer belongs to Application and an approved band snapshot; independent Approval
  records protect requisition and offer decisions. Accepted offers drive hire and
  sibling cleanup. Typed events retain actor/time/reason/old-new state snapshots.

Schema v2 stays24 tables/209 fields/45 FK groups/42 protection triggers. No schema
migration, identifier changes or validated business-logic refactor was needed.
CSV/SQL export streams rows; import batches256 rows. JSON import loads one table,
which is acceptable at this measured scale. Large texts use deterministic gzip;
this trades a little CPU/readability for much smaller single-repository artifacts.
Byte replay is scoped to the verified interpreter/SQLite/compression runtime.
Peak RSS was not measured and no broader benchmark is claimed.

## 3. Exact files created or modified

All paths below are relative to the isolated project Git root. The generated
artifact inventory in section4 lists every one of the68 additional artifact files.
Other changed paths and purposes:

| Change | Path |
| --- | --- |
| M | .gitattributes |
| M | .gitignore |
| M | AGENTS.md |
| M | README.md |
| M | docs/data-dictionary.md |
| M | docs/phase01/journal.md |
| M | docs/phase01/requirements.md |
| A | docs/phase07/export-and-reproducibility-design.md |
| A | docs/phase07/prompt.md |
| A | docs/phase07/repository-privacy-review.json |
| A | docs/phase07/reproducibility-evidence.json |
| A | docs/phase07/requirements-acceptance.md |
| A | docs/phase07/reviewer-verification.json |
| M | scripts/build_data_dictionary.py |
| A | scripts/verify_deliverable_reproducibility.py |
| A | src/yottaflex/deliverables.py |
| A | src/yottaflex/exports.py |
| A | src/yottaflex/privacy.py |
| A | tests/test_exports.py |
| A | reports/phase07-export-deliverables-handoff.md |

A=created, M=modified against Phase06 report commit685c69a. Existing README,
working agreement, ignore/attribute policies, generated dictionary header,
requirement overlays and AI journal were updated. Actual original75 requirement
rows, dictionary field/constraint rows, previous prompt files and prior phase
reports are preserved. SQLite schema and all old runtime business modules stay
unchanged. Ignored output/ and tmp/ contain actual local replay databases/logs;
these are diagnostic scratch, not deliverables. A downloadable postcommit copy
of this handoff is kept under ignored output/reports/.

## 4. Complete artifact file inventory and sizes

Paths are relative to artifacts/. Every listed file was compared byte-for-byte
across both independent full runs; staged Git blobs were also checked against
these exact bytes. SHA256 is over stored bytes, including gzip where applicable.
Manifest inventories67 files; its own hash is listed here/from external replay
evidence, avoiding self-referential hashing. Total68 files, **25,495,764 bytes**
(25.50 decimal MB; du reported25,048 KiB allocated). Largest stored file is
CandidateSkill.json,2,281,185 bytes. No individual stored file exceeds4MiB.

| File | Bytes | SHA256 |
| --- | ---: | --- |
| README.md | 1844 | e456ec3a95b826d33864e045d1ac5c32c4b00095e1ddaf59e02fa72106e7e40f |
| anomalies/input/observations.json | 29296 | 75e0ef87e9cdeeb69fe5c4c8c5b9b13b217d2f7935097f27d5321670928cc72c |
| anomalies/reports/clean-validation.json | 13380 | bdbe5c0f0753d1d6b830b98e5af37f353ad3c8347afcdebe2e2b10e5692861f6 |
| anomalies/reports/controls.json | 949 | 8446e33195cd2158c57419913937a18a3a34e7028594d80990c4916f3b0eaee4 |
| anomalies/reports/evaluation.json | 1770 | 7722e789b14b0f7ca30d6a9075bdb02096944d4ba7afd2a6732d635191dd365d |
| anomalies/reports/experiment.json | 12521 | 8d9df21567d5871f5f3b071e178760c888eb26f3c967caec0101c56842f4f6ef |
| anomalies/reports/findings.json | 34475 | 2d82364a52885e20f37af09402f02f036436184c55310a14feed100efd787059 |
| anomalies/reports/observation-structure.json | 993 | 4923ba9effcdc4c084b413ffbcd8beeab7f8e3cb2cb27f8ed0e6f065462f5593 |
| anomalies/reports/package-verification.json | 3384 | 41497f39cb453e922a7f444842765dfab67ff74b15d093fa273d41303adf95a8 |
| anomalies/truth/ground_truth.csv | 10688 | 860469ee6b8ff4ff29f5fbdbe6055e301ee4326c7417b6c079246f33f4bf793d |
| anomalies/truth/ground_truth.json | 21100 | 205b31bdb6abce3c9c84889f658b7e64ac710ef5102dbadf7431307d660e4688 |
| baseline/catalog.json | 46400 | dd67507f1c3ee5c573547fc926f835d437261204ed0dd8a2aaa3a6226f17c750 |
| baseline/csv/Application.csv | 823356 | 6480b6f817800abe3b6b942f770de332fc2a14119b06dee8a68dc495f281dd54 |
| baseline/csv/ApplicationEvent.csv.gz | 353329 | 87e4051d5fc10a8e1ec5d39940c20fd7147b024dc4a8b93c05154b5aab36938b |
| baseline/csv/Approval.csv | 56842 | 7fe7347202c4c38d3afb2415e14a397ce1e66718bc5e1e719cff4f3f3e4428a5 |
| baseline/csv/ApprovalEvent.csv | 438749 | 3ffbdde97da2a2466207e0eebe4dcb7dbd3132d947d59c205a9f4530a2fc46f5 |
| baseline/csv/Availability.csv | 179618 | 1ccbf0e1a85efc56770d222cd6e159f25942e8324a6c1e8ca3592c9d6c6c2666 |
| baseline/csv/Candidate.csv | 542125 | 9dce37dcdf806575cb302f0bc4b82daba175996def85d8821dd36a47a8518b50 |
| baseline/csv/CandidateEvent.csv | 1245457 | e3881b4e15701d8c4f19ce5d9161c464cceb9ff8122de92a14fbd76126f98b0d |
| baseline/csv/CandidateSkill.csv | 1063391 | ed1479d9d460f4446a0134df754ea6536127287c96ae252b40cb5e1bf1c11683 |
| baseline/csv/HiringManager.csv | 1377 | 1eeedddab36f9a6676497aa4bf79a882d3e996013b3f06cd210f022c8b2de142 |
| baseline/csv/Interview.csv | 246089 | 392582c7242ce268eb17989583e18ac95a352cb132cfdb79d1898757650ffc03 |
| baseline/csv/InterviewEvent.csv | 1182091 | e0b7af50b186e171f8fd2f607c5bc27c7a997c34ad47b211a14044f7b3b54ed7 |
| baseline/csv/InterviewPanel.csv | 17871 | dca5d290b35a3d7ed0dc9133536d32d2ff0663658c647de86758433b9f901c48 |
| baseline/csv/InterviewParticipant.csv | 285058 | e6f22635e6f56b599662d19119b47e68fc5997215fe5e46d253cc37719dda591 |
| baseline/csv/Offer.csv | 31202 | 9b29b43c0f02b31e185063c7bc3871a6a33b511aa1c2cc7168db5627d9429ceb |
| baseline/csv/OfferEvent.csv | 849339 | 0ad240a2eef52361de28d267edc9066ee1c51654a72ace60876598a95bf55e3d |
| baseline/csv/PanelMember.csv | 32555 | 8c654e3dcc950b454b29497c4dc572a3de08fab9314c28ed42925f0d4c6775a5 |
| baseline/csv/Requisition.csv | 22916 | b52a3e347c0859d5ea89286480e3503a7da452e7a21479b9587128e0fd33bd8f |
| baseline/csv/RequisitionEvent.csv | 256067 | a9e8c35be2bcec17eb860ebd543b1f76e1b6bed7ec7ed7fa44215e0e54fbb5a1 |
| baseline/csv/SchemaMetadata.csv | 204 | ca8e23a1814c234a8a1c84fe891aa5fec4bddd21e4224ee6095aac7999327951 |
| baseline/csv/Scorecard.csv | 131614 | 68bff2618af5d9a47d10a8cd9eedfd563afd4a9be73c8e5a82e78a6df59d5490 |
| baseline/csv/ScorecardEvent.csv.gz | 270319 | 65492c23f892e03bdf0e8161dadbf17bf2754e9535c1db646d0435295e173313 |
| baseline/csv/ScorecardItem.csv | 685282 | 9902f6d535666f3c3eabccc59a821ffb9e327a7890b4a0a32148aa13e00a79f4 |
| baseline/csv/SkillRequirement.csv | 101983 | 7a517fa9529c74bcdf6357ce78bb16e6954193f1a69529fb3ef74c0537ec0074 |
| baseline/csv/Staff.csv | 8118 | f04e1069333529821d18dae2deb4f0d179d190f3aa79342db1080f8a9069da35 |
| baseline/json/Application.json | 1487402 | 9c293ed5efb3b24d7bebffb6bb78f907b06e0282f14e2c8dbce47dc0338fc66d |
| baseline/json/ApplicationEvent.json.gz | 386612 | 52e7e253bbc588c747777f0f11d6e71fa1be980f4d1fe9dabea80fbfcb3bcce9 |
| baseline/json/Approval.json | 114371 | 5c1e3ff8a10e22e0f3d52057e63c0ce622a896996d54e1a6d9528e0ed2f451ba |
| baseline/json/ApprovalEvent.json | 601817 | 0dde6262d6639715c4f5d4780cb48ed2a055265b0d44adaf9d7c5978d749cb15 |
| baseline/json/Availability.json | 332425 | 65210422f0bb26091d02d1ab3e7e4ffeec2a6cb08d4c67b1bcc2b820df4cb76e |
| baseline/json/Candidate.json | 1047003 | 19e2f92630191878e4aa0f97532e2ab474ea6f71a7372dbee39010f099bfb007 |
| baseline/json/CandidateEvent.json | 2216359 | 6303bac6541f1282fb3eaaf9c76751915de52fabd3c856f4edc0ba813c3cbffc |
| baseline/json/CandidateSkill.json | 2281185 | f48e68e0a7433ecf570c389d1cb858bd8bbc8c4f8df1dc7b5b0e0c57ae6d1a5b |
| baseline/json/HiringManager.json | 2985 | 7889a790d661ba7a9acbdb8d52367ced1878da86ca00ddb5c3c8a7f5a5009485 |
| baseline/json/Interview.json | 422133 | 94b665fcb84c72f97952266cdf03aa7e6e124752669eac67420736a62f6c1d80 |
| baseline/json/InterviewEvent.json | 1783217 | bcb7a7112b1475f968d432a96649f3a03adce6a6ece2c95bffa9affd549d03a2 |
| baseline/json/InterviewPanel.json | 31920 | 11f9cf9751c1b26413c7c39868bc9e520690747a62526c8c5890aa9a2e67a06d |
| baseline/json/InterviewParticipant.json | 580113 | 277cd6bf6fa063da45eeb1beb33504d5cc4e68ca747ffc44dcf3e860bc510523 |
| baseline/json/Offer.json | 64218 | 7972ae642b122a3db7309c06cfea84ba2120905fa10d295d880cbfbfb09b5eef |
| baseline/json/OfferEvent.json | 1028343 | 214be428a0efb4f613be84c892c4442e8f1ffe018ffa2a42b9259016e4ec1d6d |
| baseline/json/PanelMember.json | 59601 | 85d504701f2a1a5624bb9e5a4e3109ba48969f278ee32fded7b06f819b8b5633 |
| baseline/json/Requisition.json | 49962 | 893b0e5781f2e9313d195afd9486c029969fa012b39c4342ee2ffc3b78ba9b0a |
| baseline/json/RequisitionEvent.json | 445718 | 5b1225533462b70532459674dacb0e6cd0b2f38a771b5513f746a7d85ecb33cd |
| baseline/json/SchemaMetadata.json | 314 | b33e85b2b3329821af2ed60b5004b5a3762a923f02623a2eed7d7177bf70a4b5 |
| baseline/json/Scorecard.json | 265824 | f71331c5093e1bfe4be0de9cc988e5a30a604ccfec12fa9b7a7d6b277b0cfb4d |
| baseline/json/ScorecardEvent.json.gz | 288703 | c3c07d12e9b9571c6e5d9785d55f687fbd9dd8cdcfa1a3ac56f0f3fe237ade00 |
| baseline/json/ScorecardItem.json | 1103722 | ff30ea5c01e3c33b13c2029106c8dd6a6142cbe9fd375ec442aeabb882270492 |
| baseline/json/SkillRequirement.json | 235634 | eeb9d86c4f5a12f36b1125e817b71bdd3fa175106d5ab7ad1ded37e6716242b3 |
| baseline/json/Staff.json | 14121 | bbb15109555de89661ba12a2638f8fca3222016ad43160672b15f098aa38fde8 |
| baseline/round-trip-verification.json | 46502 | df484643e95ec0afb966059a2da582547c1a9c93b53e32bc554d40d327af22bd |
| baseline/sql/schema.sql | 47328 | 75c10e0264a798ff36e6ffae4c076483dc04247e9c8a5051eead036cacab1c6f |
| baseline/sql/seed.sql.gz | 1404045 | 4dfb3d8d7275b00a5434e6dbeabacf1b257456fee09930530bf9fe8a5c3df7d7 |
| baseline/validation-summary.json | 12678 | 19ac81649c5185f14386d13b2c0e0a73200a9b6d548bf15cccaecb7d2800d086 |
| data-dictionary.md | 117786 | 0bed0685cd8924ab5ba12fea219657ad0a44336129f7be2860f3e35a793d6e7b |
| manifest.json | 20556 | 7116c3a3e3547dad3be90c2c416f7f8a5ff292fe1e9b5be08fb82460b900a420 |
| privacy-scan.json | 665 | 8e565b9491872d3c1930a5056e7794455375d21d4fcb0d903731f80699cfdebf |
| provenance.json | 750 | 97983255773e426efd26f6dbc71c70d1647c96dd8532cca840d4b61d1b0284ed |

Lossless compression is inside the same repository; no external hosting or omitted rows. CLI opens gzip transparently. Raw sizes:

| Compressed file | Stored bytes | Decompressed bytes |
| --- | ---: | ---: |
| baseline/csv/ApplicationEvent.csv.gz | 353329 | 4620952 |
| baseline/csv/ScorecardEvent.csv.gz | 270319 | 14698874 |
| baseline/json/ApplicationEvent.json.gz | 386612 | 7485702 |
| baseline/json/ScorecardEvent.json.gz | 288703 | 15857529 |
| baseline/sql/seed.sql.gz | 1404045 | 39261537 |

## 5. All24 canonical table counts and per-table checksums

FULL seed20261022; logical origin1767225600 UTC epoch seconds (2026-01-01 UTC).
Required four volumes remain exactly200 requisitions/5000 candidates/8000
applications/2000 interviews. Every table below matches in original, CSV, JSON,
SQL and the second independent build. Total **89,575 relational records**.

| Table | Records | Canonical SHA256 |
| --- | ---: | --- |
| Application | 8000 | b74c6e38190a1217982c6d1438adbea08c2b6cde8d0dadd39f047d1d232eb6ff |
| ApplicationEvent | 14843 | a21ca544f772ae5f0377fbc185d4ea3e127c99139c01fde32ba350db8e14d80d |
| Approval | 429 | d1a71a7d56092685a8cbfffa0615906e99a432e29a7d9195d291ff13d08b703a |
| ApprovalEvent | 858 | 61a273bb0df412cadea89fb84ac19312250746dae2314389173eb5be6eb0f411 |
| Availability | 2680 | 5b69acedf076075b53fe918110177340a708f9fc2a816aac6c1b781f8203690f |
| Candidate | 5000 | 5587bd6230d1512e72a8124addf427cf041b5af75fd2cd55eb22cc3b8adf3bb0 |
| CandidateEvent | 5083 | 3d11fe1e3e216663628fe5727c48ee6c706563ce605d6133de38e366189be152 |
| CandidateSkill | 27061 | 84f680161b39946ec98664e061764da3392242b2a29bb218383591e93a6f93ec |
| HiringManager | 20 | 9a939034d2dc9a78cb800e0cddd908772f9f07b99905d58279e3084b47330e90 |
| Interview | 2000 | c628268d17628e013c1955982d429f4647b9cf8dd5ad6ac29c4f1acb6ed01b18 |
| InterviewEvent | 3147 | 0c860a81cc269ce58d9d0c262ccaf1cebb6d62efe097c0a39b337ae3453dcdf3 |
| InterviewPanel | 200 | feb7a5ecb1471b9e4a69f14db43555c28cdcff27a6bcce7daa83dfbef0281f0f |
| InterviewParticipant | 5000 | 92634d5ee3cbdd48bcb474ab01aa11a8f4ac394291c38d9ec4c916d56a156127 |
| Offer | 229 | d45986d081faf45cdfc35cd6d3db17994da800ff45a79d65886f76e10a258851 |
| OfferEvent | 957 | 36f07788c2b6acf24c3b2c3c76683e586c883a342212b299798288e63537037c |
| PanelMember | 500 | 50a5148362a7f8a10777e781cb7649f1955d30b93449a675e209b5358b7a46de |
| Requisition | 200 | 0a02fb0494b420f5f26fa34c41d708d3970d74cfe8f4c7c7c6d49a4b4c1bd494 |
| RequisitionEvent | 800 | aaf1b0baab13e8c7888f82ed2124b314528baf5e8d6016d33a5799b5e255c156 |
| SchemaMetadata | 1 | 9541dcc0d5c87cf7b709276469debb2a46a8acb8ebe59f94467202082ba19162 |
| Scorecard | 1122 | 7d2c9535d9c7bdfa2e53355535679e68d1dc9fd78d6f0878bc43e04e881b9386 |
| ScorecardEvent | 6066 | 6d73eb95b065f177d12be5b0f9f45b3ab496e95c2b842f8508d642a68f213d19 |
| ScorecardItem | 4488 | 3dad7d5d07133244cac643b9b2cdda3f995d0c428a1c959a7ac6ce1df6b06ba8 |
| SkillRequirement | 800 | 9e74559cbc4b648d05f133b93ac516395352a189866ffa61659bc2edd56fc284 |
| Staff | 91 | 207f12721f23883da84938e397263cf06f3333ba5d06d605afd9024de07fcb13 |

Scorecard cohorts remain960 submitted/48 incomplete/114 draft. Offers229,
135 accepted/94 rejected;135 hired. These are source-derived synthetic coverage
choices, not employer-mandated quotas. Event and bridge rows are all retained.

## 6. CSV/JSON/SQL encoding and restoration evidence

CSV: every table has explicit schema-order header, all cells quoted, UTF-8,
LF records and PK-ordered rows. Unique null cell is backslash-N (`\N`); leading
TEXT backslashes are doubled, making literal\N/empty/NULL distinguishable.
CR/LF/quotes/Unicode/NUL survive. INTEGER decimals preserve exact int64 values,
including monetary units/timestamps and0/1 boolean fields, without float coercion.

JSON: per-table table/columns/rows envelope; every field present. Integer/string/
null scalar types and schema field order are exact. JSON-valued database TEXT
(snapshots) stays exact opaque text, not a reparsed object. Duplicate JSON keys,
wrong fields/order and booleans substituted for INTEGER reject.

SQL: unchanged exact versioned schema.sql plus complete explicit-column INSERT
seed, topological FK-safe table order and PK order. Single quotes are doubled;
NULL and integers are literal; text NUL uses UTF-8 hex CAST AS TEXT. Every table,
including all event tables and singleton SchemaMetadata, is included.

Fresh SQL restore first executes DDL without initializer-inserted metadata, then
seed once, then normal initializer verifies catalog/metadata/fingerprint. CSV/
JSON use the initializer, verify the imported metadata equals its existing row,
and do not insert it twice. FK and recursive/protection triggers stay enabled.
No protection bypass, fingerprint edit or metadata omission is used.

Existing outputs/symlinks/unowned locks are refused. Files restore into owned
scratch and publish only after verification using exclusive hard links.
Complete directories use cooperative locks and rename. Failed owned scratch is
cleaned. This is not a hostile filesystem security boundary; a narrow race with
uncooperating external directory creators remains documented.

## 7. Independent imports and source-versus-imported hashes

| Source/restore | Tables | Records | Domain checks | FK/recursive triggers | Canonical SHA256 |
| --- | ---: | ---: | ---: | --- | --- |
| Original FULL baseline | 24 | 89575 | 99 passed | ON/ON | 7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb |
| CSV fresh restore | 24 | 89575 | 99 passed | 1/1 | 7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb |
| JSON fresh restore | 24 | 89575 | 99 passed | 1/1 | 7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb |
| SQL fresh restore | 24 | 89575 | 99 passed | 1/1 | 7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb |

Each build creates separate CSV-, JSON- and SQL-restored SQLite databases.
Canonical hash equality is backed by streamed field-by-field Python type/value
comparison of every row, all IDs/joins/NULLs/embedded snapshots and histories.
No first difference was found. Diagnostics identify the first differing table,
primary key and field/type. Additional final package verification, standalone SQL
restore and clean-archive verification all reproduced the same canonical hash.
A command exit code alone is never considered sufficient evidence.

## 8. Validation results and classifications

The canonical baseline passed all99 detailed domain checks and the independently
aggregated categories below. Actual DDL enums and actual SQLite unique indexes,
including partial/implicit indexes, are inspected; categories may overlap.

| Measured category | Violations |
| --- | ---: |
| approval_history_errors | 0 |
| candidate_conflicts | 0 |
| foreign_key_violations | 0 |
| ground_truth_leakage | 0 |
| illegal_stage_transitions | 0 |
| integrity_errors | 0 |
| interviewer_conflicts | 0 |
| invalid_chronology | 0 |
| invalid_enums | 0 |
| natural_or_unique_key_duplicates | 0 |
| offer_band_violations | 0 |
| primary_key_duplicates | 0 |
| review_gate_violations | 0 |
| score_arithmetic_errors | 0 |

Checks include exact volumes, PK/natural keys, FK/integrity, required values,
chronology/effectivity, deterministic IDs, lifecycle replay/projection agreement,
calendar conflicts, participant/reviewer assignment, required complete review,
source-weighted score arithmetic, bands/currency/approvals and terminal cleanup.

Four classifications stay explicit: (1) business-valid canonical baseline;
(2) structurally valid observed projection; (3) expected semantic anomaly findings;
(4) unexpected failures. Packaged observed projection is **semantic_valid=false**
with30 expected findings, zero unexpected findings and zero missed expected
findings. Its structure passes FK/integrity/core-count/history/unrelated-change
checks. It has41 controlled observation operations and five extra relevant-FK
ScorecardItem rows representing deliberately irrelevant criteria, not baseline
corruption or omitted baseline export rows.

## 9. Anomaly package and truth isolation

anomalies/input/observations.json and truth/ground_truth.csv/json are from the same
actual Phase06 execution as reports/findings.json, evaluation.json,
clean-validation.json, observation-structure.json, experiment.json and controls.json.
package-verification.json records additional actual linked replay results.
The redundant binary SQLite copy is omitted; the complete canonical data is
restorable from any of the three required text formats.

The observation baseline hash equals the canonical hash in section7. Verification
runs detection on the restored baseline and observations before loading truth.
Detector has no truth argument/import/access or injection metadata. It runs the
same engine against clean data, then the evaluator alone reads agreed CSV/JSON
truth and matches affected identities. Existing poison/import/order tests and
new packaged replay tests check this separation.

## 10. Truth/findings/metrics reconciliation

| Issue type | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interviewer_double_booked | 10 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| irrelevant_evaluation_criterion | 5 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| offer_exceeds_band | 5 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| stage_gate_missing_review | 5 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| withdrawn_still_scheduled | 5 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| TOTAL | 30 | 0 | 0 | 1.0 | 1.0 | 1.0 |

Allfive mandatory negatives are present: advance without review, shared
interviewer overlap, over-band offer, withdrawn-but-scheduled interview and
irrelevant evaluation criterion. Shared overlaps legitimately produce findings
for both affected interviews. Clean baseline false positives0; duplicate
findings0; unexpected IDs and missed scenarios empty. Packaged files and new
standalone detector/evaluator executions agree exactly. These are controlled
synthetic-case results, not generalization/real-world accuracy claims. There is
no invented true-negative universe or accuracy percentage.

## 11. Two independent FULL end-to-end runs

Each fresh run generates its own valid complete baseline, all24-table exports,
three fresh restores with original comparisons, linked observations, separate
truth, detection/evaluation, manifest and privacy checks. Seed20261022;
all68 artifact files (including compressed seed/texts, observations/truth/findings/
metrics and manifest) match exact bytes and SHA/size. All89575 typed rows,
24 per-table hashes and aggregate hash match. Entire stable manifests are equal.
No mismatch was ignored. Timings/host paths/temp names stay outside the package.

- manifest.json: `7116c3a3e3547dad3be90c2c416f7f8a5ff292fe1e9b5be08fb82460b900a420`
- baseline/sql/seed.sql.gz: `4dfb3d8d7275b00a5434e6dbeabacf1b257456fee09930530bf9fe8a5c3df7d7`
- anomalies/input/observations.json: `75e0ef87e9cdeeb69fe5c4c8c5b9b13b217d2f7935097f27d5321670928cc72c`
- anomalies/truth/ground_truth.csv: `860469ee6b8ff4ff29f5fbdbe6055e301ee4326c7417b6c079246f33f4bf793d`
- anomalies/truth/ground_truth.json: `205b31bdb6abce3c9c84889f658b7e64ac710ef5102dbadf7431307d660e4688`
- anomalies/reports/findings.json: `2d82364a52885e20f37af09402f02f036436184c55310a14feed100efd787059`
- anomalies/reports/evaluation.json: `7722e789b14b0f7ca30d6a9075bdb02096944d4ba7afd2a6732d635191dd365d`

Aggregate: `7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb`. Full replay evidence: docs/phase07/reproducibility-evidence.json, SHA256 `4b99cdbd8c69d38d2d41eea6a73a9cd0851016a04c35c216ccaa38cbcba10140`. Combined measured elapsed 101.976450s.

## 12. Manifest verification and provenance

Runtime source commit: `50bbcfe8821d4a688b1a3725eba70a4bc29e1025`. Later data/docs commits preserve those exact tool source fingerprints and cannot cause a circular regeneration requirement.

Manifest version1/exporter1/schema2; schema SHA `75c10e0264a798ff36e6ffae4c076483dc04247e9c8a5051eead036cacab1c6f`; config SHA `7259924f35d71356b6c14dae9d42398cc87346a90cd52ea5bab3511dbb9ba4b7`.

Manifest records profile/seed/logical origin, configuration, generator commit,
all runtime source fingerprints, runtime prerequisites, eleven core entities,
actual FK dependencies, counts/per-table/aggregate hashes, formats, synthetic
provenance, every artifact size/SHA and validation/anomaly/replay references.
Inventory excludes only manifest itself; replay measurements are external under
docs/phase07 to avoid circular hashes. Verification checked all67 inventory
entries, exact file set, config/schema/catalog consistency, code fingerprints,
privacy, restores and anomaly replay. Git attributes preserve exported bytes.

All candidate identities and recruitment records are synthetic. No real candidate
resumes/contacts, scraped profiles, confidential records or external personal
datasets were used. external_datasets/vendored_dependencies are empty. No invented
source URL/license/retrieval date/third-party attribution. The project uses the
locally supplied CPython stdlib/SQLite runtime; no external core solution or
third-party project library was copied. Private challenge-source identities are
referenced by docs/phase01/sources.json; actual input files remain ignored.

## 13. Actual commands and results

Commands were run at the project root unless noted. Logs under ignored tmp/ are
local diagnostics; summaries/log hashes are preserved in reviewer-verification.json.
Meaningful inspection commands also included git status/log/diff/show/ls-files,
rg searches, file reads, schema/index/trigger metadata queries and actual source
extraction. No cloud/network/public API service was needed.

```sh
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
# Final:208 tests,93.306s, OK, exit0 (all183 previous +25 new).
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
# PASS: every dictionary field/constraint matches annotated SQL/SQLite.
PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh
# PASS:4 shell checks +3 Python groups; requires exact ignored assignment files.
PYTHONPATH=src .venv/bin/python3 scripts/verify_deliverable_reproducibility.py --profile full --seed 20261022 --directory output/phase07/repro-final-20261022
# PASS:2 full builds,68 identical files,89575 typed records,101.976450s, exit0.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/phase07/final-package-verify
# PASS:67 inventory entries,all3 restores,linked anomaly replay;16.774378s,exit0.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format sql --database output/phase07/manual-restored.sqlite3
# PASS: exact canonical/99 checks,FK+recursive ON;exit0.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.evaluation_checks --database output/phase07/manual-restored.sqlite3 --profile full --seed 20261022
# PASS:99 detailed domain checks,exit0.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/phase07/manual-restored.sqlite3 --observations artifacts/anomalies/input/observations.json
#30 expected findings,structure passes,semantic_valid=false;exit0.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables evaluate --directory artifacts/anomalies --database output/phase07/manual-restored.sqlite3
# Exact packaged metrics reproduced:30TP/0FP/0FN,exit0.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables export --baseline output/phase07/manual-restored.sqlite3 --profile full --seed 20261022 --directory output/phase07/manual-exports
# PASS:all24 tables/3formats/catalog;canonical unchanged,exit0.
du -sk artifacts
#25048 KiB allocated;sum of actual file sizes25495764 bytes.
```

Actual clean-reviewer test: extracted git archive HEAD into a new ignored
directory, asserted all68 artifacts and no private assignment files/.git/venv,
then ran from that archive:

```sh
python3 -m venv .venv
.venv/bin/python3 --version
#Python3.14.5
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/review-verification
#PASS:all3 imports/canonical/manifest/anomalies,exit0.
```

Archive revision `ea74a975a43ca7967c864dde02a3e2d136443c28`; verification measured 18.519433s. No private PDFs, preexisting environment or network needed for runtime review. The maintainer-only source smoke honestly requires the private files; it is not a runtime requirement.

New tests cover all table/header/order/field exports; CSV NULL/literal backslash/
empty/Unicode/quotes/CRLF/NUL; exact large int64 values; JSON types/opaque text;
SQL escaping/fresh seed/metadata/protections; PK/FK/domain/every-row/hash equality;
gzip determinism; manifest integrity; actual packaged detection/metrics;
independent starter byte replay; overwrite/symlink/failed cleanup; checksum,
JSON bool, updated-checksum FK and duplicate metadata corruption rejection;
privacy pattern positives and unlisted-file rejection. Full-scale exact counts,
row comparisons and two complete builds were additionally executed, not replaced
by starter tests.

Observed failures/checkpoints are retained honestly: first starter package failed
on a missing sqlite_schema record for an implicit WITHOUT ROWID index. Fixed new
aggregation code, added regression, no old business logic changed and no partial
package published. Initial24 tests passed6.145s but emitted test-only unclosed
connection warnings; explicit closes fixed them. Combined208 checkpoint passed
97.508s; final208 passed93.306s after final provenance/evaluator checks. A later
maintenance source-row assertion included repeated historical overlays and failed
its75 expectation; restricting selection to the original source sections passed
all75 unchanged rows. These are not remaining runtime/data errors.

## 14. Actual performance measurements

Seconds measured locally using perf_counter. Export measurements include their
compression work. Anomaly measurement includes generation/detection/evaluation;
component categories are not an external benchmark or guaranteed additive budget.

| Operation | Run1 seconds | Run2 seconds |
| --- | ---: | ---: |
| Baseline generation | 22.608130 | 21.222815 |
| CSV export | 0.757764 | 0.767186 |
| JSON export | 0.736905 | 0.621944 |
| SQL export | 0.771164 | 0.646020 |
| Baseline validation | 1.872102 | 1.909334 |
| Anomaly generation/detection/evaluation | 8.657549 | 8.314350 |
| Total package | 51.379010 | 49.860275 |
| CSV import | 2.886281 | 2.993617 |
| CSV validation | 1.768199 | 1.773389 |
| JSON import | 3.177406 | 2.797624 |
| JSON validation | 1.969666 | 1.776268 |
| SQL import | 3.917775 | 4.541973 |
| SQL validation | 1.767461 | 2.158403 |

Standalone SQL restore4.421968s+validation2.143805s; standalone anomaly evaluation
2.824696s. Final package verification16.774378s; clean archive18.519433s. Combined
full replay101.976450s includes comparison overhead. CPU/peak-memory profiles
were not measured; no fabricated resource or fairness/generalization claims.

## 15. Source, dictionary, privacy and publication checks

All three official inputs exist/readable and were read completely. Problem
statement remains challenge specification; PDFs supply additional submission
requirements. Source files still match the recorded identities below. They are
not included in Git. No source was treated as authority to publish/contact.

| Source | Bytes | SHA256 |
| --- | ---: | --- |
| problem-statement.md | 7735 | 8faefed019161bb66ce6ea274accd7fdf6500622ea2fb71fc6f3d756de133ace |
| YottaFlex AI Candidate Project-FAQ.pdf | 14827 | b3486be5674d00a911e2998f1d89d79904629f8a1fac99bc58b62e37d2a21c7a |
| YottaFlex AI Candidate Project Submission Guidelines.pdf | 14753 | e26107381e39c901af6a92a0a89a7178604851291eaaf2f3016e146da6532e73 |

Dictionary --check passed. All prior table/field/constraint rows are unchanged;
only its generated header narrative now points to implemented workflows. It
covers209 fields with type/required/enums/units/PK/FK/uniqueness/rules and lifecycle
links. Export/import representation is documented in README/design/catalog.

Actual generated package scan:68 files,25,495,764 bytes, **zero findings**,
including decompressed gzip content. Candidate emails exactly match deterministic
candidate IDs at example.invalid; names are Synthetic Candidate six-digit
identities and Staff names use Synthetic prefix. No real resumes/private PDFs,
scraped profiles, credentials, unexpected binaries or oversized files included.
Actual staged review:75 data/evidence files,25,636,840 bytes,68 artifact blobs
exactly equal working bytes and manifest hashes; zero staged privacy findings.
Mandatory artifacts are not ignored; scratch SQLite and private source files
remain ignored. This does not claim scanners can guarantee privacy.

Whole-repository content review flags only these inherited private-path report
references (names/line numbers only, no private values repeated here):

| Historical file | First flagged line | Finding |
| --- | ---: | --- |
| reports/phase01-handoff.md | 15 | private_path |
| reports/phase01-resumed-handoff.md | 12 | private_path |
| reports/phase02-schema-handoff.md | 11 | private_path |
| reports/phase03-data-generation-handoff.md | 10 | private_path |
| reports/phase04-interview-workflow-handoff.md | 5 | private_path |
| reports/phase05-evaluation-offer-handoff.md | 4 | private_path |
| reports/phase06-anomaly-ground-truth-handoff.md | 5 | private_path |

These old reports/commits/prompts were preserved rather than silently altered.
They are a final human publication-review item. Therefore the entire historical
repository is **not declared public-safe**, even though all new Phase07 content
and the artifact package pass. Resolve by a separately authorized, transparent
privacy decision before any public release. Foundation smoke filename checks do
not replace this actual content scan.

## 16. Updated75-requirement coverage

Original source requirement wording is unchanged. docs/phase07/requirements-
acceptance.md supplies per-ID implementation/test/artifact/remaining-limit links.
Current status totals:57 IMPLEMENTED_VERIFIED;6 IMPLEMENTED_HUMAN_REVIEW_PENDING;
6 USER_RELEASE_GATE;1 CONDITIONAL_NOT_TRIGGERED;5 OPTIONAL_OR_PERMISSION.
TECH below means IMPLEMENTED_VERIFIED in that detailed overlay; HUMAN and RELEASE
are deliberately incomplete human/public acceptance items, not claimed passed.

| ID | Source requirement | Current status |
| --- | --- | --- |
| F01 | P Context/Workflow.3: track and approve requisitions, role criteria | TECH |
| F02 | P Workflow.3: synthetic candidates and applications | TECH |
| F03 | P Workflow.3/Acceptance: define/enforce stage transitions/gates | TECH |
| F04 | P Workflow.3: interviewer calendars | TECH |
| F05 | P Workflow.3/Acceptance: schedule panels without conflicts | TECH |
| F06 | P Workflow.3/Acceptance: structured rubric scorecards | TECH |
| F07 | P Workflow.3/Acceptance: offers within approved compensation bands, approvals/history auditable | TECH |
| F08 | P Objective: working end-to-end workflow, multiple related entities, conditional rules, exceptions | TECH |
| F09 | P Objective: key decisions/exceptions visible, traceability, measurable outputs/meaningful metrics | TECH |
| F10 | P Actors: employee/candidate, manager, HR, IT/operations, administrator | TECH |
| F11 | P Granular.4/Suggested: withdrawals, rescheduling, conflicting interviewers, incomplete scorecards | TECH |
| F12 | P Workflow.4/Entities: explicit state records/events, no overwritten history | TECH |
| D01 | P Entities/Granular.1: all eleven core entities | TECH |
| D02 | P Granular.1: every field's type, required/optional, allowed values, units, uniqueness, validation | TECH |
| D03 | P Entities: PK every entity, FK every relationship, validate all joins | TECH |
| D04 | P Entities: cardinalities, optional links, effective dates, lifecycle states | TECH |
| D05 | P Entities: N:M bridge tables | TECH |
| D06 | P Workflow.1-2/Granular.2: master/parent records before children/events using valid parent IDs | TECH |
| D07 | P IDs/Granular.3: REQ-2026-000001, CAND-000001, APP-<candidate-id>-<req-id>, INT-2026-000001, SCORE-<interview-id>-<reviewer-id>, OFF-2026-000001 | TECH |
| D08 | P Granular.3: immutable IDs, zero-padded counters, exact references across files | TECH |
| D09 | P Granular.4/Suggested + user: 200 requisitions, 5,000 candidates, 8,000 applications, 2,000 interviews | TECH |
| D10 | P Granular.4: fixed seed (example 20261022) | TECH |
| D11 | P Granular.4: parameterized scale, starter/full same generator | TECH |
| D12 | P Granular.5: valid baseline first, then labelled edge injection | TECH |
| D13 | P Entities: deliberate anomalies have issue_type/ground_truth, no unrelated corruption | TECH |
| D14 | P Workflow.5/Granular.6: outcomes and totals/balances/scores/statuses/dates from rules/source records | TECH |
| D15 | P Workflow.5: labels from documented rules, not independent random outcomes | TECH |
| D16 | P Granular.7/Review(f): separate ground_truth.csv/json; never input features | TECH |
| D17 | P Review(a): realistic distributions, meaningful variation | TECH |
| D18 | P Review(e): normal/boundary/failure/exception coverage | TECH |
| D19 | P Granular.9: CSV/JSON/SQL seed data | TECH |
| D20 | P Granular.9: README, schema/dictionary, generator command, seed, source manifest, validation summary | TECH |
| D21 | P Granular.10/Review(g): regenerate twice same seed, compare counts/checksums | TECH |
| D22 | P Review(b-d): consistent joins/dependencies/lifecycles, derived reconciliation | TECH |
| N01 | P Granular.5/Negatives.1: candidate forward without required review | TECH |
| N02 | P Negatives.2: interviewer double-booked | TECH |
| N03 | P Negatives.3: offer exceeds band | TECH |
| N04 | P Negatives.4: withdrawn candidate remains scheduled | TECH |
| N05 | P Negatives.5: evaluation includes irrelevant criteria | TECH |
| V01 | P Granular.8: PK uniqueness | TECH |
| V02 | P Granular.8: FK integrity | TECH |
| V03 | P Granular.8: allowed enums | TECH |
| V04 | P Granular.8: date ordering | TECH |
| V05 | P Granular.8: arithmetic reconciliation | TECH |
| V06 | P Granular.8: lifecycle transitions | TECH |
| V07 | P Granular.8: duplicates | TECH |
| V08 | P Acceptance: schedule/stage/rubric/offer audit | TECH |
| V09 | P Review/F Q9/G 01/04: demonstrate actual verification, environment/limitations | TECH |
| V10 | F Q8/user: suitable stack, free or local services; avoid huge/slow deps where possible | TECH |
| V11 | P Lawful Use/F Q12/user: no secrets, credentials, confidential/personal/sensitive/unauthorized proprietary data | HUMAN PENDING |
| V12 | P Review(g): lawful provenance | TECH |
| S01 | G 01/F Q9/P Before Submit: executable code, install/config/run/verify instructions, environment/limits | TECH |
| S02 | G 02/F Q3/P Submission: new dedicated public GitHub repository | RELEASE PENDING |
| S03 | F Q4/Q6/G 03: ALL prompts to EVERY AI tool; responses optional | HUMAN PENDING |
| S04 | F Q6: if no export, reasonable record and disclosed limits | HUMAN PENDING |
| S05 | G 03: AI acceleration/heavy reliance, human reviewed/changed/validated work | HUMAN PENDING |
| S06 | G 04/F Q11: reasoning, problem, assumptions, decisions/trade-offs, tests, limits, incomplete work/deviations/next steps | TECH |
| S07 | G 02: meaningful commits, understandable evolution/supporting context | TECH |
| S08 | F Q7: individual, AI/public resources allowed, no other-person implementation help | HUMAN PENDING |
| S09 | F Q5/Q7/G footer/P email: understand logic/design/deps/limits/every line; walkthrough readiness | HUMAN PENDING |
| S10 | F Q1/G window: 72 hours from send timestamp/timezone, artifact timestamps verify window | RELEASE PENDING |
| S11 | F Q2: early allowed, repo public/editable through deadline, latest version evaluated | RELEASE PENDING |
| S12 | F Q3: link from same recruitment email, follow instructions | RELEASE PENDING |
| S13 | P Submission: build locally, submit portal repo link before deadline once/final | RELEASE PENDING |
| S14 | P email: one repository has code/all requested; public visibility tested in private browser | RELEASE PENDING |
| S15 | F Q4: identifiable code/prompt/support directories; format not prescribed | TECH |
| S16 | F Q10: standard deps/small snippets allowed; no complete/core imported solution; licenses/attribution | TECH |
| S17 | F Q12: safe samples, local config, README setup | TECH |
| C01 | P Lawful Use: external data optional | OPTIONAL/PERMISSION |
| C02 | P Lawful Use: external source URL/version/date/license/terms/attribution/transforms/discarded fields and redistribution rights | NOT TRIGGERED |
| C03 | P Lawful Use: no access-control bypass or confidential/personal collection; uncertain suitability -> synthetic/schema inspiration | TECH |
| O01 | F Q9 hosted demo not mandatory | OPTIONAL/PERMISSION |
| O02 | F Q9 automated suite not generally mandatory | OPTIONAL/PERMISSION |
| O03 | F Q5/Q8 any AI tool/stack permitted | OPTIONAL/PERMISSION |
| O04 | No source mandates web/auth/microservices/dashboard | OPTIONAL/PERMISSION |

Technical implementation evidence: F/D in existing schema/generator/workflow/
evaluation/offers plus new exports; all99 restored checks; N01–05 in actual
observations/findings/truth; V in validators/privacy/tests/replay; S technical
items in README/design/journal/scoped Git. Human S03–05/S08–09 include complete
AI history/all-tools audit, actual line understanding/independent verification;
V11 additionally flags inherited paths. S02/S10–14 public-repo/window/channel/
final-one-submission/incognito gates remain outside Phase07 authority. External
corpus C02 untriggered; optional hosting/auth/UI/in-application AI is not invented.

## 17. AI prompt history and human-review status

Full known project prompts P001–P010 are retained in docs/phase01/journal.md and
linked verbatim phase prompt files. P010 is all23 sections/18667 bytes, SHA256
5970599c88660b19a8e05c59efa27d80d61e974ea711457f9ef8b7d6ca35810e,
byte-identical to the human-provided attachment. Existing prompts were preserved.
No additional human AI prompts, other implementers/subagents, model services,
external personal datasets or imported core solution were used in this phase.

Codex generated code/tests/docs and ran all listed checks. The user provided
requirements and conditional progression approval. That is not proof of personal
human testing, every-line understanding, policy agreement or all-other-tools/chat
prompt export. Journal H030–H035 keeps these distinctions and final human gates.
Human should disclose any other AI tools/chats not visible in this local record;
responses are optional, complete prompts are required. No human acceptance is
fabricated. Available exports/reconstructed-history limits remain disclosed.

## 18. Remaining risks and unresolved questions

1. Seven historical local-path references and all historical content need final
   human privacy/ownership review before public availability. New artifacts are
   separately clean; scanner coverage is not an absolute guarantee.
2. Human personal tests/line understanding/explain-back/policy review and complete
   all-tools AI prompt audit remain pending. Controlled metric perfection is not
   a real-world validation claim.
3. Original invitation send timestamp/timezone, round naming and portal-versus-
   same-email submission instructions remain human administrative questions;
   supplied deadline is preserved without inventing a resolution.
4. Exact CPython3.14.5 prerequisite must be locally available. Byte replay uses
   the verified SQLite/compression environment; alternate runtime verification
   is needed before promising identical bytes elsewhere. SQLite binary files
   are intentionally not compared or published.
5. JSON imports use one-table memory; gzip has CPU cost; no peak RSS measured.
   CLI SQL import is for trusted reviewed package SQL, not arbitrary hostile SQL;
   hashes prove integrity, not signed publisher authenticity.
6. Existing immutable-history/configuration correction policies and semantic
   observation representation limits remain documented. This phase changes
   neither the baseline nor old valid business rules. Unowned files/outputs are
   refused rather than overwritten.

There is no unresolved Phase07 implementation/test/reproducibility blocker.
Public release remains separate and not authorized by this report.

## 19. Local Git state and commits

- Implementation: `50bbcfe8821d4a688b1a3725eba70a4bc29e1025` — feat: export and verify complete reproducible dataset packages.
- Data/evidence: `ea74a975a43ca7967c864dde02a3e2d136443c28` — data: add verified full synthetic exports and anomaly artifacts.
- This handoff/clean-archive evidence is committed separately as a documentation
  closure. Its actual final commit hash and postcommit working-tree result are
  appended to the downloadable copy, avoiding a self-referential commit hash.

Branch remains codex/phase-01-foundation. Isolated Git root and previous commits
preserved; no reset/squash/merge/remotes/push. Data commit completed with clean
working tree before the final report/evidence update. At data staging all75
files were reviewed for sizes/privacy/exact blob hashes. Final report/evidence
will be similarly staged/reviewed before the documentation commit. Final closure
records the actual clean/dirty result rather than predicting it.

## 20. Reviewer reproduction instructions

From a fresh local clone with the pinned interpreter available:

```sh
python3 --version
python3 -m venv .venv
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables verify --directory artifacts --work output/review-verification
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables restore --directory artifacts/baseline --format sql --database output/restored.sqlite3
PYTHONPATH=src .venv/bin/python3 -m yottaflex.evaluation_checks --database output/restored.sqlite3 --profile full --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/restored.sqlite3 --observations artifacts/anomalies/input/observations.json
PYTHONPATH=src .venv/bin/python3 -m yottaflex.deliverables evaluate --directory artifacts/anomalies --database output/restored.sqlite3
PYTHONPATH=src .venv/bin/python3 scripts/verify_deliverable_reproducibility.py --profile full --seed 20261022 --directory output/two-full-packages
```

Use new output names on each run; existing outputs are deliberately refused.
Build an individual package with deliverables build --profile full --seed 20261022
(using separate arguments, as the exact README command shows). Inspect manifest,
baseline/round-trip-verification.json and anomalies/reports/package-verification.json.
Private source PDFs are not needed for these runtime/tests; optional maintainer
smoke needs them. No API key, database server or package download is required.

## 21. Proposed Phase08 audit recommendations — not executed

After user review/explicit next-phase authorization: independently inspect source
requirements/all75 statuses, run personal reviewer commands and explain-back,
reconcile administrative deadline/channel/window questions, review all-tools AI
history, decide transparently how to handle inherited historical paths, verify
final tracked artifact inventory and absence of private data, then prepare the
single-repository release narrative/checklist. Any public remote/push/public-
visibility/incognito check/final portal or email submission/recruiter contact
requires separate explicit authorization. Do not infer it from this handoff.

**Stop after Phase07. No Phase08 implementation/publication/submission performed.**

