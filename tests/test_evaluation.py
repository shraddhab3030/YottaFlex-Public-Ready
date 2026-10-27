"""Real scorecard, approval and terminal-state operation tests in isolated DBs."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from yottaflex.canonical import dataset_digest
from yottaflex.db import connect
from yottaflex.evaluation import (applicable_criteria, computed_card, create_scorecard,
    evaluate_application, reject_evaluated_application, review_application,
    set_scorecard_item, submit_scorecard)
from yottaflex.generate import generate_database
from yottaflex.generation_config import DAY, GenerationConfig
from yottaflex.offers import (accept_offer, approval_limit, approved_band, create_offer,
    decide_offer, send_offer, submit_offer)
from yottaflex.workflow import (DomainError, complete_interview, schedule_interview,
    transition_application, withdraw_application, withdraw_candidate)


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="yottaflex-evaluation-tests-")
        cls.base = Path(cls.workspace.name)/"baseline.sqlite3"
        generate_database(cls.base,GenerationConfig(),phase="interviews")

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def setUp(self):
        self.db = connect(); self.addCleanup(self.db.close)
        with closing(connect(self.base)) as source:
            source.backup(self.db)
        self.clock = GenerationConfig().logical_origin+188*DAY
        self.interview = self.db.execute("""SELECT i.* FROM Interview i JOIN Application a USING(application_id)
            WHERE i.status='scheduled' AND (SELECT COUNT(*) FROM Application b WHERE b.candidate_id=a.candidate_id)>1
            ORDER BY i.interview_id LIMIT 1""").fetchone()
        self.app = self.interview["application_id"]
        self.reviewers = [row[0] for row in self.db.execute("SELECT staff_id FROM InterviewParticipant WHERE interview_id=? ORDER BY staff_id", (self.interview["interview_id"],))]
        self.criteria = applicable_criteria(self.db,self.interview)
        self.manager = self.db.execute("SELECT h.staff_id FROM Requisition r JOIN HiringManager h USING(hiring_manager_id) WHERE requisition_id=?", (self.interview["requisition_id"],)).fetchone()[0]
        complete_interview(self.db,self.interview["interview_id"],**self.meta())

    def meta(self, actor="STAFF-000002"):
        self.clock += 1
        return dict(actor_id=actor,when=self.clock,reason_code="ISOLATED_TEST")

    def fails(self, code, callback):
        before = dataset_digest(self.db)
        with self.assertRaises(DomainError) as error:
            callback()
        self.assertEqual(error.exception.code,code)
        self.assertEqual(dataset_digest(self.db),before)
        self.assertFalse(self.db.in_transaction)

    def card(self, reviewer=None, values=None, submit=True):
        reviewer = reviewer or self.reviewers[0]
        identity = create_scorecard(self.db,self.interview["interview_id"],reviewer,**self.meta(reviewer))
        for index,criterion in enumerate(self.criteria):
            value = 3 if values is None else values[index]
            if value is not None:
                set_scorecard_item(self.db,identity,criterion["skill_requirement_id"],value,"Synthetic test evidence",**self.meta(reviewer))
        if submit:
            submit_scorecard(self.db,identity,**self.meta(reviewer))
        return identity

    def reviewed(self, values=None):
        for reviewer in self.reviewers:
            self.card(reviewer,values)
        return review_application(self.db,self.app,**self.meta())

    def offer(self, amount=None):
        self.reviewed()
        return create_offer(self.db,self.app,amount_minor=amount,**self.meta(self.manager))

    def pending(self, upper=False):
        band = approved_band(self.db,self.interview["requisition_id"],self.clock)
        identity = self.offer(band["band_max_minor"] if upper else None)
        approval = submit_offer(self.db,identity,"STAFF-000002",**self.meta(self.manager))
        return identity,approval

    def accepted(self):
        identity,approval = self.pending()
        decide_offer(self.db,identity,True,**self.meta())
        send_offer(self.db,identity,**self.meta(self.manager))
        accept_offer(self.db,identity,**self.meta())
        return identity,approval

    def test_valid_creation_has_canonical_staff_reviewer_id_and_pending_items(self):
        identity = create_scorecard(self.db,self.interview["interview_id"],self.reviewers[0],**self.meta(self.reviewers[0]))
        self.assertEqual(identity,f"SCORE-{self.interview['interview_id']}-{self.reviewers[0]}")
        self.assertEqual(self.db.execute("SELECT status FROM Scorecard").fetchone()[0],"draft")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM ScorecardItem").fetchone()[0],4)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM ScorecardEvent").fetchone()[0],1)

    def test_invalid_reviewer_and_wrong_author_rejected(self):
        self.fails("REVIEWER_INELIGIBLE",lambda:create_scorecard(self.db,self.interview["interview_id"],"STAFF-000003",**self.meta("STAFF-000003")))
        self.fails("REVIEWER_INELIGIBLE",lambda:create_scorecard(self.db,self.interview["interview_id"],self.reviewers[0],**self.meta()))

    def test_cancelled_interview_and_uncompleted_interview_cannot_be_scored(self):
        for status in ("cancelled","scheduled"):
            row = self.db.execute("SELECT * FROM Interview WHERE status=? LIMIT 1", (status,)).fetchone()
            self.fails("INTERVIEW_NOT_COMPLETED",lambda:create_scorecard(self.db,row["interview_id"],self.reviewers[0],**self.meta(self.reviewers[0])))

    def test_irrelevant_criterion_rejected(self):
        identity = self.card(submit=False)
        other = self.db.execute("SELECT skill_requirement_id FROM SkillRequirement WHERE requisition_id<>? LIMIT 1", (self.interview["requisition_id"],)).fetchone()[0]
        self.fails("IRRELEVANT_CRITERION",lambda:set_scorecard_item(self.db,identity,other,3,"Evidence",**self.meta(self.reviewers[0])))

    def test_rubric_boundaries_zero_four_and_invalid_values(self):
        identity = self.card(submit=False)
        criterion = self.criteria[0]["skill_requirement_id"]
        for value in (0,4):
            set_scorecard_item(self.db,identity,criterion,value,"Boundary evidence",**self.meta(self.reviewers[0]))
            self.assertEqual(self.db.execute("SELECT score_value FROM ScorecardItem WHERE scorecard_id=? AND skill_requirement_id=?", (identity,criterion)).fetchone()[0],value)
        for value in (-1,5,True,1.5):
            self.fails("INVALID_RUBRIC_VALUE",lambda:set_scorecard_item(self.db,identity,criterion,value,"Evidence",**self.meta(self.reviewers[0])))

    def test_required_criterion_omission_blocks_submit(self):
        values = [None if row["is_required"] else 3 for row in self.criteria]
        identity = self.card(values=values,submit=False)
        self.fails("SCORECARD_INCOMPLETE",lambda:submit_scorecard(self.db,identity,**self.meta(self.reviewers[0])))

    def test_optional_criterion_omission_also_blocks_weight_normalization(self):
        values = [3 if row["is_required"] else None for row in self.criteria]
        identity = self.card(values=values,submit=False)
        self.fails("SCORECARD_INCOMPLETE",lambda:submit_scorecard(self.db,identity,**self.meta(self.reviewers[0])))

    def test_duplicate_scorecard_rejected(self):
        self.card()
        self.fails("DUPLICATE_SCORECARD",lambda:create_scorecard(self.db,self.interview["interview_id"],self.reviewers[0],**self.meta(self.reviewers[0])))

    def test_weighted_integer_math_and_independent_sql_recomputation(self):
        identity = self.card(values=[0,1,3,4])
        numerator = self.db.execute("SELECT SUM(i.score_value*r.weight_basis_points) FROM ScorecardItem i JOIN SkillRequirement r USING(skill_requirement_id) WHERE scorecard_id=?", (identity,)).fetchone()[0]
        independently_rounded = (numerator*1000+5000)//10000
        self.assertEqual(computed_card(self.db,identity)["total_score_milli"],independently_rounded)
        self.assertEqual(self.db.execute("SELECT total_score_milli FROM Scorecard WHERE scorecard_id=?", (identity,)).fetchone()[0],independently_rounded)

    def test_missing_evidence_rejected_and_editable_pending_reset_supported(self):
        identity = self.card(submit=False); criterion = self.criteria[0]["skill_requirement_id"]
        self.fails("EVIDENCE_REQUIRED",lambda:set_scorecard_item(self.db,identity,criterion,3," ",**self.meta(self.reviewers[0])))
        set_scorecard_item(self.db,identity,criterion,None,None,**self.meta(self.reviewers[0]))
        self.fails("SCORECARD_INCOMPLETE",lambda:submit_scorecard(self.db,identity,**self.meta(self.reviewers[0])))

    def test_submitted_scorecards_are_locked(self):
        identity = self.card()
        self.fails("SCORECARD_LOCKED",lambda:set_scorecard_item(self.db,identity,self.criteria[0]["skill_requirement_id"],4,"Changed",**self.meta(self.reviewers[0])))
        self.fails("SCORECARD_LOCKED",lambda:submit_scorecard(self.db,identity,**self.meta(self.reviewers[0])))

    def test_criterion_version_drift_rejected(self):
        identity = self.card(submit=False)
        with self.db:
            self.db.execute("UPDATE SkillRequirement SET rubric_version=2 WHERE requisition_id=?", (self.interview["requisition_id"],))
        self.fails("RUBRIC_VERSION_INVALID",lambda:submit_scorecard(self.db,identity,**self.meta(self.reviewers[0])))

    def test_incomplete_or_missing_reviewer_blocks_review(self):
        self.card(values=[None,3,3,3],submit=False)
        self.fails("REVIEW_GATE_INCOMPLETE",lambda:review_application(self.db,self.app,**self.meta()))

    def test_completed_required_evaluations_allow_real_transition(self):
        result = self.reviewed()
        self.assertTrue(result["review_eligible"])
        self.assertEqual(result["aggregate_milli"],3000)
        self.assertEqual(self.db.execute("SELECT status FROM Application WHERE application_id=?", (self.app,)).fetchone()[0],"reviewed")

    def test_general_transition_routes_to_actual_review_gate(self):
        for reviewer in self.reviewers:
            self.card(reviewer)
        transition_application(self.db,self.app,"reviewed",**self.meta())
        self.assertEqual(self.db.execute("SELECT status FROM Application WHERE application_id=?", (self.app,)).fetchone()[0],"reviewed")

    def test_uncompleted_interview_blocks_review(self):
        other = self.db.execute("SELECT application_id FROM Interview WHERE status='scheduled' LIMIT 1").fetchone()[0]
        self.fails("REVIEW_GATE_INCOMPLETE",lambda:review_application(self.db,other,**self.meta()))

    def test_withdrawn_and_rejected_applications_cannot_review(self):
        withdraw_application(self.db,self.app,**self.meta())
        self.fails("APPLICATION_WITHDRAWN",lambda:review_application(self.db,self.app,**self.meta()))
        other = self.db.execute("SELECT application_id FROM Application WHERE status='applied' LIMIT 1").fetchone()[0]
        transition_application(self.db,other,"rejected",**self.meta())
        self.fails("INVALID_TRANSITION",lambda:review_application(self.db,other,**self.meta()))

    def test_low_evaluation_rejects_review_and_supports_reasoned_rejection(self):
        for reviewer in self.reviewers:
            self.card(reviewer,[0,0,0,0])
        self.fails("REVIEW_DECISION_FAILED",lambda:review_application(self.db,self.app,**self.meta()))
        reject_evaluated_application(self.db,self.app,**self.meta())
        self.assertEqual(self.db.execute("SELECT status FROM Application WHERE application_id=?", (self.app,)).fetchone()[0],"rejected")

    def test_conflicting_complete_reviewers_block_review_despite_aggregate_and_minimum(self):
        for index,reviewer in enumerate(self.reviewers):
            self.card(reviewer,[2,2,2,2] if index==0 else [4,4,4,4])
        decision = evaluate_application(self.db,self.app)
        self.assertGreaterEqual(decision["aggregate_milli"],2500)
        self.assertGreaterEqual(decision["required_minimum"],2)
        self.assertEqual(decision["reviewer_spread_milli"],2000)
        self.fails("REVIEW_DECISION_FAILED",lambda:review_application(self.db,self.app,**self.meta()))

    def test_review_and_offer_eligibility_are_separate(self):
        values = [3]*4
        index = next(i for i,row in enumerate(self.criteria) if row["is_required"])
        values[index] = 2
        self.reviewed(values)
        self.fails("OFFER_INELIGIBLE",lambda:create_offer(self.db,self.app,**self.meta(self.manager)))

    def test_valid_offer_amount_derived_from_actual_aggregate_and_snapshot(self):
        identity = self.offer()
        row = self.db.execute("SELECT * FROM Offer WHERE offer_id=?", (identity,)).fetchone()
        band = approved_band(self.db,self.interview["requisition_id"],self.clock)
        self.assertEqual(row["amount_minor"],band["band_min_minor"])
        self.assertEqual(row["approved_requisition_event_id"],band["event_id"])

    def test_below_band_and_above_band_rejected(self):
        self.reviewed(); band = approved_band(self.db,self.interview["requisition_id"],self.clock)
        for amount in (band["band_min_minor"]-1,band["band_max_minor"]+1):
            self.fails("OFFER_OUTSIDE_BAND",lambda:create_offer(self.db,self.app,amount_minor=amount,**self.meta(self.manager)))

    def test_exact_lower_band_accepted(self):
        self.reviewed(); band = approved_band(self.db,self.interview["requisition_id"],self.clock)
        create_offer(self.db,self.app,amount_minor=band["band_min_minor"],**self.meta(self.manager))

    def test_exact_upper_band_accepted_at_creation(self):
        self.reviewed(); band = approved_band(self.db,self.interview["requisition_id"],self.clock)
        create_offer(self.db,self.app,amount_minor=band["band_max_minor"],**self.meta(self.manager))

    def test_currency_mismatch_and_noninteger_amount_rejected(self):
        self.reviewed(); band = approved_band(self.db,self.interview["requisition_id"],self.clock)
        other = "USD" if band["currency"]!="USD" else "INR"
        self.fails("CURRENCY_MISMATCH",lambda:create_offer(self.db,self.app,currency=other,**self.meta(self.manager)))
        self.fails("INVALID_AMOUNT",lambda:create_offer(self.db,self.app,amount_minor=True,**self.meta(self.manager)))

    def test_unapproved_requisition_and_mutated_compensation_rejected(self):
        self.reviewed()
        with self.db:
            self.db.execute("UPDATE Requisition SET status='draft' WHERE requisition_id=?", (self.interview["requisition_id"],))
        self.fails("REQUISITION_NOT_APPROVED",lambda:create_offer(self.db,self.app,**self.meta(self.manager)))
        with self.db:
            self.db.execute("UPDATE Requisition SET status='open',band_max_minor=band_max_minor+1 WHERE requisition_id=?", (self.interview["requisition_id"],))
        self.fails("COMPENSATION_SNAPSHOT_MISMATCH",lambda:create_offer(self.db,self.app,**self.meta(self.manager)))

    def test_invalid_offer_actor_and_application_stage_rejected(self):
        self.fails("APPLICATION_STAGE_INELIGIBLE",lambda:create_offer(self.db,self.app,**self.meta(self.manager)))
        self.reviewed()
        self.fails("ACTOR_UNAUTHORIZED",lambda:create_offer(self.db,self.app,**self.meta("STAFF-000003")))

    def test_duplicate_active_offer_rejected(self):
        self.offer()
        self.fails("INCOMPATIBLE_ACTIVE_OFFER",lambda:create_offer(self.db,self.app,**self.meta(self.manager)))

    def test_self_approval_and_unappointed_actor_rejected(self):
        self.reviewed()
        identity = create_offer(self.db,self.app,**self.meta())
        self.fails("SELF_APPROVAL_FORBIDDEN",lambda:submit_offer(self.db,identity,"STAFF-000002",**self.meta(self.manager)))
        submit_offer(self.db,identity,"STAFF-000004",**self.meta(self.manager))
        self.fails("APPROVER_UNAUTHORIZED",lambda:decide_offer(self.db,identity,True,**self.meta()))
        self.fails("ACTOR_UNAUTHORIZED",lambda:decide_offer(self.db,identity,True,**self.meta(self.manager)))

    def test_offer_rejection_audit_and_policy(self):
        identity,approval = self.pending(upper=True)
        self.fails("APPROVAL_POLICY_MISMATCH",lambda:decide_offer(self.db,identity,True,**self.meta()))
        self.assertEqual(decide_offer(self.db,identity,False,**self.meta()),"rejected")
        self.assertEqual(self.db.execute("SELECT status FROM Application WHERE application_id=?", (self.app,)).fetchone()[0],"rejected")
        self.assertEqual([r[0] for r in self.db.execute("SELECT new_status FROM ApprovalEvent WHERE approval_id=? ORDER BY sequence", (approval,))],["pending","rejected"])

    def test_approved_offer_end_to_end_audit_and_final_hired_state(self):
        identity,approval = self.accepted()
        self.assertEqual([r[0] for r in self.db.execute("SELECT new_status FROM OfferEvent WHERE offer_id=? ORDER BY sequence", (identity,))],["draft","pending_approval","approved","sent","accepted"])
        self.assertEqual([r[0] for r in self.db.execute("SELECT new_status FROM ApprovalEvent WHERE approval_id=? ORDER BY sequence", (approval,))],["pending","approved"])
        self.assertEqual(self.db.execute("SELECT status FROM Application WHERE application_id=?", (self.app,)).fetchone()[0],"hired")

    def test_direct_hired_and_accept_before_approval_rejected(self):
        identity = self.offer()
        self.fails("OFFER_OPERATION_REQUIRED",lambda:transition_application(self.db,self.app,"hired",**self.meta()))
        self.fails("OFFER_STATE_INVALID",lambda:accept_offer(self.db,identity,**self.meta()))

    def test_hiring_resolves_other_applications_and_active_scheduling(self):
        self.accepted()
        candidate = self.db.execute("SELECT candidate_id FROM Application WHERE application_id=?", (self.app,)).fetchone()[0]
        active = self.db.execute("SELECT COUNT(*) FROM Interview i JOIN Application a USING(application_id) WHERE a.candidate_id=? AND i.status='scheduled'", (candidate,)).fetchone()[0]
        self.assertEqual(active,0)
        self.fails("APPLICATION_STAGE_INELIGIBLE",lambda:schedule_interview(self.db,self.app,self.interview["panel_id"],self.interview["start_at"],self.interview["end_at"],**self.meta()))

    def test_post_hire_global_withdrawal_requires_explicit_future_policy(self):
        self.accepted()
        candidate = self.db.execute("SELECT candidate_id FROM Application WHERE application_id=?", (self.app,)).fetchone()[0]
        self.fails("POST_HIRE_POLICY_REQUIRED",lambda:withdraw_candidate(self.db,candidate,**self.meta()))

    def test_withdrawn_or_rejected_application_and_candidate_cannot_be_hired(self):
        identity,_ = self.pending()
        decide_offer(self.db,identity,True,**self.meta());send_offer(self.db,identity,**self.meta(self.manager))
        # Isolated malformed projections demonstrate guards; no anomaly artifact is generated.
        for status,code in (("withdrawn","APPLICATION_WITHDRAWN"),("rejected","APPLICATION_STAGE_INELIGIBLE")):
            with self.db:
                self.db.execute("UPDATE Application SET status=? WHERE application_id=?", (status,self.app))
            self.fails(code,lambda:accept_offer(self.db,identity,**self.meta()))
        with self.db:
            self.db.execute("UPDATE Application SET status='offer' WHERE application_id=?", (self.app,))
            self.db.execute("UPDATE Candidate SET status='withdrawn',withdrawn_at=? WHERE candidate_id=(SELECT candidate_id FROM Application WHERE application_id=?)", (self.clock,self.app))
        self.fails("CANDIDATE_WITHDRAWN",lambda:accept_offer(self.db,identity,**self.meta()))

    def test_exact_budget_limit_approval_and_expired_approval_rejection(self):
        self.reviewed();band = approved_band(self.db,self.interview["requisition_id"],self.clock)
        identity = create_offer(self.db,self.app,amount_minor=approval_limit(band),**self.meta(self.manager))
        approval = submit_offer(self.db,identity,"STAFF-000002",**self.meta(self.manager))
        with self.db:
            self.db.execute("UPDATE Approval SET valid_to=? WHERE approval_id=?", (self.clock+1,approval))
        self.fails("APPROVAL_INEFFECTIVE",lambda:decide_offer(self.db,identity,True,**self.meta()))
        with self.db:
            self.db.execute("UPDATE Approval SET valid_to=NULL WHERE approval_id=?", (approval,))
        self.assertEqual(decide_offer(self.db,identity,True,**self.meta()),"approved")

    def test_scorecard_partial_write_failure_rolls_back(self):
        before = dataset_digest(self.db)
        with patch("yottaflex.evaluation._append_event",side_effect=RuntimeError("injected event failure")),self.assertRaises(RuntimeError):
            create_scorecard(self.db,self.interview["interview_id"],self.reviewers[0],**self.meta(self.reviewers[0]))
        self.assertEqual(dataset_digest(self.db),before)

    def test_offer_partial_write_failure_rolls_back(self):
        self.reviewed(); before = dataset_digest(self.db)
        with patch("yottaflex.offers._app_change",side_effect=RuntimeError("injected stage failure")),self.assertRaises(RuntimeError):
            create_offer(self.db,self.app,**self.meta(self.manager))
        self.assertEqual(dataset_digest(self.db),before)

    def test_approval_and_hire_partial_failures_roll_back_all_entities(self):
        identity,_ = self.pending(); before = dataset_digest(self.db)
        with patch("yottaflex.offers._offer_change",side_effect=RuntimeError("injected offer failure")),self.assertRaises(RuntimeError):
            decide_offer(self.db,identity,True,**self.meta())
        self.assertEqual(dataset_digest(self.db),before)
        decide_offer(self.db,identity,True,**self.meta());send_offer(self.db,identity,**self.meta(self.manager))
        before = dataset_digest(self.db)
        with patch("yottaflex.offers._offer_change",side_effect=RuntimeError("injected hire failure")),self.assertRaises(RuntimeError):
            accept_offer(self.db,identity,**self.meta())
        self.assertEqual(dataset_digest(self.db),before)

    def test_event_time_backdating_and_evidence_tampering_cannot_review(self):
        for reviewer in self.reviewers:
            self.card(reviewer)
        self.fails("EVENT_TIME_INVALID",lambda:review_application(self.db,self.app,actor_id="STAFF-000002",when=GenerationConfig().logical_origin+151*DAY,reason_code="BACKDATE"))
        with self.db:
            self.db.execute("UPDATE ScorecardItem SET score_value=4 WHERE scorecard_id=(SELECT MIN(scorecard_id) FROM Scorecard)")
        self.fails("REVIEW_GATE_INCOMPLETE",lambda:review_application(self.db,self.app,**self.meta()))

    def test_score_offer_approval_events_are_immutable(self):
        self.accepted()
        for table in ("ScorecardEvent","OfferEvent","ApprovalEvent"):
            for sql in (f'UPDATE "{table}" SET reason_code="changed"',f'DELETE FROM "{table}"'):
                with self.assertRaises(sqlite3.IntegrityError),self.db:
                    self.db.execute(sql)


if __name__=="__main__":
    unittest.main()
