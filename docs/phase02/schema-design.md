# Phase 02 relational design and integrity boundary

User approval: the complete Phase 02 prompt in prompt.md explicitly approves
Phase 01 progression. This phase implements storage/dictionary/integrity tests
only. No generator, full dataset, workflow service, scheduler, scorer, anomaly
injection, exporter, web UI or REST API has been implemented.

## Implemented inventory

Eleven required core tables: Requisition, HiringManager, Candidate, Application,
SkillRequirement, InterviewPanel, Availability, Interview, Scorecard, Offer,
Approval. Supporting tables: Staff, CandidateSkill, PanelMember,
InterviewParticipant, ScorecardItem. Seven typed history tables: RequisitionEvent,
ApplicationEvent, InterviewEvent, OfferEvent, ApprovalEvent, ScorecardEvent,
CandidateEvent. SchemaMetadata is the initialization singleton. Total 24 tables,
207 fields, 45 FK groups (51 linked columns), 42 protection triggers.

Staff supplies FK-resolved interviewers, approvers and audit actors. Primary role
is one enum; panel membership supplies an interview assignment, not a new identity.
System events reference a synthetic Staff row with role=system; candidate-driven
events can additionally reference the Candidate origin actor. No real identity
or actual system actor is inserted by initialization.

## Explicit refinements of Phase 01 proposals

- UTC INTEGER epoch seconds replace the proposed ISO text; range 0..253402300799,
  whole seconds, no float/date strings. Phase 02 explicitly permits this choice.
  Effective/booking intervals remain half-open, optional valid_to is open-ended.
- Application/panel requisition join keys are repeated in Interview and Offer
  with composite FKs to prevent structurally inconsistent joins. These redundant
  columns are constrained, not independent sources of truth.
- Offer references immutable RequisitionEvent band/currency snapshot, preserving
  historical meaning. Currency and requisition match structurally; actual offer
  band eligibility and approved-event status remain deferred business checks.
- Scorecard has composite FK to assigned InterviewParticipant. ScorecardItem has
  valid criterion FK and scalar range/completion checks; criterion applicability,
  rubric version/weight reconciliation and reviewer-role eligibility are deferred.
- Partial UNIQUE on final offers in pending_approval/approved/sent/accepted enforces
  at most one such offer per application. Draft/nonfinal/terminal revisions remain.
- SchemaMetadata is STRICT WITHOUT ROWID: an expanded test exposed SQLite's NULL
  auto-allocation for ordinary INTEGER PRIMARY KEY; WITHOUT ROWID prevents it.
- Current lifecycle states are enums, not an implemented transition graph.
- Each typed event includes a constrained snapshot_json object to retain old/new
  slots, item scores or other non-key details. SQL verifies JSON/object shape;
  future workflow code must validate content, keep truth labels out, and append
  snapshots atomically. This uses built-in SQLite JSON, no extra dependency.

These are reasoned implementation choices, not additional source requirements.
Full columns, allowed values, defaults, units, keys, uniqueness, meaning and exact
constraints are in ../data-dictionary.md, rendered from schema annotations plus
SQLite introspection. A freshness test prevents silent documentation drift.

## Database-enforced vs deferred business rules

| Database enforced and tested | Later business rule / future coverage |
| --- | --- |
| STRICT types, NOT NULL, PKs, FK groups, natural uniqueness | Realistic synthetic distributions, full volumes and cross-export validation |
| Exact six mandatory ID patterns, supporting prefixes, immutable keys | Seeded counter allocation and cross-format deterministic regeneration |
| Epoch ranges, positive intervals, same-row causal ordering | Interviewer overlaps, calendar coverage, effective membership, withdrawal cancellation (N02/N04) |
| Enum membership and same-row decision/submission/withdrawal timestamp consistency | Legal stage/role transitions and completed-review gates (N01) |
| Integer monetary/rubric ranges, coherent band min/max, matching snapshot currency/requisition | Offer amount vs historical approved band and authorized approver (N03) |
| Reviewer assignment FK, existing criterion FK, unique reviewer pairs | Required-review completeness, role-relevant criteria/version, weighted total calculation (N05) |
| Typed event FK/sequence uniqueness and immutable event/participant rows | Sequence continuity, projection/event reconciliation and atomic workflow mutations |
| Structural storage for states/revisions/events | Full scenario injection, ground truth, detection/evaluation/export/replay |

No deferred rule is claimed to pass. Future transactional services must enforce
guards BEFORE projection/event commits. Valid baseline and labelled anomaly
artifacts remain separate; a future fixture injector must not weaken normal rules.

## Safe initialization and evolution

Use `connect` for every supported connection (FK/recursive triggers ON), then
`initialize`. Fresh v0 database only; deterministic SQL, no generated business
rows. BEGIN IMMEDIATE serializes emptiness/version checks and DDL. Exact v1 repeat
verifies schema source/catalog fingerprints and existing FK integrity; data is
preserved. Caller transactions, unknown populated schemas/versions and drift are
refused. DDL errors roll back instead of leaving partial tables/version metadata.

The small module has only schema initialization CLI, not a recruiting workflow
CLI. Example: `PYTHONPATH=src .venv/bin/python3 -m yottaflex.db tmp/example.sqlite3`.
The parent directory must exist. Database files remain ignored. No automatic
migrations/reset/delete switch exists. Any future DDL change, even source comment
edits affecting the fingerprint, needs explicit versioning/migration or a fresh
disposable local database. Never use a reset as a substitute for data migration.

Triggers/fingerprints protect ordinary application use, not a malicious database
owner who can drop triggers/change PRAGMAs. SQLite 3.38+ is required for STRICT;
the project interpreter pin is CPython 3.14.5. No third-party dependency added.

## Verification and next gate

Run `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v`,
`PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check`, and
`PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh`. Fixtures are 24 literal domain/
support/history rows plus metadata, not a dataset generator. Isolated in-memory
and temporary-file databases are used; no production/private records.

Phase 03 recommendation after review: deterministic config/ID allocation and
valid baseline generation against this schema, then full-volume integrity checks.
Other business workflows, negative fixtures, exports and evaluation need their
own authorized scope. Stop after Phase 02 for human review.
