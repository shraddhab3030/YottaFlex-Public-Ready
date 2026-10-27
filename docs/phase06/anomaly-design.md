# Phase 06 controlled observations, isolated truth and independent detection

User P009 explicitly authorizes Phase06 after conditional Phase05 approval.
Scope: five genuine semantic violations, independent findings/metrics, controls,
structural checks and reproducibility. No generalized exporter, re-import,
release manifest, dashboard, public setup or submission. All prior code/schema/
workflow guards remain unchanged. Python3.14.5 stdlib/SQLite, no new dependencies.

## Representation and immutable reference

The canonical Phase05 database remains valid and is never mutated in place.
The experiment command opens it with SQLite mode=ro and query_only=ON, verifies
schema fingerprint, all99 Phase05 domain checks and canonical content, then
backs it up to a new owned input/baseline.sqlite3. The copy is made read-only
(0444) after verification. Canonical before/after/source-copy hashes are compared.
File mode is an accidental-write guard; content verification and read-only access
are the reproducibility guarantee, not a claim of OS-owner security.

All five anomalies use **external business observations**, not forged canonical
history or ordinary workflow API bypasses. JSON envelope: format_version1,
as_of UTC integer epoch seconds, observations array. Each record contains exactly
entity_type, entity_id, observed_at, before, after. Before is the exact canonical
row or NULL for an additional ScorecardItem; after has exactly the actual schema
columns. Compound ScorecardItem identity is scorecard_id|skill_requirement_id.
No scenario/seed/issue/expected-decision/label/injection flag is an input feature.

These are untrusted observed projections, not successful domain operations or
new approvals. Their old/new values and actual references are detector-visible.
Canonical events remain the authoritative historical source. The detector first
projects observations into an isolated in-memory backup, with the original FK,
STRICT, CHECK, uniqueness and recursive triggers ON, then scans **all business
rows**, not only observed/changed records. No events/participants/schema/approvals
are editable in this representation. Only supported non-key projection fields
may differ; only ScorecardItem may introduce a new compound row with valid FKs.
It never commits that observed view back to disk/canonical source.

Current protocols permit status/updated_at for Application, status/withdrawn_at
for Candidate, interval/status for Interview, amount_minor for Offer, and item
rubric fields for ScorecardItem. Row identities and all unrelated fields are
fixed; every before snapshot must match. Wrong scalar types, unknown metadata,
unknown references, duplicate observations or malformed enums fail structurally.

## Separation and directory layout

```text
experiment/
  input/
    baseline.sqlite3       # verified read-only canonical reference
    observations.json      # business snapshots only, mixed controls/deviations
  truth/
    ground_truth.csv
    ground_truth.json
  reports/
    clean-validation.json  # A: clean structure/domain + clean detector
    observation-structure.json # B: observed view structure/content protections
    findings.json          # C: independent semantic findings
    controls.json          # coverage explanation, NOT a detector input
    evaluation.json        # E: post-detection comparison with D: truth above
    experiment.json        # experiment checksums/counts/summary, not final release manifest
```

Pipeline order: validate/reference→create observations→run clean and anomalous
 detector→serialize truth→evaluate findings against reloaded CSV/JSON-agreed
labels. Detector API accepts database and optional observations only; it has no
truth, scenario or experiment-directory argument. Its transitive dependencies
exclude injection/truth/metric modules. It cannot discover cases from filenames,
SCN IDs, seed, injection order or expected labels. Controls share the same input
record schema as violations. Tests poison/remove labels, reorder observations,
change filenames, and audit imports without changing findings.

## Five rules, intervention mechanics and matching

| Rule/type | Genuine observed violation | Evidence/invariant | Matching identity |
| --- | --- | --- | --- |
| R01 stage_gate_missing_review | actual pre-review app with unsubmitted cards observed as reviewed | all noncancelled meetings completed; every assigned reviewer complete/submitted/applicable; persisted totals and review policy reconcile | rule+type+Application+candidate+requisition |
| R02 interviewer_double_booked | two actual scheduled interviews with identical shared-panel interval | capacity statuses scheduled/completed/no_show; half-open overlap; shared immutable assigned Staff | rule+unordered interview pair+Staff |
| R03 offer_exceeds_band | actual offer amount observed as approved max+positive seeded delta | correct same-currency historical approved RequisitionEvent; amount>max | rule+Offer+band event+Application+requisition |
| R04 withdrawn_still_scheduled | effective app/candidate withdrawal with an interview observed still scheduled | withdrawal effective<=as_of; scheduled reservation still active | rule+Interview+Application+Candidate |
| R05 irrelevant_evaluation_criterion | extra observed item on a real unsubmitted Scorecard, referencing an existing wrong-requisition criterion | effective interview-time applicable requirement version/requisition; no orphan | rule+Scorecard+criterion+Interview+requisition |

