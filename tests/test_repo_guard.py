"""Regression tests for scripts/repo_guard.py.

Every test constructs a minimal target repository inside TemporaryDirectory,
executes repo_guard via CLI or inspect_repo, and asserts on both exit codes
and exact actionable error/warning messages.
"""

import json
import os
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


if __name__ == "__main__":
    unittest.main()
