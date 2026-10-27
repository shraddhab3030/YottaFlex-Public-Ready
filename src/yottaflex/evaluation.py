"""Persisted rubric arithmetic and transactional scorecard/review operations."""

import json

from .workflow import (_append_event, _app_change, _authorize, _eligible_application,
    _eligible_requisition, _fail, _last_event, _metadata, _row, write_transaction)


REVIEW_MINIMUM = 2500
OFFER_MINIMUM = 3000
MAX_REVIEWER_SPREAD = 1000


def applicable_criteria(connection, interview):
    rows = list(connection.execute("""SELECT * FROM SkillRequirement WHERE requisition_id=?
        AND status='active' AND valid_from<=? AND (valid_to IS NULL OR valid_to>=?)
        ORDER BY rubric_version,skill_requirement_id""", (interview["requisition_id"],interview["start_at"],interview["end_at"])))
    if not rows:
        _fail("RUBRIC_UNAVAILABLE","No applicable interview-time rubric")
    version = max(row["rubric_version"] for row in rows)
    rows = [row for row in rows if row["rubric_version"]==version]
    if sum(row["weight_basis_points"] for row in rows)!=10000 or not any(row["is_required"] for row in rows):
        _fail("RUBRIC_INVALID","Complete version must have required criteria and exactly 10000 basis points")
    return rows


def card_snapshot(connection, scorecard_id):
    score = _row(connection,"Scorecard","scorecard_id",scorecard_id,"SCORECARD_NOT_FOUND")
    return dict(score) | {"items":[dict(row) for row in connection.execute(
        "SELECT * FROM ScorecardItem WHERE scorecard_id=? ORDER BY skill_requirement_id", (scorecard_id,))]}


