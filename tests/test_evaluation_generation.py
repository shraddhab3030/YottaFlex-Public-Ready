"""Full Phase05 generation/replay and independent semantic corruption checks."""
from contextlib import closing
from itertools import zip_longest
import json
from pathlib import Path
import tempfile
import unittest

from yottaflex.canonical import dataset_digest, ordered_records, table_names
from yottaflex.db import connect
from yottaflex.evaluation_checks import validate_evaluations
from yottaflex.generate import generate_database
from yottaflex.generation_config import GenerationConfig
from yottaflex.workflow_checks import conflict_counts, validate_workflow

ROOT = Path(__file__).resolve().parents[1]


class EvaluationGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="yottaflex-phase05-generation-")
        cls.directory = Path(cls.workspace.name)
        cls.paths,cls.results = {},{}
        try:
            for profile in ("starter","full"):
                cls.paths[profile] = [cls.directory/f"{profile}-{i}.sqlite3" for i in (1,2)]
                cls.results[profile] = [generate_database(path,GenerationConfig(profile),phase="evaluations") for path in cls.paths[profile]]
        except BaseException:
            cls.workspace.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def test_starter_full_parent_interview_counts_and_real_core_entities(self):
        for profile,expected in (("starter",(10,100,160,40)),("full",(200,5000,8000,2000))):
            result = self.results[profile][0]
            self.assertEqual(tuple(result.summary["counts"][key] for key in ("Requisition","Candidate","Application","Interview")),expected)
            self.assertGreater(result.summary["counts"]["Scorecard"],0)
            self.assertGreater(result.summary["counts"]["Offer"],0)
            self.assertTrue(result.summary["master_preserved"])
            self.assertTrue(result.summary["validation"]["passed"])
            self.assertTrue(all(check["violations"]==0 for check in result.summary["validation"]["checks"]))

    def test_two_independent_runs_every_ordered_row_hash_count_and_decision(self):
        for profile in ("starter","full"):
            left_result,right_result = self.results[profile]
            self.assertEqual(left_result.summary,right_result.summary)
            self.assertEqual(left_result.canonical,right_result.canonical)
            with closing(connect(self.paths[profile][0])) as left,closing(connect(self.paths[profile][1])) as right:
                sentinel = object()
                for table in table_names(left):
                    for a,b in zip_longest(ordered_records(left,table),ordered_records(right,table),fillvalue=sentinel):
                        self.assertIsNot(a,sentinel);self.assertIsNot(b,sentinel)
                        self.assertEqual(tuple(a),tuple(b),(profile,table))

    def test_old_generation_modes_match_archived_master_and_workflow_digests(self):
        previous = {phase:json.loads((ROOT/f"docs/{phase}/reproducibility-evidence.json").read_text()) for phase in ("phase03","phase04")}
        for profile in ("starter","full"):
            result = self.results[profile][0]
            for phase,key in (("phase03","phase03_canonical"),("phase04","phase04_canonical")):
                self.assertEqual(result.summary[key],previous[phase]["profiles"][profile]["runs"][0]["canonical"])
            self.assertEqual(result.summary["schema_version"],2)

    def test_real_drafts_incomplete_submitted_approved_rejected_hired_variety(self):
        for profile in ("starter","full"):
            stats = self.results[profile][0].summary["evaluation"]["statistics"]
            self.assertTrue(all(stats["scorecard_statuses"][key]>0 for key in ("draft","incomplete","submitted")))
            self.assertTrue(all(stats["offer_approval_statuses"][key]>0 for key in ("approved","rejected")))
            self.assertGreater(stats["review_transitions"],0)
            self.assertGreater(stats["hired_transitions"],0)
            codes = {row["code"] for row in self.results[profile][0].summary["evaluation"]["rejected_examples"]}
            self.assertEqual(codes,{"DUPLICATE_SCORECARD","REVIEW_GATE_INCOMPLETE","SCORECARD_INCOMPLETE","OFFER_OUTSIDE_BAND"})

    def test_every_total_recomputed_independently_and_amounts_within_snapshot(self):
        for profile in ("starter","full"):
            with closing(connect(self.paths[profile][0])) as db:
                for row in db.execute("""SELECT s.scorecard_id,s.total_score_milli,SUM(i.score_value*r.weight_basis_points) weighted
                    FROM Scorecard s JOIN ScorecardItem i USING(scorecard_id) JOIN SkillRequirement r USING(skill_requirement_id)
                    WHERE s.status='submitted' GROUP BY s.scorecard_id"""):
                    self.assertEqual(row["total_score_milli"],(row["weighted"]*1000+5000)//10000)
                invalid = db.execute("""SELECT COUNT(*) FROM Offer o JOIN RequisitionEvent e ON e.event_id=o.approved_requisition_event_id
                    WHERE o.currency<>e.currency OR o.amount_minor<e.band_min_minor OR o.amount_minor>e.band_max_minor""").fetchone()[0]
                self.assertEqual(invalid,0)
                self.assertTrue(all(value==0 for value in conflict_counts(db).values()))

    def test_phase05_validator_detects_actual_semantic_corruption_without_masking(self):
        with closing(connect(self.paths["starter"][0])) as db:
            original = dataset_digest(db)
            changes = ["UPDATE Scorecard SET total_score_milli=1 WHERE status='submitted'",
                "UPDATE ScorecardItem SET weight_basis_points=1 WHERE scorecard_id=(SELECT MIN(scorecard_id) FROM Scorecard)",
                "UPDATE Offer SET amount_minor=(SELECT band_max_minor+1 FROM RequisitionEvent e WHERE e.event_id=Offer.approved_requisition_event_id)",
                "UPDATE Approval SET approver_staff_id='STAFF-000003' WHERE offer_id IS NOT NULL",
                "UPDATE Application SET status='hired' WHERE application_id=(SELECT MIN(application_id) FROM Application WHERE status='applied')",
                "UPDATE Scorecard SET rubric_version=2 WHERE status='submitted'",
                "UPDATE Offer SET status='accepted' WHERE status='rejected'"]
            for sql in changes:
                db.execute("SAVEPOINT corrupt")
                try:
                    db.execute(sql)
                    result = validate_evaluations(db,GenerationConfig(),40)
                    self.assertFalse(result["passed"],sql)
                    self.assertTrue(any(check["violations"] for check in result["checks"]))
                finally:
                    db.execute("ROLLBACK TO corrupt");db.execute("RELEASE corrupt")
            self.assertEqual(dataset_digest(db),original)

    def test_workflow_only_validation_stays_strict_and_advanced_validation_passes(self):
        with closing(connect(self.paths["starter"][0])) as db:
            self.assertFalse(validate_workflow(db,GenerationConfig(),40)["passed"])
            self.assertTrue(validate_evaluations(db,GenerationConfig(),40)["passed"])
            self.assertEqual(list(db.execute("PRAGMA foreign_key_check")),[])

    def test_existing_phase05_output_never_overwritten(self):
        target = self.paths["starter"][0]
        original = target.read_bytes()
        with self.assertRaises(FileExistsError):
            generate_database(target,GenerationConfig(),phase="evaluations")
        self.assertEqual(target.read_bytes(),original)


if __name__=="__main__":
    unittest.main()
