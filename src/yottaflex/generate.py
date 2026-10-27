"""Deterministic Phase 03 master/application generation; no downstream workflow."""

from contextlib import closing
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import random
import sqlite3
import tempfile
from time import perf_counter

from .canonical import dataset_digest, stable_json
from .db import connect, initialize
from .generation_checks import generation_summary, validate_generated
from .generation_config import (ANNUAL_BASE_MAJOR, APPROVAL_CAP_MINOR, DAY, DEFAULT_SEED,
                                GenerationConfig, ROLES, SENIORITY, SKILLS)
from .ids import application_id, numbered_id
from .matching import load_matching_inputs, skill_fit


SYSTEM = "STAFF-000001"
HR = "STAFF-000002"


@dataclass(frozen=True)
class GenerationResult:
    summary: dict
    canonical: dict
    elapsed_seconds: float  # Diagnostic only; never canonical data/summary.
    timings: dict | None = None


def domain_random(seed, domain):
    digest = hashlib.sha256(f"yottaflex:phase03:v1:{seed}:{domain}".encode()).digest()
    return random.Random(int.from_bytes(digest, "big"))


def _insert(connection, table, row):
    columns = ", ".join(row)
    marks = ", ".join("?" for _ in row)
    connection.execute(f'INSERT INTO "{table}" ({columns}) VALUES ({marks})', tuple(row.values()))


def _batch(connection, table, rows):
    if rows:
        columns = tuple(rows[0])
        marks = ", ".join("?" for _ in columns)
        connection.executemany(f'INSERT INTO "{table}" ({", ".join(columns)}) VALUES ({marks})',
                               (tuple(row[column] for column in columns) for row in rows))


def _event(event_id, subject_key, subject, sequence, previous, new, kind, actor, when, reason,
           *, candidate=None, details=None):
    snapshot = {"before": {"status": previous}, "after": {"status": new}}
    if details:
        snapshot.update(details)
    return dict(event_id=event_id, **{subject_key: subject}, sequence=sequence,
        event_type=kind, previous_status=previous, new_status=new, actor_staff_id=actor,
        actor_candidate_id=candidate, occurred_at=when, recorded_at=when,
        reason_code=reason, correlation_id=subject, snapshot_json=stable_json(snapshot))


def _staff_and_managers(connection, config):
    start = config.logical_origin-DAY
    for index, (role, name) in enumerate((("system", "Synthetic Generator"), ("hr", "Synthetic HR Partner"),
                                        ("it_operations", "Synthetic Operations"), ("administrator", "Synthetic Administrator")), 1):
        _insert(connection, "Staff", dict(staff_id=numbered_id("staff", index), display_name=name,
            role=role, status="active", valid_from=start, valid_to=None))
    for index in range(1, config.managers+1):
        staff = numbered_id("staff", index+4)
        _insert(connection, "Staff", dict(staff_id=staff, display_name=f"Synthetic Manager {index:06d}",
            role="manager", status="active", valid_from=start, valid_to=None))
        _insert(connection, "HiringManager", dict(hiring_manager_id=numbered_id("manager", index), staff_id=staff,
            department=ROLES[(index-1)%len(ROLES)][0], status="active", valid_from=start, valid_to=None))


def normalized_weights(raw):
    """Largest-remainder apportionment, with catalogue order breaking ties."""
    total = sum(raw)
    if not raw or any(type(value) is not int or value <= 0 for value in raw):
        raise ValueError("Weights need positive integer inputs")
    weights = [value*10000//total for value in raw]
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i]*10000%total), i))
    for index in order[:10000-sum(weights)]:
        weights[index] += 1
    return weights


def _approval_policy(connection, requisition_id, approver):
    """Generator-only synthetic policy evaluated from stored facts, not random labels."""
    req = connection.execute("SELECT * FROM Requisition WHERE requisition_id=?", (requisition_id,)).fetchone()
    criteria = list(connection.execute("SELECT * FROM SkillRequirement WHERE requisition_id=? ORDER BY skill_requirement_id", (requisition_id,)))
    actor = connection.execute("SELECT * FROM Staff WHERE staff_id=?", (approver,)).fetchone()
    manager = connection.execute("SELECT staff_id,status FROM HiringManager WHERE hiring_manager_id=?", (req["hiring_manager_id"],)).fetchone()
    checks = {"pending_request": req["status"] == "pending_approval", "active_manager": manager["status"] == "active",
        "independent_hr": actor["role"] == "hr" and actor["status"] == "active" and approver != manager["staff_id"],
        "valid_band": 0 < req["band_min_minor"] <= req["band_max_minor"] <= APPROVAL_CAP_MINOR.get(req["currency"], 0),
        "role_criteria": len(criteria) == 4 and any(item["is_required"] for item in criteria)
            and all(item["status"] == "active" and 0 <= item["min_proficiency"] <= 4 for item in criteria),
        "weights_reconcile": sum(item["weight_basis_points"] for item in criteria) == 10000}
    if not all(checks.values()):
        raise ValueError(f"Synthetic approval policy failed: {requisition_id}: {checks}")
    return checks


