#!/usr/bin/env python3
"""Verify or fetch the vendored pstack upstream snapshot under vendor/pstack/.

Default mode (--verify) runs strictly offline against UPSTREAM.json checksums.
Use --fetch [--commit SHA] to refresh verbatim files from upstream GitHub raw URLs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
VENDOR_REL = Path("vendor") / "pstack"
MANIFEST_NAME = "UPSTREAM.json"
EXCLUDED_TEST_DIR = Path("skills") / "statechart" / "scripts" / "test"
HEX_COMMIT = re.compile(r"^[0-9a-fA-F]{40}$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


def normalize_lf_bytes(raw: bytes) -> bytes:
    """Normalize CRLF/CR line endings to LF before hashing or writing."""
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def lf_sha256(raw: bytes) -> str:
    """Return the lowercase SHA-256 hex digest after LF line-ending normalization."""
    return hashlib.sha256(normalize_lf_bytes(raw)).hexdigest()


def safe_vendor_path(vendor_dir: Path, rel_posix: str) -> Path:
    """Resolve a relative manifest path inside vendor_dir without allowing escapes."""
    if not rel_posix or rel_posix.startswith("/") or "\\" in rel_posix:
        raise ValueError(f"invalid vendor relative path: {rel_posix!r}")
    candidate = (vendor_dir / rel_posix).resolve()
    if not candidate.is_relative_to(vendor_dir.resolve()):
        raise ValueError(f"vendor path escapes vendor/pstack: {rel_posix!r}")
    return candidate


def load_manifest(vendor_dir: Path) -> tuple[dict | None, list[str]]:
    manifest_path = vendor_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        return None, [f"missing manifest: {VENDOR_REL.as_posix()}/{MANIFEST_NAME}"]
    try:
        data = json.loads(manifest_path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"invalid {MANIFEST_NAME}: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{MANIFEST_NAME} top-level value must be a JSON object"]
    return data, []


def repo_slug(repo_value: str) -> str:
    cleaned = repo_value.strip().rstrip("/")
    prefix = "https://github.com/"
    if cleaned.startswith(prefix):
        cleaned = cleaned[len(prefix):]
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    return cleaned


def verify_vendor(root: Path) -> tuple[int, list[str]]:
    """Verify vendor/pstack/ offline against UPSTREAM.json and return (file_count, errors)."""
    vendor_dir = (root / VENDOR_REL).resolve()
    errors: list[str] = []
    data, load_errors = load_manifest(vendor_dir)
    if data is None:
        return 0, load_errors

    commit = str(data.get("commit", ""))
    if not HEX_COMMIT.fullmatch(commit):
        errors.append(f"{MANIFEST_NAME}: commit must be a 40-char SHA, got {commit!r}")
    if data.get("license") != "MIT":
        errors.append(f"{MANIFEST_NAME}: license must be 'MIT'")
    if not str(data.get("repository", "")).strip():
        errors.append(f"{MANIFEST_NAME}: repository must be non-empty")

    test_dir = vendor_dir / EXCLUDED_TEST_DIR
    if test_dir.exists():
        errors.append(
            f"excluded upstream test directory must not be vendored: "
            f"{(VENDOR_REL / EXCLUDED_TEST_DIR).as_posix()}"
        )

    license_path = vendor_dir / "LICENSE"
    if not license_path.is_file():
        errors.append(f"missing upstream license: {VENDOR_REL.as_posix()}/LICENSE")
    else:
        lic_text = license_path.read_bytes().decode("utf-8", errors="replace")
        if "MIT License" not in lic_text or "Lauren Tan" not in lic_text:
            errors.append(f"{VENDOR_REL.as_posix()}/LICENSE does not match expected MIT Lauren Tan license")

    files_map = data.get("files")
    if not isinstance(files_map, dict) or not files_map:
        errors.append(f"{MANIFEST_NAME}: 'files' must be a non-empty object")
        return 0, errors

    declared_paths: set[str] = set()
    for rel_posix, expected_hash in sorted(files_map.items()):
        if not isinstance(rel_posix, str) or not isinstance(expected_hash, str):
            errors.append(f"{MANIFEST_NAME}: invalid file entry {rel_posix!r}")
            continue
        try:
            fpath = safe_vendor_path(vendor_dir, rel_posix)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        declared_paths.add(rel_posix)
        if not SHA256_HEX.fullmatch(expected_hash):
            errors.append(f"{MANIFEST_NAME}: invalid sha256 for {rel_posix}: {expected_hash!r}")
        if not fpath.is_file():
            errors.append(f"missing vendored file: {VENDOR_REL.as_posix()}/{rel_posix}")
            continue
        actual_hash = lf_sha256(fpath.read_bytes())
        if SHA256_HEX.fullmatch(expected_hash) and actual_hash != expected_hash:
            errors.append(
                f"checksum mismatch for {VENDOR_REL.as_posix()}/{rel_posix}: "
                f"expected {expected_hash[:12]}, got {actual_hash[:12]}"
            )

    if vendor_dir.is_dir():
        for path in sorted(vendor_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(vendor_dir).as_posix()
            if rel == MANIFEST_NAME:
                continue
            if rel not in declared_paths:
                errors.append(f"undeclared file under {VENDOR_REL.as_posix()}: {rel}")

    return len(files_map), errors


def fetch_vendor(root: Path, commit_override: str | None = None) -> tuple[int, list[str]]:
    """Download declared upstream files at the pinned (or overridden) commit SHA."""
    vendor_dir = (root / VENDOR_REL).resolve()
    data, load_errors = load_manifest(vendor_dir)
    if data is None:
        return 0, load_errors

    commit = commit_override or str(data.get("commit", ""))
    if not HEX_COMMIT.fullmatch(commit):
        return 0, [f"commit must be a 40-char SHA, got {commit!r}"]

    slug = repo_slug(str(data.get("repository", "")))
    subpath = str(data.get("subpath", "pstack")).strip("/")
    files_map = data.get("files")
    if not slug or not isinstance(files_map, dict) or not files_map:
        return 0, [f"{MANIFEST_NAME}: repository and non-empty files map are required"]

    new_hashes: dict[str, str] = {}
    errors: list[str] = []
    declared_paths: set[str] = set()

    for rel_posix in sorted(files_map):
        try:
            dest = safe_vendor_path(vendor_dir, rel_posix)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        declared_paths.add(rel_posix)
        url = f"https://raw.githubusercontent.com/{slug}/{commit}/{subpath}/{rel_posix}"
        req = urllib.request.Request(url, headers={"User-Agent": "general-workflow-sync-vendor"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            errors.append(f"HTTP {exc.code} fetching {url}")
            continue
        except urllib.error.URLError as exc:
            errors.append(f"network error fetching {url}: {exc.reason}")
            continue
        normalized = normalize_lf_bytes(raw)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(normalized)
        new_hashes[rel_posix] = lf_sha256(normalized)

    if errors:
        return len(new_hashes), errors

    test_dir = vendor_dir / EXCLUDED_TEST_DIR
    if test_dir.exists():
        shutil.rmtree(test_dir)

    for path in sorted(vendor_dir.rglob("*"), reverse=True):
        if path.is_file():
            rel = path.relative_to(vendor_dir).as_posix()
            if rel != MANIFEST_NAME and rel not in declared_paths:
                path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()

    data["commit"] = commit
    data["files"] = {k: new_hashes[k] for k in sorted(new_hashes)}
    manifest_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    (vendor_dir / MANIFEST_NAME).write_bytes(manifest_text.encode("utf-8"))
    return len(new_hashes), []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help="general-workflow repository root (default: parent of scripts/)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--verify",
        action="store_true",
        help="verify vendor/pstack/ against UPSTREAM.json offline (default)",
    )
    mode.add_argument(
        "--fetch",
        action="store_true",
        help="fetch verbatim files from upstream commit into vendor/pstack/ and update hashes",
    )
    parser.add_argument(
        "--commit",
        default=None,
        help="optional 40-char upstream commit SHA for --fetch",
    )
    args = parser.parse_args(argv)
    if args.commit and not args.fetch:
        parser.error("--commit requires --fetch")

    root = Path(args.root).resolve()
    if args.fetch:
        count, errors = fetch_vendor(root, commit_override=args.commit)
        action = "fetched"
    else:
        count, errors = verify_vendor(root)
        action = "verified"

    for err in errors:
        print(f"ERROR {err}")
    print(f"vendor/pstack: {count} file(s) {action}, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
