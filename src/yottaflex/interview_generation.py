"""Fixed-capacity deterministic workflow generation through public operations."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import random

from .generation_config import DAY
from .generation_checks import role_details
from .ids import numbered_id
from .matching import load_matching_inputs, skill_fit
from .workflow import (DomainError, PANEL_MINIMUM, check_slot, complete_interview,
    cancel_interview, reschedule_interview, schedule_interview, transition_application,
    withdraw_application, withdraw_candidate, write_transaction)
from .workflow_checks import workflow_statistics


@dataclass(frozen=True)
class SchedulingConfig:
    target: int
    working_days: int = 20
    interviewer_count: int | None = None
    start_hour: int = 9
    end_hour: int = 17

    @classmethod
    def for_profile(cls, config, target=None):
        return cls(target if target is not None else (2000 if config.profile == "full" else 40))

    def validate_for(self, config):
        if type(self.target) is not int or not 1 <= self.target <= config.scale.applications:
            raise ValueError("Interview target must be positive and no greater than application count")
        if config.profile == "full" and self.target != 2000:
            raise ValueError("FULL interview target must remain exactly 2000")
        if type(self.working_days) is not int or not 1 <= self.working_days <= 20:
            raise ValueError("Calendar must contain 1..20 working days")
        if self.interviewer_count is not None and (type(self.interviewer_count) is not int or not 3 <= self.interviewer_count <= 200):
            raise ValueError("Interviewer pool must contain 3..200 staff")
        if any(type(value) is not int for value in (self.start_hour,self.end_hour)) or not 0 <= self.start_hour < self.end_hour <= 24:
            raise ValueError("Working hours must be a positive UTC day interval")


def _supporting_records(connection, config, scheduling):
    """Create the declared calendar ONCE, before any capacity search."""
    origin = config.logical_origin
    pool_size = scheduling.interviewer_count or max(8,min(80,(config.scale.requisitions+2)//3))
    staff = [numbered_id("staff",config.managers+5+i) for i in range(pool_size)]
    random.Random(config.seed ^ 0x50414E454C).shuffle(staff)
    days, day = [], origin+160*DAY
    while len(days) < scheduling.working_days:
        if datetime.fromtimestamp(day,timezone.utc).weekday() < 5:
            days.append(day)
        day += DAY
    reqs = list(connection.execute("SELECT * FROM Requisition ORDER BY requisition_id"))
    panels = {}
    with write_transaction(connection):
        for index,identity in enumerate(sorted(staff),1):
            connection.execute("INSERT INTO Staff VALUES (?,?,?,'active',?,?)",
                (identity,f"Synthetic Interviewer {index:03d}","interviewer",origin+150*DAY,origin+190*DAY))
        for index,req in enumerate(reqs):
            role,_,_ = role_details(req["title"])
            panel_id = numbered_id("panel",index+1)
            connection.execute("INSERT INTO InterviewPanel VALUES (?,?,?,'active',?,?)",
                (panel_id,req["requisition_id"],"technical:"+role[0],origin+150*DAY,origin+190*DAY))
            for offset in range(PANEL_MINIMUM[role[0]]):
                connection.execute("INSERT INTO PanelMember VALUES (?,?,?,?,'active')",
                    (panel_id,staff[(index*3+offset)%pool_size],origin+150*DAY,origin+190*DAY))
            panels[req["requisition_id"]] = panel_id
        counter = 0
        for index,identity in enumerate(sorted(staff)):
            for day in days:
                # Slight deterministic stagger, applied even to constrained test windows.
                left = day+scheduling.start_hour*3600+(index%2)*1800
                right = day+scheduling.end_hour*3600-(index%3==0)*1800
                if right > left:
                    counter += 1
                    connection.execute("INSERT INTO Availability VALUES (?,?,?,?,'available')",
                        (numbered_id("availability",counter),identity,left,right))
                if scheduling.start_hour < 12 and scheduling.end_hour > 12:
                    counter += 1
                    connection.execute("INSERT INTO Availability VALUES (?,?,?,?,'blocked')",
                        (numbered_id("availability",counter),identity,day+12*3600,day+12*3600+2700))
    return reqs,panels,days,pool_size


def _selection(connection, config, target):
    candidates,requirements = load_matching_inputs(connection)
    groups = {}
    for app in connection.execute("SELECT * FROM Application ORDER BY application_id"):
        fit = skill_fit(requirements[app["requisition_id"]],candidates[app["candidate_id"]])
        groups.setdefault(app["requisition_id"],[]).append((fit.basis_points,app["candidate_id"],app["application_id"]))
    for rows in groups.values():
        rows.sort(key=lambda row:(-row[0],row[1],row[2]))
    selected, rank = [],0
    while len(selected) < target:
        for req in sorted(groups):
            if rank < len(groups[req]):
                selected.append((groups[req][rank][2],req,rank))
                if len(selected) == target:
                    break
        rank += 1
    return selected


def populate_interviews(connection, config, scheduling):
    scheduling.validate_for(config)
    reqs,panels,days,pool_size = _supporting_records(connection,config,scheduling)
    req_index = {row["requisition_id"]:index for index,row in enumerate(reqs)}
    durations = {row["requisition_id"]:(1800,2700,3600)[("Junior","Mid","Senior").index(role_details(row["title"])[1])] for row in reqs}
    probes, probe_codes, max_probes = 0,Counter(),0
    attempts, successes, rejected = Counter(),Counter(),[]
    clock = config.logical_origin+151*DAY
    actor = numbered_id("staff",2)

    def metadata(reason):
        nonlocal clock
        clock += 1
        return dict(actor_id=actor,when=clock,reason_code=reason)

    def slot(application_id, panel_id, duration, preferred_day, offset, *, exclude=None, assigned=None, old=None):
        nonlocal probes,max_probes
        app = connection.execute("SELECT * FROM Application WHERE application_id=?", (application_id,)).fetchone()
        panel = connection.execute("SELECT * FROM InterviewPanel WHERE panel_id=?", (panel_id,)).fetchone()
        slots = (scheduling.end_hour-scheduling.start_hour)*4-duration//900+1
        local_probes = 0
        for day_offset in range(len(days)):
            day = days[(preferred_day+day_offset)%len(days)]
            for step in range(max(0,slots)):
                start = day+scheduling.start_hour*3600+((offset+step)%slots)*900
                if old == (start,start+duration):
                    continue
                probes += 1
                local_probes += 1
                try:
                    check_slot(connection,app,panel,start,start+duration,exclude=exclude,assigned=assigned)
                except DomainError as error:
                    probe_codes[error.code] += 1
                    continue
                max_probes = max(max_probes,local_probes)
                return start,start+duration
        raise DomainError("INSUFFICIENT_CAPACITY",f"Cannot place {application_id}: target={scheduling.target}, placed={successes['schedule']}, "
            f"pool={pool_size}, days={len(days)}, UTC hours={scheduling.start_hour}..{scheduling.end_hour}, probes={local_probes}; "
            "review the declared capacity or selection; no calendar expansion was attempted")

    selected = _selection(connection,config,scheduling.target)
    bookings = []
    for app,req,rank in selected:
        transition_application(connection,app,"screening",**metadata("SKILL_POOL_SELECTED"))
        index = req_index[req]
        start,end = slot(app,panels[req],durations[req],index+rank*3,rank*7+(index//20)*3)
        attempts["schedule"] += 1
        identity = schedule_interview(connection,app,panels[req],start,end,**metadata("PANEL_SLOT_RESERVED"))
        successes["schedule"] += 1
        bookings.append(identity)

    def reject(label, operation, expected):
        before = connection.total_changes
        # No SQL mutation should occur in these deliberately rejected examples.
        try:
            operation()
        except DomainError as error:
            if error.code != expected:
                raise
            if connection.total_changes != before:
                raise AssertionError("Rejected example performed a mutation")
            rejected.append({"attempt":label,"code":error.code,"state_changed":False})
        else:
            raise AssertionError("Expected business rejection")

    first = connection.execute("SELECT * FROM Interview ORDER BY interview_id LIMIT 1").fetchone()
    reject("review_without_evaluations",lambda:transition_application(connection,first["application_id"],"reviewed",**metadata("EXAMPLE_REVIEW_GATE")),"REVIEW_GATE_INCOMPLETE")
    other = connection.execute("SELECT * FROM Interview WHERE panel_id=? AND interview_id<>? ORDER BY interview_id LIMIT 1", (first["panel_id"],first["interview_id"])).fetchone()
    if other is not None:
        attempts["reschedule"] += 1
        reject("reschedule_into_busy_panel",lambda:reschedule_interview(connection,first["interview_id"],other["start_at"],other["end_at"],**metadata("EXAMPLE_CONFLICT")),"INTERVIEWER_CONFLICT")
        attempts["schedule"] += 1
        reject("schedule_into_busy_panel",lambda:schedule_interview(connection,other["application_id"],other["panel_id"],first["start_at"],first["end_at"],**metadata("EXAMPLE_CONFLICT")),"INTERVIEWER_CONFLICT")

    # Deterministic cohort positions, not independently randomized outcomes.
    for index,identity in enumerate(bookings):
        if index%20 != 0:
            continue
        interview = connection.execute("SELECT * FROM Interview WHERE interview_id=?", (identity,)).fetchone()
        assigned = [row[0] for row in connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? ORDER BY staff_id", (identity,))]
        start,end = slot(interview["application_id"],interview["panel_id"],interview["end_at"]-interview["start_at"],index+1,11,
            exclude=identity,assigned=assigned,old=(interview["start_at"],interview["end_at"]))
        attempts["reschedule"] += 1
        reschedule_interview(connection,identity,start,end,**metadata("CANDIDATE_TIME_CHANGE"))
        successes["reschedule"] += 1
    for index,identity in enumerate(bookings):
        if index%20 == 3:
            cancel_interview(connection,identity,**metadata("PANEL_SESSION_CANCELLED"))
            successes["direct_cancel"] += 1
    for index,identity in enumerate(bookings):
        if index%20 != 1:
            continue
        app = connection.execute("SELECT a.* FROM Interview i JOIN Application a USING(application_id) WHERE interview_id=?", (identity,)).fetchone()
        if app["status"] in ("applied","screening","interviewing"):
            withdraw_application(connection,app["application_id"],**metadata("APPLICATION_WITHDRAWAL"))
            successes["application_withdraw"] += 1
    for index,identity in enumerate(bookings):
        if index%20 != 2:
            continue
        candidate = connection.execute("SELECT c.* FROM Interview i JOIN Application a USING(application_id) JOIN Candidate c USING(candidate_id) WHERE interview_id=?", (identity,)).fetchone()
        if candidate["status"] == "active":
            withdraw_candidate(connection,candidate["candidate_id"],**metadata("GLOBAL_CANDIDATE_WITHDRAWAL"))
            successes["candidate_withdraw"] += 1
    # All early decisions precede meetings. Completion uses actual end times;
    # chronological order across applications need not equal generation order.
    for index,identity in enumerate(bookings):
        if index%20 != 4:
            continue
        interview = connection.execute("SELECT * FROM Interview WHERE interview_id=?", (identity,)).fetchone()
        if interview["status"] == "scheduled":
            complete_interview(connection,identity,actor_id=actor,when=interview["end_at"]+60,reason_code="INTERVIEW_HELD_AWAITING_EVALUATION")
            successes["complete"] += 1
    return {"policy_version":1,"target":scheduling.target,"pool_size":pool_size,
        "working_days":len(days),"working_hours_utc":[scheduling.start_hour,scheduling.end_hour],
        "calendar_start":days[0],"calendar_end":days[-1]+scheduling.end_hour*3600,
        "planning_probes":probes,"planning_rejections":dict(sorted(probe_codes.items())),
        "max_probes_one_operation":max_probes,"attempts":dict(sorted(attempts.items())),
        "successful_operations":dict(sorted(successes.items())),"rejected_examples":rejected,
        "statistics":workflow_statistics(connection)}
