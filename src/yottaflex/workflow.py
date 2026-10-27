"""Transactional interview lifecycle operations; no scoring or offer engine."""

from contextlib import contextmanager

from .canonical import stable_json
from .generation_checks import role_details
from .ids import numbered_id


CAPACITY_STATUSES = ("scheduled", "completed", "no_show")
PANEL_MINIMUM = {"backend": 2, "data": 2, "integration": 3, "applied_ai": 3}
ALLOWED_DURATIONS = (1800, 2700, 3600)
WITHDRAWABLE = ("applied", "screening", "interviewing")


class DomainError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def _fail(code, message):
    raise DomainError(code, message)


@contextmanager
def write_transaction(connection):
    if connection.in_transaction:
        _fail("TRANSACTION_ACTIVE", "Operation must own its transaction")
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        _fail("FOREIGN_KEYS_DISABLED", "Use yottaflex.db.connect")
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield
        connection.commit()
    except BaseException:
        connection.rollback()
        raise


def _metadata(when, reason_code, correlation_id):
    if type(when) is not int or not 0 <= when <= 253402300799:
        _fail("INVALID_TIMESTAMP", "Logical time must be whole UTC epoch seconds")
    if not isinstance(reason_code, str) or not reason_code.strip():
        _fail("METADATA_REQUIRED", "A nonblank decision/reason code is required")
    if correlation_id is not None and (not isinstance(correlation_id,str) or not correlation_id.strip()):
        _fail("METADATA_REQUIRED", "Correlation ID must be nonblank when supplied")


def _row(connection, table, key, value, code):
    row = connection.execute(f'SELECT * FROM "{table}" WHERE "{key}"=?', (value,)).fetchone()
    if row is None:
        _fail(code, f"Unknown {table} identity")
    return row


def _authorize(connection, actor_id, when, requisition_id=None, *, participant=None):
    actor = _row(connection,"Staff","staff_id",actor_id,"ACTOR_NOT_FOUND")
    if actor["status"] != "active" or actor["valid_from"] > when or (actor["valid_to"] is not None and when >= actor["valid_to"]):
        _fail("ACTOR_UNAUTHORIZED", "Actor is not effective")
    permitted = actor["role"] in ("hr","administrator")
    if requisition_id and actor["role"] == "manager":
        owner = connection.execute("SELECT h.staff_id FROM Requisition r JOIN HiringManager h USING(hiring_manager_id) WHERE r.requisition_id=?", (requisition_id,)).fetchone()
        permitted = owner is not None and owner[0] == actor_id
    if participant:
        permitted |= bool(connection.execute("SELECT 1 FROM InterviewParticipant WHERE interview_id=? AND staff_id=? AND assignment_role='reviewer'", (participant,actor_id)).fetchone())
    if not permitted:
        _fail("ACTOR_UNAUTHORIZED", "HR, administrator or owning manager required")


def _last_event(connection, subject, key, identity, status, when):
    event = connection.execute(f'SELECT * FROM "{subject}Event" WHERE "{key}"=? ORDER BY sequence DESC LIMIT 1', (identity,)).fetchone()
    if event is None or event["new_status"] != status:
        _fail("HISTORY_MISMATCH", "Projection must agree with latest event")
    if when < event["occurred_at"]:
        _fail("EVENT_TIME_INVALID", "Operation predates existing history")
    return event


def next_id(connection, table, column, kind):
    current = connection.execute(f'SELECT MAX("{column}") FROM "{table}"').fetchone()[0]
    counter = int(current[-6:])+1 if current else 1
    if counter > 999999:
        _fail("ID_CAPACITY_EXHAUSTED", "Six-digit identity capacity exhausted")
    return numbered_id(kind,counter)


