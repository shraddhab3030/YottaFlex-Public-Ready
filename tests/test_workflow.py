"""Isolated transactional lifecycle, conflicts, history and writer-race checks."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
from threading import Barrier
import unittest
from unittest.mock import patch

from yottaflex.canonical import dataset_digest
from yottaflex.db import connect
from yottaflex.generate import generate_database
from yottaflex.generation_checks import role_details
from yottaflex.generation_config import DAY, GenerationConfig
from yottaflex.workflow import (DomainError, cancel_interview, complete_interview,
    reschedule_interview, schedule_interview, transition_application,
    withdraw_application, withdraw_candidate)
from yottaflex.workflow_checks import _history_errors, conflict_counts


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="yottaflex-workflow-tests-")
        cls.directory = Path(cls.workspace.name)
        cls.base = cls.directory/"master.sqlite3"
        generate_database(cls.base,GenerationConfig())

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def setUp(self):
        self.db = connect()
        self.addCleanup(self.db.close)
        with closing(connect(self.base)) as source:
            source.backup(self.db)
        origin = GenerationConfig().logical_origin
        self.clock = origin+151*DAY
        self.start = origin+160*DAY+9*3600
        self.finish = origin+190*DAY
        self.actor = "STAFF-000002"
        pair = self.db.execute("""SELECT a.application_id x,b.application_id y FROM Application a JOIN Application b
            ON a.candidate_id=b.candidate_id AND a.requisition_id<b.requisition_id ORDER BY a.application_id,b.application_id LIMIT 1""").fetchone()
        self.a,self.b = pair
        self.apps = {identity:dict(self.db.execute("SELECT * FROM Application WHERE application_id=?", (identity,)).fetchone()) for identity in pair}
        self.c = self.db.execute("SELECT application_id FROM Application WHERE requisition_id=? AND candidate_id<>? ORDER BY application_id LIMIT 1",
            (self.apps[self.a]["requisition_id"],self.apps[self.a]["candidate_id"])).fetchone()[0]
        with self.db:
            for number in range(101,107):
                self.db.execute("INSERT INTO Staff VALUES (?,?,'interviewer','active',?,?)",
                    (f"STAFF-{number:06d}",f"Synthetic test interviewer {number}",origin+150*DAY,self.finish))
                self.db.execute("INSERT INTO Availability VALUES (?,?,?,?, 'available')",
                    (f"AVAIL-{number:06d}",f"STAFF-{number:06d}",self.start,self.start+8*3600))
            for index,app in enumerate((self.a,self.b),1):
                req = self.db.execute("SELECT * FROM Requisition WHERE requisition_id=?", (self.apps[app]["requisition_id"],)).fetchone()
                role,_,_ = role_details(req["title"])
                panel = f"PANEL-{index:06d}"
                self.db.execute("INSERT INTO InterviewPanel VALUES (?,?,?,'active',?,?)",
                    (panel,req["requisition_id"],"technical:"+role[0],origin+150*DAY,self.finish))
                for number in range(101,104):
                    self.db.execute("INSERT INTO PanelMember VALUES (?,?,?,?,'active')", (panel,f"STAFF-{number:06d}",origin+150*DAY,self.finish))

    def meta(self, **overrides):
        self.clock += 1
        return dict(actor_id=self.actor,when=self.clock,reason_code="TEST_DECISION",**overrides)

    def screen(self, app):
        transition_application(self.db,app,"screening",**self.meta())

    def book(self, app=None, panel="PANEL-000001", start=None, duration=1800):
        app = app or self.a
        status = self.db.execute("SELECT status FROM Application WHERE application_id=?", (app,)).fetchone()[0]
        if status == "applied":
            self.screen(app)
        start = self.start if start is None else start
        return schedule_interview(self.db,app,panel,start,start+duration,**self.meta())

    def fails(self, code, operation):
        before = dataset_digest(self.db)
        with self.assertRaises(DomainError) as error:
            operation()
        self.assertEqual(error.exception.code,code)
        self.assertEqual(dataset_digest(self.db),before,"Rejected operation changed persistent state")
        self.assertFalse(self.db.in_transaction)

    def separate_b_panel(self):
        with self.db:
            self.db.execute("DELETE FROM PanelMember WHERE panel_id='PANEL-000002'")
            for number in range(104,107):
                self.db.execute("INSERT INTO PanelMember VALUES ('PANEL-000002',?,?,?,'active')",
                    (f"STAFF-{number:06d}",GenerationConfig().logical_origin+150*DAY,self.finish))

    def test_eligible_schedule_creates_projection_participants_and_linked_events(self):
        identity = self.book()
        self.assertEqual(identity,"INT-2026-000001")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM InterviewParticipant").fetchone()[0],3)
        self.assertEqual(self.db.execute("SELECT status FROM Application WHERE application_id=?", (self.a,)).fetchone()[0],"interviewing")
        self.assertEqual(sum(_history_errors(self.db).values()),0)
        self.assertTrue(all(n==0 for n in conflict_counts(self.db).values()))

    def test_unapproved_requisition_rejected(self):
        self.screen(self.a)
        with self.db:
            self.db.execute("UPDATE Requisition SET status='draft' WHERE requisition_id=?", (self.apps[self.a]["requisition_id"],))
        self.fails("REQUISITION_NOT_APPROVED",lambda:self.book())

    def test_missing_causal_approval_rejected(self):
        self.screen(self.a)
        with self.db:
            self.db.execute("UPDATE Approval SET status='rejected' WHERE requisition_id=?", (self.apps[self.a]["requisition_id"],))
        self.fails("REQUISITION_NOT_APPROVED",lambda:self.book())

    def test_missing_application_rejected(self):
        self.fails("APPLICATION_NOT_FOUND",lambda:schedule_interview(self.db,"missing","PANEL-000001",self.start,self.start+1800,**self.meta()))

    def test_withdrawn_application_rejected(self):
        withdraw_application(self.db,self.a,**self.meta())
        self.fails("APPLICATION_WITHDRAWN",lambda:self.book())

    def test_candidate_withdrawal_prevents_screening_and_scheduling(self):
        result = withdraw_candidate(self.db,self.apps[self.a]["candidate_id"],**self.meta())
        self.assertIn(self.a,result["applications"])
        self.fails("APPLICATION_WITHDRAWN",lambda:self.book())

    def test_panel_requisition_mismatch_rejected(self):
        self.screen(self.a)
        self.fails("PANEL_REQUISITION_MISMATCH",lambda:self.book(panel="PANEL-000002"))

    def test_unavailable_interviewer_rejected(self):
        self.screen(self.a)
        self.fails("INTERVIEWER_UNAVAILABLE",lambda:self.book(start=self.start+8*3600))

    def test_blocked_calendar_overrides_available(self):
        self.screen(self.a)
        with self.db:
            self.db.execute("INSERT INTO Availability VALUES ('AVAIL-999999','STAFF-000101',?,?,'blocked')", (self.start+900,self.start+1800))
        self.fails("INTERVIEWER_UNAVAILABLE",lambda:self.book())

    def test_interviewer_overlap_rejected_across_applications(self):
        self.book()
        self.screen(self.c)
        self.fails("INTERVIEWER_CONFLICT",lambda:self.book(self.c,start=self.start+900))

    def test_back_to_back_bookings_and_exact_available_end_accepted(self):
        self.book()
        self.book(self.c,start=self.start+1800)
        self.book(self.c,start=self.start+8*3600-1800)
        self.assertTrue(all(n==0 for n in conflict_counts(self.db).values()))

    def test_candidate_overlap_rejected_even_with_disjoint_interviewers(self):
        self.separate_b_panel()
        self.book()
        self.screen(self.b)
        self.fails("CANDIDATE_CONFLICT",lambda:self.book(self.b,panel="PANEL-000002"))

    def test_effective_membership_boundary_and_adjacent_coverage(self):
        self.screen(self.a)
        with self.db:
            self.db.execute("UPDATE PanelMember SET valid_to=? WHERE panel_id='PANEL-000001'", (self.start+900,))
        self.fails("MEMBERSHIP_INEFFECTIVE",lambda:self.book())
        with self.db:
            for number in range(101,104):
                self.db.execute("INSERT INTO PanelMember VALUES ('PANEL-000001',?,?,?,'active')", (f"STAFF-{number:06d}",self.start+900,self.finish))
        self.book()

    def test_panel_and_staff_effective_end_exclusive(self):
        self.screen(self.a)
        with self.db:
            self.db.execute("UPDATE InterviewPanel SET valid_to=? WHERE panel_id='PANEL-000001'", (self.start,))
        self.fails("PANEL_INEFFECTIVE",lambda:self.book())
        with self.db:
            self.db.execute("UPDATE InterviewPanel SET valid_to=? WHERE panel_id='PANEL-000001'", (self.finish,))
            self.db.execute("UPDATE Staff SET valid_to=? WHERE staff_id='STAFF-000101'", (self.start,))
        self.fails("INTERVIEWER_INELIGIBLE",lambda:self.book())

    def test_overlapping_duplicate_membership_rejected(self):
        self.screen(self.a)
        with self.db:
            self.db.execute("INSERT INTO PanelMember VALUES ('PANEL-000001','STAFF-000101',?,?,'active')", (self.start,self.finish))
        self.fails("PANEL_MEMBERSHIP_OVERLAP",lambda:self.book())

    def test_invalid_interval_values_rejected_atomically(self):
        self.screen(self.a)
        for start,end in ((self.start,self.start),(self.start,self.start-1),(self.start,self.start+60),(float(self.start),self.start+1800),(True,self.start+1800)):
            self.fails("INVALID_INTERVAL",lambda:schedule_interview(self.db,self.a,"PANEL-000001",start,end,**self.meta()))

    def test_reschedule_same_id_old_schedule_and_immutable_assignment_preserved(self):
        identity = self.book()
        before = [tuple(r) for r in self.db.execute("SELECT * FROM InterviewParticipant")]
        result = reschedule_interview(self.db,identity,self.start+900,self.start+2700,**self.meta())
        self.assertEqual(result,identity)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM Interview").fetchone()[0],1)
        self.assertEqual([tuple(r) for r in self.db.execute("SELECT * FROM InterviewParticipant")],before)
        events = list(self.db.execute("SELECT * FROM InterviewEvent ORDER BY sequence"))
        self.assertEqual([r["event_type"] for r in events],["created","rescheduled"])
        self.assertEqual(json.loads(events[1]["snapshot_json"])["before"]["start_at"],self.start)
        self.assertEqual(sum(_history_errors(self.db).values()),0)

    def test_reschedule_conflict_is_atomic(self):
        identity = self.book()
        self.book(self.c,start=self.start+1800)
        self.fails("INTERVIEWER_CONFLICT",lambda:reschedule_interview(self.db,identity,self.start+1800,self.start+3600,**self.meta()))

    def test_reschedule_rechecks_original_member_effectivity(self):
        identity = self.book()
        with self.db:
            self.db.execute("UPDATE PanelMember SET valid_to=? WHERE panel_id='PANEL-000001'", (self.start+1800,))
        self.fails("MEMBERSHIP_INEFFECTIVE",lambda:reschedule_interview(self.db,identity,self.start+1800,self.start+3600,**self.meta()))

    def test_reschedule_noop_and_started_interview_rejected(self):
        identity = self.book()
        self.fails("NO_SCHEDULE_CHANGE",lambda:reschedule_interview(self.db,identity,self.start,self.start+1800,**self.meta()))
        self.clock = self.start
        self.fails("INTERVIEW_STARTED",lambda:reschedule_interview(self.db,identity,self.start+3600,self.start+5400,**self.meta()))

    def test_cancel_releases_capacity_and_preserves_participants(self):
        identity = self.book()
        cancel_interview(self.db,identity,**self.meta())
        self.book(self.c)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM InterviewParticipant WHERE interview_id=?", (identity,)).fetchone()[0],3)
        self.fails("INTERVIEW_STATE_INVALID",lambda:cancel_interview(self.db,identity,**self.meta()))

    def test_application_withdrawal_cancels_all_scheduled_and_releases_capacity(self):
        identities = [self.book(),self.book(start=self.start+1800)]
        result = withdraw_application(self.db,self.a,**self.meta())
        self.assertEqual(result,identities)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM Interview WHERE status='scheduled'").fetchone()[0],0)
        self.book(self.c)
        self.assertEqual(sum(_history_errors(self.db).values()),0)

    def test_global_withdrawal_cancels_all_applications_atomically(self):
        identities = [self.book(),self.book(self.b,"PANEL-000002",self.start+1800)]
        result = withdraw_candidate(self.db,self.apps[self.a]["candidate_id"],**self.meta())
        self.assertEqual(sorted(result["cancelled_interviews"]),identities)
        self.assertIn(self.a,result["applications"])
        self.assertIn(self.b,result["applications"])
        self.assertEqual(sum(_history_errors(self.db).values()),0)

    def test_withdrawal_retains_completed_history(self):
        identity = self.book()
        self.clock = self.start+1800
        complete_interview(self.db,identity,**self.meta())
        historical = [tuple(r) for r in self.db.execute("SELECT * FROM InterviewEvent")]
        withdraw_application(self.db,self.a,**self.meta())
        self.assertEqual(self.db.execute("SELECT status FROM Interview").fetchone()[0],"completed")
        self.assertEqual([tuple(r) for r in self.db.execute("SELECT * FROM InterviewEvent")],historical)
        self.assertEqual(sum(_history_errors(self.db).values()),0)

    def test_completion_requires_actual_end_and_authorized_participant(self):
        identity = self.book()
        self.fails("INTERVIEW_NOT_ENDED",lambda:complete_interview(self.db,identity,**self.meta()))
        self.clock = self.start+1800
        metadata = self.meta(); metadata["actor_id"] = "STAFF-000101"
        complete_interview(self.db,identity,**metadata)
        self.assertEqual(self.db.execute("SELECT status FROM Interview").fetchone()[0],"completed")

    def test_illegal_transition_and_direct_stage_bypass_rejected(self):
        self.fails("INVALID_TRANSITION",lambda:transition_application(self.db,self.a,"hired",**self.meta()))
        self.screen(self.a)
        self.fails("INTERVIEW_REQUIRED",lambda:transition_application(self.db,self.a,"interviewing",**self.meta()))

    def test_review_gate_blocks_missing_and_incomplete_evaluations(self):
        identity = self.book()
        self.fails("REVIEW_GATE_INCOMPLETE",lambda:transition_application(self.db,self.a,"reviewed",**self.meta()))
        self.clock = self.start+1800
        complete_interview(self.db,identity,**self.meta())
        self.fails("REVIEW_GATE_INCOMPLETE",lambda:transition_application(self.db,self.a,"reviewed",**self.meta()))
        # A malformed/incomplete future scorecard is only an isolated gate fixture.
        # No scorecard generation/collection operation exists in this phase.
        with self.db:
            self.db.execute("INSERT INTO Scorecard VALUES (?,?,?,1,'incomplete',NULL,?,NULL)",
                (f"SCORE-{identity}-STAFF-000101",identity,"STAFF-000101",self.clock))
        self.fails("REVIEW_GATE_INCOMPLETE",lambda:transition_application(self.db,self.a,"reviewed",**self.meta()))

    def test_authorization_and_metadata_rejected(self):
        for overrides,code in (({"actor_id":"STAFF-000003"},"ACTOR_UNAUTHORIZED"),({"reason_code":" "},"METADATA_REQUIRED"),({"when":True},"INVALID_TIMESTAMP")):
            metadata = self.meta(); metadata.update(overrides)
            self.fails(code,lambda:transition_application(self.db,self.a,"screening",**metadata))

    def test_event_and_participant_mutation_and_replace_are_prevented(self):
        identity = self.book()
        for sql in ("UPDATE InterviewParticipant SET assignment_role='observer'", "DELETE FROM InterviewParticipant", "UPDATE InterviewEvent SET reason_code='changed'", "DELETE FROM InterviewEvent"):
            before = dataset_digest(self.db)
            with self.assertRaises(sqlite3.IntegrityError),self.db:
                self.db.execute(sql)
            self.assertEqual(dataset_digest(self.db),before)
        row = tuple(self.db.execute("SELECT * FROM InterviewParticipant WHERE interview_id=? LIMIT 1", (identity,)).fetchone())
        with self.assertRaises(sqlite3.IntegrityError),self.db:
            self.db.execute("INSERT OR REPLACE INTO InterviewParticipant VALUES (?,?,?,?)",row)

    def test_injected_failure_after_writes_rolls_back_every_projection_and_event(self):
        self.screen(self.a)
        before = dataset_digest(self.db)
        with patch("yottaflex.workflow._app_change",side_effect=RuntimeError("failure after interview writes")):
            with self.assertRaises(RuntimeError):
                self.book()
        self.assertEqual(dataset_digest(self.db),before)

    def test_global_withdrawal_failure_rolls_back_all_children(self):
        self.book()
        self.book(self.b,"PANEL-000002",self.start+1800)
        before = dataset_digest(self.db)
        from yottaflex import workflow
        original = workflow._withdraw_app
        calls = 0
        def fail_second(*args,**kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("injected second application failure")
            return original(*args,**kwargs)
        with patch("yottaflex.workflow._withdraw_app",side_effect=fail_second),self.assertRaises(RuntimeError):
            withdraw_candidate(self.db,self.apps[self.a]["candidate_id"],**self.meta())
        self.assertEqual(dataset_digest(self.db),before)

    def test_two_concurrent_writers_cannot_double_book(self):
        self.screen(self.a); self.screen(self.c)
        with tempfile.TemporaryDirectory(prefix="yottaflex-lock-test-") as directory:
            target = Path(directory)/"race.sqlite3"
            with closing(connect(target)) as destination:
                self.db.backup(destination)
            barrier = Barrier(2)
            when = self.clock+1
            def contender(app):
                with closing(connect(target)) as connection:
                    barrier.wait(timeout=5)
                    try:
                        return schedule_interview(connection,app,"PANEL-000001",self.start,self.start+1800,
                            actor_id=self.actor,when=when,reason_code="CONCURRENT_TEST")
                    except DomainError as error:
                        return error.code
            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(contender,(self.a,self.c)))
            self.assertEqual(sorted(results),["INT-2026-000001","INTERVIEWER_CONFLICT"])
            with closing(connect(target)) as db:
                self.assertTrue(all(n==0 for n in conflict_counts(db).values()))
                self.assertEqual(sum(_history_errors(db).values()),0)


if __name__ == "__main__":
    unittest.main()
