"""Band snapshots, independent approval and transactional offer finalization."""

import json

from .evaluation import evaluate_application
from .workflow import (_append_event, _app_change, _authorize, _eligible_application,
    _eligible_requisition, _fail, _last_event, _metadata, _row, _withdraw_app,
    next_id, write_transaction)


ACTIVE_OFFERS = ("draft","pending_approval","approved","sent","accepted")


def approved_band(connection, requisition_id, when):
    req = _eligible_requisition(connection,requisition_id,when)
    band = connection.execute("""SELECT * FROM RequisitionEvent WHERE requisition_id=? AND new_status='approved'
        AND occurred_at<=? AND band_min_minor IS NOT NULL AND band_max_minor IS NOT NULL
        ORDER BY sequence DESC LIMIT 1""", (requisition_id,when)).fetchone()
    if band is None or (band["band_min_minor"],band["band_max_minor"],band["currency"]) != (req["band_min_minor"],req["band_max_minor"],req["currency"]):
        _fail("COMPENSATION_SNAPSHOT_MISMATCH","Current compensation must reconcile to the causal approved event")
    return band


def proposed_amount(band, decision):
    """Linear position in band from actual 3000..4000 aggregate, floor minor unit."""
    return band["band_min_minor"]+(band["band_max_minor"]-band["band_min_minor"])*max(0,min(1000,decision["aggregate_milli"]-3000))//1000


def approval_limit(band):
    return band["band_min_minor"]+(band["band_max_minor"]-band["band_min_minor"])*70//100


def _amount(band, amount, currency):
    if type(amount) is not int or amount<=0:
        _fail("INVALID_AMOUNT","Use positive integer minor currency units")
    if currency!=band["currency"]:
        _fail("CURRENCY_MISMATCH","Offer must use approved snapshot currency")
    if not band["band_min_minor"]<=amount<=band["band_max_minor"]:
        _fail("OFFER_OUTSIDE_BAND","Amount must lie inside inclusive approved boundaries")


def _other_active(connection, candidate_id, *, exclude=None):
    return connection.execute("""SELECT o.offer_id FROM Offer o JOIN Application a USING(application_id)
        WHERE a.candidate_id=? AND o.is_final=1 AND o.status IN ('draft','pending_approval','approved','sent','accepted')
        AND (? IS NULL OR o.offer_id<>?) LIMIT 1""", (candidate_id,exclude,exclude)).fetchone()


def _snapshot(connection, table, key, identity):
    return dict(_row(connection,table,key,identity,table.upper()+"_NOT_FOUND"))


def _offer_change(connection, offer, status, actor, when, reason, correlation, *, details=None):
    _last_event(connection,"Offer","offer_id",offer["offer_id"],offer["status"],when)
    connection.execute("UPDATE Offer SET status=? WHERE offer_id=?", (status,offer["offer_id"]))
    _append_event(connection,"Offer","offer_id",offer["offer_id"],"decision_recorded" if status in ("approved","rejected") else "status_changed",
        offer["status"],status,actor,when,reason,correlation,dict(offer),_snapshot(connection,"Offer","offer_id",offer["offer_id"]),details=details)


