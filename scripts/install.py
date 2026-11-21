#!/usr/bin/env python3
"""Cross-tool installer for general-workflow and its vendored pstack skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_MARKER = ".general-workflow-vendor.json"
EXCLUDE_ROOT_DIRS = {"archive"}
EXCLUDE_ANY_DIRS = {".git", ".claude", "__pycache__", ".pytest_cache"}
EXCLUDE_SUFFIXES = (".pyc", ".pyo")


@dataclass(frozen=True)
class InstallDest:
    label: str
    skills_dir: Path
    agents_dir: Path | None


def lf_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def is_link_or_junction(path: Path) -> bool:
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())


def remove_path_safely(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    elif is_link_or_junction(path):
        try:
            path.rmdir()
        except OSError:
            os.unlink(path)
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def load_upstream(root: Path) -> dict:
    manifest = root / "vendor" / "pstack" / "UPSTREAM.json"
    if not manifest.is_file():
        raise FileNotFoundError(f"missing upstream manifest: {manifest}")
    return json.loads(manifest.read_bytes().decode("utf-8"))


def resolve_destinations(
    targets: list[str],
    home: Path,
    skills_dir_arg: str | None,
    agents_dir_arg: str | None,
) -> list[InstallDest]:
    preset_map: dict[str, tuple[Path, Path | None]] = {
        "claude": (home / ".claude" / "skills", home / ".claude" / "agents"),
        "cursor": (home / ".cursor" / "skills", home / ".cursor" / "agents"),
        "codex": (home / ".codex" / "skills", None),
        "agents": (home / ".agents" / "skills", None),
        "pi": (home / ".pi" / "agent" / "skills", None),
    }
    expanded: list[str] = []
    for t in targets:
        if t == "all":
            for name in ("claude", "cursor", "codex", "agents", "pi"):
                if name not in expanded:
                    expanded.append(name)
        elif t not in expanded:
            expanded.append(t)

    dests: list[InstallDest] = [
        InstallDest(name, preset_map[name][0], preset_map[name][1]) for name in expanded
    ]
    if skills_dir_arg is not None:
        dests.append(
            InstallDest(
                "custom",
                Path(skills_dir_arg).expanduser().resolve(),
                Path(agents_dir_arg).expanduser().resolve() if agents_dir_arg else None,
            )
        )
    return dests


def copy_workflow_tree(src_root: Path, dest_dir: Path) -> None:
    resolved_src = src_root.resolve()

    def ignore_fn(dirpath: str, names: list[str]) -> set[str]:
        cur = Path(dirpath).resolve()
        ignored: set[str] = set()
        for name in names:
            if name in EXCLUDE_ANY_DIRS or name.endswith(EXCLUDE_SUFFIXES):
                ignored.add(name)
            elif cur == resolved_src and name in EXCLUDE_ROOT_DIRS:
                ignored.add(name)
        return ignored

    shutil.copytree(resolved_src, dest_dir, ignore=ignore_fn)


def is_managed_vendor_dir(path: Path) -> bool:
    marker = path / VENDOR_MARKER
    if not path.is_dir() or is_link_or_junction(path) or not marker.is_file():
        return False
    try:
        data = json.loads(marker.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return isinstance(data, dict) and data.get("managed_by") == "general-workflow"


def selected_vendor_skills(upstream: dict, vendor_mode: str) -> list[str]:
    skills_cfg = upstream.get("skills", {})
    core = list(skills_cfg.get("core", []))
    principles = list(skills_cfg.get("principles", []))
    if vendor_mode == "core":
        return core
    if vendor_mode == "all":
        return core + [p for p in principles if p not in core]
    return []


def verify_installed_workflow(installed_dir: Path) -> tuple[bool, list[str]]:
    outputs: list[str] = []
    for script_args in (
        [sys.executable, "-X", "utf8", str(installed_dir / "scripts" / "check_consistency.py"), "--root", str(installed_dir)],
        [sys.executable, "-X", "utf8", str(installed_dir / "scripts" / "sync_vendor.py"), "--root", str(installed_dir), "--verify"],
    ):
        proc = subprocess.run(
            script_args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        text = ((proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")).strip()
        if proc.returncode != 0:
            outputs.append(f"verify failed ({Path(script_args[3]).name}): {text}")
            return False, outputs
        outputs.append(text)
    return True, outputs


def install_to_destination(
    src_root: Path,
    upstream: dict,
    dest: InstallDest,
    vendor_mode: str,
    with_agents: bool | None,
    force: bool,
    dry_run: bool,
    skip_verify: bool,
) -> list[str]:
    errors: list[str] = []
    actions: list[str] = []

    workflow_dest = dest.skills_dir / "general-workflow"
    sibling_skills = selected_vendor_skills(upstream, vendor_mode)
    install_agents = (
        with_agents
        if with_agents is not None
        else (dest.agents_dir is not None and vendor_mode != "bundled")
    )
    if dest.agents_dir is None:
        install_agents = False

    # Pre-flight collision checks
    if is_link_or_junction(workflow_dest) and not force:
        errors.append(
            f"[{dest.label}] {workflow_dest} is a symlink/junction; rerun with --force to replace"
        )

    for skill_name in sibling_skills:
        s_dest = dest.skills_dir / skill_name
        if s_dest.exists() or is_link_or_junction(s_dest):
            if is_link_or_junction(s_dest) and not force:
                errors.append(
                    f"[{dest.label}] collision at {s_dest} (symlink/junction); "
                    "use --force or --vendor-mode bundled"
                )
            elif not is_managed_vendor_dir(s_dest) and not force:
                errors.append(
                    f"[{dest.label}] collision with unmanaged skill at {s_dest}; "
                    "use --force to overwrite or --vendor-mode bundled to skip sibling installs"
                )

    agent_names = list(upstream.get("agents", [])) if install_agents else []
    for agent_name in agent_names:
        assert dest.agents_dir is not None
        a_src = src_root / "vendor" / "pstack" / "agents" / f"{agent_name}.md"
        a_dest = dest.agents_dir / f"{agent_name}.md"
        if a_dest.exists() or is_link_or_junction(a_dest):
            if is_link_or_junction(a_dest) and not force:
                errors.append(
                    f"[{dest.label}] collision at {a_dest} (symlink/junction); rerun with --force"
                )
            elif a_dest.is_file() and lf_sha256(a_dest) != lf_sha256(a_src) and not force:
                errors.append(
                    f"[{dest.label}] collision with modified agent at {a_dest}; "
                    "rerun with --force or --no-agents"
                )

    if errors:
        return errors

    actions.append(f"[{dest.label}] install general-workflow -> {workflow_dest} (excluding archive/)")
    for skill_name in sibling_skills:
        actions.append(
            f"[{dest.label}] install vendored skill '{skill_name}' -> {dest.skills_dir / skill_name}"
        )
    for agent_name in agent_names:
        assert dest.agents_dir is not None
        actions.append(
            f"[{dest.label}] install vendored agent '{agent_name}.md' -> {dest.agents_dir / f'{agent_name}.md'}"
        )

    if dry_run:
        for line in actions:
            print(f"DRY-RUN {line}")
        return []

    dest.skills_dir.mkdir(parents=True, exist_ok=True)
    if workflow_dest.exists() or is_link_or_junction(workflow_dest):
        remove_path_safely(workflow_dest)
    copy_workflow_tree(src_root, workflow_dest)

    license_src = src_root / "vendor" / "pstack" / "LICENSE"
    for skill_name in sibling_skills:
        s_src = src_root / "vendor" / "pstack" / "skills" / skill_name
        s_dest = dest.skills_dir / skill_name
        if s_dest.exists() or is_link_or_junction(s_dest):
            remove_path_safely(s_dest)
        shutil.copytree(s_src, s_dest)
        shutil.copy2(license_src, s_dest / "LICENSE.pstack")
        marker = {
            "managed_by": "general-workflow",
            "vendor": "pstack",
            "skill": skill_name,
            "upstream_repository": upstream.get("repository"),
            "upstream_commit": upstream.get("commit"),
            "upstream_version": upstream.get("version"),
        }
        (s_dest / VENDOR_MARKER).write_bytes(
            (json.dumps(marker, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )

    for agent_name in agent_names:
        assert dest.agents_dir is not None
        dest.agents_dir.mkdir(parents=True, exist_ok=True)
        a_src = src_root / "vendor" / "pstack" / "agents" / f"{agent_name}.md"
        a_dest = dest.agents_dir / f"{agent_name}.md"
        if is_link_or_junction(a_dest):
            remove_path_safely(a_dest)
        shutil.copy2(a_src, a_dest)

    for line in actions:
        print(f"OK      {line}")

    if not skip_verify:
        ok, verify_outputs = verify_installed_workflow(workflow_dest)
        if not ok:
            return [f"[{dest.label}] {msg}" for msg in verify_outputs]
        for msg in verify_outputs:
            for subline in msg.splitlines():
                print(f"VERIFY  [{dest.label}] {subline}")

    return []


def uninstall_from_destination(
    src_root: Path,
    upstream: dict,
    dest: InstallDest,
    force: bool,
    dry_run: bool,
) -> list[str]:
    errors: list[str] = []
    planned: list[tuple[str, Path]] = []

    workflow_dest = dest.skills_dir / "general-workflow"
    if workflow_dest.exists() or is_link_or_junction(workflow_dest):
        if is_link_or_junction(workflow_dest) and not force:
            errors.append(
                f"[{dest.label}] refusing to remove symlink/junction {workflow_dest} without --force"
            )
        else:
            planned.append(("workflow", workflow_dest))

    if dest.skills_dir.is_dir():
        for entry in sorted(dest.skills_dir.iterdir()):
            if entry.name == "general-workflow":
                continue
            if is_managed_vendor_dir(entry):
                planned.append((f"vendored skill '{entry.name}'", entry))

    if dest.agents_dir and dest.agents_dir.is_dir():
        for agent_name in upstream.get("agents", []):
            a_src = src_root / "vendor" / "pstack" / "agents" / f"{agent_name}.md"
            a_dest = dest.agents_dir / f"{agent_name}.md"
            if not (a_dest.exists() or is_link_or_junction(a_dest)):
                continue
            if is_link_or_junction(a_dest) and not force:
                print(f"SKIP    [{dest.label}] symlink/junction agent preserved: {a_dest}")
                continue
            if a_dest.is_file() and lf_sha256(a_dest) != lf_sha256(a_src) and not force:
                print(f"SKIP    [{dest.label}] modified agent preserved: {a_dest}")
                continue
            planned.append((f"vendored agent '{agent_name}.md'", a_dest))

    if errors:
        return errors

    if not planned:
        print(f"OK      [{dest.label}] nothing managed to uninstall under {dest.skills_dir}")
        return []

    for desc, path in planned:
        if dry_run:
            print(f"DRY-RUN [{dest.label}] remove {desc}: {path}")
        else:
            remove_path_safely(path)
            print(f"REMOVED [{dest.label}] {desc}: {path}")
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help="source general-workflow directory (default: parent of scripts/)",
    )
    parser.add_argument(
        "--target",
        action="append",
        choices=("claude", "cursor", "codex", "agents", "pi", "all"),
        default=[],
        help="target tool preset (repeatable; 'all' expands to claude, cursor, codex, agents, pi)",
    )
    parser.add_argument(
        "--home",
        default=None,
        help="override user home directory for --target presets (default: current home)",
    )
    parser.add_argument(
        "--skills-dir",
        default=None,
        help="custom skills installation directory",
    )
    parser.add_argument(
        "--agents-dir",
        default=None,
        help="custom agents installation directory (used with --skills-dir)",
    )
    parser.add_argument(
        "--vendor-mode",
        choices=("core", "all", "bundled"),
        default="core",
        help="how to install vendored pstack skills: core (11 skills, default), all (23), or bundled",
    )
    agent_group = parser.add_mutually_exclusive_group()
    agent_group.add_argument(
        "--with-agents",
        dest="with_agents",
        action="store_true",
        default=None,
        help="install vendored subagent prompts (comment-sicko.md) when agents_dir exists",
    )
    agent_group.add_argument(
        "--no-agents",
        dest="with_agents",
        action="store_false",
        help="skip installing vendored subagent prompts",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print planned actions without modifying the filesystem",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite unmanaged collisions, symlinks/junctions, or modified agents",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="uninstall general-workflow and managed vendor directories from target(s)",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="skip post-install consistency and vendor checksum verification",
    )
    args = parser.parse_args(argv)

    if not args.target and args.skills_dir is None:
        parser.error(
            "specify at least one --target (claude, cursor, codex, agents, pi, all) or --skills-dir"
        )
    if args.agents_dir is not None and args.skills_dir is None:
        parser.error("--agents-dir requires --skills-dir")

    src_root = Path(args.root).resolve()
    home = Path(args.home).expanduser().resolve() if args.home else Path.home().resolve()
    try:
        upstream = load_upstream(src_root)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR failed to load vendor/pstack/UPSTREAM.json: {exc}")
        return 1

    dests = resolve_destinations(args.target, home, args.skills_dir, args.agents_dir)
    all_errors: list[str] = []
    for dest in dests:
        if args.uninstall:
            all_errors.extend(
                uninstall_from_destination(
                    src_root=src_root,
                    upstream=upstream,
                    dest=dest,
                    force=args.force,
                    dry_run=args.dry_run,
                )
            )
        else:
            all_errors.extend(
                install_to_destination(
                    src_root=src_root,
                    upstream=upstream,
                    dest=dest,
                    vendor_mode=args.vendor_mode,
                    with_agents=args.with_agents,
                    force=args.force,
                    dry_run=args.dry_run,
                    skip_verify=args.skip_verify,
                )
            )

    for err in all_errors:
        print(f"ERROR {err}")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
