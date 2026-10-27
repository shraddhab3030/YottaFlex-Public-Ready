> Publication-copy notice: private home-path identifiers are replaced by `<private-home>/`. Technical results remain historical evidence. Every redaction is logged in docs/publication-preparation/redaction-log.json; the original private report/history is unchanged.

# YottaFlex Phase 06 — controlled anomalies, ground truth and independent evaluation

**Phase 06 PASS. STOP before Phase 07. Human review pending.**
Prepared locally on2026-10-27. Deadline: **2026-10-29 13:52:35 IST**.
Root: `<private-home>/Documents/Personal/Projects/Assignment/YottaFlex`. Branch: `codex/phase-01-foundation`.
No push, merge, remote setup, publication, recruitment contact or submission.
This report is self-contained for downloading/pasting into another ChatGPT chat.
Preserve completed work, the phase boundary and the remaining requirements below.

## 1. Result and authority

User supplied the complete 21-section Phase 06 prompt and said `here is next step`.
It conditionally approves Phase 05 progression and explicitly authorizes Phase 06
only. Official problem statement/PDFs are challenge evidence, not authorization
for publication or later work. Existing valid Phase 05 code/data/history is intact.

Actual work: verified read-only canonical reference, deterministic semantic
observations, all five required types, separate agreed truth CSV/JSON, label-blind
same-engine detector, evidence-rich findings, independent matching/metrics,
structure/content protections, tests and two independent replay pairs.

**183 actual tests passed in 88.584s**, including all 148 prior tests. Final FULL
findings: 30, measured TP=30/FP=0/FN=0; precision/recall/F1=1.0 on this controlled
benchmark. Clean findings 0. These measured values are not hardcoded successes or
a broad real-world accuracy/generalization claim. All four mandatory full counts
remain 200/5000/8000/2000. All 99 clean Phase 05 checks remain zero; observed structure
checks all zero while intentional semantic findings remain visible.

## 2. Exact files created/modified

| File | Change |
| --- | --- |
| src/yottaflex/observations.py | Created |
| src/yottaflex/anomaly_rules.py | Created |
| src/yottaflex/anomaly_injection.py | Created |
| src/yottaflex/anomaly_truth.py | Created |
| src/yottaflex/detector.py | Created |
| src/yottaflex/anomaly_evaluation.py | Created |
| src/yottaflex/anomalies.py | Created |
| scripts/verify_anomaly_reproducibility.py | Created |
| tests/test_anomalies.py | Created |
| docs/phase06/prompt.md | Created |
| docs/phase06/anomaly-design.md | Created |
| docs/phase06/reproducibility-evidence.json | Created |
| reports/phase06-anomaly-ground-truth-handoff.md | Created |
| AGENTS.md | Modified |
| README.md | Modified |
| docs/phase01/journal.md | Modified |
| docs/phase01/requirements.md | Modified |

No prior runtime source module, schema, existing test or prior report modified.
All original runtime/schema bytes verified against pre-phase HEAD. No dependency,
new table, enum, trigger change, normal API bypass or disabled FK. The seven small
modules separate input/reference, public rule vocabulary, generation-only cases,
truth IO, detection, post-detection metrics and orchestration; no generic platform.
Generated experiments/databases/truth/findings remain under ignored output/phase06;
test/CLI logs under ignored tmp. Downloadable closure copy under output/reports.

## 3. Architecture and separation

A. **Valid canonical baseline**: Phase 05 source opened mode=ro/query_only=ON,
schema fingerprint and99 domain checks verified; canonical before/after compared.
An owned backup input/baseline.sqlite3 is verified and set0444. Original never
written. Mode bits are accidental-write protection, not OS-owner security.

B. **Observed business input**: input/observations.json contains only format
version, fixed logical as_of and typed entity/identity/time/before/after records.
Full before snapshots match canonical; after columns/types match actual schema.
No labels/seed/scenario IDs/injection flags. These untrusted observations can
contradict canonical projections; they are not newly approved lifecycle actions.

C. **Truth**: separate truth/ground_truth.csv and ground_truth.json, written after
detection. Every label derives independently from its known controlled business
intervention, not detector output or randomly assigned outcomes.

D. **Findings**: detector scans every projected business record using the same
logic for clean/anomalous. Reads baseline+optional observations, never labels,
control reports, scenario IDs, expected decisions, filenames or injection order.

E. **Metrics**: separate evaluator reads completed findings and reloaded truth,
applies business identity matching and measures actual results. No feedback from
truth into detection. Tests audit transitive imports and poison/remove labels.

## 4. Structural versus semantic decisions

All anomalies are external observations. Canonical approved events, submitted
cards, original participants and histories are preserved; no forged success
events inserted to manufacture negatives. Normal APIs still reject their invalid
actions (all prior tests retained).

