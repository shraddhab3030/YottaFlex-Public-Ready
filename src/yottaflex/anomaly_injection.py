"""Generation-only controlled interventions; never an ordinary workflow API."""

import hashlib
from itertools import combinations
import random

from .anomaly_rules import RULES
from .canonical import stable_json
from .generation_config import DAY, LOGICAL_ORIGIN
from .observations import entity_identity
from .workflow import check_slot, DomainError


def inject(connection, seed=20261022, cases=5):
    if type(seed) is not int or not 0<=seed<2**63 or type(cases) is not int or not 1<=cases<=10:
        raise ValueError('Use integer seed and 1..10 interventions per rule')
    rng = random.Random(seed ^ 0x414E4F4D414C59)
    as_of = LOGICAL_ORIGIN+196*DAY
    document = {'format_version':1,'as_of':as_of,'observations':[]}
    truth,controls = [],[]
    used_apps,used_candidates,used_interviews,used_offers = set(),set(),set(),set()
    observed = {}
    def rows(sql,parameters=()):
        return [dict(row) for row in connection.execute(sql,parameters)]
    def shuffled(values):
        rng.shuffle(values);return values
    def observe(table,before,after):
        identity = entity_identity(connection,table,after)
        entry = {'entity_type':table,'entity_id':identity,'observed_at':as_of,'before':before,'after':after}
        key=(table,identity)
        if key in observed and observed[key]!=entry:
            raise ValueError('Conflicting controlled observations; choose disjoint cases')
        observed[key]=entry
    def label(rule,entity_type,identity,related,evidence):
        key = {'rule_id':rule,'affected_entity_type':entity_type,'affected_entity_id':identity,'related_entity_ids':related}
        truth.append(key | {'scenario_id':'SCN-'+hashlib.sha256(stable_json(key|{'seed':seed}).encode()).hexdigest()[:24],
            'issue_type':RULES[rule],'expected_decision':'flag','observed_violation':evidence,'severity':'high',
            'applicable_timestamp':as_of,'deterministic_seed':seed})
    def require(actual,requested,rule):
        if actual!=requested:
            raise ValueError(f'INSUFFICIENT_SCENARIO_CAPACITY: {rule} requested={requested}, selected={actual}; no silent count reduction')
    # Missing real submitted reviews, not independently randomized labels.
    apps = shuffled(rows("""SELECT DISTINCT a.* FROM Application a JOIN Interview i USING(application_id)
        JOIN Scorecard s USING(interview_id) WHERE a.status='interviewing' AND s.status<>'submitted' ORDER BY a.application_id"""))
    require(min(len(apps),cases),cases,'R01')
    for app in apps[:cases]:
        observe('Application',app,app|{'status':'reviewed','updated_at':as_of})
        used_apps.add(app['application_id']);used_candidates.add(app['candidate_id'])
        label('R01','Application',app['application_id'],{'candidate_id':app['candidate_id'],'requisition_id':app['requisition_id']},
            {'before_status':app['status'],'after_status':'reviewed','incomplete_card_ids':[r[0] for r in connection.execute("SELECT s.scorecard_id FROM Scorecard s JOIN Interview i USING(interview_id) WHERE i.application_id=? AND s.status<>'submitted' ORDER BY s.scorecard_id",(app['application_id'],))]})
    # Two-member panels produce two staff-specific occurrences per pair.
    pairs=[]
    for panel in rows("SELECT panel_id FROM InterviewParticipant p JOIN Interview i USING(interview_id) GROUP BY panel_id HAVING COUNT(DISTINCT staff_id)=2 ORDER BY panel_id"):
        interviews=rows("SELECT * FROM Interview WHERE panel_id=? AND status='scheduled' ORDER BY interview_id",(panel['panel_id'],))
        pairs.extend(combinations(interviews,2))
    selected=[]
    for first,second in shuffled(pairs):
        app_a=rows('SELECT * FROM Application WHERE application_id=?',(first['application_id'],))[0]
        app_b=rows('SELECT * FROM Application WHERE application_id=?',(second['application_id'],))[0]
        if any(app['application_id'] in used_apps or app['candidate_id'] in used_candidates for app in (app_a,app_b)) or app_a['candidate_id']==app_b['candidate_id']:
            continue
        busy=connection.execute("""SELECT 1 FROM Interview i JOIN Application a USING(application_id) WHERE a.candidate_id=?
            AND i.interview_id<>? AND i.status IN ('scheduled','completed','no_show') AND i.start_at<? AND ?<i.end_at LIMIT 1""",
            (app_b['candidate_id'],second['interview_id'],first['end_at'],first['start_at'])).fetchone()
        if busy:
            continue
        members_a={r[0] for r in connection.execute('SELECT staff_id FROM InterviewParticipant WHERE interview_id=?',(first['interview_id'],))}
        members_b={r[0] for r in connection.execute('SELECT staff_id FROM InterviewParticipant WHERE interview_id=?',(second['interview_id'],))}
        shared=sorted(members_a & members_b)
        if len(shared)!=2:
            continue
        observe('Interview',first,first)
        replacement=second|{'start_at':first['start_at'],'end_at':first['end_at']}
        observe('Interview',second,replacement)
        pair=sorted((first['interview_id'],second['interview_id']))
        for staff in shared:
            label('R02','Interview',pair[0],{'interview_ids':pair,'staff_id':staff},
                {'first_interval':[first['start_at'],first['end_at']],'second_interval':[replacement['start_at'],replacement['end_at']],
                 'statuses':['scheduled','scheduled']})
        used_apps.update((app_a['application_id'],app_b['application_id']));used_candidates.update((app_a['candidate_id'],app_b['candidate_id']))
        used_interviews.update(pair);selected.append(pair)
        if len(selected)==cases:break
    require(len(selected),cases,'R02 pairs')
    offers=shuffled(rows('SELECT * FROM Offer ORDER BY offer_id'))
    require(min(len(offers),cases+1),cases+1,'R03 plus boundary control')
    for offer in offers[:cases]:
        band=rows('SELECT * FROM RequisitionEvent WHERE event_id=?',(offer['approved_requisition_event_id'],))[0]
        excess=rng.randint(1,10000)
        observe('Offer',offer,offer|{'amount_minor':band['band_max_minor']+excess})
        used_offers.add(offer['offer_id'])
        label('R03','Offer',offer['offer_id'],{'application_id':offer['application_id'],'requisition_id':offer['requisition_id'],'band_event_id':band['event_id']},
            {'observed_amount_minor':band['band_max_minor']+excess,'approved_max_minor':band['band_max_minor'],'difference_minor':excess,'currency':band['currency']})
    # Exactly one remaining scheduled booking per candidate avoids hidden cascades.
    bookings=shuffled(rows("""SELECT i.* FROM Interview i JOIN Application a USING(application_id) WHERE i.status='scheduled'
        AND (SELECT COUNT(*) FROM Interview j JOIN Application b USING(application_id) WHERE b.candidate_id=a.candidate_id AND j.status='scheduled')=1
        ORDER BY i.interview_id"""))
    withdrawals=[]
    for interview in bookings:
        app=rows('SELECT * FROM Application WHERE application_id=?',(interview['application_id'],))[0]
        if app['application_id'] in used_apps or app['candidate_id'] in used_candidates:continue
        withdrawn_at=as_of-rng.randint(3600,DAY)
        scope='application' if len(withdrawals)%2==0 else 'candidate'
        if scope=='application':
            observe('Application',app,app|{'status':'withdrawn','updated_at':withdrawn_at})
        else:
            candidate=rows('SELECT * FROM Candidate WHERE candidate_id=?',(app['candidate_id'],))[0]
            observe('Candidate',candidate,candidate|{'status':'withdrawn','withdrawn_at':withdrawn_at})
        observe('Interview',interview,interview)
        label('R04','Interview',interview['interview_id'],{'application_id':app['application_id'],'candidate_id':app['candidate_id']},
            {'scope':scope,'withdrawn_at':withdrawn_at,'observed_status':'scheduled'})
        used_apps.add(app['application_id']);used_candidates.add(app['candidate_id']);used_interviews.add(interview['interview_id']);withdrawals.append(interview['interview_id'])
        if len(withdrawals)==cases:break
    require(len(withdrawals),cases,'R04')
    cards=shuffled(rows("""SELECT s.* FROM Scorecard s JOIN Interview i USING(interview_id) JOIN Application a USING(application_id)
        WHERE s.status<>'submitted' AND a.status='interviewing' ORDER BY s.scorecard_id"""))
    irrelevant=[]
    for card in cards:
        interview=rows('SELECT * FROM Interview WHERE interview_id=?',(card['interview_id'],))[0]
        if interview['application_id'] in used_apps:continue
        criteria=rows('SELECT * FROM SkillRequirement WHERE requisition_id<>? ORDER BY skill_requirement_id',(interview['requisition_id'],))
        criterion=rng.choice(criteria)
        item={'scorecard_id':card['scorecard_id'],'skill_requirement_id':criterion['skill_requirement_id'],'score_value':2,
            'weight_basis_points':criterion['weight_basis_points'],'evidence':'Recorded structured rubric observation.','status':'scored'}
        observe('ScorecardItem',None,item)
        label('R05','Scorecard',card['scorecard_id'],{'criterion_id':criterion['skill_requirement_id'],'interview_id':interview['interview_id'],'requisition_id':interview['requisition_id']},
            {'criterion_requisition_id':criterion['requisition_id'],'scorecard_requisition_id':interview['requisition_id'],'criterion_version':criterion['rubric_version']})
        used_apps.add(interview['application_id']);irrelevant.append(card)
        if len(irrelevant)==cases:break
    require(len(irrelevant),cases,'R05')
    # Explicit boundary/near-miss observations. Their names live only in reports.
    upper=offers[cases];band=rows('SELECT * FROM RequisitionEvent WHERE event_id=?',(upper['approved_requisition_event_id'],))[0]
    observe('Offer',upper,upper|{'amount_minor':band['band_max_minor']})
    controls.append({'control':'upper_bound_offer','rule_id':'R03','entity_ids':[upper['offer_id']]})
    adjacent=None
    for panel in rows('SELECT * FROM InterviewPanel ORDER BY panel_id'):
        available=rows("SELECT * FROM Interview WHERE panel_id=? AND status='scheduled' ORDER BY interview_id",(panel['panel_id'],))
        for first,second in combinations(available,2):
            if first['interview_id'] in used_interviews or second['interview_id'] in used_interviews:continue
            app=rows('SELECT * FROM Application WHERE application_id=?',(second['application_id'],))[0]
            if app['candidate_id'] in used_candidates:continue
            start=first['end_at'];end=start+second['end_at']-second['start_at']
            try:check_slot(connection,app,panel,start,end,exclude=second['interview_id'])
            except DomainError:continue
            observe('Interview',first,first);observe('Interview',second,second|{'start_at':start,'end_at':end})
            used_interviews.update((first['interview_id'],second['interview_id']));adjacent=first;break
        if adjacent:break
    if adjacent is None:raise ValueError('INSUFFICIENT_CONTROL_CAPACITY: adjacent interviews')
    controls.append({'control':'adjacent_interviews','rule_id':'R02','entity_ids':sorted(used_interviews & {first['interview_id'],second['interview_id']})})
    cancelled=connection.execute("SELECT * FROM Interview WHERE panel_id=? AND status='cancelled' ORDER BY interview_id LIMIT 1",(adjacent['panel_id'],)).fetchone()
    if cancelled is None:raise ValueError('INSUFFICIENT_CONTROL_CAPACITY: cancelled overlap')
    cancelled=dict(cancelled);observe('Interview',cancelled,cancelled|{'start_at':adjacent['start_at'],'end_at':adjacent['end_at']})
    controls.append({'control':'cancelled_overlap','rule_id':'R02','entity_ids':[adjacent['interview_id'],cancelled['interview_id']]})
    correct=rows('SELECT * FROM ScorecardItem ORDER BY scorecard_id,skill_requirement_id LIMIT 1')[0]
    observe('ScorecardItem',correct,correct)
    controls.append({'control':'applicable_criterion','rule_id':'R05','entity_ids':[correct['scorecard_id'],correct['skill_requirement_id']]})
    # A legitimate later withdrawal of a pre-review completed application is a
    # valid R04 near-miss. It shares the R05 case, whose violation remains labelled.
    card=irrelevant[0];interview=rows('SELECT * FROM Interview WHERE interview_id=?',(card['interview_id'],))[0]
    app=rows('SELECT * FROM Application WHERE application_id=?',(interview['application_id'],))[0]
    observe('Application',app,app|{'status':'withdrawn','updated_at':as_of-60})
    controls.append({'control':'completed_before_later_application_withdrawal','rule_id':'R04','entity_ids':[interview['interview_id'],app['application_id']]})
    controls.append({'control':'unsubmitted_card_without_advancement','rule_id':'R01','entity_ids':[card['scorecard_id'],app['application_id']]})
    document['observations']=[observed[key] for key in sorted(observed)]
    return document,sorted(truth,key=lambda row:row['scenario_id']),controls
