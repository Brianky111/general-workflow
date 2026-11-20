#!/usr/bin/env python3
"""Verify codebase guardrails, escape-hatch ratchets, prose budgets, and behavioral artifacts.

Use from the installed skill against a target project:

    python /path/to/general-workflow/scripts/repo_guard.py --root PATH [--json] [--run-check] [--check-head]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

GUARD_DIR = Path(".guardrails")
GUARDRAILS_VERSION = 2
TRUST_LEVELS = ("L0", "L1", "L2", "L3")
LEGACY_V1_PATHS = (
    Path("docs") / "workflow",
    Path("docs") / "workflow-state.md",
    Path("WORKFLOW-STATE.md"),
)
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    ".guardrails",
}
DEFAULT_PROSE_FILES = ["AGENTS.md"]
DEFAULT_PROSE_MAX_BYTES = 6000
MIN_RULE_MESSAGE_CHARS = 15
MIN_VERIFY_SECTION_CHARS = 15
VERIFY_SKILL_REQUIRED_SECTIONS = ("launch", "doctor", "drive", "evidence", "cleanup")
FEATURE_FILE_REQUIRED_H2_PREFIXES = (
    "sub-features",
    "how to get to it",
    "driving it with",
    "gotchas",
)

HEADING_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FRONTMATTER_LINE = re.compile(r"(?m)^([a-z][a-z0-9_-]*):\s*(.*?)\s*$")
MARKDOWN_MD_LINK = re.compile(r"\[[^\]]+\]\((?:\./)?([A-Za-z0-9_.-]+\.md)(?:#[^)]+)?\)")
FEATURE_PRIORITY_HINT = re.compile(
    r"(?im)(?:<!--\s*priority:\s*(core|secondary)\s*-->|^\s*priority:\s*(core|secondary)\s*$)"
)

CRLF = "\r\n"
CR = "\r"
LF = "\n"

UNSET = {
    "", "-", "--", "—", "–", "?", "none", "na", "n/a", "tbd", "todo", "pending",
    "无", "暂无", "待补", "待定", "未定", "未知",
}
PLACEHOLDER_REF = UNSET | {
    "later", "soon", "asap", "someday", "x", "xx", "xxx", "wip", "tbc",
    "todos", "uncommitted", "unpushed", "unknown", "placeholder", "example",
    "以后", "之后", "稍后", "回头", "过后", "后补", "再说", "以后再说",
    "待补充", "待补全", "回头补", "之后补", "稍后补", "后面补", "补上",
    "见下", "见上", "见下文", "同上", "未提交", "未推送", "最新提交", "占位",
}
VAGUE_OBSERVED = PLACEHOLDER_REF | {
    "pass", "passed", "ok", "okay", "done", "success", "succeeded", "green",
    "works", "working", "good", "lgtm", "verified",
    "通过", "已通过", "完成", "已完成", "正常", "没问题", "看起来没问题",
    "可以", "正确", "已验证", "成功",
}
MOVING_REF = re.compile(
    r"(?:\w+/)?(?:head|master|main|trunk|latest|tip)(?:[~^@].*)?", re.I
)
IMMUTABLE_COMMIT = re.compile(
    r"^(?:[0-9a-fA-F]{7,40}|v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z._-]+)?)$"
)
HEX_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")

DEFAULT_ESCAPE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("eslint-disable", re.compile(r"eslint-disable(?:-next-line|-line)?\b")),
    ("ts-ignore", re.compile(r"@ts-(?:ignore|expect-error|nocheck)\b")),
    (
        "python-ignore",
        re.compile(r"#\s*(?:noqa|type:\s*ignore|pragma:\s*no\s*cover|pylint:\s*disable)\b"),
    ),
    ("rust-allow", re.compile(r"#\[\s*allow\(")),
    ("go-nolint", re.compile(r"//\s*nolint\b")),
    ("java-suppress", re.compile(r"@SuppressWarnings\b")),
)
WORKAROUND_COMMENT = re.compile(
    r"(?:\b(?:HACK|WORKAROUND|XXX)\b|temporary hack|quick fix|临时方案|绕过检查)",
    re.I,
)
PROSE_PROHIBITION = re.compile(
    r"(?:禁止|不得|不要使用|不要调用|\bnever use\b|\bdo not import\b|\bmust not call\b|\bavoid calling\b)",
    re.I,
)

# Import patterns by syntax family.
PY_IMPORT = re.compile(r"^\s*import\s+(.+)$")
PY_FROM_IMPORT = re.compile(r"^\s*from\s+([.\w]+)\s+import\b")
JS_FROM_IMPORT = re.compile(r"^\s*(?:import|export)\b.*?from\s+['\"]([^'\"]+)['\"]")
JS_SIDE_EFFECT_IMPORT = re.compile(r"^\s*import\s+['\"]([^'\"]+)['\"]")
JS_REQUIRE = re.compile(r"\brequire\(\s*['\"]([^'\"]+)['\"]\s*\)")
RUST_USE = re.compile(r"^\s*(?:pub\s+)?use\s+([\w:]+)")

ANTI_PATTERN_CATEGORIES = (
    "silent-catch",
    "blind-wait",
    "hardcoded-path",
    "hardcoded-localhost",
    "hardcoded-secret",
)
DEFAULT_ALWAYS_ON_ANTI_PATTERNS = (
    "silent-catch",
    "blind-wait",
    "hardcoded-path",
    "hardcoded-secret",
)
ANTI_PATTERN_REMEDIATION = {
    "silent-catch": "silent-catch: avoid swallowing exceptions or returning fake defaults inside internal code; fail fast or map at the boundary",
    "blind-wait": "blind-wait: replace fixed millisecond delays or sleep loops with real readiness/state signals",
    "hardcoded-path": "hardcoded-path: move machine-local user paths into config/env inputs at the boundary",
    "hardcoded-localhost": "hardcoded-localhost: move local host URLs into boundary configuration with an explicit fallback",
    "hardcoded-secret": "hardcoded-secret: remove credential literals from source and inject secrets via environment or secret store",
}

PY_EXTENSIONS = {".py", ".pyw"}
JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
PY_SILENT_EXCEPT_SINGLE = re.compile(
    r"^\s*except\b[^:]*:\s*(?:pass|\.\.\.|return(?:\s+(?:None|\[\]|\{\}|\"\"|''))?)\s*$"
)
PY_EXCEPT_HEADER = re.compile(r"^(\s*)except\b[^:]*:\s*$")
PY_SILENT_BODY = re.compile(
    r"^\s*(?:pass|\.\.\.|return(?:\s+(?:None|\[\]|\{\}|\"\"|''))?)\s*$"
)
JS_CATCH_OPEN = re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{")
JS_SILENT_BODY = re.compile(
    r"^return(?:\s+(?:null|undefined|\[\]|\{\}|\"\"|''))?\s*;?$"
)
BLIND_WAIT_ALWAYS = (
    re.compile(r"\bwait_for_timeout\s*\("),
    re.compile(r"\bwaitForTimeout\s*\("),
    re.compile(r"\bnew\s+Promise\s*\([^)]*\bsetTimeout\s*\("),
)
BLIND_WAIT_PROMISE_START = re.compile(r"\bnew\s+Promise\s*\(")
BLIND_WAIT_PROMISE_MULTI = re.compile(r"\bnew\s+Promise\s*\([^;]{0,160}\bsetTimeout\s*\(")
BLIND_WAIT_CONFIGURED = (
    re.compile(r"\b(?:time|asyncio)\.sleep\s*\("),
    re.compile(r"\b(?:window\.|globalThis\.)?setTimeout\s*\([^,\n]+,\s*[1-9]\d*(?:_\d+)*\b"),
)
HARDCODED_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[/\\]{1,2}Users[/\\]{1,2}[^\s'\"`\\)]+"),
    re.compile(r"(?<![A-Za-z0-9_./])/(?:Users|home)/[A-Za-z0-9._-]+/"),
)
HARDCODED_LOCALHOST = re.compile(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?\b", re.I)
HARDCODED_SECRET_PATTERNS = (
    re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


@dataclass
class ForbiddenPrimitive:
    id: str
    pattern: re.Pattern[str]
    globs: list[str]
    allow_paths: list[Path]
    message: str


@dataclass
class BoundaryRule:
    id: str
    from_dir: Path
    forbid_import: str
    message: str


@dataclass
class AntiPatternsConfig:
    configured: bool
    max_allowed: int
    enabled: list[str]
    allow_paths: list[Path]
    allow_by_category: dict[str, list[Path]]
    extra_rules: list[ForbiddenPrimitive] = field(default_factory=list)


@dataclass
class GuardConfig:
    trust_level: str
    trust_level_valid: bool
    check_command: str
    verify_cli: str
    verify_skill: Path | None
    verify_skill_configured: bool
    source_roots: list[Path]
    exclude_dirs: set[str]
    prose_files: list[Path]
    prose_max_bytes: int
    require_fresh_head: bool
    max_escape_hatches: int
    anti_patterns: AntiPatternsConfig
    extra_escape_patterns: list[tuple[str, re.Pattern[str]]] = field(default_factory=list)
    forbidden_primitives: list[ForbiddenPrimitive] = field(default_factory=list)
    boundary_rules: list[BoundaryRule] = field(default_factory=list)


def read_utf8_lf(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig").replace(CRLF, LF).replace(CR, LF)


def normalized_token(value: str) -> str:
    return (
        value.strip()
        .strip("`\"'“”‘’()（）[]【】<>《》.,;:!?、。，；：！？…-— ")
        .casefold()
    )


def is_set(value: str) -> bool:
    stripped = value.strip().strip("`")
    return stripped.casefold() not in UNSET and not (
        stripped.startswith("<") and stripped.endswith(">")
    )


def is_placeholder(value: str) -> bool:
    token = normalized_token(value)
    if not is_set(value) or token in PLACEHOLDER_REF:
        return True
    parts = [part for part in re.split(r"[-_/\s]+", token) if part]
    return len(parts) > 1 and all(part in PLACEHOLDER_REF for part in parts)


def norm_key(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def normalize_rel_path(root: Path, raw_path: str, allow_globs: bool = False) -> Path:
    cleaned = raw_path.strip().strip("`").replace("\\", "/")
    if not is_set(cleaned):
        raise ValueError("expected a non-empty project-relative path")
    if not allow_globs and any(ch in cleaned for ch in "*?[]"):
        raise ValueError("expected a literal project-relative path (no globs)")
    if any(ch in cleaned for ch in "<>`#"):
        raise ValueError("expected a literal path, not template or markup text")
    if Path(cleaned).is_absolute() or PureWindowsPath(cleaned).drive:
        raise ValueError("expected a project-relative path, not an absolute path")
    resolved = (root / cleaned).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("path escapes the project root")
    return resolved


def path_is_within(path: Path, parent: Path) -> bool:
    norm_p = Path(norm_key(path))
    norm_parent = Path(norm_key(parent))
    return norm_p == norm_parent or norm_parent in norm_p.parents


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a POSIX glob (including **/ zero-or-more dirs) to a regex."""
    pat = pattern.strip().replace("\\", "/")
    i = 0
    parts: list[str] = ["^"]
    while i < len(pat):
        if pat.startswith("**/", i):
            parts.append("(?:.*/)?")
            i += 3
        elif pat.startswith("**", i):
            parts.append(".*")
            i += 2
        elif pat[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            parts.append("[^/]")
            i += 1
        else:
            parts.append(re.escape(pat[i]))
            i += 1
    parts.append("$")
    return re.compile("".join(parts))


def visible_lines(text: str) -> list[str]:
    """Drop fenced code blocks so documented examples are not parsed as real tables."""
    lines: list[str] = []
    fence = ""
    for line in text.split(LF):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = ""
            continue
        if marker:
            fence = marker[1]
            continue
        lines.append(line)
    return lines


def rows_in(lines: list[str], header: str) -> list[list[str]]:
    """Read Markdown table rows whose first column header equals `header`."""
    rows: list[list[str]] = []
    active = False
    for raw in lines:
        line = raw.strip()
        if not line.startswith("|"):
            active = False
            continue
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip("|"))]
        if cells and cells[0].strip("`") == header:
            active = True
            continue
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells if cell):
            continue
        if active:
            rows.append(cells)
    return rows