The detector materializes an owned in-memory backup only. Observed changes apply
under unchanged STRICT/CHECK/FK/unique/recursive-trigger protections. Only allowed
non-key fields change: App status/time, Candidate withdrawal projection, Interview
interval/status, Offer amount and ScorecardItem rubric fields. Only ScorecardItem
can add a new compound row with existing parents. No event/participant/approval/
master/schema edits. Structural errors raise, not suppressed into a semantic PASS.

Six measured structure checks: foreign_key_violations, primary_key_duplicates,
integrity_errors, changed_core_counts, historical_rows_changed and
unrelated_table_changes. Protected content is compared by actual canonical table
hashes; tests compare every changed row against explicit after snapshots.

The business observations intentionally fail targeted semantic rules, so
semantic_valid=false with findings is expected. We do not present their projected
rows as a newly committed, fully 99-rule-valid canonical event chain. Controls are
rule-specific; an upper-bound price observation is band-valid without asserting
a fresh approval under the separate 70%-budget rule. No unrelated canonical
records/history are silently changed to facilitate any case.

## 5. Five types and actual counts

FULL: 5 interventions/type; each N02 two-member pair yields2 distinct staff
violations, so N02=10. Other types 5 each; total 30. STARTER:one/type, N02=2,
total 6. Internal coverage choices, not employer-prescribed volumes.

| Rule | Required issue_type | Starter findings/truth | Full findings/truth | Full TP/FP/FN |
| --- | --- | ---: | ---: | ---: |
| R01 | stage_gate_missing_review | 1 | 5 | 5 /0 /0 |
| R02 | interviewer_double_booked | 2 | 10 | 10 /0 /0 |
| R03 | offer_exceeds_band | 1 | 5 | 5 /0 /0 |
| R04 | withdrawn_still_scheduled | 1 | 5 | 5 /0 /0 |
| R05 | irrelevant_evaluation_criterion | 1 | 5 | 5 /0 /0 |

N01 advances a real incomplete-review application to observed reviewed state.
N02 places two existing shared-panel scheduled interviews on one interval, with
no unrelated candidate conflict; half-open occupied-status checks detect actual
shared Staff. N03 observes positive approved max+delta with correct currency/band
references. N04 alternates individual/candidate withdrawal effective before a
still-scheduled observation. N05 adds an item to a real unsubmitted card using an
existing wrong-requisition criterion. Every violation has a deterministic affected
business key; no five-rejected-calls shortcut or orphaned-reference trick.

## 6. Exact observed examples and independently detected evidence

Actual examples from final full-1 bundle below. Each contains real before/after
input and the independent finding; labels reside separately. Before timestamps
and identities come from canonical data, observed_at/as_of are logical UTC
seconds. Common as_of=origin+196days, after all clean source history.

### R01 — stage_gate_missing_review

```json
{
  "business_observations": [
    {
      "after": {
        "application_id": "APP-CAND-000780-REQ-2026-000056",
        "applied_at": 1773461781,
        "candidate_id": "CAND-000780",
        "requisition_id": "REQ-2026-000056",
        "status": "reviewed",
        "updated_at": 1784160000
      },
      "before": {
        "application_id": "APP-CAND-000780-REQ-2026-000056",
        "applied_at": 1773461781,
        "candidate_id": "CAND-000780",
        "requisition_id": "REQ-2026-000056",
        "status": "interviewing",
        "updated_at": 1781866920
      },
      "entity_id": "APP-CAND-000780-REQ-2026-000056",
      "entity_type": "Application",
      "observed_at": 1784160000
    }
  ],
  "independent_finding": {
    "affected_entity_id": "APP-CAND-000780-REQ-2026-000056",
    "affected_entity_type": "Application",
    "evidence_timestamps": [
      1784160000
    ],
    "expected_invariant": "Review-dependent stages require every completed, submitted, applicable evaluation and review policy.",
    "explanation": "Observed advancement is unsupported by required review evidence.",
    "finding_id": "FIND-27aa6301b1837d55d2f1eb61",
    "issue_type": "stage_gate_missing_review",
    "observed_values": {
      "decision_failure": "REVIEW_GATE_INCOMPLETE: Every assigned reviewer must submit a complete evaluation after completion",
      "evaluation_states": [
        {
          "interview_id": "INT-2026-000856",
          "interview_status": "completed",
          "scorecard_id": "SCORE-INT-2026-000856-STAFF-000033",
          "scorecard_status": "submitted",
          "staff_id": "STAFF-000033"
        },
        {
          "interview_id": "INT-2026-000856",
          "interview_status": "completed",
          "scorecard_id": "SCORE-INT-2026-000856-STAFF-000060",
          "scorecard_status": "submitted",
          "staff_id": "STAFF-000060"
        },
        {
          "interview_id": "INT-2026-000856",
          "interview_status": "completed",
          "scorecard_id": "SCORE-INT-2026-000856-STAFF-000086",
          "scorecard_status": "incomplete",
          "staff_id": "STAFF-000086"
        }
      ],
      "stage": "reviewed"
    },
    "related_entity_ids": {
      "candidate_id": "CAND-000780",
      "requisition_id": "REQ-2026-000056"
    },
    "rule_id": "R01",
    "severity": "high"
  },
  "scenario_id": "SCN-07ebbfb1b4dbcd4e24e638b0"
}
```
### R02 — interviewer_double_booked

