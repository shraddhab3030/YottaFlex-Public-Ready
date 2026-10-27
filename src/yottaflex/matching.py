"""Descriptive skill matching, not hiring decisions or anomaly ground truth."""

from typing import NamedTuple


class Fit(NamedTuple):
    basis_points: int
    missing_required: int
    category: str


def skill_fit(requirements, candidate_skills) -> Fit:
    """Integer weighted attainment, clipped at each stored requirement minimum."""
    total = 0
    missing = 0
    for requirement in requirements:
        minimum = requirement["min_proficiency"]
        level = candidate_skills.get(requirement["criterion_key"], 0)
        weight = requirement["weight_basis_points"]
        total += weight if minimum == 0 else weight*min(level, minimum)//minimum
        missing += int(bool(requirement["is_required"]) and level < minimum)
    category = "excellent" if not missing and total >= 8500 else "borderline" if total >= 6000 else "weak"
    return Fit(total, missing, category)


def load_matching_inputs(connection):
    """Use actual stored records as the sole source of fit calculations."""
    candidates = {row[0]: {} for row in connection.execute("SELECT candidate_id FROM Candidate ORDER BY candidate_id")}
    for row in connection.execute("SELECT candidate_id, skill_key, level FROM CandidateSkill ORDER BY candidate_id, skill_key"):
        candidates[row["candidate_id"]][row["skill_key"]] = row["level"]
    requirements = {row[0]: [] for row in connection.execute("SELECT requisition_id FROM Requisition ORDER BY requisition_id")}
    for row in connection.execute("SELECT * FROM SkillRequirement ORDER BY requisition_id, skill_requirement_id"):
        requirements[row["requisition_id"]].append(dict(row))
    return candidates, requirements
