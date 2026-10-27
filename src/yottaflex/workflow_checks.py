"""Independent Phase 04 scheduling/history acceptance and master preservation."""

from collections import Counter
import hashlib
import json

from .canonical import stable_json, table_digest
from .generation_checks import validate_generated
from .ids import numbered_id, valid_numbered_id
from .workflow import DomainError, check_slot


def _query_hash(connection, sql, parameters=()):
    digest = hashlib.sha256()
    for row in connection.execute(sql,parameters):
        digest.update((stable_json(list(row))+"\n").encode())
    return digest.hexdigest()


def master_fingerprint(connection, config):
    static = ("HiringManager","Requisition","SkillRequirement","CandidateSkill",
              "RequisitionEvent","SchemaMetadata")
    result = {name:table_digest(connection,name) for name in static}
    queries = {
        "candidate_identity":"SELECT candidate_id,display_name,experience_years,contact_email,created_at FROM Candidate ORDER BY candidate_id",
        "application_identity":"SELECT application_id,candidate_id,requisition_id,applied_at FROM Application ORDER BY application_id",
        "candidate_creation_history":"SELECT * FROM CandidateEvent WHERE sequence=1 ORDER BY event_id",
        "application_creation_history":"SELECT * FROM ApplicationEvent WHERE sequence=1 ORDER BY event_id"}
    result.update({name:_query_hash(connection,sql) for name,sql in queries.items()})
    result["requisition_approvals"] = _query_hash(connection,"SELECT * FROM Approval WHERE requisition_id IS NOT NULL ORDER BY approval_id")
    result["requisition_approval_history"] = _query_hash(connection,"SELECT e.* FROM ApprovalEvent e JOIN Approval a USING(approval_id) WHERE a.requisition_id IS NOT NULL ORDER BY e.event_id")
    result["original_staff"] = _query_hash(connection,"SELECT * FROM Staff WHERE staff_id<=? ORDER BY staff_id",
                                          (numbered_id("staff",config.managers+4),))
    return result


def conflict_counts(connection):
    result = {}
    for name, statuses in (("active","'scheduled'"),("capacity","'scheduled','completed','no_show'")):
        result[name+"_interviewer_overlaps"] = connection.execute(f"""SELECT COUNT(*) FROM InterviewParticipant p
            JOIN Interview i ON i.interview_id=p.interview_id
            JOIN InterviewParticipant q ON q.staff_id=p.staff_id AND p.interview_id<q.interview_id
            JOIN Interview j ON j.interview_id=q.interview_id
            WHERE i.status IN ({statuses}) AND j.status IN ({statuses}) AND i.start_at<j.end_at AND j.start_at<i.end_at""").fetchone()[0]
        result[name+"_candidate_overlaps"] = connection.execute(f"""SELECT COUNT(*) FROM Application a
            JOIN Interview i ON i.application_id=a.application_id JOIN Application b ON b.candidate_id=a.candidate_id
            JOIN Interview j ON j.application_id=b.application_id AND i.interview_id<j.interview_id
            WHERE i.status IN ({statuses}) AND j.status IN ({statuses}) AND i.start_at<j.end_at AND j.start_at<i.end_at""").fetchone()[0]
    return result


APP_EDGES = {(None,"applied","created"),("applied","screening","status_changed"),
    ("screening","interviewing","status_changed"),("applied","rejected","status_changed"),
    ("screening","rejected","status_changed"),("interviewing","interviewing","revised")} | {
    (state,"withdrawn","withdrawn") for state in ("applied","screening","interviewing")}
CANDIDATE_EDGES = {(None,"active","created"),("active","withdrawn","withdrawn")}
INTERVIEW_EDGES = {(None,"scheduled","created"),("scheduled","scheduled","rescheduled"),
    ("scheduled","cancelled","cancelled"),("scheduled","completed","status_changed")}