```json
{
  "business_observations": [
    {
      "after": {
        "application_id": "APP-CAND-000357-REQ-2026-000141",
        "end_at": 1781533800,
        "interview_id": "INT-2026-000541",
        "panel_id": "PANEL-000141",
        "requisition_id": "REQ-2026-000141",
        "start_at": 1781530200,
        "status": "scheduled"
      },
      "before": {
        "application_id": "APP-CAND-000357-REQ-2026-000141",
        "end_at": 1781533800,
        "interview_id": "INT-2026-000541",
        "panel_id": "PANEL-000141",
        "requisition_id": "REQ-2026-000141",
        "start_at": 1781530200,
        "status": "scheduled"
      },
      "entity_id": "INT-2026-000541",
      "entity_type": "Interview",
      "observed_at": 1784160000
    },
    {
      "after": {
        "application_id": "APP-CAND-002037-REQ-2026-000141",
        "end_at": 1781533800,
        "interview_id": "INT-2026-001741",
        "panel_id": "PANEL-000141",
        "requisition_id": "REQ-2026-000141",
        "start_at": 1781530200,
        "status": "scheduled"
      },
      "before": {
        "application_id": "APP-CAND-002037-REQ-2026-000141",
        "end_at": 1781620200,
        "interview_id": "INT-2026-001741",
        "panel_id": "PANEL-000141",
        "requisition_id": "REQ-2026-000141",
        "start_at": 1781616600,
        "status": "scheduled"
      },
      "entity_id": "INT-2026-001741",
      "entity_type": "Interview",
      "observed_at": 1784160000
    }
  ],
  "independent_finding": {
    "affected_entity_id": "INT-2026-000541",
    "affected_entity_type": "Interview",
    "evidence_timestamps": [
      1784160000
    ],
    "expected_invariant": "Capacity-occupying intervals for one interviewer must not overlap; adjacent intervals are valid.",
    "explanation": "Both assigned interview intervals overlap under the half-open rule.",
    "finding_id": "FIND-1351856a9e3d7e0db66b4d5c",
    "issue_type": "interviewer_double_booked",
    "observed_values": {
      "first_end": 1781533800,
      "first_id": "INT-2026-000541",
      "first_start": 1781530200,
      "first_status": "scheduled",
      "second_end": 1781533800,
      "second_id": "INT-2026-001741",
      "second_start": 1781530200,
      "second_status": "scheduled",
      "staff_id": "STAFF-000065"
    },
    "related_entity_ids": {
      "interview_ids": [
        "INT-2026-000541",
        "INT-2026-001741"
      ],
      "staff_id": "STAFF-000065"
    },
    "rule_id": "R02",
    "severity": "high"
  },
  "scenario_id": "SCN-f6724020312d12f2ac786803"
}
```
### R03 — offer_exceeds_band

```json
{
  "business_observations": [
    {
      "after": {
        "amount_minor": 222462278,
        "application_id": "APP-CAND-001947-REQ-2026-000007",
        "approved_requisition_event_id": "REQEV-000027",
        "currency": "INR",
        "is_final": 1,
        "offer_id": "OFF-2026-000133",
        "requisition_id": "REQ-2026-000007",
        "status": "accepted",
        "valid_from": 1783475930,
        "valid_to": null
      },
      "before": {
        "amount_minor": 186466900,
        "application_id": "APP-CAND-001947-REQ-2026-000007",
        "approved_requisition_event_id": "REQEV-000027",
        "currency": "INR",
        "is_final": 1,
        "offer_id": "OFF-2026-000133",
        "requisition_id": "REQ-2026-000007",
        "status": "accepted",
        "valid_from": 1783475930,
        "valid_to": null
      },
      "entity_id": "OFF-2026-000133",
      "entity_type": "Offer",
      "observed_at": 1784160000
    }
  ],
  "independent_finding": {
    "affected_entity_id": "OFF-2026-000133",
    "affected_entity_type": "Offer",
    "evidence_timestamps": [
      1784160000
    ],
    "expected_invariant": "Observed offer amount must not exceed its historically approved same-currency maximum.",
    "explanation": "Observed amount exceeds the linked approved band.",
    "finding_id": "FIND-0ecf4488a20e73ad983c5b12",
    "issue_type": "offer_exceeds_band",
    "observed_values": {
      "amount_minor": 222462278,
      "approved_max_minor": 222452500,
      "currency": "INR",
      "excess_minor": 9778
    },
    "related_entity_ids": {
      "application_id": "APP-CAND-001947-REQ-2026-000007",
      "band_event_id": "REQEV-000027",
      "requisition_id": "REQ-2026-000007"
    },
    "rule_id": "R03",
    "severity": "high"
  },
  "scenario_id": "SCN-9e4ea8e4fa653edafc32716c"
}
```
### R04 — withdrawn_still_scheduled

