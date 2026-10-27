"""Validate/summarize Phase 03 master and initial-application data only."""

from collections import Counter
from datetime import datetime, timezone
import json

from .canonical import primary_keys, table_names
from .generation_config import APPROVAL_CAP_MINOR, DAY, ROLES, SENIORITY, SKILLS
from .ids import application_id, valid_numbered_id
from .matching import load_matching_inputs, skill_fit


DEFERRED_TABLES = ("InterviewPanel", "PanelMember", "Availability", "Interview",
    "InterviewParticipant", "Scorecard", "ScorecardItem", "Offer", "InterviewEvent",
    "ScorecardEvent", "OfferEvent")
IDENTITIES = {"Staff": ("staff", "staff_id"), "HiringManager": ("manager", "hiring_manager_id"),
    "Candidate": ("candidate", "candidate_id"), "Requisition": ("requisition", "requisition_id"),
    "SkillRequirement": ("skill", "skill_requirement_id"), "Approval": ("approval", "approval_id"),
    "RequisitionEvent": ("requisition_event", "event_id"), "CandidateEvent": ("candidate_event", "event_id"),
    "ApprovalEvent": ("approval_event", "event_id"), "ApplicationEvent": ("application_event", "event_id")}


def count_tables(connection):
    return {name: connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            for name in table_names(connection)}


def role_details(title):
    seniority, remainder = title.split(" ", 1)
    role = next((role for role in ROLES if role[1] == remainder), None)
    minimum = dict(SENIORITY).get(seniority)
    if role is None or minimum is None:
        raise ValueError("Unknown synthetic role title")
    return role, seniority, minimum


def _history_violations(connection, config):
    errors = 0
    for req in connection.execute("SELECT r.*, h.staff_id AS manager_staff FROM Requisition r JOIN HiringManager h USING(hiring_manager_id) ORDER BY requisition_id"):
        events = list(connection.execute("SELECT * FROM RequisitionEvent WHERE requisition_id=? ORDER BY sequence", (req["requisition_id"],)))
        approvals = list(connection.execute("SELECT * FROM Approval WHERE requisition_id=? ORDER BY approval_id", (req["requisition_id"],)))
        expected = [(None, "draft", "created"), ("draft", "pending_approval", "status_changed"),
                    ("pending_approval", "approved", "decision_recorded"), ("approved", "open", "status_changed")]
        errors += int(len(events) != 4 or len(approvals) != 1)
        if len(events) != 4 or len(approvals) != 1:
            continue
        approval = approvals[0]
        creation_snapshot = json.loads(events[0]["snapshot_json"])
        errors += int(creation_snapshot.get("generation") != config.as_dict())
        try:
            role, seniority, _ = role_details(req["title"])
            errors += int(creation_snapshot.get("role_category") != role[0] or creation_snapshot.get("seniority") != seniority)
        except ValueError:
            errors += 1
        for index, event in enumerate(events):
            errors += int((event["previous_status"], event["new_status"], event["event_type"]) != expected[index])
            errors += int(event["sequence"] != index+1 or event["occurred_at"] != req["valid_from"]+index*3600)
            expected_actor = approval["approver_staff_id"] if index == 2 else req["manager_staff"]
            errors += int(event["actor_staff_id"] != expected_actor)
        approved = events[2]
        errors += int((approved["band_min_minor"], approved["band_max_minor"], approved["currency"]) !=
                      (req["band_min_minor"], req["band_max_minor"], req["currency"]))
        errors += int(req["status"] != events[-1]["new_status"] or approval["requested_at"] != events[1]["occurred_at"]
                      or approval["decided_at"] != approved["occurred_at"] or approval["status"] != "approved")
        actor = connection.execute("SELECT role,status,valid_from FROM Staff WHERE staff_id=?", (approval["approver_staff_id"],)).fetchone()
        errors += int(actor is None or actor["role"] != "hr" or actor["status"] != "active"
                      or actor["valid_from"] > approval["decided_at"] or approval["approver_staff_id"] == req["manager_staff"])
        audit = list(connection.execute("SELECT * FROM ApprovalEvent WHERE approval_id=? ORDER BY sequence", (approval["approval_id"],)))
        errors += int(len(audit) != 2)
        if len(audit) == 2:
            for index, event in enumerate(audit):
                wanted = (None, "pending", "created") if index == 0 else ("pending", "approved", "decision_recorded")
                errors += int((event["previous_status"], event["new_status"], event["event_type"]) != wanted
                              or event["sequence"] != index+1)
                errors += int(event["occurred_at"] != (approval["requested_at"] if index == 0 else approval["decided_at"]))
                errors += int(event["actor_staff_id"] != (req["manager_staff"] if index == 0 else approval["approver_staff_id"]))
        errors += int(approval["reason_code"] != "SYNTHETIC_POLICY_APPROVED")
    return errors