def _append_event(connection, subject, key, identity, kind, previous, new, actor, when, reason, correlation, before, after, *, candidate=None, participants=None, details=None):
    table = subject+"Event"
    prefix = {"Application":"application_event","Candidate":"candidate_event","Interview":"interview_event",
              "Scorecard":"scorecard_event","Offer":"offer_event","Approval":"approval_event"}[subject]
    event_id = next_id(connection,table,"event_id",prefix)
    sequence = connection.execute(f'SELECT COALESCE(MAX(sequence),0)+1 FROM "{table}" WHERE "{key}"=?', (identity,)).fetchone()[0]
    snapshot = {"before":before,"after":after}
    if participants is not None:
        snapshot["participants"] = sorted(participants)
    if details is not None:
        snapshot["decision"] = details
    connection.execute(f'''INSERT INTO "{table}" (event_id,"{key}",sequence,event_type,previous_status,new_status,
        actor_staff_id,actor_candidate_id,occurred_at,recorded_at,reason_code,correlation_id,snapshot_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', (event_id,identity,sequence,kind,previous,new,actor,candidate,
        when,when,reason.strip(),correlation or identity,stable_json(snapshot)))
    return event_id


def _app_change(connection, app, status, kind, actor, when, reason, correlation, *, candidate=None, details=None):
    _last_event(connection,"Application","application_id",app["application_id"],app["status"],when)
    if when < app["updated_at"]:
        _fail("EVENT_TIME_INVALID", "Application operation predates projection")
    connection.execute("UPDATE Application SET status=?,updated_at=? WHERE application_id=?", (status,when,app["application_id"]))
    return _append_event(connection,"Application","application_id",app["application_id"],kind,app["status"],status,
        actor,when,reason,correlation,{"status":app["status"],"updated_at":app["updated_at"]},
        {"status":status,"updated_at":when},candidate=candidate,details=details)


def _eligible_application(connection, application_id):
    app = _row(connection,"Application","application_id",application_id,"APPLICATION_NOT_FOUND")
    if app["status"] == "withdrawn":
        _fail("APPLICATION_WITHDRAWN", "Withdrawn applications cannot be booked")
    candidate = _row(connection,"Candidate","candidate_id",app["candidate_id"],"CANDIDATE_NOT_FOUND")
    if candidate["status"] != "active":
        _fail("CANDIDATE_WITHDRAWN", "Candidate is withdrawn")
    return app


def _eligible_requisition(connection, requisition_id, when, start=None, end=None):
    req = _row(connection,"Requisition","requisition_id",requisition_id,"REQUISITION_NOT_FOUND")
    if req["status"] not in ("approved","open"):
        _fail("REQUISITION_NOT_APPROVED", "Requisition is not approved/open")
    start = when if start is None else start
    end = start+1 if end is None else end
    if req["valid_from"] > start or (req["valid_to"] is not None and req["valid_to"] < end):
        _fail("REQUISITION_INEFFECTIVE", "Requisition does not cover requested interval")
    approval = connection.execute("""SELECT 1 FROM Approval a JOIN Staff s ON s.staff_id=a.approver_staff_id
        WHERE a.requisition_id=? AND a.offer_id IS NULL AND a.status='approved' AND a.decided_at<=?
        AND a.valid_from<=? AND (a.valid_to IS NULL OR a.valid_to>=?) AND s.role IN ('hr','administrator')""",
        (requisition_id,when,start,end)).fetchone()
    evidence = connection.execute("SELECT 1 FROM RequisitionEvent WHERE requisition_id=? AND new_status='approved' AND occurred_at<=?", (requisition_id,when)).fetchone()
    if not approval or not evidence:
        _fail("REQUISITION_NOT_APPROVED", "Causal approval decision/history required")
    return req


def _interval(start, end):
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= 253402300799 or end-start not in ALLOWED_DURATIONS:
        _fail("INVALID_INTERVAL", "Use positive whole-second UTC interval of 30, 45 or 60 minutes")


def covers(intervals, start, end):
    cursor = start
    for left,right in sorted(intervals):
        if left > cursor:
            break
        cursor = max(cursor,right)
        if cursor >= end:
            return True
    return False


def _members(connection, panel, req, start, end, assigned=None):
    if panel["requisition_id"] != req["requisition_id"]:
        _fail("PANEL_REQUISITION_MISMATCH", "Panel belongs to another requisition")
    if panel["status"] != "active" or panel["valid_from"] > start or (panel["valid_to"] is not None and panel["valid_to"] < end):
        _fail("PANEL_INEFFECTIVE", "Panel must cover the complete interview")
    role, _, _ = role_details(req["title"])
    if panel["purpose"] != "technical:"+role[0]:
        _fail("PANEL_CONFIGURATION_INVALID", "Panel purpose is not compatible with role/stage")
    rows = list(connection.execute("SELECT * FROM PanelMember WHERE panel_id=? AND status='active' ORDER BY staff_id,valid_from", (panel["panel_id"],)))
    groups = {}
    for row in rows:
        groups.setdefault(row["staff_id"],[]).append((row["valid_from"],row["valid_to"] or 253402300799))
    for intervals in groups.values():
        if any(a[1]>b[0] for a,b in zip(intervals,intervals[1:])):
            _fail("PANEL_MEMBERSHIP_OVERLAP", "Duplicate simultaneous panel membership")
    members = sorted(assigned) if assigned is not None else sorted(staff for staff,times in groups.items() if any(a<=start<b for a,b in times))
    if not PANEL_MINIMUM[role[0]] <= len(members) <= 4 or len(members) != len(set(members)):
        _fail("PANEL_CONFIGURATION_INVALID", "Role requires two/three to four distinct members")
    for staff in members:
        if not covers(groups.get(staff,[]),start,end):
            _fail("MEMBERSHIP_INEFFECTIVE", "Assigned member does not cover complete interval")
        person = _row(connection,"Staff","staff_id",staff,"INTERVIEWER_NOT_FOUND")
        if person["role"] not in ("interviewer","manager") or person["status"] != "active" or person["valid_from"]>start or (person["valid_to"] is not None and person["valid_to"]<end):
            _fail("INTERVIEWER_INELIGIBLE", "Interviewer role/status/effective dates invalid")
    return members


def _calendar(connection, staff, start, end):
    blocked = connection.execute("SELECT 1 FROM Availability WHERE staff_id=? AND status='blocked' AND start_at<? AND ?<end_at LIMIT 1", (staff,end,start)).fetchone()
    intervals = [(row[0],row[1]) for row in connection.execute("SELECT start_at,end_at FROM Availability WHERE staff_id=? AND status='available' AND start_at<? AND end_at>? ORDER BY start_at,end_at", (staff,end,start))]
    if blocked or not covers(intervals,start,end):
        _fail("INTERVIEWER_UNAVAILABLE", "Calendar coverage missing or explicitly blocked")


def check_slot(connection, app, panel, start, end, *, exclude=None, assigned=None):
    """Read-only planner check; public mutation ALWAYS rechecks under writer lock."""
    _interval(start,end)
    req = _row(connection,"Requisition","requisition_id",app["requisition_id"],"REQUISITION_NOT_FOUND")
    members = _members(connection,panel,req,start,end,assigned)
    for staff in members:
        _calendar(connection,staff,start,end)
        busy = connection.execute("""SELECT i.interview_id FROM InterviewParticipant p JOIN Interview i USING(interview_id)
            WHERE p.staff_id=? AND i.status IN ('scheduled','completed','no_show') AND i.start_at<? AND ?<i.end_at
            AND (? IS NULL OR i.interview_id<>?) LIMIT 1""", (staff,end,start,exclude,exclude)).fetchone()
        if busy:
            _fail("INTERVIEWER_CONFLICT", "Interviewer already reserved")
    busy = connection.execute("""SELECT i.interview_id FROM Application a JOIN Interview i USING(application_id)
        WHERE a.candidate_id=? AND i.status IN ('scheduled','completed','no_show') AND i.start_at<? AND ?<i.end_at
        AND (? IS NULL OR i.interview_id<>?) LIMIT 1""", (app["candidate_id"],end,start,exclude,exclude)).fetchone()
    if busy:
        _fail("CANDIDATE_CONFLICT", "Candidate already reserved")
    return members


def transition_application(connection, application_id, target_status, *, actor_id, when, reason_code, correlation_id=None):
    if target_status == "reviewed":
        from .evaluation import review_application
        return review_application(connection,application_id,actor_id=actor_id,when=when,reason_code=reason_code,correlation_id=correlation_id)
    if target_status == "withdrawn":
        return withdraw_application(connection,application_id,actor_id=actor_id,when=when,reason_code=reason_code,correlation_id=correlation_id)
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        app = _eligible_application(connection,application_id)
        _authorize(connection,actor_id,when,app["requisition_id"])
        _last_event(connection,"Application","application_id",application_id,app["status"],when)
        if (app["status"],target_status) in {("reviewed","offer"),("offer","hired")}:
            _fail("OFFER_OPERATION_REQUIRED", "Use transactional offer creation/approval/acceptance operations")
        if target_status == "interviewing" and app["status"] == "screening":
            _fail("INTERVIEW_REQUIRED", "Use atomic schedule_interview, not a stage bypass")
        if (app["status"],target_status) not in {("applied","screening"),("applied","rejected"),("screening","rejected")}:
            _fail("INVALID_TRANSITION", "Transition is not permitted")
        _eligible_requisition(connection,app["requisition_id"],when)
        return _app_change(connection,app,target_status,"status_changed",actor_id,when,reason_code,correlation_id)


def schedule_interview(connection, application_id, panel_id, start, end, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        app = _eligible_application(connection,application_id)
        _authorize(connection,actor_id,when,app["requisition_id"])
        _last_event(connection,"Application","application_id",application_id,app["status"],when)
        if app["status"] not in ("screening","interviewing"):
            _fail("APPLICATION_STAGE_INELIGIBLE", "Screening required before scheduling")
        _interval(start,end)
        if start < when:
            _fail("INTERVIEW_IN_PAST", "Booking cannot precede its decision")
        _eligible_requisition(connection,app["requisition_id"],when,start,end)
        panel = _row(connection,"InterviewPanel","panel_id",panel_id,"PANEL_NOT_FOUND")
        members = check_slot(connection,app,panel,start,end)
        identity = next_id(connection,"Interview","interview_id","interview")
        connection.execute("INSERT INTO Interview VALUES (?,?,?,?,?,?,?)", (identity,application_id,panel_id,app["requisition_id"],start,end,"scheduled"))
        connection.executemany("INSERT INTO InterviewParticipant VALUES (?,?,?,?)", ((identity,staff,"reviewer",when) for staff in members))
        after = {"status":"scheduled","start_at":start,"end_at":end}
        _append_event(connection,"Interview","interview_id",identity,"created",None,"scheduled",actor_id,when,reason_code,correlation_id,
                      {"status":None,"start_at":None,"end_at":None},after,participants=members)
        _app_change(connection,app,"interviewing","status_changed" if app["status"]=="screening" else "revised",
                    actor_id,when,reason_code,correlation_id or identity)
        return identity


def _interview_context(connection, interview_id, actor, when, *, completion=False):
    interview = _row(connection,"Interview","interview_id",interview_id,"INTERVIEW_NOT_FOUND")
    if interview["status"] != "scheduled":
        _fail("INTERVIEW_STATE_INVALID", "Only scheduled interviews can change")
    app = _eligible_application(connection,interview["application_id"])
    if app["status"] != "interviewing":
        _fail("APPLICATION_STAGE_INELIGIBLE", "Interview lifecycle requires interviewing stage")
    _authorize(connection,actor,when,app["requisition_id"],participant=interview_id if completion else None)
    _last_event(connection,"Interview","interview_id",interview_id,interview["status"],when)
    _last_event(connection,"Application","application_id",app["application_id"],app["status"],when)
    return interview,app


def _interview_change(connection, interview, status, start, end, kind, actor, when, reason, correlation):
    members = [row[0] for row in connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? ORDER BY staff_id", (interview["interview_id"],))]
    before = {name:interview[name] for name in ("status","start_at","end_at")}
    after = {"status":status,"start_at":start,"end_at":end}
    connection.execute("UPDATE Interview SET status=?,start_at=?,end_at=? WHERE interview_id=?", (status,start,end,interview["interview_id"]))
    _append_event(connection,"Interview","interview_id",interview["interview_id"],kind,interview["status"],status,
                  actor,when,reason,correlation,before,after,participants=members)


def reschedule_interview(connection, interview_id, start, end, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        interview,app = _interview_context(connection,interview_id,actor_id,when)
        if when > interview["start_at"]:
            _fail("INTERVIEW_STARTED", "Cannot reschedule an already started booking")
        _interval(start,end)
        if start < when:
            _fail("INTERVIEW_IN_PAST", "Replacement cannot precede decision")
        if (start,end) == (interview["start_at"],interview["end_at"]):
            _fail("NO_SCHEDULE_CHANGE", "Replacement must change the booking")
        _eligible_requisition(connection,app["requisition_id"],when,start,end)
        panel = _row(connection,"InterviewPanel","panel_id",interview["panel_id"],"PANEL_NOT_FOUND")
        assigned = [row[0] for row in connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? ORDER BY staff_id", (interview_id,))]
        check_slot(connection,app,panel,start,end,exclude=interview_id,assigned=assigned)
        _interview_change(connection,interview,"scheduled",start,end,"rescheduled",actor_id,when,reason_code,correlation_id)
        _app_change(connection,app,app["status"],"revised",actor_id,when,reason_code,correlation_id or interview_id)
        return interview_id


def cancel_interview(connection, interview_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        interview,app = _interview_context(connection,interview_id,actor_id,when)
        _interview_change(connection,interview,"cancelled",interview["start_at"],interview["end_at"],"cancelled",actor_id,when,reason_code,correlation_id)
        _app_change(connection,app,app["status"],"revised",actor_id,when,reason_code,correlation_id or interview_id)


def complete_interview(connection, interview_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        interview,app = _interview_context(connection,interview_id,actor_id,when,completion=True)
        if when < interview["end_at"]:
            _fail("INTERVIEW_NOT_ENDED", "Completion cannot precede interview end")
        _interview_change(connection,interview,"completed",interview["start_at"],interview["end_at"],"status_changed",actor_id,when,reason_code,correlation_id)
        _app_change(connection,app,app["status"],"revised",actor_id,when,reason_code,correlation_id or interview_id)


def _withdraw_app(connection, app, actor, when, reason, correlation, candidate_actor):
    if app["status"] not in WITHDRAWABLE:
        _fail("INVALID_TRANSITION", "Application is terminal or outside Phase 04")
    _last_event(connection,"Application","application_id",app["application_id"],app["status"],when)
    cancelled = []
    for interview in connection.execute("SELECT * FROM Interview WHERE application_id=? AND status='scheduled' ORDER BY interview_id", (app["application_id"],)).fetchall():
        _last_event(connection,"Interview","interview_id",interview["interview_id"],"scheduled",when)
        _interview_change(connection,interview,"cancelled",interview["start_at"],interview["end_at"],"cancelled",actor,when,reason,correlation)
        cancelled.append(interview["interview_id"])
    _app_change(connection,app,"withdrawn","withdrawn",actor,when,reason,correlation,candidate=candidate_actor)
    return cancelled


def withdraw_application(connection, application_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        app = _row(connection,"Application","application_id",application_id,"APPLICATION_NOT_FOUND")
        _authorize(connection,actor_id,when,app["requisition_id"])
        return _withdraw_app(connection,app,actor_id,when,reason_code,correlation_id,app["candidate_id"])


def withdraw_candidate(connection, candidate_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        candidate = _row(connection,"Candidate","candidate_id",candidate_id,"CANDIDATE_NOT_FOUND")
        _authorize(connection,actor_id,when)  # Global scope requires HR/admin.
        if candidate["status"] != "active":
            _fail("CANDIDATE_WITHDRAWN", "Candidate already withdrew")
        _last_event(connection,"Candidate","candidate_id",candidate_id,"active",when)
        applications = connection.execute("SELECT * FROM Application WHERE candidate_id=? ORDER BY application_id", (candidate_id,)).fetchall()
        if any(app["status"]=="hired" for app in applications):
            _fail("POST_HIRE_POLICY_REQUIRED", "Global withdrawal after hiring requires an explicit future policy")
        if any(app["status"] in ("reviewed","offer") for app in applications):
            _fail("ADVANCED_WITHDRAWAL_UNSUPPORTED", "Advanced application withdrawal needs an explicit future policy")
        cancelled, changed = [], []
        for app in applications:
            if app["status"] in WITHDRAWABLE:
                cancelled.extend(_withdraw_app(connection,app,actor_id,when,reason_code,correlation_id or candidate_id,candidate_id))
                changed.append(app["application_id"])
        connection.execute("UPDATE Candidate SET status='withdrawn',withdrawn_at=? WHERE candidate_id=?", (when,candidate_id))
        _append_event(connection,"Candidate","candidate_id",candidate_id,"withdrawn","active","withdrawn",actor_id,when,reason_code,
                      correlation_id,{"status":"active","withdrawn_at":None},{"status":"withdrawn","withdrawn_at":when},candidate=candidate_id)
        return {"applications":changed,"cancelled_interviews":cancelled}
