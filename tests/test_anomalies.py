"""Real anomaly observations, label-blind rules, boundaries and matching metrics."""
import ast
from contextlib import closing
from copy import deepcopy
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sqlite3

from yottaflex.anomalies import build_bundle
from yottaflex.anomaly_evaluation import evaluate,match_key
from yottaflex.anomaly_injection import inject
from yottaflex.anomaly_rules import RULES
from yottaflex.anomaly_truth import read_csv,FIELDS
from yottaflex.canonical import dataset_digest,ordered_records,table_names
from yottaflex.db import connect
from yottaflex.detector import detect
from yottaflex.generate import generate_database
from yottaflex.generation_config import GenerationConfig
from yottaflex.observations import reference,projected,entity_identity,load_document

ROOT=Path(__file__).resolve().parents[1]


class AnomalyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace=tempfile.TemporaryDirectory(prefix='yottaflex-anomalies-');cls.directory=Path(cls.workspace.name)
        cls.baseline=cls.directory/'clean.sqlite3'
        cls.generated=generate_database(cls.baseline,GenerationConfig(),phase='evaluations')
        cls.paths=[cls.directory/f'run-{i}' for i in (1,2)]
        cls.results=[build_bundle(cls.baseline,path,'starter') for path in cls.paths]
        cls.document=load_document(cls.paths[0]/'input/observations.json')
        cls.truth=json.loads((cls.paths[0]/'truth/ground_truth.json').read_text())
        cls.findings=json.loads((cls.paths[0]/'reports/findings.json').read_text())['findings']
        cls.controls=json.loads((cls.paths[0]/'reports/controls.json').read_text())

    @classmethod
    def tearDownClass(cls):cls.workspace.cleanup()

    def control(self,name):return next(row for row in self.controls if row['control']==name)
    def issue(self,rule):return next(row for row in self.truth if row['rule_id']==rule)
    def observed(self,table,identity,document=None):
        return next(row for row in (document or self.document)['observations'] if row['entity_type']==table and row['entity_id']==identity)

    def test_clean_baseline_same_engine_has_zero_findings(self):
        result=detect(self.baseline)
        self.assertEqual(result['findings'],[]);self.assertTrue(result['semantic_valid'])
        self.assertTrue(result['structure']['passed'])

    def test_all_five_types_generated_from_real_values(self):
        self.assertEqual({row['issue_type'] for row in self.truth},set(RULES.values()))
        self.assertEqual(len(self.truth),6)
        self.assertTrue(all(set(row)==set(FIELDS) for row in self.truth))

    def test_all_five_types_independently_detected(self):
        self.assertEqual({row['rule_id'] for row in self.findings},set(RULES))
        self.assertEqual({match_key(row) for row in self.findings},{match_key(row) for row in self.truth})

    def test_detector_transitive_imports_cannot_read_labels_or_injection(self):
        pending=['detector'];seen=set()
        while pending:
            name=pending.pop()
            if name in seen:continue
            seen.add(name)
            tree=ast.parse((ROOT/f'src/yottaflex/{name}.py').read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom) and node.level==1 and node.module:
                    dependency=node.module.split('.')[0]
                    self.assertNotIn(dependency,('anomaly_truth','anomaly_injection','anomaly_evaluation','anomalies'))
                    if (ROOT/f'src/yottaflex/{dependency}.py').exists():pending.append(dependency)

    def test_missing_or_poisoned_truth_cannot_change_findings(self):
        truth_dir=self.paths[0]/'truth';saved=truth_dir.with_name('hidden-labels')
        truth_dir.rename(saved)
        try:
            truth_dir.mkdir();(truth_dir/'ground_truth.json').write_text('not valid JSON; all decisions reversed')
            result=detect(self.paths[0]/'input/baseline.sqlite3',self.document)
            self.assertEqual(result['findings'],self.findings)
        finally:
            (truth_dir/'ground_truth.json').unlink();truth_dir.rmdir();saved.rename(truth_dir)

    def test_adjacent_control_is_not_double_booked(self):
        pair=set(self.control('adjacent_interviews')['entity_ids'])
        self.assertEqual(len(pair),2)
        self.assertFalse(any(row['rule_id']=='R02' and set(row['related_entity_ids']['interview_ids'])==pair for row in self.findings))
        entries=[self.observed('Interview',identity)['after'] for identity in pair]
        self.assertTrue(entries[0]['end_at']==entries[1]['start_at'] or entries[1]['end_at']==entries[0]['start_at'])

    def test_cancelled_booking_never_blocks_shared_staff(self):
        ids=self.control('cancelled_overlap')['entity_ids']
        cancelled=next(identity for identity in ids if self.observed('Interview',identity)['after']['status']=='cancelled')
        self.assertFalse(any(row['rule_id']=='R02' and cancelled in row['related_entity_ids']['interview_ids'] for row in self.findings))

    def test_above_band_offer_and_exact_boundary_distinguished(self):
        truth=self.issue('R03');finding=next(row for row in self.findings if row['rule_id']=='R03')
        self.assertGreater(finding['observed_values']['excess_minor'],0)
        self.assertEqual(finding['observed_values']['excess_minor'],truth['observed_violation']['difference_minor'])
        upper=self.control('upper_bound_offer')['entity_ids'][0]
        self.assertFalse(any(row['rule_id']=='R03' and row['affected_entity_id']==upper for row in self.findings))

    def test_wrong_requisition_is_existing_fk_not_orphan(self):
        row=self.issue('R05');criterion=row['related_entity_ids']['criterion_id']
        with reference(self.baseline) as source:
            actual=source.execute('SELECT requisition_id FROM SkillRequirement WHERE skill_requirement_id=?',(criterion,)).fetchone()[0]
        self.assertNotEqual(actual,row['related_entity_ids']['requisition_id'])
        self.assertTrue(any(f['rule_id']=='R05' and f['related_entity_ids']['criterion_id']==criterion for f in self.findings))

    def test_correct_criterion_is_accepted(self):
        score,criterion=self.control('applicable_criterion')['entity_ids']
        self.assertFalse(any(row['rule_id']=='R05' and row['affected_entity_id']==score and row['related_entity_ids']['criterion_id']==criterion for row in self.findings))

    def test_same_requisition_future_version_is_still_irrelevant(self):
        fixture=self.directory/'future-version-fixture.sqlite3'
        with reference(self.baseline) as source,closing(connect(fixture)) as destination:source.backup(destination)
        score=self.issue('R05')['affected_entity_id']
        with closing(connect(fixture)) as db:
            interview=db.execute('SELECT i.* FROM Interview i JOIN Scorecard s USING(interview_id) WHERE s.scorecard_id=?',(score,)).fetchone()
            criterion=dict(db.execute('SELECT * FROM SkillRequirement WHERE requisition_id=? ORDER BY skill_requirement_id LIMIT 1',(interview['requisition_id'],)).fetchone())
            criterion['skill_requirement_id']='SKILL-900000';criterion['rubric_version']=2
            criterion['valid_from']=db.execute('SELECT MAX(end_at)+1 FROM Interview WHERE requisition_id=?',(interview['requisition_id'],)).fetchone()[0]
            names=list(criterion)
            with db:db.execute('INSERT INTO SkillRequirement ('+','.join(names)+') VALUES ('+','.join('?' for _ in names)+')',tuple(criterion[name] for name in names))
        item={'scorecard_id':score,'skill_requirement_id':criterion['skill_requirement_id'],'score_value':3,
            'weight_basis_points':criterion['weight_basis_points'],'evidence':'Recorded rubric evidence.','status':'scored'}
        doc={'format_version':1,'as_of':self.document['as_of'],'observations':[{'entity_type':'ScorecardItem',
            'entity_id':score+'|'+criterion['skill_requirement_id'],'observed_at':self.document['as_of'],'before':None,'after':item}]}
        findings=detect(fixture,doc)['findings']
        self.assertTrue(any(row['rule_id']=='R05' and row['related_entity_ids']['criterion_id']=='SKILL-900000' for row in findings))

    def test_incomplete_review_without_advancement_is_not_anomalous(self):
        truth=self.issue('R01');identity=truth['affected_entity_id']
        doc=deepcopy(self.document);doc['observations']=[row for row in doc['observations'] if not(row['entity_type']=='Application' and row['entity_id']==identity)]
        findings=detect(self.baseline,doc)['findings']
        self.assertFalse(any(row['rule_id']=='R01' and row['affected_entity_id']==identity for row in findings))

    def test_advancement_despite_missing_review_has_actual_card_evidence(self):
        identity=self.issue('R01')['affected_entity_id']
        finding=next(row for row in self.findings if row['rule_id']=='R01' and row['affected_entity_id']==identity)
        self.assertEqual(finding['observed_values']['stage'],'reviewed')
        self.assertTrue(any(row['scorecard_status']!='submitted' for row in finding['observed_values']['evaluation_states']))

    def test_withdrawn_scheduled_is_detected_and_cancelled_is_not(self):
        identity=self.issue('R04')['affected_entity_id']
        self.assertTrue(any(row['rule_id']=='R04' and row['affected_entity_id']==identity for row in self.findings))
        doc=deepcopy(self.document);self.observed('Interview',identity,doc)['after']['status']='cancelled'
        self.assertFalse(any(row['rule_id']=='R04' and row['affected_entity_id']==identity for row in detect(self.baseline,doc)['findings']))

    def test_candidate_wide_withdrawal_and_completed_history(self):
        truth=self.issue('R04');identity=truth['affected_entity_id'];candidate=truth['related_entity_ids']['candidate_id']
        with reference(self.baseline) as source:
            before=dict(source.execute('SELECT * FROM Candidate WHERE candidate_id=?',(candidate,)).fetchone())
        doc={'format_version':1,'as_of':self.document['as_of'],'observations':[{'entity_type':'Candidate','entity_id':candidate,
            'observed_at':self.document['as_of'],'before':before,'after':before|{'status':'withdrawn','withdrawn_at':self.document['as_of']-60}}]}
        self.assertTrue(any(row['rule_id']=='R04' and row['affected_entity_id']==identity for row in detect(self.baseline,doc)['findings']))
        history=self.control('completed_before_later_application_withdrawal')['entity_ids'][0]
        self.assertFalse(any(row['rule_id']=='R04' and row['affected_entity_id']==history for row in self.findings))

    def test_all_references_and_pk_fk_scalar_constraints_hold(self):
        with reference(self.baseline) as source,projected(source,self.document) as (view,structure):
            self.assertTrue(structure['passed']);self.assertTrue(all(value==0 for value in structure['checks'].values()))
            self.assertEqual(list(view.execute('PRAGMA foreign_key_check')),[])
            self.assertEqual(view.execute('PRAGMA foreign_keys').fetchone()[0],1)
            self.assertEqual(view.execute('PRAGMA recursive_triggers').fetchone()[0],1)

    def test_immutable_reference_and_no_baseline_change(self):
        before=self.baseline.read_bytes()
        with reference(self.baseline) as source:
            with self.assertRaises(sqlite3.OperationalError):source.execute("UPDATE Application SET status='reviewed'")
        detect(self.baseline,self.document)
        self.assertEqual(self.baseline.read_bytes(),before)
        with reference(self.baseline) as source:self.assertEqual(dataset_digest(source),self.generated.canonical)

    def test_exact_observed_rows_only_no_unrelated_history_changes(self):
        expected={(r['entity_type'],r['entity_id']) for r in self.document['observations'] if r['before']!=r['after']}
        changed=set()
        with reference(self.baseline) as source,projected(source,self.document) as (view,_):
            for table in table_names(source):
                left={entity_identity(source,table,dict(r)):tuple(r) for r in ordered_records(source,table)}
                right={entity_identity(view,table,dict(r)):tuple(r) for r in ordered_records(view,table)}
                changed.update((table,key) for key in left.keys()|right.keys() if left.get(key)!=right.get(key))
        self.assertEqual(changed,expected)

    def test_truth_csv_and_json_exact_agreement(self):
        self.assertEqual(read_csv(self.paths[0]/'truth/ground_truth.csv'),self.truth)

    def test_answer_keys_and_extra_metadata_rejected_from_input(self):
        for name in ('ground_truth','issue_type','expected_decision','scenario_id','is_injected'):
            doc=deepcopy(self.document);doc['observations'][0][name]='answer'
            with self.assertRaises(ValueError):detect(self.baseline,doc)

    def test_shuffle_or_identifiers_in_filename_do_not_influence_engine(self):
        doc=deepcopy(self.document);doc['observations'].reverse()
        path=self.directory/'ground_truth_fake_name_observations.json';path.write_text(json.dumps(doc))
        self.assertEqual(detect(self.baseline,load_document(path))['findings'],self.findings)

    def test_tp_fp_fn_and_conventional_precision_recall_f1(self):
        findings=deepcopy(self.findings[1:]);extra=deepcopy(self.findings[0]);extra['affected_entity_id']='UNEXPECTED';extra['finding_id']='FIND-UNEXPECTED'
        # Use an ordinary single-entity rule for the explicit false positive.
        extra=deepcopy(next(f for f in self.findings if f['rule_id']=='R03'));extra['affected_entity_id']='OFF-2026-999999';extra['finding_id']='FIND-UNEXPECTED'
        result=evaluate(findings+[extra],self.truth)
        self.assertEqual((result['TP'],result['FP'],result['FN']),(5,1,1))
        self.assertAlmostEqual(result['precision'],5/6);self.assertAlmostEqual(result['recall'],5/6);self.assertAlmostEqual(result['f1'],5/6)

    def test_duplicate_findings_are_fp_not_multiple_tp(self):
        result=evaluate(self.findings+[self.findings[0]],self.truth)
        self.assertEqual((result['TP'],result['FP'],result['FN'],result['duplicate_findings']),(6,1,0,1))

    def test_pair_order_invariant_but_staff_identity_required(self):
        finding=deepcopy(next(f for f in self.findings if f['rule_id']=='R02'));truth=next(t for t in self.truth if match_key(t)==match_key(finding))
        finding['related_entity_ids']['interview_ids'].reverse();finding['affected_entity_id']=finding['related_entity_ids']['interview_ids'][0]
        self.assertEqual(evaluate([finding],[truth])['TP'],1)
        finding['related_entity_ids']['staff_id']='STAFF-999999'
        self.assertEqual((evaluate([finding],[truth])['FP'],evaluate([finding],[truth])['FN']),(1,1))

    def test_criterion_and_band_identity_required_for_matching(self):
        for rule,field in (('R03','band_event_id'),('R05','criterion_id')):
            finding=deepcopy(next(f for f in self.findings if f['rule_id']==rule));truth=next(t for t in self.truth if match_key(t)==match_key(finding))
            finding['related_entity_ids'][field]='WRONG-EXISTING-REFERENCE'
            self.assertEqual((evaluate([finding],[truth])['TP'],evaluate([finding],[truth])['FP'],evaluate([finding],[truth])['FN']),(0,1,1))

    def test_zero_denominators_and_no_accuracy_or_fake_tn(self):
        result=evaluate([],[])
        self.assertIsNone(result['precision']);self.assertIsNone(result['recall']);self.assertIsNone(result['f1'])
        self.assertNotIn('accuracy',result);self.assertNotIn('TN',result)
        missing=evaluate([],self.truth)
        self.assertIsNone(missing['precision']);self.assertEqual(missing['recall'],0);self.assertEqual(missing['f1'],0)

    def test_same_engine_used_for_clean_and_anomalous(self):
        from yottaflex import detector
        with patch('yottaflex.detector.detect_records',wraps=detector.detect_records) as engine:
            detector.detect(self.baseline);detector.detect(self.baseline,self.document)
            self.assertEqual(engine.call_count,2)

    def test_two_independent_bundles_match_all_files_and_content(self):
        self.assertEqual(self.results[0][0],self.results[1][0])
        for name in self.results[0][0]['file_sha256']:
            self.assertEqual((self.paths[0]/name).read_bytes(),(self.paths[1]/name).read_bytes(),name)
        for path in self.paths:
            with reference(path/'input/baseline.sqlite3') as source:self.assertEqual(dataset_digest(source),self.generated.canonical)

    def test_different_anomaly_seed_changes_interventions_not_baseline(self):
        with reference(self.baseline) as source:
            left=inject(source,20261022,1);right=inject(source,20261023,1)
            self.assertEqual(dataset_digest(source),self.generated.canonical)
        self.assertNotEqual(left[0],right[0]);self.assertNotEqual(left[1],right[1]);self.assertEqual(len(left[1]),len(right[1]))

    def test_injection_failure_never_publishes_partial_output(self):
        target=self.directory/'failed-experiment'
        with patch('yottaflex.anomalies.write_truth',side_effect=RuntimeError('injected IO failure')),self.assertRaises(RuntimeError):
            build_bundle(self.baseline,target,'starter')
        self.assertFalse(target.exists());self.assertFalse((target.parent/('.'+target.name+'.publication-lock')).exists())
        self.assertEqual(list(self.directory.glob('.phase06-*')),[])

    def test_existing_outputs_and_unowned_locks_preserved(self):
        with self.assertRaises(FileExistsError):build_bundle(self.baseline,self.paths[0],'starter')
        target=self.directory/'locked';lock=self.directory/'.locked.publication-lock';lock.write_text('other owner')
        try:
            with self.assertRaises(FileExistsError):build_bundle(self.baseline,target,'starter')
            self.assertEqual(lock.read_text(),'other owner')
        finally:lock.unlink()

    def test_invalid_foreign_key_scalar_and_before_snapshot_rejected(self):
        doc=deepcopy(self.document);entry=next(r for r in doc['observations'] if r['entity_type']=='ScorecardItem' and r['before'] is None)
        entry['after']['skill_requirement_id']='SKILL-999999';entry['entity_id']=entry['after']['scorecard_id']+'|SKILL-999999'
        with self.assertRaises(sqlite3.IntegrityError):detect(self.baseline,doc)
        doc=deepcopy(self.document);doc['observations'][0]['before']={}
        with self.assertRaises(ValueError):detect(self.baseline,doc)
        doc=deepcopy(self.document);entry=next(r for r in doc['observations'] if r['entity_type']=='Interview');entry['after']['start_at']=True
        with self.assertRaises(ValueError):detect(self.baseline,doc)

    def test_generation_runs_detector_before_truth_serialization(self):
        from yottaflex import anomalies
        trace=[];original=anomalies.detect;writer=anomalies.write_truth
        def detect_first(*args,**kwargs):trace.append('detect');return original(*args,**kwargs)
        def labels_later(*args,**kwargs):
            self.assertEqual(trace,['detect','detect']);return writer(*args,**kwargs)
        with patch('yottaflex.anomalies.detect',side_effect=detect_first),patch('yottaflex.anomalies.write_truth',side_effect=labels_later):
            build_bundle(self.baseline,self.directory/'ordering','starter')


class FullAnomalyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace=tempfile.TemporaryDirectory(prefix='yottaflex-full-anomalies-');cls.directory=Path(cls.workspace.name)
        cls.baseline=cls.directory/'full.sqlite3'
        cls.generated=generate_database(cls.baseline,GenerationConfig('full'),phase='evaluations')
        cls.summary,cls.timing=build_bundle(cls.baseline,cls.directory/'experiment','full')

    @classmethod
    def tearDownClass(cls):cls.workspace.cleanup()

    def test_full_target_counts_preserved_with_all_five_detectable_types(self):
        counts=self.summary['structure']['counts'];self.assertEqual(tuple(counts[k] for k in ('Requisition','Candidate','Application','Interview')),(200,5000,8000,2000))
        self.assertEqual(self.summary['findings_by_rule'],{'R01':5,'R02':10,'R03':5,'R04':5,'R05':5})
        self.assertEqual((self.summary['evaluation']['TP'],self.summary['evaluation']['FP'],self.summary['evaluation']['FN']),(30,0,0))
        self.assertEqual(self.summary['clean_findings'],0)

    def test_previous_phase05_full_canonical_content_unchanged(self):
        previous=json.loads((ROOT/'docs/phase05/reproducibility-evidence.json').read_text())['profiles']['full']['runs'][0]['canonical']
        self.assertEqual(self.generated.canonical,previous);self.assertEqual(self.summary['baseline_canonical'],previous)
        self.assertTrue(self.summary['source_preserved']);self.assertTrue(all(v==0 for v in self.summary['structure']['checks'].values()))


if __name__=='__main__':unittest.main()
