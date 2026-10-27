# YottaFlex AI — PHASE 02: RELATIONAL DATABASE SCHEMA, DATA DICTIONARY & INTEGRITY TESTS

You are continuing the existing YottaFlex AI 72-Hour Code Challenge project.

**Phase 01 has been reviewed and approved for progression.**

The objective of Phase 02 is to implement the complete relational database schema and field-level data dictionary, with strong integrity constraints and focused database tests.

Do not begin synthetic data generation or workflow implementation in this phase.

## 1. First inspect the existing project

Before changing anything:

1. Read `AGENTS.md`, `README.md`, and all Phase 01 architecture, requirements, model and risk documents.
2. Read the complete problem statement and both official PDFs from `docs/assignment/`.
3. Inspect the current Git branch, recent commits and working-tree state.
4. Review the existing architecture and repository structure.
5. Identify existing conventions and constraints that must be preserved.

Do not rewrite or unnecessarily refactor Phase 01 work.

Treat the 75-row requirements traceability matrix as the project coverage baseline, but verify relevant requirements against the original source documents.

## 2. Strict scope of Phase 02

Implement:

- Complete SQLite relational schema.
- All eleven required core entities.
- Necessary supporting entities and bridge tables.
- Primary keys, foreign keys and uniqueness constraints.
- Applicable check constraints.
- Lifecycle status definitions.
- Effective-date and interval conventions.
- Append-only event-history schema.
- Deterministic ID-format definitions.
- Complete field-level data dictionary.
- Focused schema and integrity tests.
- Updated documentation and AI prompt journal.

Do not implement:

- Synthetic data generation.
- Full dataset creation.
- Stage-transition business operations.
- Scheduling algorithms.
- Scorecard calculation engines.
- Offer workflow logic.
- Negative-case injection.
- CSV/JSON/SQL export engines.
- Web frontend or REST API.

These belong to later phases.

## 3. Core entity schema

Implement all eleven mandatory entities:

1. Requisition
2. HiringManager
3. Candidate
4. Application
5. SkillRequirement
6. InterviewPanel
7. Availability
8. Interview
9. Scorecard
10. Offer
11. Approval

Every table must have an explicit primary key and appropriate lifecycle/status columns.

Required relationships must use foreign keys.

Implement supporting tables only where justified, such as:

- Staff
- PanelMember
- InterviewParticipant
- ScorecardItem
- RequisitionEvent
- ApplicationEvent
- InterviewEvent
- OfferEvent
- ApprovalEvent, if needed

Use clear, consistent names.

Do not create unnecessary abstraction layers or generic frameworks.

## 4. Relational design and cardinality

Support the following:

- HiringManager 1:N Requisition.
- Candidate N:M Requisition through Application.
- Requisition 1:N SkillRequirement.
- Requisition 1:N InterviewPanel.
- InterviewPanel N:M Staff through PanelMember.
- Staff 1:N Availability.
- Application 1:N Interview.
- InterviewPanel 1:N Interview.
- Interview N:M Staff through immutable InterviewParticipant records.
- Interview 1:N Scorecard, with one scorecard per assigned reviewer.
- Scorecard 1:N ScorecardItem.
- Application 1:N Offer, with at most one active final offer.
- Requisition and Offer approvals linked to their respective subjects.

Document optional relationships, lifecycle conditions and effective-date semantics.

Ensure a reviewer can clearly understand every join and relationship.

## 5. Constraints and SQLite integrity

Implement constraints for all practical structural invariants:

- Primary-key uniqueness.
- Foreign-key integrity.
- Required non-null fields.
- Unique natural keys where applicable.
- Allowed enum/status values.
- Valid date and interval representations.
- Positive interview durations.
- Valid compensation bands.
- Consistent monetary units.
- Score values inside documented rubric boundaries.
- Unique candidate/requisition application pairs.
- Unique interview/reviewer scorecard pairs.
- Appropriate scorecard/criterion relationships.
- Valid approval target relationships.

Use integer minor currency units where possible to avoid floating-point compensation errors.

Define a single timestamp convention, preferably UTC ISO-8601 or UTC epoch integers, and document it.

Enable `PRAGMA foreign_keys = ON` for every database connection.

Do not assume CHECK constraints alone enforce all business rules.

Cross-record scheduling conflicts, role-specific transitions, completed-review gates and temporal overlaps may require transactional Python validation in future phases.

Explicitly distinguish database-enforced constraints from business-level rules.

## 6. Deterministic ID conventions

Support these exact mandatory formats:

- `REQ-2026-000001`
- `CAND-000001`
- `APP-<candidate-id>-<req-id>`
- `INT-2026-000001`
- `SCORE-<interview-id>-<reviewer-id>`
- `OFF-2026-000001`

Specify deterministic ID validation functions or patterns.

IDs must be immutable and consistently represented.

Document reasonable naming conventions for supporting entities.

Avoid relying on randomly generated UUIDs for the required identifiers.

## 7. Event history and traceability

Create an explicit, append-only event-history design for meaningful state changes.

History records should retain:

- Unique event identity.
- Affected entity ID.
- Event type.
- Previous state, where relevant.
- New state, where relevant.
- Actor ID.
- Event timestamp.
- Relevant reason or decision code.
- Correlation/reference ID when useful.