```json
{
  "business_observations": [
    {
      "after": {
        "candidate_id": "CAND-002480",
        "contact_email": "candidate002480@example.invalid",
        "created_at": 1771749000,
        "display_name": "Synthetic Candidate 002480",
        "experience_years": 5,
        "status": "withdrawn",
        "withdrawn_at": 1784142555
      },
      "before": {
        "candidate_id": "CAND-002480",
        "contact_email": "candidate002480@example.invalid",
        "created_at": 1771749000,
        "display_name": "Synthetic Candidate 002480",
        "experience_years": 5,
        "status": "active",
        "withdrawn_at": null
      },
      "entity_id": "CAND-002480",
      "entity_type": "Candidate",
      "observed_at": 1784160000
    },
    {
      "after": {
        "application_id": "APP-CAND-002480-REQ-2026-000040",
        "end_at": 1782383400,
        "interview_id": "INT-2026-000840",
        "panel_id": "PANEL-000040",
        "requisition_id": "REQ-2026-000040",
        "start_at": 1782381600,
        "status": "scheduled"
      },
      "before": {
        "application_id": "APP-CAND-002480-REQ-2026-000040",
        "end_at": 1782383400,
        "interview_id": "INT-2026-000840",
        "panel_id": "PANEL-000040",
        "requisition_id": "REQ-2026-000040",
        "start_at": 1782381600,
        "status": "scheduled"
      },
      "entity_id": "INT-2026-000840",
      "entity_type": "Interview",
      "observed_at": 1784160000
    }
  ],
  "independent_finding": {
    "affected_entity_id": "INT-2026-000840",
    "affected_entity_type": "Interview",
    "evidence_timestamps": [
      1784160000
    ],
    "expected_invariant": "No scheduled reservation may remain active after effective candidate/application withdrawal.",
    "explanation": "Scheduled booking persists after a withdrawal effective before this observation.",
    "finding_id": "FIND-2dc1e9f1758463f95696642d",
    "issue_type": "withdrawn_still_scheduled",
    "observed_values": {
      "end_at": 1782383400,
      "start_at": 1782381600,
      "status": "scheduled",
      "withdrawals": [
        {
          "scope": "candidate",
          "withdrawn_at": 1784142555
        }
      ]
    },
    "related_entity_ids": {
      "application_id": "APP-CAND-002480-REQ-2026-000040",
      "candidate_id": "CAND-002480"
    },
    "rule_id": "R04",
    "severity": "high"
  },
  "scenario_id": "SCN-6864e8437167c0c048bcde70"
}
```
### R05 — irrelevant_evaluation_criterion

```json
{
  "business_observations": [
    {
      "after": {
        "evidence": "Recorded structured rubric observation.",
        "score_value": 2,
        "scorecard_id": "SCORE-INT-2026-000176-STAFF-000074",
        "skill_requirement_id": "SKILL-000635",
        "status": "scored",
        "weight_basis_points": 2486
      },
      "before": null,
      "entity_id": "SCORE-INT-2026-000176-STAFF-000074|SKILL-000635",
      "entity_type": "ScorecardItem",
      "observed_at": 1784160000
    }
  ],
  "independent_finding": {
    "affected_entity_id": "SCORE-INT-2026-000176-STAFF-000074",
    "affected_entity_type": "Scorecard",
    "evidence_timestamps": [
      1784160000
    ],
    "expected_invariant": "Each rubric item must be from this interview's applicable requisition and effective version.",
    "explanation": "Existing criterion reference is semantically irrelevant to this scorecard.",
    "finding_id": "FIND-7746641661a9be41056ca1bd",
    "issue_type": "irrelevant_evaluation_criterion",
    "observed_values": {
      "criterion_requisition": "REQ-2026-000159",
      "criterion_version": 1,
      "interview_id": "INT-2026-000176",
      "requisition_id": "REQ-2026-000176",
      "rubric_version": 1,
      "scorecard_id": "SCORE-INT-2026-000176-STAFF-000074",
      "skill_requirement_id": "SKILL-000635",
      "valid_from": 1768123042,
      "valid_to": null
    },
    "related_entity_ids": {
      "criterion_id": "SKILL-000635",
      "interview_id": "INT-2026-000176",
      "requisition_id": "REQ-2026-000176"
    },
    "rule_id": "R05",
    "severity": "high"
  },
  "scenario_id": "SCN-2fa7cac30ef2499e042b9b88"
}
```

## 7. Truth and report locations

Final actual FULL pair:

- `output/phase06/repro-final-20261022/full-1/truth/ground_truth.csv`
- `output/phase06/repro-final-20261022/full-1/truth/ground_truth.json`
- Equivalent independently built files under full-2/truth/.
- Starter equivalents under starter-1/truth/ and starter-2/truth/.