R01 reuses the existing read-only evaluation predicate, not labels. Findings show
observed stage, actual interview/reviewer/card states and failure reason. Other
rules use explicit joins/business predicates; R05 uses applicable_criteria from
the established rubric policy. Detector never consults injector selections.

N02 selects two-member panels and disjoint candidate/apps, with no existing
candidate conflict at the replacement slot. One interval already belongs to the
same panel and calendars, so moving the other observation there avoids unrelated
availability/participant/candidate problems. Each shared Staff is a separate
violation: five pairs produce10 staff-specific findings, not duplicate credits.
Pairs are sorted for identity, regardless of which observation arrived first.

N03 preserves offer/application/requisition/currency/band references. Amounts
remain positive integers, only the upper bound is violated. Historical band and
unrelated approval records are never manipulated. Amount observations are not a
claim that a fresh approval/acceptance happened at that value.

N04 uses as_of=origin+196days (after clean history) with withdrawal between one
hour and one day earlier. Application-level and candidate-wide cases alternate;
candidate-wide selections have exactly one current scheduled booking, preventing
hidden cascades. A past but unresolved scheduled row still occupies capacity;
completed/cancelled meetings are not active just because withdrawal occurs later.

N05 uses an unsubmitted card on a different app from N01, so its extra criterion
cannot create an unlabelled advanced-stage failure. The extra item's criterion,
weight/value/evidence/status satisfy scalar/FK rules; semantic applicability is
wrong. Tests additionally cover an existing same-requisition future-version
criterion that is not effective at the interview, not only wrong requisitions.

## Counts, controls and rule scope

Defaults: full5 interventions/type, starter1. Full N02 yields10 staff-specific
occurrences; other types5 each, total30. Starter total6. These modest internal
coverage goals are not employer-prescribed counts. Insufficient selectable cases
or controls fail with actionable diagnostics; no silent count reduction.
Selection starts from sorted canonical queries with seeded shuffling; only
synthetic source selection/deltas vary, never independent random truth labels.

Six explicitly documented controls:

- Adjacent scheduled intervals: end==next.start, no R02.
- Cancelled booking overlapping a real slot: no occupied capacity/R02.
- Offer exactly at approved upper boundary: no R03.
- Correct existing effective criterion: no R05.
- Unsubmitted card without advanced app state: no R01.
- Completed interview before a later individual app withdrawal: no R04.

Controls are **rule-specific**. The last two intentionally share the R05 card/app
while preserving its separate labelled criterion violation; this overlap is
explicit and represented in truth. Full canonical clean data supplies many more
normal rows. An exact-upper amount is valid for the band rule even if a new
approval under the separate70%-budget policy would reject it; no new approval is
asserted by that observation. An external observed projection is not represented
as a newly committed Phase05 event chain. We do not claim that replaying these
untrusted row views through all99 canonical history checks is valid. Canonical
history itself remains unchanged and passes those checks.

## Truth schema and independent evaluation

Both formats contain exactly scenario_id, issue_type, affected_entity_type,
affected_entity_id, related_entity_ids, expected_decision, rule_id,
observed_violation, severity, applicable_timestamp, deterministic_seed.
Nested objects use canonical JSON in CSV; integer fields decode back to integers.
Loaded CSV rows must equal JSON exactly. Each SCN ID hashes its intervention
identity+seed and exists only in labels. Labels arise from actual interventions:
known missing cards, shared real assignments/intervals, approved max+delta,
withdrawal-before-active, and a provably different existing requirement.
The injector does not call the detector to decide labels or tune expected counts.

