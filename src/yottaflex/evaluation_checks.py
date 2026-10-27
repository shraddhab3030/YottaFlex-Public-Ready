"""Independent persisted-source score, approval and lifecycle reconciliation."""

from collections import Counter
import json

from .ids import valid_numbered_id
from .workflow_checks import validate_workflow


def _histories(connection, table, key, edges, rows):
    errors = Counter()
    for projection in rows:
        events = list(connection.execute(f'SELECT * FROM "{table}Event" WHERE "{key}"=? ORDER BY sequence', (projection[key],)))
        if not events:
            errors["missing_history"] += 1
            continue
        previous,when,state = None,-1,None
        for index,event in enumerate(events,1):
            snapshot = json.loads(event["snapshot_json"])
            before,after = snapshot.get("before"),snapshot.get("after")
            errors["history_sequence"] += int(event["sequence"]!=index)
            errors["history_continuity"] += int(event["previous_status"]!=state)
            errors["history_edges"] += int((event["previous_status"],event["new_status"],event["event_type"]) not in edges)
            errors["history_time"] += int(event["occurred_at"]<when or event["recorded_at"]<event["occurred_at"])
            if not isinstance(before,dict) or not isinstance(after,dict):
                errors["history_snapshot_shape"] += 1
                continue
            errors["history_snapshot_states"] += int(before.get("status")!=state or after.get("status")!=event["new_status"])
            if previous is not None:
                errors["history_full_snapshots"] += int(before!=previous)
            actor = connection.execute("SELECT * FROM Staff WHERE staff_id=?", (event["actor_staff_id"],)).fetchone()
            errors["history_actor_time"] += int(actor["valid_from"]>event["occurred_at"] or (actor["valid_to"] is not None and actor["valid_to"]<=event["occurred_at"]))
            if table=="Scorecard":
                errors["scorecard_event_author"] += int(event["actor_staff_id"]!=projection["reviewer_staff_id"])
                if event["new_status"]=="submitted":
                    errors["submission_event_time"] += int(after.get("submitted_at")!=event["occurred_at"])
            previous,when,state = after,event["occurred_at"],event["new_status"]
        current = dict(projection)
        if table=="Scorecard":
            current["items"] = [dict(row) for row in connection.execute("SELECT * FROM ScorecardItem WHERE scorecard_id=? ORDER BY skill_requirement_id", (projection[key],))]
        errors["history_projection"] += int(previous!=current or state!=projection["status"])
    return errors


