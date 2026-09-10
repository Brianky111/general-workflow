"""Run the status CLI against the committed example projects in examples/.

test_workflow_status.py synthesizes its state in a temp directory, so nothing a
reader can open ever proves the templates still work: the fixtures are written
alongside the script and drift with it. examples/ is committed, hand-written
from the templates, and checked here, so a contract change that the synthesized
fixtures happen to survive still turns this file red.

Two trees. greenfield/ is a project the workflow built from scratch; takeover/
is an old repository brought in through 00-brownfield-entry.md. Each is run the
way a consumer runs it: with --root, from elsewhere.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "workflow_status.py"
EXAMPLES = ROOT / "examples"
GREENFIELD = EXAMPLES / "greenfield"
TAKEOVER = EXAMPLES / "takeover"
# The seven fields of the shared project.md contract. A field that stops being
# written is invisible to the script -- most gates skip a value they cannot see.
CONTRACT_FIELDS = (
    "state_version", "lifecycle", "tier", "path", "next_action",
    "acceptance_source", "delivery_target",
)


def backlog_rows(example):
    """The (A-ID, assignment, note) rows of one example's backlog table."""
    text = (example / "docs" / "workflow" / "backlog.md").read_text(encoding="utf-8")
    return [
        tuple(cell.strip() for cell in match.groups())
        for match in re.finditer(r"(?m)^\|\s*(A-\d\S*)\s*\|([^|]*)\|([^|]*)\|", text)
    ]


def status(example, *args):
    """Invoke the shipped CLI the way a consumer does: --root, from elsewhere."""
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(example), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def promised_output(example):
    """The output block examples/README.md promises for this tree, or None."""
    readme = (EXAMPLES / "README.md").read_text(encoding="utf-8")
    block = re.search(
        rf"--root examples/{example.name}\n```\n+预期退出码 0，输出：\n+```text\n(.*?)```",
        readme, re.S,
    )
    return block[1] if block else None


class ExampleChecks:
    """What every example tree has to satisfy; mixed into one class per tree."""

    EXAMPLE: Path
    DOCUMENTED: tuple

    @classmethod
    def setUpClass(cls):
        # One run for the whole class: the example is read-only here.
        cls.cli = status(cls.EXAMPLE, "--json")
        try:
            cls.report = json.loads(cls.cli.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"the status CLI printed no JSON for {cls.EXAMPLE.name}/ "
                f"(exit {cls.cli.returncode}):\n{cls.cli.stdout}\n{cls.cli.stderr}"
            ) from exc
        cls.state = cls.EXAMPLE / "docs" / "workflow"

    def test_example_state_passes_every_gate(self):
        self.assertEqual(self.report["errors"], [], self.cli.stdout)
        self.assertEqual(self.cli.returncode, 0, self.cli.stderr)

    def test_scope_is_verified_but_not_complete(self):
        # Verified: the acceptance source and the backlog hold the same A-IDs.
        # Not complete: something is still owed. An example whose ledger were
        # finished would stop exercising the condition people get wrong -- a
        # cleared ledger is not a delivered project.
        self.assertTrue(self.report["scope_verified"], self.report)
        self.assertFalse(self.report["scope_complete"], self.report)

    def test_project_declares_all_seven_contract_fields(self):
        text = (self.state / "project.md").read_text(encoding="utf-8")
        for name in CONTRACT_FIELDS:
            with self.subTest(field=name):
                self.assertRegex(text, rf"(?m)^- {name}: ")

    def test_documented_files_exist(self):
        for name in self.DOCUMENTED:
            with self.subTest(file=name):
                self.assertTrue((self.EXAMPLE / name).is_file(), name)

    def test_terminal_notes_point_at_a_real_change_record(self):
        # The script only checks the note's shape. A deferred or dropped row
        # aimed at a file that does not exist passes it, and the example would
        # then teach exactly the habit the rule exists to stop.
        terminal = [
            (aid, assignment, note)
            for aid, assignment, note in backlog_rows(self.EXAMPLE)
            if assignment in ("deferred", "dropped")
        ]
        self.assertEqual({a for _, a, _ in terminal}, {"deferred", "dropped"}, terminal)
        for aid, assignment, note in terminal:
            with self.subTest(aid=aid, assignment=assignment):
                pointer = re.search(r"(\S+\.md)#(C-\d+)", note)
                self.assertIsNotNone(
                    pointer, f"{aid} is {assignment} but its note points at nothing locatable: {note}")
                target = self.EXAMPLE / pointer[1]
                self.assertTrue(target.is_file(), f"{pointer[1]} does not exist under {self.EXAMPLE.name}/")
                self.assertIn(f"## {pointer[2]}", target.read_text(encoding="utf-8"))

    def test_readme_shows_what_the_cli_actually_prints(self):
        # The examples exist because README fragments drift unnoticed; their
        # own promised output must not become another such fragment.
        block = promised_output(self.EXAMPLE)
        self.assertIsNotNone(
            block, f"examples/README.md shows no expected output for {self.EXAMPLE.name}/")
        printed = status(self.EXAMPLE)
        self.assertEqual(printed.returncode, 0, printed.stderr)
        self.assertEqual(
            [line.rstrip() for line in block.strip().splitlines()],
            [line.rstrip() for line in printed.stdout.strip().splitlines()],
        )