Business inputs are only input/baseline.sqlite3 and input/observations.json.
reports/clean-validation.json records clean source/domain/detection;
reports/observation-structure.json records structure;
reports/findings.json records semantic failures;
reports/controls.json explains boundaries;
reports/evaluation.json records post-detection metrics;
reports/experiment.json summarizes this experiment, not a final release manifest.

Truth fields: scenario_id,issue_type,affected_entity_type,affected_entity_id,
related_entity_ids,expected_decision,rule_id,observed_violation,severity,
applicable_timestamp,deterministic_seed. Nested CSV fields are stable JSON and
numeric fields decode to ints; complete CSV rows equal JSON records exactly.
SCN IDs hash intervention identity+seed and exist only in truth/evaluation, not
input features. Severity high reflects serious recruiting-rule violations.

## 8. Isolation proof and detector independence

- Detector and all transitive source imports exclude injection, truth and
  post-detection evaluation/orchestration modules; AST test executed.
- Detector finishes clean and anomalous scans before truth serialization; an
  instrumented ordering test verified both calls happened first.
- Poisoned/missing truth files do not change findings. Reversed observations and
  a label-like filename do not change results. No injection sequence consulted.
- Strict envelope/row schemas reject scenario_id, issue_type, ground_truth,
  expected_decision and is_injected metadata. After rows contain business schema
  fields only. Existing canonical JSON/features have no anomaly answer labels.
- Detector scans all rows after projection; it does not assume observations are
  invalid. Six near-miss/control cases share the same format and are evaluated.
- Truth is computed from controlled interventions/source relationships without
  detector imports/calls. Metric code consumes labels only after findings exist.

Static rule vocabulary includes issue_type names because output requires them;
it contains no record-specific answers. Reuse of existing pure review/rubric
predicates is legitimate domain-rule reuse, not truth lookup.

## 9. Actual findings by rule and explanations

R01=5: observed advanced app lacks required completed/submitted applicable
reviews; evidence includes actual reviewer/card states and failure reason.
R02=10: actual pair+Staff overlap with both capacity statuses; exact intervals
shown. Cancelled excluded; adjacent allowed. Each Staff/pair reported once.
R03=5: amount>historically approved same-currency max; observed amount/max/excess
and band reference shown. Equality valid.
R04=5: scheduled row persists after effective Candidate/App withdrawal; actual
scope/time/app/candidate IDs shown. Completed/cancelled histories excluded.
R05=5: existing criterion outside interview's requisition/effective rubric;
source criterion/scorecard versions, intervals and references shown.

Every finding has content-key FIND ID, rule/issue, primary/related identity,
observed values, invariant, explanation, evidence time and severity. No unexpected
findings were dropped. Full expected 30 matched actual 30; clean engine found 0.

## 10. TP/FP/FN, precision/recall/F1 and matching

| Dataset | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Starter controlled | 6 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| Full controlled | 30 | 0 | 0 | 1.0 | 1.0 | 1.0 |

Per-rule metrics in section5 all precision/recall/F1=1.0; all five rules have true
positives. Duplicate findings0, unexpected IDs empty, missed scenario IDs empty.
These results are measured from actual findings and separate truth.

TP requires correct rule+issue+affected entity and relevant related keys. R02
uses unordered interview pair AND Staff, independent of pair ordering; R03 needs
Offer+band+app+req; R05 needs Scorecard+criterion+interview+req; R04 needs
Interview+app+candidate; R01 needs App+candidate+req. A truth key earns credit once.
A repeated finding becomes FP/duplicate rather than another TP. Wrong related
Staff/criterion/band cannot receive credit. Unexpected findings always count FP.

Precision=TP/(TP+FP); recall=TP/(TP+FN); F1=2TP/(2TP+FP+FN).
Undefined denominators are JSON null; only misses/false positives give F1=0.
No accuracy/TN count is reported without a defensible exhaustive negative universe.
Tests explicitly measure a TP5/FP1/FN1 fixture (precision/recall/F1=5/6), duplicates,
wrong identities, pair reversal and zero-denominator cases, not only perfect runs.

## 11. Clean false positives and boundary controls

Both clean references:0 findings, semantic_valid=true, all 99 Phase 05 domain checks
zero. Same detector for both input types. Six explicit per-rule controls in each
bundle: adjacent scheduled pair, cancelled overlapping booking, exact-upper
amount, applicable criterion, unsubmitted card without advancement, completed
interview followed by later individual withdrawal. Actual control IDs are in
reports/controls.json and identical across replay pairs.

The last two intentionally share the R05 app/card; it still has its separately
labelled irrelevant-criterion issue. The rule-specific clean statuses themselves
produce no R01/R04 finding. This limited overlap is documented, not hidden.
Full canonical source supplies many additional normal records. No true-negative
universe is invented from control count or all source rows.

## 12. Structural results and exact counts

