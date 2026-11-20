"""Tests for scripts/install.py and scripts/sync_vendor.py."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = ROOT / "scripts" / "install.py"
SYNC_SCRIPT = ROOT / "scripts" / "sync_vendor.py"
MANIFEST = json.loads((ROOT / "vendor" / "pstack" / "UPSTREAM.json").read_text(encoding="utf-8"))
CORE_SKILLS = MANIFEST["skills"]["core"]
PRINCIPLE_SKILLS = MANIFEST["skills"]["principles"]


class InstallerAndVendorSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="gw-install-test-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.home.mkdir(parents=True, exist_ok=True)

    def run_install(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(INSTALL_SCRIPT),
                "--root",
                str(ROOT),
                "--home",
                str(self.home),
                *args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def test_claude_default_core_install_and_verify(self):
        res = self.run_install("--target", "claude")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

        skills_dir = self.home / ".claude" / "skills"
        gw_dir = skills_dir / "general-workflow"
        self.assertTrue((gw_dir / "SKILL.md").is_file())
        self.assertTrue((gw_dir / "vendor" / "pstack" / "UPSTREAM.json").is_file())
        self.assertFalse((gw_dir / "archive").exists())

        for name in CORE_SKILLS:
            s_dir = skills_dir / name
            self.assertTrue((s_dir / "SKILL.md").is_file(), name)
            self.assertTrue((s_dir / "LICENSE.pstack").is_file(), name)
            marker = json.loads((s_dir / ".general-workflow-vendor.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["managed_by"], "general-workflow")
            self.assertEqual(marker["skill"], name)

        for name in PRINCIPLE_SKILLS:
            self.assertFalse((skills_dir / name).exists(), name)

        agent_file = self.home / ".claude" / "agents" / "comment-sicko.md"
        self.assertTrue(agent_file.is_file())

    def test_vendor_mode_all_and_bundled(self):
        res_all = self.run_install("--target", "codex", "--vendor-mode", "all")
        self.assertEqual(res_all.returncode, 0, res_all.stdout + res_all.stderr)
        codex_skills = self.home / ".codex" / "skills"
        for name in CORE_SKILLS + PRINCIPLE_SKILLS:
            self.assertTrue((codex_skills / name / "SKILL.md").is_file(), name)
        self.assertFalse((self.home / ".codex" / "agents").exists())

        res_bundled = self.run_install("--target", "agents", "--vendor-mode", "bundled")
        self.assertEqual(res_bundled.returncode, 0, res_bundled.stdout + res_bundled.stderr)
        agents_skills = self.home / ".agents" / "skills"
        self.assertTrue((agents_skills / "general-workflow" / "vendor" / "pstack" / "SKILL.md").is_file() is False)
        self.assertTrue((agents_skills / "general-workflow" / "vendor" / "pstack" / "skills" / "correct" / "SKILL.md").is_file())
        self.assertEqual([p.name for p in agents_skills.iterdir()], ["general-workflow"])

    def test_idempotent_reinstall_does_not_nest_directory(self):
        self.assertEqual(self.run_install("--target", "claude").returncode, 0)
        res2 = self.run_install("--target", "claude")
        self.assertEqual(res2.returncode, 0, res2.stdout + res2.stderr)
        gw_dir = self.home / ".claude" / "skills" / "general-workflow"
        self.assertFalse((gw_dir / "general-workflow").exists())

    def test_collision_protection_requires_force_and_force_succeeds(self):
        unmanaged = self.home / ".claude" / "skills" / "correct"
        unmanaged.mkdir(parents=True, exist_ok=True)
        (unmanaged / "SKILL.md").write_text("custom\n", encoding="utf-8")

        blocked = self.run_install("--target", "claude")
        self.assertEqual(blocked.returncode, 1)
        self.assertIn("collision with unmanaged skill", blocked.stdout + blocked.stderr)
        self.assertEqual((unmanaged / "SKILL.md").read_text(encoding="utf-8"), "custom\n")

        forced = self.run_install("--target", "claude", "--force")
        self.assertEqual(forced.returncode, 0, forced.stdout + forced.stderr)
        self.assertTrue((unmanaged / ".general-workflow-vendor.json").is_file())

    def test_dry_run_creates_nothing_and_uninstall_preserves_unrelated(self):
        dry = self.run_install("--target", "claude", "--dry-run")
        self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
        self.assertFalse((self.home / ".claude").exists())

        self.assertEqual(self.run_install("--target", "claude").returncode, 0)
        unrelated_skill = self.home / ".claude" / "skills" / "my-own-skill"
        unrelated_skill.mkdir(parents=True, exist_ok=True)
        (unrelated_skill / "SKILL.md").write_text("# mine\n", encoding="utf-8")
        unrelated_agent = self.home / ".claude" / "agents" / "my-agent.md"
        unrelated_agent.write_text("# my agent\n", encoding="utf-8")

        un = self.run_install("--target", "claude", "--uninstall")
        self.assertEqual(un.returncode, 0, un.stdout + un.stderr)
        self.assertFalse((self.home / ".claude" / "skills" / "general-workflow").exists())
        for name in CORE_SKILLS:
            self.assertFalse((self.home / ".claude" / "skills" / name).exists())
        self.assertFalse((self.home / ".claude" / "agents" / "comment-sicko.md").exists())
        self.assertTrue((unrelated_skill / "SKILL.md").is_file())
        self.assertTrue(unrelated_agent.is_file())

    def test_sync_vendor_verify_passes_on_repo_and_fails_on_mutation(self):
        ok = subprocess.run(
            [sys.executable, "-X", "utf8", str(SYNC_SCRIPT), "--verify"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("54 file(s) verified, 0 error(s)", ok.stdout)

        copy_root = Path(self.temp.name) / "repo-copy"
        shutil.copytree(ROOT / "vendor", copy_root / "vendor")
        target = copy_root / "vendor" / "pstack" / "skills" / "architect" / "SKILL.md"
        target.write_text("corrupted\n", encoding="utf-8")
        bad = subprocess.run(
            [sys.executable, "-X", "utf8", str(SYNC_SCRIPT), "--root", str(copy_root), "--verify"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(bad.returncode, 1)
        self.assertIn("checksum mismatch", bad.stdout + bad.stderr)


if __name__ == "__main__":
    unittest.main()
