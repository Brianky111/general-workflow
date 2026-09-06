#!/usr/bin/env python3
"""Consistency checks for the active Greenfield workflow.

The checker deliberately validates the workflow's contract, not a particular
project implementation. It verifies that the active reference graph is
complete and reachable, that the lifecycle stages remain ordered, and that the
archive is not accidentally used as an active dependency.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
REFS = ROOT / "references"
ARCHIVE = ROOT / "archive" / "general-workflow-v0.12.0"

EXPECTED_REFERENCES = {
    "00-progress-router.md",
    "00-project-profile.md",
    "00-lean-path.md",
    "01-requirements-and-goals.md",
    "02-scenarios-and-acceptance.md",
    "03-scope-and-nongoals.md",
    "04-constraints-quality-risks.md",
    "05-architecture-design.md",
    "05a-mechanisms-and-contracts.md",
    "06-scaffolding-and-ci.md",
    "07-vertical-slice.md",
    "08-implementation-tdd.md",
    "09-testing-review-integration.md",
    "10-release-operations.md",
    "11-retrospective-evolution.md",
    "99-state-and-handoff.md",
}

# The always-loaded surface is SKILL.md plus the router; every other reference is
# paid for only when its stage is entered. These budgets exist so that content
# belonging to a stage document cannot quietly drift back into the entry path,
# and so no single stage document grows back into a load spike.
SIZE_BUDGETS = {
    "SKILL.md": 9_500,
    "00-progress-router.md": 9_500,
}
REFERENCE_BUDGET = 14_000
CRLF = "\r\n"
LF = "\n"

REFERENCE_NAME = re.compile(r"\b\d{2}[a-z]?-[a-z0-9][a-z0-9-]*\.md\b")
FRONTMATTER_FIELD = re.compile(r"(?m)^([a-z][a-z0-9_-]*):\s*(.+?)\s*$")

POLICY_ANCHORS: dict[str, tuple[str, ...]] = {
    "SKILL.md": (
        "Greenfield",
        "P0 项目画像与架构驱动",
        "第一条垂直切片",
        "统一阶段规则",
        "交付完成条件",
        "运行反馈驱动演化",
        "一个事实一个权威来源",
        "证据胜过口头状态",
        "不得用测试专属实现",
    ),
    "00-progress-router.md": (
        "## 第一次判断",
        "## 生命周期状态",
        "## 路由算法",
        "## 阶段选择表",
        "## 全局门禁",
        "## 结束与回流",
        "## 路径深度",
        "只加载当前 reference",
        "docs/workflow-state.md",
    ),
    "00-project-profile.md": (
        "## 画像维度",
        "## 规模判断：看负载和边界，不看文件数",
        "## 形态信号",
        "## 流程档位",
        "LEAN",
        "STANDARD",
        "HIGH-RISK",
        "## 画像门禁",
    ),
    "00-lean-path.md": (
        "## 入口条件",
        "## 一页项目合同",
        "## 快路径的最低要求",
        "## 合并后的主线",
        "## 与下游阶段的对接",
        "## 升级触发",
        "## 快路径门禁",
    ),
    "01-requirements-and-goals.md": (
        "## 需求提炼顺序",
        "## 需求分类",
        "## 最小目标合同",
        "success_metrics",
        "initial_requirements",
        "## 退出门禁",
    ),
    "02-scenarios-and-acceptance.md": (
        "## 场景写法",
        "Given",
        "When",
        "Then",
        "验收 ID",
        "## 验收矩阵",
        "## 退出门禁",
    ),
    "03-scope-and-nongoals.md": (
        "## 范围分层",
        "Must",
        "Should",
        "Could",
        "Non-goal",
        "## 范围防火墙",
        "## 变更协议",
        "## 范围门禁",
    ),
    "04-constraints-quality-risks.md": (
        "## 质量属性写法",
        "Q-ID",
        "## 约束清单",
        "## 风险登记与最小实验",
        "假设→实验→通过条件→结果→处置",
        "## 风险门禁",
    ),
    "05-architecture-design.md": (
        "## 决策顺序",
        "## 系统形态选择",
        "## 目录组织与模块边界",
        "## 运行时拓扑",
        "## 核心数据模型",
        "## 关键机制与契约",
        "现在必须有",
        "明确不需要",
        "由风险触发",
        "## 技术栈选择",
        "## 数据与基础设施匹配",
        "## 部署拓扑与恢复",
        "## ADR 与验证计划",
        "## Architecture Ready 门禁",
    ),
    "05a-mechanisms-and-contracts.md": (
        "## 关键机制决策",
        "身份、授权和租户",
        "异步任务与可靠副作用",
        "幂等",
        "事务、并发和缓存",
        "## API 与事件契约",
        "统一响应和错误",
        "版本和兼容",
        "## 配置、秘密与可观测性",
        "## 机制门禁",
    ),
    "06-scaffolding-and-ci.md": (
        "## 落地顺序",
        "固定具体版本",
        "使用官方脚手架",
        "配置工程质量",
        "基础 CI",
        "干净 clone 验证",
        "## Bootstrap Ready 门禁",
    ),
    "07-vertical-slice.md": (
        "## 选择标准",
        "## 切片地图",
        "真实入口",
        "architecture_hypothesis",
        "## Slice Ready 门禁",
    ),
    "08-implementation-tdd.md": (
        "## 一个行为一个循环",
        "### Red",
        "### Green",
        "### Refactor",
        "真实入口与组合根规则",
        "范围控制",
        "## Implementation Ready/Done 门禁",
    ),
    "09-testing-review-integration.md": (
        "## 测试层次",
        "单元",
        "集成",
        "合同",
        "E2E",
        "## 证据映射",
        "## 架构约束检查",
        "## 评审与集成顺序",
        "Definition of Done",
    ),
    "10-release-operations.md": (
        "## 环境分级",
        "## 构建产物与可追溯性",
        "## 数据库迁移与兼容",
        "## 发布策略",
        "## CI/CD 流程",
        "## 监控、告警与观察窗口",
        "## 回滚、前滚与恢复",
        "## Release Ready 门禁",
    ),
    "11-retrospective-evolution.md": (
        "## 复盘问题",
        "## 证据与决策表",
        "## 架构演化规则",
        "## 下一条垂直切片",
        "## 回流条件",
        "## 复盘门禁",
    ),
    "99-state-and-handoff.md": (
        "## 状态文件是游标和索引，不是第二份真相",
        "## 位置与规模",
        "## 状态文件模板",
        "## 会话开始：读取并校验",
        "## 会话结束：更新",
        "## 反模式",
        "仓库事实赢",
    ),
}


def reference_mentions(text: str) -> set[str]:
    """Return reference-looking filenames mentioned in text."""

    return set(REFERENCE_NAME.findall(text))


def read_text(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"not UTF-8: {path.relative_to(ROOT)} ({exc})")
        return ""


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
    # The map is an index; reachability starts in the operating rules before it.
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


def check_stage_order(skill_text: str, router_text: str, errors: list[str]) -> None:
    stages = (
        "P0 项目画像与架构驱动",
        "1. 明确需求与目标",
        "2. 用户场景与验收结果",
        "3. 范围、非目标与版本边界",
        "4. 约束、质量属性、风险与未知",
        "5. 架构评估与设计",
        "6. 技术栈、仓库脚手架与基础 CI",
        "7. 第一条垂直切片",
        "8. 真实代码实现：红 → 绿 → 重构",
        "9. 测试、评审与集成",
        "10. 发布、监控、回滚与运行",
        "11. 复盘、架构演化与下一条切片",
    )
    positions: list[int] = []
    for stage in stages:
        pos = skill_text.find(stage)
        if pos < 0:
            errors.append(f"SKILL.md is missing lifecycle stage: {stage}")
        positions.append(pos)
    present = [pos for pos in positions if pos >= 0]
    if present and present != sorted(present):
        errors.append("SKILL.md lifecycle stages are out of order")
    for token in ("IDEA", "DEFINED", "ARCHITECTURE-READY", "BOOTSTRAPPED",
                  "SLICE-READY", "BUILDING", "RELEASE-CANDIDATE",
                  "OPERATING", "PAUSED", "CANCELLED"):
        if token not in router_text:
            errors.append(f"router is missing lifecycle state: {token}")


def check_mentions(
    texts: dict[str, str], actual: set[str], errors: list[str]
) -> None:
    for source, text in texts.items():
        for name in sorted(reference_mentions(text) - actual):
            errors.append(f"{source} mentions missing reference: {name}")


def check_archive(skill_text: str, texts: dict[str, str], errors: list[str]) -> None:
    required = (
        ARCHIVE / "SKILL.md",
        ARCHIVE / "README.md",
        ARCHIVE / "references",
        ARCHIVE / "scripts",
        ROOT / "archive" / "ARCHIVE-NOTE.md",
    )
    for path in required:
        if not path.exists():
            errors.append(f"archive is incomplete: {path.relative_to(ROOT)}")

    active_text = skill_text + "\n" + "\n".join(
        text for name, text in texts.items() if name != "SKILL.md"
    )
    if "archive/general-workflow-v0.12.0" in active_text:
        errors.append("active SKILL/references must not depend on archived workflow path")
    if "archive/" in skill_text:
        errors.append("SKILL.md must not route through archive/")


def check_policy_anchors(texts: dict[str, str], errors: list[str]) -> None:
    for source, anchors in POLICY_ANCHORS.items():
        text = texts.get(source, "")
        for anchor in anchors:
            if anchor not in text:
                errors.append(f"{source} is missing policy anchor: {anchor}")


def section(text: str, heading: str) -> str | None:
    """Return the body of a level-2 section, or None when it is absent."""

    match = re.search(
        r"(?ms)^## " + re.escape(heading) + r"\s*\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1) if match else None


def check_return_table(texts: dict[str, str], errors: list[str]) -> None:
    """The retrospective's return table is a second router; keep it in sync.

    Stage 11 routes work back into earlier stages, so every destination the
    forward table can reach must also be reachable backwards. When the two
    drift, a stage becomes enterable but not returnable -- which is how a
    section that moves to a new file silently loses its inbound edge.
    """

    forward = section(texts.get("00-progress-router.md", ""), "阶段选择表")
    backward = section(texts.get("11-retrospective-evolution.md", ""), "回流条件")
    if forward is None:
        errors.append("00-progress-router.md has no ## 阶段选择表 section")
        return
    if backward is None:
        errors.append("11-retrospective-evolution.md has no ## 回流条件 section")
        return

    # Stage 11 owns the return table; it is a forward destination, not a target.
    targets = reference_mentions(forward) - {"11-retrospective-evolution.md"}
    for name in sorted(targets - reference_mentions(backward)):
        errors.append(
            f"11-retrospective-evolution.md return table is missing {name}, "
            "which the router can route into"
        )


def check_size_budgets(texts: dict[str, str], errors: list[str]) -> None:
    """Keep the entry path small and stage documents load-on-demand.

    A stage rule restated in SKILL.md is a second authority that drifts, and a
    stage document that absorbs a neighbouring stage stops being loadable on
    demand. Both show up first as size growth, so the budgets are the cheap
    mechanical guard; exceeding one means split the file or push detail down,
    not raise the number.
    """

    for name, text in texts.items():
        # Normalize newlines: with core.autocrlf the working tree differs by one
        # byte per line across platforms, and a budget must not depend on that.
        size = len(text.replace(CRLF, LF).encode("utf-8"))
        budget = SIZE_BUDGETS.get(name, REFERENCE_BUDGET)
        if size > budget:
            errors.append(
                f"{name} is {size} bytes, over its {budget}-byte budget; "
                "move stage detail into the reference that owns it"
            )


def main() -> int:
    errors: list[str] = []
    actual = {path.name for path in REFS.glob("*.md")} if REFS.exists() else set()
    unexpected = actual - EXPECTED_REFERENCES
    missing = EXPECTED_REFERENCES - actual
    for name in sorted(missing):
        errors.append(f"expected reference is missing: references/{name}")
    for name in sorted(unexpected):
        errors.append(f"unexpected active reference (add it to checker/map): references/{name}")

    skill_text = read_text(SKILL, errors)
    texts = {"SKILL.md": skill_text}
    for name in sorted(actual):
        texts[name] = read_text(REFS / name, errors)

    check_frontmatter(skill_text, errors)
    mapped, map_start = check_reference_map(skill_text, actual, errors)
    del mapped  # The function reports map mismatches; no second interpretation here.
    check_mentions(texts, actual, errors)
    if skill_text:
        check_reachability(skill_text, texts, actual, map_start, errors)
    check_stage_order(skill_text, texts.get("00-progress-router.md", ""), errors)
    check_archive(skill_text, texts, errors)
    check_policy_anchors(texts, errors)
    check_return_table(texts, errors)
    check_size_budgets(texts, errors)

    # Empty active references are almost always an accidental placeholder.
    for name, text in texts.items():
        if name != "SKILL.md" and not text.strip():
            errors.append(f"active reference is empty: {name}")

    for error in errors:
        print(f"ERROR {error}")
    print(
        f"{len(actual)} active reference files, {len(errors)} error(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
