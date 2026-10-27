"""Public business-rule catalogue, shared vocabulary without per-record answers."""
RULES = {
    "R01":"stage_gate_missing_review",
    "R02":"interviewer_double_booked",
    "R03":"offer_exceeds_band",
    "R04":"withdrawn_still_scheduled",
    "R05":"irrelevant_evaluation_criterion",
}
CAPACITY = ("scheduled","completed","no_show")
