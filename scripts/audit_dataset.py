"""Independent final-audit SQL evidence and real, isolated rejected operations."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import tempfile

from yottaflex.canonical import dataset_digest,table_names,ordered_records
from yottaflex.db import connect
from yottaflex.evaluation import create_scorecard,set_scorecard_item,submit_scorecard,review_application
from yottaflex.generate import generate_database
from yottaflex.generation_config import GenerationConfig,DAY
from yottaflex.observations import reference,projected,load_document,entity_identity
from yottaflex.offers import create_offer,submit_offer,approved_band
from yottaflex.workflow import DomainError,complete_interview,schedule_interview


def audit(database,observations,truth):
    with reference(database) as source:
        canonical=dataset_digest(source)
        offer=dict(source.execute("SELECT * FROM Offer WHERE status='accepted' ORDER BY offer_id LIMIT 1").fetchone())
        app=dict(source.execute('SELECT * FROM Application WHERE application_id=?',(offer['application_id'],)).fetchone())
        req=dict(source.execute('SELECT * FROM Requisition WHERE requisition_id=?',(app['requisition_id'],)).fetchone())
        histories={}
        for subject,key,identity in [('Requisition','requisition_id',req['requisition_id']),('Application','application_id',app['application_id']),('Offer','offer_id',offer['offer_id'])]:
            histories[subject]=[dict(r) for r in source.execute(f'SELECT event_id,sequence,previous_status,new_status,actor_staff_id,occurred_at FROM {subject}Event WHERE {key}=? ORDER BY sequence',(identity,))]
        approval=dict(source.execute('SELECT * FROM Approval WHERE offer_id=?',(offer['offer_id'],)).fetchone())
        histories['Approval']=[dict(r) for r in source.execute('SELECT event_id,sequence,new_status,actor_staff_id,occurred_at FROM ApprovalEvent WHERE approval_id=? ORDER BY sequence',(approval['approval_id'],))]
        interview=dict(source.execute("SELECT * FROM Interview WHERE application_id=? AND status='completed' ORDER BY interview_id LIMIT 1",(app['application_id'],)).fetchone())
        histories['Interview']=[dict(r) for r in source.execute('SELECT event_id,sequence,new_status,actor_staff_id,occurred_at FROM InterviewEvent WHERE interview_id=? ORDER BY sequence',(interview['interview_id'],))]
        cards=[dict(r) for r in source.execute('SELECT * FROM Scorecard WHERE interview_id=? ORDER BY scorecard_id',(interview['interview_id'],))]
        assert app['status']=='hired' and approval['status']=='approved'
        assert [r['new_status'] for r in histories['Offer']]==['draft','pending_approval','approved','sent','accepted']
        assert {'applied','screening','interviewing','reviewed','offer','hired'}<=set(r['new_status'] for r in histories['Application'])
        for card in cards:
            numerator=source.execute('SELECT SUM(x.score_value*r.weight_basis_points) FROM ScorecardItem x JOIN SkillRequirement r USING(skill_requirement_id) WHERE scorecard_id=?',(card['scorecard_id'],)).fetchone()[0]
            assert card['status']=='submitted' and card['total_score_milli']==(numerator+5)//10
        arithmetic=source.execute("""SELECT COUNT(*) FROM (SELECT s.scorecard_id FROM Scorecard s JOIN ScorecardItem x USING(scorecard_id)
            JOIN SkillRequirement r USING(skill_requirement_id) WHERE s.status='submitted' GROUP BY s.scorecard_id
            HAVING s.total_score_milli<>(SUM(x.score_value*r.weight_basis_points)+5)/10)""").fetchone()[0]
        bands=source.execute('SELECT COUNT(*) FROM Offer o JOIN RequisitionEvent e ON e.event_id=o.approved_requisition_event_id WHERE o.currency<>e.currency OR o.amount_minor<e.band_min_minor OR o.amount_minor>e.band_max_minor').fetchone()[0]
        assert arithmetic==bands==0
        variation={table:{str(r[0]):r[1] for r in source.execute(f'SELECT {column},COUNT(*) FROM {table} GROUP BY {column} ORDER BY {column}')} for table,column in [('Application','status'),('Interview','status'),('Scorecard','status'),('Offer','status'),('Requisition','currency'),('Candidate','experience_years')]}
        variation['rescheduled_events']=source.execute("SELECT COUNT(*) FROM InterviewEvent WHERE event_type='rescheduled'").fetchone()[0]
        document=load_document(observations);labels=json.loads(Path(truth).read_text());independent=[]
        with projected(source,document) as (view,structure):
            observed={(r['entity_type'],r['entity_id']) for r in document['observations'] if r['before']!=r['after']};changed=set()
            for table in table_names(source):
                a={entity_identity(source,table,dict(r)):tuple(r) for r in ordered_records(source,table)}
                b={entity_identity(view,table,dict(r)):tuple(r) for r in ordered_records(view,table)}
                changed.update((table,key) for key in a.keys()|b.keys() if a.get(key)!=b.get(key))
            assert observed==changed
            for label in labels:
                rule=label['rule_id'];identity=label['affected_entity_id'];related=label['related_entity_ids'];evidence={}
                if rule=='R01':
                    row=view.execute('SELECT status FROM Application WHERE application_id=?',(identity,)).fetchone()
                    missing=view.execute("""SELECT COUNT(*) FROM Interview i JOIN InterviewParticipant p USING(interview_id)
                        LEFT JOIN Scorecard s ON s.interview_id=i.interview_id AND s.reviewer_staff_id=p.staff_id
                        WHERE i.application_id=? AND i.status<>'cancelled' AND p.assignment_role='reviewer' AND (s.status IS NULL OR s.status<>'submitted')""",(identity,)).fetchone()[0]
                    assert row[0] in ('reviewed','offer','hired') and missing>0;evidence={'stage':row[0],'unsubmitted_required_reviews':missing}
                elif rule=='R02':
                    pair=[dict(view.execute('SELECT * FROM Interview WHERE interview_id=?',(i,)).fetchone()) for i in related['interview_ids']]
                    assert all(r['status'] in ('scheduled','completed','no_show') for r in pair)
                    assert pair[0]['start_at']<pair[1]['end_at'] and pair[1]['start_at']<pair[0]['end_at']
                    assert all(view.execute('SELECT 1 FROM InterviewParticipant WHERE interview_id=? AND staff_id=?',(r['interview_id'],related['staff_id'])).fetchone() for r in pair)
                    evidence={'staff_id':related['staff_id'],'interview_ids':related['interview_ids'],'intervals':[[r['start_at'],r['end_at']] for r in pair]}
                elif rule=='R03':
                    row=view.execute('SELECT o.amount_minor,e.band_max_minor,o.currency,e.currency FROM Offer o JOIN RequisitionEvent e ON e.event_id=o.approved_requisition_event_id WHERE offer_id=?',(identity,)).fetchone()
                    assert row[0]>row[1] and row[2]==row[3];evidence={'amount_minor':row[0],'maximum_minor':row[1],'excess_minor':row[0]-row[1]}
                elif rule=='R04':
                    row=view.execute('SELECT i.status,a.status,c.status,a.updated_at,c.withdrawn_at FROM Interview i JOIN Application a USING(application_id) JOIN Candidate c USING(candidate_id) WHERE interview_id=?',(identity,)).fetchone()
                    assert row[0]=='scheduled' and (row[1]=='withdrawn' and row[3]<=document['as_of'] or row[2]=='withdrawn' and row[4]<=document['as_of']);evidence={'interview_status':row[0],'application_status':row[1],'candidate_status':row[2]}
                elif rule=='R05':
                    row=view.execute('SELECT r.requisition_id,i.requisition_id FROM ScorecardItem x JOIN SkillRequirement r USING(skill_requirement_id) JOIN Scorecard s USING(scorecard_id) JOIN Interview i USING(interview_id) WHERE x.scorecard_id=? AND x.skill_requirement_id=?',(identity,related['criterion_id'])).fetchone()
                    assert row and row[0]!=row[1];evidence={'criterion_requisition':row[0],'interview_requisition':row[1]}
                else:raise AssertionError('Unknown mandatory rule')
                independent.append({'scenario_id':label['scenario_id'],'rule':rule,'entity_id':identity,'actual_sql_evidence':evidence,'passed':True})
        assert dataset_digest(source)==canonical
        return {'canonical':canonical,'successful_path':{'requisition_id':req['requisition_id'],'candidate_id':app['candidate_id'],'application_id':app['application_id'],'interview_id':interview['interview_id'],'scorecards':cards,'offer':offer,'approval':approval,'histories':histories},'independent_sql':{'score_arithmetic_errors':arithmetic,'offer_band_errors':bands},'variation':variation,'observation_structure':structure,'exact_changed_rows_match_observations':True,'independently_checked_truth_issues':independent,'baseline_preserved':True}


def rejected_operations():
    with tempfile.TemporaryDirectory(prefix='yottaflex-audit-operations-') as name:
        p=Path(name)/'interviews.sqlite3';generate_database(p,GenerationConfig(),phase='interviews')
        with closing(connect(p)) as db:
            row=db.execute("SELECT * FROM Interview WHERE status='scheduled' ORDER BY interview_id LIMIT 1").fetchone();identity=row['application_id'];when=db.execute('SELECT updated_at FROM Application WHERE application_id=?',(identity,)).fetchone()[0]+1
            result=[]
            def reject(label,expected,callback):
                before=dataset_digest(db)
                try:callback()
                except DomainError as error:
                    assert error.code==expected and dataset_digest(db)==before and not db.in_transaction
                    result.append({'operation':label,'observed_code':error.code,'all_rows_unchanged':True})
                else:raise AssertionError('Operation unexpectedly accepted')
            meta=lambda actor,t:dict(actor_id=actor,when=t,reason_code='FINAL_AUDIT')
            reject('double-book existing panel','INTERVIEWER_CONFLICT',lambda:schedule_interview(db,identity,row['panel_id'],row['start_at'],row['end_at'],**meta('STAFF-000002',when)))
            when=GenerationConfig().logical_origin+188*DAY
            complete_interview(db,row['interview_id'],**meta('STAFF-000002',when))
            reject('advance before required reviews','REVIEW_GATE_INCOMPLETE',lambda:review_application(db,identity,**meta('STAFF-000002',when+1)))
            criteria=[r[0] for r in db.execute('SELECT skill_requirement_id FROM SkillRequirement WHERE requisition_id=? ORDER BY skill_requirement_id',(row['requisition_id'],))]
            other=db.execute('SELECT skill_requirement_id FROM SkillRequirement WHERE requisition_id<>? LIMIT 1',(row['requisition_id'],)).fetchone()[0]
            for reviewer, in db.execute('SELECT staff_id FROM InterviewParticipant WHERE interview_id=? ORDER BY staff_id',(row['interview_id'],)).fetchall():
                when+=1;card=create_scorecard(db,row['interview_id'],reviewer,**meta(reviewer,when))
                reject('irrelevant existing criterion','IRRELEVANT_CRITERION',lambda:set_scorecard_item(db,card,other,3,'Audit evidence',**meta(reviewer,when)))
                for criterion in criteria:
                    when+=1;set_scorecard_item(db,card,criterion,3,'Synthetic audit evidence',**meta(reviewer,when))
                when+=1;submit_scorecard(db,card,**meta(reviewer,when))
            when+=1;review_application(db,identity,**meta('STAFF-000002',when));band=approved_band(db,row['requisition_id'],when)
            reject('offer above approved band','OFFER_OUTSIDE_BAND',lambda:create_offer(db,identity,amount_minor=band['band_max_minor']+1,**meta('STAFF-000002',when)))
            offer=create_offer(db,identity,**meta('STAFF-000002',when))
            reject('creator self-approval','SELF_APPROVAL_FORBIDDEN',lambda:submit_offer(db,offer,'STAFF-000002',**meta('STAFF-000002',when)))
            withdrawn=db.execute("SELECT application_id FROM Application WHERE status='withdrawn' ORDER BY application_id LIMIT 1").fetchone()[0]
            reject('book withdrawn application','APPLICATION_WITHDRAWN',lambda:schedule_interview(db,withdrawn,row['panel_id'],row['start_at'],row['end_at'],**meta('STAFF-000002',when)))
            return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('database','observations','truth','output'):parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();result=audit(a.database,a.observations,a.truth);result['rejected_operations']=rejected_operations()
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS independent SQL/actual histories:',len(result['canonical']['tables']),'tables,',len(result['independently_checked_truth_issues']),'issues,',len(result['rejected_operations']),'rejected operations')
