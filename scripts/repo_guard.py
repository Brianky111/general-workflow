#!/usr/bin/env python3
"""Verify codebase guardrails, escape-hatch ratchets, prose budgets, and behavioral artifacts.

Use from the installed skill against a target project:

    python /path/to/general-workflow/scripts/repo_guard.py --root PATH [--json] [--run-check] [--check-head]
"""

from __future__ import annotations

import argparse
import ast
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
PROJECT_KINDS = ("app", "library")
LEGACY_V1_PATHS = (
    Path("docs") / "workflow",
    Path("docs") / "workflow-state.md",
    Path("WORKFLOW-STATE.md"),
)
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    "node_modules",
    ".pnpm-store",
    ".venv",
    "venv",
    ".guardrails",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".turbo",
}
ROOT_ARTIFACT_DIRS = {
    "dist",
    "build",
    "coverage",
    "htmlcov",
    "test-results",
    "playwright-report",
    "vendor",
    "target",
}
SKIPPED_FILENAMES = {
    ".api-token",
    ".gitkeep",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "Cargo.lock",
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
}
SKIPPED_SUFFIXES = {".log", ".lock", ".sqlite", ".sqlite3", ".db", ".map"}
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

SHALLOW_HEALTH_URL = re.compile(
    r"(?:https?://\S+|(?:^|\s))/(?:api/)?(?:healthz?|readyz?|livez?|ping|status)(?:[/?#\s'\"`]|$)",
    re.I,
)
HTTP_PROBE_TOOL = re.compile(
    r"(?:\b(?:curl|wget|http|xh|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)\b|"
    r"\bapi\.sh\b|\bGET\s+/(?:api/)?(?:healthz?|readyz?|livez?|ping|status)\b)",
    re.I,
)
PY_TEST_RUNNER = re.compile(
    r"^(?:uv(?:\s+--\S+(?:\s+\S+)?)*\s+run(?:\s+--\S+)*\s+|poetry\s+run\s+|"
    r"python(?:3(?:\.\d+)?)?(?:\s+-[A-Za-z0-9_]+)*\s+-m\s+)?"
    r"(?:pytest|py\.test|unittest)\b",
    re.I,
)
JS_TEST_RUNNER = re.compile(
    r"^(?:(?:npx|bunx|(?:pnpm|yarn|npm)(?:\s+(?:--dir|--prefix|--cwd)\s+\S+)*\s+exec(?:\s+--)?)\s+)?"
    r"(?:vitest|jest|mocha|ava)\b|"
    r"^(?:npm|pnpm|yarn|bun)(?:\s+(?:--dir|--prefix|--cwd)\s+\S+|\s+run)*\s+"
    r"(?:test(?::[A-Za-z0-9_.:-]+)?|vitest|jest|mocha|ava)\b",
    re.I,
)
NATIVE_TEST_RUNNER = re.compile(
    r"^(?:cargo(?:\s+\S+)*\s+test|go(?:\s+-C\s+\S+)?\s+test)\b",
    re.I,
)
BUILD_OR_LINT_ONLY = re.compile(
    r"^(?:(?:npm|pnpm|yarn|bun)(?:\s+(?:--dir|--prefix|--cwd)\s+\S+|\s+run)*\s+"
    r"(?:build|lint|typecheck|format|fmt|check)|"
    r"(?:uv(?:\s+--\S+(?:\s+\S+)?)*\s+run(?:\s+--\S+)*\s+)?(?:ruff|pyright|mypy|tsc|eslint))\b",
    re.I,
)

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
    "mock-in-prod",
)
DEFAULT_ALWAYS_ON_ANTI_PATTERNS = (
    "silent-catch",
    "blind-wait",
    "hardcoded-path",
    "hardcoded-secret",
    "mock-in-prod",
)
ANTI_PATTERN_REMEDIATION = {
    "silent-catch": "silent-catch: avoid swallowing exceptions/rejections or returning fake defaults inside internal code; fail fast or map at the boundary",
    "blind-wait": "blind-wait: replace fixed millisecond delays or artificial minLoadingMs waits with readiness signals; encapsulate legitimate retry backoff in a single runtime helper whitelisted via allow_by_category",
    "hardcoded-path": "hardcoded-path: move machine-local/WSL user paths into config/env inputs at the boundary",
    "hardcoded-localhost": "hardcoded-localhost: move local/LAN URLs and DB/WS endpoints into boundary configuration with an explicit fallback",
    "hardcoded-secret": "hardcoded-secret: remove credential literals from source and inject secrets via environment or secret store",
    "mock-in-prod": "mock-in-prod: remove MOCK_/FAKE_ data or mock fallbacks from production code; isolate demo/test data in seeds or fixtures",
}

DEFAULT_MAX_FILE_LINES = 600
STACK_DETECT_EXCLUDES = set(DEFAULT_EXCLUDE_DIRS)
DIRECT_SOURCE_ROOTS = ("src", "app", "lib", "cmd", "internal")
WORKSPACE_PARENT_DIRS = ("apps", "packages")
CONTAINER_DIRS = ("backend", "server", "api", "frontend", "client", "web")
NESTED_CODE_SUBDIRS = ("src", "app", "lib", "cmd", "internal")