def validate_generated(connection, config, *, phase="master"):
    """Return measured violation counts; never use anomaly labels or fake PASS."""
    if phase not in ("master","interviews","evaluations"):
        raise ValueError("Unknown validation phase")
    checks = []
    def add(name, violations):
        checks.append({"check": name, "violations": int(violations)})
    def scalar(sql, parameters=()):
        return connection.execute(sql, parameters).fetchone()[0]

    counts = count_tables(connection)
    r, c, a = config.scale.requisitions, config.scale.candidates, config.scale.applications
    expected = {"Requisition": r, "Candidate": c, "Application": a, "HiringManager": config.managers,
        "Staff": config.managers+4, "SkillRequirement": 4*r, "Approval": r,
        "RequisitionEvent": 4*r, "ApprovalEvent": 2*r, "CandidateEvent": c, "ApplicationEvent": a}
    if phase != "master":
        for name in ("Staff","CandidateEvent","ApplicationEvent"):
            expected.pop(name)
    if phase == "evaluations":
        expected.pop("Approval")
        expected.pop("ApprovalEvent")
    add("exact_populated_counts", sum(abs(counts[name]-count) for name, count in expected.items()))
    deferred = DEFERRED_TABLES if phase == "master" else (() if phase=="evaluations" else ("Scorecard","ScorecardItem","Offer","ScorecardEvent","OfferEvent"))
    add("deferred_tables_empty", sum(counts[name] for name in deferred))
    add("foreign_keys", len(list(connection.execute("PRAGMA foreign_key_check"))))
    add("sqlite_integrity", sum(row[0] != "ok" for row in connection.execute("PRAGMA integrity_check")))
    pk_errors = null_errors = time_errors = 0
    time_fields = {"valid_from", "valid_to", "created_at", "withdrawn_at", "applied_at", "updated_at",
                   "requested_at", "decided_at", "occurred_at", "recorded_at", "start_at", "end_at", "assigned_at"}
    for table in counts:
        keys = ", ".join(f'"{key}"' for key in primary_keys(connection, table))
        pk_errors += scalar(f'SELECT COUNT(*) FROM (SELECT {keys} FROM "{table}" GROUP BY {keys} HAVING COUNT(*) > 1)')
        columns = list(connection.execute(f'PRAGMA table_info("{table}")'))
        required = [f'"{col["name"]}" IS NULL' for col in columns if col["notnull"]]
        null_errors += scalar(f'SELECT COUNT(*) FROM "{table}" WHERE ' + " OR ".join(required))
        for column in columns:
            if column["name"] in time_fields:
                name = column["name"]
                time_errors += scalar(f'SELECT COUNT(*) FROM "{table}" WHERE "{name}" IS NOT NULL AND ("{name}" < ? OR "{name}" > ?)',
                                      (config.logical_origin-DAY, config.logical_origin+200*DAY))
    add("primary_keys", pk_errors)
    add("required_fields", null_errors)
    add("logical_time_bounds", time_errors)
    id_errors = sum(not valid_numbered_id(kind, row[0]) for table, (kind, key) in IDENTITIES.items()
                    for row in connection.execute(f'SELECT "{key}" FROM "{table}" ORDER BY "{key}"'))
    id_errors += sum(row["application_id"] != application_id(row["candidate_id"], row["requisition_id"])
                     for row in connection.execute("SELECT * FROM Application ORDER BY application_id"))
    add("deterministic_identity_formats", id_errors)
    add("application_pair_uniqueness", scalar("SELECT COUNT(*) FROM (SELECT candidate_id,requisition_id FROM Application GROUP BY candidate_id,requisition_id HAVING COUNT(*)>1)"))
    app_states = scalar("SELECT COUNT(*) FROM Application WHERE status<>'applied' OR updated_at<>applied_at") if phase == "master" else scalar("SELECT COUNT(*) FROM Application WHERE status NOT IN ('applied','screening','interviewing','rejected','withdrawn'"+(",'reviewed','offer','hired'" if phase=="evaluations" else "")+")")
    candidate_states = scalar("SELECT COUNT(*) FROM Candidate WHERE status<>'active' OR withdrawn_at IS NOT NULL") if phase == "master" else scalar("SELECT COUNT(*) FROM Candidate WHERE status NOT IN ('active','withdrawn')")
    add("initial_lifecycle_states" if phase == "master" else "phase04_lifecycle_states", app_states+candidate_states
        + scalar("SELECT COUNT(*) FROM Requisition WHERE status<>'open'"))
    roles = "'manager','hr','system','administrator','it_operations'" + (",'interviewer'" if phase != "master" else "")
    add("active_staff_and_managers", scalar(f"SELECT COUNT(*) FROM Staff WHERE status<>'active' OR role NOT IN ({roles})")
        + scalar("SELECT COUNT(*) FROM HiringManager h JOIN Staff s USING(staff_id) WHERE h.status<>'active' OR s.role<>'manager'"))
    add("application_chronology", scalar("""SELECT COUNT(*) FROM Application a JOIN Candidate c USING(candidate_id)
        JOIN Requisition r USING(requisition_id) LEFT JOIN RequisitionEvent e ON e.requisition_id=r.requisition_id AND e.sequence=4
        WHERE e.event_id IS NULL OR a.applied_at<c.created_at OR a.applied_at<e.occurred_at
        OR (r.valid_to IS NOT NULL AND a.applied_at>=r.valid_to)"""))
    add("approval_subjects", scalar("SELECT COUNT(*) FROM Approval WHERE "+("requisition_id IS NOT NULL AND (offer_id IS NOT NULL OR status<>'approved')" if phase=="evaluations" else "requisition_id IS NULL OR offer_id IS NOT NULL OR status<>'approved'")))
    add("requisition_approval_histories", _history_violations(connection, config))
    policy_errors = 0
    for req in connection.execute("SELECT * FROM Requisition ORDER BY requisition_id"):
        criteria = list(connection.execute("SELECT * FROM SkillRequirement WHERE requisition_id=? ORDER BY skill_requirement_id", (req["requisition_id"],)))
        try:
            role, _, minimum = role_details(req["title"])
        except ValueError:
            policy_errors += 1
            continue
        policy_errors += int(req["currency"] not in APPROVAL_CAP_MINOR or req["band_min_minor"] <= 0
                            or req["band_max_minor"] < req["band_min_minor"]
                            or req["band_max_minor"] > APPROVAL_CAP_MINOR.get(req["currency"], 0))
        policy_errors += int(len(criteria) != 4 or sum(item["weight_basis_points"] for item in criteria) != 10000)
        policy_errors += int({item["criterion_key"] for item in criteria} != {item[0] for item in role[3]})
        for item in criteria:
            expected_required = next((value[1] for value in role[3] if value[0] == item["criterion_key"]), None)
            policy_errors += int(item["status"] != "active" or not 1 <= item["weight_basis_points"] <= 10000
                                or item["is_required"] != expected_required
                                or item["min_proficiency"] != (minimum if item["is_required"] else max(1,minimum-1))
                                or item["valid_from"] != req["valid_from"]+60 or item["rubric_version"] != 1)
    add("requirement_weights_ranges_and_approval_bands", policy_errors)
    skills = list(connection.execute("SELECT DISTINCT skill_key FROM CandidateSkill ORDER BY skill_key"))
    add("candidate_skill_ranges", scalar("SELECT COUNT(*) FROM CandidateSkill WHERE level NOT BETWEEN 0 AND 4 OR status<>'active'")
        + scalar("SELECT COUNT(*) FROM Candidate WHERE experience_years NOT BETWEEN 0 AND 50")
        + sum(row[0] not in SKILLS for row in skills))
    add("candidate_skill_coverage", scalar("SELECT COUNT(*) FROM Candidate c WHERE NOT EXISTS (SELECT 1 FROM CandidateSkill s WHERE s.candidate_id=c.candidate_id)"))
    add("synthetic_contacts", scalar("SELECT COUNT(*) FROM Candidate WHERE contact_email IS NULL OR contact_email NOT LIKE '%@example.invalid'"))
    for table, subject, key, timestamp, status in [("CandidateEvent", "Candidate", "candidate_id", "created_at", "active"),
                                                  ("ApplicationEvent", "Application", "application_id", "applied_at", "applied")]:
        origin = "p.candidate_id"
        add(table+"_creation_history", scalar(f'''SELECT COUNT(*) FROM "{subject}" p WHERE NOT EXISTS
            (SELECT 1 FROM "{table}" e JOIN Staff s ON s.staff_id=e.actor_staff_id
             WHERE e."{key}"=p."{key}" AND e.sequence=1 AND e.previous_status IS NULL AND e.new_status=?
             AND e.event_type='created' AND e.occurred_at=p."{timestamp}" AND s.role='system'
             AND e.actor_candidate_id={origin})''', (status,)))
    add("candidate_experience_history", scalar("""SELECT COUNT(*) FROM Candidate c JOIN CandidateEvent e USING(candidate_id)
        WHERE e.sequence=1 AND json_extract(e.snapshot_json,'$.experience_years') IS NOT c.experience_years"""))
    snapshot_errors = 0
    for table in ("RequisitionEvent", "ApprovalEvent", "CandidateEvent", "ApplicationEvent"):
        snapshot_errors += scalar(f'''SELECT COUNT(*) FROM "{table}" WHERE
            json_extract(snapshot_json,'$.before.status') IS NOT previous_status OR
            json_extract(snapshot_json,'$.after.status') IS NOT new_status OR recorded_at<>occurred_at''')
        snapshot_errors += scalar(f'''SELECT COUNT(*) FROM "{table}" e, json_tree(e.snapshot_json) j
            WHERE j.key IN ('issue_type','ground_truth','expected_decision','anomaly_label')''')
        snapshot_errors += scalar(f'''SELECT COUNT(*) FROM "{table}" e JOIN Staff s ON s.staff_id=e.actor_staff_id
            WHERE s.valid_from>e.occurred_at OR (s.valid_to IS NOT NULL AND e.occurred_at>=s.valid_to)''')
    add("snapshot_states_times_actors_and_no_truth_labels", snapshot_errors)
    return {"passed": all(item["violations"] == 0 for item in checks), "checks": checks}


