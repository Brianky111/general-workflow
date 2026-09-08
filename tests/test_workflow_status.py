"""Exercise the installed status CLI against isolated consumer projects."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workflow_status.py"


class WorkflowStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="workflow-status-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "consumer project"
        self.state = self.root / "docs" / "workflow"
        (self.state / "slices").mkdir(parents=True)
        self.project()
        self.source()
        self.backlog(("A-01", "S-01", ""))
        self.slice()

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def project(self, source="docs/acceptance.md#Current version", lifecycle="BUILDING",
                target="release to staging", extra=""):
        self.write(self.state / "project.md", (
            f"# Project\n- lifecycle: {lifecycle}\n- tier: LEAN\n- path: lean\n"
            f"- acceptance_source: {source}\n- delivery_target: {target}\n{extra}"
        ))

    def source(self, ids=("A-01",)):
        self.write(self.root / "docs/acceptance.md", (
            "# Contract\n## Current version\n| A-ID | behavior |\n| --- | --- |\n"
            + "".join(f"| {aid} | Required behavior |\n" for aid in ids)
            + "\n## Later\n| A-ID | behavior |\n| --- | --- |\n| A-99 | Future work |\n"
        ))

    def backlog(self, *rows):
        self.write(self.state / "backlog.md", (
            "# Backlog\n| A-ID | slice | note |\n| --- | --- | --- |\n"
            + "".join(f"| {aid} | {assignment} | {note} |\n" for aid, assignment, note in rows)
        ))

    def slice(self, sid="S-01", aid="A-01", status="in-slice", evidence="-",
              owner="alice", claimed="2026-09-08 / abc123", scope="src/a", stage="8 implementation"):
        self.write(self.state / "slices" / f"{sid}.md", (
            f"# Slice {sid}\n- owner: {owner}\n- claimed: {claimed}\n"
            f"- stage: {stage}\n- write_scope: {scope}\n\n## Acceptance\n"
            "| A-ID | status | evidence |\n| --- | --- | --- |\n"
            f"| {aid} | {status} | {evidence} |\n"
        ))

    def run_status(self):
        # The consumer has no copy of the script; cwd is neither project nor skill.
        run = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(self.root), "--json"],
            cwd=self.temp.name, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertIn(run.returncode, (0, 1), run.stderr)
        return run.returncode, json.loads(run.stdout)

    def assert_invalid(self, fragment):
        code, report = self.run_status()
        self.assertEqual(code, 1, report)
        self.assertFalse(report["scope_complete"], report)
        self.assertTrue(any(fragment in error for error in report["errors"]), report)
        return report

    def two_live_slices(self, first_scope="src/a", second_scope="src/b", second_owner="bob"):
        self.source(("A-01", "A-02"))
        self.backlog(("A-01", "S-01", ""), ("A-02", "S-02", ""))
        self.slice(scope=first_scope)
        self.slice(sid="S-02", aid="A-02", scope=second_scope, owner=second_owner)

    def test_claimed_scope_is_not_complete(self):
        code, report = self.run_status()
        self.assertEqual(code, 0)
        self.assertTrue(report["scope_verified"])
        self.assertFalse(report["scope_complete"])
        self.assertEqual(report["in_flight"], ["A-01"])

    def test_stage_nine_completes_scope_without_claiming_release(self):
        self.slice(status="delivered", evidence="pytest: PASS at abc123", stage="9 integration")
        code, report = self.run_status()
        self.assertEqual(code, 0)
        self.assertTrue(report["scope_complete"])
        self.assertEqual(report["lifecycle"], "BUILDING")
        self.assertEqual(report["delivery_target"], "release to staging")

    def test_removing_required_backlog_row_fails(self):
        self.source(("A-01", "A-02"))
        self.slice(status="delivered", evidence="pytest: PASS at abc123")
        self.assert_invalid("A-02")

    def test_cleared_backlog_and_slices_cannot_complete(self):
        self.write(self.state / "backlog.md", "")
        (self.state / "slices/S-01.md").unlink()
        self.assert_invalid("A-01")

    def test_unapproved_backlog_id_fails(self):
        self.backlog(("A-01", "S-01", ""), ("A-02", "-", ""))
        self.assert_invalid("A-02")

    def test_unavailable_or_empty_authority_fails(self):
        for source_text in ("", "# Contract\n## Current version\nNo acceptance table yet.\n"):
            with self.subTest(source=source_text):
                self.write(self.root / "docs/acceptance.md", source_text)
                self.assert_invalid("acceptance_source")
        (self.root / "docs/acceptance.md").unlink()
        self.assert_invalid("acceptance_source")

    def test_fenced_examples_do_not_create_acceptance(self):
        self.write(self.root / "docs/acceptance.md", (
            "# Contract\n## Current version\n```markdown\n"
            "| A-ID | behavior |\n| --- | --- |\n| A-02 | Example |\n```\n"
            "| A-ID | behavior |\n| --- | --- |\n| A-01 | Actual requirement |\n"
        ))
        self.assertEqual(self.run_status()[0], 0)

    def test_duplicate_authoritative_id_fails(self):
        self.source(("A-01", "A-01"))
        self.assert_invalid("duplicate")

    def test_backlog_cannot_be_its_own_authority(self):
        self.project(source="docs/workflow/backlog.md")
        self.assert_invalid("acceptance_source")

    def test_source_heading_must_exist_and_be_unique(self):
        self.project(source="docs/acceptance.md#Missing")
        self.assert_invalid("acceptance_source")
        self.project()
        path = self.root / "docs/acceptance.md"
        self.write(path, path.read_text(encoding="utf-8") + "\n## Current version\n")
        self.assert_invalid("acceptance_source")

    def test_early_draft_is_valid_but_not_complete(self):
        self.project(source="-", lifecycle="IDEA")
        self.backlog()
        (self.state / "slices/S-01.md").unlink()
        code, report = self.run_status()
        self.assertEqual(code, 0)
        self.assertFalse(report["scope_verified"])
        self.assertFalse(report["scope_complete"])

    def test_existing_work_cannot_omit_authority(self):
        self.project(source="-")
        self.assert_invalid("acceptance_source")

    def test_partially_missing_state_is_invalid_json_report(self):
        (self.state / "backlog.md").unlink()
        self.assert_invalid("backlog.md")

    def test_uninitialized_project_is_not_complete(self):
        self.root = Path(self.temp.name) / "new project"
        self.root.mkdir()
        code, report = self.run_status()
        self.assertEqual(code, 0)
        self.assertEqual(report["state_status"], "uninitialized")
        self.assertFalse(report["scope_complete"])

    def test_delivered_requires_evidence(self):
        self.slice(status="delivered")
        self.assert_invalid("evidence")

    def test_deferred_remains_in_authoritative_scope(self):
        self.backlog(("A-01", "deferred", "docs/changes.md#C-01"))
        (self.state / "slices/S-01.md").unlink()
        code, report = self.run_status()
        self.assertEqual(code, 0)
        self.assertTrue(report["scope_complete"])

    def test_overlap_handles_relative_spellings_and_root(self):
        for left, right in (("src", "src/a.py"), ("./src", "src/a.py"),
                            (".", "src/a.py"), ("src/tmp/..", "src/a.py"),
                            ("src\\nested", "src/nested/a.py")):
            with self.subTest(left=left, right=right):
                self.two_live_slices(left, right)
                self.assert_invalid("write_scope overlap")

    @unittest.skipUnless(os.name == "nt", "Windows path case behavior")
    def test_windows_path_case_overlap(self):
        self.two_live_slices("src", "SRC/a.py")
        self.assert_invalid("write_scope overlap")

    def test_adjacent_path_names_do_not_overlap(self):
        self.two_live_slices("src/a", "src/ab")
        self.assertEqual(self.run_status()[0], 0)

    def test_live_claim_requires_owner_date_and_scope(self):
        for kwargs, fragment in (({"owner": "", "claimed": ""}, "owner"),
                                 ({"claimed": "2026-99-99 / abc123"}, "claimed"),
                                 ({"claimed": "20260908 / abc123"}, "claimed"),
                                 ({"scope": ""}, "write_scope"),
                                 ({"scope": "../outside"}, "write_scope"),
                                 ({"scope": "src/**"}, "write_scope")):
            with self.subTest(kwargs=kwargs):
                self.slice(**kwargs)
                self.assert_invalid(fragment)

    def test_owner_cannot_hold_two_live_slices(self):
        self.two_live_slices(second_owner="alice")
        self.assert_invalid("owner")

    def test_owner_can_reuse_scope_after_delivery(self):
        self.two_live_slices("src", "src", second_owner="alice")
        self.slice(status="delivered", evidence="pytest: PASS at abc123", scope="src")
        self.assertEqual(self.run_status()[0], 0)

    def test_claimed_slice_holds_its_scope_before_rows_exist(self):
        # Claiming precedes writing acceptance rows, so an owner alone is a claim.
        self.two_live_slices(second_owner="bob")
        self.backlog(("A-01", "S-01", ""), ("A-02", "-", ""))
        self.write(self.state / "slices/S-02.md", (
            "# Slice S-02\n- owner: bob\n- claimed: 2026-09-08 / abc123\n"
            "- stage: 7 slice\n- write_scope: src/a\n"
        ))
        self.assert_invalid("write_scope overlap")

    def test_empty_value_markers_are_not_evidence(self):
        for marker in ("\u65e0", "\u5f85\u8865", "TODO", "\u2014", "pending"):
            with self.subTest(marker=marker):
                self.slice(status="delivered", evidence=marker)
                self.assert_invalid("evidence")

    def test_delivery_target_is_required_before_completion(self):
        for target in ("-", "<\u6307\u5411\u5b8c\u6210\u8fb9\u754c>"):
            with self.subTest(target=target):
                self.project(target=target)
                self.assert_invalid("delivery_target")

    def test_unedited_write_scope_placeholder_is_rejected(self):
        # Verbatim from 99-state-and-handoff.md: the placeholder contains the
        # separators it documents, so splitting before validating would turn one
        # rejected value into fragments that each pass as a plausible path.
        self.slice(scope="<\u9879\u76ee\u76f8\u5bf9\u8def\u5f84\uff1b"
                         "\u4f8b\u5982 src/items; tests/items>")
        self.assert_invalid("write_scope")

    def test_prose_below_a_heading_does_not_redefine_a_field(self):
        # A handover note in Blockers used to win over the real owner field.
        self.two_live_slices(second_owner="alice")
        path = self.state / "slices/S-02.md"
        self.write(path, path.read_text(encoding="utf-8")
                   + "\n## Blockers\n- owner: \u7b49 carol \u786e\u8ba4\u6743\u9650\n")
        self.assert_invalid("holds two live slices")

    def test_fenced_field_example_is_not_read_as_state(self):
        path = self.state / "slices/S-01.md"
        text = path.read_text(encoding="utf-8")
        self.write(path, text.replace(
            "- owner: alice",
            "- owner: alice\n\n```markdown\n- owner: <template>\n```\n"))
        self.assertEqual(self.run_status()[0], 0)

    def test_a_field_set_twice_is_rejected(self):
        self.project(extra="- lifecycle: internal long-lived tool\n")
        self.assert_invalid("set twice")

    def test_terminal_note_must_point_at_a_change_record(self):
        (self.state / "slices/S-01.md").unlink()
        self.backlog(("A-01", "dropped", "\u4ee5\u540e\u518d\u8bf4"))
        self.assert_invalid("change record")
        self.backlog(("A-01", "dropped", "\u53d8\u66f4\u8bb0\u5f55 C-03"))
        self.assertEqual(self.run_status()[0], 0)

    def test_terminal_id_must_leave_its_slice(self):
        self.backlog(("A-01", "dropped", "docs/changes.md#C-02"))
        report = self.assert_invalid("drop its row")
        self.assertTrue(any("S-01" in error for error in report["errors"]), report)


if __name__ == "__main__":
    unittest.main()