Findings contain deterministic content-key ID, rule/issue, primary and related
references, actual values, expected invariant, explanation, evidence timestamp and
severity. Rule-specific business key matching requires relevant related IDs;
wrong Staff/criterion/band cannot receive credit. One truth key can be credited
once. Repeated findings count as FP plus duplicate count; unexpected findings
are not ignored. Truth duplicate keys/unsupported labels are rejected.

Metrics from actual matches: TP, FP, FN, precision=TP/(TP+FP), recall=TP/(TP+FN),
F1=2TP/(2TP+FP+FN); per-rule and per-type, coverage and clean baseline FP count.
Undefined zero denominators are JSON null; if there are only misses/false
positives, F1 is0. No accuracy or TN claim, because no exhaustive negative universe
is defined. Perfect metrics are measured on this controlled benchmark, not a
claim of generalization or evidence of a hardcoded successful result.

## Structure, preservation and publication safety

Separate reports distinguish clean canonical structure/domain, observed input
structure, intentional semantic findings, truth and post-detection metrics.
No single overall PASS flag hides expected semantic failures. Actual observed
view applies unchanged real SQLite constraints, checks PK/FK/integrity, exact
parent counts, and compares content hashes of all uneditable tables including
events/participants. Tests compare every row difference against explicit after
snapshots; no unrelated row can silently change. Source canonical checksum is
verified before copying, after copying and after the entire experiment.

Output built in owned sibling scratch; exclusive publication lock protects
cooperating writers and complete directory rename publishes only finished work.
Existing outputs/symlinks and unowned locks refused; exceptions remove owned
scratch/lock. A noncooperating external writer racing an empty destination could
still exploit host rename semantics; no cross-process security guarantee. All
normal workflow functions and their safeguards remain unchanged.

## Commands and deterministic replay

```sh
# Existing baseline must pass unchanged Phase05 validation first.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.anomalies --baseline output/phase05/repro-final-20261022/full-1.sqlite3 --directory output/phase06/new-full --profile full --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/phase06/new-full/input/baseline.sqlite3 --observations output/phase06/new-full/input/observations.json
# Same engine without observations is the clean benchmark.
PYTHONPATH=src .venv/bin/python3 -m yottaflex.detector --database output/phase06/new-full/input/baseline.sqlite3
PYTHONPATH=src .venv/bin/python3 scripts/verify_anomaly_reproducibility.py --directory output/phase06/new-replay --profile both --seed 20261022
PYTHONPATH=src .venv/bin/python3 -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python3 scripts/build_data_dictionary.py --check
PYTHON_BIN=.venv/bin/python3 sh scripts/smoke.sh
```

Use new output directories. Master/interviews/evaluations generator modes are
preserved byte-for-byte. No --phase anomalies is added: the dedicated command
requires an explicit validated source and makes the separation obvious. Profile
and baseline seed must match supplied Phase05 content; anomaly seed can differ.

Replay makes fresh valid starter/full references, independently creates two
bundles/profile, compares every ordered row of the anomalous business projection,
its counts/table hashes, baseline hashes and all observation/truth/finding/metric/
control report bytes. Canonical input hash covers baseline SHA plus observation
SHA. Raw SQLite file hashes are not primary evidence. Timing diagnostics stay
outside deterministic content; no absolute path/wall-clock/temp filename is an
input/hash feature. Actual measured results live in report and evidence JSON.

## Limits and remaining challenge work

Only the five mandated anomaly rules are detected here, not a universal detector
for every possible business/history corruption. Structural/input-schema errors
are explicit errors, not suppressed findings. Normal API rejection is not counted
as an injected anomaly. Source/observations distinction is central: canonical
rows/events remain valid; observations can contradict them intentionally.

Generated artifacts remain ignored/local during Phase06. Under separately
approved Phase07 scope, regenerate safe synthetic content and include reviewed
input/observations.json, truth/ground_truth.csv+json and reports/*.json under an
artifacts/phase06/ subtree. Include the canonical baseline through required final
CSV/JSON/SQL exports with source checksums and equivalent IDs, then import/join
verification and final delivery metadata. Those generalized exports, re-import,
complete release manifest/public repository setup/submission are NOT implemented
or authorized here. Human ownership/policy/privacy/all-tools prompt audit and
original submission-channel/send-time uncertainties remain pending. STOP after
Phase06 for review.
