"""Actual small/full generation, independent replay and focused failure tests."""

from contextlib import closing
from itertools import zip_longest
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from yottaflex.canonical import dataset_digest, ordered_records, stable_json, table_names
from yottaflex.db import connect
from yottaflex.generate import generate_database, normalized_weights
from yottaflex.generation_checks import DEFERRED_TABLES, generation_summary, validate_generated
from yottaflex.generation_config import GenerationConfig, PROFILES, Scale, SKILLS
from yottaflex.ids import application_id, numbered_id, valid_numbered_id
from yottaflex.matching import load_matching_inputs, skill_fit


ROOT = Path(__file__).resolve().parents[1]


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="yottaflex-generation-tests-")
        cls.directory = Path(cls.workspace.name)
        cls.paths, cls.results = {}, {}
        try:
            for profile in ("starter","full"):
                cls.paths[profile], cls.results[profile] = [], []
                for index in (1,2):
                    path = cls.directory/f"{profile}-{index}.sqlite3"
                    cls.paths[profile].append(path)
                    cls.results[profile].append(generate_database(path,GenerationConfig(profile=profile)))
        except BaseException:
            cls.workspace.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def test_exact_starter_and_full_counts_same_generator(self):
        for profile, scale in PROFILES.items():
            for result in self.results[profile]:
                with self.subTest(profile=profile):
                    self.assertEqual(result.summary["counts"]["Requisition"],scale.requisitions)
                    self.assertEqual(result.summary["counts"]["Candidate"],scale.candidates)
                    self.assertEqual(result.summary["counts"]["Application"],scale.applications)
                    self.assertEqual(result.summary["counts"]["SkillRequirement"],4*scale.requisitions)
                    self.assertEqual(result.summary["approved_requisitions"],scale.requisitions)

    def test_every_generated_pk_fk_and_required_field_valid(self):
        for profile in PROFILES:
            with closing(connect(self.paths[profile][0])) as db:
                validation = validate_generated(db,GenerationConfig(profile=profile))
                self.assertTrue(validation["passed"],validation)
                self.assertTrue(all(item["violations"]==0 for item in validation["checks"]))
                self.assertEqual(list(db.execute("PRAGMA foreign_key_check")),[])
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")

    def test_unique_application_pairs_and_exact_composite_identities(self):
        for profile in PROFILES:
            with closing(connect(self.paths[profile][0])) as db:
                rows = list(db.execute("SELECT application_id,candidate_id,requisition_id FROM Application ORDER BY application_id"))
                self.assertEqual(len(rows),len({(row[1],row[2]) for row in rows}))
                for row in rows:
                    self.assertEqual(row[0],application_id(row[1],row[2]))
                for table,kind,column in (("Candidate","candidate","candidate_id"),("Requisition","requisition","requisition_id")):
                    actual=[row[0] for row in db.execute(f'SELECT {column} FROM {table} ORDER BY {column}')]
                    self.assertEqual(actual,[numbered_id(kind,index) for index in range(1,len(actual)+1)])

    def test_chronological_approval_and_application_history(self):
        for profile in PROFILES:
            with closing(connect(self.paths[profile][0])) as db:
                for req in db.execute("SELECT * FROM Requisition ORDER BY requisition_id"):
                    events=list(db.execute("SELECT * FROM RequisitionEvent WHERE requisition_id=? ORDER BY sequence",(req["requisition_id"],)))
                    self.assertEqual([row["new_status"] for row in events],["draft","pending_approval","approved","open"])
                    self.assertEqual([row["sequence"] for row in events],[1,2,3,4])
                    self.assertEqual([row["occurred_at"] for row in events],[req["valid_from"]+i*3600 for i in range(4)])
                    approval=db.execute("SELECT * FROM Approval WHERE requisition_id=?",(req["requisition_id"],)).fetchone()
                    self.assertEqual(approval["status"],"approved")
                    self.assertEqual(approval["decided_at"],events[2]["occurred_at"])
                    history=list(db.execute("SELECT snapshot_json FROM ApprovalEvent WHERE approval_id=? AND sequence=2",(approval["approval_id"],)))
                    checks=json.loads(history[0][0])["policy_checks"]
                    self.assertEqual(set(checks),{"pending_request","active_manager","independent_hr","valid_band","role_criteria","weights_reconcile"})
                    self.assertTrue(all(checks.values()))
                errors=db.execute("""SELECT COUNT(*) FROM Application a JOIN Candidate c USING(candidate_id)
                    JOIN RequisitionEvent e ON e.requisition_id=a.requisition_id AND e.sequence=4
                    WHERE a.applied_at<c.created_at OR a.applied_at<e.occurred_at""").fetchone()[0]
                self.assertEqual(errors,0)

    def test_projection_and_snapshot_history_agree(self):
        for profile in PROFILES:
            with closing(connect(self.paths[profile][0])) as db:
                for subject,key in (("Candidate","candidate_id"),("Application","application_id"),("Requisition","requisition_id"),("Approval","approval_id")):
                    bad=db.execute(f'''SELECT COUNT(*) FROM "{subject}" p WHERE p.status IS NOT
                        (SELECT e.new_status FROM "{subject}Event" e WHERE e."{key}"=p."{key}" ORDER BY sequence DESC LIMIT 1)''').fetchone()[0]
                    self.assertEqual(bad,0)

    def test_weights_proficiency_compensation_and_required_skills(self):
        for profile in PROFILES:
            with closing(connect(self.paths[profile][0])) as db:
                for row in db.execute("SELECT requisition_id,COUNT(*) n,SUM(weight_basis_points) w,MIN(min_proficiency) low,MAX(min_proficiency) high,SUM(is_required) required FROM SkillRequirement GROUP BY requisition_id"):
                    self.assertEqual(row["n"],4)
                    self.assertEqual(row["w"],10000)
                    self.assertGreater(row["required"],0)
                    self.assertTrue(0<=row["low"]<=row["high"]<=4)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM CandidateSkill WHERE level NOT BETWEEN 0 AND 4").fetchone()[0],0)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM Requisition WHERE band_min_minor<=0 OR band_max_minor<band_min_minor").fetchone()[0],0)
                self.assertTrue({row[0] for row in db.execute("SELECT DISTINCT skill_key FROM CandidateSkill")}<=set(SKILLS))

    def test_measured_distributions_and_experience_correlation(self):
        for profile in PROFILES:
            result=self.results[profile][0]
            self.assertEqual(set(result.summary["role_categories"]),{"backend","data","integration","applied_ai"})
            self.assertEqual(set(result.summary["seniority"]),{"Junior","Mid","Senior"})
            self.assertTrue(all(n>0 for n in result.summary["fit_categories"].values()))
            depths=result.summary["experience_skill_depth"]
            self.assertLess(depths["early"]["mean_level_milli"],depths["mid"]["mean_level_milli"])
            self.assertLess(depths["mid"]["mean_level_milli"],depths["experienced"]["mean_level_milli"])
            self.assertEqual(sum(result.summary["fit_categories"].values()),PROFILES[profile].applications)
            self.assertEqual(result.summary["applications_per_requisition"],{"16" if profile=="starter" else "40":PROFILES[profile].requisitions})
            with closing(connect(self.paths[profile][0])) as db:
                self.assertEqual(result.summary["counts"]["CandidateSkill"],db.execute("SELECT COUNT(*) FROM CandidateSkill").fetchone()[0])
                self.assertGreater(db.execute("SELECT COUNT(DISTINCT experience_years) FROM Candidate").fetchone()[0],5)

    def test_no_downstream_records_advanced_states_or_truth_labels(self):
        for profile in PROFILES:
            with closing(connect(self.paths[profile][0])) as db:
                self.assertTrue(all(db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]==0 for table in DEFERRED_TABLES))
                self.assertEqual([row[0] for row in db.execute("SELECT DISTINCT status FROM Application")],["applied"])
                self.assertEqual(db.execute("SELECT COUNT(*) FROM Approval WHERE offer_id IS NOT NULL").fetchone()[0],0)
                for table in ("CandidateEvent","ApplicationEvent","RequisitionEvent","ApprovalEvent"):
                    self.assertEqual(db.execute(f'''SELECT COUNT(*) FROM "{table}" e,json_tree(e.snapshot_json) j
                        WHERE j.key IN ('ground_truth','issue_type','expected_decision','anomaly_label')''').fetchone()[0],0)

    def test_two_independent_generations_equal_records_counts_summaries_and_hashes(self):
        for profile in PROFILES:
            left_result,right_result=self.results[profile]
            self.assertEqual(left_result.summary,right_result.summary)
            self.assertEqual(left_result.canonical,right_result.canonical)
            with closing(connect(self.paths[profile][0])) as left,closing(connect(self.paths[profile][1])) as right:
                self.assertEqual(dataset_digest(left),dataset_digest(right))
                sentinel=object()
                for table in table_names(left):
                    for index,(a,b) in enumerate(zip_longest(ordered_records(left,table),ordered_records(right,table),fillvalue=sentinel)):
                        self.assertIsNot(a,sentinel)
                        self.assertIsNot(b,sentinel)
                        self.assertEqual(tuple(a),tuple(b),(profile,table,index))

    def test_different_seed_changes_real_attributes_but_preserves_ids_and_counts(self):
        target=self.directory/"different-seed.sqlite3"
        other=generate_database(target,GenerationConfig(seed=20261023))
        self.assertEqual(other.summary["counts"],self.results["starter"][0].summary["counts"] | {"CandidateSkill":other.summary["counts"]["CandidateSkill"]})
        self.assertNotEqual(other.canonical["tables"]["Candidate"]["sha256"],self.results["starter"][0].canonical["tables"]["Candidate"]["sha256"])
        with closing(connect(self.paths["starter"][0])) as a,closing(connect(target)) as b:
            self.assertEqual([r[0] for r in a.execute("SELECT candidate_id FROM Candidate ORDER BY candidate_id")],
                             [r[0] for r in b.execute("SELECT candidate_id FROM Candidate ORDER BY candidate_id")])
            self.assertNotEqual([tuple(r) for r in a.execute("SELECT experience_years FROM Candidate ORDER BY candidate_id")],
                                [tuple(r) for r in b.execute("SELECT experience_years FROM Candidate ORDER BY candidate_id")])

    def test_hash_randomization_and_working_directory_do_not_affect_data(self):
        outputs=[]
        for value in ("17","123456"):
            environment=dict(os.environ,PYTHONPATH=str(ROOT/"src"),PYTHONHASHSEED=value)
            result=subprocess.run([sys.executable,"-m","yottaflex.generate","--profile","STARTER","--seed","20261022",
                "--database",str(self.directory/f"hash-{value}.sqlite3")],cwd=self.directory,
                env=environment,check=True,text=True,capture_output=True)
            outputs.append(json.loads(result.stdout))
        self.assertEqual(outputs[0]["canonical"],outputs[1]["canonical"])
        self.assertEqual(outputs[0]["summary"],outputs[1]["summary"])
        self.assertEqual(outputs[0]["canonical"],self.results["starter"][0].canonical)

    def test_derived_fit_formula_required_criteria_and_zero_minimum(self):
        requirements=[dict(criterion_key="python",min_proficiency=3,weight_basis_points=7500,is_required=1),
                      dict(criterion_key="sql",min_proficiency=2,weight_basis_points=2500,is_required=0)]
        self.assertEqual(skill_fit(requirements,{"python":3,"sql":2}),(10000,0,"excellent"))
        self.assertEqual(skill_fit(requirements,{"python":2,"sql":1}),(6250,1,"borderline"))
        self.assertEqual(skill_fit(requirements,{}),(0,1,"weak"))
        zero=[dict(criterion_key="python",min_proficiency=0,weight_basis_points=10000,is_required=1)]
        self.assertEqual(skill_fit(zero,{}),(10000,0,"excellent"))
        # High total cannot bypass a missing required criterion.
        uneven=[dict(criterion_key="python",min_proficiency=1,weight_basis_points=1,is_required=1),
                dict(criterion_key="sql",min_proficiency=1,weight_basis_points=9999,is_required=0)]
        self.assertEqual(skill_fit(uneven,{"sql":1}).category,"borderline")

    def test_fit_uses_actual_database_skills(self):
        with closing(connect(self.paths["starter"][0])) as db:
            candidates,requirements=load_matching_inputs(db)
            candidate=next(iter(candidates)); req=next(iter(requirements))
            original=skill_fit(requirements[req],candidates[candidate])
            db.execute("SAVEPOINT altered_skills")
            try:
                db.execute("UPDATE CandidateSkill SET level=0 WHERE candidate_id=?",(candidate,))
                changed,_=load_matching_inputs(db)
                self.assertEqual(skill_fit(requirements[req],changed[candidate]).basis_points,0)
                self.assertGreater(original.basis_points,0)
            finally:
                db.execute("ROLLBACK TO altered_skills")
                db.execute("RELEASE altered_skills")

    def test_single_pair_capacity_and_zero_application_boundaries(self):
        for count in (0,1):
            result=generate_database(self.directory/f"tiny-{count}.sqlite3",
                GenerationConfig(profile="custom",seed=0,scale=Scale(1,1,count)))
            self.assertEqual(result.summary["counts"]["Application"],count)
            self.assertTrue(result.summary["validation"]["passed"])
            self.assertEqual(result.summary["applications_per_requisition"],{str(count):1})

    def test_invalid_configuration_and_id_capacity(self):
        for scale in (Scale(0,1,0),Scale(1,0,0),Scale(1,1,2),Scale(1,1,-1),Scale(1.5,2,1)):
            with self.subTest(scale=scale),self.assertRaises(ValueError):
                GenerationConfig(profile="custom",scale=scale)
        for seed in (-1,2**63,True,1.5):
            with self.subTest(seed=seed),self.assertRaises(ValueError): GenerationConfig(seed=seed)
        with self.assertRaises(ValueError): GenerationConfig(profile="starter",scale=Scale(1,1,1))
        for counter in (0,-1,1000000,True):
            with self.assertRaises(ValueError): numbered_id("candidate",counter)
        self.assertEqual(numbered_id("candidate",999999),"CAND-999999")
        self.assertFalse(valid_numbered_id("candidate","CAND-000000"))
        with self.assertRaises(ValueError): application_id("CAND-0","REQ-2026-000001")

    def test_weight_rounding_is_deterministic_and_reconciles(self):
        self.assertEqual(normalized_weights([1,1,1]),[3334,3333,3333])
        self.assertEqual(sum(normalized_weights([35,30,20,15])),10000)
        for value in ([],[0,1],[-1,2]):
            with self.assertRaises(ValueError): normalized_weights(value)

    def test_existing_empty_populated_and_symlink_outputs_are_never_overwritten(self):
        for index,content in enumerate((b"",b"unrelated data")):
            target=self.directory/f"preserve-{index}.sqlite3"
            target.write_bytes(content)
            with self.assertRaises(FileExistsError): generate_database(target,GenerationConfig())
            self.assertEqual(target.read_bytes(),content)
        symlink=self.directory/"existing-link.sqlite3"
        symlink.symlink_to(self.directory/"does-not-exist.sqlite3")
        with self.assertRaises(FileExistsError): generate_database(symlink,GenerationConfig())
        self.assertTrue(symlink.is_symlink())
        with self.assertRaises(ValueError): generate_database(self.directory/"wrong-extension.txt",GenerationConfig())

    def test_transaction_failure_removes_scratch_and_never_publishes_partial_db(self):
        target=self.directory/"failed.sqlite3"
        with patch("yottaflex.generate._applications",side_effect=RuntimeError("injected failure after master writes")):
            with self.assertRaises(RuntimeError): generate_database(target,GenerationConfig())
        self.assertFalse(target.exists())
        self.assertEqual(list(self.directory.glob(".yottaflex-generation-*")),[])

    def test_failed_real_approval_policy_cannot_fabricate_approved_history(self):
        target=self.directory/"policy-failure.sqlite3"
        with patch.dict("yottaflex.generate.APPROVAL_CAP_MINOR",{"INR":1,"USD":1}):
            with self.assertRaisesRegex(ValueError,"Synthetic approval policy failed"):
                generate_database(target,GenerationConfig())
        self.assertFalse(target.exists())
        self.assertEqual(list(self.directory.glob(".yottaflex-generation-*")),[])

    def test_publish_race_preserves_another_writers_output(self):
        target=self.directory/"publish-race.sqlite3"
        def competing_writer(source,destination):
            Path(destination).write_bytes(b"other writer owns this")
            raise FileExistsError("simulated competing publisher")
        with patch("yottaflex.generate.os.link",side_effect=competing_writer):
            with self.assertRaises(FileExistsError): generate_database(target,GenerationConfig())
        self.assertEqual(target.read_bytes(),b"other writer owns this")
        self.assertEqual(list(self.directory.glob(".yottaflex-generation-*")),[])

    def test_validation_detects_semantic_corruption_in_isolated_savepoints(self):
        changes=["UPDATE Application SET status='screening' WHERE application_id=(SELECT MIN(application_id) FROM Application)",
                 "UPDATE SkillRequirement SET weight_basis_points=1 WHERE skill_requirement_id='SKILL-000001'",
                 "UPDATE SkillRequirement SET is_required=0,min_proficiency=1 WHERE skill_requirement_id='SKILL-000001'",
                 "UPDATE Staff SET role='interviewer' WHERE staff_id='STAFF-000002'",
                 "UPDATE Candidate SET experience_years=50 WHERE candidate_id='CAND-000001'",
                 "UPDATE Candidate SET created_at=created_at+15000000 WHERE candidate_id='CAND-000001'"]
        with closing(connect(self.paths["starter"][0])) as db:
            for sql in changes:
                db.execute("SAVEPOINT invalid_baseline")
                try:
                    db.execute(sql)
                    validation=validate_generated(db,GenerationConfig())
                    self.assertFalse(validation["passed"],validation)
                    self.assertTrue(any(check["violations"] for check in validation["checks"]))
                finally:
                    db.execute("ROLLBACK TO invalid_baseline")
                    db.execute("RELEASE invalid_baseline")
            self.assertEqual(dataset_digest(db),self.results["starter"][0].canonical)

    def test_cli_failure_has_nonzero_status_no_success_output(self):
        output=self.directory/"invalid-seed.sqlite3"
        environment=dict(os.environ,PYTHONPATH=str(ROOT/"src"))
        result=subprocess.run([sys.executable,"-m","yottaflex.generate","--profile","starter",
            "--seed","-1","--database",str(output)],env=environment,text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(result.stdout,"")
        self.assertIn("Generation failed",result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
