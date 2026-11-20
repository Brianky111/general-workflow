"""Regression tests for scripts/repo_guard.py.

Every test constructs a minimal target repository inside TemporaryDirectory,
executes repo_guard via CLI or inspect_repo, and asserts on both exit codes
and exact actionable error/warning messages.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "repo_guard.py"


class RepoGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="repo-guard-test-")
        self.addCleanup(self.temp.cleanup)
        # Include a space in the path to catch unquoted path bugs.
        self.repo = Path(self.temp.name) / "target repo"
        self.repo.mkdir(parents=True, exist_ok=True)

    def write(self, rel_path: str, content: str, newline: str = "\n") -> Path:
        path = self.repo / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(content.replace("\r\n", "\n").replace("\n", newline))
        return path

    def write_minimal_guardrails(
        self,
        *,
        trust_level: str = "L1",
        max_allowed: int = 0,
        require_fresh_head: bool = False,
        forbidden_primitives: list | None = None,
        boundary_rules: list | None = None,
        extra_patterns: list | None = None,
        check_command: str = "python -c \"print('ok')\"",
        verify_cli: str = "python -c \"print('verify')\"",
        prose_max_bytes: int = 6000,
    ) -> None:
        cfg = {
            "guardrails_version": 2,
            "trust_level": trust_level,
            "check_command": check_command,
            "verify_cli": verify_cli,
            "source_roots": ["src"],
            "exclude_dirs": [".git", "__pycache__", ".guardrails"],
            "prose_files": ["AGENTS.md"],
            "prose_max_bytes": prose_max_bytes,
            "require_fresh_head": require_fresh_head,
            "escape_hatches": {
                "max_allowed": max_allowed,
                "extra_patterns": extra_patterns or [],
            },
            "forbidden_primitives": forbidden_primitives or [],
            "boundary_rules": boundary_rules or [],
        }
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        self.write(
            ".guardrails/feature-map.md",
            "\n".join([
                "# Feature Map",
                "| Feature | Entrypoint | Verify CLI | Artifact | Priority |",
                "| --- | --- | --- | --- | --- |",
                "| 导出报表 | `python -m src.app` | `python -m tools.verify` | `artifacts/out.txt` | core |",
                "",
            ]),
        )
        self.write(
            ".guardrails/verification.md",
            "\n".join([
                "# Verification",
                "| Feature | Command | Observed | Artifact | Commit |",
                "| --- | --- | --- | --- | --- |",
                "| 导出报表 | `python -m tools.verify` | 生成 2 行 CSV 输出 | `artifacts/out.txt` | a1b2c3d |",
                "",
            ]),
        )
        self.write("artifacts/out.txt", "id,amount\n1,100\n")
        self.write("src/app.py", "def run():\n    return 1\n")

    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> tuple[int, dict, str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(self.repo), "--json", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=merged_env,
        )
        self.assertIn(proc.returncode, (0, 1), proc.stdout + proc.stderr)
        report = json.loads(proc.stdout)
        return proc.returncode, report, proc.stderr

    def test_uninitialized_repo_returns_zero(self):
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(report["guard_status"], "uninitialized")
        self.assertEqual(report["errors"], [])

    def test_legacy_v1_docs_workflow_detected_without_overwriting(self):
        self.write("docs/workflow/project.md", "# Project\n- state_version: 2\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(report["guard_status"], "legacy_v1")
        self.assertEqual(report["legacy_paths"], ["docs/workflow"])
        self.assertIn("06-repo-guard-contract.md", report["message"])

    def test_legacy_v1_single_file_state_detected(self):
        self.write("WORKFLOW-STATE.md", "# Old state\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(report["guard_status"], "legacy_v1")
        self.assertEqual(report["legacy_paths"], ["WORKFLOW-STATE.md"])

    def test_missing_required_guardrail_files_fail(self):
        self.write(".guardrails/config.json", "{}")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(report["guard_status"], "invalid")
        self.assertTrue(any("missing .guardrails/feature-map.md" in e for e in report["errors"]))
        self.assertTrue(any("missing .guardrails/verification.md" in e for e in report["errors"]))

    def test_invalid_json_and_wrong_version_rejected(self):
        self.write_minimal_guardrails()
        self.write(".guardrails/config.json", "{not json")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("invalid JSON" in e for e in report["errors"]))

        self.write(".guardrails/config.json", json.dumps({"guardrails_version": True, "trust_level": "L0", "check_command": "pytest"}))
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("guardrails_version must be integer 2" in e for e in report["errors"]))

        self.write(".guardrails/config.json", json.dumps({"guardrails_version": 1, "trust_level": "L0", "check_command": "pytest"}))
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("unsupported guardrails_version 1" in e for e in report["errors"]))

    def test_invalid_trust_level_and_placeholders_rejected(self):
        self.write_minimal_guardrails(trust_level="L9", check_command="TODO", verify_cli="-")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("trust_level 'L9' is invalid" in e for e in report["errors"]))
        self.assertTrue(any("check_command is missing or placeholder" in e for e in report["errors"]))

        self.write_minimal_guardrails(trust_level="L1", verify_cli="待补")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("requires a non-placeholder verify_cli" in e for e in report["errors"]))

    def test_l2_and_l3_enforce_zero_escape_hatches_and_fresh_head(self):
        self.write_minimal_guardrails(trust_level="L2", max_allowed=1)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("L2 requires escape_hatches.max_allowed == 0" in e for e in report["errors"]))

        self.write_minimal_guardrails(trust_level="L3", max_allowed=0, require_fresh_head=False)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("L3 automerge requires require_fresh_head: true" in e for e in report["errors"]))

    def test_escape_hatches_detection_ratchet_and_warning(self):
        self.write_minimal_guardrails(trust_level="L0", max_allowed=1)
        self.write(
            "src/legacy.py",
            "x = 1  # noqa\ny = 2  # type: ignore\n# HACK: quick fix\n",
        )
        self.write(
            "src/view.ts",
            "// eslint-disable-next-line\n// @ts-ignore\n",
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(report["scan"]["escape_hatches"], 5)
        self.assertTrue(any("exceed ratchet max_allowed (1)" in e for e in report["errors"]))

        # When actual drops below max_allowed, emit ratchet-down warning.
        self.write("src/legacy.py", "x = 1\n")
        self.write("src/view.ts", "export const ok = 1;\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(report["scan"]["escape_hatches"], 0)
        self.assertTrue(any("lower escape_hatches.max_allowed to 0" in w for w in report["warnings"]))

    def test_custom_extra_pattern_and_invalid_regex(self):
        self.write_minimal_guardrails(trust_level="L0", max_allowed=0, extra_patterns=[r"\bFIXME\b"])
        self.write("src/app.py", "# FIXME: clean later\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("extra-1" in e for e in report["errors"]))

        self.write_minimal_guardrails(trust_level="L0", extra_patterns=["[unclosed"])
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("invalid regex in extra_patterns" in e for e in report["errors"]))

    def test_forbidden_primitives_allow_paths_comments_and_message_length(self):
        rules = [{
            "id": "no-sleep",
            "pattern": r"\btime\.sleep\s*\(",
            "globs": ["src/**/*.py"],
            "allow_paths": ["src/runtime"],
            "message": "业务逻辑禁止直调 time.sleep，请改用 src/runtime/clock.py 封装接口。",
        }]
        self.write_minimal_guardrails(forbidden_primitives=rules)
        self.write("src/runtime/clock.py", "import time\ndef wait():\n    time.sleep(0.01)\n")
        self.write("src/ui/page.py", "# example: time.sleep(1) is disallowed here\nx = 'http://x' # time.sleep(1)\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])

        self.write("src/ui/page.py", "import time\ntime.sleep(0.5)\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any(
            "forbidden_primitive 'no-sleep' at src/ui/page.py:2" in e and "src/runtime/clock.py" in e
            for e in report["errors"]
        ))

        short_rules = [{
            "id": "no-sleep",
            "pattern": r"time\.sleep",
            "globs": ["src/**/*.py"],
            "message": "forbidden",
        }]
        self.write_minimal_guardrails(forbidden_primitives=short_rules)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("requires an actionable root-cause message" in e for e in report["errors"]))

    def test_boundary_rules_python_and_js_and_path_escape(self):
        rules = [{
            "id": "ui-no-storage",
            "from_dir": "src/ui",
            "forbid_import": "core/storage",
            "message": "src/ui 不得绕过 core/api 直接导入 core/storage，请改调 OrderService。",
        }]
        self.write_minimal_guardrails(boundary_rules=rules)
        self.write("src/ui/view.py", "# from core.storage import Store\nfrom src.core.api import Service\n")
        self.write("src/ui/widget.ts", "import { api } from '../core/api';\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])

        self.write("src/ui/view.py", "from src.core.storage import Store\n")
        self.write("src/ui/widget.ts", "import { db } from '../core/storage';\nconst x = require('../core/storage/db');\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(report["scan"]["boundary_violations"], 3)
        self.assertTrue(any("boundary_rule 'ui-no-storage' at src/ui/view.py:1" in e for e in report["errors"]))
        self.assertTrue(any("boundary_rule 'ui-no-storage' at src/ui/widget.ts:1" in e for e in report["errors"]))
        self.assertTrue(any("boundary_rule 'ui-no-storage' at src/ui/widget.ts:2" in e for e in report["errors"]))

        bad_rules = [{
            "id": "escape-dir",
            "from_dir": "../outside",
            "forbid_import": "core/storage",
            "message": "这条边界消息足够长但是目录越界了。",
        }]
        self.write_minimal_guardrails(boundary_rules=bad_rules)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("path escapes the project root" in e for e in report["errors"]))

    def test_prose_diet_lf_crlf_parity_nested_agents_and_prohibitions(self):
        self.write_minimal_guardrails(prose_max_bytes=120)
        # 6 lines of 18 bytes each -> 108 LF bytes (<=120), 114 CRLF bytes.
        text = "\n".join([f"rule line {i:02d} ok!" for i in range(6)]) + "\n"
        self.write("AGENTS.md", text, newline="\r\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["prose"][0]["file"], "AGENTS.md")
        self.assertEqual(report["prose"][0]["bytes"], len(text.encode("utf-8")))

        # Exceed budget in nested src/sub/AGENTS.md AND trigger >=3 prohibitions warning.
        nested = "\n".join([
            "# Sub Module",
            "- 禁止直接调用底层接口 A，必须走上层入口。",
            "- 不得绕过权限校验 B，否则拒绝合并。",
            "- 不要使用全局状态 C，保持调用无副作用。",
            "- Extra padding line so UTF-8 byte count exceeds 120 bytes easily.",
        ]) + "\n"
        self.write("src/sub/AGENTS.md", nested)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("src/sub/AGENTS.md is" in e and "over its 120-byte prose budget" in e for e in report["errors"]))
        self.assertTrue(any("contains 3 prose prohibitions" in w for w in report["warnings"]))

    def test_feature_map_and_verification_reject_bad_rows_and_fences(self):
        self.write_minimal_guardrails()
        self.write(
            ".guardrails/feature-map.md",
            "\n".join([
                "# Feature Map",
                "| Feature | Entrypoint | Verify CLI | Artifact | Priority |",
                "| --- | --- | --- | --- | --- |",
                "| 导出报表 | `python -m src.app` | `python -m tools.verify` | `artifacts/out.txt` | core |",
                "| 导出报表 | `python -m src.app` | `python -m tools.verify` | `artifacts/out.txt` | invalid_prio |",
            ]),
        )
        self.write(
            ".guardrails/verification.md",
            "\n".join([
                "# Verification",
                "```markdown",
                "| Feature | Command | Observed | Artifact | Commit |",
                "| --- | --- | --- | --- | --- |",
                "| 围栏示例 | `cmd` | 通过 | `missing.txt` | HEAD |",
                "```",
                "| Feature | Command | Observed | Artifact | Commit |",
                "| --- | --- | --- | --- | --- |",
                "| 导出报表 | `cmd` | 通过 | `artifacts/missing.txt` | HEAD |",
                "| 孤儿行 | `cmd` | 返回 0 | `artifacts/empty.txt` | later |",
            ]),
        )
        self.write("artifacts/empty.txt", "")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        errs = report["errors"]
        self.assertFalse(any("围栏示例" in e for e in errs))
        self.assertTrue(any("duplicate feature '导出报表'" in e for e in errs))
        self.assertTrue(any("observed result '通过' is too vague" in e for e in errs))
        self.assertTrue(any("does not exist on disk" in e for e in errs))
        self.assertTrue(any("commit 'HEAD' is a moving ref" in e for e in errs))
        self.assertTrue(any("not listed in feature-map.md" in e for e in errs))
        self.assertTrue(any("is empty (0 bytes)" in e for e in errs))
        self.assertTrue(any("commit anchor is missing" in e for e in errs))

    def test_https_artifact_link_and_l1_missing_core_feature(self):
        self.write_minimal_guardrails(trust_level="L1")
        self.write(
            ".guardrails/feature-map.md",
            "\n".join([
                "| Feature | Entrypoint | Verify CLI | Artifact | Priority |",
                "| --- | --- | --- | --- | --- |",
                "| 导出报表 | `python -m src.app` | `python -m tools.verify` | `https://ci.example/1` | core |",
                "| 并发幂等 | `python -m src.app --replay` | `python -m tools.verify` | `artifacts/out.txt` | core |",
            ]),
        )
        self.write(
            ".guardrails/verification.md",
            "\n".join([
                "| Feature | Command | Observed | Artifact | Commit |",
                "| --- | --- | --- | --- | --- |",
                "| 导出报表 | `python -m tools.verify` | 生成 2 行 CSV 报表 | `https://ci.example/artifacts/1` | v2.0.0 |",
            ]),
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("missing: 并发幂等" in e for e in report["errors"]))
        # First row had valid HTTPS artifact and semver tag, so only missing core errored.
        self.assertEqual(len(report["errors"]), 1, report["errors"])

    def test_check_head_git_freshness_clean_stale_and_dirty(self):
        self.write_minimal_guardrails(trust_level="L3", max_allowed=0, require_fresh_head=True)
        # Before git init, --check-head must fail clearly.
        code, report, _ = self.run_cli("--check-head")
        self.assertEqual(code, 1)
        self.assertTrue(any("requires a git repository" in e for e in report["errors"]))

        def git(*args: str) -> str:
            proc = subprocess.run(
                ["git", "-C", str(self.repo), *args],
                capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
            )
            return proc.stdout.strip()

        git("init")
        git("config", "user.name", "Test")
        git("config", "user.email", "test@example.com")
        git("add", ".")
        git("commit", "-m", "initial commit")
        sha1 = git("rev-parse", "HEAD")

        # Update verification.md to match sha1; guardrails edits should not invalidate source_roots cleanliness.
        self.write(
            ".guardrails/verification.md",
            "\n".join([
                "# Verification",
                "| Feature | Command | Observed | Artifact | Commit |",
                "| --- | --- | --- | --- | --- |",
                f"| 导出报表 | `python -m tools.verify` | 生成 2 行 CSV 输出 | `artifacts/out.txt` | {sha1[:7]} |",
                "",
            ]),
        )
        code, report, _ = self.run_cli("--check-head")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["verification"]["head_sha"], sha1[:12])

        # Uncommitted edit inside source_roots invalidates freshness.
        self.write("src/app.py", "def run():\n    return 2\n")
        code, report, _ = self.run_cli("--check-head")
        self.assertEqual(code, 1)
        self.assertTrue(any("uncommitted changes under source_roots" in e for e in report["errors"]))

        # Committing moves HEAD forward -> recorded commit becomes stale.
        git("add", "src/app.py")
        git("commit", "-m", "change src")
        sha2 = git("rev-parse", "HEAD")
        code, report, _ = self.run_cli("--check-head")
        self.assertEqual(code, 1)
        self.assertTrue(any(
            f"recorded commit '{sha1[:7]}', current HEAD is '{sha2[:7]}'" in e
            for e in report["errors"]
        ))

    def test_run_check_executes_command_pass_and_fail(self):
        self.write_minimal_guardrails(check_command="python -c \"print('all checks green')\"")
        code, report, _ = self.run_cli("--run-check")
        self.assertEqual(code, 0, report["errors"])
        self.assertTrue(report["check_run"]["passed"])

        self.write_minimal_guardrails(check_command="python -c \"import sys; print('boom'); sys.exit(2)\"")
        code, report, _ = self.run_cli("--run-check")
        self.assertEqual(code, 1)
        self.assertFalse(report["check_run"]["passed"])
        self.assertTrue(any("check_command failed (exit 2)" in e and "boom" in e for e in report["errors"]))

    def test_cp1252_console_stdout_does_not_crash(self):
        self.write_minimal_guardrails()
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.repo)],
            cwd=ROOT,
            capture_output=True,
            env={**os.environ, "PYTHONIOENCODING": "cp1252"},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", errors="replace"))

    def write_verify_skill_repo(
        self,
        *,
        trust_level: str = "L1",
        with_verification: bool = True,
        verification_feature_name: str = "create-order",
        include_feature_map: bool = False,
    ) -> None:
        cfg = {
            "guardrails_version": 2,
            "trust_level": trust_level,
            "check_command": "python -c \"print('ok')\"",
            "verify_skill": ".agents/skills/verify-orders",
            "source_roots": ["src"],
            "exclude_dirs": [".git", "__pycache__", ".guardrails"],
            "prose_files": ["AGENTS.md"],
            "prose_max_bytes": 6000,
            "require_fresh_head": False,
            "escape_hatches": {"max_allowed": 0, "extra_patterns": []},
            "forbidden_primitives": [],
            "boundary_rules": [],
        }
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        self.write("src/app.py", "def run():\n    return 1\n")
        self.write("artifacts/create.txt", "order_id=1 status=open\n")
        if include_feature_map:
            self.write(
                ".guardrails/feature-map.md",
                "| Feature | Entrypoint | Verify CLI | Artifact | Priority |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| Legacy | `cmd` | `cmd` | `artifacts/create.txt` | core |\n",
            )
        if with_verification:
            self.write(
                ".guardrails/verification.md",
                "# Verification\n"
                "| Feature | Command | Observed | Artifact | Commit |\n"
                "| --- | --- | --- | --- | --- |\n"
                f"| {verification_feature_name} | `python tools/verify.py` | 创建订单返回 status=open | `artifacts/create.txt` | a1b2c3d |\n",
            )
        self.write(
            ".agents/skills/verify-orders/SKILL.md",
            "---\n"
            "name: verify-orders\n"
            "description: Verify orders CLI\n"
            "---\n\n"
            "# Verify Orders\n\n"
            "## Launch\n\nRun orders CLI in a fresh temporary workspace.\n\n"
            "## Doctor\n\nRun python -m src.orders --help and check exit 0.\n\n"
            "## Drive\n\nExecute tools/control_orders.py for the target feature.\n\n"
            "## Evidence\n\nCapture stdout and store artifact logs under artifacts/.\n\n"
            "## Cleanup\n\nDelete temporary workspace while keeping artifacts/.\n",
        )
        self.write(
            ".agents/skills/verify-orders/features/README.md",
            "# Features\n\n- [Create order](./create-order.md) creates an order.\n",
        )
        self.write(
            ".agents/skills/verify-orders/features/create-order.md",
            "# Create order\n\nCreate order saves a new record.\n\n"
            "## Sub-features\n\n- `create-fresh` creates a new order.\n\n"
            "## How to get to it (user POV)\n\n- Run `orders create` from CLI.\n\n"
            "## Driving it with control_orders.py\n\nPreconditions: doctor ok. Run `control_orders.py create`.\n\n"
            "## Gotchas\n\n- Empty IDs return exit code 1.\n",
        )

    def test_verify_skill_valid_pass_with_slug_alias_and_no_feature_map(self):
        self.write_verify_skill_repo(verification_feature_name="create-order")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["guard_status"], "ready")
        self.assertEqual(report["verification"]["features_total"], 1)
        self.assertEqual(report["verification"]["core_features"], 1)
        self.assertEqual(report["verification"]["verified_features"], 1)
        self.assertEqual(report["verify_skill"]["name"], "verify-orders")

    def test_verify_skill_missing_required_sections_fails(self):
        self.write_verify_skill_repo()
        self.write(
            ".agents/skills/verify-orders/SKILL.md",
            "---\nname: verify-orders\ndescription: Verify orders\n---\n\n"
            "## Launch\n\nRun CLI in temp dir.\n\n"
            "## Drive\n\nExecute tools/control_orders.py.\n\n"
            "## Evidence\n\nSave artifacts/create.txt.\n",
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("missing required section 'Doctor'" in e for e in report["errors"]))
        self.assertTrue(any("missing required section 'Cleanup'" in e for e in report["errors"]))

    def test_verify_skill_index_hygiene_catches_unindexed_and_dead_links(self):
        self.write_verify_skill_repo()
        self.write(
            ".agents/skills/verify-orders/features/README.md",
            "# Features\n\n- [Ghost](./missing-feature.md)\n",
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("broken link to missing feature file 'missing-feature.md'" in e for e in report["errors"]))
        self.assertTrue(any("unindexed feature file 'create-order.md'" in e for e in report["errors"]))

    def test_verify_skill_feature_file_out_of_order_or_missing_h2_fails(self):
        self.write_verify_skill_repo()
        self.write(
            ".agents/skills/verify-orders/features/create-order.md",
            "# Create order\n\n"
            "## Gotchas\n\n- Empty IDs return exit code 1.\n\n"
            "## Sub-features\n\n- `create-fresh` creates a new order.\n\n"
            "## How to get to it (user POV)\n\n- Run `orders create` from CLI.\n\n"
            "## Driving it with control_orders.py\n\nPreconditions: doctor ok. Run `control_orders.py create`.\n",
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("required H2 sections are out of order" in e for e in report["errors"]))

        self.write(
            ".agents/skills/verify-orders/features/create-order.md",
            "# Create order\n\n## Sub-features\n\n- `create-fresh` creates an order.\n",
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("missing required H2 section starting with 'gotchas'" in e for e in report["errors"]))

    def test_dual_feature_map_warns_when_verify_skill_also_configured(self):
        self.write_verify_skill_repo(include_feature_map=True)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        self.assertTrue(any("both verify_skill and .guardrails/feature-map.md exist" in w for w in report["warnings"]))

    def test_l0_optional_verification_md_vs_l1_required(self):
        self.write_verify_skill_repo(trust_level="L0", with_verification=False)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        self.assertTrue(any("optional at L0" in w for w in report["warnings"]))

        self.write_verify_skill_repo(trust_level="L1", with_verification=False)
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("missing .guardrails/verification.md" in e for e in report["errors"]))

    def test_anti_patterns_default_always_on_catches_silent_catch_blind_wait_paths_secrets(self):
        self.write_minimal_guardrails(trust_level="L1")
        self.write(
            "src/bad.py",
            "def f():\n"
            "    try:\n"
            "        work()\n"
            "    except Exception: pass\n\n"
            "def g():\n"
            "    try:\n"
            "        work()\n"
            "    except KeyError:\n"
            "        return []\n\n"
            "def ok_catch():\n"
            "    try:\n"
            "        work()\n"
            "    except ValueError as err:\n"
            "        log(err)\n"
            "        return None\n\n"
            "# C:\\Users\\comment_only\\ignored\n"
            "LOCAL = r'C:\\Users\\alice\\data.db'\n"
            "UNIX_HOME = '/Users/bob/app.sqlite'\n"
            "TOKEN = 'sk-proj-1234567890abcdefghijklmno'\n"
            "async def drive(page):\n"
            "    await page.wait_for_timeout(1500)\n",
        )
        self.write(
            "src/view.ts",
            "export async function load() {\n"
            "  try { await fetchIt(); } catch (e) {}\n"
            "  try { await fetchIt(); } catch {\n"
            "    return null;\n"
            "  }\n"
            "  try { await fetchIt(); } catch (err) { log(err); return null; }\n"
            "  await new Promise(resolve => setTimeout(resolve, 1500));\n"
            "}\n",
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertFalse(report["anti_patterns_config"]["configured"])
        # bad.py: 2 silent-catch + 2 hardcoded-path + 1 hardcoded-secret + 1 blind-wait = 6
        # view.ts: 2 silent-catch + 1 blind-wait = 3 (total = 9; ok_catch and logged catch not flagged)
        self.assertEqual(report["scan"]["anti_patterns"], 9, report["errors"])
        err_blob = "\n".join(report["errors"])
        self.assertIn("anti-patterns found (9) exceed ratchet max_allowed (0)", err_blob)
        self.assertIn("silent-catch", err_blob)
        self.assertIn("blind-wait", err_blob)
        self.assertIn("hardcoded-path", err_blob)
        self.assertIn("hardcoded-secret", err_blob)

    def test_anti_patterns_explicit_config_ratchet_whitelists_and_extra_rules(self):
        self.write_minimal_guardrails(trust_level="L1")
        cfg = json.loads((self.repo / ".guardrails" / "config.json").read_text(encoding="utf-8"))
        cfg["anti_patterns"] = {
            "max_allowed": 2,
            "enabled": [
                "silent-catch",
                "blind-wait",
                "hardcoded-path",
                "hardcoded-localhost",
                "hardcoded-secret",
            ],
            "allow_paths": ["src/allowed"],
            "allow_by_category": {"hardcoded-localhost": ["src/config"]},
            "extra_rules": [
                {
                    "id": "no-hardcoded-inception",
                    "pattern": r"2026-06-14",
                    "globs": ["src/**/*.py"],
                    "allow_paths": ["src/config"],
                    "message": "起算日必须从配置中心读取，禁止在业务代码中写死业务日期常量。",
                }
            ],
        }
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        self.write("src/allowed/helper.py", "import time\ntime.sleep(1.5)\n")
        self.write("src/config/defaults.py", "API = 'http://localhost:8000'\nINCEPTION = '2026-06-14'\n")
        self.write("src/ui/page.ts", "setTimeout(() => show(), 0);\nsetTimeout(() => show(), 1500);\n")
        self.write("src/service.py", "import asyncio\nURL = 'http://127.0.0.1:9000'\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        # page.ts line 2 (1500ms) + service.py 127.0.0.1 = 2; allowed & config whitelisted; setTimeout(..., 0) ignored
        self.assertEqual(report["scan"]["anti_patterns"], 2)

        # Drop hits below max_allowed -> ratchet-down warning
        self.write("src/ui/page.ts", "setTimeout(() => show(), 0);\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        self.assertTrue(any("lower anti_patterns.max_allowed to 1" in w for w in report["warnings"]))

        # Hit extra_rule & exceed ratchet at L2
        self.write("src/service.py", "DATE = '2026-06-14'\n")
        cfg["trust_level"] = "L2"
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        err_blob = "\n".join(report["errors"])
        self.assertIn("L2 requires anti_patterns.max_allowed == 0", err_blob)
        self.assertIn("anti_pattern_rule 'no-hardcoded-inception' at src/service.py:1", err_blob)

    def test_anti_patterns_invalid_category_rejected(self):
        self.write_minimal_guardrails(trust_level="L1")
        cfg = json.loads((self.repo / ".guardrails" / "config.json").read_text(encoding="utf-8"))
        cfg["anti_patterns"] = {"enabled": ["bogus-category"]}
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("unknown anti_patterns category 'bogus-category'" in e for e in report["errors"]))

    def test_anti_patterns_v22_blind_spots_and_mock_in_prod(self):
        self.write_minimal_guardrails(trust_level="L1")
        cfg = json.loads((self.repo / ".guardrails" / "config.json").read_text(encoding="utf-8"))
        cfg["source_roots"] = ["src", "tests"]
        cfg["anti_patterns"] = {
            "max_allowed": 50,
            "enabled": [
                "silent-catch",
                "blind-wait",
                "hardcoded-path",
                "hardcoded-localhost",
                "hardcoded-secret",
                "mock-in-prod",
            ],
            "allow_paths": [],
            "allow_by_category": {},
            "extra_rules": [],
        }
        # Re-test at max_allowed=0 after collecting exact violation list.
        cfg["anti_patterns"]["max_allowed"] = 0
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        self.write(
            "src/py_blind_spots.py",
            "from contextlib import suppress as hide\n"
            "import contextlib\n"
            "def multi_except():\n"
            "    try:\n        risky()\n"
            "    except (\n        KeyError,\n        ValueError,\n    ):\n"
            "        pass\n"
            "with contextlib.suppress(Exception):\n    risky()\n"
            "with hide(BaseException):\n    risky()\n"
            "with contextlib.suppress(FileNotFoundError):\n    cleanup()\n"
            "async def spin(proc):\n"
            "    await sleep(1500)\n"
            "    await proc.wait(5)\n"
            "    await sleep(0)\n"
            "WSL = '/mnt/c/Users/alice/db.sqlite'\n"
            "ROOT_PATH = '/root/config.json'\n"
            "FILE_URI = 'file:///C:/Users/alice/config.json'\n"
            "DB_URL = 'postgresql://user:pw@127.0.0.1:5432/db'\n"
            "LAN_URL = 'http://192.168.1.50:8080/api'\n"
            "IPV6_URL = 'http://[::1]:3000/api'\n"
            "HOST_OK = 'https://localhost.example.test'\n"
            "GKEY = 'AIza" + "SyD-1234567890abcdefghijklmnopqr123'\n"
            "SLACK = 'xoxb-" + "1234567890-abcdefghij123456'\n",
        )
        self.write(
            "src/service.ts",
            "import { items } from '../__mocks__/items';\n"
            "export const MOCK_USERS = [{ id: 1 }];\n"
            "const minLoadingMs = 1500;\n"
            "const safeLoading = 0;\n"
            "const minLoadingMsZero = 0;\n"
            "const AFTER_SYNC_REFRESH_MS: number = 1500;\n"
            "const routePath = '/home/settings/profile';\n"
            "const mockMode = false;\n"
            "const flag = safeLoading || mockMode;\n"
            "const quoted = '.catch(() => {})';\n"
            "export async function run(p: Promise<any>, rows: any[]) {\n"
            "  await p.catch(() => {});\n"
            "  await p.catch(async () => {});\n"
            "  await p.catch(function() {});\n"
            "  await p.then(() => 1, () => null);\n"
            "  try { await p; } catch (e) { /* } */ throw e; }\n"
            "  await p.catch(err => { log(err); return null; });\n"
            "  await delay(300);\n"
            "  delay(1500);\n"
            "  const ws = 'ws://localhost:3000';\n"
            "  return rows || mockOrdersData;\n"
            "}\n",
        )
        # First-party dirs named 'test_*' in TS or 'build/' in src/ must NOT be exempted.
        self.write("src/test_pipeline.ts", "try { work(); } catch (e) {}\n")
        self.write("src/build/release.py", "def build():\n    try:\n        step()\n    except Exception:\n        pass\n")
        # Test/fixture files exempt from noise categories, EXCEPT hardcoded-secret remains enforced!
        self.write(
            "src/__tests__/service.test.ts",
            "import { items } from '../__mocks__/items';\n"
            "export const MOCK_USERS = [{ id: 1 }];\n"
            "const SAFE_HTTP = 'http://localhost:3000';\n",
        )
        self.write(
            "tests/fixtures.py",
            "MOCK_ROWS = [{'id': 1}]\n"
            "LEAKED = 'sk-" + "proj-1234567890abcdefghijklmnop'\n",
        )
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        err_blob = "\n".join(report["errors"])
        # Expected hits:
        # py_blind_spots.py: 1 multi_except + 2 suppress + 1 await sleep + 3 path + 3 localhost + 2 secret = 12
        # service.ts: 1 import + 1 MOCK_USERS + 1 minLoadingMs + 1 AFTER_SYNC_REFRESH_MS + 4 catch/then + 1 await delay + 1 delay + 1 ws + 1 fallback = 12
        # test_pipeline.ts: 1, build/release.py: 1, tests/fixtures.py: 1 secret
        # Total = 27
        self.assertEqual(report["scan"]["anti_patterns"], 27, err_blob)
        for token in (
            "src/build/release.py:4[silent-catch]",
            "src/py_blind_spots.py:6[silent-catch]",
            "src/py_blind_spots.py:11[silent-catch]",
            "src/py_blind_spots.py:13[silent-catch]",
            "src/py_blind_spots.py:18[blind-wait]",
            "src/py_blind_spots.py:21[hardcoded-path]",
            "src/py_blind_spots.py:22[hardcoded-path]",
            "src/py_blind_spots.py:23[hardcoded-path]",
        ):
            self.assertIn(token, err_blob)
        self.assertNotIn("service.test.ts", err_blob)
        self.assertNotIn("HOST_OK", err_blob)

        # Verify negative controls alone yield 0 hits, and individual blind spots / edge cases each hit at exact lines.
        self.write(
            "src/py_blind_spots.py",
            "import contextlib\n"
            "with contextlib.suppress(FileNotFoundError):\n    pass\n"
            "async def spin(proc):\n    await proc.wait(5)\n    await sleep(0)\n"
            "HOST_OK = 'https://localhost.example.test'\n",
        )
        self.write(
            "src/service.ts",
            "const minLoadingMsZero = 0;\n"
            "const routePath = '/home/settings/profile';\n"
            "const newsRoute = '/home/news/latest';\n"
            "const mockMode = false;\n"
            "const flag = routePath || newsRoute || mockMode;\n"
            "const quoted = '.catch(() => {})';\n"
            "export async function run(p: Promise<any>) {\n"
            "  try { await p; } catch (e) { /* } */ throw e; }\n"
            "  await p.catch(err => { log(err); return null; });\n"
            "}\n",
        )
        self.write("src/__tests__/service.test.ts", "const SAFE_HTTP = 'http://localhost:3000';\n")
        self.write("tests/fixtures.py", "MOCK_ROWS = [{'id': 1}]\n")
        self.write("src/test_pipeline.ts", "export const ok = 1;\n")
        self.write("src/build/release.py", "ok = 1\n")
        code_ok, rep_ok, _ = self.run_cli()
        self.assertEqual(code_ok, 0, rep_ok["errors"])
        self.assertEqual(rep_ok["scan"]["anti_patterns"], 0)

        # Prove exact per-line detections across Python IPv6 & /home/<user>, TS mockData & catch variants, and exempt-exemptions.
        for rel_p, bad_src, expected_locs in (
            (
                "src/py_blind_spots.py",
                "IPV6_URL = 'http://[::1]:3000/api'\n"
                "LIN_HOME = '/home/alice/config.json'\n",
                (
                    "src/py_blind_spots.py:1[hardcoded-localhost]",
                    "src/py_blind_spots.py:2[hardcoded-path]",
                ),
            ),
            (
                "src/service.ts",
                "const AFTER_SYNC_REFRESH_MS: number = 1500;\n"
                "const mockData = [];\n"
                "async function f(p: Promise<any>, rows: any[]) {\n"
                "  await p.catch(async () => {});\n"
                "  await p.catch(function() {});\n"
                "  await p.then(() => 1, () => null);\n"
                "  return rows || mockData;\n"
                "}\n",
                (
                    "src/service.ts:1[blind-wait]",
                    "src/service.ts:2[mock-in-prod]",
                    "src/service.ts:4[silent-catch]",
                    "src/service.ts:5[silent-catch]",
                    "src/service.ts:6[silent-catch]",
                    "src/service.ts:7[mock-in-prod]",
                ),
            ),
            ("src/test_pipeline.ts", "try { x(); } catch (e) {}\n", ("src/test_pipeline.ts:1[silent-catch]",)),
            ("src/build/release.py", "try:\n    x()\nexcept Exception:\n    pass\n", ("src/build/release.py:3[silent-catch]",)),
            ("tests/fixtures.py", "LEAK = 'sk-" + "proj-1234567890abcdefghijklmnop'\n", ("tests/fixtures.py:1[hardcoded-secret]",)),
        ):
            self.write(rel_p, bad_src)
            c, r, _ = self.run_cli()
            self.assertEqual(c, 1, rel_p)
            blobs = "\n".join(r["errors"])
            for loc in expected_locs:
                self.assertIn(loc, blobs)
            self.write(rel_p, "ok = 1\n")

    def test_file_limits_guardrail_ratchet_allow_paths_and_outer_loop_block(self):
        self.write_minimal_guardrails(trust_level="L1")
        cfg = json.loads((self.repo / ".guardrails" / "config.json").read_text(encoding="utf-8"))
        cfg["file_limits"] = {"max_lines": 5, "max_allowed": 1, "allow_paths": ["src/generated"]}
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        self.write("src/generated/types.py", "\n".join(f"LINE_{i} = {i}" for i in range(8)) + "\n")
        self.write("src/legacy_big.py", "\n".join(f"X_{i} = {i}" for i in range(6)) + "\n")

        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        self.assertTrue(report["file_limits_config"]["configured"])
        self.assertEqual(report["scan"]["oversize_files"], 1)

        # Adding a second oversize file exceeds max_allowed (1).
        self.write("src/another_big.py", "\n".join(f"Y_{i} = {i}" for i in range(6)) + "\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("oversize files found (2) exceed file_limits.max_allowed (1)", "\n".join(report["errors"]))

        # Splitting files below max_allowed triggers ratchet-down warning.
        self.write("src/legacy_big.py", "X_0 = 0\n")
        self.write("src/another_big.py", "Y_0 = 0\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 0, report["errors"])
        self.assertTrue(any("lower file_limits.max_allowed to 0" in w for w in report["warnings"]))

        # L2/L3 reject file_limits.max_allowed > 0.
        cfg["trust_level"] = "L2"
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertTrue(any("L2 requires file_limits.max_allowed == 0" in e for e in report["errors"]))

    def test_scan_detects_node_and_python_stacks_without_touching_disk(self):
        # 1. Node repo with lint + vitest, filtering "no test specified" separately.
        self.write(
            "package.json",
            json.dumps({
                "name": "demo",
                "scripts": {"lint": "eslint .", "test": "vitest"},
            }),
        )
        self.write("pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
        self.write("tsconfig.json", "{}\n")
        self.write("src/index.ts", "export const x = 1; // @ts-ignore\nawait sleep(1500);\n")
        self.write("src/big.ts", "\n".join(f"export const v{i} = {i};" for i in range(12)) + "\n")
        code, report, _ = self.run_cli("--scan", "--max-lines", "10")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["guard_status"], "baseline_scan")
        self.assertFalse((self.repo / ".guardrails").exists())
        self.assertEqual(report["detected"]["stacks"], ["node", "typescript"])
        self.assertEqual(report["detected"]["check_command"], "pnpm run lint && pnpm exec vitest run")
        self.assertEqual(report["baseline"]["escape_hatches"], 1)
        self.assertEqual(report["baseline"]["anti_patterns"], 1)
        self.assertEqual(report["baseline"]["oversize_files"], 1)

        # Verify npm default placeholder "no test specified" is ignored.
        self.setUp()
        self.write(
            "package.json",
            json.dumps({
                "name": "npm-placeholder",
                "scripts": {"test": 'echo "Error: no test specified" && exit 1'},
            }),
        )
        self.write("src/app.js", "export const ok = 1;\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0)
        self.assertEqual(report["detected"]["check_command"], "")
        self.assertTrue(any("no check_command auto-detected" in w for w in report["warnings"]))

        # 2. Python repo with pyproject pytest.
        self.setUp()
        self.write("pyproject.toml", "[tool.pytest.ini_options]\ntestpaths = ['tests']\n")
        self.write("app/main.py", "def ok():\n    return 1\n")
        self.write("tests/test_main.py", "def test_ok():\n    assert True\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0)
        self.assertEqual(report["detected"]["stacks"], ["python"])
        self.assertEqual(report["detected"]["source_roots"], ["app"])
        self.assertEqual(report["detected"]["check_command"], "python -X utf8 -m pytest")

    def test_init_bootstraps_l0_and_refuses_existing_or_legacy_state(self):
        self.write("tests/test_ok.py", "import unittest\nclass T(unittest.TestCase):\n    def test_1(self): pass\n")
        self.write(
            "src/legacy.py",
            "x = 1  # noqa\n"
            "def f():\n    try:\n        pass\n    except Exception: pass\n",
        )
        code, report, _ = self.run_cli("--init", "--max-lines", "500")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["guard_status"], "ready")
        self.assertEqual(report["trust_level"], "L0")
        self.assertEqual(report["max_escape_hatches"], 1)
        self.assertEqual(report["anti_patterns_config"]["max_allowed"], 1)
        self.assertEqual(report["file_limits_config"]["max_lines"], 500)
        self.assertTrue((self.repo / ".guardrails" / "config.json").is_file())
        self.assertTrue((self.repo / ".guardrails" / "feature-map.md").is_file())
        self.assertTrue(any("has no feature rows yet" in w for w in report["warnings"]))

        # Re-running repo_guard without --init immediately passes at L0.
        code2, report2, _ = self.run_cli()
        self.assertEqual(code2, 0, report2["errors"])
        self.assertEqual(report2["guard_status"], "ready")

        # Refuses --init when .guardrails/ already exists.
        code3, report3, _ = self.run_cli("--init")
        self.assertEqual(code3, 1)
        self.assertTrue(any("cannot --init: .guardrails/ already exists" in e for e in report3["errors"]))

        # Refuses --init when legacy_v1 exists without overwriting.
        self.setUp()
        self.write("docs/workflow/project.md", "# v1\n")
        code4, report4, _ = self.run_cli("--init")
        self.assertEqual(code4, 1)
        self.assertTrue(any("legacy v1 state detected" in e for e in report4["errors"]))
        self.assertFalse((self.repo / ".guardrails").exists())

    def test_fullstack_monorepo_scan_and_noise_exclusions(self):
        # Backend (Python + uv + pytest) with asyncio.sleep(0) exempt, AFTER_SYNC_REFRESH_MS flagged,
        # plus .env, debug.log, and .ruff_cache/ excluded INSIDE scanned backend/app/.
        self.write("backend/pyproject.toml", "[tool.pytest.ini_options]\ntestpaths = ['tests']\n")
        self.write("backend/uv.lock", "version = 1\n")
        self.write(
            "backend/app/main.py",
            "import asyncio\n"
            "AFTER_SYNC_REFRESH_MS = 1500\n"
            "async def spin():\n"
            "    await asyncio.sleep(0)\n",
        )
        self.write("backend/app/.env", "OPENAI_API_KEY=sk-" + "proj-1234567890abcdefghijklmnop\n")
        self.write("backend/app/debug.log", "listening on http://localhost:8000\n")
        self.write("backend/app/.ruff_cache/cached.py", "def f():\n    try:\n        pass\n    except Exception: pass\n")
        self.write("backend/tests/test_api.py", "URL = 'http://127.0.0.1:8000'\n")

        # Frontend (Node + pnpm check) with co-located test exempt, large CSS exempt, monolith TSX flagged.
        self.write(
            "frontend/package.json",
            json.dumps({"name": "web", "scripts": {"check": "pnpm lint && pnpm test"}}),
        )
        self.write("frontend/pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
        self.write("frontend/src/App.tsx", "export const App = () => null;\n")
        self.write(
            "frontend/src/App.test.tsx",
            "const URL = 'http://localhost:3000';\n"
            "setTimeout(() => {}, 50);\n",
        )
        self.write("frontend/src/styles.css", "\n".join(f".c{i} {{ color: red; }}" for i in range(20)) + "\n")
        self.write("frontend/src/GodPage.tsx", "\n".join(f"export const x{i} = {i};" for i in range(15)) + "\n")

        code, report, _ = self.run_cli("--scan", "--max-lines", "10")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["detected"]["stacks"], ["python", "node"])
        self.assertEqual(report["detected"]["source_roots"], ["backend/app", "frontend/src"])
        self.assertEqual(
            report["detected"]["check_command"],
            "uv --directory backend run pytest && pnpm --dir frontend run check",
        )
        self.assertEqual(report["baseline"]["escape_hatches"], 0)
        self.assertEqual(report["baseline"]["anti_patterns"], 1, report["baseline"])
        self.assertEqual(report["baseline"]["oversize_files"], 1, report["baseline"])
        self.assertEqual(report["baseline"]["oversize_samples"], ["frontend/src/GodPage.tsx:15"])

    def test_package_manager_commands_cwd_and_multistack_non_displacement(self):
        # 1. Bun: empty scripts + tsconfig -> `bunx tsc --noEmit`; explicit `typecheck` -> `bun run typecheck`;
        #    nested check -> `bun run --cwd frontend check`; nested vitest -> `bun run --cwd frontend vitest run`.
        self.write("package.json", json.dumps({"name": "root", "scripts": {}}))
        self.write("bun.lock", "")
        self.write("tsconfig.json", "{}\n")
        self.write("src/index.ts", "export const ok = 1;\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["detected"]["check_command"], "bunx tsc --noEmit")

        self.write("package.json", json.dumps({"name": "root", "scripts": {"typecheck": "tsc --noEmit"}}))
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["detected"]["check_command"], "bun run typecheck")

        self.setUp()
        self.write("frontend/package.json", json.dumps({"name": "web", "scripts": {"check": "vite build"}}))
        self.write("frontend/bun.lockb", "")
        self.write("frontend/src/App.tsx", "export const App = 1;\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["detected"]["check_command"], "bun run --cwd frontend check")

        self.setUp()
        self.write("frontend/package.json", json.dumps({"name": "web", "scripts": {"test": "vitest"}}))
        self.write("frontend/bun.lock", "")
        self.write("frontend/src/App.tsx", "export const App = 1;\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["detected"]["check_command"], "bun run --cwd frontend vitest run")

        # 2. Nearest lockfile wins: nested apps/web/package-lock.json overrides root pnpm-lock.yaml,
        #    and root uv.lock applies to root and packages/svc unless packages/svc has its own uv.lock.
        self.setUp()
        self.write("pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
        self.write("uv.lock", "version = 1\n")
        self.write("pyproject.toml", "[tool.pytest.ini_options]\ntestpaths = ['tests']\n")
        self.write("apps/web/package.json", json.dumps({"name": "web", "scripts": {"test": "vitest"}}))
        self.write("apps/web/package-lock.json", "{}\n")
        self.write("apps/web/src/page.tsx", "export const p = 1;\n")
        self.write("packages/svc/pyproject.toml", "[tool.pytest.ini_options]\n")
        self.write("packages/svc/app/core.py", "x = 1\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0, report["errors"])
        self.assertIn("apps/web/src", report["detected"]["source_roots"])
        self.assertIn("packages/svc/app", report["detected"]["source_roots"])
        self.assertEqual(
            report["detected"]["check_command"],
            "uv run pytest && npm --prefix apps/web run test -- --run && uv run pytest packages/svc",
        )

        # 2b. Workspace root pyproject without pytest/tests must NOT invent `python -m unittest`,
        #     and repo_guard keeps discovered child checks explicit instead of guessing root coverage.
        self.setUp()
        self.write("pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
        self.write("package.json", json.dumps({"name": "ws", "scripts": {"check": "pnpm -r run check"}}))
        self.write("pyproject.toml", "[tool.uv.workspace]\nmembers = ['packages/*']\n")
        self.write("uv.lock", "version = 1\n")
        self.write("apps/web/package.json", json.dumps({"name": "web", "scripts": {"check": "tsc --noEmit"}}))
        self.write("apps/web/src/index.ts", "export const ok = 1;\n")
        self.write("packages/svc/pyproject.toml", "[tool.pytest.ini_options]\n")
        self.write("packages/svc/app/core.py", "x = 1\n")
        ws_code, ws_rep, _ = self.run_cli("--scan")
        self.assertEqual(ws_code, 0, ws_rep["errors"])
        self.assertEqual(
            ws_rep["detected"]["check_command"],
            "pnpm run check && pnpm --dir apps/web run check && uv run pytest packages/svc",
        )

        # 2c. Co-located Node + Python manifests in the same directory compose BOTH check commands.
        self.setUp()
        self.write("package.json", json.dumps({"name": "co", "scripts": {"check": "node -e \"process.exit(0)\""}}))
        self.write("src/app.js", "export const ok = 1;\n")
        self.write("tests/test_py.py", "import unittest\nclass T(unittest.TestCase):\n    def test_f(self): pass\n")
        co_code, co_rep, _ = self.run_cli("--scan")
        self.assertEqual(co_code, 0, co_rep["errors"])
        self.assertEqual(co_rep["detected"]["stacks"], ["node", "python"])
        self.assertIn("npm run check", co_rep["detected"]["check_command"])
        self.assertIn("unittest discover", co_rep["detected"]["check_command"])

        # 2d. Manifestless workspace sibling (apps/shared) stays in source_roots beside apps/ui.
        self.setUp()
        self.write("apps/ui/package.json", json.dumps({"name": "ui", "scripts": {"check": "vitest run"}}))
        self.write("apps/ui/src/a.ts", "export const a = 1;\n")
        self.write("apps/shared/src/tool.ts", "try { x(); } catch (e) {}\n")
        sh_code, sh_rep, _ = self.run_cli("--scan")
        self.assertEqual(sh_code, 0, sh_rep["errors"])
        self.assertIn("apps/ui/src", sh_rep["detected"]["source_roots"])
        self.assertIn("apps/shared/src", sh_rep["detected"]["source_roots"])
        self.assertEqual(sh_rep["baseline"]["anti_patterns"], 1)
        self.assertEqual(sh_rep["baseline"]["anti_pattern_samples"], ["apps/shared/src/tool.ts:1[silent-catch]"])

        # 3. Root check must NOT displace sub-stack checks (Node root + Python backend),
        #    and --run-check must fail with exact exit status when check command fails.
        self.setUp()
        self.write("package.json", json.dumps({"name": "root", "scripts": {"check": "node -e \"process.exit(0)\""}}))
        self.write("pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
        self.write("src/index.js", "export const ok = 1;\n")
        self.write("backend/pytest.ini", "[pytest]\n")
        self.write("backend/app/api.py", "def ok():\n    return 1\n")
        self.write("backend/tests/test_fail.py", "def test_fail():\n    assert False\n")
        scan_code, scan_rep, _ = self.run_cli("--scan")
        self.assertEqual(scan_code, 0)
        self.assertIn("pnpm run check", scan_rep["detected"]["check_command"])
        self.assertIn("pytest", scan_rep["detected"]["check_command"])

        self.write_minimal_guardrails(
            trust_level="L1",
            check_command='python -X utf8 -c "import sys; sys.exit(0)" && python -X utf8 -c "import sys; sys.exit(7)"',
        )
        run_code, run_rep, _ = self.run_cli("--run-check")
        self.assertEqual(run_code, 1)
        self.assertFalse(run_rep["check_run"]["passed"])
        self.assertEqual(run_rep["check_run"]["returncode"], 7)

        # 4. Nested tsconfig-only fallback uses package-scoped commands without npx squat/CWD mismatch.
        for lockfile, expected_tsc in (
            ("frontend/bun.lock", "bun run --cwd frontend tsc --noEmit"),
            ("frontend/pnpm-lock.yaml", "pnpm --dir frontend exec tsc --noEmit"),
            ("frontend/yarn.lock", "yarn --cwd frontend tsc --noEmit"),
            ("frontend/package-lock.json", "npm --prefix frontend exec --no -- tsc -p frontend/tsconfig.json --noEmit"),
        ):
            self.setUp()
            self.write("frontend/package.json", json.dumps({"name": "web", "scripts": {}}))
            self.write("frontend/tsconfig.json", "{}\n")
            self.write(lockfile, "{}\n")
            self.write("frontend/src/App.tsx", "export const ok = 1;\n")
            tsc_code, tsc_rep, _ = self.run_cli("--scan")
            self.assertEqual(tsc_code, 0, tsc_rep["errors"])
            self.assertEqual(tsc_rep["detected"]["check_command"], expected_tsc, lockfile)

        # 5. Real subprocess verification across installed package managers: failing script cannot false-green,
        #    and script CWD actually resolves to `frontend`.
        if shutil.which("node"):
            for pm, lockfile in (
                ("npm", "package-lock.json"),
                ("pnpm", "pnpm-lock.yaml"),
                ("bun", "bun.lock"),
            ):
                if not shutil.which(pm):
                    continue
                self.setUp()
                self.write("frontend/package.json", json.dumps({"name": "web", "scripts": {"check": "node check_cwd.mjs"}}))
                self.write(f"frontend/{lockfile}", "{}\n")
                self.write("frontend/src/index.js", "export const ok = 1;\n")
                self.write("frontend/check_cwd.mjs", "process.exit(7);\n")
                c_fail, r_fail, _ = self.run_cli("--init", "--run-check")
                self.assertEqual(c_fail, 1, pm)
                self.assertFalse(r_fail["check_run"]["passed"], pm)

                self.write(
                    "frontend/check_cwd.mjs",
                    'import path from "node:path";\n'
                    'process.exit(path.basename(process.cwd()) === "frontend" ? 0 : 9);\n',
                )
                c_ok, r_ok, _ = self.run_cli("--run-check")
                self.assertEqual(c_ok, 0, (pm, r_ok["errors"]))
                self.assertTrue(r_ok["check_run"]["passed"], pm)

    def test_missing_or_empty_source_roots_and_manifest_script_discovery(self):
        # 1. Nonexistent source_root fails loudly instead of silently passing.
        self.write_minimal_guardrails(trust_level="L1")
        cfg = json.loads((self.repo / ".guardrails" / "config.json").read_text(encoding="utf-8"))
        cfg["source_roots"] = ["src", "missing_dir"]
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertIn("configured source_root does not exist: missing_dir", "\n".join(report["errors"]))

        # 2. Existing empty source_root (or only .gitkeep / NUL binary) fails loudly.
        (self.repo / "empty_dir").mkdir(parents=True, exist_ok=True)
        self.write("empty_dir/.gitkeep", "")
        (self.repo / "empty_dir" / "blob.bin").write_bytes(b"\x00\x01\x02\x03")
        cfg["source_roots"] = ["empty_dir"]
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        code, report, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(report["scan"]["files_scanned"], 0)
        self.assertIn("source_roots matched 0 source files", "\n".join(report["errors"]))

        # 3. Root package.json scripts referencing scripts/ pulls scripts into source_roots.
        self.setUp()
        self.write(
            "package.json",
            json.dumps({
                "name": "console",
                "scripts": {"check": "tsc --noEmit", "backfill": "node scripts/backfill.mjs"},
            }),
        )
        self.write("src/app.ts", "export const ok = 1;\n")
        self.write("scripts/backfill.mjs", "await new Promise(r => setTimeout(r, 1500));\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["detected"]["source_roots"], ["src", "scripts"])
        self.assertEqual(report["baseline"]["anti_patterns"], 1)
        self.assertEqual(report["baseline"]["anti_pattern_samples"], ["scripts/backfill.mjs:1[blind-wait]"])

        # 4. Unreferenced scripts/ directory emits an explicit unscanned warning.
        self.setUp()
        self.write("package.json", json.dumps({"name": "app", "scripts": {"check": "tsc --noEmit"}}))
        self.write("src/app.ts", "export const ok = 1;\n")
        self.write("scripts/job.py", "x = 1\n")
        code, report, _ = self.run_cli("--scan")
        self.assertEqual(code, 0, report["errors"])
        self.assertEqual(report["detected"]["source_roots"], ["src"])
        self.assertTrue(any("unscanned code directory 'scripts' found" in w for w in report["warnings"]))

    def test_init_prevalidates_check_command_atomically(self):
        # 1. When no check_command can be detected and none is passed, --init fails BEFORE writing .guardrails/.
        self.write("src/app.js", "export const x = 1;\n")
        code1, rep1, _ = self.run_cli("--init")
        self.assertEqual(code1, 1)
        self.assertIn('cannot --init without a runnable check_command', "\n".join(rep1["errors"]))
        self.assertFalse((self.repo / ".guardrails").exists())

        # Immediate retry with --check-command succeeds cleanly without leftover .guardrails/.
        code2, rep2, _ = self.run_cli("--init", "--check-command", 'python -X utf8 -c "print(1)"')
        self.assertEqual(code2, 0, rep2["errors"])
        self.assertTrue((self.repo / ".guardrails" / "config.json").is_file())

        # 2. Empty src/ (valid check command but 0 readable files) also fails BEFORE creating .guardrails/.
        self.setUp()
        (self.repo / "src").mkdir(parents=True, exist_ok=True)
        (self.repo / "src" / "bin.dat").write_bytes(b"\x00\x01")
        c_empty, rep_empty, _ = self.run_cli("--init", "--check-command", 'python -X utf8 -c "print(1)"')
        self.assertEqual(c_empty, 1)
        self.assertIn("matched 0 readable source files", "\n".join(rep_empty["errors"]))
        self.assertFalse((self.repo / ".guardrails").exists())

        # Adding readable code and retrying --init succeeds immediately.
        self.write("src/app.js", "export const ok = 1;\n")
        c_retry, rep_retry, _ = self.run_cli("--init", "--check-command", 'python -X utf8 -c "print(1)"')
        self.assertEqual(c_retry, 0, rep_retry["errors"])
        self.assertTrue((self.repo / ".guardrails" / "config.json").is_file())

        # 3. Flat repo with tests/ keeps allow_paths=[] so hardcoded-secret in tests/ stays active.
        self.setUp()
        self.write("pyproject.toml", "[tool.pytest.ini_options]\ntestpaths = ['tests']\n")
        self.write("main.py", "x = 1\n")
        self.write("tests/test_key.py", "KEY = 'sk-" + "proj-1234567890abcdefghijklmnop'\n")
        c_flat, rep_flat, _ = self.run_cli("--init")
        self.assertEqual(c_flat, 0, rep_flat["errors"])
        self.assertEqual(rep_flat["detected"]["allow_paths"], [])
        self.assertEqual(rep_flat["anti_patterns_config"]["max_allowed"], 1)

        # 4. --init --check-head is rejected upfront by CLI parser.
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(self.repo), "--init", "--check-head"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--init cannot be combined with --check-head", proc.stderr)

    def test_file_limits_baseline_files_ratchet_and_extensions(self):
        # --init populates baseline_files with existing oversize code files (.mts/.cts included, .css excluded).
        self.write("src/big.mts", "\n".join(f"export const a{i} = {i};" for i in range(8)) + "\n")
        self.write("src/styles.css", "\n".join(f".s{i} {{ color: red; }}" for i in range(15)) + "\n")
        self.write("tests/test_ok.py", "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self): pass\n")
        code_init, rep_init, _ = self.run_cli("--init", "--max-lines", "5")
        self.assertEqual(code_init, 0, rep_init["errors"])
        init_cfg = json.loads((self.repo / ".guardrails" / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(init_cfg["file_limits"]["baseline_files"], {"src/big.mts": 8})

        # Switch to valid L1 setup and test growth, new monolith, stale missing file, and shrunk file.
        self.write_minimal_guardrails(trust_level="L1")
        cfg = json.loads((self.repo / ".guardrails" / "config.json").read_text(encoding="utf-8"))
        cfg["file_limits"] = {
            "max_lines": 5,
            "max_allowed": 3,
            "allow_paths": [],
            "baseline_files": {"src/big.mts": 8, "src/gone.cts": 10},
        }
        self.write(".guardrails/config.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

        # 1. Exact baseline ceiling passes (with stale missing warning for gone.cts).
        c1, r1, _ = self.run_cli()
        self.assertEqual(c1, 0, r1["errors"])
        self.assertTrue(any("baselined oversize file 'src/gone.cts' no longer exists" in w for w in r1["warnings"]))

        # 2. Growing src/big.mts from 8 -> 9 fails EVEN THOUGH max_allowed is 3.
        self.write("src/big.mts", "\n".join(f"export const a{i} = {i};" for i in range(9)) + "\n")
        c2, r2, _ = self.run_cli()
        self.assertEqual(c2, 1)
        self.assertIn("oversize file 'src/big.mts' grew from 8 to 9 lines", "\n".join(r2["errors"]))

        # 3. Reset src/big.mts to 8 lines; adding new oversize src/new_big.cts fails EVEN WITH max_allowed=3.
        self.write("src/big.mts", "\n".join(f"export const a{i} = {i};" for i in range(8)) + "\n")
        self.write("src/new_big.cts", "\n".join(f"export const b{i} = {i};" for i in range(7)) + "\n")
        c3, r3, _ = self.run_cli()
        self.assertEqual(c3, 1)
        self.assertIn("new oversize file 'src/new_big.cts' is 7 lines (> 5)", "\n".join(r3["errors"]))

        # 4. Remove new_big.cts and shrink src/big.mts <= 5 -> warns to remove from baseline_files and lower max_allowed.
        (self.repo / "src/new_big.cts").unlink()
        self.write("src/big.mts", "export const a0 = 0;\n")
        c4, r4, _ = self.run_cli()
        self.assertEqual(c4, 0, r4["errors"])
        self.assertTrue(any("oversize file 'src/big.mts' shrunk to 1 lines" in w for w in r4["warnings"]))


if __name__ == "__main__":
    unittest.main()