def create_offer(connection, application_id, *, actor_id, when, reason_code, amount_minor=None, currency=None, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        app = _eligible_application(connection,application_id)
        _authorize(connection,actor_id,when,app["requisition_id"])
        _last_event(connection,"Application","application_id",application_id,app["status"],when)
        if _other_active(connection,app["candidate_id"]):
            _fail("INCOMPATIBLE_ACTIVE_OFFER","Candidate already has an incompatible active final offer")
        if app["status"]!="reviewed":
            _fail("APPLICATION_STAGE_INELIGIBLE","Offer creation requires reviewed application")
        decision = evaluate_application(connection,application_id,when=when)
        if not decision["offer_eligible"]:
            _fail("OFFER_INELIGIBLE","Evaluation does not meet the separate offer threshold/minimums")
        band = approved_band(connection,app["requisition_id"],when)
        amount = proposed_amount(band,decision) if amount_minor is None else amount_minor
        currency = band["currency"] if currency is None else currency
        _amount(band,amount,currency)
        identity = next_id(connection,"Offer","offer_id","offer")
        connection.execute("INSERT INTO Offer VALUES (?,?,?,?,?,?,1,'draft',?,NULL)",
            (identity,application_id,app["requisition_id"],band["event_id"],currency,amount,when))
        _append_event(connection,"Offer","offer_id",identity,"created",None,"draft",actor_id,when,reason_code,correlation_id,
            {"status":None},_snapshot(connection,"Offer","offer_id",identity),details=decision)
        _app_change(connection,app,"offer","status_changed",actor_id,when,reason_code,correlation_id or identity,details=decision|{"offer_id":identity})
        return identity


def _context(connection, identity, actor, when, allowed):
    offer = _row(connection,"Offer","offer_id",identity,"OFFER_NOT_FOUND")
    if offer["status"] not in allowed:
        _fail("OFFER_STATE_INVALID","Operation not permitted from current offer status")
    app = _eligible_application(connection,offer["application_id"])
    if app["status"]!="offer":
        _fail("APPLICATION_STAGE_INELIGIBLE","Offer workflow requires application offer stage")
    _authorize(connection,actor,when,app["requisition_id"])
    event = _last_event(connection,"Offer","offer_id",identity,offer["status"],when)
    if json.loads(event["snapshot_json"]).get("after")!=dict(offer):
        _fail("HISTORY_MISMATCH","Offer projection must agree with its last complete snapshot")
    _last_event(connection,"Application","application_id",app["application_id"],app["status"],when)
    if when<offer["valid_from"] or (offer["valid_to"] is not None and when>=offer["valid_to"]):
        _fail("OFFER_INEFFECTIVE","Offer is not effective")
    decision = evaluate_application(connection,app["application_id"],when=when)
    if not decision["offer_eligible"]:
        _fail("OFFER_INELIGIBLE","Required evaluation no longer reconciles")
    band = approved_band(connection,app["requisition_id"],when)
    if offer["approved_requisition_event_id"]!=band["event_id"]:
        _fail("COMPENSATION_SNAPSHOT_MISMATCH","Historical authorization changed; explicit new offer policy required")
    _amount(band,offer["amount_minor"],offer["currency"])
    if _other_active(connection,app["candidate_id"],exclude=identity):
        _fail("INCOMPATIBLE_ACTIVE_OFFER","Candidate has another active final offer")
    return offer,app,band


def submit_offer(connection, offer_id, approver_id, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        offer,app,_ = _context(connection,offer_id,actor_id,when,("draft",))
        _authorize(connection,approver_id,when)  # HR/admin, never requisition owner alone.
        creator = connection.execute("SELECT actor_staff_id FROM OfferEvent WHERE offer_id=? AND sequence=1", (offer_id,)).fetchone()
        if approver_id==actor_id or creator is None or approver_id==creator[0]:
            _fail("SELF_APPROVAL_FORBIDDEN","Requester and approver must differ")
        if connection.execute("SELECT 1 FROM Approval WHERE offer_id=?", (offer_id,)).fetchone():
            _fail("DUPLICATE_APPROVAL","One approval decision per offer")
        identity = next_id(connection,"Approval","approval_id","approval")
        connection.execute("INSERT INTO Approval VALUES (?,NULL,?,?,'pending',?,NULL,?,?,NULL)",
            (identity,offer_id,approver_id,when,reason_code,when))
        _append_event(connection,"Approval","approval_id",identity,"created",None,"pending",actor_id,when,reason_code,correlation_id or offer_id,
            {"status":None},_snapshot(connection,"Approval","approval_id",identity))
        _offer_change(connection,offer,"pending_approval",actor_id,when,reason_code,correlation_id,details={"approval_id":identity})
        _app_change(connection,app,"offer","revised",actor_id,when,reason_code,correlation_id or offer_id,details={"offer_id":offer_id,"approval_id":identity})
        return identity


def decide_offer(connection, offer_id, approve, *, actor_id, when, reason_code, correlation_id=None):
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        if type(approve) is not bool:
            _fail("INVALID_DECISION","Approval decision must be boolean")
        offer,app,band = _context(connection,offer_id,actor_id,when,("pending_approval",))
        approval = connection.execute("SELECT * FROM Approval WHERE offer_id=?", (offer_id,)).fetchone()
        if approval is None or approval["status"]!="pending":
            _fail("APPROVAL_STATE_INVALID","Pending offer-specific Approval required")
        if when<approval["valid_from"] or (approval["valid_to"] is not None and when>=approval["valid_to"]):
            _fail("APPROVAL_INEFFECTIVE","Approval authorization does not cover decision time")
        _authorize(connection,actor_id,when)
        requester = connection.execute("SELECT actor_staff_id FROM ApprovalEvent WHERE approval_id=? AND sequence=1", (approval["approval_id"],)).fetchone()
        if actor_id!=approval["approver_staff_id"] or requester is None or requester[0]==actor_id:
            _fail("APPROVER_UNAUTHORIZED","Only appointed independent HR/admin may decide")
        _last_event(connection,"Approval","approval_id",approval["approval_id"],"pending",when)
        if approve != (offer["amount_minor"]<=approval_limit(band)):
            _fail("APPROVAL_POLICY_MISMATCH","Decision must match the documented 70%-of-band budget limit")
        status = "approved" if approve else "rejected"
        details = {"offer_id":offer_id,"approval_id":approval["approval_id"],"budget_limit_minor":approval_limit(band)}
        connection.execute("UPDATE Approval SET status=?,decided_at=?,reason_code=? WHERE approval_id=?", (status,when,reason_code,approval["approval_id"]))
        _append_event(connection,"Approval","approval_id",approval["approval_id"],"decision_recorded","pending",status,actor_id,when,reason_code,correlation_id or offer_id,
            dict(approval),_snapshot(connection,"Approval","approval_id",approval["approval_id"]),details=details)
        _offer_change(connection,offer,status,actor_id,when,reason_code,correlation_id,details=details)
        _app_change(connection,app,"offer" if approve else "rejected","revised" if approve else "decision_recorded",
            actor_id,when,reason_code,correlation_id or offer_id,details=details)
        return status


def _approved(connection, offer_id, when):
    approval = connection.execute("SELECT * FROM Approval WHERE offer_id=? AND status='approved' AND decided_at<=? AND valid_from<=? AND (valid_to IS NULL OR valid_to>?)", (offer_id,when,when,when)).fetchone()
    if approval is None:
        _fail("APPROVAL_REQUIRED","Causal approved offer decision required")
    event = _last_event(connection,"Approval","approval_id",approval["approval_id"],"approved",when)
    if event["actor_staff_id"]!=approval["approver_staff_id"]:
        _fail("APPROVER_UNAUTHORIZED","Approved decision must retain its appointed actor")
    return approval


def send_offer(connection, offer_id, *, actor_id, when, reason_code, correlation_id=None):
    """Local sent state only; never sends email or contacts any person."""
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        offer,app,_ = _context(connection,offer_id,actor_id,when,("approved",))
        approval = _approved(connection,offer_id,when)
        details = {"offer_id":offer_id,"approval_id":approval["approval_id"]}
        _offer_change(connection,offer,"sent",actor_id,when,reason_code,correlation_id,details=details)
        _app_change(connection,app,"offer","revised",actor_id,when,reason_code,correlation_id or offer_id,details=details)


def accept_offer(connection, offer_id, *, actor_id, when, reason_code, correlation_id=None):
    """HR records synthetic candidate acceptance; atomically resolves other apps."""
    with write_transaction(connection):
        _metadata(when,reason_code,correlation_id)
        offer,app,_ = _context(connection,offer_id,actor_id,when,("sent",))
        _authorize(connection,actor_id,when)  # Cross-requisition cleanup needs HR/admin.
        approval = _approved(connection,offer_id,when)
        for other in connection.execute("SELECT * FROM Application WHERE candidate_id=? AND application_id<>? ORDER BY application_id", (app["candidate_id"],app["application_id"])).fetchall():
            if other["status"] in ("applied","screening","interviewing"):
                _withdraw_app(connection,other,actor_id,when,"OTHER_ROLE_ACCEPTED",offer_id,app["candidate_id"])
            elif other["status"]=="reviewed":
                _app_change(connection,other,"withdrawn","withdrawn",actor_id,when,"OTHER_ROLE_ACCEPTED",offer_id,candidate=app["candidate_id"])
            elif other["status"] in ("offer","hired"):
                _fail("INCOMPATIBLE_ACTIVE_OFFER","Other advanced application must be explicitly resolved")
        details = {"offer_id":offer_id,"approval_id":approval["approval_id"]}
        _offer_change(connection,offer,"accepted",actor_id,when,reason_code,correlation_id,details=details)
        _app_change(connection,app,"hired","status_changed",actor_id,when,reason_code,correlation_id or offer_id,candidate=app["candidate_id"],details=details)