PY_EXTENSIONS = {".py", ".pyw"}
JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}
CODE_EXTENSIONS = (
    PY_EXTENSIONS
    | JS_EXTENSIONS
    | {
        ".vue", ".svelte", ".astro",
        ".rs", ".go", ".java", ".kt", ".kts",
        ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp",
        ".cs", ".rb", ".php", ".swift", ".scala",
        ".ex", ".exs", ".lua", ".sh", ".bash", ".ps1",
    }
)
PY_SILENT_EXCEPT_SINGLE = re.compile(
    r"^\s*except\b[^:]*:\s*(?:pass|\.\.\.|return(?:\s+(?:None|\[\]|\{\}|\"\"|''))?)\s*$"
)
PY_BROAD_SUPPRESS = re.compile(
    r"\b(?:contextlib\.)?suppress\s*\([^)]*\b(?:BaseException|Exception)\b"
)
PY_EXCEPT_HEADER = re.compile(r"^(\s*)except\b[^:]*:\s*$")
PY_SILENT_BODY = re.compile(
    r"^\s*(?:pass|\.\.\.|return(?:\s+(?:None|\[\]|\{\}|\"\"|''))?)\s*$"
)
JS_CATCH_OPEN = re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{")
JS_PROMISE_CATCH_BLOCK_OPEN = re.compile(
    r"\.\s*catch\s*\(\s*(?:(?:async\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>|(?:async\s+)?function\s*(?:\([^)]*\))?)\s*\{"
)
JS_PROMISE_CATCH_CONCISE = re.compile(
    r"\.\s*catch\s*\(\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*"
    r"(?:null|undefined|\[\]|\(\s*\{\s*\}\s*\)|\"\"|''|``|void\s+0)\s*\)"
)
JS_THEN_REJECT_BLOCK_OPEN = re.compile(
    r"\.\s*then\s*\([^,\n]+,\s*(?:(?:async\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>|(?:async\s+)?function\s*(?:\([^)]*\))?)\s*\{"
)
JS_THEN_REJECT_CONCISE = re.compile(
    r"\.\s*then\s*\([^,\n]+,\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*"
    r"(?:null|undefined|\[\]|\(\s*\{\s*\}\s*\)|\"\"|''|``|void\s+0)\s*\)"
)
JS_SILENT_BODY = re.compile(
    r"^return(?:\s+(?:null|undefined|\[\]|\{\}|\"\"|''|``|void\s+0))?\s*;?$"
)
BLIND_WAIT_ALWAYS = (
    re.compile(r"\bwait_for_timeout\s*\("),
    re.compile(r"\bwaitForTimeout\s*\("),
    re.compile(r"\bnew\s+Promise\s*\([^)]*\bsetTimeout\s*\("),
    re.compile(
        r"\bawait\s+(?:sleep|delay|waitMs|artificialDelay|fakeDelay)\s*\(\s*"
        r"(?:[1-9]\d*(?:_\d+)*(?:\.\d+)?|0\.\d*[1-9])"
    ),
    re.compile(
        r"\b(?:min_?loading_?(?:ms|time|duration)|min_?skeleton_?(?:ms|time|duration)|"
        r"artificial_?delay|fake_?(?:delay|loading)|"
        r"after_(?:sync|load|reset|init)_refresh_ms|"
        r"(?:loading|render|display|page)_delay_(?:ms|sec|seconds))\s*"
        r"(?::[^=;\n]+)?(?:=\s*(?!0+(?:\.0+)?(?![.\d]))\S+|:\s*(?!0+(?:\.0+)?(?![.\d]))[1-9])",
        re.I,
    ),
)
BLIND_WAIT_PROMISE_START = re.compile(r"\bnew\s+Promise\s*\(")
BLIND_WAIT_PROMISE_MULTI = re.compile(r"\bnew\s+Promise\s*\([^;]{0,160}\bsetTimeout\s*\(")
BLIND_WAIT_CONFIGURED = (
    re.compile(r"\b(?:time|asyncio)\.sleep\s*\((?!\s*0+(?:\.0+)?\s*[,)])"),
    re.compile(r"\b(?:window\.|globalThis\.)?setTimeout\s*\([^,\n]+,\s*[1-9]\d*(?:_\d+)*\b"),
    re.compile(
        r"(?<![.\w$])(?:sleep|delay|waitMs|artificialDelay|fakeDelay)\s*\(\s*"
        r"(?:[1-9]\d*(?:_\d+)*(?:\.\d+)?|0\.\d*[1-9])\s*\)"
    ),
)
HARDCODED_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[/\\]{1,2}Users[/\\]{1,2}[^\s'\"`\\)]+"),
    re.compile(r"(?<![A-Za-z0-9_./])/Users/[A-Za-z0-9._-]+/"),
    re.compile(
        r"(?<![A-Za-z0-9_./])/home/[A-Za-z0-9._-]+/"
        r"(?:\.[A-Za-z0-9._-]+|(?:Desktop|Documents|Downloads|projects?|workspace|repos?|code|src|app|data|config|bin|venv|tmp)(?:/|$)|[^\s'\"`\\)]*\.[A-Za-z0-9]{1,8}\b)"
    ),
    re.compile(r"(?<![A-Za-z0-9_./])/mnt/[a-zA-Z]/Users/[^\s'\"`\\)]+"),
    re.compile(r"(?<![A-Za-z0-9_./])/root/[A-Za-z0-9._-]+"),
    re.compile(r"file:///(?:[A-Za-z]:/Users/|Users/|home/|root/)", re.I),
)
HARDCODED_LOCALHOST = re.compile(
    r"(?:https?|wss?|postgres(?:ql)?|mysql|redis|mongodb(?:\+srv)?)://"
    r"(?:[^/\s'\"`@]+@)?"
    r"(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|"
    r"192\.168\.\d{1,3}\.\d{1,3}|"
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?::\d+)?(?=[/?#'\"`\s),;]|$)",
    re.I,
)
HARDCODED_SECRET_PATTERNS = (
    re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b"),
)
TEST_FIXTURE_DIRS = {
    "tests", "test", "__tests__", "__mocks__", "mocks",
    "fixtures", "fixture", "seeds", "seed", "stories", "testdata",
}
TEST_FIXTURE_FILE = re.compile(
    r"(?:^|[._-])(?:test|tests|spec|specs|mock|mocks|fixture|fixtures|seed|seeds|stories)\.[a-z0-9]+$",
    re.I,
)
MOCK_DATA_DECL = re.compile(
    r"\b(?:(?:const|let|var)\s+)?(?:"
    r"(?!MOCK_(?:MODE|ENABLED|FLAG)\b)(?:MOCK|FAKE|DUMMY)_[A-Z0-9_]{2,}|"
    r"(?:mock|fake|dummy)(?:[A-Z]\w*)?(?:Data|List|Items|Users|Orders|Records|Response|Rows|Result|Results|Payload|Store)|"
    r"(?:mock|fake|dummy)_(?:data|list|items|users|orders|records|response|rows|result|results|payload|store)"
    r")\s*(?::[^=\n]+)?=\s*(?:\[|\{)"
)
MOCK_FALLBACK_EXPR = re.compile(
    r"(?:\|\||\?\?|\bor\b)\s*(?:"
    r"(?!MOCK_(?:MODE|ENABLED|FLAG)\b)(?:MOCK|FAKE|DUMMY)_[A-Z0-9_]{2,}|"
    r"(?:mock|fake|dummy)(?:[A-Z]\w*)?(?:Data|List|Items|Users|Orders|Records|Response|Rows|Result|Results|Payload|Store)|"
    r"(?:mock|fake|dummy)_(?:data|list|items|users|orders|records|response|rows|result|results|payload|store)"
    r")\b"
)
MOCK_IMPORT_DIR = re.compile(
    r"(?:^|/)(?:__mocks__|mocks|fixtures|testdata|seeds?)(?:/|$)", re.I
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
class FileLimitsConfig:
    configured: bool
    max_lines: int
    max_allowed: int
    allow_paths: list[Path]
    baseline_files: dict[str, int] = field(default_factory=dict)
    baseline_files_configured: bool = False


@dataclass
class GuardConfig:
    trust_level: str
    trust_level_valid: bool
    project_kind: str
    check_command: str
    verify_cli: str
    verify_skill: Path | None
    verify_skill_configured: bool
    source_roots: list[Path]
    clean_scopes: list[Path]
    exclude_dirs: set[str]
    prose_files: list[Path]
    prose_max_bytes: int
    require_fresh_head: bool
    max_escape_hatches: int
    anti_patterns: AntiPatternsConfig
    file_limits: FileLimitsConfig
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


def _split_shell_segments(cmd: str) -> list[str]:
    """Split a command string on &&, ||, or ; outside quoted substrings."""
    segments: list[str] = []
    cur: list[str] = []
    quote = ""
    escaped = False
    i = 0
    n = len(cmd)
    while i < n:
        ch = cmd[i]
        if quote:
            cur.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\" and quote != "'":
                escaped = True
            elif ch == quote:
                quote = ""
            i += 1
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            cur.append(ch)
            i += 1
            continue
        if cmd.startswith("&&", i) or cmd.startswith("||", i):
            seg = "".join(cur).strip()
            if seg:
                segments.append(seg)
            cur = []
            i += 2
            continue
        if ch == ";":
            seg = "".join(cur).strip()
            if seg:
                segments.append(seg)
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    tail = "".join(cur).strip()
    if tail:
        segments.append(tail)
    return segments


def _is_health_probe_segment(seg: str) -> bool:
    return bool(HTTP_PROBE_TOOL.search(seg) and SHALLOW_HEALTH_URL.search(seg))


def _is_test_runner_segment(seg: str) -> bool:
    s = seg.strip()
    return bool(
        PY_TEST_RUNNER.search(s) or JS_TEST_RUNNER.search(s) or NATIVE_TEST_RUNNER.search(s)
    )


def classify_fake_verify_cli(cmd: str, check_command: str = "") -> str | None:
    """Return a concrete reason if cmd looks like a fake verify_cli on an app repo."""
    norm_cmd = " ".join(cmd.strip().strip("`").split())
    if not norm_cmd:
        return None
    norm_chk = " ".join(check_command.strip().strip("`").split())
    if norm_chk and norm_cmd == norm_chk:
        return "duplicates check_command verbatim"
    segments = _split_shell_segments(norm_cmd)
    if not segments:
        return None
    probes = [_is_health_probe_segment(seg) for seg in segments]
    tests = [_is_test_runner_segment(seg) for seg in segments]
    has_real_driver = any(
        not p and not t and not BUILD_OR_LINT_ONLY.search(seg)
        for seg, p, t in zip(segments, probes, tests)
    )
    if any(probes) and not has_real_driver:
        return "is a shallow health/ping probe rather than a user-scenario driver"
    if any(tests) and not has_real_driver:
        return "invokes a test runner instead of a reusable application scenario driver"
    return None


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
    root: Path,
    raw_ap: object,
    trust_level_valid: str,
    errors: list[str],
    allow_l2_with_clean_scopes: bool = False,
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
        if (
            trust_level_valid == "L3"
            or (trust_level_valid == "L2" and not allow_l2_with_clean_scopes)
        ) and max_allowed > 0:
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


def parse_file_limits_config(
    root: Path,
    raw_fl: object,
    trust_level_valid: str,
    errors: list[str],
    clean_scopes: list[Path] | None = None,
) -> FileLimitsConfig:
    allow_l2_clean = bool(clean_scopes)
    if raw_fl is None:
        return FileLimitsConfig(
            configured=False,
            max_lines=DEFAULT_MAX_FILE_LINES,
            max_allowed=0,
            allow_paths=[],
            baseline_files={},
            baseline_files_configured=False,
        )
    if not isinstance(raw_fl, dict):
        errors.append(".guardrails/config.json: file_limits must be an object")
        return FileLimitsConfig(
            configured=True,
            max_lines=DEFAULT_MAX_FILE_LINES,
            max_allowed=0,
            allow_paths=[],
            baseline_files={},
            baseline_files_configured=False,
        )

    max_lines = raw_fl.get("max_lines", DEFAULT_MAX_FILE_LINES)
    if not is_int_strict(max_lines) or max_lines < 1:
        errors.append(".guardrails/config.json: file_limits.max_lines must be a positive integer")
        max_lines = DEFAULT_MAX_FILE_LINES

    max_allowed = 0
    max_val = raw_fl.get("max_allowed", 0)
    if not is_int_strict(max_val) or max_val < 0:
        errors.append(
            ".guardrails/config.json: file_limits.max_allowed must be a non-negative integer"
        )
    else:
        max_allowed = max_val
        if (
            trust_level_valid == "L3"
            or (trust_level_valid == "L2" and not allow_l2_clean)
        ) and max_allowed > 0:
            errors.append(
                f".guardrails/config.json: {trust_level_valid} requires "
                "file_limits.max_allowed == 0; split oversize monolith files before "
                "enabling outer-loop automation"
            )

    allow_paths: list[Path] = []
    allow_raw = raw_fl.get("allow_paths", [])
    if not isinstance(allow_raw, list) or any(not isinstance(a, str) for a in allow_raw):
        errors.append(".guardrails/config.json: file_limits.allow_paths must be an array of paths")
    else:
        for a in allow_raw:
            try:
                allow_paths.append(normalize_rel_path(root, a))
            except ValueError as exc:
                errors.append(
                    f".guardrails/config.json: file_limits invalid allow_path '{a}': {exc}"
                )

    baseline_files: dict[str, int] = {}
    baseline_files_configured = "baseline_files" in raw_fl and raw_fl.get("baseline_files") is not None
    if baseline_files_configured:
        raw_bf = raw_fl.get("baseline_files")
        if not isinstance(raw_bf, dict):
            errors.append(
                ".guardrails/config.json: file_limits.baseline_files must be an object mapping paths to line counts"
            )
        else:
            root_resolved = root.resolve()
            for raw_k, raw_v in raw_bf.items():
                if not isinstance(raw_k, str):
                    errors.append(
                        ".guardrails/config.json: file_limits.baseline_files keys must be relative file paths"
                    )
                    continue
                try:
                    norm_rel = normalize_rel_path(root, raw_k).relative_to(root_resolved).as_posix()
                except ValueError as exc:
                    errors.append(
                        f".guardrails/config.json: file_limits invalid baseline_files path '{raw_k}': {exc}"
                    )
                    continue
                if not is_int_strict(raw_v) or raw_v < 1:
                    errors.append(
                        f".guardrails/config.json: file_limits.baseline_files['{raw_k}'] must be a positive integer"
                    )
                    continue
                baseline_files[norm_rel] = raw_v
                if clean_scopes and any(
                    path_is_within((root_resolved / norm_rel).resolve(), cs)
                    for cs in clean_scopes
                ):
                    errors.append(
                        f".guardrails/config.json: file_limits.baseline_files entry '{norm_rel}' "
                        "cannot live inside clean_scopes"
                    )
            if (
                trust_level_valid == "L3"
                or (trust_level_valid == "L2" and not allow_l2_clean)
            ) and baseline_files:
                errors.append(
                    f".guardrails/config.json: {trust_level_valid} requires "
                    "file_limits.baseline_files to be empty; split oversize monolith files before "
                    "enabling outer-loop automation"
                )
    if trust_level_valid == "L2" and allow_l2_clean and max_allowed > 0 and not baseline_files:
        errors.append(
            ".guardrails/config.json: L2 with clean_scopes and file_limits.max_allowed > 0 "
            "requires non-empty file_limits.baseline_files to lock oversize monoliths outside clean_scopes"
        )

    return FileLimitsConfig(
        configured=True,
        max_lines=max_lines,
        max_allowed=max_allowed,
        allow_paths=allow_paths,
        baseline_files=baseline_files,
        baseline_files_configured=baseline_files_configured,
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

    project_kind = data.get("project_kind", "app")
    if not isinstance(project_kind, str) or project_kind not in PROJECT_KINDS:
        errors.append(
            f".guardrails/config.json: project_kind '{project_kind}' is invalid; "
            f"expected one of {', '.join(PROJECT_KINDS)}"
        )
        project_kind = "app"

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

    clean_scopes: list[Path] = []
    raw_cs = data.get("clean_scopes", [])
    if raw_cs is None:
        raw_cs = []
    if not isinstance(raw_cs, list) or any(not isinstance(x, str) for x in raw_cs):
        errors.append(".guardrails/config.json: clean_scopes must be an array of paths")
    else:
        seen_cs: set[str] = set()
        for entry in raw_cs:
            try:
                cs_path = normalize_rel_path(root, entry)
            except ValueError as exc:
                errors.append(f".guardrails/config.json: invalid clean_scopes entry '{entry}': {exc}")
                continue
            if source_roots and not any(path_is_within(cs_path, sr) for sr in source_roots):
                errors.append(
                    f".guardrails/config.json: clean_scopes entry '{entry}' is not under any configured source_roots"
                )
                continue
            key = norm_key(cs_path)
            if key not in seen_cs:
                seen_cs.add(key)
                clean_scopes.append(cs_path)

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
            if (
                trust_level_valid == "L3"
                or (trust_level_valid == "L2" and not clean_scopes)
            ) and max_escape_hatches > 0:
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
    anti_patterns = parse_anti_patterns_config(
        root, raw_ap, trust_level_valid, errors, allow_l2_with_clean_scopes=bool(clean_scopes)
    )
    raw_fl = data["file_limits"] if "file_limits" in data else None
    file_limits = parse_file_limits_config(
        root, raw_fl, trust_level_valid, errors, clean_scopes=clean_scopes
    )

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
        project_kind=project_kind,
        check_command=check_cmd,
        verify_cli=verify_cli,
        verify_skill=verify_skill,
        verify_skill_configured=verify_skill_configured,
        source_roots=source_roots,
        clean_scopes=clean_scopes,
        exclude_dirs=exclude_dirs,
        prose_files=prose_files,
        prose_max_bytes=prose_max_bytes,
        require_fresh_head=require_fresh_head,
        max_escape_hatches=max_escape_hatches,
        anti_patterns=anti_patterns,
        file_limits=file_limits,
        extra_escape_patterns=extra_patterns,
        forbidden_primitives=forbidden_primitives,
        boundary_rules=boundary_rules,
    )


def _should_skip_source_file(fpath: Path) -> bool:
    fname = fpath.name
    if fname == ".env" or fname.startswith(".env.") or fname in SKIPPED_FILENAMES:
        return True
    lower_name = fname.lower()
    if lower_name.endswith(".min.js") or lower_name.endswith(".min.css"):
        return True
    return fpath.suffix.lower() in SKIPPED_SUFFIXES


def _is_package_level_dir(root: Path, dir_path: Path) -> bool:
    try:
        parts = dir_path.relative_to(root).parts
    except ValueError:
        return False
    if not parts:
        return True
    if len(parts) == 1 and (parts[0] in CONTAINER_DIRS or parts[0] in WORKSPACE_PARENT_DIRS):
        return True
    return len(parts) == 2 and parts[0] in WORKSPACE_PARENT_DIRS


def collect_source_files(root: Path, cfg: GuardConfig) -> list[Path]:
    root = root.resolve()
    seen: set[str] = set()
    files: list[Path] = []
    for src_root in cfg.source_roots:
        if not src_root.exists():
            continue
        if src_root.is_file():
            if _should_skip_source_file(src_root):
                continue
            key = norm_key(src_root)
            if key not in seen:
                seen.add(key)
                files.append(src_root)
            continue
        for dirpath, dirnames, filenames in os.walk(src_root):
            pkg_level = _is_package_level_dir(root, Path(dirpath))
            dirnames[:] = sorted(
                d
                for d in dirnames
                if d not in cfg.exclude_dirs
                and not d.startswith(".git")
                and not (pkg_level and d in ROOT_ARTIFACT_DIRS)
            )
            for fname in sorted(filenames):
                fpath = Path(dirpath) / fname
                if _should_skip_source_file(fpath):
                    continue
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


def _is_silent_return_expr(expr: ast.expr | None) -> bool:
    if expr is None:
        return True
    if isinstance(expr, ast.Constant):
        return expr.value is None or expr.value == ""
    if isinstance(expr, (ast.List, ast.Tuple)):
        return len(expr.elts) == 0
    if isinstance(expr, ast.Dict):
        return len(expr.keys) == 0
    return False


def _is_broad_suppress_arg(arg: ast.expr) -> bool:
    if isinstance(arg, ast.Name) and arg.id in {"Exception", "BaseException"}:
        return True
    if isinstance(arg, ast.Tuple):
        return any(_is_broad_suppress_arg(elt) for elt in arg.elts)
    return False


def _scan_python_silent_catch(
    text: str, stripped_lines: list[str], rel_posix: str
) -> list[tuple[str, int, str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        hits: list[tuple[str, int, str]] = []
        for i, code in enumerate(stripped_lines):
            if not code.strip():
                continue
            if PY_SILENT_EXCEPT_SINGLE.match(code) or PY_BROAD_SUPPRESS.search(code):
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
        return hits

    suppress_names: set[str] = {"suppress"}
    contextlib_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "contextlib":
                    contextlib_aliases.add(alias.asname or "contextlib")
        elif isinstance(node, ast.ImportFrom) and node.module == "contextlib":
            for alias in node.names:
                if alias.name == "suppress":
                    suppress_names.add(alias.asname or "suppress")

    hit_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if len(node.body) == 1:
                stmt = node.body[0]
                is_silent = (
                    isinstance(stmt, ast.Pass)
                    or (
                        isinstance(stmt, ast.Expr)
                        and isinstance(stmt.value, ast.Constant)
                        and stmt.value.value is Ellipsis
                    )
                    or (isinstance(stmt, ast.Return) and _is_silent_return_expr(stmt.value))
                )
                if is_silent:
                    hit_lines.add(node.lineno)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                expr = item.context_expr
                if not isinstance(expr, ast.Call):
                    continue
                func = expr.func
                is_suppress_call = (
                    (isinstance(func, ast.Name) and func.id in suppress_names)
                    or (
                        isinstance(func, ast.Attribute)
                        and func.attr == "suppress"
                        and isinstance(func.value, ast.Name)
                        and func.value.id in contextlib_aliases
                    )
                )
                if is_suppress_call and any(_is_broad_suppress_arg(arg) for arg in expr.args):
                    hit_lines.add(node.lineno)

    return [(rel_posix, ln, "silent-catch") for ln in sorted(hit_lines)]


def _scrub_js_non_code(text: str) -> list[str]:
    """Blank out JS/TS comment text and string/template contents while preserving line numbers."""
    out: list[str] = []
    n = len(text)
    i = 0
    state = "normal"
    tmpl_brace_stack: list[int] = []

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if state == "line_comment":
            if ch == "\n":
                out.append("\n")
                state = "normal"
            else:
                out.append(" ")
            i += 1
            continue

        if state == "block_comment":
            if ch == "*" and nxt == "/":
                out.append("  ")
                i += 2
                state = "normal"
            elif ch == "\n":
                out.append("\n")
                i += 1
            else:
                out.append(" ")
                i += 1
            continue

        if state in ("single", "double"):
            q = "'" if state == "single" else '"'
            if ch == "\\":
                if nxt == "\n":
                    out.append(" \n")
                    i += 2
                elif nxt:
                    out.append("  ")
                    i += 2
                else:
                    out.append(" ")
                    i += 1
            elif ch == q:
                out.append(ch)
                i += 1
                state = "normal"
            elif ch == "\n":
                out.append("\n")
                i += 1
                state = "normal"
            else:
                out.append(" ")
                i += 1
            continue

        if state == "template":
            if ch == "\\":
                if nxt == "\n":
                    out.append(" \n")
                    i += 2
                elif nxt:
                    out.append("  ")
                    i += 2
                else:
                    out.append(" ")
                    i += 1
            elif ch == "`":
                out.append(ch)
                i += 1
                state = "normal"
            elif ch == "$" and nxt == "{":
                out.append("  ")
                i += 2
                tmpl_brace_stack.append(1)
                state = "normal"
            elif ch == "\n":
                out.append("\n")
                i += 1
            else:
                out.append(" ")
                i += 1
            continue

        if ch == "/" and nxt == "/":
            out.append("  ")
            i += 2
            state = "line_comment"
        elif ch == "/" and nxt == "*":
            out.append("  ")
            i += 2
            state = "block_comment"
        elif ch == "'":
            out.append(ch)
            i += 1
            state = "single"
        elif ch == '"':
            out.append(ch)
            i += 1
            state = "double"
        elif ch == "`":
            out.append(ch)
            i += 1
            state = "template"
        elif ch == "{" and tmpl_brace_stack:
            tmpl_brace_stack[-1] += 1
            out.append(ch)
            i += 1
        elif ch == "}" and tmpl_brace_stack:
            tmpl_brace_stack[-1] -= 1
            if tmpl_brace_stack[-1] == 0:
                tmpl_brace_stack.pop()
                out.append(" ")
                state = "template"
            else:
                out.append(ch)
            i += 1
        else:
            out.append(ch)
            i += 1

    return "".join(out).split(LF)


def _extract_js_brace_body(
    stripped_lines: list[str], start_line: int, open_end_col: int
) -> str | None:
    """Return whitespace-normalized body after '{' across up to 6 lines, or None if unclosed."""
    body_chars: list[str] = []
    depth = 1
    for idx_line in range(start_line, min(len(stripped_lines), start_line + 6)):
        seg = stripped_lines[idx_line]
        if idx_line == start_line:
            seg = seg[open_end_col:]
        for ch in seg:
            if ch == "{":
                depth += 1
                body_chars.append(ch)
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return " ".join("".join(body_chars).split())
                body_chars.append(ch)
            else:
                body_chars.append(ch)
        body_chars.append(" ")
    return None


def is_test_or_fixture_path(rel_posix: str) -> bool:
    parts = [p for p in rel_posix.split("/") if p]
    if any(part.lower() in TEST_FIXTURE_DIRS for part in parts[:-1]):
        return True
    fname = parts[-1].lower() if parts else ""
    is_py_test_prefix = fname.startswith("test_") and Path(fname).suffix in PY_EXTENSIONS
    return (
        is_py_test_prefix
        or fname == "conftest.py"
        or bool(TEST_FIXTURE_FILE.search(fname))
    )


def scan_anti_patterns_in_file(
    fpath: Path,
    rel_posix: str,
    text: str,
    stripped_lines: list[str],
    ap: AntiPatternsConfig,
) -> list[tuple[str, int, str]]:
    suffix = fpath.suffix.lower()
    if suffix not in CODE_EXTENSIONS:
        return []

    is_test_file = is_test_or_fixture_path(rel_posix)
    hits: list[tuple[str, int, str]] = []
    enabled = set(ap.enabled)

    if (
        not is_test_file
        and "silent-catch" in enabled
        and not is_anti_pattern_allowed(fpath, "silent-catch", ap)
    ):
        if suffix in PY_EXTENSIONS:
            hits.extend(_scan_python_silent_catch(text, stripped_lines, rel_posix))
        elif suffix in JS_EXTENSIONS:
            js_lines = _scrub_js_non_code(text)
            for i, code in enumerate(js_lines):
                if not code.strip():
                    continue
                found_silent = bool(
                    JS_PROMISE_CATCH_CONCISE.search(code) or JS_THEN_REJECT_CONCISE.search(code)
                )
                if not found_silent:
                    for pat in (JS_CATCH_OPEN, JS_PROMISE_CATCH_BLOCK_OPEN, JS_THEN_REJECT_BLOCK_OPEN):
                        for m in pat.finditer(code):
                            body = _extract_js_brace_body(js_lines, i, m.end())
                            if body is not None and (body == "" or JS_SILENT_BODY.match(body)):
                                found_silent = True
                                break
                        if found_silent:
                            break
                if found_silent:
                    hits.append((rel_posix, i + 1, "silent-catch"))

    if (
        not is_test_file
        and "blind-wait" in enabled
        and not is_anti_pattern_allowed(fpath, "blind-wait", ap)
    ):
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

    if (
        not is_test_file
        and "hardcoded-path" in enabled
        and not is_anti_pattern_allowed(fpath, "hardcoded-path", ap)
    ):
        for i, code in enumerate(stripped_lines):
            if code and any(pat.search(code) for pat in HARDCODED_PATH_PATTERNS):
                hits.append((rel_posix, i + 1, "hardcoded-path"))

    if (
        not is_test_file
        and ap.configured
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

    if (
        not is_test_file
        and "mock-in-prod" in enabled
        and not is_anti_pattern_allowed(fpath, "mock-in-prod", ap)
    ):
        for i, code in enumerate(stripped_lines):
            if not code.strip():
                continue
            matched = bool(MOCK_DATA_DECL.search(code) or MOCK_FALLBACK_EXPR.search(code))
            if not matched:
                for target in extract_imports(code):
                    if MOCK_IMPORT_DIR.search(normalize_import_target(target)):
                        matched = True
                        break
            if matched:
                hits.append((rel_posix, i + 1, "mock-in-prod"))

    return hits


def _collect_code_findings(root: Path, cfg: GuardConfig) -> dict:
    root = root.resolve()
    files = collect_source_files(root, cfg)
    escape_violations: list[tuple[str, int, str]] = []
    ap_hits: list[tuple[str, int, str]] = []
    oversize_violations: list[tuple[str, int]] = []
    seen_line_counts: dict[str, int] = {}
    primitive_errors: list[str] = []
    extra_ap_errors: list[str] = []
    boundary_errors: list[str] = []
    clean_scope_errors: list[str] = []
    clean_scope_file_counts: dict[str, int] = {}
    clean_scope_unique_files = 0

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
    all_escape_patterns = list(DEFAULT_ESCAPE_PATTERNS) + cfg.extra_escape_patterns

    decoded_files = 0
    for fpath in files:
        text = read_source_text(fpath)
        if text is None:
            continue
        decoded_files += 1
        rel_posix = fpath.relative_to(root).as_posix()
        lines = text.split(LF)
        stripped_lines = [strip_code_comments(line) for line in lines]
        matching_cs = [
            cs.relative_to(root).as_posix()
            for cs in cfg.clean_scopes
            if path_is_within(fpath, cs)
        ]
        if matching_cs:
            clean_scope_unique_files += 1
            for cs_rel in matching_cs:
                clean_scope_file_counts[cs_rel] = clean_scope_file_counts.get(cs_rel, 0) + 1

        # 1. Escape hatches & workaround comments
        file_escapes: list[tuple[int, str]] = []
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
                file_escapes.append((idx, matched_tag))

        # 2. Forbidden primitives & anti_patterns.extra_rules
        match_pattern_rules(
            fpath,
            rel_posix,
            stripped_lines,
            cfg.forbidden_primitives,
            compiled_globs,
            "forbidden_primitive",
            primitive_errors,
        )
        match_pattern_rules(
            fpath,
            rel_posix,
            stripped_lines,
            cfg.anti_patterns.extra_rules,
            ap_compiled_globs,
            "anti_pattern_rule",
            extra_ap_errors,
        )

        # 3. Built-in anti-patterns
        file_ap_hits = scan_anti_patterns_in_file(
            fpath, rel_posix, text, stripped_lines, cfg.anti_patterns
        )
        ap_hits.extend(file_ap_hits)

        # 4. File line limits
        file_line_count = 0
        file_oversize = False
        if (
            fpath.suffix.lower() in CODE_EXTENSIONS
            and not is_test_or_fixture_path(rel_posix)
            and not any(path_is_within(fpath, allow) for allow in cfg.file_limits.allow_paths)
        ):
            file_line_count = len(text.splitlines())
            if cfg.file_limits.configured:
                seen_line_counts[rel_posix] = file_line_count
                if file_line_count > cfg.file_limits.max_lines:
                    oversize_violations.append((rel_posix, file_line_count))
                    file_oversize = True
            elif matching_cs and file_line_count > cfg.file_limits.max_lines:
                file_oversize = True

        if matching_cs:
            for cs_rel in matching_cs:
                for ln, tag in file_escapes:
                    clean_scope_errors.append(
                        f"clean_scope '{cs_rel}' violation: escape hatch at {rel_posix}:{ln}[{tag}]"
                    )
                for _p, ln, cat in file_ap_hits:
                    clean_scope_errors.append(
                        f"clean_scope '{cs_rel}' violation: anti-pattern at {rel_posix}:{ln}[{cat}]"
                    )
                if file_oversize:
                    clean_scope_errors.append(
                        f"clean_scope '{cs_rel}' violation: oversize file '{rel_posix}' "
                        f"has {file_line_count} lines (> {cfg.file_limits.max_lines})"
                    )

        # 5. Boundary rules
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
                        boundary_errors.append(
                            f"boundary_rule '{rule.id}' at {rel_posix}:{idx} imports "
                            f"'{target}': {rule.message}"
                        )

    return {
        "files_scanned": decoded_files,
        "escape_violations": escape_violations,
        "ap_hits": ap_hits,
        "oversize_violations": oversize_violations,
        "seen_line_counts": seen_line_counts,
        "primitive_errors": primitive_errors,
        "extra_ap_errors": extra_ap_errors,
        "boundary_errors": boundary_errors,
        "clean_scope_errors": clean_scope_errors,
        "clean_scope_file_counts": clean_scope_file_counts,
        "clean_scope_unique_files": clean_scope_unique_files,
    }


def scan_sources(
    root: Path, cfg: GuardConfig, errors: list[str], warnings: list[str]
) -> dict[str, int]:
    findings = _collect_code_findings(root, cfg)
    root_resolved = root.resolve()
    missing_roots = [
        sr.relative_to(root_resolved).as_posix()
        for sr in cfg.source_roots
        if not sr.exists()
    ]
    if missing_roots:
        errors.append(
            ".guardrails/config.json: configured source_root does not exist: "
            + ", ".join(missing_roots)
        )
    elif findings["files_scanned"] == 0:
        errors.append(
            ".guardrails/config.json: source_roots matched 0 source files; "
            "check source_roots and exclude_dirs"
        )

    escape_violations = findings["escape_violations"]
    ap_hits = findings["ap_hits"]
    oversize_violations = findings["oversize_violations"]

    errors.extend(findings["primitive_errors"])
    errors.extend(findings["extra_ap_errors"])
    errors.extend(findings["boundary_errors"])
    clean_scope_file_counts = findings["clean_scope_file_counts"]
    for cs in cfg.clean_scopes:
        cs_rel = cs.relative_to(root_resolved).as_posix()
        if not cs.exists() or clean_scope_file_counts.get(cs_rel, 0) == 0:
            errors.append(
                f".guardrails/config.json: clean_scopes '{cs_rel}' matched 0 readable source files"
            )
    errors.extend(findings["clean_scope_errors"])

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

    found_oversize = len(oversize_violations)
    if cfg.file_limits.configured:
        fl_max = cfg.file_limits.max_allowed
        if cfg.file_limits.baseline_files_configured:
            bf = cfg.file_limits.baseline_files
            seen_counts = findings["seen_line_counts"]
            for rel_posix, ln_count in oversize_violations:
                if rel_posix in bf:
                    if ln_count > bf[rel_posix]:
                        errors.append(
                            f"oversize file '{rel_posix}' grew from {bf[rel_posix]} to {ln_count} lines; "
                            "split domain logic instead of growing a monolith"
                        )
                else:
                    errors.append(
                        f"new oversize file '{rel_posix}' is {ln_count} lines (> {cfg.file_limits.max_lines}); "
                        "keep modules under file_limits.max_lines instead of adding a new monolith"
                    )
            for rel_p, _ceiling in sorted(bf.items()):
                if not (root_resolved / rel_p).is_file():
                    warnings.append(
                        f"baselined oversize file '{rel_p}' no longer exists; "
                        "remove it from file_limits.baseline_files and lower max_allowed"
                    )
                elif rel_p in seen_counts and seen_counts[rel_p] <= cfg.file_limits.max_lines:
                    warnings.append(
                        f"oversize file '{rel_p}' shrunk to {seen_counts[rel_p]} lines "
                        f"(<= {cfg.file_limits.max_lines}); remove it from file_limits.baseline_files and lower max_allowed"
                    )
        if found_oversize > fl_max:
            sample = ", ".join(
                f"{p}:{ln} (>{cfg.file_limits.max_lines})" for p, ln in oversize_violations[:8]
            )
            more = f" (+{found_oversize - 8} more)" if found_oversize > 8 else ""
            errors.append(
                f"oversize files found ({found_oversize}) exceed file_limits.max_allowed "
                f"({fl_max}): {sample}{more}; split domain logic from UI/IO adapters "
                "instead of growing monolith files or raising max_allowed"
            )
        elif found_oversize < fl_max:
            warnings.append(
                f"oversize files dropped to {found_oversize} under ratchet {fl_max}; "
                f"lower file_limits.max_allowed to {found_oversize} in .guardrails/config.json"
            )

    return {
        "files_scanned": findings["files_scanned"],
        "escape_hatches": found_escapes,
        "anti_patterns": found_ap,
        "anti_pattern_rule_violations": len(findings["extra_ap_errors"]),
        "oversize_files": found_oversize,
        "primitive_violations": len(findings["primitive_errors"]),
        "boundary_violations": len(findings["boundary_errors"]),
        "clean_scope_files": findings["clean_scope_unique_files"],
        "clean_scope_violations": len(findings["clean_scope_errors"]),
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
    enforce_driver_verify = cfg.project_kind == "app" and not cfg.verify_skill_configured

    if enforce_driver_verify and cfg.verify_cli and not is_placeholder(cfg.verify_cli):
        fake_reason = classify_fake_verify_cli(cfg.verify_cli, cfg.check_command)
        if fake_reason:
            msg = (
                f".guardrails/config.json: verify_cli '{cfg.verify_cli}' {fake_reason}; "
                "provide a reusable user-scenario driver (or verify_skill), or set "
                '"project_kind": "library" for standalone libraries'
            )
            if cfg.trust_level_valid and cfg.trust_level in {"L1", "L2", "L3"}:
                errors.append(msg)
            else:
                warnings.append(msg)

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
            if cfg.trust_level_valid and cfg.trust_level == "L0":
                warnings.append(
                    ".guardrails/feature-map.md has no feature rows yet "
                    "(optional at L0; populate core entrypoints before L1)"
                )
            else:
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
            elif enforce_driver_verify and not is_placeholder(cli):
                row_fake = classify_fake_verify_cli(cli, cfg.check_command)
                if row_fake:
                    row_msg = (
                        f".guardrails/feature-map.md: '{name}' verify CLI '{cli}' {row_fake}; "
                        "point to a real scenario driver command"
                    )
                    if cfg.trust_level_valid and cfg.trust_level in {"L1", "L2", "L3"} and prio_norm == "core":
                        errors.append(row_msg)
                    else:
                        warnings.append(row_msg)
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


def _pm_run(pm: str, rel_dir: str, script: str) -> str:
    if not rel_dir:
        return f"{pm} run {script}"
    if pm == "pnpm":
        return f"pnpm --dir {rel_dir} run {script}"
    if pm == "npm":
        return f"npm --prefix {rel_dir} run {script}"
    if pm == "bun":
        return f"bun run --cwd {rel_dir} {script}"
    return f"{pm} --cwd {rel_dir} run {script}"


def _pm_vitest_run(pm: str, rel_dir: str) -> str:
    if not rel_dir:
        return {
            "npm": "npx vitest run",
            "pnpm": "pnpm exec vitest run",
            "yarn": "yarn vitest run",
            "bun": "bunx vitest run",
        }.get(pm, "npx vitest run")
    if pm == "npm":
        return f"npm --prefix {rel_dir} run test -- --run"
    if pm == "pnpm":
        return f"pnpm --dir {rel_dir} exec vitest run"
    if pm == "bun":
        return f"bun run --cwd {rel_dir} vitest run"
    return f"{pm} --cwd {rel_dir} vitest run"


def _has_stack_manifest(dir_path: Path) -> bool:
    for fname in ("package.json", "pyproject.toml", "pytest.ini", "setup.py", "Cargo.toml", "go.mod"):
        if (dir_path / fname).is_file():
            return True
    tests_dir = dir_path / "tests"
    return tests_dir.is_dir() and any(tests_dir.glob("*.py"))


def _detect_dir_stack_and_check(dir_path: Path, rel_dir: str, root: Path) -> tuple[list[str], str, str]:
    stacks: list[str] = []
    pkg_manager = ""
    dir_cmds: list[str] = []

    pkg_path = dir_path / "package.json"
    if pkg_path.is_file():
        node_cmd = ""
        stacks.append("node")
        if (dir_path / "tsconfig.json").is_file():
            stacks.append("typescript")
        search_bases = [dir_path, root] if rel_dir else [dir_path]
        for base in search_bases:
            if (base / "pnpm-lock.yaml").is_file():
                pkg_manager = "pnpm"
                break
            if (base / "package-lock.json").is_file() or (base / "npm-shrinkwrap.json").is_file():
                pkg_manager = "npm"
                break
            if (base / "yarn.lock").is_file():
                pkg_manager = "yarn"
                break
            if (base / "bun.lockb").is_file() or (base / "bun.lock").is_file():
                pkg_manager = "bun"
                break
        if not pkg_manager:
            pkg_manager = "npm"
        try:
            pkg_data = json.loads(read_utf8_lf(pkg_path))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pkg_data = {}
        scripts = pkg_data.get("scripts") if isinstance(pkg_data, dict) else None
        if isinstance(scripts, dict):
            check_script = scripts.get("check")
            if isinstance(check_script, str) and check_script.strip():
                node_cmd = _pm_run(pkg_manager, rel_dir, "check")
            else:
                parts: list[str] = []
                for key in ("lint", "typecheck", "test"):
                    raw = scripts.get(key)
                    if not isinstance(raw, str) or not raw.strip():
                        continue
                    if key == "test":
                        if "no test specified" in raw.casefold():
                            continue
                        if raw.strip() == "vitest":
                            parts.append(_pm_vitest_run(pkg_manager, rel_dir))
                            continue
                    parts.append(_pm_run(pkg_manager, rel_dir, key))
                if parts:
                    node_cmd = " && ".join(parts)
                elif isinstance(scripts.get("build"), str) and scripts["build"].strip():
                    node_cmd = _pm_run(pkg_manager, rel_dir, "build")
        if not node_cmd and (dir_path / "tsconfig.json").is_file():
            if not rel_dir:
                node_cmd = (
                    "bunx tsc --noEmit"
                    if pkg_manager == "bun"
                    else ("pnpm exec tsc --noEmit" if pkg_manager == "pnpm" else "npx tsc --noEmit")
                )
            elif pkg_manager == "pnpm":
                node_cmd = f"pnpm --dir {rel_dir} exec tsc --noEmit"
            elif pkg_manager == "bun":
                node_cmd = f"bun run --cwd {rel_dir} tsc --noEmit"
            elif pkg_manager == "yarn":
                node_cmd = f"yarn --cwd {rel_dir} tsc --noEmit"
            else:
                node_cmd = f"npm --prefix {rel_dir} exec --no -- tsc -p {rel_dir}/tsconfig.json --noEmit"
        if node_cmd:
            dir_cmds.append(node_cmd)

    py_has_tests = (dir_path / "tests").is_dir() and any((dir_path / "tests").glob("*.py"))
    pyproject_path = dir_path / "pyproject.toml"
    if (
        pyproject_path.is_file()
        or (dir_path / "pytest.ini").is_file()
        or (dir_path / "setup.py").is_file()
        or py_has_tests
    ):
        stacks.append("python")
        has_pytest = (dir_path / "pytest.ini").is_file()
        if not has_pytest and pyproject_path.is_file():
            try:
                has_pytest = "pytest" in read_utf8_lf(pyproject_path).casefold()
            except UnicodeDecodeError:
                has_pytest = False
        py_cmd = ""
        if not rel_dir:
            if (dir_path / "uv.lock").is_file() and has_pytest:
                py_cmd = "uv run pytest"
            elif has_pytest:
                py_cmd = "python -X utf8 -m pytest"
            elif (dir_path / "tests").is_dir():
                py_cmd = 'python -X utf8 -B -m unittest discover -s tests -p "test_*.py"'
            elif not dir_cmds:
                py_cmd = "python -X utf8 -m unittest"
        else:
            if (dir_path / "uv.lock").is_file() and has_pytest:
                py_cmd = f"uv --directory {rel_dir} run pytest"
            elif (root / "uv.lock").is_file() and has_pytest:
                py_cmd = f"uv run pytest {rel_dir}"
            elif has_pytest:
                py_cmd = f"python -X utf8 -m pytest {rel_dir}"
            elif (dir_path / "tests").is_dir():
                py_cmd = f'python -X utf8 -B -m unittest discover -s {rel_dir}/tests -p "test_*.py"'
            else:
                py_cmd = f"python -X utf8 -m unittest discover -s {rel_dir}"
        if py_cmd:
            dir_cmds.append(py_cmd)

    if (dir_path / "Cargo.toml").is_file():
        stacks.append("rust")
        dir_cmds.append("cargo test" if not rel_dir else f"cargo test --manifest-path {rel_dir}/Cargo.toml")

    if (dir_path / "go.mod").is_file():
        stacks.append("go")
        dir_cmds.append("go test ./..." if not rel_dir else f"go -C {rel_dir} test ./...")

    return stacks, pkg_manager, " && ".join(dir_cmds)


def _manifest_referenced_script_dirs(root: Path) -> list[str]:
    refs: list[str] = []
    pkg_path = root / "package.json"
    if pkg_path.is_file():
        try:
            pkg_data = json.loads(read_utf8_lf(pkg_path))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pkg_data = {}
        if isinstance(pkg_data, dict):
            for key in ("scripts", "bin"):
                val = pkg_data.get(key)
                if isinstance(val, str):
                    refs.append(val)
                elif isinstance(val, dict):
                    refs.extend(str(v) for v in val.values() if isinstance(v, str))
    pyproj_path = root / "pyproject.toml"
    if pyproj_path.is_file():
        try:
            refs.append(read_utf8_lf(pyproj_path))
        except UnicodeDecodeError:
            pass
    blob = "\n".join(refs).replace("\\", "/")
    found: list[str] = []
    for candidate in ("scripts", "bin"):
        if (root / candidate).is_dir() and f"{candidate}/" in blob:
            found.append(candidate)
    return found


def detect_project_stack(root: Path, override_check_cmd: str = "") -> dict:
    source_roots = [d for d in DIRECT_SOURCE_ROOTS if (root / d).is_dir()]
    manifest_targets: list[tuple[str, Path]] = []

    for wp in WORKSPACE_PARENT_DIRS:
        wp_dir = root / wp
        if not wp_dir.is_dir():
            continue
        matched_any = False
        children = sorted(
            (
                p
                for p in wp_dir.iterdir()
                if p.is_dir()
                and p.name not in DEFAULT_EXCLUDE_DIRS
                and p.name not in ROOT_ARTIFACT_DIRS
                and not p.name.startswith(".git")
            ),
            key=lambda p: p.name,
        )
        for ch in children:
            rel_c = f"{wp}/{ch.name}"
            nested = [f"{rel_c}/{sub}" for sub in NESTED_CODE_SUBDIRS if (ch / sub).is_dir()]
            if _has_stack_manifest(ch):
                source_roots.extend(nested if nested else [rel_c])
                manifest_targets.append((rel_c, ch))
                matched_any = True
            elif _dir_has_code_files(ch):
                source_roots.extend(nested if nested else [rel_c])
                matched_any = True
        if not matched_any and _dir_has_code_files(wp_dir):
            source_roots.append(wp)

    for container in CONTAINER_DIRS:
        c_dir = root / container
        if not c_dir.is_dir():
            continue
        nested = [f"{container}/{sub}" for sub in NESTED_CODE_SUBDIRS if (c_dir / sub).is_dir()]
        source_roots.extend(nested if nested else [container])
        if _has_stack_manifest(c_dir):
            manifest_targets.append((container, c_dir))

    for ref_dir in _manifest_referenced_script_dirs(root):
        if ref_dir not in source_roots:
            source_roots.append(ref_dir)

    source_roots = list(dict.fromkeys(source_roots))
    allow_paths: list[str] = []
    if not source_roots:
        source_roots = ["."]

    root_stacks, pkg_manager, root_cmd = _detect_dir_stack_and_check(root, "", root)
    stacks = list(root_stacks)
    sub_results: list[tuple[str, list[str], str]] = []
    for rel_dir, c_dir in manifest_targets:
        s_stacks, s_pm, s_cmd = _detect_dir_stack_and_check(c_dir, rel_dir, root)
        for st in s_stacks:
            if st not in stacks:
                stacks.append(st)
        if not pkg_manager and s_pm:
            pkg_manager = s_pm
        sub_results.append((rel_dir, s_stacks, s_cmd))

    cmds: list[str] = []
    if root_cmd and not (
        manifest_targets
        and root_cmd == "python -X utf8 -m unittest"
        and not (root / "tests").is_dir()
    ):
        cmds.append(root_cmd)
    for rel_dir, _s_stacks, s_cmd in sub_results:
        if not s_cmd or s_cmd in cmds:
            continue
        if not cmds or not root_cmd:
            cmds.append(s_cmd)
            continue
        if rel_dir in root_cmd:
            continue
        cmds.append(s_cmd)

    detected_check_cmd = " && ".join(cmds)
    final_cmd = override_check_cmd.strip() or detected_check_cmd
    return {
        "stacks": stacks,
        "package_manager": pkg_manager,
        "source_roots": source_roots,
        "allow_paths": allow_paths,
        "check_command": final_cmd,
    }


def _dir_has_code_files(base: Path) -> bool:
    for _dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS and not d.startswith(".git")]
        for fname in filenames:
            if Path(fname).suffix.lower() in CODE_EXTENSIONS:
                return True
    return False


def scan_baseline(
    root: Path,
    max_lines: int = DEFAULT_MAX_FILE_LINES,
    override_check_cmd: str = "",
) -> dict:
    root = root.resolve()
    if not root.is_dir():
        return {
            "root": str(root),
            "guard_status": "invalid",
            "errors": [f"target root does not exist or is not a directory: {root}"],
            "warnings": [],
        }
    if not is_int_strict(max_lines) or max_lines < 1:
        return {
            "root": str(root),
            "guard_status": "invalid",
            "errors": ["--max-lines must be a positive integer"],
            "warnings": [],
        }

    detected = detect_project_stack(root, override_check_cmd)
    cfg = GuardConfig(
        trust_level="L0",
        trust_level_valid=True,
        project_kind="app",
        check_command=detected["check_command"] or "TODO",
        verify_cli="",
        verify_skill=None,
        verify_skill_configured=False,
        source_roots=[normalize_rel_path(root, sr) for sr in detected["source_roots"]],
        clean_scopes=[],
        exclude_dirs=set(STACK_DETECT_EXCLUDES),
        prose_files=[root / "AGENTS.md"],
        prose_max_bytes=DEFAULT_PROSE_MAX_BYTES,
        require_fresh_head=False,
        max_escape_hatches=0,
        anti_patterns=AntiPatternsConfig(
            configured=True,
            max_allowed=0,
            enabled=list(ANTI_PATTERN_CATEGORIES),
            allow_paths=[normalize_rel_path(root, a) for a in detected["allow_paths"]],
            allow_by_category={},
            extra_rules=[],
        ),
        file_limits=FileLimitsConfig(
            configured=True,
            max_lines=max_lines,
            max_allowed=0,
            allow_paths=[],
            baseline_files={},
            baseline_files_configured=False,
        ),
    )
    findings = _collect_code_findings(root, cfg)
    escape_violations = findings["escape_violations"]
    ap_hits = findings["ap_hits"]
    oversize_violations = findings["oversize_violations"]
    by_cat: dict[str, int] = {cat: 0 for cat in ANTI_PATTERN_CATEGORIES}
    for _p, _ln, cat in ap_hits:
        by_cat[cat] = by_cat.get(cat, 0) + 1

    warnings: list[str] = []
    if not detected["check_command"]:
        warnings.append(
            "no check_command auto-detected; pass --check-command \"<cmd>\" before --init"
        )
    if (
        detected["source_roots"] != ["."]
        and (root / "scripts").is_dir()
        and "scripts" not in detected["source_roots"]
        and _dir_has_code_files(root / "scripts")
    ):
        warnings.append(
            "unscanned code directory 'scripts' found; add 'scripts' to source_roots if it ships operational code"
        )

    legacy_found = [p.as_posix() for p in LEGACY_V1_PATHS if (root / p).exists()]
    return {
        "root": str(root),
        "guard_status": "baseline_scan",
        "existing_guardrails": (root / GUARD_DIR).exists(),
        "legacy_paths": legacy_found,
        "detected": detected,
        "baseline": {
            "files_scanned": findings["files_scanned"],
            "escape_hatches": len(escape_violations),
            "escape_hatch_samples": [f"{p}:{ln}[{tag}]" for p, ln, tag in escape_violations[:8]],
            "anti_patterns": len(ap_hits),
            "anti_pattern_by_category": by_cat,
            "anti_pattern_samples": [f"{p}:{ln}[{cat}]" for p, ln, cat in ap_hits[:8]],
            "oversize_files": len(oversize_violations),
            "oversize_map": {p: ln for p, ln in oversize_violations},
            "oversize_samples": [f"{p}:{ln}" for p, ln in oversize_violations[:8]],
            "max_lines": max_lines,
        },
        "errors": [],
        "warnings": warnings,
    }


def init_guardrails(
    root: Path,
    max_lines: int = DEFAULT_MAX_FILE_LINES,
    override_check_cmd: str = "",
    run_check: bool = False,
) -> dict:
    root = root.resolve()
    if not root.is_dir():
        return {
            "root": str(root),
            "guard_status": "invalid",
            "errors": [f"target root does not exist or is not a directory: {root}"],
            "warnings": [],
        }
    if not is_int_strict(max_lines) or max_lines < 1:
        return {
            "root": str(root),
            "guard_status": "invalid",
            "errors": ["--max-lines must be a positive integer"],
            "warnings": [],
        }
    guard_dir = root / GUARD_DIR
    if guard_dir.exists():
        return {
            "root": str(root),
            "guard_status": "invalid",
            "errors": [
                "cannot --init: .guardrails/ already exists; edit .guardrails/config.json directly"
            ],
            "warnings": [],
        }
    legacy_found = [p.as_posix() for p in LEGACY_V1_PATHS if (root / p).exists()]
    if legacy_found:
        return {
            "root": str(root),
            "guard_status": "invalid",
            "legacy_paths": legacy_found,
            "errors": [
                f"cannot --init: legacy v1 state detected ({', '.join(legacy_found)}); "
                "migrate per references/06-repo-guard-contract.md"
            ],
            "warnings": [],
        }

    scan = scan_baseline(root, max_lines=max_lines, override_check_cmd=override_check_cmd)
    if scan.get("errors"):
        return scan
    detected = scan["detected"]
    baseline = scan["baseline"]
    scan_warnings = list(scan.get("warnings", []))
    if baseline["files_scanned"] == 0:
        return {
            "root": str(root),
            "guard_status": "invalid",
            "detected": detected,
            "baseline": baseline,
            "errors": [
                "cannot --init: source_roots matched 0 readable source files; "
                "add code or check source_roots"
            ],
            "warnings": scan_warnings,
        }
    cmd_candidate = detected.get("check_command", "")
    if not cmd_candidate or is_placeholder(cmd_candidate):
        return {
            "root": str(root),
            "guard_status": "invalid",
            "detected": detected,
            "baseline": baseline,
            "errors": [
                'cannot --init without a runnable check_command; re-run with --check-command "<cmd>"'
            ],
            "warnings": scan_warnings,
        }

    cfg_obj = {
        "guardrails_version": GUARDRAILS_VERSION,
        "trust_level": "L0",
        "check_command": cmd_candidate,
        "verify_cli": "",
        "source_roots": detected["source_roots"],
        "exclude_dirs": sorted(STACK_DETECT_EXCLUDES),
        "prose_files": ["AGENTS.md"],
        "prose_max_bytes": DEFAULT_PROSE_MAX_BYTES,
        "require_fresh_head": False,
        "escape_hatches": {
            "max_allowed": baseline["escape_hatches"],
            "extra_patterns": [],
        },
        "anti_patterns": {
            "max_allowed": baseline["anti_patterns"],
            "enabled": list(ANTI_PATTERN_CATEGORIES),
            "allow_paths": detected["allow_paths"],
            "allow_by_category": {},
            "extra_rules": [],
        },
        "file_limits": {
            "max_lines": max_lines,
            "max_allowed": baseline["oversize_files"],
            "allow_paths": [],
            "baseline_files": dict(baseline["oversize_map"]),
        },
        "forbidden_primitives": [],
        "boundary_rules": [],
    }
    feature_map_text = LF.join([
        "# Feature Map",
        "",
        "| Feature | Entrypoint | Verify CLI | Artifact | Priority |",
        "| --- | --- | --- | --- | --- |",
        "",
        "~~~markdown",
        "<!-- Example row (replace with real core features before upgrading to L1):",
        "| 核心功能名 | `python -m src.app` | `python tools/verify.py core` | `artifacts/core.txt` | core |",
        "-->",
        "~~~",
        "",
    ])

    try:
        guard_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        return {
            "root": str(root),
            "guard_status": "invalid",
            "errors": [
                "cannot --init: .guardrails/ already exists; edit .guardrails/config.json directly"
            ],
            "warnings": [],
        }
    with (guard_dir / "config.json").open("w", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(cfg_obj, ensure_ascii=False, indent=2) + LF)
    with (guard_dir / "feature-map.md").open("w", encoding="utf-8", newline="") as handle:
        handle.write(feature_map_text)

    report = inspect_repo(root, run_check=run_check)
    for warn in scan_warnings:
        if "no check_command auto-detected" in warn:
            continue
        if warn not in report["warnings"]:
            report["warnings"].append(warn)
    report["initialized_files"] = [".guardrails/config.json", ".guardrails/feature-map.md"]
    report["detected"] = detected
    return report


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
                "no .guardrails/ found; run --scan / --init or start from references/01-intent-and-invariants.md"
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

    root_resolved = root.resolve()
    clean_scope_rels = (
        [cs.relative_to(root_resolved).as_posix() for cs in cfg.clean_scopes]
        if cfg
        else []
    )
    return {
        "root": str(root),
        "guard_status": "invalid" if errors else "ready",
        "trust_level": cfg.trust_level if cfg else "",
        "project_kind": cfg.project_kind if cfg else "app",
        "require_fresh_head": cfg.require_fresh_head if cfg else False,
        "max_escape_hatches": cfg.max_escape_hatches if cfg else None,
        "clean_scopes": clean_scope_rels,
        "anti_patterns_config": (
            {
                "configured": cfg.anti_patterns.configured,
                "max_allowed": cfg.anti_patterns.max_allowed,
                "enabled": cfg.anti_patterns.enabled,
            }
            if cfg
            else None
        ),
        "file_limits_config": (
            {
                "configured": cfg.file_limits.configured,
                "max_lines": cfg.file_limits.max_lines,
                "max_allowed": cfg.file_limits.max_allowed,
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
    if status == "baseline_scan":
        det = report.get("detected") or {}
        base = report.get("baseline") or {}
        lines = [
            f"baseline_scan | stacks={','.join(det.get('stacks') or ['unknown'])} | "
            f"source_roots={','.join(det.get('source_roots') or [])} | "
            f"check_command={det.get('check_command') or '(none)'}",
            f"  files_scanned={base.get('files_scanned', 0)} "
            f"escape_hatches={base.get('escape_hatches', 0)} "
            f"anti_patterns={base.get('anti_patterns', 0)} "
            f"oversize_files={base.get('oversize_files', 0)} "
            f"(max_lines={base.get('max_lines', DEFAULT_MAX_FILE_LINES)})",
        ]
        by_cat = base.get("anti_pattern_by_category") or {}
        non_zero = ", ".join(f"{k}={v}" for k, v in by_cat.items() if v)
        if non_zero:
            lines.append(f"  anti_pattern_by_category: {non_zero}")
        if base.get("escape_hatch_samples"):
            lines.append(f"  escape_samples: {', '.join(base['escape_hatch_samples'])}")
        if base.get("anti_pattern_samples"):
            lines.append(f"  anti_pattern_samples: {', '.join(base['anti_pattern_samples'])}")
        if base.get("oversize_samples"):
            lines.append(f"  oversize_samples: {', '.join(base['oversize_samples'])}")
        for warn in report.get("warnings") or []:
            lines.append(f"WARN  {warn}")
        for err in report.get("errors") or []:
            lines.append(f"ERROR {err}")
        lines.append(
            f"{len(report.get('errors') or [])} error(s), {len(report.get('warnings') or [])} warning(s)"
        )
        return "\n".join(lines)

    lines = []
    if report.get("initialized_files"):
        lines.append(f"initialized: {', '.join(report['initialized_files'])}")
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
        fl_cfg = report.get("file_limits_config") or {}
        fl_found = scan.get("oversize_files", 0)
        if fl_cfg.get("configured") or fl_found > 0:
            lines.append(
                f"  file_limits: oversize={fl_found}/{fl_cfg.get('max_allowed', 0)} "
                f"(max_lines={fl_cfg.get('max_lines', DEFAULT_MAX_FILE_LINES)})"
            )
        clean_scopes_list = report.get("clean_scopes") or []
        if clean_scopes_list:
            lines.append(
                f"  clean_scopes: {', '.join(clean_scopes_list)} "
                f"(files={scan.get('clean_scope_files', 0)}, "
                f"violations={scan.get('clean_scope_violations', 0)})"
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
    parser.add_argument(
        "--scan",
        action="store_true",
        help="scan project stack and debt baseline without creating or modifying .guardrails/",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="initialize L0 .guardrails/ skeleton locked to current baseline counts",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_MAX_FILE_LINES,
        help=f"source file line limit threshold for --scan/--init (default: {DEFAULT_MAX_FILE_LINES})",
    )
    parser.add_argument(
        "--check-command",
        default="",
        help="explicit check_command override when running --scan or --init",
    )
    args = parser.parse_args(argv)
    if args.scan and args.init:
        parser.error("--scan and --init cannot be used together")
    if args.scan and (args.run_check or args.check_head):
        parser.error("--scan is read-only and cannot be combined with --run-check or --check-head")
    if args.init and args.check_head:
        parser.error("--init cannot be combined with --check-head; commit .guardrails/ and verification.md first")

    root = Path(args.root)
    if args.scan:
        report = scan_baseline(root, max_lines=args.max_lines, override_check_cmd=args.check_command)
    elif args.init:
        report = init_guardrails(
            root,
            max_lines=args.max_lines,
            override_check_cmd=args.check_command,
            run_check=args.run_check,
        )
    else:
        report = inspect_repo(root, run_check=args.run_check, check_head=args.check_head)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_human(report))
    return 1 if (report["guard_status"] == "invalid" or report.get("errors")) else 0


if __name__ == "__main__":
    sys.exit(main())
