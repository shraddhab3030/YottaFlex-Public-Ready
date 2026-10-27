"""Post-detection identity matching/metrics. Never imported by the detector."""

from collections import Counter
from .anomaly_rules import RULES
from .canonical import stable_json


def match_key(row):
    rule = row['rule_id']; related = row['related_entity_ids']
    if row['issue_type']!=RULES.get(rule):
        return (rule,row['issue_type'],'unrecognized',row['affected_entity_id'])
    if rule=='R02':
        if row['affected_entity_type']!='Interview':
            return (rule,'wrong_entity_type',row['affected_entity_type'],row['affected_entity_id'])
        pair = tuple(sorted(related['interview_ids']))
        if len(set(pair))!=2 or row['affected_entity_id'] not in pair:
            raise ValueError('Double-booking identity must contain exactly two distinct interviews')
        return (rule,'Interview',pair,related['staff_id'])
    extras = {'R01':('candidate_id','requisition_id'), 'R03':('band_event_id','application_id','requisition_id'),
              'R04':('application_id','candidate_id'), 'R05':('criterion_id','interview_id','requisition_id')}[rule]
    return (rule,row['affected_entity_type'],row['affected_entity_id'],*(related[key] for key in extras))


def _metrics(tp,fp,fn):
    return {'TP':tp,'FP':fp,'FN':fn,'precision':tp/(tp+fp) if tp+fp else None,
        'recall':tp/(tp+fn) if tp+fn else None,'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}


def evaluate(findings, truth, *, clean_findings=()):
    if any(row['expected_decision']!='flag' or RULES.get(row['rule_id'])!=row['issue_type'] for row in truth):
        raise ValueError('Unsupported or inconsistent truth rule/expected decision')
    expected = {match_key(row):row for row in truth}
    if len(expected)!=len(truth):
        raise ValueError('Ground truth must not contain duplicate business issue keys')
    seen,matched,duplicates = set(),set(),0
    counts = {rule:Counter() for rule in RULES}
    unexpected = []
    for finding in findings:
        key = match_key(finding); rule = finding['rule_id']
        counts.setdefault(rule,Counter())
        if key in seen:
            duplicates += 1
        seen.add(key)
        if key in expected and key not in matched:
            counts[rule]['TP'] += 1; matched.add(key)
        else:
            counts[rule]['FP'] += 1; unexpected.append(finding['finding_id'])
    missing = []
    for key,row in expected.items():
        if key not in matched:
            counts[row['rule_id']]['FN'] += 1; missing.append(row['scenario_id'])
    totals = sum((counter for counter in counts.values()),Counter())
    return _metrics(totals['TP'],totals['FP'],totals['FN']) | {
        'by_rule':{rule:_metrics(value['TP'],value['FP'],value['FN']) for rule,value in sorted(counts.items())},
        'by_issue_type':{RULES.get(rule,rule):_metrics(value['TP'],value['FP'],value['FN']) for rule,value in sorted(counts.items())},
        'duplicate_findings':duplicates,'unexpected_finding_ids':sorted(unexpected),'missed_scenario_ids':sorted(missing),
        'clean_baseline_false_positives':len(clean_findings),'rules_with_true_positives':sum(value['TP']>0 for value in counts.values()),
        'zero_denominators':'undefined precision/recall/F1 are null; F1=2TP/(2TP+FP+FN); no accuracy/TN claim'}