Each source passes unchanged99 clean domain checks. Each observed view passes
all6 structural/content-protection checks with zero violations. PK unique, FKs
resolve, actual SQLite scalar/enum/range/uniqueness constraints retained;
protected event/participant/unrelated table hashes identical. Bad references,
bools/types, before mismatches/extra labels are rejected by real tests.

| Table | Starter clean /observed rows | Full clean /observed rows |
| --- | ---: | ---: |
| Application | 160 /160 | 8,000 /8,000 |
| ApplicationEvent | 312 /312 | 14,843 /14,843 |
| Approval | 17 /17 | 429 /429 |
| ApprovalEvent | 34 /34 | 858 /858 |
| Availability | 320 /320 | 2,680 /2,680 |
| Candidate | 100 /100 | 5,000 /5,000 |
| CandidateEvent | 102 /102 | 5,083 /5,083 |
| CandidateSkill | 522 /522 | 27,061 /27,061 |
| HiringManager | 2 /2 | 20 /20 |
| Interview | 40 /40 | 2,000 /2,000 |
| InterviewEvent | 62 /62 | 3,147 /3,147 |
| InterviewPanel | 10 /10 | 200 /200 |
| InterviewParticipant | 96 /96 | 5,000 /5,000 |
| Offer | 7 /7 | 229 /229 |
| OfferEvent | 33 /33 | 957 /957 |
| PanelMember | 24 /24 | 500 /500 |
| Requisition | 10 /10 | 200 /200 |
| RequisitionEvent | 40 /40 | 800 /800 |
| SchemaMetadata | 1 /1 | 1 /1 |
| Scorecard | 24 /24 | 1,122 /1,122 |
| ScorecardEvent | 132 /132 | 6,066 /6,066 |
| ScorecardItem | 96 /97 | 4,488 /4,493 |
| SkillRequirement | 40 /40 | 800 /800 |
| Staff | 14 /14 | 91 /91 |

Only extra observed ScorecardItem keys increase logical projection row count
(one starter/five full); existing canonical card/items are not modified/deleted.
All four scale targets and all legitimate scorecards/offers/approvals/assignments/
events in the actual canonical database remain unchanged. Observation records:
13 starter /41 full, including controls and unchanged contextual snapshots.

## 13. Baseline preservation evidence

Read-only source canonical checksum is compared before copying, after verified
backup, and after complete experiment. Source copy matches. Every old runtime
module and schema remains byte-identical to Phase 05 HEAD. Schema version2,
24 tables/209 fields/45 FK groups/42 protection triggers retained. No migration.
Dictionary freshness passes; all 148 previous tests still pass.

Clean SHA256 unchanged from Phase 05 evidence:

- Starter: `d58886c7f9758d7fb03139416493ff94bba6577d63097ecf3e623365f70d2cfe`.
- Full: `7362b01eeb0aa15999480aa8b0a810d96ff21060bd06f9b230eb637d57642ebb`.

Tests compare every source/projected row difference to the explicit allowed
observations, verify read-only update rejection and compare source bytes/content
before/after. Binary equality is secondary accidental-write evidence; canonical
logical hashes/every-row replay are primary. Canonical history not weakened.

## 14. Actual commands/tests and results

Read-only inspection: git status/branch/log/ignored paths, AGENTS/README,
original statement/PDFs, prior handoffs/matrix/dictionary/schema/modules/tests and
repro evidence using cat/rg/sed/Python. Sources match manifest SHA/size; both full
one-page PDF texts extracted read-only with bundled pypdf/PDF skill. Some large
repetitive output truncated; exact fields/enums/history used from inspected
sections and preserved context. No external core solution/dependency fetched.

| Actual executed command | Observed result |
| --- | --- |
| `PYTHONPATH=src .venv/bin/python3 -m yottaflex.anomalies --baseline output/phase05/repro-final-20261022/starter-1.sqlite3 --directory output/phase06/initial-starter --profile starter` | exit 0;6 genuine findings/truth; clean0; initial structure/metrics passed |
| same command with `full-1.sqlite3`, `initial-full`, `--profile full` | exit 0;30 findings/truth; clean0; initial full total 6.199590s |
| same starter command to checked-starter after structure/metric hardening | exit 0;6 checks zero; by-rule/type metrics measured |
| `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -p test_anomalies.py -v` | 34 new tests passed,24.971s before final version-boundary addition |
| `PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v` | **183 tests in 88.584s, OK, exit 0**, final35 new +all 148 previous |
| `PYTHONPATH=src .venv/bin/python3 scripts/verify_anomaly_reproducibility.py --directory output/phase06/repro-final-20261022 --profile both --seed 20261022` | exit 0; two independent bundles/profile; all ordered rows/files/counts/hashes/metrics matched |
| `cp output/phase06/repro-final-20261022/reproducibility.json docs/phase06/reproducibility-evidence.json` | success; evidence preserved unchanged |
| `PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/phase06/repro-final-20261022/full-1/input/baseline.sqlite3 --observations output/phase06/repro-final-20261022/full-1/input/observations.json` | exit 0;30 visible semantic findings, structure valid; matches bundle report |
| same detector command without --observations | exit 0;0 clean findings |
| `PYTHONPATH=src .venv/bin/python3 -m yottaflex.evaluation_checks --database output/phase06/repro-final-20261022/full-1/input/baseline.sqlite3 --profile full` | exit 0;99 checks zero; unchanged clean baseline valid |
| `PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check` | exit 0; every field/constraint matches actual SQL/metadata |
| `PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh` | exit 0;4 shell +3 Python groups; source/runtime/privacy passed |
| `git diff --check` and Python preservation assertions | no whitespace errors; original 75 rows, all old runtime/schema and complete prompt bytes unchanged |

