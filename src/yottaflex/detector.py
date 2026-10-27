"""Label-blind detection from canonical facts and typed business observations."""

from collections import Counter
import hashlib
import json

from .anomaly_rules import RULES
from .canonical import stable_json
from .evaluation import applicable_criteria, evaluate_application
from .observations import reference, projected, load_document, empty_document
from .workflow import DomainError


def _finding(rule, entity_type, identity, related, observed, invariant, explanation, when):
    key = {"rule_id":rule,"affected_entity_type":entity_type,"affected_entity_id":identity,"related_entity_ids":related}
    return key | {"finding_id":"FIND-"+hashlib.sha256(stable_json(key).encode()).hexdigest()[:24],
        "issue_type":RULES[rule],"observed_values":observed,"expected_invariant":invariant,
        "explanation":explanation,"evidence_timestamps":[when],"severity":"high"}


def detect_records(connection, as_of):
    """Same engine for every valid input. No scenario IDs, labels or filenames."""
    findings = []
    for app in connection.execute("SELECT * FROM Application WHERE status IN ('reviewed','offer','hired') ORDER BY application_id"):
        try:
            decision = evaluate_application(connection,app["application_id"],when=as_of)
            valid = decision["review_eligible"]
            reason = "review policy threshold or agreement failed" if not valid else ""
        except DomainError as error:
            valid,reason = False,str(error)
        if not valid:
            states = [dict(row) for row in connection.execute("""SELECT i.interview_id,i.status AS interview_status,
                p.staff_id,s.scorecard_id,s.status AS scorecard_status FROM Interview i
                LEFT JOIN InterviewParticipant p ON p.interview_id=i.interview_id AND p.assignment_role='reviewer'
                LEFT JOIN Scorecard s ON s.interview_id=i.interview_id AND s.reviewer_staff_id=p.staff_id
                WHERE i.application_id=? AND i.status<>'cancelled' ORDER BY i.interview_id,p.staff_id""", (app["application_id"],))]
            findings.append(_finding("R01","Application",app["application_id"],
                {"candidate_id":app["candidate_id"],"requisition_id":app["requisition_id"]},
                {"stage":app["status"],"evaluation_states":states,"decision_failure":reason},
                "Review-dependent stages require every completed, submitted, applicable evaluation and review policy.",
                "Observed advancement is unsupported by required review evidence.",as_of))
    for row in connection.execute("""SELECT i.interview_id AS first_id,j.interview_id AS second_id,p.staff_id,
        i.start_at AS first_start,i.end_at AS first_end,i.status AS first_status,
        j.start_at AS second_start,j.end_at AS second_end,j.status AS second_status
        FROM InterviewParticipant p JOIN Interview i ON i.interview_id=p.interview_id
        JOIN InterviewParticipant q ON q.staff_id=p.staff_id AND p.interview_id<q.interview_id
        JOIN Interview j ON j.interview_id=q.interview_id
        WHERE i.status IN ('scheduled','completed','no_show') AND j.status IN ('scheduled','completed','no_show')
        AND i.start_at<j.end_at AND j.start_at<i.end_at ORDER BY i.interview_id,j.interview_id,p.staff_id"""):
        findings.append(_finding("R02","Interview",row["first_id"],
            {"interview_ids":[row["first_id"],row["second_id"]],"staff_id":row["staff_id"]},dict(row),
            "Capacity-occupying intervals for one interviewer must not overlap; adjacent intervals are valid.",
            "Both assigned interview intervals overlap under the half-open rule.",as_of))
    for offer in connection.execute("SELECT * FROM Offer ORDER BY offer_id"):
        band = connection.execute("SELECT * FROM RequisitionEvent WHERE event_id=?", (offer["approved_requisition_event_id"],)).fetchone()
        if band is None or band["new_status"]!="approved" or band["requisition_id"]!=offer["requisition_id"] or band["currency"]!=offer["currency"] or band["occurred_at"]>offer["valid_from"]:
            raise ValueError("Offer lacks applicable historical approved compensation evidence")
        if offer["amount_minor"]>band["band_max_minor"]:
            findings.append(_finding("R03","Offer",offer["offer_id"],
                {"application_id":offer["application_id"],"requisition_id":offer["requisition_id"],"band_event_id":band["event_id"]},
                {"amount_minor":offer["amount_minor"],"approved_max_minor":band["band_max_minor"],"currency":offer["currency"],
                 "excess_minor":offer["amount_minor"]-band["band_max_minor"]},
                "Observed offer amount must not exceed its historically approved same-currency maximum.",
                "Observed amount exceeds the linked approved band.",as_of))
    for row in connection.execute("""SELECT i.interview_id,i.start_at,i.end_at,a.application_id,a.status AS application_status,
        a.updated_at,c.candidate_id,c.status AS candidate_status,c.withdrawn_at FROM Interview i
        JOIN Application a USING(application_id) JOIN Candidate c USING(candidate_id)
        WHERE i.status='scheduled' ORDER BY i.interview_id"""):
        effective = []
        if row["application_status"]=="withdrawn" and row["updated_at"]<=as_of:
            effective.append({"scope":"application","withdrawn_at":row["updated_at"]})
        if row["candidate_status"]=="withdrawn" and row["withdrawn_at"]<=as_of:
            effective.append({"scope":"candidate","withdrawn_at":row["withdrawn_at"]})
        if effective:
            findings.append(_finding("R04","Interview",row["interview_id"],
                {"application_id":row["application_id"],"candidate_id":row["candidate_id"]},
                {"status":"scheduled","withdrawals":effective,"start_at":row["start_at"],"end_at":row["end_at"]},
                "No scheduled reservation may remain active after effective candidate/application withdrawal.",
                "Scheduled booking persists after a withdrawal effective before this observation.",as_of))
    criteria_cache = {}
    for item in connection.execute("""SELECT s.scorecard_id,s.rubric_version,i.interview_id,i.requisition_id,
        x.skill_requirement_id,r.requisition_id AS criterion_requisition,r.rubric_version AS criterion_version,
        r.valid_from,r.valid_to FROM ScorecardItem x JOIN Scorecard s USING(scorecard_id)
        JOIN Interview i USING(interview_id) JOIN SkillRequirement r USING(skill_requirement_id)
        ORDER BY s.scorecard_id,x.skill_requirement_id"""):
        if item["interview_id"] not in criteria_cache:
            interview = connection.execute("SELECT * FROM Interview WHERE interview_id=?", (item["interview_id"],)).fetchone()
            criteria_cache[item["interview_id"]] = {row["skill_requirement_id"]:row["rubric_version"] for row in applicable_criteria(connection,interview)}
        applicable = criteria_cache[item["interview_id"]]
        if item["skill_requirement_id"] not in applicable or applicable.get(item["skill_requirement_id"])!=item["rubric_version"]:
            findings.append(_finding("R05","Scorecard",item["scorecard_id"],
                {"criterion_id":item["skill_requirement_id"],"interview_id":item["interview_id"],"requisition_id":item["requisition_id"]},dict(item),
                "Each rubric item must be from this interview's applicable requisition and effective version.",
                "Existing criterion reference is semantically irrelevant to this scorecard.",as_of))
    return sorted(findings,key=lambda row:row["finding_id"])


def detect(database, document=None):
    with reference(database) as source:
        document = empty_document(source) if document is None else document
        with projected(source,document) as (view,structure):
            findings = detect_records(view,document["as_of"])
    counts = Counter(row["rule_id"] for row in findings)
    return {"structure":structure,"semantic_valid":not findings,"findings":findings,
        "counts_by_rule":{rule:counts[rule] for rule in RULES}}


def main():
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database",type=Path,required=True)
    parser.add_argument("--observations",type=Path)
    args = parser.parse_args()
    result = detect(args.database,load_document(args.observations) if args.observations else None)
    print(json.dumps(result,sort_keys=True,indent=2))
    # Findings are observations, not a crashed structural check; report them explicitly.
    return 0


if __name__=="__main__":
    raise SystemExit(main())