def extract_comment_fragment(line: str) -> str:
    """Return the comment portion of a line outside quoted strings, or empty string."""
    quote = ""
    escaped = False
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\" and quote != "`":
                escaped = True
            elif ch == quote:
                quote = ""
            i += 1
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            continue
        if ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[i:]
        if line.startswith("//", i) or line.startswith("/*", i):
            return line[i:]
        i += 1
    stripped = line.lstrip()
    if stripped.startswith("*"):
        return stripped
    return ""


def strip_code_comments(line: str) -> str:
    """Return code before any inline # or // comment (outside quoted strings)."""
    stripped = line.lstrip()
    if stripped.startswith(("#", "//", "/*", "*")):
        return ""
    frag = extract_comment_fragment(line)
    if not frag:
        return line
    idx = line.rfind(frag)
    return line[:idx] if idx >= 0 else line


def is_int_strict(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def parse_pattern_rules(
    root: Path, raw_rules: object, field_name: str, errors: list[str]
) -> list[ForbiddenPrimitive]:
    """Parse forbidden_primitives or anti_patterns.extra_rules entries with shared validation."""
    rules: list[ForbiddenPrimitive] = []
    if not isinstance(raw_rules, list):
        errors.append(f".guardrails/config.json: {field_name} must be an array")
        return rules
    for idx, item in enumerate(raw_rules):
        if not isinstance(item, dict):
            errors.append(f".guardrails/config.json: {field_name}[{idx}] must be object")
            continue
        rid = str(item.get("id", "")).strip()
        pat_str = item.get("pattern", "")
        globs = item.get("globs", [])
        allow_raw = item.get("allow_paths", [])
        msg = str(item.get("message", "")).strip()
        if not rid or is_placeholder(rid):
            errors.append(f".guardrails/config.json: {field_name}[{idx}] missing id")
            continue
        if not isinstance(pat_str, str) or not pat_str:
            errors.append(f".guardrails/config.json: {field_name} '{rid}' missing pattern")
            continue
        try:
            compiled = re.compile(pat_str)
        except re.error as exc:
            errors.append(
                f".guardrails/config.json: {field_name} '{rid}' invalid regex: {exc}"
            )
            continue
        if not isinstance(globs, list) or not globs or any(
            not isinstance(g, str) or not g.strip() for g in globs
        ):
            errors.append(
                f".guardrails/config.json: {field_name} '{rid}' requires non-empty globs"
            )
            continue
        if not isinstance(allow_raw, list) or any(not isinstance(a, str) for a in allow_raw):
            errors.append(
                f".guardrails/config.json: {field_name} '{rid}' allow_paths must be strings"
            )
            continue
        allow_paths: list[Path] = []
        valid_allow = True
        for a in allow_raw:
            try:
                allow_paths.append(normalize_rel_path(root, a))
            except ValueError as exc:
                errors.append(
                    f".guardrails/config.json: {field_name} '{rid}' invalid allow_path '{a}': {exc}"
                )
                valid_allow = False
        if not valid_allow:
            continue
        if is_placeholder(msg) or len(msg) < MIN_RULE_MESSAGE_CHARS:
            errors.append(
                f".guardrails/config.json: {field_name} '{rid}' requires an actionable "
                f"root-cause message (>= {MIN_RULE_MESSAGE_CHARS} chars)"
            )
            continue
        rules.append(
            ForbiddenPrimitive(rid, compiled, [g.strip() for g in globs], allow_paths, msg)
        )
    return rules


def parse_anti_patterns_config(
    root: Path, raw_ap: object, trust_level_valid: str, errors: list[str]
) -> AntiPatternsConfig:
    if raw_ap is None:
        return AntiPatternsConfig(
            configured=False,
            max_allowed=0,
            enabled=list(DEFAULT_ALWAYS_ON_ANTI_PATTERNS),
            allow_paths=[],
            allow_by_category={},
            extra_rules=[],
        )
    if not isinstance(raw_ap, dict):
        errors.append(".guardrails/config.json: anti_patterns must be an object")
        return AntiPatternsConfig(
            configured=True,
            max_allowed=0,
            enabled=list(DEFAULT_ALWAYS_ON_ANTI_PATTERNS),
            allow_paths=[],
            allow_by_category={},
            extra_rules=[],
        )

    max_allowed = 0
    max_val = raw_ap.get("max_allowed", 0)
    if not is_int_strict(max_val) or max_val < 0:
        errors.append(
            ".guardrails/config.json: anti_patterns.max_allowed must be a non-negative integer"
        )
    else:
        max_allowed = max_val
        if trust_level_valid in {"L2", "L3"} and max_allowed > 0:
            errors.append(
                f".guardrails/config.json: {trust_level_valid} requires "
                "anti_patterns.max_allowed == 0; clean up anti-patterns before "
                "enabling outer-loop automation"
            )

    enabled_raw = raw_ap.get("enabled", list(ANTI_PATTERN_CATEGORIES))
    enabled: list[str] = []
    if not isinstance(enabled_raw, list) or any(not isinstance(c, str) for c in enabled_raw):
        errors.append(".guardrails/config.json: anti_patterns.enabled must be an array of categories")
        enabled = list(ANTI_PATTERN_CATEGORIES)
    else:
        for cat in enabled_raw:
            if cat not in ANTI_PATTERN_CATEGORIES:
                errors.append(
                    f".guardrails/config.json: unknown anti_patterns category '{cat}' "
                    f"(expected one of {', '.join(ANTI_PATTERN_CATEGORIES)})"
                )
            elif cat not in enabled:
                enabled.append(cat)

    allow_paths: list[Path] = []
    allow_raw = raw_ap.get("allow_paths", [])
    if not isinstance(allow_raw, list) or any(not isinstance(a, str) for a in allow_raw):
        errors.append(".guardrails/config.json: anti_patterns.allow_paths must be an array of paths")
    else:
        for a in allow_raw:
            try:
                allow_paths.append(normalize_rel_path(root, a))
            except ValueError as exc:
                errors.append(
                    f".guardrails/config.json: anti_patterns invalid allow_path '{a}': {exc}"
                )

    allow_by_category: dict[str, list[Path]] = {}
    by_cat_raw = raw_ap.get("allow_by_category", {})
    if not isinstance(by_cat_raw, dict):
        errors.append(".guardrails/config.json: anti_patterns.allow_by_category must be an object")
    else:
        for cat, paths_raw in by_cat_raw.items():
            if cat not in ANTI_PATTERN_CATEGORIES:
                errors.append(
                    f".guardrails/config.json: unknown category '{cat}' in allow_by_category"
                )
                continue
            if not isinstance(paths_raw, list) or any(not isinstance(a, str) for a in paths_raw):
                errors.append(
                    f".guardrails/config.json: anti_patterns.allow_by_category['{cat}'] must be strings"
                )
                continue
            resolved_list: list[Path] = []
            for a in paths_raw:
                try:
                    resolved_list.append(normalize_rel_path(root, a))
                except ValueError as exc:
                    errors.append(
                        f".guardrails/config.json: anti_patterns.allow_by_category['{cat}'] "
                        f"invalid path '{a}': {exc}"
                    )
            allow_by_category[cat] = resolved_list

    extra_rules = parse_pattern_rules(
        root, raw_ap.get("extra_rules", []), "anti_patterns.extra_rules", errors
    )
    return AntiPatternsConfig(
        configured=True,
        max_allowed=max_allowed,
        enabled=enabled,
        allow_paths=allow_paths,
        allow_by_category=allow_by_category,
        extra_rules=extra_rules,
    )


def parse_config(root: Path, raw_text: str, errors: list[str]) -> GuardConfig | None:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        errors.append(f".guardrails/config.json: invalid JSON ({exc.msg} at line {exc.lineno})")
        return None
    if not isinstance(data, dict):
        errors.append(".guardrails/config.json: top-level JSON value must be an object")
        return None

    version = data.get("guardrails_version")
    if not is_int_strict(version):
        errors.append(
            f".guardrails/config.json: guardrails_version must be integer {GUARDRAILS_VERSION}"
        )
    elif version != GUARDRAILS_VERSION:
        errors.append(
            f".guardrails/config.json: unsupported guardrails_version {version}; "
            f"expected {GUARDRAILS_VERSION}"
        )

    trust_level = data.get("trust_level", "")
    if not isinstance(trust_level, str) or trust_level not in TRUST_LEVELS:
        errors.append(
            f".guardrails/config.json: trust_level '{trust_level}' is invalid; "
            f"expected one of {', '.join(TRUST_LEVELS)}"
        )
        trust_level_valid = ""
    else:
        trust_level_valid = trust_level

    check_cmd = data.get("check_command", "")
    if not isinstance(check_cmd, str) or is_placeholder(check_cmd):
        errors.append(
            ".guardrails/config.json: check_command is missing or placeholder; "
            "provide a runnable deterministic check command"
        )
        check_cmd = ""

    verify_skill_raw = data.get("verify_skill")
    verify_skill: Path | None = None
    verify_skill_configured = verify_skill_raw is not None and verify_skill_raw != ""
    if verify_skill_configured:
        if not isinstance(verify_skill_raw, str):
            errors.append(".guardrails/config.json: verify_skill must be a string path")
        else:
            try:
                verify_skill = normalize_rel_path(root, verify_skill_raw)
            except ValueError as exc:
                errors.append(
                    f".guardrails/config.json: invalid verify_skill '{verify_skill_raw}': {exc}"
                )

    verify_cli = data.get("verify_cli", "")
    if verify_cli is None:
        verify_cli = ""
    if not isinstance(verify_cli, str):
        errors.append(".guardrails/config.json: verify_cli must be a string")
        verify_cli = ""
    elif (
        trust_level_valid in {"L1", "L2", "L3"}
        and is_placeholder(verify_cli)
        and not verify_skill_configured
    ):
        errors.append(
            f".guardrails/config.json: trust_level {trust_level_valid} requires a non-placeholder "
            "verify_cli command (or verify_skill directory)"
        )

    raw_roots = data.get("source_roots", ["."])
    source_roots: list[Path] = []
    if not isinstance(raw_roots, list) or not raw_roots:
        errors.append(".guardrails/config.json: source_roots must be a non-empty array of paths")
    else:
        for entry in raw_roots:
            if not isinstance(entry, str):
                errors.append(".guardrails/config.json: source_roots entries must be strings")
                continue
            try:
                source_roots.append(normalize_rel_path(root, entry))
            except ValueError as exc:
                errors.append(f".guardrails/config.json: invalid source_root '{entry}': {exc}")

    raw_excludes = data.get("exclude_dirs", [])
    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    if not isinstance(raw_excludes, list) or any(not isinstance(x, str) for x in raw_excludes):
        errors.append(".guardrails/config.json: exclude_dirs must be an array of directory names")
    else:
        exclude_dirs |= {x.strip().strip("/\\") for x in raw_excludes if x.strip()}

    raw_prose = data.get("prose_files", DEFAULT_PROSE_FILES)
    prose_files: list[Path] = []
    if not isinstance(raw_prose, list) or any(not isinstance(x, str) for x in raw_prose):
        errors.append(".guardrails/config.json: prose_files must be an array of relative paths")
    else:
        for entry in raw_prose:
            try:
                prose_files.append(normalize_rel_path(root, entry))
            except ValueError as exc:
                errors.append(f".guardrails/config.json: invalid prose_files entry '{entry}': {exc}")

    prose_max_bytes = data.get("prose_max_bytes", DEFAULT_PROSE_MAX_BYTES)
    if not is_int_strict(prose_max_bytes) or prose_max_bytes <= 0:
        errors.append(".guardrails/config.json: prose_max_bytes must be a positive integer")
        prose_max_bytes = DEFAULT_PROSE_MAX_BYTES

    require_fresh_head = data.get("require_fresh_head", False)
    if not isinstance(require_fresh_head, bool):
        errors.append(".guardrails/config.json: require_fresh_head must be a boolean")
        require_fresh_head = False
    elif trust_level_valid == "L3" and not require_fresh_head:
        errors.append(".guardrails/config.json: L3 automerge requires require_fresh_head: true")

    eh_raw = data.get("escape_hatches", {})
    max_escape_hatches = 0
    extra_patterns: list[tuple[str, re.Pattern[str]]] = []
    if not isinstance(eh_raw, dict):
        errors.append(".guardrails/config.json: escape_hatches must be an object")
    else:
        max_val = eh_raw.get("max_allowed", 0)
        if not is_int_strict(max_val) or max_val < 0:
            errors.append(
                ".guardrails/config.json: escape_hatches.max_allowed must be a non-negative integer"
            )
        else:
            max_escape_hatches = max_val
            if trust_level_valid in {"L2", "L3"} and max_escape_hatches > 0:
                errors.append(
                    f".guardrails/config.json: {trust_level_valid} requires "
                    "escape_hatches.max_allowed == 0; weed existing escape hatches before "
                    "enabling outer-loop automation"
                )
        raw_extra = eh_raw.get("extra_patterns", [])
        if not isinstance(raw_extra, list) or any(not isinstance(p, str) for p in raw_extra):
            errors.append(
                ".guardrails/config.json: escape_hatches.extra_patterns must be an array of regexes"
            )
        else:
            for idx, pat_str in enumerate(raw_extra):
                try:
                    extra_patterns.append((f"extra-{idx + 1}", re.compile(pat_str)))
                except re.error as exc:
                    errors.append(
                        f".guardrails/config.json: invalid regex in extra_patterns '{pat_str}': {exc}"
                    )

    forbidden_primitives = parse_pattern_rules(
        root, data.get("forbidden_primitives", []), "forbidden_primitives", errors
    )
    raw_ap = data["anti_patterns"] if "anti_patterns" in data else None
    anti_patterns = parse_anti_patterns_config(root, raw_ap, trust_level_valid, errors)

    boundary_rules: list[BoundaryRule] = []
    raw_br = data.get("boundary_rules", [])
    if not isinstance(raw_br, list):
        errors.append(".guardrails/config.json: boundary_rules must be an array")
    else:
        for idx, item in enumerate(raw_br):
            if not isinstance(item, dict):
                errors.append(f".guardrails/config.json: boundary_rules[{idx}] must be object")
                continue
            rid = str(item.get("id", "")).strip()
            from_raw = item.get("from_dir", "")
            forbid_raw = item.get("forbid_import", "")
            msg = str(item.get("message", "")).strip()
            if not rid or is_placeholder(rid):
                errors.append(f".guardrails/config.json: boundary_rules[{idx}] missing id")
                continue
            if not isinstance(from_raw, str):
                errors.append(f".guardrails/config.json: boundary_rules '{rid}' invalid from_dir")
                continue
            try:
                from_dir = normalize_rel_path(root, from_raw)
            except ValueError as exc:
                errors.append(
                    f".guardrails/config.json: boundary_rules '{rid}' invalid from_dir '{from_raw}': {exc}"
                )
                continue
            if not isinstance(forbid_raw, str) or is_placeholder(forbid_raw):
                errors.append(
                    f".guardrails/config.json: boundary_rules '{rid}' requires non-placeholder forbid_import"
                )
                continue
            if is_placeholder(msg) or len(msg) < MIN_RULE_MESSAGE_CHARS:
                errors.append(
                    f".guardrails/config.json: boundary_rules '{rid}' requires an actionable "
                    f"root-cause message (>= {MIN_RULE_MESSAGE_CHARS} chars)"
                )
                continue
            norm_forbid = forbid_raw.strip().replace("\\", "/").replace(".", "/").strip("/")
            boundary_rules.append(BoundaryRule(rid, from_dir, norm_forbid, msg))

    return GuardConfig(
        trust_level=trust_level_valid or "L0",
        trust_level_valid=bool(trust_level_valid),
        check_command=check_cmd,
        verify_cli=verify_cli,
        verify_skill=verify_skill,
        verify_skill_configured=verify_skill_configured,
        source_roots=source_roots,
        exclude_dirs=exclude_dirs,
        prose_files=prose_files,
        prose_max_bytes=prose_max_bytes,
        require_fresh_head=require_fresh_head,
        max_escape_hatches=max_escape_hatches,
        anti_patterns=anti_patterns,
        extra_escape_patterns=extra_patterns,
        forbidden_primitives=forbidden_primitives,
        boundary_rules=boundary_rules,
    )


def collect_source_files(root: Path, cfg: GuardConfig) -> list[Path]:
    seen: set[str] = set()
    files: list[Path] = []
    for src_root in cfg.source_roots:
        if not src_root.exists():
            continue
        if src_root.is_file():
            key = norm_key(src_root)
            if key not in seen:
                seen.add(key)
                files.append(src_root)
            continue
        for dirpath, dirnames, filenames in os.walk(src_root):
            dirnames[:] = sorted(
                d for d in dirnames if d not in cfg.exclude_dirs and not d.startswith(".git")
            )
            for fname in sorted(filenames):
                fpath = Path(dirpath) / fname
                key = norm_key(fpath)
                if key not in seen:
                    seen.add(key)
                    files.append(fpath)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def read_source_text(path: Path) -> str | None:
    raw = path.read_bytes()
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8-sig").replace(CRLF, LF).replace(CR, LF)
    except UnicodeDecodeError:
        return None


def extract_imports(code_line: str) -> list[str]:
    targets: list[str] = []
    if m := PY_FROM_IMPORT.match(code_line):
        targets.append(m[1])
    elif m := PY_IMPORT.match(code_line):
        for part in m[1].split(","):
            mod = part.strip().split()[0] if part.strip() else ""
            if mod:
                targets.append(mod)
    if m := JS_FROM_IMPORT.match(code_line):
        targets.append(m[1])
    elif m := JS_SIDE_EFFECT_IMPORT.match(code_line):
        targets.append(m[1])
    for m in JS_REQUIRE.finditer(code_line):
        targets.append(m[1])
    if m := RUST_USE.match(code_line):
        targets.append(m[1])
    return targets


def normalize_import_target(target: str) -> str:
    cleaned = target.strip().replace("\\", "/")
    cleaned = cleaned.replace("::", "/")
    if not cleaned.startswith("."):
        cleaned = cleaned.replace(".", "/")
    else:
        # Handle relative JS/TS like ../core/storage or Python .core.storage
        if "/" not in cleaned:
            cleaned = cleaned.lstrip(".").replace(".", "/")
    return cleaned.strip("/")


def is_anti_pattern_allowed(fpath: Path, category: str, ap: AntiPatternsConfig) -> bool:
    if any(path_is_within(fpath, allow) for allow in ap.allow_paths):
        return True
    return any(path_is_within(fpath, allow) for allow in ap.allow_by_category.get(category, ()))


def match_pattern_rules(
    fpath: Path,
    rel_posix: str,
    stripped_lines: list[str],
    rules: list[ForbiddenPrimitive],
    compiled_globs: dict[str, list[re.Pattern[str]]],
    label: str,
    errors: list[str],
) -> int:
    hits = 0
    for rule in rules:
        if any(path_is_within(fpath, allow) for allow in rule.allow_paths):
            continue
        if not any(g.match(rel_posix) for g in compiled_globs[rule.id]):
            continue
        for idx, code in enumerate(stripped_lines, start=1):
            if code and rule.pattern.search(code):
                hits += 1
                errors.append(f"{label} '{rule.id}' at {rel_posix}:{idx}: {rule.message}")
    return hits


def scan_anti_patterns_in_file(
    fpath: Path,
    rel_posix: str,
    stripped_lines: list[str],
    ap: AntiPatternsConfig,
) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    suffix = fpath.suffix.lower()
    enabled = set(ap.enabled)

    if "silent-catch" in enabled and not is_anti_pattern_allowed(fpath, "silent-catch", ap):
        if suffix in PY_EXTENSIONS:
            for i, code in enumerate(stripped_lines):
                if not code.strip():
                    continue
                if PY_SILENT_EXCEPT_SINGLE.match(code):
                    hits.append((rel_posix, i + 1, "silent-catch"))
                    continue
                m = PY_EXCEPT_HEADER.match(code)
                if not m:
                    continue
                base_indent = len(m[1].expandtabs(4))
                first_j = next(
                    (j for j in range(i + 1, len(stripped_lines)) if stripped_lines[j].strip()),
                    None,
                )
                if first_j is None:
                    continue
                code_j = stripped_lines[first_j]
                indent_j = len(code_j[:len(code_j) - len(code_j.lstrip())].expandtabs(4))
                if indent_j <= base_indent or not PY_SILENT_BODY.match(code_j):
                    continue
                next_k = next(
                    (k for k in range(first_j + 1, len(stripped_lines)) if stripped_lines[k].strip()),
                    None,
                )
                if next_k is None:
                    hits.append((rel_posix, i + 1, "silent-catch"))
                    continue
                code_k = stripped_lines[next_k]
                indent_k = len(code_k[:len(code_k) - len(code_k.lstrip())].expandtabs(4))
                if indent_k <= base_indent:
                    hits.append((rel_posix, i + 1, "silent-catch"))
        elif suffix in JS_EXTENSIONS:
            for i, code in enumerate(stripped_lines):
                if not code.strip():
                    continue
                m = JS_CATCH_OPEN.search(code)
                if not m:
                    continue
                body_chars: list[str] = []
                depth = 1
                closed = False
                for idx_line in range(i, min(len(stripped_lines), i + 6)):
                    seg = stripped_lines[idx_line]
                    if idx_line == i:
                        seg = seg[m.end():]
                    for ch in seg:
                        if ch == "{":
                            depth += 1
                            body_chars.append(ch)
                        elif ch == "}":
                            depth -= 1
                            if depth == 0:
                                closed = True
                                break
                            body_chars.append(ch)
                        else:
                            body_chars.append(ch)
                    if closed:
                        break
                    body_chars.append(" ")
                if closed:
                    body = " ".join("".join(body_chars).split())
                    if body == "" or JS_SILENT_BODY.match(body):
                        hits.append((rel_posix, i + 1, "silent-catch"))

    if "blind-wait" in enabled and not is_anti_pattern_allowed(fpath, "blind-wait", ap):
        blind_patterns = list(BLIND_WAIT_ALWAYS)
        if ap.configured:
            blind_patterns.extend(BLIND_WAIT_CONFIGURED)
        skip_lines: set[int] = set()
        for i, code in enumerate(stripped_lines):
            if not code.strip() or i in skip_lines:
                continue
            if any(pat.search(code) for pat in blind_patterns):
                hits.append((rel_posix, i + 1, "blind-wait"))
                continue
            if BLIND_WAIT_PROMISE_START.search(code):
                window_parts = [code]
                for offset in (1, 2):
                    if i + offset < len(stripped_lines):
                        window_parts.append(stripped_lines[i + offset])
                if BLIND_WAIT_PROMISE_MULTI.search(" ".join(window_parts)):
                    hits.append((rel_posix, i + 1, "blind-wait"))
                    skip_lines.update({i + 1, i + 2})

    if "hardcoded-path" in enabled and not is_anti_pattern_allowed(fpath, "hardcoded-path", ap):
        for i, code in enumerate(stripped_lines):
            if code and any(pat.search(code) for pat in HARDCODED_PATH_PATTERNS):
                hits.append((rel_posix, i + 1, "hardcoded-path"))

    if (
        ap.configured
        and "hardcoded-localhost" in enabled
        and not is_anti_pattern_allowed(fpath, "hardcoded-localhost", ap)
    ):
        for i, code in enumerate(stripped_lines):
            if code and HARDCODED_LOCALHOST.search(code):
                hits.append((rel_posix, i + 1, "hardcoded-localhost"))

    if "hardcoded-secret" in enabled and not is_anti_pattern_allowed(fpath, "hardcoded-secret", ap):
        for i, code in enumerate(stripped_lines):
            if code and any(pat.search(code) for pat in HARDCODED_SECRET_PATTERNS):
                hits.append((rel_posix, i + 1, "hardcoded-secret"))

    return hits


def scan_sources(
    root: Path, cfg: GuardConfig, errors: list[str], warnings: list[str]
) -> dict[str, int]:
    files = collect_source_files(root, cfg)
    escape_violations: list[tuple[str, int, str]] = []
    ap_hits: list[tuple[str, int, str]] = []
    primitive_violations = 0
    extra_ap_violations = 0
    boundary_violations = 0

    compiled_globs = {
        rule.id: [glob_to_regex(g) for g in rule.globs]
        for rule in cfg.forbidden_primitives
    }
    ap_compiled_globs = {
        rule.id: [glob_to_regex(g) for g in rule.globs]
        for rule in cfg.anti_patterns.extra_rules
    }
    boundary_patterns = {
        rule.id: re.compile(rf"(?:^|/){re.escape(rule.forbid_import)}(?:/|$)")
        for rule in cfg.boundary_rules
    }

    for fpath in files:
        text = read_source_text(fpath)
        if text is None:
            continue
        rel_posix = fpath.relative_to(root).as_posix()
        lines = text.split(LF)
        stripped_lines = [strip_code_comments(line) for line in lines]

        # 1. Escape hatches & workaround comments
        all_escape_patterns = list(DEFAULT_ESCAPE_PATTERNS) + cfg.extra_escape_patterns
        for idx, line in enumerate(lines, start=1):
            matched_tag = None
            for tag, pat in all_escape_patterns:
                if pat.search(line):
                    matched_tag = tag
                    break
            if matched_tag is None:
                comment = extract_comment_fragment(line)
                if comment and WORKAROUND_COMMENT.search(comment):
                    matched_tag = "workaround-comment"
            if matched_tag is not None:
                escape_violations.append((rel_posix, idx, matched_tag))

        # 2. Forbidden primitives & anti_patterns.extra_rules
        primitive_violations += match_pattern_rules(
            fpath,
            rel_posix,
            stripped_lines,
            cfg.forbidden_primitives,
            compiled_globs,
            "forbidden_primitive",
            errors,
        )
        extra_ap_violations += match_pattern_rules(
            fpath,
            rel_posix,
            stripped_lines,
            cfg.anti_patterns.extra_rules,
            ap_compiled_globs,
            "anti_pattern_rule",
            errors,
        )

        # 3. Built-in anti-patterns
        ap_hits.extend(scan_anti_patterns_in_file(fpath, rel_posix, stripped_lines, cfg.anti_patterns))

        # 4. Boundary rules
        for rule in cfg.boundary_rules:
            if not path_is_within(fpath, rule.from_dir):
                continue
            pat = boundary_patterns[rule.id]
            for idx, code in enumerate(stripped_lines, start=1):
                if not code:
                    continue
                for target in extract_imports(code):
                    norm_target = normalize_import_target(target)
                    if pat.search(norm_target):
                        boundary_violations += 1
                        errors.append(
                            f"boundary_rule '{rule.id}' at {rel_posix}:{idx} imports "
                            f"'{target}': {rule.message}"
                        )

    found_escapes = len(escape_violations)
    if found_escapes > cfg.max_escape_hatches:
        sample = ", ".join(f"{p}:{ln}[{tag}]" for p, ln, tag in escape_violations[:8])
        more = f" (+{found_escapes - 8} more)" if found_escapes > 8 else ""
        errors.append(
            f"escape hatches found ({found_escapes}) exceed ratchet max_allowed "
            f"({cfg.max_escape_hatches}): {sample}{more}; fix the root cause or weed old debt "
            "instead of raising max_allowed"
        )
    elif found_escapes < cfg.max_escape_hatches:
        warnings.append(
            f"escape hatches dropped to {found_escapes} under ratchet {cfg.max_escape_hatches}; "
            f"lower escape_hatches.max_allowed to {found_escapes} in .guardrails/config.json"
        )

    found_ap = len(ap_hits)
    ap_max = cfg.anti_patterns.max_allowed
    if found_ap > ap_max:
        sample = ", ".join(f"{p}:{ln}[{cat}]" for p, ln, cat in ap_hits[:8])
        more = f" (+{found_ap - 8} more)" if found_ap > 8 else ""
        seen_cats = list(dict.fromkeys(cat for _p, _ln, cat in ap_hits))
        hints = "; ".join(ANTI_PATTERN_REMEDIATION[c] for c in seen_cats)
        errors.append(
            f"anti-patterns found ({found_ap}) exceed ratchet max_allowed ({ap_max}): "
            f"{sample}{more}; {hints}"
        )
    elif cfg.anti_patterns.configured and found_ap < ap_max:
        warnings.append(
            f"anti-patterns dropped to {found_ap} under ratchet {ap_max}; "
            f"lower anti_patterns.max_allowed to {found_ap} in .guardrails/config.json"
        )

    return {
        "files_scanned": len(files),
        "escape_hatches": found_escapes,
        "anti_patterns": found_ap,
        "anti_pattern_rule_violations": extra_ap_violations,
        "primitive_violations": primitive_violations,
        "boundary_violations": boundary_violations,
    }


def check_prose_diet(
    root: Path, cfg: GuardConfig, errors: list[str], warnings: list[str]
) -> list[dict]:
    candidates: dict[str, Path] = {}
    for p in cfg.prose_files:
        if p.is_file():
            candidates[norm_key(p)] = p
    for src_root in cfg.source_roots:
        if not src_root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(src_root):
            dirnames[:] = sorted(
                d for d in dirnames if d not in cfg.exclude_dirs and not d.startswith(".git")
            )
            if "AGENTS.md" in filenames:
                fpath = Path(dirpath) / "AGENTS.md"
                candidates[norm_key(fpath)] = fpath

    stats: list[dict] = []
    for key in sorted(candidates):
        fpath = candidates[key]
        rel = fpath.relative_to(root).as_posix()
        text = read_utf8_lf(fpath)
        byte_len = len(text.encode("utf-8"))
        if byte_len > cfg.prose_max_bytes:
            errors.append(
                f"{rel} is {byte_len} bytes, over its {cfg.prose_max_bytes}-byte prose budget; "
                "promote rules to APIs or executable checks instead of growing prose"
            )
        elif byte_len > cfg.prose_max_bytes * 0.90:
            warnings.append(
                f"{rel} is at {100 * byte_len / cfg.prose_max_bytes:.0f}% of its "
                f"{cfg.prose_max_bytes}-byte budget; trim or promote rules to lint"
            )
        prohibition_count = sum(
            1 for line in visible_lines(text) if PROSE_PROHIBITION.search(line)
        )
        if prohibition_count >= 3:
            warnings.append(
                f"{rel} contains {prohibition_count} prose prohibitions; consider promoting "
                "them into forbidden_primitives, boundary_rules, or lint checks"
            )
        stats.append({"file": rel, "bytes": byte_len, "prohibitions": prohibition_count})
    return stats


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Parse leading YAML frontmatter key/value pairs, or return None if missing/unclosed."""
    if not text.startswith("---\n"):
        return None
    closing = text.find("\n---", 4)
    if closing < 0:
        return None
    fields: dict[str, str] = {}
    for key, raw_val in FRONTMATTER_LINE.findall(text[4:closing]):
        val = raw_val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1].strip()
        fields[key] = val
    return fields


def markdown_sections(text: str) -> list[tuple[int, str, str]]:
    """Return (depth, title, body_without_headings) for each heading outside code fences."""
    lines = text.split(LF)
    fenced: set[int] = set()
    fence = ""
    for i, line in enumerate(lines):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            fenced.add(i)
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = ""
        elif marker:
            fence = marker[1]
            fenced.add(i)
    marks = [
        (i, len(m[1]), m[2].strip())
        for i, line in enumerate(lines)
        if i not in fenced and (m := HEADING_LINE.match(line))
    ]
    out: list[tuple[int, str, str]] = []
    for idx, (start, depth, title) in enumerate(marks):
        end = len(lines)
        for other, level, _ in marks[idx + 1:]:
            if level <= depth:
                end = other
                break
        body_lines = [
            line
            for k, line in enumerate(lines[start + 1:end], start=start + 1)
            if k in fenced or not HEADING_LINE.match(line)
        ]
        out.append((depth, title, LF.join(body_lines)))
    return out


def validate_verify_skill(
    root: Path,
    skill_dir: Path,
    errors: list[str],
) -> tuple[dict[str, dict[str, str]], dict[str, str], dict]:
    """Validate a sharded project-local verify-<app> skill directory and collect its features."""
    rel_skill = skill_dir.relative_to(root).as_posix()
    features: dict[str, dict[str, str]] = {}
    aliases: dict[str, str] = {}
    stats = {"path": rel_skill, "name": "", "features": 0}

    if not skill_dir.is_dir():
        errors.append(f"{rel_skill}: verify_skill directory does not exist")
        return features, aliases, stats

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{rel_skill}/SKILL.md: missing verify_skill entrypoint")
        return features, aliases, stats

    skill_text = read_utf8_lf(skill_md)
    fm = parse_frontmatter(skill_text)
    if fm is None:
        errors.append(f"{rel_skill}/SKILL.md: missing or unclosed YAML frontmatter")
    else:
        skill_name = fm.get("name", "")
        skill_desc = fm.get("description", "")
        if is_placeholder(skill_name):
            errors.append(f"{rel_skill}/SKILL.md: frontmatter 'name' is missing or placeholder")
        else:
            stats["name"] = skill_name
        if is_placeholder(skill_desc):
            errors.append(
                f"{rel_skill}/SKILL.md: frontmatter 'description' is missing or placeholder"
            )

    sec_map: dict[str, str] = {}
    for _depth, title, body in markdown_sections(skill_text):
        key = re.sub(r"[:：]+$", "", title.strip()).casefold()
        sec_map.setdefault(key, body)
    for req in VERIFY_SKILL_REQUIRED_SECTIONS:
        if req not in sec_map:
            errors.append(f"{rel_skill}/SKILL.md: missing required section '{req.title()}'")
        else:
            chars = len("".join(sec_map[req].split()))
            if chars < MIN_VERIFY_SECTION_CHARS:
                errors.append(
                    f"{rel_skill}/SKILL.md: section '{req.title()}' has {chars} chars, "
                    f"under the {MIN_VERIFY_SECTION_CHARS}-char minimum"
                )

    features_dir = skill_dir / "features"
    if not features_dir.is_dir():
        errors.append(f"{rel_skill}/features: missing features/ directory")
        return features, aliases, stats

    siblings = sorted(p for p in features_dir.glob("*.md") if p.name.lower() != "readme.md")
    readme_path = features_dir / "README.md"
    if not readme_path.is_file():
        errors.append(f"{rel_skill}/features/README.md: missing feature map index")
    else:
        readme_visible = LF.join(visible_lines(read_utf8_lf(readme_path)))
        linked_names: set[str] = set()
        for match in MARKDOWN_MD_LINK.finditer(readme_visible):
            linked = match[1]
            if linked.lower() == "readme.md":
                continue
            linked_names.add(linked)
            if not (features_dir / linked).is_file():
                errors.append(
                    f"{rel_skill}/features/README.md: broken link to missing feature file '{linked}'"
                )
        for sib in siblings:
            if sib.name not in linked_names:
                errors.append(
                    f"{rel_skill}/features/README.md: unindexed feature file '{sib.name}'"
                )

    if not siblings:
        errors.append(f"{rel_skill}/features/: at least one feature markdown file is required")
        return features, aliases, stats

    for fpath in siblings:
        rel_file = fpath.relative_to(root).as_posix()
        ftext = read_utf8_lf(fpath)
        fsecs = markdown_sections(ftext)
        h1s = [title for depth, title, _body in fsecs if depth == 1]
        if not h1s:
            errors.append(f"{rel_file}: missing H1 feature title")
            continue
        title = h1s[0].strip()
        if is_placeholder(title):
            errors.append(f"{rel_file}: feature H1 title cannot be placeholder")
            continue
        if title in features:
            errors.append(f"{rel_file}: duplicate feature title '{title}'")
            continue

        h2s = [(t, b) for depth, t, b in fsecs if depth == 2]
        positions: list[int] = []
        for prefix in FEATURE_FILE_REQUIRED_H2_PREFIXES:
            idx = next(
                (i for i, (t, _b) in enumerate(h2s) if t.strip().casefold().startswith(prefix)),
                None,
            )
            if idx is None:
                errors.append(f"{rel_file}: missing required H2 section starting with '{prefix}'")
            else:
                positions.append(idx)
                body_chars = len("".join(h2s[idx][1].split()))
                if body_chars < MIN_VERIFY_SECTION_CHARS:
                    errors.append(
                        f"{rel_file}: section '{h2s[idx][0]}' has {body_chars} chars, "
                        f"under the {MIN_VERIFY_SECTION_CHARS}-char minimum"
                    )
        if len(positions) == len(FEATURE_FILE_REQUIRED_H2_PREFIXES) and positions != sorted(positions):
            errors.append(
                f"{rel_file}: required H2 sections are out of order "
                "(expected Sub-features -> How to get to it -> Driving it with -> Gotchas)"
            )

        vis_text = LF.join(visible_lines(ftext))
        prio_match = FEATURE_PRIORITY_HINT.search(vis_text)
        priority = (prio_match[1] or prio_match[2]).lower() if prio_match else "core"
        features[title] = {
            "entrypoint": rel_file,
            "verify_cli": rel_skill,
            "artifact": rel_file,
            "priority": priority,
        }
        aliases[fpath.stem] = title
        aliases[fpath.stem.casefold()] = title

    stats["features"] = len(features)
    return features, aliases, stats


def check_features_and_verification(
    root: Path,
    cfg: GuardConfig,
    guard_dir: Path,
    check_head: bool,
    errors: list[str],
    warnings: list[str],
) -> tuple[dict, dict | None]:
    features: dict[str, dict[str, str]] = {}
    aliases: dict[str, str] = {}
    verify_skill_stats: dict | None = None
    feature_map_file = guard_dir / "feature-map.md"

    if cfg.verify_skill_configured:
        if feature_map_file.is_file():
            warnings.append(
                "both verify_skill and .guardrails/feature-map.md exist; "
                "using verify_skill as single source of truth"
            )
        if cfg.verify_skill is not None:
            features, aliases, verify_skill_stats = validate_verify_skill(
                root, cfg.verify_skill, errors
            )
    elif feature_map_file.is_file():
        fm_text = read_utf8_lf(feature_map_file)
        fm_rows = rows_in(visible_lines(fm_text), "Feature")
        if not fm_rows:
            errors.append(
                ".guardrails/feature-map.md: missing non-empty Feature table "
                "('| Feature | Entrypoint | Verify CLI | Artifact | Priority |')"
            )
        for row in fm_rows:
            if len(row) < 5:
                errors.append(f".guardrails/feature-map.md: row has fewer than 5 columns: {row}")
                continue
            name, entry, cli, artifact, priority = [c.strip() for c in row[:5]]
            if is_placeholder(name):
                errors.append(".guardrails/feature-map.md: feature name cannot be placeholder")
                continue
            if name in features:
                errors.append(f".guardrails/feature-map.md: duplicate feature '{name}'")
                continue
            if is_placeholder(entry):
                errors.append(
                    f".guardrails/feature-map.md: '{name}' entrypoint is missing/placeholder"
                )
            if is_placeholder(cli):
                errors.append(
                    f".guardrails/feature-map.md: '{name}' verify CLI is missing/placeholder"
                )
            if is_placeholder(artifact):
                errors.append(
                    f".guardrails/feature-map.md: '{name}' artifact expectation is missing"
                )
            prio_norm = priority.lower()
            if prio_norm not in {"core", "secondary"}:
                errors.append(
                    f".guardrails/feature-map.md: '{name}' priority '{priority}' must be core or secondary"
                )
                prio_norm = "core"
            features[name] = {
                "entrypoint": entry,
                "verify_cli": cli,
                "artifact": artifact,
                "priority": prio_norm,
            }

    vr_file = guard_dir / "verification.md"
    vr_rows = rows_in(visible_lines(read_utf8_lf(vr_file)), "Feature") if vr_file.is_file() else []
    verified: dict[str, dict[str, str]] = {}
    map_label = "verify_skill" if cfg.verify_skill_configured else "feature-map.md"
    for row in vr_rows:
        if len(row) < 5:
            errors.append(f".guardrails/verification.md: row has fewer than 5 columns: {row}")
            continue
        raw_name, cmd, observed, artifact, commit = [c.strip() for c in row[:5]]
        if is_placeholder(raw_name):
            errors.append(".guardrails/verification.md: feature name cannot be placeholder")
            continue
        name = aliases.get(raw_name) or aliases.get(raw_name.casefold()) or raw_name
        if name in verified:
            errors.append(f".guardrails/verification.md: duplicate verification row for '{raw_name}'")
            continue
        if features and name not in features:
            errors.append(
                f".guardrails/verification.md: '{raw_name}' is not listed in {map_label}"
            )
        if is_placeholder(cmd):
            errors.append(f".guardrails/verification.md: '{name}' command is missing/placeholder")
        obs_norm = normalized_token(observed)
        if is_placeholder(observed) or obs_norm in VAGUE_OBSERVED:
            errors.append(
                f".guardrails/verification.md: '{name}' observed result '{observed}' is too vague; "
                "record what the command or user actually observed"
            )

        art_clean = artifact.strip().strip("`")
        if is_placeholder(art_clean):
            errors.append(f".guardrails/verification.md: '{name}' artifact is missing/placeholder")
        elif re.fullmatch(r"https?://\S+", art_clean):
            pass
        else:
            try:
                art_path = normalize_rel_path(root, art_clean)
                if not art_path.is_file():
                    errors.append(
                        f".guardrails/verification.md: '{name}' artifact '{art_clean}' "
                        "does not exist on disk"
                    )
                elif art_path.stat().st_size <= 0:
                    errors.append(
                        f".guardrails/verification.md: '{name}' artifact '{art_clean}' "
                        "is empty (0 bytes)"
                    )
            except ValueError as exc:
                errors.append(
                    f".guardrails/verification.md: '{name}' invalid artifact '{art_clean}': {exc}"
                )

        commit_clean = commit.strip().strip("`")
        if is_placeholder(commit_clean):
            errors.append(f".guardrails/verification.md: '{name}' commit anchor is missing")
        elif MOVING_REF.fullmatch(normalized_token(commit_clean)):
            errors.append(
                f".guardrails/verification.md: '{name}' commit '{commit_clean}' is a moving ref; "
                "anchor to an immutable commit SHA or release tag"
            )
        elif not IMMUTABLE_COMMIT.fullmatch(commit_clean):
            errors.append(
                f".guardrails/verification.md: '{name}' commit '{commit_clean}' does not look "
                "like an immutable commit SHA or version tag"
            )

        verified[name] = {
            "command": cmd,
            "observed": observed,
            "artifact": art_clean,
            "commit": commit_clean,
        }

    core_features = [name for name, meta in features.items() if meta["priority"] == "core"]
    missing_core = [name for name in core_features if name not in verified]
    if cfg.trust_level in {"L1", "L2", "L3"} and missing_core:
        errors.append(
            f".guardrails/verification.md: {cfg.trust_level} requires verification artifacts for "
            f"every core feature; missing: {', '.join(missing_core)}"
        )
    elif cfg.trust_level == "L0" and missing_core:
        warnings.append(
            f"core features without verification rows yet: {', '.join(missing_core)}"
        )

    head_sha = ""
    dirty_source_paths: list[str] = []
    if check_head or cfg.require_fresh_head:
        head_proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if head_proc.returncode != 0 or not head_proc.stdout.strip():
            errors.append(
                "--check-head / require_fresh_head requires a git repository with at least one commit"
            )
        else:
            head_sha = head_proc.stdout.strip()
            status_proc = subprocess.run(
                ["git", "-C", str(root), "-c", "core.quotepath=false", "status", "--porcelain"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            if status_proc.returncode == 0:
                guard_resolved = guard_dir.resolve()
                for raw_line in status_proc.stdout.splitlines():
                    if len(raw_line) < 4:
                        continue
                    rel_item = raw_line[3:].strip()
                    if " -> " in rel_item:
                        rel_item = rel_item.split(" -> ", 1)[1].strip()
                    rel_item = rel_item.strip('"')
                    candidate = (root / rel_item).resolve()
                    if path_is_within(candidate, guard_resolved):
                        continue
                    if any(path_is_within(candidate, sr) for sr in cfg.source_roots):
                        dirty_source_paths.append(rel_item)
            if dirty_source_paths:
                errors.append(
                    "freshness check failed: uncommitted changes under source_roots invalidate "
                    f"verification ({', '.join(dirty_source_paths[:6])})"
                )
            for name, meta in verified.items():
                rec_commit = meta["commit"]
                if not HEX_SHA.fullmatch(rec_commit) or not head_sha.lower().startswith(
                    rec_commit.lower()
                ):
                    errors.append(
                        f"stale verification for '{name}': recorded commit '{rec_commit}', "
                        f"current HEAD is '{head_sha[:7]}'; re-verify on current HEAD"
                    )

    return (
        {
            "features_total": len(features),
            "core_features": len(core_features),
            "verified_features": len(verified),
            "head_sha": head_sha[:12] if head_sha else "",
            "dirty_source_paths": dirty_source_paths,
        },
        verify_skill_stats,
    )


def run_check_command(root: Path, command: str, errors: list[str]) -> dict:
    proc = subprocess.run(
        command,
        shell=True,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    combined = ((proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")).strip()
    tail_lines = combined.splitlines()[-10:] if combined else []
    tail = "\n".join(tail_lines)
    if proc.returncode != 0:
        errors.append(
            f"check_command failed (exit {proc.returncode}): {command}"
            + (f"\n{tail}" if tail else "")
        )
    return {
        "command": command,
        "returncode": proc.returncode,
        "passed": proc.returncode == 0,
        "output_tail": tail,
    }


def inspect_repo(root: Path, run_check: bool = False, check_head: bool = False) -> dict:
    root = root.resolve()
    guard_dir = root / GUARD_DIR
    legacy_found = [
        p.as_posix() for p in LEGACY_V1_PATHS if (root / p).exists()
    ]

    if not guard_dir.exists():
        if legacy_found:
            return {
                "root": str(root),
                "guard_status": "legacy_v1",
                "legacy_paths": legacy_found,
                "errors": [],
                "warnings": [],
                "message": (
                    "found v1.x workflow state without .guardrails/; migrate to v2 per "
                    "references/06-repo-guard-contract.md instead of overwriting"
                ),
            }
        return {
            "root": str(root),
            "guard_status": "uninitialized",
            "legacy_paths": [],
            "errors": [],
            "warnings": [],
            "message": (
                "no .guardrails/ found; start from references/01-intent-and-invariants.md"
            ),
        }

    errors: list[str] = []
    warnings: list[str] = []
    config_file = guard_dir / "config.json"
    if not config_file.is_file():
        for name in ("config.json", "feature-map.md", "verification.md"):
            if not (guard_dir / name).is_file():
                errors.append(f"missing .guardrails/{name}")
        return {
            "root": str(root),
            "guard_status": "invalid",
            "legacy_paths": legacy_found,
            "errors": errors,
            "warnings": warnings,
        }

    cfg = parse_config(root, read_utf8_lf(config_file), errors)
    has_feature_map = (guard_dir / "feature-map.md").is_file()
    has_verification = (guard_dir / "verification.md").is_file()
    using_verify_skill = bool(cfg and cfg.verify_skill_configured)
    if not using_verify_skill and not has_feature_map:
        errors.append("missing .guardrails/feature-map.md")
    if not has_verification:
        if cfg is not None and cfg.trust_level_valid and cfg.trust_level == "L0":
            warnings.append(
                "missing .guardrails/verification.md (optional at L0; required before L1)"
            )
        else:
            errors.append("missing .guardrails/verification.md")

    scan_stats: dict[str, int] = {}
    prose_stats: list[dict] = []
    verify_stats: dict = {}
    verify_skill_stats: dict | None = None
    check_run: dict | None = None

    if cfg is not None:
        scan_stats = scan_sources(root, cfg, errors, warnings)
        prose_stats = check_prose_diet(root, cfg, errors, warnings)
        verify_stats, verify_skill_stats = check_features_and_verification(
            root, cfg, guard_dir, check_head, errors, warnings
        )
        if run_check and cfg.check_command:
            check_run = run_check_command(root, cfg.check_command, errors)

    return {
        "root": str(root),
        "guard_status": "invalid" if errors else "ready",
        "trust_level": cfg.trust_level if cfg else "",
        "require_fresh_head": cfg.require_fresh_head if cfg else False,
        "max_escape_hatches": cfg.max_escape_hatches if cfg else None,
        "anti_patterns_config": (
            {
                "configured": cfg.anti_patterns.configured,
                "max_allowed": cfg.anti_patterns.max_allowed,
                "enabled": cfg.anti_patterns.enabled,
            }
            if cfg
            else None
        ),
        "legacy_paths": legacy_found,
        "scan": scan_stats,
        "prose": prose_stats,
        "verification": verify_stats,
        "verify_skill": verify_skill_stats,
        "check_run": check_run,
        "errors": errors,
        "warnings": warnings,
    }


def format_human(report: dict) -> str:
    status = report["guard_status"]
    if status == "uninitialized":
        return "\n".join([report["message"], "0 error(s), 0 warning(s)"])
    if status == "legacy_v1":
        return "\n".join([
            f"legacy v1 state detected: {', '.join(report['legacy_paths'])}",
            report["message"],
            "0 error(s), 0 warning(s)",
        ])

    lines: list[str] = []
    scan = report.get("scan") or {}
    ver = report.get("verification") or {}
    lines.append(
        f"trust_level {report.get('trust_level') or '?'} | "
        f"guard_status {status} | "
        f"fresh_head {str(report.get('require_fresh_head', False)).lower()}"
    )
    if scan:
        lines.append(
            f"  scan: files={scan.get('files_scanned', 0)} "
            f"escape_hatches={scan.get('escape_hatches', 0)}/{report.get('max_escape_hatches', 0)} "
            f"primitive_violations={scan.get('primitive_violations', 0)} "
            f"boundary_violations={scan.get('boundary_violations', 0)}"
        )
        ap_cfg = report.get("anti_patterns_config") or {}
        ap_found = scan.get("anti_patterns", 0)
        if ap_cfg.get("configured") or ap_found > 0:
            lines.append(
                f"  anti_patterns: hits={ap_found}/{ap_cfg.get('max_allowed', 0)} "
                f"(enabled={len(ap_cfg.get('enabled') or [])})"
            )
    if ver:
        lines.append(
            f"  features: total={ver.get('features_total', 0)} "
            f"core={ver.get('core_features', 0)} "
            f"verified={ver.get('verified_features', 0)}"
        )
    vs = report.get("verify_skill")
    if vs:
        lines.append(
            f"  verify_skill: {vs.get('path', '')} "
            f"(name={vs.get('name', '?')}, features={vs.get('features', 0)})"
        )
    for item in report.get("prose") or []:
        lines.append(
            f"  prose: {item['file']} bytes={item['bytes']} prohibitions={item['prohibitions']}"
        )
    if report.get("check_run"):
        cr = report["check_run"]
        lines.append(
            f"  check_run: {'PASS' if cr['passed'] else 'FAIL'} (exit {cr['returncode']})"
        )
    for warn in report.get("warnings") or []:
        lines.append(f"WARN  {warn}")
    for err in report.get("errors") or []:
        lines.append(f"ERROR {err}")
    lines.append(
        f"{len(report.get('errors') or [])} error(s), {len(report.get('warnings') or [])} warning(s)"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=".",
        help="target project root directory (default: current working directory)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON report"
    )
    parser.add_argument(
        "--run-check",
        action="store_true",
        help="execute config.json check_command inside --root",
    )
    parser.add_argument(
        "--check-head",
        action="store_true",
        help="require verification.md commits to match current git HEAD with clean source_roots",
    )
    args = parser.parse_args(argv)
    report = inspect_repo(Path(args.root), run_check=args.run_check, check_head=args.check_head)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_human(report))
    return 1 if report["guard_status"] == "invalid" else 0


if __name__ == "__main__":
    sys.exit(main())