No failed test/generation run in this phase. A documentation journal patch had
incorrect context, applied nothing and was corrected by append. Malformed inputs,
locked/existing outputs and injected IO failures are intentional
isolated tests, not fake PASS output or normal success events.

New 35 tests cover all 28 requested topics: all five real cases/detections,
clean findings, transitive label isolation/missing-label/order/filename tests,
adjacent/cancelled/upper/correct-criterion/incomplete/historical controls,
candidate/app withdrawal, wrong requisition/future effective version, every
reference/PK/FK/scalar, immutable source and exact changed-row comparison, agreed
CSV/JSON, TP/FP/FN/duplicate/related-key metrics, same engine/replay/different seed,
no partial output on IO failure, no overwrite/unowned lock deletion and full
counts/old Phase 05 hash. All prior 148 tests executed unchanged in combined suite.

## 15. Same-seed checksum/every-row evidence

Seed 20261022; fixed logical as_of, no wall-clock/path/temp name in deterministic
content. Fresh valid starter/full baselines generated, then two independently
verified bundles/profile. All24 projected tables compared in PK order, plus
counts/per-table/aggregate hashes and every observation/truth/finding/metric/
control report byte. No raw SQLite binary hash as primary proof.

| Profile | Projected rows compared | Anomalous projection SHA256 | Baseline+observation input SHA256 |
| --- | ---: | --- | --- |
| starter | 2199 | 6915576660591d1194914f742bbf23fed147bc67a71f315ca9b25a6b16614e92 | 991d87e434f4b77c277d4a20c4e7b05e58c26be1d90ffda7fa36a536cc55c2ab |
| full | 89580 | 65cd10bb60b62eb825fb7853cea995c4755ad7fdae4fed530ce7bc78b6cebe26 | cd8f04ec144ee4f1284234857daa5afb2217355d21d24c8992ce441f1f2514df |

Truth checksums (CSV and JSON need not have the same byte hash; decoded records
are exactly equal):

| File | Starter SHA256 | Full SHA256 |
| --- | --- | --- |
| ground_truth.csv | 032844e4ff6fdc6f39a82078bd6b8efeb63ff836ad48673e48e09a0691a82b9a | 860469ee6b8ff4ff29f5fbdbe6055e301ee4326c7417b6c079246f33f4bf793d |
| ground_truth.json | 62da2af6e643806a58dacbe246015d65c6527a9081605f173a1a678330e9a8e9 | 205b31bdb6abce3c9c84889f658b7e64ac710ef5102dbadf7431307d660e4688 |

All remaining file hashes/counts/comparisons in
`docs/phase06/reproducibility-evidence.json`, an unedited copy of the actual run.
Clean master/interview/evaluation generation functions were not changed; prior
hash regression suite remains green. Different anomaly seed changes selected
inputs/deltas/SCN labels while preserving clean source; test actually executed.

## 16. Measured performance

Local Python 3.14.5/SQLite 3.53.1; seconds diagnostic, not deterministic features or
speed guarantee. Detection timing includes clean+anomalous scans and structural
projection. Injection time includes observation structure and projected hash;
total includes truth/reports/evaluation/hash/safe publication.

| Profile/run | Bundle total | Baseline validation/copy | Injection/structure/hash | Detection |
| --- | ---: | ---: | ---: | ---: |
| starter 1 | 0.184593 | 0.075220 | 0.043869 | 0.051706 |
| starter 2 | 0.160387 | 0.051432 | 0.043404 | 0.051671 |
| full 1 | 5.763966 | 2.160549 | 1.462015 | 1.798638 |
| full 2 | 5.818591 | 2.198144 | 1.423910 | 1.851127 |

Fresh clean generation during final replay: starter0.330640s,
full17.574610s. Whole two-profile replay including
baseline generation, four bundles and every-row/file comparison:
**31.699756s**. No peak-RSS measurement fabricated. Required
scale is manageable with simple local SQLite/in-memory view; no new infrastructure.

## 17. Known limitations and risks

1. Detection covers the five mandated invariants, not all possible business/
   historical/security violations. These are observed projections, not newly
   committed canonical transactions. Rule-specific controls must not be sold as
   full 99-rule canonical transaction acceptance.