def _histogram(connection, sql):
    return {str(row[0]): row[1] for row in connection.execute(sql)}


def generation_summary(connection, config, validation):
    counts = count_tables(connection)
    role_counts, seniority_counts = Counter(), Counter()
    for row in connection.execute("SELECT title FROM Requisition ORDER BY requisition_id"):
        role, seniority, _ = role_details(row[0])
        role_counts[role[0]] += 1
        seniority_counts[seniority] += 1
    candidates, requirements = load_matching_inputs(connection)
    fits, missing, fit_sum = Counter({"excellent": 0, "borderline": 0, "weak": 0}), Counter(), 0
    for row in connection.execute("SELECT * FROM Application ORDER BY application_id"):
        fit = skill_fit(requirements[row["requisition_id"]], candidates[row["candidate_id"]])
        fits[fit.category] += 1
        missing[fit.missing_required] += 1
        fit_sum += fit.basis_points
    compensation = {row["currency"]: {"requisitions": row["n"], "min_lower_minor": row["low"], "max_upper_minor": row["high"],
                                    "mean_lower_minor": row["total_low"]//row["n"], "mean_upper_minor": row["total_high"]//row["n"]}
        for row in connection.execute("SELECT currency,COUNT(*) n,MIN(band_min_minor) low,MAX(band_max_minor) high,SUM(band_min_minor) total_low,SUM(band_max_minor) total_high FROM Requisition GROUP BY currency ORDER BY currency")}
    depth = {}
    for label, low, high in (("early", 0, 2), ("mid", 3, 6), ("experienced", 7, 50)):
        row = connection.execute("SELECT COUNT(DISTINCT c.candidate_id) candidates,COUNT(*) skills,COALESCE(SUM(s.level),0) levels FROM Candidate c JOIN CandidateSkill s USING(candidate_id) WHERE experience_years BETWEEN ? AND ?", (low, high)).fetchone()
        depth[label] = {"candidates": row["candidates"], "skills": row["skills"], "mean_level_milli": row["levels"]*1000//row["skills"] if row["skills"] else None}
    return {"scope": "phase03_master_and_initial_applications", "config": config.as_dict(),
        "logical_origin_utc": datetime.fromtimestamp(config.logical_origin, timezone.utc).isoformat(),
        "schema_version": connection.execute("PRAGMA user_version").fetchone()[0],
        "schema_sha256": connection.execute("SELECT source_sha256 FROM SchemaMetadata").fetchone()[0],
        "counts": counts, "populated_table_counts": {name: count for name,count in counts.items() if count},
        "approved_requisitions": connection.execute("SELECT COUNT(DISTINCT requisition_id) FROM Approval WHERE status='approved' AND offer_id IS NULL").fetchone()[0],
        "current_requisition_statuses": _histogram(connection,"SELECT status,COUNT(*) FROM Requisition GROUP BY status ORDER BY status"),
        "applications_per_requisition": _histogram(connection,"SELECT n,COUNT(*) FROM (SELECT r.requisition_id,COUNT(a.application_id) n FROM Requisition r LEFT JOIN Application a USING(requisition_id) GROUP BY r.requisition_id) GROUP BY n ORDER BY n"),
        "experience_years": _histogram(connection,"SELECT experience_years,COUNT(*) FROM Candidate GROUP BY experience_years ORDER BY experience_years"),
        "proficiency_levels": _histogram(connection,"SELECT level,COUNT(*) FROM CandidateSkill GROUP BY level ORDER BY level"),
        "experience_skill_depth": depth, "role_categories": dict(sorted(role_counts.items())),
        "seniority": dict(sorted(seniority_counts.items())), "compensation": compensation,
        "fit_categories": dict(fits), "missing_required_criteria": dict(sorted(missing.items())),
        "mean_application_fit_basis_points": fit_sum//counts["Application"] if counts["Application"] else None,
        "validation": validation, "unavailable_metrics": ["scheduling_conflicts", "review_completion", "offer_outcomes", "anomaly_detection"]}
