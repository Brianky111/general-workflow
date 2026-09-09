"""Exercise the installed status CLI against isolated consumer projects."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workflow_status.py"
# A delivered row records an invocation, its observed result, and where to find
# it again.
CALL = "POST /items {\"name\": \"x\"} -> 201 id=it_7; GET /items has name=x @ abc123"
# delivery_target is a pointer plus one of the three completion boundaries.
TARGET = "docs/contract.md#Done / deployed:staging"
NEXT = "write the failing test for A-01; verify: pytest tests/items -q"


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
                target=TARGET, extra="", tier="LEAN", path="lean", state_version="2",
                next_action=NEXT):
        # None drops the line entirely; "" keeps the field with an empty value.
        fields = (("state_version", state_version), ("lifecycle", lifecycle), ("tier", tier),
                  ("path", path), ("next_action", next_action),
                  ("acceptance_source", source), ("delivery_target", target))
        body = "".join(f"- {name}: {value}\n" for name, value in fields if value is not None)
        self.write(self.state / "project.md", f"# Project\n{body}{extra}")

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

    def run_cli(self, *args, env=None, utf8=True):
        # The consumer has no copy of the script; cwd is neither project nor skill.
        command = [sys.executable] + (["-X", "utf8"] if utf8 else [])
        return subprocess.run(
            command + [str(SCRIPT), "--root", str(self.root), *args],
            cwd=self.temp.name, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env,
        )

    def run_status(self):
        run = self.run_cli("--json")
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
        self.slice(status="delivered", evidence=CALL, stage="9 integration")
        code, report = self.run_status()
        self.assertEqual(code, 0)
        self.assertTrue(report["scope_complete"])
        self.assertEqual(report["lifecycle"], "BUILDING")
        self.assertEqual(report["delivery_target"], TARGET)

    def test_removing_required_backlog_row_fails(self):
        self.source(("A-01", "A-02"))
        self.slice(status="delivered", evidence=CALL)
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

    def test_pre_shard_single_file_state_is_not_a_new_project(self):
        # Before the shards the whole ledger lived in one file. Reported as
        # "uninitialized", the next agent creates an empty docs/workflow/ beside
        # it and every A-ID, claim and evidence line stops being read.
        for index, legacy in enumerate(("docs/workflow-state.md", "WORKFLOW-STATE.md")):
            with self.subTest(legacy=legacy):
                self.root = Path(self.temp.name) / f"pre-shard project {index}"
                self.write(self.root / legacy,
                           "- lifecycle: BUILDING\n- owner: alice\n"
                           "| A-ID | slice | evidence |\n| --- | --- | --- |\n"
                           "| A-01 | S-01 | POST /items -> 201 id=it_7 @ abc123 |\n")
                code, report = self.run_status()
                self.assertEqual(code, 0, report)
                self.assertEqual(report["state_status"], "legacy", report)
                self.assertEqual(report["legacy_state"], [legacy], report)
                self.assertFalse(report["scope_complete"], report)
        run = self.run_cli()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("99-state-and-handoff.md", run.stdout)
        self.assertNotIn("create it this round", run.stdout)
        # With no such file it is a new project again, and says so.
        self.root = Path(self.temp.name) / "empty project"
        self.root.mkdir()
        code, report = self.run_status()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["state_status"], "uninitialized", report)
        self.assertEqual(report["legacy_state"], [], report)

    def test_a_migrated_project_keeps_reading_its_shards(self):
        # The old file usually survives the split; existing shards win, so the
        # migration notice cannot strand a project that already migrated.
        self.write(self.root / "docs/workflow-state.md", "# 旧状态\n- lifecycle: BUILDING\n")
        code, report = self.run_status()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["state_status"], "ready", report)
        self.assertEqual(report["legacy_state"], [], report)

    def test_delivered_requires_evidence(self):
        self.slice(status="delivered")
        self.assert_invalid("evidence")

    def test_delivered_evidence_must_record_an_observed_result(self):
        # A command proves an assertion held; it does not prove the entrypoint
        # could be called and returned what the acceptance row promises.
        for evidence in ("pytest tests/items -q: 12 passed",
                         "https://ci.example/run/123",
                         "\u5b9e\u73b0\u5df2\u5b8c\u6210\uff0c\u4ee3\u7801\u5df2\u8bc4\u5ba1",
                         "pytest tests/items -q ->",
                         "-> 201 created"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                self.assert_invalid("observed result")

    def test_a_real_call_with_its_result_is_evidence(self):
        for evidence in (CALL,
                         "app export --from 2026-09-01 => report.csv 3 rows, exit 0 @ abc123",
                         "\u6253\u5f00 /orders \u2192 \u9996\u5c4f 3 \u884c @ abc123"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                code, report = self.run_status()
                self.assertEqual(code, 0, report)
                self.assertTrue(report["scope_complete"], report)

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
        report = self.assert_invalid("owner")
        # Returning a slice by deleting its rows but keeping owner/claimed locks
        # that person out of the next claim, so the error has to say so.
        self.assertTrue(any("clearing its owner and claimed" in e for e in report["errors"]), report)

    def test_owner_can_reuse_scope_after_delivery(self):
        self.two_live_slices("src", "src", second_owner="alice")
        self.slice(status="delivered", evidence=CALL, scope="src")
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
        # "follow-up" once read as an id because any short hyphenated word did.
        # The slash cases are the same vague note wearing a slash: while any
        # string containing one counted as a path, "ask/bob" was a change record.
        (self.state / "slices/S-01.md").unlink()
        for note in ("\u4ee5\u540e\u518d\u8bf4", "follow-up", "later", "not-now",
                     "TODO/later", "\u63a8\u8fdf\u5230 v2/\u4ee5\u540e", "ask/bob",
                     "src/report", "\u95ee\u95ee alice/bob \u518d\u5b9a"):
            with self.subTest(note=note):
                self.backlog(("A-01", "dropped", note))
                self.assert_invalid("change record")
        for note in ("\u53d8\u66f4\u8bb0\u5f55 C-03", "docs/changes.md#C-02", "notes/decisions.md",
                     "https://tracker.example/changes/9"):
            with self.subTest(note=note):
                self.backlog(("A-01", "dropped", note))
                self.assertEqual(self.run_status()[0], 0)

    def test_terminal_id_must_leave_its_slice(self):
        self.backlog(("A-01", "dropped", "docs/changes.md#C-02"))
        report = self.assert_invalid("drop its row")
        self.assertTrue(any("S-01" in error for error in report["errors"]), report)

    def test_state_version_must_declare_the_layout(self):
        self.project(state_version=None)
        report = self.assert_invalid("state_version")
        # The error carries the line to paste; a version gate that only says
        # "invalid" costs a round trip to the reference.
        self.assertTrue(any("- state_version: 2" in e for e in report["errors"]), report)
        for version in ("1", "-", "<n>"):
            with self.subTest(version=version):
                self.project(state_version=version)
                self.assert_invalid("state_version")

    def test_lifecycle_tier_and_path_must_be_known_values(self):
        for kwargs, fragment in (({"lifecycle": "BUILDNG"}, "lifecycle"),
                                 ({"lifecycle": "building"}, "lifecycle"),
                                 ({"lifecycle": None}, "lifecycle"),
                                 ({"tier": None}, "tier"),
                                 ({"tier": "MEDIUM"}, "tier"),
                                 ({"path": "quick"}, "path"),
                                 ({"path": None}, "path")):
            with self.subTest(kwargs=kwargs):
                self.project(**kwargs)
                self.assert_invalid(fragment)

    def test_unedited_enum_placeholders_are_not_values(self):
        # Verbatim from the template in 99-state-and-handoff.md.
        self.project(lifecycle="IDEA | DEFINED | ARCHITECTURE-READY | BUILDING",
                     tier="LEAN | STANDARD | HIGH-RISK", path="lean | full")
        report = self.assert_invalid("still lists every option")
        for field in ("lifecycle", "tier", "path"):
            self.assertTrue(any(f"{field} still lists" in e for e in report["errors"]), report)

    def test_delivery_target_must_end_at_a_completion_boundary(self):
        for target in ("差不多做完就行", "docs/contract.md#Done / release to staging",
                       "docs/contract.md#Done / deployed:", "implementation and tests"):
            with self.subTest(target=target):
                self.project(target=target)
                self.assert_invalid("delivery_target")

    def test_delivery_target_must_also_point_at_the_boundary(self):
        # The endpoint says where closeout stops; the pointer says what closeout
        # checks off. "release-ready" alone passed, and then closeout had nothing
        # to compare the work against.
        for target in ("release-ready", "implementation-and-tests", "deployed:staging",
                       "- / release-ready", "<指向完成边界的指针> / release-ready",
                       "TODO / deployed:staging"):
            with self.subTest(target=target):
                self.project(target=target)
                report = self.assert_invalid("delivery_target")
                # Missing pointer and unusable endpoint need different repairs,
                # so they must not arrive as one sentence.
                self.assertTrue(any("no pointer" in e for e in report["errors"]), report)
                self.assertFalse(any("names no completion boundary" in e
                                     for e in report["errors"]), report)

    def test_delivery_target_pointer_must_reach_a_place(self):
        # 99-state-and-handoff.md makes the pointer half the thing closeout ticks
        # off item by item. These cleared the "not a placeholder word" test and
        # still opened nothing, which leaves closeout with the same "差不多了"
        # the endpoint half was added to stop.
        for target in ("随便 / release-ready", "见合同 / release-ready",
                       "完成边界 / implementation-and-tests",
                       "ask/bob / deployed:staging", "issues/17 / release-ready"):
            with self.subTest(target=target):
                self.project(target=target)
                report = self.assert_invalid("delivery_target")
                self.assertTrue(any("no pointer" in e for e in report["errors"]), report)
        for target in ("docs/contract.md#完成边界 / release-ready",
                       "https://tracker.example/epics/4 / release-ready",
                       "C-03 / implementation-and-tests"):
            with self.subTest(target=target):
                self.project(target=target)
                self.assertEqual(self.run_status()[0], 0)

    def test_delivery_target_endpoint_is_read_after_the_last_separator(self):
        for target in ("docs/contract.md#Done / implementation-and-tests",
                       "docs/contract.md#Done / release-ready",
                       "docs/contract.md#Done / 只到「验收场景」为止 / deployed:staging"):
            with self.subTest(target=target):
                self.project(target=target)
                code, report = self.run_status()
                self.assertEqual(code, 0, report)
                self.assertEqual(report["delivery_target"], target)

    def test_next_action_is_required_when_no_slice_is_in_flight(self):
        self.backlog(("A-01", "-", ""))
        (self.state / "slices/S-01.md").unlink()
        self.project(next_action=None)
        self.assert_invalid("next_action")
        self.project(next_action="-")
        self.assert_invalid("next_action")
        self.project()
        code, report = self.run_status()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["next_action"], NEXT)

    def test_next_action_must_name_an_action(self):
        # 99-state-and-handoff.md lists "下一步继续" as an anti-pattern, and it
        # passed: only an empty value was rejected. The script stops at words
        # that name no action; whether a concrete one is executable is a
        # judgement it cannot make.
        for value in ("下一步继续", "继续", "推进", "看情况", "x",
                      "continue", "next step", "in progress"):
            with self.subTest(value=value):
                self.project(next_action=value)
                self.assert_invalid("names no action")
        self.project(next_action="补 A-02 的越界区间用例；verify: pytest tests/items -q")
        self.assertEqual(self.run_status()[0], 0)

    def test_a_live_slice_carries_the_cursor_instead_of_next_action(self):
        # The in-flight slice's own stage is the cursor, so project.md may be
        # empty here; a claimed slice with no acceptance rows yet counts.
        self.project(next_action=None)
        self.assertEqual(self.run_status()[0], 0)
        self.backlog(("A-01", "-", ""))
        self.write(self.state / "slices/S-01.md", (
            "# Slice S-01\n- owner: alice\n- claimed: 2026-09-08 / abc123\n"
            "- stage: 7 slice\n- write_scope: src/a\n"
        ))
        self.assertEqual(self.run_status()[0], 0)

    def test_delivered_evidence_must_be_locatable(self):
        for evidence in ("pytest tests/items -q -> 12 passed",
                         "打开 /orders → 首屏 3 行"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                self.assert_invalid("located again")

    def test_a_placeholder_after_the_at_sign_is_not_a_location(self):
        # "@ later" says an anchor will exist, not where it is; nobody can check
        # anything out and re-run the call, which is what the anchor is for.
        # The second group is what the word table missed until now; the joined
        # forms ("someday-soon") are the same promise wearing a hyphen.
        for ref in ("later", "稍后", "x", "TODO", "待补", "以后",
                    "待补充", "回头补", "之后补", "未提交", "最新提交",
                    "见下", "someday-soon", "TODOs", "todo_later"):
            with self.subTest(ref=ref):
                self.slice(status="delivered",
                           evidence=f"pytest tests/items -q -> 12 passed @ {ref}")
                self.assert_invalid("located again")

    def test_a_moving_ref_is_not_a_location(self):
        # "@ HEAD" is the worst of them because it has the shape of a ref and
        # passes every word table. It resolves to whoever committed last, so the
        # row keeps reading as anchored while pointing at different code.
        for ref in ("HEAD", "head", "HEAD~1", "HEAD^", "main", "master",
                    "origin/main", "latest"):
            with self.subTest(ref=ref):
                self.slice(status="delivered",
                           evidence=f"pytest tests/items -q -> 12 passed @ {ref}")
                self.assert_invalid("located again")

    def test_a_url_in_the_call_is_not_an_anchor(self):
        # An HTTP entrypoint puts a URL in every invocation. While a URL anywhere
        # in the string counted, this gate was free for every HTTP project: the
        # first row below passed with no anchor at all, the second with "@ later"
        # still attached. Losing it loses the only part of delivered that a
        # description of the work cannot stand in for.
        for evidence in ("curl https://api.example.com/orders -> 200 OK",
                         "curl https://api.example.com/orders -> 200 OK @ later",
                         "GET https://api.example.com/orders -> 200 OK，3 条",
                         "打开 https://app.example.com/orders → 首屏 3 行",
                         "POST https://api.example.com/items -> 201 @ HEAD",
                         # A URL inside the result is not one either: this row
                         # reports where the redirect went, and then says the
                         # anchor is coming later.
                         "POST /items -> 302 到 https://api.example.com/login @ later"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                self.assert_invalid("located again")

    def test_a_commit_or_link_anchors_the_evidence(self):
        # The anchor counts where a reader looks for it: at the end of the result
        # half. Row three is row one of the negative test above with a commit
        # appended -- the URL never was the anchor, the commit is.
        for evidence in (CALL,
                         "pytest tests/items -q -> 12 passed @ v1.4.0",
                         "curl https://api.example.com/orders -> 200 OK @ abc123",
                         "POST /items -> 201 id=it_7 @ https://ci.example/run/123",
                         "POST /items -> 201 id=it_7；运行 https://ci.example/run/123",
                         "pytest tests/items -q -> 12 passed @ later @ abc123",
                         "pytest tests/items -q -> 12 passed @ release-2026-09"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                code, report = self.run_status()
                self.assertEqual(code, 0, report)
                self.assertTrue(report["scope_complete"], report)

    def test_an_anchor_cannot_stand_in_for_the_result(self):
        # 09 asks for one real call and what it returned. Each row below fills
        # both halves and ends in something findable, and records no result: the
        # first two hand back the anchor, the third copies the URL the call was
        # sent to. They are also what pins the anchor to the result half -- read
        # against the whole line, "cmd ->" and "curl <url> ->" are the result and
        # all three pass again.
        for evidence in ("pytest tests/items -q -> @ abc123",
                         "打开 /orders → @ https://ci.example/run/123",
                         "curl https://api.example.com/orders -> https://api.example.com/orders"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                self.assert_invalid("anchor where the result belongs")
        # A URL is a fine result when it is what came back, not what was called.
        for evidence in ("POST /items -> 201 https://api.example.com/items/7 @ abc123",
                         "curl https://api.example.com/orders -> 200 OK @ abc123"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                code, report = self.run_status()
                self.assertEqual(code, 0, report)
                self.assertTrue(report["scope_complete"], report)

    def test_a_placeholder_is_not_a_result_either(self):
        # The script already keeps a table of words that promise a place instead
        # of naming one. It was applied to the anchor and not to the half the
        # anchor is there to locate, so "see above" plus a real commit read as a
        # recorded observation.
        for evidence in ("cmd --run -> 见上 @ abc123",
                         "app export -> TODO @ abc123",
                         "GET /orders -> 同上 @ https://ci.example/run/9"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                self.assert_invalid("anchor where the result belongs")
        # A real observation that merely contains a listed word still passes.
        self.slice(status="delivered", evidence="GET /orders -> 3 行，与上一次相同 @ abc123")
        code, report = self.run_status()
        self.assertEqual(code, 0, report)

    def test_a_half_built_state_still_names_the_old_file_beside_it(self):
        # An empty docs/workflow/ next to a full single-file ledger reports
        # "invalid" for the missing shards. Without this line the rendered text
        # says only "missing project.md", and the ledger beside it goes unread.
        self.write(self.root / "docs/workflow-state.md", "- lifecycle: BUILDING" + chr(10))
        (self.state / "project.md").unlink()
        run = self.run_cli()
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn("docs/workflow-state.md", run.stdout)
        self.assertIn("99-state-and-handoff.md", run.stdout)

    def test_the_anchor_must_end_the_result_half(self):
        # An anchor is only an anchor at the end of the result half. A ref or a
        # link found anywhere in it is part of what came back -- the redirect
        # target below, the note after the commit -- and neither one lets a
        # reader re-run the call. Row two also fails to be an anchor at the end
        # because the ref is not the last thing there.
        for evidence in ("POST /items -> 302 到 https://api.example.com/login 后仍是 401",
                         "pytest tests/items -q -> 12 passed @ abc123 之后又改了一版"):
            with self.subTest(evidence=evidence):
                self.slice(status="delivered", evidence=evidence)
                self.assert_invalid("located again")

    def test_acceptance_source_failures_name_their_own_cause(self):
        def reason():
            report = self.assert_invalid("acceptance_source")
            return [e for e in report["errors"] if e.startswith("acceptance_source")][0]

        (self.root / "docs/acceptance.md").unlink()
        unreadable = reason()
        self.source()
        self.project(source="docs/acceptance.md#Missing")
        absent = reason()
        self.project()
        path = self.root / "docs/acceptance.md"
        self.write(path, path.read_text(encoding="utf-8") + "\n## Current version\n| x |\n")
        duplicated = reason()
        self.write(path, "# Contract\n## Current version\nNo acceptance table yet.\n")
        untabled = reason()

        self.assertIn("cannot read", unreadable)
        self.assertIn("no heading", absent)
        self.assertIn("appears 2 times", duplicated)
        self.assertIn("no A-ID table", untabled)
        self.assertEqual(len({unreadable, absent, duplicated, untabled}), 4)

    def test_report_survives_a_console_that_is_not_utf8(self):
        # An English Windows console is cp1252. Crashing on the first Chinese
        # character exits 1, which an agent reads as "the state is invalid".
        self.project(target="docs/合同.md#完成边界 / deployed:staging")
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        for args in ((), ("--json",)):
            with self.subTest(args=args):
                run = self.run_cli(*args, env=env, utf8=False)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertIn("合同", run.stdout)

    def test_render_prints_the_next_action(self):
        run = self.run_cli()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(f"next action: {NEXT}", run.stdout)


if __name__ == "__main__":
    unittest.main()
