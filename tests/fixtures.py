"""Tiny literal schema fixtures, not a synthetic dataset generator."""

T = 1_793_000_000
REQ = "REQ-2026-000001"
CAND = "CAND-000001"
APP = f"APP-{CAND}-{REQ}"
INT = "INT-2026-000001"
REVIEWER = "STAFF-000002"
SCORE = f"SCORE-{INT}-{REVIEWER}"


def audit(event_id, subject_column, subject_id, state):
    return dict(event_id=event_id, **{subject_column: subject_id}, sequence=1,
        event_type="created", previous_status=None, new_status=state,
        actor_staff_id="STAFF-000001", actor_candidate_id=None,
        occurred_at=T, recorded_at=T, reason_code="SCHEMA_TEST", correlation_id=None)


FIXTURES = [
    ("Staff", dict(staff_id="STAFF-000001", display_name="Synthetic Manager", role="manager", status="active", valid_from=T, valid_to=None)),
    ("Staff", dict(staff_id=REVIEWER, display_name="Synthetic Reviewer", role="interviewer", status="active", valid_from=T, valid_to=None)),
    ("HiringManager", dict(hiring_manager_id="HM-000001", staff_id="STAFF-000001", department="Synthetic Team", status="active", valid_from=T, valid_to=None)),
    ("Candidate", dict(candidate_id=CAND, display_name="Synthetic Candidate", experience_years=5, contact_email="candidate1@example.invalid", status="active", created_at=T, withdrawn_at=None)),
    ("CandidateSkill", dict(candidate_id=CAND, skill_key="python", level=2, status="active")),
    ("Requisition", dict(requisition_id=REQ, hiring_manager_id="HM-000001", title="Synthetic Engineer", status="open", band_min_minor=10000, band_max_minor=20000, currency="INR", policy_version=1, valid_from=T, valid_to=None)),
    ("SkillRequirement", dict(skill_requirement_id="SKILL-000001", requisition_id=REQ, criterion_key="python", description="Synthetic evidence", is_required=1, weight_basis_points=10000, min_proficiency=2, rubric_version=1, status="active", valid_from=T, valid_to=None)),
    ("Application", dict(application_id=APP, candidate_id=CAND, requisition_id=REQ, status="applied", applied_at=T, updated_at=T)),
    ("InterviewPanel", dict(panel_id="PANEL-000001", requisition_id=REQ, purpose="Technical", status="active", valid_from=T, valid_to=None)),
    ("PanelMember", dict(panel_id="PANEL-000001", staff_id=REVIEWER, valid_from=T, valid_to=None, status="active")),
    ("Availability", dict(availability_id="AVAIL-000001", staff_id=REVIEWER, start_at=T, end_at=T+3600, status="available")),
    ("Interview", dict(interview_id=INT, application_id=APP, panel_id="PANEL-000001", requisition_id=REQ, start_at=T, end_at=T+1800, status="scheduled")),
    ("InterviewParticipant", dict(interview_id=INT, staff_id=REVIEWER, assignment_role="reviewer", assigned_at=T)),
    ("Scorecard", dict(scorecard_id=SCORE, interview_id=INT, reviewer_staff_id=REVIEWER, rubric_version=1, status="draft", total_score_milli=None, created_at=T, submitted_at=None)),
    ("ScorecardItem", dict(scorecard_id=SCORE, skill_requirement_id="SKILL-000001", score_value=None, weight_basis_points=10000, evidence=None, status="pending")),
    ("RequisitionEvent", dict(**audit("REQEV-000001", "requisition_id", REQ, "approved"), band_min_minor=10000, band_max_minor=20000, currency="INR")),
    ("Offer", dict(offer_id="OFF-2026-000001", application_id=APP, requisition_id=REQ, approved_requisition_event_id="REQEV-000001", currency="INR", amount_minor=15000, is_final=1, status="draft", valid_from=T, valid_to=None)),
    ("Approval", dict(approval_id="APR-000001", requisition_id=REQ, offer_id=None, approver_staff_id="STAFF-000001", status="pending", requested_at=T, decided_at=None, reason_code="SCHEMA_TEST", valid_from=T, valid_to=None)),
    ("ApplicationEvent", audit("APPEV-000001", "application_id", APP, "applied")),
    ("InterviewEvent", audit("INTEV-000001", "interview_id", INT, "scheduled")),
    ("OfferEvent", audit("OFFEV-000001", "offer_id", "OFF-2026-000001", "draft")),
    ("ApprovalEvent", audit("APREV-000001", "approval_id", "APR-000001", "pending")),
    ("ScorecardEvent", audit("SCREV-000001", "scorecard_id", SCORE, "draft")),
    ("CandidateEvent", audit("CANEV-000001", "candidate_id", CAND, "active")),
]


def insert(db, table, row):
    columns = ", ".join(row)
    placeholders = ", ".join("?" for _ in row)
    db.execute(f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})', tuple(row.values()))


def seed(db):
    for table, row in FIXTURES:
        insert(db, table, row)


SAMPLE = dict(reversed(FIXTURES))  # First occurrence of Staff is canonical.
