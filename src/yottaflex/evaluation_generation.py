"""Deterministic evaluations and derived offers on a valid interview baseline."""

from collections import Counter
import hashlib
from time import perf_counter

from .evaluation import (applicable_criteria, create_scorecard, evaluate_application,
    reject_evaluated_application, review_application, set_scorecard_item, submit_scorecard)
from .generation_config import DAY
from .offers import (approval_limit, approved_band, accept_offer, create_offer,
    decide_offer, send_offer, submit_offer)
from .workflow import DomainError, complete_interview


def evaluation_statistics(connection):
    def histogram(table,column):
        return {str(row[0]):row[1] for row in connection.execute(f'SELECT "{column}",COUNT(*) FROM "{table}" GROUP BY "{column}" ORDER BY "{column}"')}
    return {"scorecard_statuses":histogram("Scorecard","status"),"offer_statuses":histogram("Offer","status"),
        "application_statuses":histogram("Application","status"),"interview_statuses":histogram("Interview","status"),
        "offer_approval_statuses":{row[0]:row[1] for row in connection.execute("SELECT status,COUNT(*) FROM Approval WHERE offer_id IS NOT NULL GROUP BY status ORDER BY status")},
        "scorecard_total_milli_histogram":histogram("Scorecard","total_score_milli"),
        "review_transitions":connection.execute("SELECT COUNT(*) FROM ApplicationEvent WHERE previous_status='interviewing' AND new_status='reviewed'").fetchone()[0],
        "hired_transitions":connection.execute("SELECT COUNT(*) FROM ApplicationEvent WHERE new_status='hired'").fetchone()[0]}


