"""Actual starter/full workflow replay, validation and capacity failure evidence."""

from contextlib import closing
from itertools import zip_longest
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from yottaflex.canonical import dataset_digest, ordered_records, table_names
from yottaflex.db import connect
from yottaflex.generate import generate_database
from yottaflex.generation_checks import validate_generated
from yottaflex.generation_config import GenerationConfig
from yottaflex.interview_generation import SchedulingConfig
from yottaflex.matching import load_matching_inputs, skill_fit
from yottaflex.workflow import DomainError
from yottaflex.workflow_checks import validate_workflow


ROOT = Path(__file__).resolve().parents[1]


class InterviewGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="yottaflex-interview-generation-")
        cls.directory = Path(cls.workspace.name)
        cls.paths,cls.results = {},{}
        try:
            for profile in ("starter","full"):
                cls.paths[profile] = [cls.directory/f"{profile}-{index}.sqlite3" for index in (1,2)]
                cls.results[profile] = [generate_database(path,GenerationConfig(profile),phase="interviews") for path in cls.paths[profile]]
        except BaseException:
            cls.workspace.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def test_exact_40_and_2000_master_counts_preserved_all_checks_zero(self):
        for profile,target,counts in (("starter",40,(10,100,160)),("full",2000,(200,5000,8000))):
            result = self.results[profile][0]
            self.assertEqual(tuple(result.summary["counts"][name] for name in ("Requisition","Candidate","Application")),counts)
            self.assertEqual(result.summary["counts"]["Interview"],target)
            self.assertTrue(result.summary["master_preserved"])
            self.assertTrue(result.summary["validation"]["passed"])
            self.assertTrue(all(item["violations"]==0 for item in result.summary["validation"]["checks"]))
            self.assertTrue(all(value==0 for value in result.summary["scheduling"]["statistics"]["conflicts"].values()))
            self.assertGreater(result.timings["scheduling_seconds"],0)
            self.assertGreater(result.timings["validation_seconds"],0)

    def test_two_independent_replays_every_row_count_table_hash_and_aggregate(self):
        for profile in ("starter","full"):
            left_result,right_result = self.results[profile]
            self.assertEqual(left_result.canonical,right_result.canonical)
            self.assertEqual(left_result.summary,right_result.summary)
            with closing(connect(self.paths[profile][0])) as left,closing(connect(self.paths[profile][1])) as right:
                sentinel = object()
                for table in table_names(left):
                    for a,b in zip_longest(ordered_records(left,table),ordered_records(right,table),fillvalue=sentinel):
                        self.assertIsNot(a,sentinel)
                        self.assertIsNot(b,sentinel)
                        self.assertEqual(tuple(a),tuple(b),(profile,table))

    def test_original_phase03_master_digest_and_schema_unchanged(self):
        previous = json.loads((ROOT/"docs/phase03/reproducibility-evidence.json").read_text())
        for profile in ("starter","full"):
            self.assertEqual(self.results[profile][0].summary["phase03_canonical"],previous["profiles"][profile]["runs"][0]["canonical"])
            self.assertEqual(self.results[profile][0].summary["schema_version"],2)

    def test_variations_have_real_history_no_fake_scores_and_distinct_attempt_counts(self):
        for profile in ("starter","full"):
            summary = self.results[profile][0].summary
            operations = summary["scheduling"]
            self.assertEqual(operations["attempts"]["schedule"],operations["target"]+1)
            self.assertEqual(operations["successful_operations"]["schedule"],operations["target"])
            for operation in ("reschedule","application_withdraw","candidate_withdraw","complete","direct_cancel"):
                self.assertGreater(operations["successful_operations"][operation],0)
            self.assertEqual({r["code"] for r in operations["rejected_examples"]},{"REVIEW_GATE_INCOMPLETE","INTERVIEWER_CONFLICT"})
            for table in ("Scorecard","ScorecardItem","ScorecardEvent","Offer","OfferEvent"):
                self.assertEqual(summary["counts"][table],0)
            self.assertGreater(len(operations["statistics"]["schedule_dates_utc"]),5)
            self.assertEqual(set(operations["statistics"]["durations_seconds"]),{"1800","2700","3600"})

    def test_weak_applications_remain_initial_stage(self):
        for profile in ("starter","full"):
            with closing(connect(self.paths[profile][0])) as db:
                candidates,requirements = load_matching_inputs(db)
                weak_applied = sum(row["status"]=="applied" and skill_fit(requirements[row["requisition_id"]],candidates[row["candidate_id"]]).category=="weak"
                    for row in db.execute("SELECT * FROM Application"))
                self.assertGreater(weak_applied,0)

    def test_master_and_workflow_validation_are_distinct(self):
        with closing(connect(self.paths["starter"][0])) as db:
            self.assertFalse(validate_generated(db,GenerationConfig())["passed"])
            self.assertTrue(validate_workflow(db,GenerationConfig(),40)["passed"])

    def test_workflow_validator_detects_semantic_corruption(self):
        with closing(connect(self.paths["starter"][0])) as db:
            original = dataset_digest(db)
            changes = ["UPDATE Application SET status='reviewed' WHERE application_id=(SELECT MIN(application_id) FROM Application WHERE status='interviewing')",
                "UPDATE Interview SET start_at=start_at+1 WHERE interview_id='INT-2026-000001'",
                "UPDATE Availability SET status='cancelled' WHERE status='available'",
                "UPDATE PanelMember SET valid_to=valid_from+1",
                "UPDATE Candidate SET status='withdrawn',withdrawn_at=created_at WHERE candidate_id=(SELECT a.candidate_id FROM Interview i JOIN Application a USING(application_id) WHERE i.status='scheduled' LIMIT 1)"]
            for sql in changes:
                db.execute("SAVEPOINT corruption")
                try:
                    db.execute(sql)
                    self.assertFalse(validate_workflow(db,GenerationConfig(),40)["passed"],sql)
                finally:
                    db.execute("ROLLBACK TO corruption")
                    db.execute("RELEASE corruption")
            self.assertEqual(dataset_digest(db),original)

    def test_insufficient_fixed_capacity_fails_without_publishing_or_expanding(self):
        target = self.directory/"insufficient.sqlite3"
        with self.assertRaises(DomainError) as error:
            generate_database(target,GenerationConfig(),phase="interviews",
                scheduling=SchedulingConfig(40,working_days=1,interviewer_count=3,start_hour=9,end_hour=10))
        self.assertEqual(error.exception.code,"INSUFFICIENT_CAPACITY")
        self.assertIn("no calendar expansion",str(error.exception))
        self.assertFalse(target.exists())
        self.assertEqual(list(self.directory.glob(".yottaflex-generation-*")),[])

    def test_starter_target_configurable_full_fixed_and_invalid_inputs_refused(self):
        result = generate_database(self.directory/"configured.sqlite3",GenerationConfig(),phase="interviews",scheduling=SchedulingConfig(17))
        self.assertEqual(result.summary["counts"]["Interview"],17)
        for options,config in ((SchedulingConfig(0),GenerationConfig()),(SchedulingConfig(2001),GenerationConfig("full")),
                               (SchedulingConfig(40,working_days=21),GenerationConfig()),(SchedulingConfig(40,interviewer_count=2),GenerationConfig())):
            with self.assertRaises(ValueError):
                options.validate_for(config)

    def test_different_hash_seed_and_working_directory_preserve_workflow(self):
        environment = dict(os.environ,PYTHONPATH=str(ROOT/"src"),PYTHONHASHSEED="8792")
        result = subprocess.run([sys.executable,"-m","yottaflex.generate","--profile","starter","--phase","interviews",
            "--database",str(self.directory/"hash-seed.sqlite3")],cwd=self.directory,env=environment,text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(result.stdout)["canonical"],self.results["starter"][0].canonical)


if __name__ == "__main__":
    unittest.main()