class GreenfieldExampleTests(ExampleChecks, unittest.TestCase):
    EXAMPLE = GREENFIELD
    DOCUMENTED = (
        "docs/contract.md",
        "docs/changes.md",
        "docs/workflow/project.md",
        "docs/workflow/backlog.md",
        "docs/workflow/slices/S-01.md",
    )

    def test_ledger_covers_every_status_value(self):
        self.assertEqual(self.report["delivered"], ["A-01"], self.report)
        self.assertEqual(self.report["in_flight"], ["A-02"], self.report)
        self.assertEqual(self.report["unclaimed"], ["A-03"], self.report)
        self.assertEqual(self.report["deferred_or_dropped"], ["A-04", "A-05"], self.report)

    def test_backlog_shows_all_four_assignment_values(self):
        # README sends readers here to see the ledger; a value missing from the
        # example is a value nobody is taught to write. dropped was the one
        # absent, and it is the one most easily handled by deleting the row
        # instead -- which passes the script and shortens the ledger.
        rows = backlog_rows(GREENFIELD)
        self.assertEqual(
            {assignment for _, assignment, _ in rows},
            {"S-01", "-", "deferred", "dropped"},
            rows,
        )

    def test_declaration_matches_the_shared_contract(self):
        self.assertEqual(self.report["state_version"], "2")
        self.assertEqual(self.report["lifecycle"], "BUILDING")
        self.assertEqual(self.report["tier"], "LEAN")
        self.assertEqual(self.report["path"], "lean")
        self.assertTrue(
            self.report["delivery_target"].endswith(" / implementation-and-tests"),
            self.report["delivery_target"],
        )

    def test_slice_carries_a_slice_map(self):
        # Stage 7 writes the slice map into the slice file; no second file. The
        # status script never reads it, so only this assertion keeps it there.
        text = (self.state / "slices" / "S-01.md").read_text(encoding="utf-8")
        self.assertIn("\n## Slice map\n", text)
        self.assertIn("- user_outcome:", text)
        self.assertIn("- real_entrypoint:", text)

    def test_repo_readme_snippets_are_cut_from_this_example(self):
        # The repo README says its three state snippets are cut from this tree.
        # Nothing enforced that, and they drifted: the README promised four
        # backlog values while the example only ever showed three. Every line of
        # a snippet has to be a line of the file it claims to quote.
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        quoted = dict(re.findall(r"<!-- (\S+?) -->\n(.*?)```", readme, re.S))
        self.assertEqual(
            set(quoted),
            {"docs/workflow/project.md", "docs/workflow/backlog.md",
             "docs/workflow/slices/S-01.md"},
            sorted(quoted),
        )
        for name, snippet in quoted.items():
            source = (GREENFIELD / name).read_text(encoding="utf-8").splitlines()
            for line in snippet.splitlines():
                if line.strip():
                    with self.subTest(file=name, line=line):
                        self.assertIn(line, source)