def populate_evaluations(connection, config):
    started = perf_counter()
    additional = 0
    for interview in connection.execute("SELECT * FROM Interview WHERE status='scheduled' ORDER BY interview_id").fetchall():
        if (int(interview["interview_id"][-6:])-1)%10 in (5,6):
            complete_interview(connection,interview["interview_id"],actor_id="STAFF-000002",when=interview["end_at"]+120,reason_code="EVALUATION_COHORT_INTERVIEW_HELD")
            additional += 1
    completed = list(connection.execute("SELECT * FROM Interview WHERE status='completed' ORDER BY interview_id"))
    clock = config.logical_origin+188*DAY
    def metadata(actor,reason):
        nonlocal clock
        clock += 1
        return dict(actor_id=actor,when=clock,reason_code=reason)
    rejections = []
    def rejected(label,callback,code):
        changes = connection.total_changes
        try:
            callback()
        except DomainError as error:
            if error.code!=code:
                raise
            if connection.total_changes!=changes:
                raise AssertionError("Rejected demonstration mutated data")
            rejections.append({"attempt":label,"code":code,"state_changed":False})
        else:
            raise AssertionError("Expected a rejected operation")
    decisions = Counter()
    for index,interview in enumerate(completed):
        reviewers = [row[0] for row in connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? AND assignment_role='reviewer' ORDER BY staff_id", (interview["interview_id"],))]
        criteria = applicable_criteria(connection,interview)
        candidate = connection.execute("SELECT candidate_id FROM Application WHERE application_id=?", (interview["application_id"],)).fetchone()[0]
        skills = {row[0]:row[1] for row in connection.execute("SELECT skill_key,level FROM CandidateSkill WHERE candidate_id=? AND status='active'", (candidate,))}
        draft = index%10==8 or (len(completed)>=4 and index==len(completed)-2)
        partial = not draft and (index%10==9 or (len(completed)>=4 and index==len(completed)-1))
        for reviewer_index,reviewer in enumerate(reviewers):
            identity = create_scorecard(connection,interview["interview_id"],reviewer,**metadata(reviewer,"STRUCTURED_EVALUATION_OPENED"))
            if index==0 and reviewer_index==0:
                rejected("duplicate_scorecard",lambda:create_scorecard(connection,interview["interview_id"],reviewer,**metadata(reviewer,"DUPLICATE_EXAMPLE")),"DUPLICATE_SCORECARD")
            if draft:
                continue
            omitted = next(row["skill_requirement_id"] for row in criteria if row["is_required"])
            for criterion in criteria:
                if partial and reviewer_index==len(reviewers)-1 and criterion["skill_requirement_id"]==omitted:
                    continue
                level = skills.get(criterion["criterion_key"],0)
                target = criterion["min_proficiency"]
                base = min(4,max(0,3+level-target))
                material = f"{config.seed}|{interview['interview_id']}|{reviewer}|{criterion['skill_requirement_id']}".encode()
                adjustment = -1 if int.from_bytes(hashlib.sha256(material).digest()[:4],"big")%11==0 else 0
                value = max(0,base+adjustment)
                evidence = f"Synthetic rubric observation: stored level={level}; role minimum={target}; observation adjustment={adjustment}."
                set_scorecard_item(connection,identity,criterion["skill_requirement_id"],value,evidence,**metadata(reviewer,"CRITERION_EVIDENCE_RECORDED"))
            if partial and reviewer_index==len(reviewers)-1:
                rejected("incomplete_submission",lambda:submit_scorecard(connection,identity,**metadata(reviewer,"INCOMPLETE_EXAMPLE")),"SCORECARD_INCOMPLETE")
            else:
                submit_scorecard(connection,identity,**metadata(reviewer,"EVALUATION_SUBMITTED"))
        if draft or partial:
            rejected("incomplete_review_gate",lambda:review_application(connection,interview["application_id"],**metadata("STAFF-000002","INCOMPLETE_REVIEW_EXAMPLE")),"REVIEW_GATE_INCOMPLETE")
            decisions["incomplete"] += 1
            continue
        decision = evaluate_application(connection,interview["application_id"])
        if decision["review_eligible"]:
            review_application(connection,interview["application_id"],**metadata("STAFF-000002","COMPLETE_EVALUATION_REVIEWED"))
            decisions["offer_eligible" if decision["offer_eligible"] else "reviewed_below_offer_policy"] += 1
        else:
            reject_evaluated_application(connection,interview["application_id"],**metadata("STAFF-000002","EVALUATION_BELOW_REVIEW_POLICY"))
            decisions["evaluation_rejected"] += 1
    evaluation_seconds = perf_counter()-started
    offers_started = perf_counter()
    offer_calls = Counter()
    for app in connection.execute("SELECT * FROM Application WHERE status='reviewed' ORDER BY application_id").fetchall():
        # Earlier acceptances may have withdrawn sibling applications.
        if connection.execute("SELECT status FROM Application WHERE application_id=?", (app["application_id"],)).fetchone()[0]!="reviewed":
            offer_calls["resolved_by_other_hire"] += 1
            continue
        decision = evaluate_application(connection,app["application_id"])
        if not decision["offer_eligible"]:
            continue
        manager = connection.execute("SELECT h.staff_id FROM Requisition r JOIN HiringManager h USING(hiring_manager_id) WHERE requisition_id=?", (app["requisition_id"],)).fetchone()[0]
        band = approved_band(connection,app["requisition_id"],clock)
        if not offer_calls["created"]:
            rejected("above_band_offer",lambda:create_offer(connection,app["application_id"],amount_minor=band["band_max_minor"]+1,**metadata(manager,"ABOVE_BAND_EXAMPLE")),"OFFER_OUTSIDE_BAND")
        identity = create_offer(connection,app["application_id"],**metadata(manager,"EVALUATION_DERIVED_OFFER"))
        offer_calls["created"] += 1
        submit_offer(connection,identity,"STAFF-000002",**metadata(manager,"INDEPENDENT_APPROVAL_REQUESTED"))
        offer = connection.execute("SELECT * FROM Offer WHERE offer_id=?", (identity,)).fetchone()
        approve = offer["amount_minor"]<=approval_limit(band)
        decide_offer(connection,identity,approve,**metadata("STAFF-000002","WITHIN_BUDGET_APPROVED" if approve else "BUDGET_LIMIT_REJECTED"))
        offer_calls["approved" if approve else "rejected"] += 1
        if approve:
            send_offer(connection,identity,**metadata(manager,"LOCAL_OFFER_PRESENTED"))
            accept_offer(connection,identity,**metadata("STAFF-000002","SYNTHETIC_CANDIDATE_ACCEPTED"))
            offer_calls["accepted"] += 1
    offer_seconds = perf_counter()-offers_started
    return {"policy_version":1,"additional_completed_interviews":additional,"evaluated_interviews":len(completed),
        "evaluation_decisions":dict(sorted(decisions.items())),"offer_operations":dict(sorted(offer_calls.items())),
        "rejected_examples":rejections,"statistics":evaluation_statistics(connection)}, {
        "evaluation_seconds":evaluation_seconds,"offer_seconds":offer_seconds}