def computed_card(connection, scorecard_id, *, require_complete=True):
    """Derive totals exclusively from persisted items and applicable criteria."""
    score = _row(connection,"Scorecard","scorecard_id",scorecard_id,"SCORECARD_NOT_FOUND")
    interview = _row(connection,"Interview","interview_id",score["interview_id"],"INTERVIEW_NOT_FOUND")
    criteria = applicable_criteria(connection,interview)
    if score["rubric_version"]!=criteria[0]["rubric_version"]:
        _fail("RUBRIC_VERSION_INVALID","Scorecard must use the effective rubric version")
    expected = {row["skill_requirement_id"]:row for row in criteria}
    items = list(connection.execute("SELECT * FROM ScorecardItem WHERE scorecard_id=? ORDER BY skill_requirement_id", (scorecard_id,)))
    if {row["skill_requirement_id"] for row in items} != set(expected):
        _fail("SCORECARD_INCOMPLETE","Every applicable criterion, including optional, must have an item")
    numerator, required_values, complete = 0,[],True
    for item in items:
        criterion = expected[item["skill_requirement_id"]]
        if item["weight_basis_points"] != criterion["weight_basis_points"]:
            _fail("WEIGHT_MISMATCH","Item weight must match effective criterion")
        scored = item["status"]=="scored" and type(item["score_value"]) is int and 0<=item["score_value"]<=4 and bool(item["evidence"] and item["evidence"].strip())
        complete &= scored
        if scored:
            numerator += item["score_value"]*criterion["weight_basis_points"]
            if criterion["is_required"]:
                required_values.append(item["score_value"])
    if not complete:
        if require_complete:
            _fail("SCORECARD_INCOMPLETE","All items must be scored with evidence before submission")
        return {"complete":False,"total_score_milli":None,"required_minimum":None}
    return {"complete":True,"total_score_milli":(numerator+5)//10,"required_minimum":min(required_values)}


def _interview_for_card(connection, identity, reviewer, actor, when):
    interview = _row(connection,"Interview","interview_id",identity,"INTERVIEW_NOT_FOUND")
    if interview["status"] != "completed":
        _fail("INTERVIEW_NOT_COMPLETED","Only completed interviews may be evaluated")
    last = _last_event(connection,"Interview","interview_id",identity,"completed",when)
    if when < interview["end_at"] or last["occurred_at"]>when:
        _fail("EVENT_TIME_INVALID","Evaluation must follow recorded completion")
    app = _eligible_application(connection,interview["application_id"])
    if app["status"] != "interviewing":
        _fail("APPLICATION_STAGE_INELIGIBLE","Evaluations are editable only before review")
    _last_event(connection,"Application","application_id",app["application_id"],app["status"],when)
    assigned = connection.execute("SELECT * FROM InterviewParticipant WHERE interview_id=? AND staff_id=? AND assignment_role='reviewer'", (identity,reviewer)).fetchone()
    person = connection.execute("SELECT * FROM Staff WHERE staff_id=?", (reviewer,)).fetchone()
    if not assigned or not person or person["role"] not in ("interviewer","manager") or actor!=reviewer:
        _fail("REVIEWER_INELIGIBLE","Only the assigned reviewer may author this scorecard")
    if person["status"]!="active" or person["valid_from"]>when or (person["valid_to"] is not None and when>=person["valid_to"]):
        _fail("REVIEWER_INELIGIBLE","Reviewer is not effective at evaluation time")
    return interview


def create_scorecard(connection, interview_id, reviewer_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        interview = _interview_for_card(connection,interview_id,reviewer_id,actor_id,when)
        identity = f"SCORE-{interview_id}-{reviewer_id}"
        if connection.execute("SELECT 1 FROM Scorecard WHERE interview_id=? AND reviewer_staff_id=?", (interview_id,reviewer_id)).fetchone():
            _fail("DUPLICATE_SCORECARD","Interview/reviewer scorecard already exists")
        criteria = applicable_criteria(connection,interview)
        connection.execute("INSERT INTO Scorecard VALUES (?,?,?,?,'draft',NULL,?,NULL)", (identity,interview_id,reviewer_id,criteria[0]["rubric_version"],when))
        connection.executemany("INSERT INTO ScorecardItem VALUES (?,?,NULL,?,NULL,'pending')",
            ((identity,row["skill_requirement_id"],row["weight_basis_points"]) for row in criteria))
        _append_event(connection,"Scorecard","scorecard_id",identity,"created",None,"draft",actor_id,when,reason_code,correlation_id,
            {"status":None},card_snapshot(connection,identity))
        return identity


def _editable(connection, identity, actor, when):
    score = _row(connection,"Scorecard","scorecard_id",identity,"SCORECARD_NOT_FOUND")
    if score["status"]=="submitted":
        _fail("SCORECARD_LOCKED","Submitted evidence is immutable through public operations; correction requires a future explicit policy")
    _interview_for_card(connection,score["interview_id"],score["reviewer_staff_id"],actor,when)
    event = _last_event(connection,"Scorecard","scorecard_id",identity,score["status"],when)
    if json.loads(event["snapshot_json"]).get("after")!=card_snapshot(connection,identity):
        _fail("HISTORY_MISMATCH","Editable evidence must agree with its last event")
    computed_card(connection,identity,require_complete=False)
    return score


def set_scorecard_item(connection, scorecard_id, criterion_id, score_value, evidence, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        score = _editable(connection,scorecard_id,actor_id,when)
        interview = _row(connection,"Interview","interview_id",score["interview_id"],"INTERVIEW_NOT_FOUND")
        criteria = {row["skill_requirement_id"] for row in applicable_criteria(connection,interview)}
        if criterion_id not in criteria:
            _fail("IRRELEVANT_CRITERION","Criterion must belong to this interview's effective requisition rubric")
        if score_value is not None and (type(score_value) is not int or not 0<=score_value<=4):
            _fail("INVALID_RUBRIC_VALUE","Use an integer rubric value 0..4 or pending NULL")
        if score_value is not None and (not isinstance(evidence,str) or not evidence.strip()):
            _fail("EVIDENCE_REQUIRED","Scored items need qualitative evidence")
        if evidence is not None and (not isinstance(evidence,str) or not evidence.strip()):
            _fail("EVIDENCE_REQUIRED","Evidence must be nonblank when provided")
        before = card_snapshot(connection,scorecard_id)
        connection.execute("UPDATE ScorecardItem SET score_value=?,evidence=?,status=? WHERE scorecard_id=? AND skill_requirement_id=?",
            (score_value,evidence,"pending" if score_value is None else "scored",scorecard_id,criterion_id))
        connection.execute("UPDATE Scorecard SET status='incomplete',total_score_milli=NULL WHERE scorecard_id=?", (scorecard_id,))
        _append_event(connection,"Scorecard","scorecard_id",scorecard_id,"revised",score["status"],"incomplete",actor_id,when,reason_code,correlation_id,
            before,card_snapshot(connection,scorecard_id))


def submit_scorecard(connection, scorecard_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        score = _editable(connection,scorecard_id,actor_id,when)
        result = computed_card(connection,scorecard_id)
        before = card_snapshot(connection,scorecard_id)
        connection.execute("UPDATE Scorecard SET status='submitted',total_score_milli=?,submitted_at=? WHERE scorecard_id=?",
            (result["total_score_milli"],when,scorecard_id))
        _append_event(connection,"Scorecard","scorecard_id",scorecard_id,"status_changed",score["status"],"submitted",actor_id,when,reason_code,correlation_id,
            before,card_snapshot(connection,scorecard_id))
        return result["total_score_milli"]


def evaluate_application(connection, application_id, *, when=None):
    """Read-only decision from every required participant/card; no lifecycle mutation."""
    app = _row(connection,"Application","application_id",application_id,"APPLICATION_NOT_FOUND")
    interviews = list(connection.execute("SELECT * FROM Interview WHERE application_id=? AND status<>'cancelled' ORDER BY interview_id", (application_id,)))
    if not interviews or any(row["status"]!="completed" for row in interviews):
        _fail("REVIEW_GATE_INCOMPLETE","All noncancelled meetings must be completed")
    totals,minimums,identities,latest = [],[],[],0
    for interview in interviews:
        completion = connection.execute("SELECT occurred_at FROM InterviewEvent WHERE interview_id=? AND new_status='completed' ORDER BY sequence DESC LIMIT 1", (interview["interview_id"],)).fetchone()
        if completion is None:
            _fail("REVIEW_GATE_INCOMPLETE","Recorded interview completion is required")
        reviewers = list(connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? AND assignment_role='reviewer' ORDER BY staff_id", (interview["interview_id"],)))
        if not reviewers:
            _fail("REVIEW_GATE_INCOMPLETE","Assigned reviewers required")
        for reviewer in reviewers:
            score = connection.execute("SELECT * FROM Scorecard WHERE interview_id=? AND reviewer_staff_id=?", (interview["interview_id"],reviewer[0])).fetchone()
            if score is None or score["status"]!="submitted" or score["submitted_at"]<completion[0] or score["created_at"]<completion[0]:
                _fail("REVIEW_GATE_INCOMPLETE","Every assigned reviewer must submit a complete evaluation after completion")
            event = connection.execute("SELECT * FROM ScorecardEvent WHERE scorecard_id=? ORDER BY sequence DESC LIMIT 1", (score["scorecard_id"],)).fetchone()
            if event is None or event["new_status"]!="submitted" or event["actor_staff_id"]!=reviewer[0] or json.loads(event["snapshot_json"]).get("after")!=card_snapshot(connection,score["scorecard_id"]):
                _fail("REVIEW_GATE_INCOMPLETE","Audited submission must agree with current source evidence")
            try:
                result = computed_card(connection,score["scorecard_id"])
            except ValueError:
                _fail("REVIEW_GATE_INCOMPLETE","Applicable complete rubric evidence required")
            if score["total_score_milli"]!=result["total_score_milli"]:
                _fail("SCORE_RECONCILIATION_FAILED","Stored total disagrees with source items")
            totals.append(result["total_score_milli"]); minimums.append(result["required_minimum"])
            identities.append(score["scorecard_id"]); latest=max(latest,score["submitted_at"])
    if when is not None and when<latest:
        _fail("EVENT_TIME_INVALID","Decision cannot precede submitted evidence")
    aggregate = (sum(totals)+len(totals)//2)//len(totals)
    spread = max(totals)-min(totals)
    reviewed = aggregate>=REVIEW_MINIMUM and min(minimums)>=2 and spread<=MAX_REVIEWER_SPREAD
    eligible = reviewed and aggregate>=OFFER_MINIMUM and min(minimums)>=3
    return {"policy_version":1,"scorecard_ids":identities,"reviewer_totals_milli":totals,
        "aggregate_milli":aggregate,"required_minimum":min(minimums),"reviewer_spread_milli":spread,
        "review_eligible":reviewed,"offer_eligible":eligible,"latest_evidence_at":latest}


def _review_context(connection, application_id, actor, when):
    app = _eligible_application(connection,application_id)
    _authorize(connection,actor,when,app["requisition_id"])
    _last_event(connection,"Application","application_id",application_id,app["status"],when)
    _eligible_requisition(connection,app["requisition_id"],when)
    return app,evaluate_application(connection,application_id,when=when)


def review_application(connection, application_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        app = _eligible_application(connection,application_id)
        if app["status"]!="interviewing":
            _fail("INVALID_TRANSITION","Review must follow interviewing")
        app,decision = _review_context(connection,application_id,actor_id,when)
        if not decision["review_eligible"]:
            _fail("REVIEW_DECISION_FAILED","Aggregate, required minimum or reviewer agreement gate failed")
        _app_change(connection,app,"reviewed","decision_recorded",actor_id,when,reason_code,correlation_id,details=decision)
        return decision


def reject_evaluated_application(connection, application_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        app,decision = _review_context(connection,application_id,actor_id,when)
        if app["status"] not in ("interviewing","reviewed") or (app["status"]=="interviewing" and decision["review_eligible"]) or (app["status"]=="reviewed" and decision["offer_eligible"]):
            _fail("INVALID_REJECTION","Rejection must follow a recorded negative evaluation policy")
        _app_change(connection,app,"rejected","decision_recorded",actor_id,when,reason_code,correlation_id,details=decision)
        return decision
