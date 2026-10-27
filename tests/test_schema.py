"""Structural invariants only; no recruiting workflow, generation or evaluation."""

from contextlib import closing, contextmanager
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from yottaflex.db import SCHEMA_PATH, SchemaError, connect, initialize
from scripts.build_data_dictionary import OUTPUT, annotations, render_dictionary
from fixtures import APP, CAND, FIXTURES, INT, REQ, REVIEWER, SAMPLE, SCORE, T, insert, seed


CORE = {"Requisition", "HiringManager", "Candidate", "Application", "SkillRequirement",
        "InterviewPanel", "Availability", "Interview", "Scorecard", "Offer", "Approval"}
EVENTS = {name for name in SAMPLE if name.endswith("Event")}
IMMUTABLE = EVENTS | {"InterviewParticipant", "SchemaMetadata"}
TIME_FIELDS = {"valid_from", "valid_to", "created_at", "withdrawn_at", "applied_at",
    "updated_at", "start_at", "end_at", "assigned_at", "submitted_at", "requested_at",
    "decided_at", "occurred_at", "recorded_at"}


@contextmanager
def parents_for(table):
    """Load only prerequisite literal rows, leaving tested table empty."""
    with closing(connect()) as db:
        initialize(db)
        for name, row in FIXTURES:
            if name == table:
                break
            insert(db, name, row)
        yield db


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.db = connect()
        initialize(self.db)
        seed(self.db)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    @contextmanager
    def isolated_statement(self, db):
        db.execute("SAVEPOINT constraint_case")
        try:
            yield
        finally:
            db.execute("ROLLBACK TO constraint_case")
            db.execute("RELEASE constraint_case")

    def reject(self, db, table, row, error_name=None):
        with self.isolated_statement(db):
            with self.assertRaises(sqlite3.IntegrityError) as raised:
                insert(db, table, row)
            if error_name:
                self.assertEqual(raised.exception.sqlite_errorname, error_name)

    def accept(self, db, table, row):
        with self.isolated_statement(db):
            insert(db, table, row)

    def test_core_and_support_inventory_explicit_primary_keys_and_strict_storage(self):
        tables = {row["name"]: row for row in self.db.execute("PRAGMA table_list") if row["name"] != "sqlite_schema" and row["schema"] == "main"}
        self.assertEqual(set(tables), set(SAMPLE) | {"SchemaMetadata"})
        self.assertEqual(len(CORE), 11)
        self.assertTrue(CORE <= tables.keys())
        for table in tables:
            with self.subTest(table=table):
                self.assertTrue(any(row["pk"] for row in self.db.execute(f'PRAGMA table_info("{table}")')))
                self.assertEqual(tables[table]["strict"], 1)

    def test_all_declared_required_fk_relationships(self):
        expected = {
            "HiringManager": {("staff_id", "Staff", "staff_id")},
            "CandidateSkill": {("candidate_id", "Candidate", "candidate_id")},
            "Requisition": {("hiring_manager_id", "HiringManager", "hiring_manager_id")},
            "SkillRequirement": {("requisition_id", "Requisition", "requisition_id")},
            "Application": {("candidate_id", "Candidate", "candidate_id"), ("requisition_id", "Requisition", "requisition_id")},
            "InterviewPanel": {("requisition_id", "Requisition", "requisition_id")},
            "PanelMember": {("panel_id", "InterviewPanel", "panel_id"), ("staff_id", "Staff", "staff_id")},
            "Availability": {("staff_id", "Staff", "staff_id")},
            "Interview": {("application_id", "Application", "application_id"), ("requisition_id", "Application", "requisition_id"), ("panel_id", "InterviewPanel", "panel_id"), ("requisition_id", "InterviewPanel", "requisition_id")},
            "InterviewParticipant": {("interview_id", "Interview", "interview_id"), ("staff_id", "Staff", "staff_id")},
            "Scorecard": {("interview_id", "Interview", "interview_id"), ("reviewer_staff_id", "Staff", "staff_id"), ("interview_id", "InterviewParticipant", "interview_id"), ("reviewer_staff_id", "InterviewParticipant", "staff_id")},
            "ScorecardItem": {("scorecard_id", "Scorecard", "scorecard_id"), ("skill_requirement_id", "SkillRequirement", "skill_requirement_id")},
            "Offer": {("application_id", "Application", "application_id"), ("requisition_id", "Application", "requisition_id"), ("approved_requisition_event_id", "RequisitionEvent", "event_id"), ("requisition_id", "RequisitionEvent", "requisition_id"), ("currency", "RequisitionEvent", "currency")},
            "Approval": {("requisition_id", "Requisition", "requisition_id"), ("offer_id", "Offer", "offer_id"), ("approver_staff_id", "Staff", "staff_id")},
        }
        for table in EVENTS:
            subject = table.removesuffix("Event")
            id_column = next(row["name"] for row in self.db.execute(f'PRAGMA table_info("{subject}")') if row["pk"])
            expected[table] = {(id_column, subject, id_column), ("actor_staff_id", "Staff", "staff_id"), ("actor_candidate_id", "Candidate", "candidate_id")}
        for table, links in expected.items():
            with self.subTest(table=table):
                actual = {(row["from"], row["table"], row["to"]) for row in self.db.execute(f'PRAGMA foreign_key_list("{table}")')}
                self.assertEqual(actual, links)

    def test_every_fk_group_rejects_missing_references(self):
        for table, sample in SAMPLE.items():
            groups = {}
            for link in self.db.execute(f'PRAGMA foreign_key_list("{table}")'):
                groups.setdefault(link["id"], []).append(link)
            with parents_for(table) as db:
                self.accept(db, table, sample)
                for group, links in groups.items():
                    row = sample.copy()
                    for link in links:
                        value = SAMPLE[link["table"]][link["to"]]
                        row[link["from"]] = "ZZZ" if link["to"] == "currency" else value[:-6] + "999999"
                    if table == "Application":
                        row["application_id"] = f"APP-{row['candidate_id']}-{row['requisition_id']}"
                    if table == "Scorecard":
                        row["scorecard_id"] = f"SCORE-{row['interview_id']}-{row['reviewer_staff_id']}"
                    if table == "Approval":
                        if any(link["from"] == "offer_id" for link in links):
                            row["requisition_id"] = None
                        elif any(link["from"] == "requisition_id" for link in links):
                            row["offer_id"] = None
                    with self.subTest(table=table, fk_group=group):
                        self.reject(db, table, row, "SQLITE_CONSTRAINT_FOREIGNKEY")

    def test_every_required_domain_field_rejects_null(self):
        for table, sample in SAMPLE.items():
            with parents_for(table) as db:
                for column in db.execute(f'PRAGMA table_info("{table}")').fetchall():
                    if column["notnull"]:
                        with self.subTest(table=table, field=column["name"]):
                            self.reject(db, table, dict(sample, **{column["name"]: None}), "SQLITE_CONSTRAINT_NOTNULL")

    def test_duplicate_primary_keys_all_tables(self):
        for table in set(SAMPLE) | {"SchemaMetadata"}:
            row = dict(self.db.execute(f'SELECT * FROM "{table}" LIMIT 1').fetchone())
            with self.subTest(table=table):
                self.reject(self.db, table, row)

    def test_composite_application_and_reviewer_uniqueness_indexes(self):
        for table, pair in [("Application", ["candidate_id", "requisition_id"]), ("Scorecard", ["interview_id", "reviewer_staff_id"])]:
            indexes = [[row["name"] for row in self.db.execute(f'PRAGMA index_info("{index["name"]}")')] for index in self.db.execute(f'PRAGMA index_list("{table}")') if index["unique"]]
            self.assertIn(pair, indexes)
            self.reject(self.db, table, SAMPLE[table])
        # These natural pairs also determine their exact required PK strings.
        with parents_for("Application") as db:
            self.reject(db, "Application", dict(SAMPLE["Application"], application_id="APP-OTHER"), "SQLITE_CONSTRAINT_CHECK")
        with parents_for("Scorecard") as db:
            self.reject(db, "Scorecard", dict(SAMPLE["Scorecard"], scorecard_id="SCORE-OTHER"), "SQLITE_CONSTRAINT_CHECK")

    def test_all_scalar_lifecycle_enums_reject_unknown_values(self):
        for table, sample in SAMPLE.items():
            fields = {field for field in ("status", "role", "assignment_role", "event_type", "previous_status", "new_status") if field in sample}
            with parents_for(table) as db:
                for field in fields:
                    with self.subTest(table=table, field=field):
                        self.reject(db, table, dict(sample, **{field: "not_a_status"}), "SQLITE_CONSTRAINT_CHECK")

    def test_deterministic_counter_id_patterns(self):
        for table, sample in SAMPLE.items():
            pk = next((field for field in self.db.execute(f'PRAGMA table_info("{table}")') if field["pk"]), None)
            name = pk["name"]
            if not re.search(r"[0-9]{6}$", str(sample[name])) or table in {"Application", "Scorecard", "PanelMember", "InterviewParticipant", "CandidateSkill", "ScorecardItem"}:
                continue
            original = sample[name]
            invalid = [original.lower(), original[:-1], original + "0", original[:-6] + "000000", original[:-1] + "x"]
            if "2026" in original:
                invalid.append(original.replace("2026", "2025"))
            with parents_for(table) as db:
                for value in invalid:
                    with self.subTest(table=table, value=value):
                        self.reject(db, table, dict(sample, **{name: value}), "SQLITE_CONSTRAINT_CHECK")

    def test_all_primary_identities_immutable(self):
        for table in set(SAMPLE) - IMMUTABLE:
            keys = [row for row in self.db.execute(f'PRAGMA table_info("{table}")') if row["pk"]]
            for key in keys:
                name = key["name"]
                original = SAMPLE[table][name]
                changed = original + "_changed" if isinstance(original, str) else original + 1
                with self.subTest(table=table, key=name), self.isolated_statement(self.db):
                    with self.assertRaises(sqlite3.IntegrityError) as raised:
                        self.db.execute(f'UPDATE "{table}" SET {name}=?', (changed,))
                    self.assertEqual(raised.exception.sqlite_errorname, "SQLITE_CONSTRAINT_TRIGGER")

    def test_each_timestamp_rejects_text_negative_and_out_of_range(self):
        for table, sample in SAMPLE.items():
            with parents_for(table) as db:
                for field in TIME_FIELDS & sample.keys():
                    for value in ("2026-02-30T00:00:00Z", -1, 253402300800, 1.5):
                        row = dict(sample, **{field: value})
                        if field == "withdrawn_at": row["status"] = "withdrawn"
                        if field == "submitted_at": row["status"] = "submitted"
                        if field == "decided_at": row["status"] = "approved"
                        with self.subTest(table=table, field=field, value=value):
                            self.reject(db, table, row)

    def test_effective_and_booking_intervals_positive(self):
        for table, sample in SAMPLE.items():
            fields = ("valid_from", "valid_to") if "valid_from" in sample else ("start_at", "end_at") if "end_at" in sample else None
            if fields:
                start, end = fields
                with parents_for(table) as db:
                    for difference in (0, -1):
                        with self.subTest(table=table, difference=difference):
                            self.reject(db, table, dict(sample, **{end: sample[start]+difference}), "SQLITE_CONSTRAINT_CHECK")
                    self.accept(db, table, dict(sample, **{end: sample[start]+1}))

    def test_same_row_causal_dates_and_status_timestamps(self):
        cases = [("Candidate", dict(status="withdrawn", withdrawn_at=T-1)), ("Candidate", dict(status="withdrawn")),
            ("Candidate", dict(withdrawn_at=T)), ("Application", dict(updated_at=T-1)),
            ("Scorecard", dict(status="submitted")), ("Scorecard", dict(submitted_at=T)),
            ("Scorecard", dict(status="submitted", submitted_at=T-1)),
            ("Approval", dict(status="approved")), ("Approval", dict(decided_at=T)),
            ("Approval", dict(status="approved", decided_at=T-1))]
        for table, changes in cases:
            with self.subTest(table=table, changes=changes), parents_for(table) as db:
                self.reject(db, table, dict(SAMPLE[table], **changes), "SQLITE_CONSTRAINT_CHECK")
        for table in EVENTS:
            with self.subTest(table=table), parents_for(table) as db:
                self.reject(db, table, dict(SAMPLE[table], recorded_at=T-1), "SQLITE_CONSTRAINT_CHECK")

    def test_compensation_ranges_integer_units_and_currency(self):
        for table in ("Requisition", "RequisitionEvent"):
            with parents_for(table) as db:
                for changes in (dict(band_min_minor=-1), dict(band_max_minor=9999), dict(band_min_minor=1.5), dict(currency="inr"), dict(currency="INRR")):
                    with self.subTest(table=table, changes=changes):
                        self.reject(db, table, dict(SAMPLE[table], **changes))
                self.accept(db, table, dict(SAMPLE[table], band_min_minor=0, band_max_minor=0))
        with parents_for("RequisitionEvent") as db:
            for name in ("band_min_minor", "band_max_minor", "currency"):
                self.reject(db, "RequisitionEvent", dict(SAMPLE["RequisitionEvent"], **{name: None}), "SQLITE_CONSTRAINT_CHECK")
        with parents_for("Offer") as db:
            for value in (0, -1, 1.5):
                self.reject(db, "Offer", dict(SAMPLE["Offer"], amount_minor=value))
            self.reject(db, "Offer", dict(SAMPLE["Offer"], currency="USD"), "SQLITE_CONSTRAINT_FOREIGNKEY")

    def test_rubric_values_weights_flags_and_versions(self):
        checks = {"CandidateSkill": {"level": (-1, 5)}, "Scorecard": {"total_score_milli": (-1, 4001), "rubric_version": (0,)},
            "ScorecardItem": {"score_value": (-1, 5), "weight_basis_points": (0, 10001)},
            "SkillRequirement": {"weight_basis_points": (0, 10001), "rubric_version": (0,), "is_required": (2,)},
            "Offer": {"is_final": (2,)}, "Requisition": {"policy_version": (0,)}}
        for table, fields in checks.items():
            with parents_for(table) as db:
                for field, values in fields.items():
                    for value in values:
                        row = dict(SAMPLE[table], **{field: value})
                        if table == "ScorecardItem" and field == "score_value": row["status"] = "scored"
                        with self.subTest(table=table, field=field, value=value):
                            self.reject(db, table, row, "SQLITE_CONSTRAINT_CHECK")
        with parents_for("ScorecardItem") as db:
            for value in (0, 4):
                self.accept(db, "ScorecardItem", dict(SAMPLE["ScorecardItem"], status="scored", score_value=value))
            self.reject(db, "ScorecardItem", dict(SAMPLE["ScorecardItem"], status="scored"), "SQLITE_CONSTRAINT_CHECK")
            self.reject(db, "ScorecardItem", dict(SAMPLE["ScorecardItem"], score_value=2), "SQLITE_CONSTRAINT_CHECK")
        with parents_for("Scorecard") as db:
            for value in (0, 4000):
                self.accept(db, "Scorecard", dict(SAMPLE["Scorecard"], total_score_milli=value))

    def test_approval_target_xor_and_both_valid_subject_types(self):
        with parents_for("Approval") as db:
            self.reject(db, "Approval", dict(SAMPLE["Approval"], requisition_id=None), "SQLITE_CONSTRAINT_CHECK")
            self.reject(db, "Approval", dict(SAMPLE["Approval"], offer_id="OFF-2026-000001"), "SQLITE_CONSTRAINT_CHECK")
            self.accept(db, "Approval", SAMPLE["Approval"])
            self.accept(db, "Approval", dict(SAMPLE["Approval"], requisition_id=None, offer_id="OFF-2026-000001"))

    def test_only_one_active_final_offer_partial_unique_index(self):
        self.db.execute("UPDATE Offer SET status='approved'")
        second = dict(SAMPLE["Offer"], offer_id="OFF-2026-000002", status="approved")
        self.reject(self.db, "Offer", second, "SQLITE_CONSTRAINT_UNIQUE")
        self.accept(self.db, "Offer", dict(second, is_final=0))
        self.accept(self.db, "Offer", dict(second, status="draft"))
        self.db.execute("UPDATE Offer SET status='declined'")
        self.accept(self.db, "Offer", second)

    def test_scorecard_requires_assigned_reviewer(self):
        with parents_for("Scorecard") as db:
            # Staff exists, but is not assigned to this interview.
            row = dict(SAMPLE["Scorecard"], reviewer_staff_id="STAFF-000001", scorecard_id=f"SCORE-{INT}-STAFF-000001")
            self.reject(db, "Scorecard", row, "SQLITE_CONSTRAINT_FOREIGNKEY")

    def test_panel_and_application_must_share_requisition(self):
        second = dict(SAMPLE["Requisition"], requisition_id="REQ-2026-000002")
        insert(self.db, "Requisition", second)
        insert(self.db, "InterviewPanel", dict(SAMPLE["InterviewPanel"], panel_id="PANEL-000002", requisition_id=second["requisition_id"]))
        self.reject(self.db, "Interview", dict(SAMPLE["Interview"], interview_id="INT-2026-000002", panel_id="PANEL-000002"), "SQLITE_CONSTRAINT_FOREIGNKEY")

    def test_append_only_events_participants_metadata_update_delete_replace(self):
        for table in IMMUTABLE:
            before = [tuple(row) for row in self.db.execute(f'SELECT * FROM "{table}"')]
            row = dict(self.db.execute(f'SELECT * FROM "{table}" LIMIT 1').fetchone())
            column = next(iter(row))
            for action in (f'UPDATE "{table}" SET {column}={column}', f'DELETE FROM "{table}"'):
                with self.subTest(table=table, action=action), self.isolated_statement(self.db):
                    with self.assertRaises(sqlite3.IntegrityError) as raised:
                        self.db.execute(action)
                    self.assertEqual(raised.exception.sqlite_errorname, "SQLITE_CONSTRAINT_TRIGGER")
            columns = ", ".join(row)
            marks = ", ".join("?" for _ in row)
            # Explicit duplicate INSERT guard also protects OR REPLACE even if a
            # caller disables recursive DELETE triggers (not normal API use).
            self.db.execute("PRAGMA recursive_triggers=OFF")
            with self.subTest(table=table, action="replace"), self.isolated_statement(self.db):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.db.execute(f'INSERT OR REPLACE INTO "{table}" ({columns}) VALUES ({marks})', tuple(row.values()))
            self.db.execute("PRAGMA recursive_triggers=ON")
            self.assertEqual([tuple(row) for row in self.db.execute(f'SELECT * FROM "{table}"')], before)

    def test_event_subject_sequence_unique(self):
        for table in EVENTS:
            row = dict(SAMPLE[table], event_id=SAMPLE[table]["event_id"][:-6]+"000002")
            with self.subTest(table=table):
                self.reject(self.db, table, row, "SQLITE_CONSTRAINT_UNIQUE")
                self.accept(self.db, table, dict(row, sequence=2))
            with parents_for(table) as db:
                self.reject(db, table, dict(SAMPLE[table], sequence=0), "SQLITE_CONSTRAINT_CHECK")

    def test_event_snapshots_require_json_objects_and_retain_before_after_values(self):
        for table in EVENTS:
            with self.subTest(table=table), parents_for(table) as db:
                for value in ("broken json", "[]", '"text"', "null", "1", "true"):
                    self.reject(db, table, dict(SAMPLE[table], snapshot_json=value), "SQLITE_CONSTRAINT_CHECK")
                for value in ("{}", '{"before":{"start_at":1793000000},"after":{"start_at":1793003600}}'):
                    self.accept(db, table, dict(SAMPLE[table], snapshot_json=value))

    def test_text_fields_nonblank_synthetic_contact_and_natural_uniques(self):
        for table in SAMPLE:
            notes = annotations(SCHEMA_PATH.read_text())[table]["fields"]
            with parents_for(table) as db:
                for field, (definition, _, _) in notes.items():
                    if "length(trim(" in definition:
                        with self.subTest(table=table, field=field):
                            self.reject(db, table, dict(SAMPLE[table], **{field: "  "}), "SQLITE_CONSTRAINT_CHECK")
        with parents_for("Candidate") as db:
            self.reject(db, "Candidate", dict(SAMPLE["Candidate"], contact_email="example@example.com"), "SQLITE_CONSTRAINT_CHECK")
            self.accept(db, "Candidate", dict(SAMPLE["Candidate"], contact_email=None))
        for table, changes in [("HiringManager", dict(hiring_manager_id="HM-000002")), ("Candidate", dict(candidate_id="CAND-000002", contact_email="CANDIDATE1@EXAMPLE.INVALID")), ("SkillRequirement", dict(skill_requirement_id="SKILL-000002")), ("Availability", dict(availability_id="AVAIL-000002"))]:
            with self.subTest(table=table):
                self.reject(self.db, table, dict(SAMPLE[table], **changes), "SQLITE_CONSTRAINT_UNIQUE")

    def test_metadata_singleton_version_and_hash_storage_constraints(self):
        # Exercise metadata before its one legal row exists, without bypassing
        # append-only protection on an initialized database.
        with closing(connect()) as db:
            db.executescript(SCHEMA_PATH.read_text())
            sample = dict(self.db.execute("SELECT * FROM SchemaMetadata").fetchone())
            self.accept(db, "SchemaMetadata", sample)
            for field in sample:
                with self.subTest(field=field, value=None):
                    self.reject(db, "SchemaMetadata", dict(sample, **{field: None}), "SQLITE_CONSTRAINT_NOTNULL")
            for field, values in {"singleton": (0, 2), "schema_version": (0, 3),
                                  "source_sha256": ("short", "z"*64),
                                  "catalog_sha256": ("short", "z"*64)}.items():
                for value in values:
                    with self.subTest(field=field, value=value):
                        self.reject(db, "SchemaMetadata", dict(sample, **{field: value}), "SQLITE_CONSTRAINT_CHECK")

    def test_valid_cross_table_references_and_integrity(self):
        row = self.db.execute("""SELECT o.offer_id, c.candidate_id, r.requisition_id,
            i.interview_id, s.scorecard_id, si.skill_requirement_id
            FROM Offer o JOIN Application a ON a.application_id=o.application_id
            JOIN Candidate c USING(candidate_id) JOIN Requisition r ON r.requisition_id=a.requisition_id
            JOIN Interview i ON i.application_id=a.application_id
            JOIN Scorecard s ON s.interview_id=i.interview_id
            JOIN ScorecardItem si ON si.scorecard_id=s.scorecard_id""").fetchone()
        self.assertEqual(tuple(row), ("OFF-2026-000001", CAND, REQ, INT, SCORE, "SKILL-000001"))
        self.assertEqual(list(self.db.execute("PRAGMA foreign_key_check")), [])
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_fresh_and_repeated_initialization_deterministic_and_preserves_rows(self):
        before = list(self.db.iterdump())
        initialize(self.db)
        self.assertEqual(list(self.db.iterdump()), before)
        self.assertEqual(self.db.execute("PRAGMA user_version").fetchone()[0], 2)
        with closing(connect()) as other:
            initialize(other)
            self.assertEqual(other.execute("SELECT COUNT(*) FROM Candidate").fetchone()[0], 0)
            self.assertEqual(tuple(other.execute("SELECT * FROM SchemaMetadata").fetchone()), tuple(self.db.execute("SELECT * FROM SchemaMetadata").fetchone()))

    def test_connections_enable_foreign_keys_and_file_isolation(self):
        with tempfile.TemporaryDirectory(prefix="yottaflex-schema-") as directory:
            first = Path(directory)/"first.sqlite3"
            second = Path(directory)/"second.sqlite3"
            with closing(connect(first)) as db:
                initialize(db)
                seed(db)
                db.commit()
            with closing(connect(first)) as db:
                initialize(db)
                self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
                self.assertEqual(db.execute("PRAGMA recursive_triggers").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM Candidate").fetchone()[0], 1)
            with closing(connect(second)) as db:
                initialize(db)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM Candidate").fetchone()[0], 0)

    def test_unknown_populated_unversioned_database_not_destroyed(self):
        with closing(connect()) as db:
            db.execute("CREATE TABLE existing (value TEXT)")
            db.execute("INSERT INTO existing VALUES ('preserve')")
            db.commit()
            with self.assertRaises(SchemaError): initialize(db)
            self.assertEqual(db.execute("SELECT value FROM existing").fetchone()[0], "preserve")
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 0)

    def test_sqlite_lookalike_user_table_is_not_hidden_from_safety_checks(self):
        # SQL LIKE treats underscore as a wildcard. Only literal sqlite_* internal
        # names may be excluded, not an unrelated populated sqliteXuser table.
        with closing(connect()) as db:
            db.execute("CREATE TABLE sqliteXuser (value TEXT)")
            db.execute("INSERT INTO sqliteXuser VALUES ('preserve')")
            db.commit()
            with self.assertRaises(SchemaError): initialize(db)
            self.assertEqual(db.execute("SELECT value FROM sqliteXuser").fetchone()[0], "preserve")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sqlite_schema WHERE type='table'").fetchone()[0], 1)

    def test_version_one_database_preserved_and_not_silently_upgraded(self):
        with closing(connect()) as db:
            db.execute("CREATE TABLE preserved_v1 (value TEXT)")
            db.execute("INSERT INTO preserved_v1 VALUES ('keep')")
            db.execute("PRAGMA user_version=1")
            db.commit()
            with self.assertRaises(SchemaError): initialize(db)
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT value FROM preserved_v1").fetchone()[0], "keep")

    def test_experience_and_required_proficiency_ranges(self):
        for table, field, high in [("Candidate", "experience_years", 50), ("SkillRequirement", "min_proficiency", 4)]:
            with parents_for(table) as db:
                for value in (-1, high+1, 1.5):
                    with self.subTest(table=table, value=value):
                        self.reject(db, table, dict(SAMPLE[table], **{field: value}))
                for value in (0, high):
                    self.accept(db, table, dict(SAMPLE[table], **{field: value}))

    def test_unknown_version_and_catalog_drift_refused(self):
        self.db.execute("PRAGMA user_version=99")
        with self.assertRaises(SchemaError): initialize(self.db)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM Candidate").fetchone()[0], 1)
        self.db.execute("PRAGMA user_version=2")
        self.db.execute("CREATE TABLE unexpected (value TEXT)")
        with self.assertRaises(SchemaError): initialize(self.db)
        self.assertIsNotNone(self.db.execute("SELECT name FROM sqlite_schema WHERE name='unexpected'").fetchone())

    def test_caller_transaction_not_committed_or_rolled_back_by_initializer(self):
        self.db.execute("UPDATE Candidate SET display_name='Pending Synthetic Edit'")
        with self.assertRaises(SchemaError): initialize(self.db)
        self.assertTrue(self.db.in_transaction)
        self.db.rollback()
        self.assertEqual(self.db.execute("SELECT display_name FROM Candidate").fetchone()[0], "Synthetic Candidate")

    def test_source_schema_drift_refused_and_failed_ddl_rolls_back(self):
        with tempfile.TemporaryDirectory(prefix="yottaflex-ddl-") as directory:
            changed = Path(directory)/"schema.sql"
            changed.write_text(SCHEMA_PATH.read_text()+"\n-- changed version requires explicit migration\n")
            with patch("yottaflex.db.SCHEMA_PATH", changed):
                with self.assertRaises(SchemaError): initialize(self.db)
            changed.write_text(SCHEMA_PATH.read_text()+"\nTHIS IS INVALID SQL;\n")
            with closing(connect()) as db, patch("yottaflex.db.SCHEMA_PATH", changed):
                with self.assertRaises(sqlite3.OperationalError): initialize(db)
                self.assertFalse(db.in_transaction)
                self.assertEqual(list(db.execute("SELECT name FROM sqlite_schema")), [])
                self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 0)

    def test_existing_fk_corruption_refused_not_silently_repaired(self):
        self.db.execute("PRAGMA foreign_keys=OFF")
        self.db.execute("UPDATE Requisition SET hiring_manager_id='HM-999999'")
        self.db.commit()
        with self.assertRaises(SchemaError): initialize(self.db)
        self.assertEqual(self.db.execute("SELECT hiring_manager_id FROM Requisition").fetchone()[0], "HM-999999")

    def test_data_dictionary_exactly_covers_every_field_and_constraint(self):
        self.assertEqual(OUTPUT.read_text(), render_dictionary())
        notes = annotations(SCHEMA_PATH.read_text())
        count = 0
        for table in notes:
            columns = {row["name"] for row in self.db.execute(f'PRAGMA table_info("{table}")')}
            self.assertEqual(columns, notes[table]["fields"].keys())
            count += len(columns)
        self.assertEqual(count, 209)


if __name__ == "__main__":
    unittest.main()
