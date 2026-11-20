"""Run scripts/repo_guard.py against the committed example trees in examples/."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "repo_guard.py"
EXAMPLES = ROOT / "examples"
CLEAN_APP = EXAMPLES / "clean-app"
WEEDING = EXAMPLES / "weeding-brownfield"
VERIFY_SKILL = EXAMPLES / "verify-skill-app"


def run_guard(example: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(example), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def promised_output(example: Path) -> str | None:
    readme = (EXAMPLES / "README.md").read_text(encoding="utf-8")
    match = re.search(
        rf"--root examples/{re.escape(example.name)} --run-check\n```\n+预期退出码 0，输出：\n+```text\n(.*?)```",
        readme,
        re.S,
    )
    return match[1] if match else None


class ExampleChecks:
    EXAMPLE: Path
    EXPECTED_TRUST: str
    EXPECTED_ESCAPES: int
    EXPECTED_MAX_ESCAPES: int
    EXPECTED_TOTAL_FEATURES: int
    EXPECTED_CORE_FEATURES: int
    EXPECTED_VERIFIED: int

    @classmethod
    def setUpClass(cls):
        cls.cli = run_guard(cls.EXAMPLE, "--run-check", "--json")
        cls.report = json.loads(cls.cli.stdout)

    def test_example_passes_all_guardrails_and_checks(self):
        self.assertEqual(self.cli.returncode, 0, self.cli.stdout + self.cli.stderr)
        self.assertEqual(self.report["guard_status"], "ready")
        self.assertEqual(self.report["errors"], [], self.report["errors"])
        self.assertEqual(self.report["warnings"], [], self.report["warnings"])
        self.assertTrue(self.report["check_run"]["passed"], self.report["check_run"])

    def test_example_metrics_match_contract(self):
        self.assertEqual(self.report["trust_level"], self.EXPECTED_TRUST)
        self.assertEqual(self.report["scan"]["escape_hatches"], self.EXPECTED_ESCAPES)
        self.assertEqual(self.report["max_escape_hatches"], self.EXPECTED_MAX_ESCAPES)
        self.assertEqual(self.report["verification"]["features_total"], self.EXPECTED_TOTAL_FEATURES)
        self.assertEqual(self.report["verification"]["core_features"], self.EXPECTED_CORE_FEATURES)
        self.assertEqual(self.report["verification"]["verified_features"], self.EXPECTED_VERIFIED)

    def test_examples_readme_matches_actual_cli_output(self):
        expected = promised_output(self.EXAMPLE)
        self.assertIsNotNone(expected, f"examples/README.md missing output block for {self.EXAMPLE.name}")
        printed = run_guard(self.EXAMPLE, "--run-check")
        self.assertEqual(printed.returncode, 0, printed.stderr)
        self.assertEqual(
            [line.rstrip() for line in expected.strip().splitlines()],
            [line.rstrip() for line in printed.stdout.strip().splitlines()],
        )


class CleanAppExampleTests(ExampleChecks, unittest.TestCase):
    EXAMPLE = CLEAN_APP
    EXPECTED_TRUST = "L1"
    EXPECTED_ESCAPES = 0
    EXPECTED_MAX_ESCAPES = 0
    EXPECTED_TOTAL_FEATURES = 3
    EXPECTED_CORE_FEATURES = 2
    EXPECTED_VERIFIED = 2

    def test_repo_readme_snippets_are_cut_from_clean_app(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        quoted = dict(re.findall(r"<!-- (\S+?) -->\n(.*?)```", readme, re.S))
        self.assertEqual(
            set(quoted),
            {
                ".guardrails/config.json",
                ".guardrails/feature-map.md",
                ".guardrails/verification.md",
            },
            sorted(quoted),
        )
        for name, snippet in quoted.items():
            source = (CLEAN_APP / name).read_text(encoding="utf-8").splitlines()
            for line in snippet.splitlines():
                if line.strip():
                    with self.subTest(file=name, line=line):
                        self.assertIn(line, source)


class WeedingBrownfieldExampleTests(ExampleChecks, unittest.TestCase):
    EXAMPLE = WEEDING
    EXPECTED_TRUST = "L0"
    EXPECTED_ESCAPES = 1
    EXPECTED_MAX_ESCAPES = 1
    EXPECTED_TOTAL_FEATURES = 2
    EXPECTED_CORE_FEATURES = 1
    EXPECTED_VERIFIED = 1


class VerifySkillAppExampleTests(ExampleChecks, unittest.TestCase):
    EXAMPLE = VERIFY_SKILL
    EXPECTED_TRUST = "L1"
    EXPECTED_ESCAPES = 0
    EXPECTED_MAX_ESCAPES = 0
    EXPECTED_TOTAL_FEATURES = 2
    EXPECTED_CORE_FEATURES = 2
    EXPECTED_VERIFIED = 2

    def test_verify_skill_metadata_is_reported(self):
        vs = self.report["verify_skill"]
        self.assertIsNotNone(vs)
        self.assertEqual(vs["path"], ".agents/skills/verify-orders")
        self.assertEqual(vs["name"], "verify-orders")
        self.assertEqual(vs["features"], 2)
        self.assertEqual(self.report["scan"]["anti_patterns"], 0)
        self.assertTrue(self.report["anti_patterns_config"]["configured"])


if __name__ == "__main__":
    unittest.main()