class TakeoverExampleTests(ExampleChecks, unittest.TestCase):
    EXAMPLE = TAKEOVER
    DOCUMENTED = (
        "docs/architecture-as-is.md",
        "docs/requirements.md",
        "docs/changes.md",
        "docs/workflow/project.md",
        "docs/workflow/backlog.md",
        "docs/workflow/slices/S-00.md",
    )

    def test_the_baseline_slice_has_no_owner_and_only_delivered_rows(self):
        # S-00 is the shape 00-brownfield-entry.md prescribes: nobody claimed
        # it, every row was called once at the takeover commit. The script has
        # to read that as finished, not as a claim with the owner missing.
        entry = next(item for item in self.report["slices"] if item["id"] == "S-00")
        self.assertEqual(entry["kind"], "feature", entry)
        self.assertEqual(entry["in_slice"], [], entry)
        self.assertEqual(len(entry["delivered"]), 6, entry)
        head = (self.state / "slices" / "S-00.md").read_text(encoding="utf-8").split("\n## ")[0]
        for name in ("owner", "claimed", "write_scope"):
            with self.subTest(field=name):
                self.assertRegex(head, rf"(?m)^- {name}: -$")

    def test_the_ledger_carries_every_review_answer(self):
        # Keep, change, drop and do-not-know each land on the backlog in a
        # different way; an example missing one teaches three answers and
        # leaves the fourth to be handled by deleting the row.
        rows = backlog_rows(TAKEOVER)
        self.assertEqual({a for _, a, _ in rows}, {"S-00", "-", "deferred", "dropped"}, rows)
        self.assertEqual(
            self.report["delivered"], ["A-01", "A-02", "A-03", "A-05", "A-06", "A-07"], self.report)
        self.assertEqual(self.report["unclaimed"], ["A-10"], self.report)
        self.assertEqual(self.report["deferred_or_dropped"], ["A-04", "A-08", "A-09"], self.report)
        self.assertEqual(self.report["in_flight"], [], self.report)

    def test_the_requirements_document_was_reviewed_row_by_row(self):
        # acceptance_source may only point at a reviewed document, and every
        # A-ID the ledger tracks has to carry the reviewer's answer; a row with
        # no answer is a guess that reached the ledger unread.
        text = (TAKEOVER / "docs" / "requirements.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^- status: reviewed \d{4}-\d{2}-\d{2}$")
        answered = {
            match[1]: match[2].strip()
            for match in re.finditer(r"(?m)^\|\s*(A-\d+)\s*\|(?:[^|]*\|){7}([^|]*)\|\s*$", text)
        }
        for aid, _, _ in backlog_rows(TAKEOVER):
            with self.subTest(aid=aid):
                self.assertIn(aid, answered)
                self.assertNotIn(answered[aid], ("", "-"), f"{aid} has no review answer")
        self.assertTrue(any(answer.startswith("不知道") for answer in answered.values()), answered)

    def test_the_takeover_kept_its_declaration(self):
        self.assertEqual(self.report["state_version"], "2")
        self.assertEqual(self.report["lifecycle"], "BUILDING")
        self.assertEqual(self.report["tier"], "STANDARD")
        self.assertEqual(self.report["path"], "full")
        self.assertTrue(
            self.report["delivery_target"].endswith(" / implementation-and-tests"),
            self.report["delivery_target"],
        )

    def test_deviations_are_recorded_as_facts_not_work(self):
        # The survey lists what it saw and marks each deviation unauthorized;
        # a row without that mark reads as a task, which is the drift the
        # firewall in the entry exists to stop.
        text = (TAKEOVER / "docs" / "architecture-as-is.md").read_text(encoding="utf-8")
        section = text.split("## 结构偏离", 1)[1]
        rows = [line for line in section.splitlines()
                if line.startswith("|") and not set(line) <= set("|- ")]
        self.assertGreaterEqual(len(rows), 3, rows)
        for row in rows[1:]:
            with self.subTest(row=row[:40]):
                self.assertIn("未授权", row)


if __name__ == "__main__":
    unittest.main()