def validate_evaluations(connection, config, interview_target):
    base = validate_workflow(connection,config,interview_target,phase="evaluations")
    checks = list(base["checks"])
    errors = Counter()
    def add(name,value):
        checks.append({"check":name,"violations":int(value)})
    def scalar(sql):
        return connection.execute(sql).fetchone()[0]
    cards,calculated = {},{}
    for score in connection.execute("SELECT * FROM Scorecard ORDER BY scorecard_id"):
        identity = score["scorecard_id"]
        cards[identity] = score
        interview = connection.execute("SELECT * FROM Interview WHERE interview_id=?", (score["interview_id"],)).fetchone()
        reviewer = connection.execute("SELECT * FROM InterviewParticipant WHERE interview_id=? AND staff_id=? AND assignment_role='reviewer'", (score["interview_id"],score["reviewer_staff_id"])).fetchone()
        errors["scorecard_identity_reviewer"] += int(identity!=f"SCORE-{score['interview_id']}-{score['reviewer_staff_id']}" or reviewer is None)
        person = connection.execute("SELECT * FROM Staff WHERE staff_id=?", (score["reviewer_staff_id"],)).fetchone()
        errors["reviewer_role_effectivity"] += int(person["role"] not in ("interviewer","manager") or person["valid_from"]>interview["start_at"] or
            (person["valid_to"] is not None and person["valid_to"]<interview["end_at"]))
        completed = connection.execute("SELECT MAX(occurred_at) FROM InterviewEvent WHERE interview_id=? AND new_status='completed'", (score["interview_id"],)).fetchone()[0]
        errors["scorecard_interview_chronology"] += int(interview["status"]!="completed" or completed is None or score["created_at"]<max(interview["end_at"],completed or 0))
        criteria = list(connection.execute("""SELECT * FROM SkillRequirement WHERE requisition_id=? AND status='active'
            AND valid_from<=? AND (valid_to IS NULL OR valid_to>=?) ORDER BY rubric_version,skill_requirement_id""",
            (interview["requisition_id"],interview["start_at"],interview["end_at"])))
        version = max((row["rubric_version"] for row in criteria),default=0)
        criteria = {row["skill_requirement_id"]:row for row in criteria if row["rubric_version"]==version}
        items = list(connection.execute("SELECT * FROM ScorecardItem WHERE scorecard_id=? ORDER BY skill_requirement_id", (identity,)))
        coverage = {row["skill_requirement_id"] for row in items}==set(criteria) and bool(criteria)
        errors["scorecard_criteria_version_coverage"] += int(not coverage or score["rubric_version"]!=version or sum(row["weight_basis_points"] for row in criteria.values())!=10000)
        weighted,total_weight,required = 0,0,[]
        complete = coverage
        for item in items:
            criterion = criteria.get(item["skill_requirement_id"])
            if criterion is None:
                errors["irrelevant_criterion"] += 1
                complete = False
                continue
            errors["criterion_weight_snapshot"] += int(item["weight_basis_points"]!=criterion["weight_basis_points"])
            scored = item["status"]=="scored" and type(item["score_value"]) is int and 0<=item["score_value"]<=4 and bool(item["evidence"] and item["evidence"].strip())
            complete &= scored
            if scored:
                weighted += item["score_value"]*criterion["weight_basis_points"]
                total_weight += criterion["weight_basis_points"]
                if criterion["is_required"]:
                    required.append(item["score_value"])
        if score["status"]=="submitted":
            total = (weighted*1000+5000)//10000
            valid = complete and total_weight==10000 and bool(required)
            errors["submitted_rubric_completion"] += int(not valid)
            errors["independent_score_arithmetic"] += int(score["total_score_milli"]!=total)
            errors["submission_chronology"] += int(score["submitted_at"]<score["created_at"] or score["submitted_at"]<(completed or 0))
            if valid:
                calculated[identity] = (total,min(required))
        else:
            errors["editable_scorecard_legitimacy"] += int(score["total_score_milli"] is not None or score["submitted_at"] is not None)
    score_edges = {(None,"draft","created"),("draft","incomplete","revised"),("incomplete","incomplete","revised"),
                   ("draft","submitted","status_changed"),("incomplete","submitted","status_changed")}
    errors.update(_histories(connection,"Scorecard","scorecard_id",score_edges,cards.values()))

    def decision(application_id):
        interviews = list(connection.execute("SELECT * FROM Interview WHERE application_id=? AND status<>'cancelled' ORDER BY interview_id", (application_id,)))
        if not interviews or any(i["status"]!="completed" for i in interviews):
            return None
        values,minimums,ids,times = [],[],[],[]
        for interview in interviews:
            reviewers = list(connection.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? AND assignment_role='reviewer' ORDER BY staff_id", (interview["interview_id"],)))
            if not reviewers:
                return None
            for reviewer in reviewers:
                identity = f"SCORE-{interview['interview_id']}-{reviewer[0]}"
                if identity not in calculated:
                    return None
                values.append(calculated[identity][0]); minimums.append(calculated[identity][1]); ids.append(identity); times.append(cards[identity]["submitted_at"])
        aggregate = (2*sum(values)+len(values))//(2*len(values))
        reviewed = aggregate>=2500 and min(minimums)>=2 and max(values)-min(values)<=1000
        return {"policy_version":1,"scorecard_ids":ids,"reviewer_totals_milli":values,"aggregate_milli":aggregate,
            "required_minimum":min(minimums),"reviewer_spread_milli":max(values)-min(values),
            "review_eligible":reviewed,"offer_eligible":reviewed and aggregate>=3000 and min(minimums)>=3,"latest_evidence_at":max(times)}
    for event in connection.execute("SELECT * FROM ApplicationEvent WHERE new_status='reviewed' OR (event_type='decision_recorded' AND previous_status IN ('interviewing','reviewed')) ORDER BY event_id"):
        derived = decision(event["application_id"])
        recorded = json.loads(event["snapshot_json"]).get("decision")
        errors["review_decision_reconciliation"] += int(derived is None or derived!=recorded)
        if derived is not None:
            errors["review_decision_chronology"] += int(event["occurred_at"]<derived["latest_evidence_at"])
            if event["new_status"]=="reviewed":
                errors["review_threshold_enforcement"] += int(not derived["review_eligible"])
            elif event["previous_status"]=="interviewing":
                errors["evaluation_rejection_policy"] += int(derived["review_eligible"])
            else:
                errors["evaluation_rejection_policy"] += int(derived["offer_eligible"])

    offers = list(connection.execute("SELECT * FROM Offer ORDER BY offer_id"))
    offer_edges = {(None,"draft","created"),("draft","pending_approval","status_changed"),
        ("pending_approval","approved","decision_recorded"),("pending_approval","rejected","decision_recorded"),
        ("approved","sent","status_changed"),("sent","accepted","status_changed")}
    errors.update(_histories(connection,"Offer","offer_id",offer_edges,offers))
    approvals = list(connection.execute("SELECT * FROM Approval WHERE offer_id IS NOT NULL ORDER BY approval_id"))
    approval_edges = {(None,"pending","created"),("pending","approved","decision_recorded"),("pending","rejected","decision_recorded")}
    errors.update(_histories(connection,"Approval","approval_id",approval_edges,approvals))
    for offer in offers:
        app = connection.execute("SELECT * FROM Application WHERE application_id=?", (offer["application_id"],)).fetchone()
        band = connection.execute("SELECT * FROM RequisitionEvent WHERE event_id=?", (offer["approved_requisition_event_id"],)).fetchone()
        derived = decision(offer["application_id"])
        errors["offer_evaluation_gate"] += int(derived is None or not derived["offer_eligible"])
        candidate = connection.execute("SELECT status FROM Candidate WHERE candidate_id=?", (app["candidate_id"],)).fetchone()[0]
        errors["offer_candidate_lifecycle"] += int(candidate!="active")
        errors["offer_band_snapshot"] += int(band["new_status"]!="approved" or band["requisition_id"]!=offer["requisition_id"] or band["occurred_at"]>offer["valid_from"])
        errors["offer_band_currency_amount"] += int(offer["currency"]!=band["currency"] or not band["band_min_minor"]<=offer["amount_minor"]<=band["band_max_minor"])
        first = connection.execute("SELECT * FROM OfferEvent WHERE offer_id=? AND sequence=1", (offer["offer_id"],)).fetchone()
        if first is None:
            errors["offer_creation_audit"] += 1
            continue
        review = connection.execute("SELECT 1 FROM ApplicationEvent WHERE application_id=? AND new_status='reviewed' AND occurred_at<=?", (app["application_id"],offer["valid_from"])).fetchone()
        errors["offer_creation_audit"] += int(review is None or first["occurred_at"]!=offer["valid_from"])
        if derived is not None:
            errors["offer_creation_decision"] += int(json.loads(first["snapshot_json"]).get("decision")!=derived)
        manager = connection.execute("SELECT h.staff_id FROM Requisition r JOIN HiringManager h USING(hiring_manager_id) WHERE requisition_id=?", (offer["requisition_id"],)).fetchone()[0]
        for event in connection.execute("SELECT * FROM OfferEvent WHERE offer_id=? ORDER BY sequence", (offer["offer_id"],)):
            actor = connection.execute("SELECT role FROM Staff WHERE staff_id=?", (event["actor_staff_id"],)).fetchone()[0]
            errors["offer_actor_authority"] += int(actor not in ("hr","administrator") and event["actor_staff_id"]!=manager)
        related = [a for a in approvals if a["offer_id"]==offer["offer_id"]]
        if offer["status"]=="draft":
            errors["offer_approval_state"] += len(related)
        elif len(related)!=1:
            errors["offer_approval_state"] += 1
        else:
            approval = related[0]
            wanted = "pending" if offer["status"]=="pending_approval" else "rejected" if offer["status"]=="rejected" else "approved"
            errors["offer_approval_state"] += int(approval["status"]!=wanted or approval["requisition_id"] is not None)
            request = connection.execute("SELECT * FROM ApprovalEvent WHERE approval_id=? AND sequence=1", (approval["approval_id"],)).fetchone()
            approver = connection.execute("SELECT * FROM Staff WHERE staff_id=?", (approval["approver_staff_id"],)).fetchone()
            errors["approval_authority_separation"] += int(approver["role"] not in ("hr","administrator") or request is None or approval["approver_staff_id"] in (first["actor_staff_id"],request["actor_staff_id"] if request else None))
            errors["approval_request_chronology"] += int(approval["requested_at"]<offer["valid_from"] or request is None or request["occurred_at"]!=approval["requested_at"])
            submitted = connection.execute("SELECT * FROM OfferEvent WHERE offer_id=? AND new_status='pending_approval'", (offer["offer_id"],)).fetchone()
            errors["approval_request_link"] += int(request is None or submitted is None or request["occurred_at"]!=submitted["occurred_at"] or request["actor_staff_id"]!=submitted["actor_staff_id"])
            if approval["status"]!="pending":
                limit = band["band_min_minor"]+(band["band_max_minor"]-band["band_min_minor"])*7//10
                errors["approval_budget_decision"] += int((approval["status"]=="approved")!=(offer["amount_minor"]<=limit))
                event = connection.execute("SELECT * FROM ApprovalEvent WHERE approval_id=? ORDER BY sequence DESC LIMIT 1", (approval["approval_id"],)).fetchone()
                errors["approval_decision_actor_time"] += int(event is None or event["actor_staff_id"]!=approval["approver_staff_id"] or event["occurred_at"]!=approval["decided_at"])
                errors["approval_effectivity"] += int(approval["valid_from"]>approval["decided_at"] or (approval["valid_to"] is not None and approval["valid_to"]<=approval["decided_at"]))
                causal = connection.execute("SELECT MIN(occurred_at) FROM OfferEvent WHERE offer_id=? AND new_status=?", (offer["offer_id"],approval["status"])).fetchone()[0]
                errors["approval_precedes_offer_decision"] += int(causal is None or causal!=approval["decided_at"])
        wanted_app = "hired" if offer["status"]=="accepted" else "rejected" if offer["status"]=="rejected" else "offer"
        errors["offer_application_projection"] += int(app["status"]!=wanted_app)
    for name,value in sorted(errors.items()):
        add(name,value)
    add("incompatible_candidate_offers",scalar("""SELECT COUNT(*) FROM (SELECT a.candidate_id FROM Offer o JOIN Application a USING(application_id)
        WHERE o.is_final=1 AND o.status IN ('draft','pending_approval','approved','sent','accepted') GROUP BY a.candidate_id HAVING COUNT(*)>1)"""))
    add("hired_candidate_scheduling",scalar("""SELECT COUNT(*) FROM Interview i JOIN Application a USING(application_id)
        WHERE i.status='scheduled' AND EXISTS (SELECT 1 FROM Application h WHERE h.candidate_id=a.candidate_id AND h.status='hired')"""))
    add("advanced_stage_support",scalar("""SELECT COUNT(*) FROM Application a WHERE
        (a.status='hired' AND NOT EXISTS (SELECT 1 FROM Offer o WHERE o.application_id=a.application_id AND o.status='accepted')) OR
        (a.status='offer' AND NOT EXISTS (SELECT 1 FROM Offer o WHERE o.application_id=a.application_id)) OR
        (a.status IN ('reviewed','offer','hired') AND NOT EXISTS (SELECT 1 FROM ApplicationEvent e WHERE e.application_id=a.application_id AND e.new_status='reviewed'))"""))
    add("advanced_application_actor",scalar("""SELECT COUNT(*) FROM ApplicationEvent e JOIN Application a USING(application_id)
        JOIN Requisition r USING(requisition_id) JOIN HiringManager h USING(hiring_manager_id)
        JOIN Staff s ON s.staff_id=e.actor_staff_id WHERE e.new_status IN ('reviewed','offer','hired')
        AND (NOT (s.role IN ('hr','administrator') OR (s.role='manager' AND s.staff_id=h.staff_id))
             OR (e.new_status='hired' AND s.role NOT IN ('hr','administrator')))"""))
    for table,kind in (("ScorecardEvent","scorecard_event"),("OfferEvent","offer_event")):
        add(table+"_ids",sum(not valid_numbered_id(kind,row[0]) for row in connection.execute(f'SELECT event_id FROM "{table}"')))
    add("Offer_ids",sum(not valid_numbered_id("offer",row[0]) for row in offers))
    leakage = sum(scalar(f'''SELECT COUNT(*) FROM "{table}" e,json_tree(e.snapshot_json) j
        WHERE j.key IN ('issue_type','ground_truth','expected_decision','anomaly_label')''') for table in ("ScorecardEvent","OfferEvent","ApprovalEvent"))
    add("evaluation_truth_leakage",leakage)
    return {"passed":all(item["violations"]==0 for item in checks),"checks":checks,"slot_error_codes":base["slot_error_codes"]}


def main():
    import argparse
    from contextlib import closing
    from pathlib import Path
    from .db import connect,initialize
    from .generation_config import GenerationConfig
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database",type=Path,required=True)
    parser.add_argument("--profile",choices=("starter","full"),required=True)
    parser.add_argument("--seed",type=int,default=20261022)
    parser.add_argument("--interviews",type=int)
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error("Existing database required")
    target = args.interviews if args.interviews is not None else (2000 if args.profile=="full" else 40)
    with closing(connect(args.database)) as connection:
        initialize(connection)
        result = validate_evaluations(connection,GenerationConfig(args.profile,args.seed),target)
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0 if result["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
