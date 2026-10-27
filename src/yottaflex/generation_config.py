"""Explicit synthetic assumptions; none are empirical hiring population claims."""

from dataclasses import dataclass


DEFAULT_SEED = 20261022
LOGICAL_ORIGIN = 1767225600  # 2026-01-01T00:00:00Z, not execution time.
DAY = 86400
SKILLS = ("python", "sql", "backend", "cloud", "api_integration",
          "data_analysis", "ml_fundamentals", "problem_solving")
# Category, title, compensation multiplier (%), (skill, required, base weight).
ROLES = (
    ("backend", "Backend Engineer", 100, (("backend", 1, 35), ("python", 1, 30), ("api_integration", 1, 20), ("sql", 0, 15))),
    ("data", "Data Analyst", 95, (("sql", 1, 35), ("data_analysis", 1, 35), ("python", 0, 20), ("problem_solving", 1, 10))),
    ("integration", "Integration Engineer", 105, (("api_integration", 1, 40), ("backend", 1, 25), ("cloud", 1, 25), ("problem_solving", 0, 10))),
    ("applied_ai", "Applied AI Engineer", 115, (("python", 1, 35), ("ml_fundamentals", 1, 35), ("sql", 1, 20), ("cloud", 0, 10))),
)
SENIORITY = (("Junior", 2), ("Mid", 3), ("Senior", 4))
ANNUAL_BASE_MAJOR = {"INR": (900000, 1700000, 2800000), "USD": (60000, 100000, 150000)}
APPROVAL_CAP_MINOR = {"INR": 500000000, "USD": 25000000}


@dataclass(frozen=True)
class Scale:
    requisitions: int
    candidates: int
    applications: int


PROFILES = {"starter": Scale(10, 100, 160), "full": Scale(200, 5000, 8000)}


@dataclass(frozen=True)
class GenerationConfig:
    profile: str = "starter"
    seed: int = DEFAULT_SEED
    logical_origin: int = LOGICAL_ORIGIN
    scale: Scale | None = None  # Tiny explicit scales support boundary tests.

    def __post_init__(self):
        if self.profile not in PROFILES and self.profile != "custom":
            raise ValueError("Unknown generation profile")
        if self.scale is None:
            if self.profile == "custom":
                raise ValueError("Custom profile requires an explicit Scale")
            object.__setattr__(self, "scale", PROFILES[self.profile])
        elif self.profile != "custom" and self.scale != PROFILES[self.profile]:
            raise ValueError("Named profile counts cannot be overridden")
        if type(self.seed) is not int or not 0 <= self.seed < 2**63:
            raise ValueError("Seed must be an integer in 0..2^63-1")
        if type(self.logical_origin) is not int or not DAY <= self.logical_origin <= 253402300799-200*DAY:
            raise ValueError("Logical origin must leave room for the declared 200-day timeline")
        if not isinstance(self.scale, Scale):
            raise ValueError("Scale must be a Scale value")
        r, c, a = self.scale.requisitions, self.scale.candidates, self.scale.applications
        if any(type(value) is not int for value in (r, c, a)):
            raise ValueError("Counts must be integers")
        if not 1 <= r <= 249999 or not 1 <= c <= 999999 or not 0 <= a <= min(r*c, 999999):
            raise ValueError("Counts exceed pair capacity or six-digit identity capacity")

    @property
    def managers(self):
        return min(self.scale.requisitions, max(2, min(20, (self.scale.requisitions+9)//10)))

    def as_dict(self):
        return {"profile": self.profile, "seed": self.seed, "logical_origin": self.logical_origin,
                "counts": {"Requisition": self.scale.requisitions, "Candidate": self.scale.candidates,
                           "Application": self.scale.applications}, "policy_version": 1}