2. Perfect controlled-case metrics do not establish recall/precision on unknown
   real data. No TN universe/accuracy or random expected-success claim.
3. Independent truth derives from designed interventions, not external human
   adjudication. Human policy/data/metric review and all-tools prompt audit pending.
4. SQLite/schema/input structure is enforced, but a machine owner can alter files.
   Read-only references/hash checks prevent accidental mutation, not hostile OS use.
5. Publication lock serializes cooperating writers; host directory rename semantics
   leave a narrow noncooperating empty-directory race. Existing observed outputs
   and owned failure cleanup are actually tested; no cross-process security claim.
6. Current baseline profile/default origin/seed must match declared config;
   insufficient requested cases/controls fail explicitly. Scenario volumes are
   internal test choices. No auto calendar extension/normal API weakening.
7. Generalized seed exports, SQL re-import, final delivery manifest/public setup
   and submission remain incomplete. Privacy smoke is a baseline, not exhaustive
   secret/real-person detection. Original send-time/round/channel ambiguities and
   final human ownership/release review remain open.

## 18. Requirements coverage

Original 75 source rows intact; Phase 06 overlay appended in requirements.md.
N01–N05 now have genuine controlled input violations, separate source-derived
truth and independent findings/metrics. D12–D18 valid-first/controlled injection/
no unrelated corruption/derived labels/truth separation/variation/controls are
implemented at this phase boundary. D21–D22 and V01–V09 actual structure/domain/
matching/replay evidence extend preserved clean workflows. S03–S09 prompt/AI/
verification/reasoning/commits/individual-work records updated; human ownership
is not fabricated. Other functional/entity/ID/scale/quality/lawful/optional/admin
requirements retained with no deletions.

Still incomplete: D19 generalized CSV/JSON/SQL data exports, final D20 artifact
bundle/manifests, export-level import/ID/join/equivalence/reproducibility checks,
final release narrative/public GitHub/visibility/submission/admin gates. Optional
UI/hosting not required. No complete-challenge PASS claimed.

## 19. AI disclosure and human review

Codex generated all new code/tests/docs and executed every reported check. No
subagents, other-person implementation, other generative service, external corpus,
paid service or new dependency. PDF skill used read-only for official sources.
Complete 21-section prompt in docs/phase06/prompt.md has SHA256
`b3c4c23b021d36e7c7a3d596eb88b9f754c0c612a906cf5fb8ffe18458e8dadb`.
P009/H026–H029 preserve the user's conditional Phase 05 approval separately from
AI implementation and pending human Phase 06 personal testing/line understanding.
No additional human prompt this phase at report preparation. Prior complete
available prompts/reports/export limits retained; human audit of any other tools/
chats remains required. No AI-run result is attributed to human review.

## 20. Local Git state and commits

Initial HEAD d00e2eb (Phase 05 handoff). Original branch/commits preserved.
Implementation commit: `1f53d85ae976bfb59c4e19dcec51c90ca38c33c6`.
Message: `feat: add isolated anomaly observations and independent detection`.
Handoff message: `docs: record phase 06 anomaly evidence and handoff`.
Only explicit reviewed code/test/docs/safe evidence staged; no raw PDFs/private
source, credentials, real candidate information, DB or scratch artifacts.
This report gets a separate local commit; final full hashes and clean state are
appended in the ignored downloadable closure copy to avoid self-reference loops.
No push/merge/remotes/publish/contact/submission.

## 21. Phase 07 recommendations and stop

**Phase 06 PASS:** valid unchanged clean baseline; exact mandatory counts; all five
real semantic types/labels/findings; agreed isolated truth; independent same-engine
clean/anomalous detection; correct identity matching/metrics; structure/history/
unrelated-row protections; boundary controls; full replay; all 183 tests; honest
limits/deferred exporter scope. Human review pending.

After explicit Phase 07 authorization, regenerate reviewed synthetic baseline and
Phase 06 artifacts; implement all-table CSV/JSON/SQL seed exporters, deterministic
round-trip import/FK/count/content equivalence and complete final deliverables.
Planned public artifact layout: artifacts/phase06/input/observations.json,
artifacts/phase06/truth/ground_truth.csv+json and reports/*.json, linked to reviewed
canonical baseline exports under artifacts/baseline/. Include only safe synthetic
content and provenance/commands/checksums after human review. Do not copy private
assignment sources or local scratch DBs indiscriminately. Complete release
metadata and public setup/submission only in their separately authorized scope.

**STOP HERE. No Phase 07 exporter/re-import/manifest/public setup work started.**


Actual Git closure so far: explicitly staged16 intended implementation/test/
documentation/evidence files; staged whitespace/file/schema/prompt/privacy checks
passed. Implementation commit above succeeded with generic Codex local identity.
Immediately afterward only this report remained untracked; source work committed.
Final pre-report smoke passed4 shell +3 Python groups,71 publication candidates.
This report is committed separately; final full hashes/clean-tree state follow
in the ignored downloadable closure copy. No publication or later-phase work.