def _history_errors(connection, *, evaluations=False):
    errors = Counter()
    extra = {("interviewing","reviewed","decision_recorded"),("interviewing","rejected","decision_recorded"),
        ("reviewed","rejected","decision_recorded"),("reviewed","offer","status_changed"),
        ("offer","offer","revised"),("offer","rejected","decision_recorded"),("offer","hired","status_changed"),
        ("reviewed","withdrawn","withdrawn")} if evaluations else set()
    for subject,key,edges in (("Application","application_id",APP_EDGES|extra),
                              ("Candidate","candidate_id",CANDIDATE_EDGES),
                              ("Interview","interview_id",INTERVIEW_EDGES)):
        for projection in connection.execute(f'SELECT * FROM "{subject}" ORDER BY "{key}"'):
            events = list(connection.execute(f'SELECT * FROM "{subject}Event" WHERE "{key}"=? ORDER BY sequence', (projection[key],)))
            if not events:
                errors["missing_history"] += 1
                continue
            previous, previous_time, previous_slot = None,-1,None
            participants = None
            if subject == "Interview":
                participants = [row[0] for row in connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? ORDER BY staff_id", (projection[key],))]
            for index,event in enumerate(events,1):
                snapshot = json.loads(event["snapshot_json"])
                errors["event_sequence"] += int(event["sequence"] != index)
                errors["event_continuity"] += int(event["previous_status"] != previous)
                errors["legal_transitions"] += int((event["previous_status"],event["new_status"],event["event_type"]) not in edges)
                errors["event_chronology"] += int(event["occurred_at"]<previous_time or event["recorded_at"]<event["occurred_at"])
                before,after = snapshot.get("before",{}),snapshot.get("after",{})
                if not isinstance(before,dict) or not isinstance(after,dict):
                    errors["snapshot_shape"] += 1
                    before,after = {},{}
                errors["status_snapshots"] += int(before.get("status")!=event["previous_status"] or after.get("status")!=event["new_status"])
                if subject == "Application" and index > 1:
                    errors["application_time_snapshots"] += int(before.get("updated_at")!=previous_time or after.get("updated_at")!=event["occurred_at"])
                if subject == "Interview":
                    slot = (after.get("start_at"),after.get("end_at"))
                    old_slot = (before.get("start_at"),before.get("end_at"))
                    errors["participant_snapshots"] += int(snapshot.get("participants")!=participants)
                    valid_slot = all(type(value) is int for value in slot) and 0 <= slot[0] < slot[1] <= 253402300799 and slot[1]-slot[0] in (1800,2700,3600)
                    errors["history_intervals"] += int(not valid_slot)
                    if index == 1:
                        errors["schedule_history"] += int(old_slot!=(None,None) or not valid_slot or slot[0]<event["occurred_at"])
                    else:
                        errors["schedule_history"] += int(old_slot!=previous_slot)
                        if event["event_type"] == "rescheduled":
                            errors["reschedule_history"] += int(slot==previous_slot or not valid_slot or slot[0]<event["occurred_at"] or previous_slot[0] is None or previous_slot[0]<event["occurred_at"])
                        else:
                            errors["schedule_history"] += int(slot!=previous_slot)
                    if event["new_status"] == "completed":
                        errors["completion_chronology"] += int(not valid_slot or event["occurred_at"]<slot[1])
                    previous_slot = slot
                if subject == "Application" and (event["new_status"]=="interviewing"):
                    related = connection.execute("""SELECT 1 FROM Interview i JOIN InterviewEvent e USING(interview_id)
                        WHERE i.application_id=? AND e.occurred_at=? AND e.actor_staff_id=? AND e.correlation_id=? LIMIT 1""",
                        (projection[key],event["occurred_at"],event["actor_staff_id"],event["correlation_id"])).fetchone()
                    errors["application_interview_audit_link"] += int(related is None)
                previous,previous_time = event["new_status"],event["occurred_at"]
            errors["projection_status"] += int(previous!=projection["status"])
            if subject == "Application":
                errors["application_projection_time"] += int(projection["updated_at"]!=previous_time)
            if subject == "Candidate" and projection["status"]=="withdrawn":
                errors["candidate_withdrawal_history"] += int(projection["withdrawn_at"]!=previous_time)
            if subject == "Interview":
                errors["schedule_projection"] += int(previous_slot!=(projection["start_at"],projection["end_at"]))
                errors["participant_recording_time"] += connection.execute("SELECT COUNT(*) FROM InterviewParticipant WHERE interview_id=? AND assigned_at<>?", (projection[key],events[0]["occurred_at"])).fetchone()[0]
    return errors


def validate_workflow(connection, config, interview_target, *, phase="interviews"):
    if phase not in ("interviews","evaluations"):
        raise ValueError("Unknown workflow validation phase")
    baseline = validate_generated(connection,config,phase=phase)
    checks = list(baseline["checks"])
    def add(name,value):
        checks.append({"check":name,"violations":int(value)})
    def scalar(sql):
        return connection.execute(sql).fetchone()[0]
    add("exact_interview_count",abs(scalar("SELECT COUNT(*) FROM Interview")-interview_target))
    for name,count in conflict_counts(connection).items():
        add(name,count)
    add("panel_requisition_joins",scalar("""SELECT COUNT(*) FROM Interview i JOIN Application a USING(application_id)
        JOIN InterviewPanel p USING(panel_id) WHERE i.requisition_id<>a.requisition_id OR i.requisition_id<>p.requisition_id"""))
    add("membership_overlap",scalar("""SELECT COUNT(*) FROM PanelMember a JOIN PanelMember b ON a.panel_id=b.panel_id
        AND a.staff_id=b.staff_id AND a.valid_from<b.valid_from WHERE a.status='active' AND b.status='active'
        AND a.valid_from<COALESCE(b.valid_to,253402300799) AND b.valid_from<COALESCE(a.valid_to,253402300799)"""))
    slot_errors = Counter()
    for interview in connection.execute("SELECT * FROM Interview WHERE status='scheduled' ORDER BY interview_id"):
        app = connection.execute("SELECT * FROM Application WHERE application_id=?", (interview["application_id"],)).fetchone()
        panel = connection.execute("SELECT * FROM InterviewPanel WHERE panel_id=?", (interview["panel_id"],)).fetchone()
        assigned = [row[0] for row in connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? ORDER BY staff_id", (interview["interview_id"],))]
        try:
            check_slot(connection,app,panel,interview["start_at"],interview["end_at"],exclude=interview["interview_id"],assigned=assigned)
        except DomainError as error:
            slot_errors[error.code] += 1
    add("active_membership_calendar_participants",sum(slot_errors.values()))
    add("active_withdrawal_or_stage_mismatch",scalar("""SELECT COUNT(*) FROM Interview i JOIN Application a USING(application_id)
        JOIN Candidate c USING(candidate_id) WHERE i.status='scheduled' AND
        (a.status<>'interviewing' OR c.status<>'active')"""))
    add("global_withdrawal_consistency",scalar("""SELECT COUNT(*) FROM Application a JOIN Candidate c USING(candidate_id)
        WHERE c.status='withdrawn' AND a.status NOT IN ('withdrawn','rejected','hired')"""))
    add("intervals_and_states",scalar("SELECT COUNT(*) FROM Interview WHERE end_at-start_at NOT IN (1800,2700,3600) OR status NOT IN ('scheduled','cancelled','completed')"))
    add("interview_event_actors",scalar("""SELECT COUNT(*) FROM InterviewEvent e JOIN Staff s ON s.staff_id=e.actor_staff_id
        JOIN Interview i USING(interview_id) JOIN Requisition r ON r.requisition_id=i.requisition_id
        JOIN HiringManager h USING(hiring_manager_id) WHERE s.valid_from>e.occurred_at
        OR (s.valid_to IS NOT NULL AND e.occurred_at>=s.valid_to)
        OR NOT (s.role IN ('hr','administrator') OR (s.role='manager' AND s.staff_id=h.staff_id)
        OR (e.new_status='completed' AND EXISTS (SELECT 1 FROM InterviewParticipant p
            WHERE p.interview_id=e.interview_id AND p.staff_id=s.staff_id AND p.assignment_role='reviewer')))"""))
    id_errors = 0
    for table,column,kind in (("Interview","interview_id","interview"),("InterviewPanel","panel_id","panel"),
                              ("Availability","availability_id","availability"),("InterviewEvent","event_id","interview_event")):
        id_errors += sum(not valid_numbered_id(kind,row[0]) for row in connection.execute(f'SELECT "{column}" FROM "{table}"'))
    add("interview_support_id_formats",id_errors)
    for name,value in sorted(_history_errors(connection,evaluations=phase=="evaluations").items()):
        add(name,value)
    leakage = 0
    for table in ("InterviewEvent","ApplicationEvent","CandidateEvent"):
        leakage += scalar(f'''SELECT COUNT(*) FROM "{table}" e,json_tree(e.snapshot_json) j
            WHERE j.key IN ('issue_type','ground_truth','expected_decision','anomaly_label')''')
    add("workflow_truth_leakage",leakage)
    return {"passed":all(item["violations"]==0 for item in checks),"checks":checks,
            "slot_error_codes":dict(sorted(slot_errors.items()))}


def workflow_statistics(connection):
    def histogram(sql):
        return {str(row[0]):row[1] for row in connection.execute(sql)}
    return {"conflicts":conflict_counts(connection),
        "interview_statuses":histogram("SELECT status,COUNT(*) FROM Interview GROUP BY status ORDER BY status"),
        "application_statuses":histogram("SELECT status,COUNT(*) FROM Application GROUP BY status ORDER BY status"),
        "rescheduled_events":connection.execute("SELECT COUNT(*) FROM InterviewEvent WHERE event_type='rescheduled'").fetchone()[0],
        "candidate_withdrawals":connection.execute("SELECT COUNT(*) FROM Candidate WHERE status='withdrawn'").fetchone()[0],
        "application_withdrawals":connection.execute("SELECT COUNT(*) FROM Application WHERE status='withdrawn'").fetchone()[0],
        "durations_seconds":histogram("SELECT end_at-start_at,COUNT(*) FROM Interview GROUP BY end_at-start_at ORDER BY 1"),
        "schedule_dates_utc":histogram("SELECT date(start_at,'unixepoch'),COUNT(*) FROM Interview GROUP BY 1 ORDER BY 1"),
        "panel_sizes":histogram("SELECT n,COUNT(*) FROM (SELECT panel_id,COUNT(*) n FROM PanelMember GROUP BY panel_id) GROUP BY n ORDER BY n")}


def main():
    import argparse
    from contextlib import closing
    from pathlib import Path
    from .db import connect,initialize
    from .generation_config import GenerationConfig
    parser = argparse.ArgumentParser(description="Validate existing Phase 04 workflow data")
    parser.add_argument("--database",type=Path,required=True)
    parser.add_argument("--profile",choices=("starter","full"),required=True)
    parser.add_argument("--seed",type=int,default=20261022)
    parser.add_argument("--interviews",type=int)
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error("Database must already exist")
    target = args.interviews if args.interviews is not None else (2000 if args.profile=="full" else 40)
    with closing(connect(args.database)) as connection:
        initialize(connection)
        result = validate_workflow(connection,GenerationConfig(args.profile,args.seed),target)
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