def _requisitions(connection, config):
    rng = domain_random(config.seed, "requisitions")
    for index in range(1, config.scale.requisitions+1):
        req = numbered_id("requisition", index)
        manager_index = (index-1)%config.managers+1
        manager, manager_staff = numbered_id("manager", manager_index), numbered_id("staff", manager_index+4)
        role = ROLES[(index-1)%len(ROLES)]
        seniority_index = ((index-1)//len(ROLES))%len(SENIORITY)
        seniority, minimum = SENIORITY[seniority_index]
        currency = "USD" if rng.randrange(5) == 0 else "INR"
        base = ANNUAL_BASE_MAJOR[currency][seniority_index]*role[2]//100
        lower_major = base + rng.randint(-base//10, base//10)
        upper_major = lower_major+base*30//100
        created = config.logical_origin+rng.randrange(90*DAY)
        _insert(connection, "Requisition", dict(requisition_id=req, hiring_manager_id=manager,
            title=f"{seniority} {role[1]}", status="draft", band_min_minor=lower_major*100,
            band_max_minor=upper_major*100, currency=currency, policy_version=1, valid_from=created, valid_to=None))
        _insert(connection, "RequisitionEvent", _event(numbered_id("requisition_event", (index-1)*4+1),
            "requisition_id", req, 1, None, "draft", "created", manager_staff, created, "SYNTHETIC_ROLE_CREATED",
            details={"generation": config.as_dict(), "role_category": role[0], "seniority": seniority}))
        weights = normalized_weights([criterion[2]*100+rng.randint(-300,300) for criterion in role[3]])
        for offset, ((skill, required, _), weight) in enumerate(zip(role[3], weights), 1):
            _insert(connection, "SkillRequirement", dict(skill_requirement_id=numbered_id("skill", (index-1)*4+offset),
                requisition_id=req, criterion_key=skill, description=f"Synthetic {seniority.lower()} {skill} evidence",
                is_required=required, weight_basis_points=weight, min_proficiency=minimum if required else max(1,minimum-1),
                rubric_version=1, status="active", valid_from=created+60, valid_to=None))
        requested, decided, opened = created+3600, created+7200, created+10800
        connection.execute("UPDATE Requisition SET status='pending_approval' WHERE requisition_id=?", (req,))
        _insert(connection, "RequisitionEvent", _event(numbered_id("requisition_event", (index-1)*4+2),
            "requisition_id", req, 2, "draft", "pending_approval", "status_changed", manager_staff, requested, "SYNTHETIC_APPROVAL_REQUESTED"))
        approval = numbered_id("approval", index)
        _insert(connection, "Approval", dict(approval_id=approval, requisition_id=req, offer_id=None,
            approver_staff_id=HR, status="pending", requested_at=requested, decided_at=None,
            reason_code="SYNTHETIC_APPROVAL_REQUESTED", valid_from=requested, valid_to=None))
        _insert(connection, "ApprovalEvent", _event(numbered_id("approval_event", (index-1)*2+1),
            "approval_id", approval, 1, None, "pending", "created", manager_staff, requested, "SYNTHETIC_APPROVAL_REQUESTED"))
        checks = _approval_policy(connection, req, HR)
        connection.execute("UPDATE Approval SET status='approved',decided_at=?,reason_code='SYNTHETIC_POLICY_APPROVED' WHERE approval_id=?", (decided,approval))
        _insert(connection, "ApprovalEvent", _event(numbered_id("approval_event", (index-1)*2+2),
            "approval_id", approval, 2, "pending", "approved", "decision_recorded", HR, decided,
            "SYNTHETIC_POLICY_APPROVED", details={"policy_checks": checks}))
        connection.execute("UPDATE Requisition SET status='approved' WHERE requisition_id=?", (req,))
        event = _event(numbered_id("requisition_event", (index-1)*4+3), "requisition_id", req, 3,
            "pending_approval", "approved", "decision_recorded", HR, decided, "SYNTHETIC_POLICY_APPROVED")
        event.update(band_min_minor=lower_major*100,band_max_minor=upper_major*100,currency=currency)
        _insert(connection, "RequisitionEvent", event)
        connection.execute("UPDATE Requisition SET status='open' WHERE requisition_id=?", (req,))
        _insert(connection, "RequisitionEvent", _event(numbered_id("requisition_event", index*4),
            "requisition_id", req, 4, "approved", "open", "status_changed", manager_staff, opened, "SYNTHETIC_ROLE_OPENED"))


def _candidates(connection, config):
    rng = domain_random(config.seed, "candidates")
    profiles, skills, events = [], [], []
    def flush():
        _batch(connection, "Candidate", profiles)
        _batch(connection, "CandidateSkill", skills)
        _batch(connection, "CandidateEvent", events)
        profiles.clear(); skills.clear(); events.clear()
    for index in range(1, config.scale.candidates+1):
        candidate = numbered_id("candidate", index)
        bucket = (index-1)%3
        low, high = ((0,2),(3,6),(7,15))[bucket]
        experience = rng.randint(low, high)
        base_level = bucket+1
        primary = {criterion[0] for criterion in ROLES[(index-1)%len(ROLES)][3]}
        created = config.logical_origin+rng.randrange(120*DAY)
        profiles.append(dict(candidate_id=candidate, display_name=f"Synthetic Candidate {index:06d}",
            experience_years=experience, contact_email=f"candidate{index:06d}@example.invalid",
            status="active", created_at=created, withdrawn_at=None))
        for skill in SKILLS:  # Catalogue order, never set/hash iteration order.
            if skill in primary:
                level = base_level+rng.randrange(2)
            elif rng.randrange(100) < 35:
                level = max(0,base_level-1+rng.randrange(2))
            else:
                continue
            skills.append(dict(candidate_id=candidate,skill_key=skill,level=level,status="active"))
        events.append(_event(numbered_id("candidate_event",index), "candidate_id",candidate,1,None,"active",
            "created",SYSTEM,created,"SYNTHETIC_PROFILE_CREATED",candidate=candidate,details={"experience_years":experience}))
        if len(profiles) == 256:
            flush()
    flush()


def _applications(connection, config):
    rng = domain_random(config.seed, "applications")
    candidates, requirements = load_matching_inputs(connection)
    candidate_ids = sorted(candidates)
    creation = {row["candidate_id"]: row["created_at"] for row in connection.execute("SELECT candidate_id,created_at FROM Candidate ORDER BY candidate_id")}
    rows, events, counter = [], [], 0
    base, extra = divmod(config.scale.applications,config.scale.requisitions)
    for index, req in enumerate(sorted(requirements)):
        desired = base+int(index<extra)
        groups = {"excellent": [], "borderline": [], "weak": []}
        for candidate in candidate_ids:
            groups[skill_fit(requirements[req],candidates[candidate]).category].append(candidate)
        quotas = {"excellent": desired*40//100, "borderline": desired*35//100}
        quotas["weak"] = desired-sum(quotas.values())
        chosen = []
        for category in ("excellent","borderline","weak"):
            chosen.extend(rng.sample(groups[category],min(quotas[category],len(groups[category]))))
        selected = set(chosen)
        if len(chosen)<desired:
            chosen.extend(rng.sample([candidate for candidate in candidate_ids if candidate not in selected],desired-len(chosen)))
        opened = connection.execute("SELECT occurred_at FROM RequisitionEvent WHERE requisition_id=? AND sequence=4", (req,)).fetchone()[0]
        for candidate in sorted(chosen):
            counter += 1
            applied = max(creation[candidate],opened)+rng.randint(60,30*DAY)
            app = application_id(candidate,req)
            rows.append(dict(application_id=app,candidate_id=candidate,requisition_id=req,
                status="applied",applied_at=applied,updated_at=applied))
            events.append(_event(numbered_id("application_event",counter),"application_id",app,1,None,"applied",
                "created",SYSTEM,applied,"SYNTHETIC_APPLICATION_SUBMITTED",candidate=candidate))
            if len(rows)==256:
                _batch(connection,"Application",rows); _batch(connection,"ApplicationEvent",events)
                rows.clear(); events.clear()
    _batch(connection,"Application",rows); _batch(connection,"ApplicationEvent",events)


def _populate(connection, config):
    _staff_and_managers(connection,config)
    _requisitions(connection,config)
    _candidates(connection,config)
    _applications(connection,config)


def generate_database(database: str | Path, config: GenerationConfig, *, phase="master", scheduling=None) -> GenerationResult:
    """Publish a new complete validated DB, atomically, with no overwrite option."""
    started = perf_counter()
    if phase not in ("master","interviews","evaluations") or (phase == "master" and scheduling is not None):
        raise ValueError("Use master, interviews or evaluations mode; scheduling config belongs to workflow modes")
    if phase != "master":
        from .interview_generation import SchedulingConfig
        scheduling = scheduling or SchedulingConfig.for_profile(config)
        scheduling.validate_for(config)
    timings = None
    target = Path(database)
    if target.suffix.lower() not in (".sqlite3",".sqlite",".db"):
        raise ValueError("Output must have .sqlite3, .sqlite or .db extension")
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing existing output: {target}")
    target.parent.mkdir(parents=True,exist_ok=True)
    descriptor, scratch_name = tempfile.mkstemp(prefix=".yottaflex-generation-",suffix=".sqlite3",dir=target.parent)
    os.close(descriptor)
    scratch = Path(scratch_name)
    try:
        with closing(connect(scratch)) as connection:
            initialize(connection)
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                _populate(connection,config)
                validation = validate_generated(connection,config)
                if not validation["passed"]:
                    raise ValueError(f"Generated data failed validation: {stable_json(validation)}")
                summary = generation_summary(connection,config,validation)
                canonical = dataset_digest(connection)
            if phase != "master":
                from .interview_generation import populate_interviews
                from .workflow_checks import master_fingerprint, validate_workflow
                before = master_fingerprint(connection,config)
                phase03_canonical = canonical
                schedule_started = perf_counter()
                operations = populate_interviews(connection,config,scheduling)
                schedule_seconds = perf_counter()-schedule_started
                validation_started = perf_counter()
                validation = validate_workflow(connection,config,scheduling.target)
                validation_seconds = perf_counter()-validation_started
                preservation = before == master_fingerprint(connection,config)
                if not validation["passed"] or not preservation:
                    raise ValueError(f"Workflow validation failed: {stable_json(validation)}; master_preserved={preservation}")
                summary = generation_summary(connection,config,validation)
                summary.update(scope="phase04_interview_lifecycle",scheduling=operations,
                               phase03_canonical=phase03_canonical,master_preserved=preservation,
                               unavailable_metrics=["review_completion","offer_outcomes","anomaly_detection"])
                canonical = dataset_digest(connection)
                timings = {"scheduling_seconds":schedule_seconds,"validation_seconds":validation_seconds}
                if phase == "evaluations":
                    from .evaluation_generation import populate_evaluations
                    from .evaluation_checks import validate_evaluations
                    phase04_canonical = canonical
                    evaluation,components = populate_evaluations(connection,config)
                    validation_started = perf_counter()
                    validation = validate_evaluations(connection,config,scheduling.target)
                    final_validation_seconds = perf_counter()-validation_started
                    preservation = before==master_fingerprint(connection,config)
                    if not validation["passed"] or not preservation:
                        raise ValueError(f"Evaluation validation failed: {stable_json(validation)}; master_preserved={preservation}")
                    summary = generation_summary(connection,config,validation)
                    summary.update(scope="phase05_evaluation_offer_lifecycle",scheduling=operations,evaluation=evaluation,
                        phase03_canonical=phase03_canonical,phase04_canonical=phase04_canonical,master_preserved=preservation,
                        unavailable_metrics=["anomaly_detection","export_equivalence"])
                    timings.update(phase04_validation_seconds=timings.pop("validation_seconds"),
                        validation_seconds=final_validation_seconds,**components)
                    canonical = dataset_digest(connection)
        # Same-directory hard link is atomic and cannot replace an existing path.
        # Random scratch names are IO safety only, never generated data or IDs.
        os.link(scratch,target)
    finally:
        scratch.unlink(missing_ok=True)
    return GenerationResult(summary,canonical,perf_counter()-started,timings)


def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile",type=str.lower,choices=("starter","full"),required=True)
    parser.add_argument("--seed",type=int,default=DEFAULT_SEED)
    parser.add_argument("--database",required=True,help="New local SQLite output; existing paths are refused")
    parser.add_argument("--phase",choices=("master","interviews","evaluations"),default="master")
    parser.add_argument("--interviews",type=int,help="Starter target (default 40); full must be 2000")
    args = parser.parse_args()
    try:
        config = GenerationConfig(profile=args.profile,seed=args.seed)
        scheduling = None
        if args.interviews is not None:
            if args.phase == "master":
                raise ValueError("--interviews requires a workflow phase")
            from .interview_generation import SchedulingConfig
            scheduling = SchedulingConfig.for_profile(config,args.interviews)
        result = generate_database(args.database,config,phase=args.phase,scheduling=scheduling)
    except (OSError,ValueError,sqlite3.Error) as error:
        print(f"Generation failed: {error}",file=sys.stderr)
        return 1
    output = {"summary":result.summary,"canonical":result.canonical,"elapsed_seconds":result.elapsed_seconds}
    if result.timings is not None:
        output["timings"] = result.timings
    print(json.dumps(output,sort_keys=True,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