Document the relationship between current-state projections and historical events.

Never overwrite or delete historical events as part of normal lifecycle operations.

The actual workflow mutations and transaction handling will be implemented in later phases.

## 8. Data dictionary

Create:

`docs/data-dictionary.md`

For every field in every core, support, bridge and event table, document:

- Field name.
- Data type.
- Required or optional.
- Allowed values.
- Units, where applicable.
- Default.
- Primary-key / foreign-key information.
- Uniqueness rules.
- Validation constraints.
- Meaning and business purpose.

Also include:

- Entity relationships.
- Cardinalities.
- Lifecycle states.
- Effective dates.
- Timestamp conventions.
- Monetary representation.
- Rubric score representation.
- Nullability and optional relationships.
- Schema versioning strategy.

Ensure the dictionary agrees exactly with the implemented SQL.

## 9. Schema implementation requirements

Use Python standard library and SQLite, consistent with the existing Phase 01 architecture.

Prefer transparent SQL schema files and a small database initialization module.

Keep initialization deterministic and safe.

Schema initialization must:

- Work on a fresh database.
- Reject invalid structural data.
- Enable foreign-key checks.
- Be testable without production/synthetic generated data.
- Avoid accidental destructive resets of an existing populated database.

Document whether initialization is idempotent and how future schema changes will be handled.

Avoid introducing third-party runtime dependencies unless strictly necessary and justified.

## 10. Automated schema tests

Use `unittest` from the Python standard library unless the existing project specifies another appropriate testing approach.

Implement and execute tests verifying:

1. All eleven core tables exist.
2. Every core table has a primary key.
3. Every required relationship has the appropriate foreign key.
4. Invalid foreign-key references are rejected.
5. Duplicate primary keys are rejected.
6. Duplicate candidate/requisition application pairs are rejected.
7. Invalid statuses are rejected.
8. Invalid compensation ranges are rejected.
9. Invalid rubric ranges are rejected.
10. Invalid date/interval values are rejected where enforced by the schema.
11. Unique scorecard reviewer pairs are enforced.
12. Approval target constraints work.
13. SQL initialization succeeds on an empty database.
14. Safe repeated initialization does not delete existing data.
15. Event-history tables support audit records and prevent unintended changes where appropriate.
16. Basic cross-table references resolve correctly.
17. Tests work with an isolated temporary database.
18. Existing Phase 01 smoke tests continue passing.

Use minimal synthetic fixtures exclusively for testing integrity constraints.

Do not introduce the full dataset generator.

For business rules intentionally deferred to later phases, document their future test coverage instead of claiming they already pass.

## 11. Update requirements traceability

Update the existing requirements matrix.

For each applicable requirement, clearly indicate:

- Implemented.
- Tested.
- Documented.
- Deferred.
- Blocked, if applicable.

Do not mark a requirement as fully satisfied simply because the database supports it structurally.

Do not modify unrelated requirements or rewrite historical evidence.

## 12. AI transparency and development history

Record this complete Phase 02 prompt in the project's AI prompt history.

Record any additional prompts used during implementation.

Document:

- What AI implemented.
- Which decisions were inferred or proposed.
- What tests AI executed.
- What remains pending human verification.

Do not fabricate human review or testing evidence.

## 13. Git and file safety

Preserve existing branches, commits and completed work.

Make only Phase 02-related changes.

Avoid unrelated refactoring.

Do not modify sensitive or private assignment-source documents unnecessarily.

Do not introduce real personal information or credentials.

Run relevant tests before committing.

Create one or more meaningful local commits after successful verification.

Do not push, merge, create a GitHub repository, contact recruiters or submit anything.

## 14. Final acceptance criteria

Phase 02 is complete only when:

- All eleven core tables are implemented.
- Required supporting relationships are modeled.
- Every entity has its primary key.
- Appropriate foreign-key constraints are enforced.
- The data dictionary covers every schema field.
- Lifecycle states and effective-date conventions are documented.
- History tables are defined.
- All implemented structural constraints have passing tests.
- The schema can be initialized in an empty database.
- Existing Phase 01 checks still pass.
- No full generator or later-phase workflow was prematurely implemented.
- Documentation and AI history are updated.

## 15. Final handoff report

Create a complete Markdown report at:

`reports/phase02-schema-handoff.md`

Include:

1. Phase 02 PASS / PARTIAL / FAIL.
2. Executive summary.
3. All created and modified files.
4. Database table inventory.
5. Eleven-entity coverage matrix.
6. PK/FK relationship summary.
7. Schema design decisions and trade-offs.
8. Exact test commands executed.
9. Actual test results.
10. Database constraints versus deferred business rules.
11. Known limitations and risks.
12. Requirements matrix changes.
13. AI usage disclosure.
14. Local Git commit hashes and working-tree status.
15. Recommended Phase 03 scope.

The report must be self-contained enough to review in a different ChatGPT conversation without losing essential context.

**STOP after Phase 02. Do not proceed to Phase 03 without my review.**

Focus on correctness, simplicity, maintainability and explicit evidence. Do not invent results or claim completion of unimplemented functionality.