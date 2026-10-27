"""Deterministic identities for implemented master and interview workflows."""

import re


PREFIXES = {"staff": "STAFF-", "manager": "HM-", "requisition": "REQ-2026-",
    "candidate": "CAND-", "skill": "SKILL-", "approval": "APR-",
    "requisition_event": "REQEV-", "candidate_event": "CANEV-",
    "approval_event": "APREV-", "application_event": "APPEV-",
    "panel": "PANEL-", "availability": "AVAIL-", "interview": "INT-2026-",
    "interview_event": "INTEV-", "scorecard_event":"SCREV-",
    "offer":"OFF-2026-", "offer_event":"OFFEV-"}


def numbered_id(kind: str, counter: int) -> str:
    if kind not in PREFIXES or type(counter) is not int or not 1 <= counter <= 999999:
        raise ValueError("Unknown identity kind or counter outside 1..999999")
    return f"{PREFIXES[kind]}{counter:06d}"


def valid_numbered_id(kind: str, value: str) -> bool:
    prefix = PREFIXES.get(kind)
    return bool(prefix and isinstance(value, str) and re.fullmatch(re.escape(prefix)+r"[0-9]{6}", value)
                and not value.endswith("000000"))


def application_id(candidate_id: str, requisition_id: str) -> str:
    if not valid_numbered_id("candidate", candidate_id) or not valid_numbered_id("requisition", requisition_id):
        raise ValueError("Application parents must use valid required identities")
    return f"APP-{candidate_id}-{requisition_id}"
