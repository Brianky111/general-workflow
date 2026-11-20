#!/usr/bin/env python3
"""Consistency checks for the Codebase-First workflow skill package.

Validates the skill's own contract: Reference Map, reachability from SKILL.md,
Inverse Trust Pyramid order, policy section anchors, single-authority guards,
anti-restatement trust-ladder check, scripts, budgets, and frozen archives.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
import sync_vendor  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_VERSIONS = ("general-workflow-v0.12.0", "general-workflow-v1.10.1")


class Tree(NamedTuple):
    """One workflow tree: root plus the active and archived paths."""

    root: Path
    skill: Path
    refs: Path
    archives: tuple[Path, ...]

    @classmethod
    def at(cls, root: Path) -> "Tree":
        root = root.resolve()
        return cls(
            root,
            root / "SKILL.md",
            root / "references",
            tuple(root / "archive" / version for version in ARCHIVE_VERSIONS),
        )


EXPECTED_REFERENCES = {
    "00-router.md",
    "01-intent-and-invariants.md",
    "02-codebase-guardrails.md",
    "03-verification-and-artifacts.md",
    "04-correction-and-gardening.md",
    "05-outer-loop-factory.md",
    "06-repo-guard-contract.md",
}

# Pinned by BudgetContractTests in tests/test_check_consistency.py so raising a
# budget to absorb duplicated prose requires changing two files with rationale.
SIZE_BUDGETS = {
    "SKILL.md": 6_500,
    "00-router.md": 7_500,
}
REFERENCE_BUDGET = 12_000
BUDGET_WARN = 0.90
MIN_BODY_CHARS = 30
MIN_GATE_CHARS = 60
CRLF = "\r\n"
CR = "\r"
LF = "\n"

REFERENCE_NAME = re.compile(r"\b\d{2}[a-z]?-[a-z0-9][a-z0-9-]*\.md\b")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SCRIPT_PATH = re.compile(r"scripts/[A-Za-z0-9_./-]+\.py")
FRONTMATTER_FIELD = re.compile(r"(?m)^([a-z][a-z0-9_-]*):\s*(.+?)\s*$")

POLICY_ANCHORS: dict[str, tuple[str, ...]] = {
    "SKILL.md": (
        "## 使用边界",
        "## 必须先做的事",
        "## 信任倒金字塔",
        "1. 代码库与 API 设计",
        "2. 静态分析与可执行检查",
        "3. 运行时与形式化验证",
        "4. 极薄文档与规则",
        "## 核心原则",
        "## 五条工作循环",
        "## 默认响应形状",
        "00-router.md",
    ),
    "00-router.md": (
        "## 第一次判断",
        '--root "<目标项目绝对路径>" --json',
        "legacy_v1",
        "## 信任层级（L0–L3）",
        "## 路由表",
        "## 内置 pstack 专项技能调度",
        "## 全局停止条件",
    ),
    "01-intent-and-invariants.md": (
        "## 为什么只留一页意图合同",
        "## 意图与不变量模板",
        "configurable_params",
        "## 垂直可演示切片与决策分工",
        "## 接手已有仓库（Brownfield 起步）",
        "max_allowed",
        "## 意图门禁",
    ),
    "02-codebase-guardrails.md": (
        "## 目录即上下文",
        "## 业务层禁用高分寸感原语",
        "## 反过度工程、反防御性吞错与反硬编码",
        "## 根因导向的自定义 Lint",
        "## 注释与逃生舱策略",
        "## 护栏门禁",
    ),
    "03-verification-and-artifacts.md": (
        "## 为什么审行为产物而不是逐行审 diff",
        "## 用户视角 Feature Map",
        "## 复用型验证 CLI 与调试通道",
        "## 行为产物与新鲜度门禁",
        "## 深度验证：PBT 与形式化验证",
        "## 验证门禁",
    ),
    "04-correction-and-gardening.md": (
        "## 倒金字塔纠错阶梯",
        "## 历史错误聚类与旧错例证伪（/correct 闭环）",
        "## 反深潜熔断与停放区（Anti-Rabbit-Hole）",
        "## 主动除草与棘轮协议",
        "## AGENTS.md 瘦身规则",
        "## 除草门禁",
    ),
    "05-outer-loop-factory.md": (
        "## 先内循环，再外循环",
        "## 成熟度阶梯（L0–L3）",
        "## 不可逆边界的永久人工门禁",
        "## 真实质量指标（不只看 PR 数量）",
        "## 外循环门禁",
    ),
    "06-repo-guard-contract.md": (
        "## .guardrails/ 目录布局",
        "## config.json 契约",
        "verify_skill",
        "anti_patterns",
        "## feature-map.md 与 verification.md 格式",
        "## 运行 scripts/repo_guard.py",
        "## 从 v1.x 状态目录迁移",
        "## 检查边界",
        "## 契约门禁",
    ),
}

EXCLUSIVE_PHRASES: dict[str, tuple[str, tuple[str, ...]]] = {
    "02-codebase-guardrails.md": (
        "注释与逃生舱策略",
        (
            "默认禁止解释 workaround 的注释",
            "99% 的解释性注释只会过时并成为坏样例的通行证",
            "不得用 lint-disable、noqa 或 @ts-ignore 绕过检查",
            "注释不是可执行约束，能写成类型、API 或 lint 就删掉注释",
        ),
    ),
    "03-verification-and-artifacts.md": (
        "行为产物与新鲜度门禁",
        (
            "每条核心验证必须产出可复查的行为产物",
            "视觉或复杂交互优先交录屏、截图或用户视角状态图",
            "验证记录必须锚定不可变 commit，代码改动后旧绿灯即失效",
            "禁止用 HEAD、main 或 later 冒充验证锚点",
        ),
    ),
    "04-correction-and-gardening.md": (
        "倒金字塔纠错阶梯",
        (
            "纠错按倒金字塔从上到下尝试，最后才写 AGENTS.md",
            "第一步：收窄或重写 API，让错误写法在结构上不可表达",
            "第二步：加一条带根因修复提示的静态检查或依赖规则",
            "第三步：清理仓库里同源旧坏样例，阻止后续 Agent 模仿",
            "第四步：补运行时验证、PBT 或形式化不变量",
            "第五步：只有无法编码的主观判断才写入极简 AGENTS.md",
        ),
    ),
    "05-outer-loop-factory.md": (
        "外循环成熟度阶梯",
        (
            "L0 低信任：尚未建成确定性护栏，禁止并行多 Agent 与自动合入",
            "L1 产物审查内循环：确定性检查全绿且核心功能具备 Feature Map 与行为产物，人工审产物不逐行审 diff",
            "L2 发版探索外循环：逃生舱清零后，发版或合入后自动启动探索 Agent 模拟真实用户 Fuzz 并提附带录屏的修复 PR",
            "L3 高信任自动合入：验证必须锚定当前 HEAD，低风险产品修复按规则自动合入，不可逆边界仍保留人工门禁",
        ),
    ),
}

TRUST_LADDER_OWNER = "05-outer-loop-factory.md"
TRUST_LEVEL_TOKEN = re.compile(r"(?<![0-9A-Za-z])L[0-3](?![0-9A-Za-z])")
TRUST_GATE_VERBS = (
    "禁止", "必须", "允许", "要求", "清零", "自动合入", "探索", "锚定", "人工",
)
TRUST_REACH = 32
TRUST_DISTINCT_MIN = 3


def reference_mentions(text: str) -> set[str]:
    """Return reference-looking filenames mentioned in text."""
    return set(REFERENCE_NAME.findall(text))


def read_text(tree: Tree, path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(tree.root)}")
        return ""
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"not UTF-8: {path.relative_to(tree.root)} ({exc})")
        return ""
    return text.replace(CRLF, LF).replace(CR, LF)


def check_frontmatter(text: str, errors: list[str]) -> None:
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
        return
    closing = text.find("\n---", 4)
    if closing < 0:
        errors.append("SKILL.md frontmatter has no closing delimiter")
        return
    block = text[4:closing]
    fields = {name: value for name, value in FRONTMATTER_FIELD.findall(block)}
    if fields.get("name") != "general-workflow":
        errors.append("SKILL.md frontmatter name must be general-workflow")
    if not fields.get("description"):
        errors.append("SKILL.md frontmatter description is empty")


def check_reference_map(
    skill_text: str, actual: set[str], errors: list[str]
) -> tuple[set[str], int]:
    match = re.search(r"(?ms)^## Reference Map\s*\n(.*?)(?=^## |\Z)", skill_text)
    if not match:
        errors.append("SKILL.md has no ## Reference Map section")
        return set(), len(skill_text)
    mapped = reference_mentions(match.group(1))
    for name in sorted(mapped - actual):
        errors.append(f"Reference Map lists missing file: {name}")
    for name in sorted(actual - mapped):
        errors.append(f"references/{name} is not listed in the Reference Map")
    return mapped, match.start()


def check_reachability(
    skill_text: str,
    texts: dict[str, str],
    actual: set[str],
    map_start: int,
    errors: list[str],
) -> None:
    frontier = reference_mentions(skill_text[:map_start]) & actual
    reachable: set[str] = set()
    while frontier:
        name = frontier.pop()
        if name in reachable:
            continue
        reachable.add(name)
        frontier |= (reference_mentions(texts.get(name, "")) & actual) - reachable
    for name in sorted(actual - reachable):
        errors.append(f"references/{name} is unreachable from active router/rules")


def check_pyramid_order(skill_text: str, router_text: str, errors: list[str]) -> None:
    layers = (
        "1. 代码库与 API 设计",
        "2. 静态分析与可执行检查",
        "3. 运行时与形式化验证",
        "4. 极薄文档与规则",
    )
    positions: list[int] = []
    for layer in layers:
        pos = skill_text.find(layer)
        if pos < 0:
            errors.append(f"SKILL.md is missing trust pyramid layer: {layer}")
        positions.append(pos)
    present = [pos for pos in positions if pos >= 0]
    if present and present != sorted(present):
        errors.append("SKILL.md trust pyramid layers are out of order")
    for level in ("L0", "L1", "L2", "L3"):
        if level not in router_text:
            errors.append(f"router is missing trust level: {level}")


def check_mentions(
    texts: dict[str, str], actual: set[str], errors: list[str]
) -> None:
    for source, text in texts.items():
        for name in sorted(reference_mentions(text) - actual):
            errors.append(f"{source} mentions missing reference: {name}")


def check_archive(
    tree: Tree,
    skill_text: str,
    texts: dict[str, str],
    errors: list[str],
    notes: list[str],
) -> None:
    """Keep both frozen archive snapshots whole where archive/ exists, never routed through."""
    if (tree.root / "archive").exists():
        note_file = tree.root / "archive" / "ARCHIVE-NOTE.md"
        if not note_file.exists():
            errors.append(f"archive is incomplete: {note_file.relative_to(tree.root)}")
        for arch in tree.archives:
            for rel in ("SKILL.md", "README.md", "references", "scripts"):
                path = arch / rel
                if not path.exists():
                    errors.append(f"archive is incomplete: {path.relative_to(tree.root)}")
    else:
        notes.append(
            "archive/ is absent, so its completeness is not checked; this tree reads as an "
            "installed copy, not as the repository"
        )

    active_text = skill_text + "\n" + "\n".join(
        text for name, text in texts.items() if name != "SKILL.md"
    )
    for version in ARCHIVE_VERSIONS:
        if f"archive/{version}" in active_text:
            errors.append("active SKILL/references must not depend on archived workflow path")
    if "archive/" in active_text:
        errors.append("active SKILL/references must not route through archive/")


def outline(text: str) -> tuple[list[str], list[tuple[int, int, str]]]:
    """Split into lines plus every heading outside a code fence."""
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
        (i, len(match[1]), match[2])
        for i, line in enumerate(lines)
        if i not in fenced and (match := HEADING.match(line))
    ]
    return lines, marks


def sections(text: str) -> dict[str, str]:
    """Map each heading title to its body, up to the next same-or-higher heading."""
    lines, marks = outline(text)
    found: dict[str, str] = {}
    for index, (start, depth, title) in enumerate(marks):
        end = len(lines)
        for other, level, _ in marks[index + 1:]:
            if level <= depth:
                end = other
                break
        found[title] = LF.join(lines[start + 1:end])
    return found


def own_bodies(text: str) -> list[tuple[str, str]]:
    """Each heading with only the lines written directly under it."""
    lines, marks = outline(text)
    blocks = [("(before the first heading)", LF.join(lines[:marks[0][0]] if marks else lines))]
    for index, (start, _depth, title) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else len(lines)
        blocks.append((title, LF.join(lines[start + 1:end])))
    return blocks


def check_policy_anchors(texts: dict[str, str], errors: list[str]) -> None:
    """Anchors naming a heading require a non-empty section body."""
    for source, anchors in POLICY_ANCHORS.items():
        text = texts.get(source, "")
        found = sections(text)
        for anchor in anchors:
            if not anchor.startswith("#"):
                if anchor not in text:
                    errors.append(f"{source} is missing policy anchor: {anchor}")
                continue
            title = anchor.lstrip("#").strip()
            if title not in found:
                errors.append(f"{source} is missing policy anchor: {anchor}")
                continue
            body = "".join(
                "".join(line.split())
                for line in found[title].split(LF)
                if line.strip() and not HEADING.match(line)
            )
            gate = "门禁" in title or "停止条件" in title
            minimum = MIN_GATE_CHARS if gate else MIN_BODY_CHARS
            if len(body) < minimum:
                errors.append(
                    f"{source} section '{title}' has {len(body)} characters of body, "
                    f"under the {minimum} this policy needs; the heading is not the policy"
                )


def check_single_authority(texts: dict[str, str], errors: list[str]) -> None:
    """Each single-authority rule stays in its owning file and is not pasted elsewhere."""
    for owner, (rule, phrases) in EXCLUSIVE_PHRASES.items():
        for phrase in phrases:
            if phrase not in texts.get(owner, ""):
                errors.append(
                    f"{owner} no longer contains the {rule} wording this checker "
                    f"holds as single-authority: {phrase}; move the rule back, or "
                    "update the exclusive-phrase table to the new wording"
                )
            for source, text in texts.items():
                if source != owner and phrase in text:
                    errors.append(
                        f"{source} restates {rule}: {phrase}; the single authority "
                        f"for this rule is references/{owner}, so point at "
                        f"{owner} here instead of copying the rule"
                    )


def check_restated_trust_ladder(texts: dict[str, str], errors: list[str]) -> None:
    """Catch a reworded L0-L3 automation/gate ladder outside 05-outer-loop-factory.md."""
    for source, text in texts.items():
        if source == TRUST_LADDER_OWNER:
            continue
        for title, body in own_bodies(text):
            hits: dict[str, str] = {}
            for match in TRUST_LEVEL_TOKEN.finditer(body):
                window = body[match.end():match.end() + TRUST_REACH].split(LF)[0]
                for verb in TRUST_GATE_VERBS:
                    if verb in window:
                        hits.setdefault(match[0], verb)
                        break
            if len(hits) < TRUST_DISTINCT_MIN:
                continue
            listed = "、".join(f"{lvl} {verb}" for lvl, verb in sorted(hits.items()))
            errors.append(
                f"{source} section '{title}' reads as a restated trust ladder ({listed}); "
                f"the single authority for L0-L3 gates is references/{TRUST_LADDER_OWNER}, "
                "so point at that file instead of re-specifying level rules here"
            )


def parse_frontmatter_fields(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    closing = text.find("\n---", 4)
    if closing < 0:
        return None
    fields: dict[str, str] = {}
    for name, value in FRONTMATTER_FIELD.findall(text[4:closing]):
        cleaned = value.strip()
        if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in ('"', "'"):
            cleaned = cleaned[1:-1].strip()
        fields[name] = cleaned
    return fields


def check_scripts(tree: Tree, texts: dict[str, str], errors: list[str]) -> None:
    for required_script in ("repo_guard.py", "install.py", "sync_vendor.py"):
        if not (tree.root / "scripts" / required_script).is_file():
            errors.append(f"missing scripts/{required_script}")
    if not (tree.root / "tests").is_dir():
        errors.append("missing tests/; scripts/ changes are only gated by them")
    mentioned: set[str] = set()
    for text in texts.values():
        mentioned |= set(SCRIPT_PATH.findall(text))
    for name in sorted(mentioned):
        if not (tree.root / name).is_file():
            errors.append(f"SKILL/references reference a script that does not exist: {name}")


VENDOR_PATH_MENTION = re.compile(r"vendor/pstack/[A-Za-z0-9_./<>-]+")


def check_vendor(tree: Tree, texts: dict[str, str], errors: list[str]) -> None:
    """Verify bundled vendor/pstack/ manifest, checksums, skill/agent frontmatter, and refs."""
    _count, vendor_errors = sync_vendor.verify_vendor(tree.root)
    errors.extend(vendor_errors)

    vendor_dir = tree.root / "vendor" / "pstack"
    manifest_path = vendor_dir / "UPSTREAM.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(read_text(tree, manifest_path, errors) or "{}")
        except json.JSONDecodeError:
            manifest = {}
        if isinstance(manifest, dict) and manifest:
            if not str(manifest.get("version", "")).strip():
                errors.append("vendor/pstack/UPSTREAM.json: version must be non-empty")
            skills_cfg = manifest.get("skills")
            core: list[str] = []
            principles: list[str] = []
            if not isinstance(skills_cfg, dict):
                errors.append("vendor/pstack/UPSTREAM.json: skills must be an object")
            else:
                raw_core = skills_cfg.get("core")
                raw_principles = skills_cfg.get("principles")
                if not isinstance(raw_core, list) or not raw_core or any(
                    not isinstance(x, str) or not x.strip() for x in raw_core
                ):
                    errors.append("vendor/pstack/UPSTREAM.json: skills.core must be a non-empty list")
                else:
                    core = raw_core
                if not isinstance(raw_principles, list) or any(
                    not isinstance(x, str) or not x.strip() for x in raw_principles
                ):
                    errors.append("vendor/pstack/UPSTREAM.json: skills.principles must be a list")
                else:
                    principles = raw_principles

            expected_skills = set(core) | set(principles)
            skills_root = vendor_dir / "skills"
            actual_skills = (
                {p.name for p in skills_root.iterdir() if p.is_dir()}
                if skills_root.is_dir()
                else set()
            )
            for name in sorted(expected_skills - actual_skills):
                errors.append(f"missing vendored skill directory: vendor/pstack/skills/{name}")
            for name in sorted(actual_skills - expected_skills):
                errors.append(f"undeclared vendored skill directory: vendor/pstack/skills/{name}")
            for name in sorted(actual_skills & expected_skills):
                skill_file = skills_root / name / "SKILL.md"
                if not skill_file.is_file():
                    errors.append(f"missing SKILL.md in vendor/pstack/skills/{name}")
                    continue
                fm = parse_frontmatter_fields(read_text(tree, skill_file, errors))
                if fm is None:
                    errors.append(f"vendor/pstack/skills/{name}/SKILL.md: missing YAML frontmatter")
                else:
                    if fm.get("name") != name:
                        errors.append(
                            f"vendor/pstack/skills/{name}/SKILL.md: frontmatter name "
                            f"{fm.get('name')!r} != directory name {name!r}"
                        )
                    if not fm.get("description"):
                        errors.append(
                            f"vendor/pstack/skills/{name}/SKILL.md: frontmatter description is empty"
                        )

            raw_agents = manifest.get("agents")
            expected_agents: set[str] = set()
            if not isinstance(raw_agents, list) or any(
                not isinstance(x, str) or not x.strip() for x in raw_agents
            ):
                errors.append("vendor/pstack/UPSTREAM.json: agents must be a list")
            else:
                expected_agents = set(raw_agents)
            agents_root = vendor_dir / "agents"
            actual_agent_files = (
                {p.name for p in agents_root.iterdir() if p.is_file()}
                if agents_root.is_dir()
                else set()
            )
            expected_agent_files = {f"{a}.md" for a in expected_agents}
            for fname in sorted(expected_agent_files - actual_agent_files):
                errors.append(f"missing vendored agent file: vendor/pstack/agents/{fname}")
            for fname in sorted(actual_agent_files - expected_agent_files):
                errors.append(f"undeclared vendored agent file: vendor/pstack/agents/{fname}")
            for agent in sorted(expected_agents):
                afile = agents_root / f"{agent}.md"
                if not afile.is_file():
                    continue
                fm = parse_frontmatter_fields(read_text(tree, afile, errors))
                if fm is None or fm.get("name") != agent:
                    errors.append(
                        f"vendor/pstack/agents/{agent}.md: frontmatter name must equal {agent!r}"
                    )

            statechart_ts = skills_root / "statechart" / "scripts" / "statechart.ts"
            if not statechart_ts.is_file():
                errors.append("missing vendor/pstack/skills/statechart/scripts/statechart.ts")

    for source, text in texts.items():
        for match in VENDOR_PATH_MENTION.finditer(text):
            rel = match.group(0).rstrip("/")
            if any(ch in rel for ch in "<>*?"):
                continue
            if not (tree.root / rel).exists():
                errors.append(f"{source} references missing vendor path: {rel}")


def check_size_budgets(texts: dict[str, str], errors: list[str], warnings: list[str]) -> None:
    for name, text in texts.items():
        size = len(text.encode("utf-8"))
        budget = SIZE_BUDGETS.get(name, REFERENCE_BUDGET)
        if size > budget:
            errors.append(
                f"{name} is {size} bytes, over its {budget}-byte budget; "
                "move stage detail into the reference that owns it"
            )
        elif size > budget * BUDGET_WARN:
            warnings.append(
                f"{name} is at {100 * size / budget:.0f}% of its {budget}-byte budget "
                f"({budget - size} bytes left); the next addition will need a trim"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help="workflow tree to check (default: the skill directory holding this script)",
    )
    tree = Tree.at(Path(parser.parse_args(argv).root))

    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    actual = {path.name for path in tree.refs.glob("*.md")} if tree.refs.exists() else set()
    unexpected = actual - EXPECTED_REFERENCES
    missing = EXPECTED_REFERENCES - actual
    for name in sorted(missing):
        errors.append(f"expected reference is missing: references/{name}")
    for name in sorted(unexpected):
        errors.append(f"unexpected active reference (add it to checker/map): references/{name}")

    skill_text = read_text(tree, tree.skill, errors)
    texts = {"SKILL.md": skill_text}
    for name in sorted(actual):
        texts[name] = read_text(tree, tree.refs / name, errors)

    check_frontmatter(skill_text, errors)
    mapped, map_start = check_reference_map(skill_text, actual, errors)
    del mapped
    check_mentions(texts, actual, errors)
    if skill_text:
        check_reachability(skill_text, texts, actual, map_start, errors)
    check_pyramid_order(skill_text, texts.get("00-router.md", ""), errors)
    check_archive(tree, skill_text, texts, errors, notes)
    check_policy_anchors(texts, errors)
    check_single_authority(texts, errors)
    check_restated_trust_ladder(texts, errors)
    check_scripts(tree, texts, errors)
    check_vendor(tree, texts, errors)
    check_size_budgets(texts, errors, warnings)

    for name, text in texts.items():
        if name != "SKILL.md" and not text.strip():
            errors.append(f"active reference is empty: {name}")

    for note in notes:
        print(f"NOTE  {note}")
    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")
    print(
        f"{len(actual)} active reference files, {len(errors)} error(s), "
        f"{len(warnings)} warning(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
