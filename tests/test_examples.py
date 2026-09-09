"""Run the status CLI against the committed example project in examples/.

test_workflow_status.py synthesizes its state in a temp directory, so nothing a
reader can open ever proves the templates still work: the fixtures are written
alongside the script and drift with it. examples/ is committed, hand-written
from the templates, and checked here, so a contract change that the synthesized
fixtures happen to survive still turns this file red.
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "workflow_status.py"
EXAMPLE = ROOT / "examples"
STATE = EXAMPLE / "docs" / "workflow"
# The seven fields of the shared project.md contract. A field that stops being
# written is invisible to the script -- most gates skip a value they cannot see.
CONTRACT_FIELDS = (
    "state_version", "lifecycle", "tier", "path", "next_action",
    "acceptance_source", "delivery_target",
)
DOCUMENTED = (
    "README.md",
    "docs/contract.md",
    "docs/changes.md",
    "docs/workflow/project.md",
    "docs/workflow/backlog.md",
    "docs/workflow/slices/S-01.md",
)


def backlog_rows():
    """The (A-ID, assignment, note) rows of the example backlog table."""
    text = (STATE / "backlog.md").read_text(encoding="utf-8")
    return [
        tuple(cell.strip() for cell in match.groups())
        for match in re.finditer(r"(?m)^\|\s*(A-\d\S*)\s*\|([^|]*)\|([^|]*)\|", text)
    ]


def status(*args):
    """Invoke the shipped CLI the way a consumer does: --root, from elsewhere."""
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(EXAMPLE), *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


class ExampleProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One run for the whole class: the example is read-only here.
        cls.cli = status("--json")
        try:
            cls.report = json.loads(cls.cli.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"the status CLI printed no JSON for examples/ (exit {cls.cli.returncode}):\n"
                f"{cls.cli.stdout}\n{cls.cli.stderr}"
            ) from exc

    def test_example_state_passes_every_gate(self):
        self.assertEqual(self.report["errors"], [], self.cli.stdout)
        self.assertEqual(self.cli.returncode, 0, self.cli.stderr)

    def test_scope_is_verified_but_not_complete(self):
        # Verified: the acceptance source and the backlog hold the same A-IDs.
        # Not complete: one row is still in-slice and one is unclaimed. An
        # example whose ledger were finished would stop exercising the two
        # conditions that keep scope_complete false, which is the half people
        # get wrong -- a cleared ledger is not a delivered project.
        self.assertTrue(self.report["scope_verified"], self.report)
        self.assertFalse(self.report["scope_complete"], self.report)

    def test_ledger_covers_every_status_value(self):
        self.assertEqual(self.report["delivered"], ["A-01"], self.report)
        self.assertEqual(self.report["in_flight"], ["A-02"], self.report)
        self.assertEqual(self.report["unclaimed"], ["A-03"], self.report)
        self.assertEqual(self.report["deferred_or_dropped"], ["A-04", "A-05"], self.report)

    def test_backlog_shows_all_four_assignment_values(self):
        # README sends readers here to see the ledger; a value missing from the
        # example is a value nobody is taught to write. 'dropped' was the one
        # absent, and it is the one most easily handled by deleting the row
        # instead -- which passes the script and shortens the ledger.
        rows = backlog_rows()
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

    def test_project_declares_all_seven_contract_fields(self):
        text = (STATE / "project.md").read_text(encoding="utf-8")
        for name in CONTRACT_FIELDS:
            with self.subTest(field=name):
                self.assertRegex(text, rf"(?m)^- {name}: ")

    def test_slice_carries_a_slice_map(self):
        # Stage 7 writes the slice map into the slice file; no second file. The
        # status script never reads it, so only this assertion keeps it there.
        text = (STATE / "slices" / "S-01.md").read_text(encoding="utf-8")
        self.assertIn("\n## Slice map\n", text)
        self.assertIn("- user_outcome:", text)
        self.assertIn("- real_entrypoint:", text)

    def test_documented_files_exist(self):
        for name in DOCUMENTED:
            with self.subTest(file=name):
                self.assertTrue((EXAMPLE / name).is_file(), name)

    def test_terminal_notes_point_at_a_real_change_record(self):
        # The script only checks the note's shape. A deferred or dropped row
        # aimed at a file that does not exist passes it, and the example would
        # then teach exactly the habit the rule exists to stop.
        terminal = {
            assignment: note
            for _, assignment, note in backlog_rows()
            if assignment in ("deferred", "dropped")
        }
        self.assertEqual(set(terminal), {"deferred", "dropped"}, terminal)
        for assignment, note in terminal.items():
            with self.subTest(assignment=assignment):
                pointer = re.search(r"(\S+\.md)#(C-\d+)", note)
                self.assertIsNotNone(pointer, f"the {assignment} note points at nothing locatable: {note}")
                target = EXAMPLE / pointer[1]
                self.assertTrue(target.is_file(), f"{pointer[1]} does not exist under examples/")
                self.assertIn(f"## {pointer[2]}", target.read_text(encoding="utf-8"))

    def test_repo_readme_snippets_are_cut_from_this_example(self):
        # The repo README says its three state snippets are cut from examples/.
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
            source = (EXAMPLE / name).read_text(encoding="utf-8").splitlines()
            for line in snippet.splitlines():
                if line.strip():
                    with self.subTest(file=name, line=line):
                        self.assertIn(line, source)

    def test_readme_shows_what_the_cli_actually_prints(self):
        # The example exists because README fragments drift unnoticed; its own
        # promised output must not become another such fragment.
        readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        block = re.search(r"预期退出码 0，输出：\n+```text\n(.*?)```", readme, re.S)
        self.assertIsNotNone(block, "examples/README.md no longer shows an expected output block")
        printed = status()
        self.assertEqual(printed.returncode, 0, printed.stderr)
        self.assertEqual(
            [line.rstrip() for line in block[1].strip().splitlines()],
            [line.rstrip() for line in printed.stdout.strip().splitlines()],
        )


if __name__ == "__main__":
    unittest.main()
