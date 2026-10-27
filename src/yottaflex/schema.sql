-- YottaFlex schema version 2. Static DDL; initialize through yottaflex.db.
-- STRICT storage; timestamps UTC epoch integer seconds; no wall-clock defaults.
-- Column comments: business meaning | units. See generated docs/data-dictionary.md.

-- table: Singleton version and schema fingerprints; no domain data
CREATE TABLE SchemaMetadata (
    singleton INTEGER NOT NULL CHECK (singleton = 1), -- Singleton metadata key | count
    schema_version INTEGER NOT NULL CHECK (schema_version = 2), -- Explicit migration version | count
    source_sha256 TEXT NOT NULL CHECK (length(source_sha256) = 64 AND source_sha256 NOT GLOB '*[^0-9a-f]*'), -- SHA256 of exact schema.sql bytes | none
    catalog_sha256 TEXT NOT NULL CHECK (length(catalog_sha256) = 64 AND catalog_sha256 NOT GLOB '*[^0-9a-f]*'), -- SHA256 of canonical sqlite_schema catalog | none
    PRIMARY KEY (singleton)
) STRICT, WITHOUT ROWID;

-- table: Synthetic staff/system actors and interviewers
CREATE TABLE Staff (
    staff_id TEXT NOT NULL PRIMARY KEY CHECK (staff_id GLOB 'STAFF-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(staff_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0), -- Synthetic display name, never a real person | none
    role TEXT NOT NULL CHECK (role IN ('manager', 'hr', 'it_operations', 'administrator', 'interviewer', 'system')), -- Primary actor role; panel membership supplies interviewing assignment | none
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')), -- Current lifecycle projection | none
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Manager profile with one Staff identity
CREATE TABLE HiringManager (
    hiring_manager_id TEXT NOT NULL PRIMARY KEY CHECK (hiring_manager_id GLOB 'HM-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(hiring_manager_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    staff_id TEXT NOT NULL, -- Manager staff identity | none
    department TEXT NOT NULL CHECK (length(trim(department)) > 0), -- Synthetic organizational department | none
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')), -- Manager profile lifecycle | none
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (staff_id),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Synthetic candidate profiles; no real candidate records
CREATE TABLE Candidate (
    candidate_id TEXT NOT NULL PRIMARY KEY CHECK (candidate_id GLOB 'CAND-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(candidate_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    display_name TEXT NOT NULL CHECK (length(trim(display_name)) > 0), -- Synthetic display name | none
    experience_years INTEGER NOT NULL CHECK (experience_years BETWEEN 0 AND 50), -- Synthetic professional experience, not inferred from outcomes | whole years
    contact_email TEXT COLLATE NOCASE CHECK (contact_email IS NULL OR (length(contact_email) > 16 AND contact_email LIKE '%@example.invalid')), -- Optional non-routable synthetic contact | none
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'withdrawn')), -- Global candidate lifecycle | none
    created_at INTEGER NOT NULL CHECK (created_at BETWEEN 0 AND 253402300799), -- Profile creation time | UTC epoch seconds; whole seconds, 1970..9999
    withdrawn_at INTEGER CHECK (withdrawn_at BETWEEN 0 AND 253402300799), -- Global withdrawal time | UTC epoch seconds; whole seconds, 1970..9999
    UNIQUE (contact_email),
    CHECK ((status = 'withdrawn') = (withdrawn_at IS NOT NULL)),
    CHECK (withdrawn_at IS NULL OR withdrawn_at >= created_at)
) STRICT;

-- table: Structured candidate skill levels
CREATE TABLE CandidateSkill (
    candidate_id TEXT NOT NULL, -- Candidate owner | none
    skill_key TEXT NOT NULL CHECK (length(trim(skill_key)) > 0), -- Canonical synthetic skill key | none
    level INTEGER NOT NULL CHECK (level BETWEEN 0 AND 4), -- Declared proficiency | rubric points, integer 0..4
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')), -- Profile skill lifecycle | none
    PRIMARY KEY (candidate_id, skill_key),
    FOREIGN KEY (candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

-- table: Role, compensation band and lifecycle projection
CREATE TABLE Requisition (
    requisition_id TEXT NOT NULL PRIMARY KEY CHECK (requisition_id GLOB 'REQ-2026-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(requisition_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    hiring_manager_id TEXT NOT NULL, -- Owning hiring manager | none
    title TEXT NOT NULL CHECK (length(trim(title)) > 0), -- Synthetic role title | none
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'open', 'filled', 'closed', 'cancelled')), -- Requisition lifecycle | none
    band_min_minor INTEGER NOT NULL CHECK (band_min_minor >= 0), -- Minimum approved/proposed compensation | integer minor currency units
    band_max_minor INTEGER NOT NULL CHECK (band_max_minor >= 0), -- Maximum approved/proposed compensation | integer minor currency units
    currency TEXT NOT NULL CHECK (currency GLOB '[A-Z][A-Z][A-Z]'), -- Three-uppercase-letter currency code; dictionary validity not independently looked up | currency code; amounts in hundredths
    policy_version INTEGER NOT NULL DEFAULT 1 CHECK (policy_version >= 1), -- Stage/review policy version | count
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (hiring_manager_id) REFERENCES HiringManager (hiring_manager_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK (band_max_minor >= band_min_minor),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Versioned requisition criteria and rubric weights
CREATE TABLE SkillRequirement (
    skill_requirement_id TEXT NOT NULL PRIMARY KEY CHECK (skill_requirement_id GLOB 'SKILL-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(skill_requirement_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    requisition_id TEXT NOT NULL, -- Owning requisition | none
    criterion_key TEXT NOT NULL CHECK (length(trim(criterion_key)) > 0), -- Canonical role criterion key | none
    description TEXT NOT NULL CHECK (length(trim(description)) > 0), -- Criterion meaning and expected evidence | none
    is_required INTEGER NOT NULL DEFAULT 1 CHECK (is_required IN (0, 1)), -- Required criterion indicator | boolean 0/1
    weight_basis_points INTEGER NOT NULL CHECK (weight_basis_points BETWEEN 1 AND 10000), -- Declared criterion weight | basis points; 10000 = 100 percent
    min_proficiency INTEGER NOT NULL CHECK (min_proficiency BETWEEN 0 AND 4), -- Minimum role-specific skill proficiency | integer rubric points 0..4
    rubric_version INTEGER NOT NULL DEFAULT 1 CHECK (rubric_version >= 1), -- Immutable criterion version key | count
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'retired')), -- Criterion lifecycle | none
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (requisition_id) REFERENCES Requisition (requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (requisition_id, criterion_key, rubric_version),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Candidate/requisition relationship and stage projection
CREATE TABLE Application (
    application_id TEXT NOT NULL PRIMARY KEY CHECK (application_id = 'APP-' || candidate_id || '-' || requisition_id), -- Immutable literal composite application identity | none
    candidate_id TEXT NOT NULL, -- Applying candidate | none
    requisition_id TEXT NOT NULL, -- Target requisition | none
    status TEXT NOT NULL DEFAULT 'applied' CHECK (status IN ('applied', 'screening', 'interviewing', 'reviewed', 'offer', 'hired', 'rejected', 'withdrawn')), -- Application stage/lifecycle | none
    applied_at INTEGER NOT NULL CHECK (applied_at BETWEEN 0 AND 253402300799), -- Application creation time | UTC epoch seconds; whole seconds, 1970..9999
    updated_at INTEGER NOT NULL CHECK (updated_at BETWEEN 0 AND 253402300799), -- Projection last-change time | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (requisition_id) REFERENCES Requisition (requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (candidate_id, requisition_id),
    UNIQUE (application_id, requisition_id),
    CHECK (updated_at >= applied_at)
) STRICT;

-- table: Requisition-specific panel definition
CREATE TABLE InterviewPanel (
    panel_id TEXT NOT NULL PRIMARY KEY CHECK (panel_id GLOB 'PANEL-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(panel_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    requisition_id TEXT NOT NULL, -- Owning requisition | none
    purpose TEXT NOT NULL CHECK (length(trim(purpose)) > 0), -- Interview stage or panel purpose | none
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')), -- Panel lifecycle | none
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (requisition_id) REFERENCES Requisition (requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (panel_id, requisition_id),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Effective panel/staff many-to-many membership
CREATE TABLE PanelMember (
    panel_id TEXT NOT NULL, -- Panel | none
    staff_id TEXT NOT NULL, -- Member staff identity | none
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')), -- Membership lifecycle | none
    PRIMARY KEY (panel_id, staff_id, valid_from),
    FOREIGN KEY (panel_id) REFERENCES InterviewPanel (panel_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Interviewer calendar intervals, not scheduling algorithm
CREATE TABLE Availability (
    availability_id TEXT NOT NULL PRIMARY KEY CHECK (availability_id GLOB 'AVAIL-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(availability_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    staff_id TEXT NOT NULL, -- Calendar owner | none
    start_at INTEGER NOT NULL CHECK (start_at BETWEEN 0 AND 253402300799), -- Calendar interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    end_at INTEGER NOT NULL CHECK (end_at BETWEEN 0 AND 253402300799), -- Calendar interval end, exclusive | UTC epoch seconds; whole seconds, 1970..9999
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'blocked', 'cancelled')), -- Calendar interval status | none
    FOREIGN KEY (staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (staff_id, start_at, end_at),
    CHECK (end_at > start_at)
) STRICT;

-- table: Scheduled interview projection linked consistently to application and panel
CREATE TABLE Interview (
    interview_id TEXT NOT NULL PRIMARY KEY CHECK (interview_id GLOB 'INT-2026-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(interview_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    application_id TEXT NOT NULL, -- Interviewed application | none
    panel_id TEXT NOT NULL, -- Selected panel | none
    requisition_id TEXT NOT NULL, -- Redundant FK join key to enforce panel/application share requisition | none
    start_at INTEGER NOT NULL CHECK (start_at BETWEEN 0 AND 253402300799), -- Scheduled start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    end_at INTEGER NOT NULL CHECK (end_at BETWEEN 0 AND 253402300799), -- Scheduled end, exclusive | UTC epoch seconds; whole seconds, 1970..9999
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')), -- Interview lifecycle | none
    FOREIGN KEY (application_id, requisition_id) REFERENCES Application (application_id, requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (panel_id, requisition_id) REFERENCES InterviewPanel (panel_id, requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK (end_at > start_at)
) STRICT;

-- table: Immutable snapshot of assigned interview members
CREATE TABLE InterviewParticipant (
    interview_id TEXT NOT NULL, -- Interview assignment | none
    staff_id TEXT NOT NULL, -- Assigned interviewer/reviewer | none
    assignment_role TEXT NOT NULL DEFAULT 'reviewer' CHECK (assignment_role IN ('reviewer', 'observer')), -- Immutable assignment kind | none
    assigned_at INTEGER NOT NULL CHECK (assigned_at BETWEEN 0 AND 253402300799), -- Snapshot recording time | UTC epoch seconds; whole seconds, 1970..9999
    PRIMARY KEY (interview_id, staff_id),
    FOREIGN KEY (interview_id) REFERENCES Interview (interview_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

-- table: One structured scorecard per assigned reviewer/interview
CREATE TABLE Scorecard (
    scorecard_id TEXT NOT NULL PRIMARY KEY CHECK (scorecard_id = 'SCORE-' || interview_id || '-' || reviewer_staff_id), -- Immutable literal composite scorecard identity | none
    interview_id TEXT NOT NULL, -- Scored interview | none
    reviewer_staff_id TEXT NOT NULL, -- Assigned reviewer staff identity | none
    rubric_version INTEGER NOT NULL DEFAULT 1 CHECK (rubric_version >= 1), -- Rubric version used for scoring | count
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'incomplete', 'submitted')), -- Scorecard lifecycle | none
    total_score_milli INTEGER CHECK (total_score_milli BETWEEN 0 AND 4000), -- Optional derived total; calculation deferred | thousandths of rubric point, 0..4000
    created_at INTEGER NOT NULL CHECK (created_at BETWEEN 0 AND 253402300799), -- Scorecard creation time | UTC epoch seconds; whole seconds, 1970..9999
    submitted_at INTEGER CHECK (submitted_at BETWEEN 0 AND 253402300799), -- Submission time | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (interview_id) REFERENCES Interview (interview_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (reviewer_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (interview_id, reviewer_staff_id) REFERENCES InterviewParticipant (interview_id, staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (interview_id, reviewer_staff_id),
    CHECK (submitted_at IS NULL OR submitted_at >= created_at),
    CHECK ((status = 'submitted') = (submitted_at IS NOT NULL))
) STRICT;

-- table: Structured rubric evidence and criterion score
CREATE TABLE ScorecardItem (
    scorecard_id TEXT NOT NULL, -- Owning scorecard | none
    skill_requirement_id TEXT NOT NULL, -- Existing criterion; requisition applicability checked in later business validation | none
    score_value INTEGER CHECK (score_value BETWEEN 0 AND 4), -- Optional raw criterion score | integer rubric points 0..4
    weight_basis_points INTEGER NOT NULL CHECK (weight_basis_points BETWEEN 1 AND 10000), -- Snapshot weight; reconciliation deferred | basis points; 10000 = 100 percent
    evidence TEXT CHECK (length(trim(evidence)) > 0), -- Optional synthetic evaluation explanation | none
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'scored')), -- Item completion state | none
    PRIMARY KEY (scorecard_id, skill_requirement_id),
    FOREIGN KEY (scorecard_id) REFERENCES Scorecard (scorecard_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (skill_requirement_id) REFERENCES SkillRequirement (skill_requirement_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK ((status = 'scored') = (score_value IS NOT NULL))
) STRICT;

-- table: Append-only Requisition audit history
CREATE TABLE RequisitionEvent (
    event_id TEXT NOT NULL PRIMARY KEY CHECK (event_id GLOB 'REQEV-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(event_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    requisition_id TEXT NOT NULL, -- Affected entity | none
    sequence INTEGER NOT NULL CHECK (sequence >= 1), -- Unique per-entity ordinal | count
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'rescheduled', 'decision_recorded', 'revised', 'withdrawn', 'cancelled')), -- Audit event kind | none
    previous_status TEXT CHECK (previous_status IN ('draft', 'pending_approval', 'approved', 'open', 'filled', 'closed', 'cancelled')), -- Optional previous projection state; NULL for creation | none
    new_status TEXT NOT NULL CHECK (new_status IN ('draft', 'pending_approval', 'approved', 'open', 'filled', 'closed', 'cancelled')), -- New or retained projection state | none
    actor_staff_id TEXT NOT NULL, -- Required recording actor; role system denotes a synthetic system identity | none
    actor_candidate_id TEXT, -- Optional originating candidate actor | none
    occurred_at INTEGER NOT NULL CHECK (occurred_at BETWEEN 0 AND 253402300799), -- Effective event time | UTC epoch seconds; whole seconds, 1970..9999
    recorded_at INTEGER NOT NULL CHECK (recorded_at BETWEEN 0 AND 253402300799), -- Audit recording time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Explicit reason/decision code | none
    correlation_id TEXT CHECK (length(trim(correlation_id)) > 0), -- Optional opaque correlation token, not an entity FK | none
    snapshot_json TEXT NOT NULL DEFAULT '{}' CHECK (CASE WHEN json_valid(snapshot_json) THEN json_type(snapshot_json) = 'object' ELSE 0 END), -- Before/after non-key values such as slots and rubric items; contents validated by future workflow | JSON object; no truth labels
    band_min_minor INTEGER CHECK (band_min_minor >= 0), -- Optional historical band snapshot minimum | integer minor currency units
    band_max_minor INTEGER CHECK (band_max_minor >= 0), -- Optional historical band snapshot maximum | integer minor currency units
    currency TEXT CHECK (currency GLOB '[A-Z][A-Z][A-Z]'), -- Optional historical band currency; all three snapshot fields present together | currency code; amounts in hundredths
    FOREIGN KEY (requisition_id) REFERENCES Requisition (requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (requisition_id, sequence),
    CHECK (recorded_at >= occurred_at),
    CHECK ((band_min_minor IS NULL AND band_max_minor IS NULL AND currency IS NULL) OR (band_min_minor IS NOT NULL AND band_max_minor IS NOT NULL AND currency IS NOT NULL AND band_max_minor >= band_min_minor)),
    UNIQUE (event_id, requisition_id, currency)
) STRICT;

-- table: Offer projection; scalar amount validated, band eligibility remains business rule
CREATE TABLE Offer (
    offer_id TEXT NOT NULL PRIMARY KEY CHECK (offer_id GLOB 'OFF-2026-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(offer_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    application_id TEXT NOT NULL, -- Application receiving offer | none
    requisition_id TEXT NOT NULL, -- Join key for application and approved band event | none
    approved_requisition_event_id TEXT NOT NULL, -- Historical requisition band snapshot | none
    currency TEXT NOT NULL CHECK (currency GLOB '[A-Z][A-Z][A-Z]'), -- Currency must match referenced band snapshot | currency code; amounts in hundredths
    amount_minor INTEGER NOT NULL CHECK (amount_minor > 0), -- Offered compensation, not cross-record band check | integer minor currency units
    is_final INTEGER NOT NULL DEFAULT 1 CHECK (is_final IN (0, 1)), -- Final-offer indicator | boolean 0/1
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'sent', 'accepted', 'declined', 'expired', 'rejected', 'withdrawn')), -- Offer lifecycle | none
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (application_id, requisition_id) REFERENCES Application (application_id, requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (approved_requisition_event_id, requisition_id, currency) REFERENCES RequisitionEvent (event_id, requisition_id, currency) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Decision record targeting exactly one requisition or offer
CREATE TABLE Approval (
    approval_id TEXT NOT NULL PRIMARY KEY CHECK (approval_id GLOB 'APR-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(approval_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    requisition_id TEXT, -- Optional requisition subject, XOR offer | none
    offer_id TEXT, -- Optional offer subject, XOR requisition | none
    approver_staff_id TEXT NOT NULL, -- Decision maker; role authorization deferred | none
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')), -- Approval lifecycle | none
    requested_at INTEGER NOT NULL CHECK (requested_at BETWEEN 0 AND 253402300799), -- Approval request time | UTC epoch seconds; whole seconds, 1970..9999
    decided_at INTEGER CHECK (decided_at BETWEEN 0 AND 253402300799), -- Decision time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Required reason/decision code | none
    valid_from INTEGER NOT NULL CHECK (valid_from BETWEEN 0 AND 253402300799), -- Effective interval start, inclusive | UTC epoch seconds; whole seconds, 1970..9999
    valid_to INTEGER CHECK (valid_to BETWEEN 0 AND 253402300799), -- Effective interval end, exclusive; NULL means open-ended | UTC epoch seconds; whole seconds, 1970..9999
    FOREIGN KEY (requisition_id) REFERENCES Requisition (requisition_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (offer_id) REFERENCES Offer (offer_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (approver_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK ((requisition_id IS NOT NULL) + (offer_id IS NOT NULL) = 1),
    CHECK (decided_at IS NULL OR decided_at >= requested_at),
    CHECK ((status = 'pending') = (decided_at IS NULL)),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- table: Append-only Application audit history
CREATE TABLE ApplicationEvent (
    event_id TEXT NOT NULL PRIMARY KEY CHECK (event_id GLOB 'APPEV-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(event_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    application_id TEXT NOT NULL, -- Affected entity | none
    sequence INTEGER NOT NULL CHECK (sequence >= 1), -- Unique per-entity ordinal | count
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'rescheduled', 'decision_recorded', 'revised', 'withdrawn', 'cancelled')), -- Audit event kind | none
    previous_status TEXT CHECK (previous_status IN ('applied', 'screening', 'interviewing', 'reviewed', 'offer', 'hired', 'rejected', 'withdrawn')), -- Optional previous projection state; NULL for creation | none
    new_status TEXT NOT NULL CHECK (new_status IN ('applied', 'screening', 'interviewing', 'reviewed', 'offer', 'hired', 'rejected', 'withdrawn')), -- New or retained projection state | none
    actor_staff_id TEXT NOT NULL, -- Required recording actor; role system denotes a synthetic system identity | none
    actor_candidate_id TEXT, -- Optional originating candidate actor | none
    occurred_at INTEGER NOT NULL CHECK (occurred_at BETWEEN 0 AND 253402300799), -- Effective event time | UTC epoch seconds; whole seconds, 1970..9999
    recorded_at INTEGER NOT NULL CHECK (recorded_at BETWEEN 0 AND 253402300799), -- Audit recording time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Explicit reason/decision code | none
    correlation_id TEXT CHECK (length(trim(correlation_id)) > 0), -- Optional opaque correlation token, not an entity FK | none
    snapshot_json TEXT NOT NULL DEFAULT '{}' CHECK (CASE WHEN json_valid(snapshot_json) THEN json_type(snapshot_json) = 'object' ELSE 0 END), -- Before/after non-key values such as slots and rubric items; contents validated by future workflow | JSON object; no truth labels
    FOREIGN KEY (application_id) REFERENCES Application (application_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (application_id, sequence),
    CHECK (recorded_at >= occurred_at)
) STRICT;

-- table: Append-only Interview audit history
CREATE TABLE InterviewEvent (
    event_id TEXT NOT NULL PRIMARY KEY CHECK (event_id GLOB 'INTEV-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(event_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    interview_id TEXT NOT NULL, -- Affected entity | none
    sequence INTEGER NOT NULL CHECK (sequence >= 1), -- Unique per-entity ordinal | count
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'rescheduled', 'decision_recorded', 'revised', 'withdrawn', 'cancelled')), -- Audit event kind | none
    previous_status TEXT CHECK (previous_status IN ('scheduled', 'completed', 'cancelled', 'no_show')), -- Optional previous projection state; NULL for creation | none
    new_status TEXT NOT NULL CHECK (new_status IN ('scheduled', 'completed', 'cancelled', 'no_show')), -- New or retained projection state | none
    actor_staff_id TEXT NOT NULL, -- Required recording actor; role system denotes a synthetic system identity | none
    actor_candidate_id TEXT, -- Optional originating candidate actor | none
    occurred_at INTEGER NOT NULL CHECK (occurred_at BETWEEN 0 AND 253402300799), -- Effective event time | UTC epoch seconds; whole seconds, 1970..9999
    recorded_at INTEGER NOT NULL CHECK (recorded_at BETWEEN 0 AND 253402300799), -- Audit recording time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Explicit reason/decision code | none
    correlation_id TEXT CHECK (length(trim(correlation_id)) > 0), -- Optional opaque correlation token, not an entity FK | none
    snapshot_json TEXT NOT NULL DEFAULT '{}' CHECK (CASE WHEN json_valid(snapshot_json) THEN json_type(snapshot_json) = 'object' ELSE 0 END), -- Before/after non-key values such as slots and rubric items; contents validated by future workflow | JSON object; no truth labels
    FOREIGN KEY (interview_id) REFERENCES Interview (interview_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (interview_id, sequence),
    CHECK (recorded_at >= occurred_at)
) STRICT;

-- table: Append-only Offer audit history
CREATE TABLE OfferEvent (
    event_id TEXT NOT NULL PRIMARY KEY CHECK (event_id GLOB 'OFFEV-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(event_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    offer_id TEXT NOT NULL, -- Affected entity | none
    sequence INTEGER NOT NULL CHECK (sequence >= 1), -- Unique per-entity ordinal | count
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'rescheduled', 'decision_recorded', 'revised', 'withdrawn', 'cancelled')), -- Audit event kind | none
    previous_status TEXT CHECK (previous_status IN ('draft', 'pending_approval', 'approved', 'sent', 'accepted', 'declined', 'expired', 'rejected', 'withdrawn')), -- Optional previous projection state; NULL for creation | none
    new_status TEXT NOT NULL CHECK (new_status IN ('draft', 'pending_approval', 'approved', 'sent', 'accepted', 'declined', 'expired', 'rejected', 'withdrawn')), -- New or retained projection state | none
    actor_staff_id TEXT NOT NULL, -- Required recording actor; role system denotes a synthetic system identity | none
    actor_candidate_id TEXT, -- Optional originating candidate actor | none
    occurred_at INTEGER NOT NULL CHECK (occurred_at BETWEEN 0 AND 253402300799), -- Effective event time | UTC epoch seconds; whole seconds, 1970..9999
    recorded_at INTEGER NOT NULL CHECK (recorded_at BETWEEN 0 AND 253402300799), -- Audit recording time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Explicit reason/decision code | none
    correlation_id TEXT CHECK (length(trim(correlation_id)) > 0), -- Optional opaque correlation token, not an entity FK | none
    snapshot_json TEXT NOT NULL DEFAULT '{}' CHECK (CASE WHEN json_valid(snapshot_json) THEN json_type(snapshot_json) = 'object' ELSE 0 END), -- Before/after non-key values such as slots and rubric items; contents validated by future workflow | JSON object; no truth labels
    FOREIGN KEY (offer_id) REFERENCES Offer (offer_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (offer_id, sequence),
    CHECK (recorded_at >= occurred_at)
) STRICT;

-- table: Append-only Approval audit history
CREATE TABLE ApprovalEvent (
    event_id TEXT NOT NULL PRIMARY KEY CHECK (event_id GLOB 'APREV-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(event_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    approval_id TEXT NOT NULL, -- Affected entity | none
    sequence INTEGER NOT NULL CHECK (sequence >= 1), -- Unique per-entity ordinal | count
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'rescheduled', 'decision_recorded', 'revised', 'withdrawn', 'cancelled')), -- Audit event kind | none
    previous_status TEXT CHECK (previous_status IN ('pending', 'approved', 'rejected')), -- Optional previous projection state; NULL for creation | none
    new_status TEXT NOT NULL CHECK (new_status IN ('pending', 'approved', 'rejected')), -- New or retained projection state | none
    actor_staff_id TEXT NOT NULL, -- Required recording actor; role system denotes a synthetic system identity | none
    actor_candidate_id TEXT, -- Optional originating candidate actor | none
    occurred_at INTEGER NOT NULL CHECK (occurred_at BETWEEN 0 AND 253402300799), -- Effective event time | UTC epoch seconds; whole seconds, 1970..9999
    recorded_at INTEGER NOT NULL CHECK (recorded_at BETWEEN 0 AND 253402300799), -- Audit recording time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Explicit reason/decision code | none
    correlation_id TEXT CHECK (length(trim(correlation_id)) > 0), -- Optional opaque correlation token, not an entity FK | none
    snapshot_json TEXT NOT NULL DEFAULT '{}' CHECK (CASE WHEN json_valid(snapshot_json) THEN json_type(snapshot_json) = 'object' ELSE 0 END), -- Before/after non-key values such as slots and rubric items; contents validated by future workflow | JSON object; no truth labels
    FOREIGN KEY (approval_id) REFERENCES Approval (approval_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (approval_id, sequence),
    CHECK (recorded_at >= occurred_at)
) STRICT;

-- table: Append-only Scorecard audit history
CREATE TABLE ScorecardEvent (
    event_id TEXT NOT NULL PRIMARY KEY CHECK (event_id GLOB 'SCREV-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(event_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    scorecard_id TEXT NOT NULL, -- Affected entity | none
    sequence INTEGER NOT NULL CHECK (sequence >= 1), -- Unique per-entity ordinal | count
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'rescheduled', 'decision_recorded', 'revised', 'withdrawn', 'cancelled')), -- Audit event kind | none
    previous_status TEXT CHECK (previous_status IN ('draft', 'incomplete', 'submitted')), -- Optional previous projection state; NULL for creation | none
    new_status TEXT NOT NULL CHECK (new_status IN ('draft', 'incomplete', 'submitted')), -- New or retained projection state | none
    actor_staff_id TEXT NOT NULL, -- Required recording actor; role system denotes a synthetic system identity | none
    actor_candidate_id TEXT, -- Optional originating candidate actor | none
    occurred_at INTEGER NOT NULL CHECK (occurred_at BETWEEN 0 AND 253402300799), -- Effective event time | UTC epoch seconds; whole seconds, 1970..9999
    recorded_at INTEGER NOT NULL CHECK (recorded_at BETWEEN 0 AND 253402300799), -- Audit recording time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Explicit reason/decision code | none
    correlation_id TEXT CHECK (length(trim(correlation_id)) > 0), -- Optional opaque correlation token, not an entity FK | none
    snapshot_json TEXT NOT NULL DEFAULT '{}' CHECK (CASE WHEN json_valid(snapshot_json) THEN json_type(snapshot_json) = 'object' ELSE 0 END), -- Before/after non-key values such as slots and rubric items; contents validated by future workflow | JSON object; no truth labels
    FOREIGN KEY (scorecard_id) REFERENCES Scorecard (scorecard_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (scorecard_id, sequence),
    CHECK (recorded_at >= occurred_at)
) STRICT;

-- table: Append-only Candidate audit history
CREATE TABLE CandidateEvent (
    event_id TEXT NOT NULL PRIMARY KEY CHECK (event_id GLOB 'CANEV-[0-9][0-9][0-9][0-9][0-9][0-9]' AND substr(event_id, -6) <> '000000'), -- Immutable deterministic identity; six-digit positive counter | none
    candidate_id TEXT NOT NULL, -- Affected entity | none
    sequence INTEGER NOT NULL CHECK (sequence >= 1), -- Unique per-entity ordinal | count
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'status_changed', 'rescheduled', 'decision_recorded', 'revised', 'withdrawn', 'cancelled')), -- Audit event kind | none
    previous_status TEXT CHECK (previous_status IN ('active', 'withdrawn')), -- Optional previous projection state; NULL for creation | none
    new_status TEXT NOT NULL CHECK (new_status IN ('active', 'withdrawn')), -- New or retained projection state | none
    actor_staff_id TEXT NOT NULL, -- Required recording actor; role system denotes a synthetic system identity | none
    actor_candidate_id TEXT, -- Optional originating candidate actor | none
    occurred_at INTEGER NOT NULL CHECK (occurred_at BETWEEN 0 AND 253402300799), -- Effective event time | UTC epoch seconds; whole seconds, 1970..9999
    recorded_at INTEGER NOT NULL CHECK (recorded_at BETWEEN 0 AND 253402300799), -- Audit recording time | UTC epoch seconds; whole seconds, 1970..9999
    reason_code TEXT NOT NULL CHECK (length(trim(reason_code)) > 0), -- Explicit reason/decision code | none
    correlation_id TEXT CHECK (length(trim(correlation_id)) > 0), -- Optional opaque correlation token, not an entity FK | none
    snapshot_json TEXT NOT NULL DEFAULT '{}' CHECK (CASE WHEN json_valid(snapshot_json) THEN json_type(snapshot_json) = 'object' ELSE 0 END), -- Before/after non-key values such as slots and rubric items; contents validated by future workflow | JSON object; no truth labels
    FOREIGN KEY (candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_staff_id) REFERENCES Staff (staff_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (actor_candidate_id) REFERENCES Candidate (candidate_id) ON UPDATE RESTRICT ON DELETE RESTRICT,
    UNIQUE (candidate_id, sequence),
    CHECK (recorded_at >= occurred_at)
) STRICT;

CREATE UNIQUE INDEX one_active_final_offer ON Offer (application_id) WHERE is_final = 1 AND status IN ('pending_approval', 'approved', 'sent', 'accepted');

CREATE INDEX availability_by_staff ON Availability (staff_id, start_at, end_at);

CREATE INDEX interview_by_time ON Interview (start_at, end_at);

CREATE INDEX participant_by_staff ON InterviewParticipant (staff_id, interview_id);

CREATE TRIGGER SchemaMetadata_no_update BEFORE UPDATE ON SchemaMetadata
BEGIN
    SELECT RAISE(ABORT, 'SchemaMetadata is append-only');
END;

CREATE TRIGGER SchemaMetadata_no_delete BEFORE DELETE ON SchemaMetadata
BEGIN
    SELECT RAISE(ABORT, 'SchemaMetadata is append-only');
END;

CREATE TRIGGER SchemaMetadata_no_replace BEFORE INSERT ON SchemaMetadata
WHEN EXISTS (SELECT 1 FROM SchemaMetadata WHERE singleton = NEW.singleton)
BEGIN
    SELECT RAISE(ABORT, 'SchemaMetadata cannot replace existing identity');
END;

CREATE TRIGGER Staff_immutable_pk BEFORE UPDATE ON Staff
WHEN OLD.staff_id IS NOT NEW.staff_id
BEGIN
    SELECT RAISE(ABORT, 'Staff identity is immutable');
END;

CREATE TRIGGER HiringManager_immutable_pk BEFORE UPDATE ON HiringManager
WHEN OLD.hiring_manager_id IS NOT NEW.hiring_manager_id
BEGIN
    SELECT RAISE(ABORT, 'HiringManager identity is immutable');
END;

CREATE TRIGGER Candidate_immutable_pk BEFORE UPDATE ON Candidate
WHEN OLD.candidate_id IS NOT NEW.candidate_id
BEGIN
    SELECT RAISE(ABORT, 'Candidate identity is immutable');
END;

CREATE TRIGGER CandidateSkill_immutable_pk BEFORE UPDATE ON CandidateSkill
WHEN OLD.candidate_id IS NOT NEW.candidate_id OR OLD.skill_key IS NOT NEW.skill_key
BEGIN
    SELECT RAISE(ABORT, 'CandidateSkill identity is immutable');
END;

CREATE TRIGGER Requisition_immutable_pk BEFORE UPDATE ON Requisition
WHEN OLD.requisition_id IS NOT NEW.requisition_id
BEGIN
    SELECT RAISE(ABORT, 'Requisition identity is immutable');
END;

CREATE TRIGGER SkillRequirement_immutable_pk BEFORE UPDATE ON SkillRequirement
WHEN OLD.skill_requirement_id IS NOT NEW.skill_requirement_id
BEGIN
    SELECT RAISE(ABORT, 'SkillRequirement identity is immutable');
END;

CREATE TRIGGER Application_immutable_pk BEFORE UPDATE ON Application
WHEN OLD.application_id IS NOT NEW.application_id
BEGIN
    SELECT RAISE(ABORT, 'Application identity is immutable');
END;

CREATE TRIGGER InterviewPanel_immutable_pk BEFORE UPDATE ON InterviewPanel
WHEN OLD.panel_id IS NOT NEW.panel_id
BEGIN
    SELECT RAISE(ABORT, 'InterviewPanel identity is immutable');
END;

CREATE TRIGGER PanelMember_immutable_pk BEFORE UPDATE ON PanelMember
WHEN OLD.panel_id IS NOT NEW.panel_id OR OLD.staff_id IS NOT NEW.staff_id OR OLD.valid_from IS NOT NEW.valid_from
BEGIN
    SELECT RAISE(ABORT, 'PanelMember identity is immutable');
END;

CREATE TRIGGER Availability_immutable_pk BEFORE UPDATE ON Availability
WHEN OLD.availability_id IS NOT NEW.availability_id
BEGIN
    SELECT RAISE(ABORT, 'Availability identity is immutable');
END;

CREATE TRIGGER Interview_immutable_pk BEFORE UPDATE ON Interview
WHEN OLD.interview_id IS NOT NEW.interview_id
BEGIN
    SELECT RAISE(ABORT, 'Interview identity is immutable');
END;

CREATE TRIGGER InterviewParticipant_no_update BEFORE UPDATE ON InterviewParticipant
BEGIN
    SELECT RAISE(ABORT, 'InterviewParticipant is append-only');
END;

CREATE TRIGGER InterviewParticipant_no_delete BEFORE DELETE ON InterviewParticipant
BEGIN
    SELECT RAISE(ABORT, 'InterviewParticipant is append-only');
END;

CREATE TRIGGER InterviewParticipant_no_replace BEFORE INSERT ON InterviewParticipant
WHEN EXISTS (SELECT 1 FROM InterviewParticipant WHERE interview_id = NEW.interview_id AND staff_id = NEW.staff_id)
BEGIN
    SELECT RAISE(ABORT, 'InterviewParticipant cannot replace existing identity');
END;

CREATE TRIGGER Scorecard_immutable_pk BEFORE UPDATE ON Scorecard
WHEN OLD.scorecard_id IS NOT NEW.scorecard_id
BEGIN
    SELECT RAISE(ABORT, 'Scorecard identity is immutable');
END;

CREATE TRIGGER ScorecardItem_immutable_pk BEFORE UPDATE ON ScorecardItem
WHEN OLD.scorecard_id IS NOT NEW.scorecard_id OR OLD.skill_requirement_id IS NOT NEW.skill_requirement_id
BEGIN
    SELECT RAISE(ABORT, 'ScorecardItem identity is immutable');
END;

CREATE TRIGGER RequisitionEvent_no_update BEFORE UPDATE ON RequisitionEvent
BEGIN
    SELECT RAISE(ABORT, 'RequisitionEvent is append-only');
END;

CREATE TRIGGER RequisitionEvent_no_delete BEFORE DELETE ON RequisitionEvent
BEGIN
    SELECT RAISE(ABORT, 'RequisitionEvent is append-only');
END;

CREATE TRIGGER RequisitionEvent_no_replace BEFORE INSERT ON RequisitionEvent
WHEN EXISTS (SELECT 1 FROM RequisitionEvent WHERE event_id = NEW.event_id)
BEGIN
    SELECT RAISE(ABORT, 'RequisitionEvent cannot replace existing identity');
END;

CREATE TRIGGER Offer_immutable_pk BEFORE UPDATE ON Offer
WHEN OLD.offer_id IS NOT NEW.offer_id
BEGIN
    SELECT RAISE(ABORT, 'Offer identity is immutable');
END;

CREATE TRIGGER Approval_immutable_pk BEFORE UPDATE ON Approval
WHEN OLD.approval_id IS NOT NEW.approval_id
BEGIN
    SELECT RAISE(ABORT, 'Approval identity is immutable');
END;

CREATE TRIGGER ApplicationEvent_no_update BEFORE UPDATE ON ApplicationEvent
BEGIN
    SELECT RAISE(ABORT, 'ApplicationEvent is append-only');
END;

CREATE TRIGGER ApplicationEvent_no_delete BEFORE DELETE ON ApplicationEvent
BEGIN
    SELECT RAISE(ABORT, 'ApplicationEvent is append-only');
END;

CREATE TRIGGER ApplicationEvent_no_replace BEFORE INSERT ON ApplicationEvent
WHEN EXISTS (SELECT 1 FROM ApplicationEvent WHERE event_id = NEW.event_id)
BEGIN
    SELECT RAISE(ABORT, 'ApplicationEvent cannot replace existing identity');
END;

CREATE TRIGGER InterviewEvent_no_update BEFORE UPDATE ON InterviewEvent
BEGIN
    SELECT RAISE(ABORT, 'InterviewEvent is append-only');
END;

CREATE TRIGGER InterviewEvent_no_delete BEFORE DELETE ON InterviewEvent
BEGIN
    SELECT RAISE(ABORT, 'InterviewEvent is append-only');
END;

CREATE TRIGGER InterviewEvent_no_replace BEFORE INSERT ON InterviewEvent
WHEN EXISTS (SELECT 1 FROM InterviewEvent WHERE event_id = NEW.event_id)
BEGIN
    SELECT RAISE(ABORT, 'InterviewEvent cannot replace existing identity');
END;

CREATE TRIGGER OfferEvent_no_update BEFORE UPDATE ON OfferEvent
BEGIN
    SELECT RAISE(ABORT, 'OfferEvent is append-only');
END;

CREATE TRIGGER OfferEvent_no_delete BEFORE DELETE ON OfferEvent
BEGIN
    SELECT RAISE(ABORT, 'OfferEvent is append-only');
END;

CREATE TRIGGER OfferEvent_no_replace BEFORE INSERT ON OfferEvent
WHEN EXISTS (SELECT 1 FROM OfferEvent WHERE event_id = NEW.event_id)
BEGIN
    SELECT RAISE(ABORT, 'OfferEvent cannot replace existing identity');
END;

CREATE TRIGGER ApprovalEvent_no_update BEFORE UPDATE ON ApprovalEvent
BEGIN
    SELECT RAISE(ABORT, 'ApprovalEvent is append-only');
END;

CREATE TRIGGER ApprovalEvent_no_delete BEFORE DELETE ON ApprovalEvent
BEGIN
    SELECT RAISE(ABORT, 'ApprovalEvent is append-only');
END;

CREATE TRIGGER ApprovalEvent_no_replace BEFORE INSERT ON ApprovalEvent
WHEN EXISTS (SELECT 1 FROM ApprovalEvent WHERE event_id = NEW.event_id)
BEGIN
    SELECT RAISE(ABORT, 'ApprovalEvent cannot replace existing identity');
END;

CREATE TRIGGER ScorecardEvent_no_update BEFORE UPDATE ON ScorecardEvent
BEGIN
    SELECT RAISE(ABORT, 'ScorecardEvent is append-only');
END;

CREATE TRIGGER ScorecardEvent_no_delete BEFORE DELETE ON ScorecardEvent
BEGIN
    SELECT RAISE(ABORT, 'ScorecardEvent is append-only');
END;

CREATE TRIGGER ScorecardEvent_no_replace BEFORE INSERT ON ScorecardEvent
WHEN EXISTS (SELECT 1 FROM ScorecardEvent WHERE event_id = NEW.event_id)
BEGIN
    SELECT RAISE(ABORT, 'ScorecardEvent cannot replace existing identity');
END;

CREATE TRIGGER CandidateEvent_no_update BEFORE UPDATE ON CandidateEvent
BEGIN
    SELECT RAISE(ABORT, 'CandidateEvent is append-only');
END;

CREATE TRIGGER CandidateEvent_no_delete BEFORE DELETE ON CandidateEvent
BEGIN
    SELECT RAISE(ABORT, 'CandidateEvent is append-only');
END;

CREATE TRIGGER CandidateEvent_no_replace BEFORE INSERT ON CandidateEvent
WHEN EXISTS (SELECT 1 FROM CandidateEvent WHERE event_id = NEW.event_id)
BEGIN
    SELECT RAISE(ABORT, 'CandidateEvent cannot replace existing identity');
END;
