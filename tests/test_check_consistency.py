"""Exercise the consistency checker against copies of the v2 workflow tree.

Each case clones the active tree into a TemporaryDirectory, breaks one rule,
and asserts the checker emits the expected error. BudgetContractTests pins the
four size constants so raising a budget requires a deliberate two-file change.
"""

from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_consistency.py"
sys.path.insert(0, str(SCRIPT.parent))
import check_consistency  # noqa: E402

REFERENCES = sorted(path.name for path in (REPO / "references").glob("*.md"))
ARCHIVES = ("archive/general-workflow-v0.12.0", "archive/general-workflow-v1.10.1")
ROUTER_NAME = "00-router.md"
ROUTER = f"references/{ROUTER_NAME}"
OUTER = "references/05-outer-loop-factory.md"
GUARDRAILS = "references/02-codebase-guardrails.md"
VERIFICATION = "references/03-verification-and-artifacts.md"
GARDENING = "references/04-correction-and-gardening.md"
CONTRACT = "references/06-repo-guard-contract.md"
LEAF = "06-repo-guard-contract.md"
POINTER = "契约说明文档"
LF = "\n"
CRLF = "\r\n"


class CheckConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="check-consistency-v2-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workflow copy"
        self.write("SKILL.md", (REPO / "SKILL.md").read_text(encoding="utf-8"))
        for name in REFERENCES:
            self.write(
                f"references/{name}",
                (REPO / "references" / name).read_text(encoding="utf-8"),
            )
        for script_name in ("repo_guard.py", "install.py", "sync_vendor.py"):
            self.write(
                f"scripts/{script_name}",
                (REPO / "scripts" / script_name).read_text(encoding="utf-8"),
            )
        shutil.copytree(REPO / "vendor" / "pstack", self.root / "vendor" / "pstack")
        self.write("tests/test_repo_guard.py", "")
        self.write("archive/ARCHIVE-NOTE.md", "placeholder\n")
        for archive in ARCHIVES:
            for name in ("SKILL.md", "README.md", "references/.keep", "scripts/.keep"):
                self.write(f"{archive}/{name}", "")

    def write(self, name: str, text: str, newline: str = LF) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text.replace(LF, newline))

    def read(self, name: str) -> str:
        return (self.root / name).read_text(encoding="utf-8")

    def replace(self, name: str, old: str, new: str) -> None:
        text = self.read(name)
        self.assertEqual(text.count(old), 1, f"{old!r} is not unique in {name}")
        self.write(name, text.replace(old, new))

    def set_section(self, name: str, heading: str, body: str) -> None:
        lines = self.read(name).split(LF)
        start = lines.index(heading)
        depth = len(heading.split(" ")[0])
        end = next(
            (i for i in range(start + 1, len(lines)) if re.match(rf"^#{{1,{depth}}}\s", lines[i])),
            len(lines),
        )
        self.write(name, LF.join(lines[:start + 1] + ["", body, ""] + lines[end:]))

    def run_check(self, *args: str) -> tuple[int, str]:
        run = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *args],
            cwd=self.temp.name,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertIn(run.returncode, (0, 1), run.stdout + run.stderr)
        return run.returncode, run.stdout

    def errors(self) -> list[str]:
        code, out = self.run_check("--root", str(self.root))
        prefix = "ERROR "
        found = [line[len(prefix):] for line in out.splitlines() if line.startswith(prefix)]
        self.assertEqual(code, 1, out)
        return found

    def assert_error(self, fragment: str) -> list[str]:
        found = self.errors()
        self.assertTrue(any(fragment in error for error in found), found)
        return found

    def assert_only_error(self, fragment: str) -> str:
        found = self.assert_error(fragment)
        self.assertEqual(len(found), 1, found)
        return found[0]

    def test_a_clean_copy_passes(self):
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("7 active reference files, 0 error(s), 0 warning(s)", out)

    def test_the_default_root_is_the_shipped_tree(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("7 active reference files, 0 error(s), 0 warning(s)", out)

    def test_file_missing_from_reference_map_is_reported(self):
        head, sep, tail = self.read("SKILL.md").partition("## Reference Map")
        kept = [
            line for line in tail.split(LF)
            if not line.startswith(f"- `{LEAF}`")
        ]
        self.write("SKILL.md", head + sep + LF.join(kept))
        self.assert_only_error(f"references/{LEAF} is not listed in the Reference Map")

    def test_reference_map_cannot_list_missing_file(self):
        row = "## Reference Map\n"
        self.replace("SKILL.md", row, row + "\n- `07-nonexistent.md`：占位。")
        found = self.assert_error("Reference Map lists missing file: 07-nonexistent.md")
        self.assertTrue(
            any("mentions missing reference: 07-nonexistent.md" in e for e in found),
            found,
        )

    def test_unreachable_reference_is_caught(self):
        head, sep, tail = self.read("SKILL.md").partition("## Reference Map")
        self.write("SKILL.md", head.replace(LEAF, POINTER) + sep + tail)
        for name in REFERENCES:
            if name != LEAF:
                self.write(f"references/{name}", self.read(f"references/{name}").replace(LEAF, POINTER))
        self.assert_only_error(f"references/{LEAF} is unreachable from active router/rules")

    def test_emptied_section_and_gate_body_minimums_are_enforced(self):
        self.set_section(GARDENING, "## AGENTS.md 瘦身规则", "")
        error = self.assert_only_error("section 'AGENTS.md 瘦身规则' has 0 characters of body")
        self.assertIn("under the 30", error)

        self.setUp()
        self.set_section(
            ROUTER,
            "## 全局停止条件",
            "遇到意图歧义、不可逆边界或检验环境损坏时，必须先停下来向用户确认关键决策再继续。",
        )
        error = self.assert_only_error("under the 60")
        self.assertGreaterEqual(int(re.search(r"has (\d+) characters", error)[1]), 30)

    def test_heading_inside_fence_does_not_count_as_section(self):
        self.replace(CONTRACT, "## 契约门禁", "~~~markdown\n## 契约门禁\n~~~")
        self.assert_only_error("missing policy anchor: ## 契约门禁")

    def test_fenced_example_does_not_shadow_real_section(self):
        self.write(CONTRACT, self.read(CONTRACT) + "\n~~~markdown\n## 契约门禁\n~~~\n")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

    def pad_to(self, name: str, target: int) -> str:
        text = self.read(name)
        line = "对齐体积预算的填充行。" + LF
        while len(text.encode("utf-8")) + len(line.encode("utf-8")) <= target:
            text += line
        return text

    def test_crlf_checkout_passes_with_identical_byte_counts(self):
        for name in ["SKILL.md"] + [f"references/{ref}" for ref in REFERENCES]:
            self.write(name, self.read(name), newline=CRLF)
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)

        padded = self.read(CONTRACT) + LF + "撑破预算的填充行。\n" * 400
        measured = {}
        for newline in (LF, CRLF):
            self.write(CONTRACT, padded, newline=newline)
            error = self.assert_only_error("over its 12000-byte budget")
            measured[newline] = (
                (self.root / CONTRACT).stat().st_size,
                int(re.search(r"is (\d+) bytes", error)[1]),
            )
        self.assertNotEqual(measured[LF][0], measured[CRLF][0])
        self.assertEqual(measured[LF][1], measured[CRLF][1])

    def test_deleted_repo_guard_or_tests_dir_caught(self):
        (self.root / "scripts/repo_guard.py").unlink()
        found = self.assert_error("missing scripts/repo_guard.py")
        self.assertTrue(any("does not exist: scripts/repo_guard.py" in e for e in found), found)

        shutil.rmtree(self.root / "tests")
        self.assert_error("missing tests/")

    def test_shuffled_or_dropped_pyramid_layers_caught(self):
        l1, l2 = "1. 代码库与 API 设计", "2. 静态分析与可执行检查"
        swapped = self.read("SKILL.md").replace(l1, "<swap>").replace(l2, l1).replace("<swap>", l2)
        self.write("SKILL.md", swapped)
        self.assert_only_error("SKILL.md trust pyramid layers are out of order")

    def test_unlisted_reference_file_rejected(self):
        self.write("references/07-extra.md", "# Extra\n\n正文。\n")
        found = self.assert_error("unexpected active reference (add it to checker/map): references/07-extra.md")
        self.assertTrue(any("07-extra.md is not listed in the Reference Map" in e for e in found), found)

    def test_single_authority_phrases_cannot_be_pasted_elsewhere_or_dropped(self):
        self.write(ROUTER, self.read(ROUTER) + "\n- 提醒：默认禁止解释 workaround 的注释。\n")
        found = self.assert_error("00-router.md restates 注释与逃生舱策略")
        self.assertTrue(any("references/02-codebase-guardrails.md" in e for e in found), found)

        self.setUp()
        self.replace(VERIFICATION, "禁止用 HEAD、main 或 later 冒充验证锚点", "不可用移动分支做锚点")
        self.assert_only_error(
            "03-verification-and-artifacts.md no longer contains the 行为产物与新鲜度门禁 wording"
        )

    def test_reworded_trust_ladder_caught_outside_owner(self):
        self.write(
            ROUTER,
            self.read(ROUTER)
            + LF.join([
                "",
                "## 层级速查",
                "",
                "- L0 尚未建护栏禁止并行与合入。",
                "- L1 需要通过检查并人工审产物。",
                "- L2 必须逃生舱清零后开启探索测试。",
                "- L3 验证必须锚定当前版本才允许自动合入。",
                "",
            ]),
        )
        found = self.assert_error("00-router.md section '层级速查' reads as a restated trust ladder")
        self.assertTrue(any("references/05-outer-loop-factory.md" in e for e in found), found)

    def test_both_archives_checked_and_installed_copy_supported(self):
        (self.root / ARCHIVES[1] / "README.md").unlink()
        self.assert_only_error(f"archive is incomplete: {Path(ARCHIVES[1]) / 'README.md'}")

        shutil.rmtree(self.root / "archive")
        code, out = self.run_check("--root", str(self.root))
        self.assertEqual(code, 0, out)
        self.assertIn("NOTE  archive/ is absent", out)

        self.write(CONTRACT, self.read(CONTRACT) + f"\n旧版参考 {ARCHIVES[1]}/references。\n")
        self.assert_error("active SKILL/references must not depend on archived workflow path")

    def test_vendor_tampered_checksum_caught(self):
        target = self.root / "vendor" / "pstack" / "skills" / "why" / "SKILL.md"
        target.write_text(target.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
        self.assert_only_error("checksum mismatch for vendor/pstack/skills/why/SKILL.md")

    def test_vendor_undeclared_skill_and_missing_license_caught(self):
        self.write("vendor/pstack/skills/extra-skill/SKILL.md", "---\nname: extra-skill\ndescription: x\n---\n")
        found = self.assert_error("undeclared vendored skill directory: vendor/pstack/skills/extra-skill")
        self.assertTrue(any("undeclared file under vendor/pstack" in e for e in found), found)

        self.setUp()
        (self.root / "vendor" / "pstack" / "LICENSE").unlink()
        found = self.assert_error("missing upstream license: vendor/pstack/LICENSE")
        self.assertTrue(any("missing vendored file: vendor/pstack/LICENSE" in e for e in found), found)

    def test_vendor_excluded_statechart_tests_and_broken_mentions_caught(self):
        self.write("vendor/pstack/skills/statechart/scripts/test/dummy.test.ts", "export {};\n")
        found = self.assert_error("excluded upstream test directory must not be vendored")
        self.assertTrue(any("undeclared file under vendor/pstack" in e for e in found), found)

        self.setUp()
        self.write(ROUTER, self.read(ROUTER) + "\n参见 `vendor/pstack/skills/does-not-exist/SKILL.md`。\n")
        self.assert_only_error("00-router.md references missing vendor path: vendor/pstack/skills/does-not-exist/SKILL.md")

    def test_missing_install_script_caught(self):
        (self.root / "scripts" / "install.py").unlink()
        self.assert_only_error("missing scripts/install.py")

        self.setUp()
        (self.root / "scripts" / "sync_vendor.py").unlink()
        self.assert_only_error("missing scripts/sync_vendor.py")


PINNED_SIZE_BUDGETS = {"SKILL.md": 6_500, "00-router.md": 7_500}
PINNED_REFERENCE_BUDGET = 12_000
PINNED_BUDGET_WARN = 0.90

WHY_THE_BUDGETS_HOLD = """
SKILL.md and 00-router.md are loaded at the start of every turn; references
01-06 are loaded one at a time on demand. Raising a budget to absorb prose
instead of keeping docs lean erodes context discipline across every future
session. Change both files together with rationale if a budget truly changes.
"""


class BudgetContractTests(unittest.TestCase):
    def run_budgets(self, texts: dict[str, str]):
        errors, warnings = [], []
        check_consistency.check_size_budgets(texts, errors, warnings)
        return errors, warnings

    def test_budget_constants_are_pinned(self):
        self.assertEqual(check_consistency.SIZE_BUDGETS, PINNED_SIZE_BUDGETS, WHY_THE_BUDGETS_HOLD)
        self.assertEqual(check_consistency.REFERENCE_BUDGET, PINNED_REFERENCE_BUDGET, WHY_THE_BUDGETS_HOLD)
        self.assertEqual(check_consistency.BUDGET_WARN, PINNED_BUDGET_WARN, WHY_THE_BUDGETS_HOLD)

    def test_each_budget_boundary_is_enforced(self):
        budgets = {**PINNED_SIZE_BUDGETS, LEAF: PINNED_REFERENCE_BUDGET}
        for name, budget in budgets.items():
            with self.subTest(name=name):
                errors, _ = self.run_budgets({name: "x" * budget})
                self.assertEqual(errors, [])
                errors, _ = self.run_budgets({name: "x" * (budget + 1)})
                self.assertEqual(len(errors), 1)
                self.assertIn(f"is {budget + 1} bytes, over its {budget}-byte budget", errors[0])

    def test_warn_line_fires_at_ninety_percent(self):
        budget = PINNED_SIZE_BUDGETS[ROUTER_NAME]
        notice = round(budget * (1 - PINNED_BUDGET_WARN))
        self.assertEqual(notice, 750)
        _, quiet = self.run_budgets({ROUTER_NAME: "x" * (budget - notice)})
        self.assertEqual(quiet, [])
        _, loud = self.run_budgets({ROUTER_NAME: "x" * (budget - notice + 1)})
        self.assertEqual(len(loud), 1)
        self.assertIn(f"({notice - 1} bytes left)", loud[0])


if __name__ == "__main__":
    unittest.main()
