#!/usr/bin/env python3
"""Consistency checks for the active Greenfield workflow.

The checker deliberately validates the workflow's contract, not a particular
project implementation. It verifies that the active reference graph is
complete and reachable, that the lifecycle stages remain ordered, and that the
archive is not accidentally used as an active dependency.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


# Default to the skill this script ships in, so `python scripts/check_consistency.py`
# keeps checking its own tree; --root points the same checks at a copy.
DEFAULT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_VERSION = "general-workflow-v0.12.0"


class Tree(NamedTuple):
    """One workflow tree: a root plus the four paths every check reads."""

    root: Path
    skill: Path
    refs: Path
    archive: Path

    @classmethod
    def at(cls, root: Path) -> "Tree":
        root = root.resolve()
        return cls(
            root,
            root / "SKILL.md",
            root / "references",
            root / "archive" / ARCHIVE_VERSION,
        )

EXPECTED_REFERENCES = {
    "00-progress-router.md",
    "00-project-profile.md",
    "00-lean-path.md",
    "00-refactor-path.md",
    "00-brownfield-entry.md",
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
#
# The four numbers below are pinned by BudgetContractTests in
# tests/test_check_consistency.py, because raising one is the only way past this
# gate that leaves both gates green. Editing a number here fails there, with the
# reasons written out; that test is the place to read them and the place to argue.
SIZE_BUDGETS = {
    "SKILL.md": 8_000,
    "00-progress-router.md": 9_500,
}
REFERENCE_BUDGET = 13_000
# A budget that is nearly spent is the last warning before the next edit has
# to shave bytes off unrelated prose to fit.
BUDGET_WARN = 0.90
# A heading whose body was emptied still satisfies a substring anchor, so the
# anchors are checked inside their own section and the section must say
# something. Gates carry more than a sentence.
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
        "Greenfield",
        "P0 项目画像与架构驱动",
        "第一条垂直切片",
        "统一阶段规则",
        "交付完成条件",
        # Reporting is two-tier: full only on handoff or a tier/stage change. The
        # heading alone does not carry that; the compact tier is the half that
        # gets dropped, and losing it means every turn re-reports the profile.
        "## 默认响应形状",
        "同一阶段内连续推进时",
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
        "## 路径深度与暂停",
        # Loading the profile conditionally is what keeps the resident set at
        # three files and stops a confirmed tier from being silently recomputed.
        # Deleting this section, or making the load unconditional again, left
        # every other check green: the router still routed, every anchor still
        # matched, and the saving was gone.
        "### 画像按需加载",
        "跳过画像直接进阶段选择",
        # The condition list and the HIGH-RISK exception are the two halves that
        # make the skip safe. Without the first, "load it when needed" has no
        # test; without the second, a HIGH-RISK project at stage 8 skips the
        # deepening row too, and no stage document carries a replacement.
        "以下情况才加载 00-project-profile.md",
        "只取表不重定档位",
        "只加载当前 reference",
        "docs/workflow/",
        "delivery_target",
        # The router must say what happens after the user confirms a non-Greenfield
        # boundary, not just flag it as a risk; compat_surface is where that lands.
        "compat_surface",
        # Same literal as 99-state-and-handoff.md: see the note there.
        '--root "<目标项目绝对路径>" --json',
    ),
    "00-project-profile.md": (
        "## 画像维度",
        "## 规模判断：看负载和边界，不看文件数",
        "## 形态信号",
        "## 流程档位",
        "### LEAN",
        "### STANDARD",
        "### HIGH-RISK",
        # The one place HIGH-RISK deepening is defined. Emptied or deleted, every
        # stage document goes back to inventing its own high-risk requirements.
        "## HIGH-RISK 加深清单",
        "maintenance_horizon",
        "## 画像门禁",
    ),
    "00-lean-path.md": (
        "## 入口条件",
        "## 一页项目合同",
        "delivery_endpoint",
        "## 快路径的最低要求",
        "- commands:",
        "| C-ID | date |",
        "## 合并后的主线",
        # The exemption list is single-authority here; the router, SKILL.md and
        # README only point at it. Both sentences are load-bearing: one says LEAN
        # never gives up clean-clone CI and real-entrypoint evidence, the other
        # names this file as the only place the list may live. A second copy
        # growing back elsewhere is caught by EXCLUSIVE_PHRASES below, not here.
        "LEAN 有两条不打折",
        "LEAN 减免的唯一权威位置",
        "## 与下游阶段的对接",
        "## 升级触发",
        "## 快路径门禁",
    ),
    "00-refactor-path.md": (
        "## 入口",
        "## 分类",
        "## 保护基线",
        "## 目标结构",
        "## 认领与切片文件",
        "## 执行",
        "## 退出门禁",
        "## 停止条件",
        # A refactor is authorized, never self-started, and never a feature.
        "authorized_by",
        "不产生 R-ID 或 A-ID",
        # The two halves of its evidence: kept behavior called again at the
        # closing commit, and a structure check that fails before and passes
        # after. Dropping either turns the path back into "tests still pass".
        "baseline",
        "不改断言，不改公开签名",
    ),
    "00-brownfield-entry.md": (
        "## 入口条件",
        "## 第 0 步：跑起来，建游标",
        "## 第 1 步：全量读",
        "## 第 2 步：agent 先下结论，反向出需求文档",
        "## 第 3 步：用户审阅",
        "## 第 4 步：基线，再调偏差",
        "## 收口门禁",
        "## 停止条件",
        # Read everything, call only what the user keeps. The survey is complete
        # at the entrypoint and module level before the review, and no baseline
        # runs before it; drop either half and the entry becomes a guess that
        # was verified against itself.
        "先读全量，再调用",
        "从组合根反查",
        # The derived document is a hypothesis until the user has read it, and
        # the status line is the only thing that says which of the two it is.
        "status: derived",
        # The fourth review answer. Without it the reviewer is pushed into
        # "keep" whenever unsure, and the deviation is filed as confirmed.
        "不知道",
        # A deviation is a fact, never work: the queue is not authorization.
        "未授权",
        "S-00",
    ),
    "01-requirements-and-goals.md": (
        "## 需求提炼顺序",
        "## 需求分类",
        "## 最小目标合同",
        "success_metrics",
        "initial_requirements",
        "delivery_endpoint",
        "## 退出门禁",
    ),
    "02-scenarios-and-acceptance.md": (
        "## 场景写法",
        "## 可执行形状",
        "接缝",
        "Given <",
        "When <",
        "Then <",
        "验收 ID",
        "## 验收矩阵",
        "## 退出门禁",
    ),
    "03-scope-and-nongoals.md": (
        "## 范围分层",
        "MVP 用删除法判定",
        "| Must |",
        "| Should |",
        "| Could |",
        "| Non-goal |",
        "## 范围防火墙",
        "## 变更协议",
        "变更记录是一份文件",
        "| C-ID | date |",
        "## 范围门禁",
    ),
    "04-constraints-quality-risks.md": (
        "## 质量属性写法",
        "Q-ID",
        "## 约束清单",
        "## 风险登记与最小实验",
        "假设→实验→通过条件→结果→处置",
        "K-ID",
        "## 风险门禁",
    ),
    "05-architecture-design.md": (
        "## 决策顺序",
        "## 系统形态选择",
        "## 目录组织与模块边界",
        "seam 并集",
        "## 运行时拓扑",
        "## 核心数据模型",
        "## 关键机制与契约",
        "现在必须有",
        "明确不需要",
        "由风险触发",
        "## 技术栈选择",
        "## 数据与基础设施匹配",
        "## 部署拓扑与恢复",
        "H-ID 在这里产生",
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
        "还没有远端仓库或 CI 提供方时",
        "能重复对真实入口发起调用并看到结果",
        "## Bootstrap Ready 门禁",
    ),
    "07-vertical-slice.md": (
        "## 选择标准",
        "首条与后续切片的权重差别",
        "## 交付完成的判定",
        "## 切片地图",
        "- user_outcome:",
        "真实入口",
        "architecture_hypothesis",
        # Claiming happens in stage 7, so the rules live with the stage instead of
        # in the always-resident state file. 99 keeps a pointer, not a copy.
        "## 认领规则",
        # The heading plus one rule is not the procedure. These name the two rules
        # that are cheapest to drop and most expensive to lose: without rule 1 the
        # backlog never learns who owns the A-ID, and without the one-live-slice
        # limit two claims overlap on write_scope with nothing to reject them.
        "认领即在自己的切片文件里写上 owner 和 claimed",
        "一次一条",
        # Returning a slice must also clear owner/claimed; dropping this rule
        # leaves an empty slice permanently in flight and locks the owner out.
        "归还与改判",
        "## Slice Ready 门禁",
    ),
    "08-implementation-tdd.md": (
        "## 一个行为一个循环",
        "### Red",
        "### Green",
        "### Refactor",
        "真实入口与组合根规则",
        "绿之后立刻对真实入口发起一次调用",
        "范围控制",
        "## Implementation Ready/Done 门禁",
    ),
    "09-testing-review-integration.md": (
        "## 测试层次",
        "| 单元 |",
        "| 集成 |",
        "| 合同 |",
        "| E2E |",
        "## 证据映射",
        "### 单条 A-ID：可以标 delivered",
        "对真实入口发起过一次实际调用",
        "<调用> → <观察到的结果>",
        "### 当前批次：可以进入 10-release-operations.md",
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
        "（STANDARD 起",
        "## Release Ready 门禁",
    ),
    "11-retrospective-evolution.md": (
        "## 复盘问题",
        "## 证据与决策表",
        "## 架构演化规则",
        "## 下一条垂直切片",
        "## 复盘门禁",
    ),
    "99-state-and-handoff.md": (
        "## 状态文件是游标和索引，不是第二份真相",
        "## 范围台账规则",
        "delivered 单调不可退",
        "一次真实调用及其结果",
        "（即 remaining）",
        "## 为什么分片",
        "## 布局",
        "`## Slice map`",
        "delivery_target",
        # Two contract fields the status script reads and the template must keep:
        # state_version is mandatory, next_action is the pre-slice cursor. Losing
        # the template line is how a field quietly stops being written at all.
        "- state_version: 2",
        "- next_action:",
        # Without the migration procedure, a pre-2 state file has no documented
        # way forward and the version check reads as an unexplained rejection.
        "## 状态格式版本",
        "## 会话开始：读取并校验",
        # Deliberate second copy: the router inlines this same line so a
        # read-only status check does not load this file. Asserting the identical
        # string in both places turns a one-sided edit into an error here.
        '--root "<目标项目绝对路径>" --json',
        "## 会话结束：更新",
        "## 反模式",
        "仓库事实赢",
    ),
}


# One fact, one authority. Consolidating a rule into one file does not keep it
# there: restating it where it is needed is always shorter than sending the
# reader somewhere else, so the copy grows back unless a gate rejects it. Each
# entry names the file that owns a rule and the wording that travels with the
# rule when someone pastes it.
#
# Scope, stated plainly so nobody trusts this table for more than it does: it
# matches literal phrases, so it catches copy-paste and only copy-paste. Anyone
# who retypes the rule in their own words walks past it untouched — and typing
# it out again is exactly what a reader who wants the rule to hand does. A
# pointer is meant to stay legal, which is why no phrase here is a filename:
# "减免清单只在 00-lean-path.md" passes, and so does a paraphrase. For the two
# tier policies, check_restated_tier_policy below covers part of that gap by
# shape instead of wording; every other rule in this table is guarded against
# pasting alone, and a reworded copy still needs a human to notice.
EXCLUSIVE_PHRASES: dict[str, tuple[str, tuple[str, ...]]] = {
    "00-lean-path.md": (
        "LEAN 减免清单",
        (
            "逐阶段的减免如下",
            "整个阶段跳过",
            "不要求部署到 staging",
            "不要求一个行为一个提交",
            "不要求合同测试",
            "不要求独立 staging 环境",
            "简化为一次 closeout",
        ),
    ),
    "00-project-profile.md": (
        "HIGH-RISK 加深清单",
        (
            "在完整路径之上额外要求的证据",
            "唯一加深清单",
            "实验在实现开始前跑完",
            "由非作者做一次独立架构评审",
            "评审人与实现者分离",
            "清单只加证据",
        ),
    ),
    "07-vertical-slice.md": (
        "切片认领与归还规则",
        (
            "不要抢一个 owner 有新鲜证据的切片",
            "在途切片必须有 owner",
            "只能持有一条",
            "接手一条 stale 切片",
            "漏掉第三件事会被自己的归还锁住",
        ),
    ),
}


# The table above matches wording, and the two tier policies are the copies that
# hurt most: they are per-stage lists, they are long, and a reader who is inside
# stage 09 wants only the 09 line, so the tempting edit is to retype that row
# where it is needed. Retyping evades a phrase table by construction, so this
# guard ignores wording and reads shape. A tier policy is recognizable without
# knowing any of its sentences: bare stage numbers, each one immediately
# followed by an exemption or a deepening, three or more of them inside a single
# block. Ordinary prose names one stage and says one thing about it; only a
# transcribed policy enumerates.
TIER_POLICY_OWNERS = ("00-lean-path.md", "00-project-profile.md")
# Bare stage numbers only. `07-vertical-slice.md` is a pointer, which is the
# behaviour being asked for, so a filename must not read as a stage number —
# including by backtracking, which is what `[a-z]?` invites: without the first
# lookahead, `05a-mechanisms-…` gives up its `a` and matches a bare `05`.
STAGE_NUMBER = re.compile(r"(?<![0-9A-Za-z])(0[1-9]|1[01])[a-z]?(?![0-9a-z])(?!-[a-z])")
TIER_POLICY_VERBS = (
    "不要求", "不必", "无需", "只需", "可以省", "可省", "省略", "免除",
    "跳过", "简化为", "合并为", "减免", "不做",
    "另加", "额外", "加深", "再补", "还要", "才允许", "必须先",
)
# How far past the number the verb may sit and still belong to it: enough for a
# table cell's `| ` and a few words, short enough that the next list item's verb
# does not get borrowed by the previous number.
TIER_POLICY_REACH = 24
# Two stages with exemption wording in one block is a paragraph that mentions
# two stages; the whole tree's high-water mark outside the owning files is one.
# Three is a list, and the margin says so.
TIER_POLICY_STAGES = 3


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
    # Decode the bytes here rather than call Path.read_text, which applies
    # universal newlines and hands back a string CRLF can never appear in. The
    # size budget counts the bytes of what this returns, and with core.autocrlf
    # a checkout differs by one byte per line across platforms; normalizing at
    # the single place that touches the disk is what makes the budget mean the
    # same thing on Windows and on Linux.
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


def check_archive(
    tree: Tree, skill_text: str, texts: dict[str, str], errors: list[str],
    notes: list[str],
) -> None:
    """The archive stays whole where it exists; the active tree never routes
    through it, anywhere.

    Completeness is checked only in a tree that carries archive/ at all. The
    README's install step deletes the directory on purpose, and the README also
    says to point --root at the installed copy to confirm it is complete; while
    the five paths were demanded wherever the checker ran, those two could not
    both hold, and every documented install failed with five errors that buried
    the answer. A tree without archive/ is read as an installed copy and says so
    in a NOTE line, so a reader is not left wondering why the archive went
    unmentioned.

    The routing check runs regardless: a reference into archive/ is broken
    exactly where the directory is gone, so it is the half that matters on an
    install. What this cannot tell apart: the whole directory deleted from the
    repository itself, which then reads as an install. git shows that deletion;
    a file missing inside the archive is what the completeness check is for.
    """

    if (tree.root / "archive").exists():
        required = (
            tree.archive / "SKILL.md",
            tree.archive / "README.md",
            tree.archive / "references",
            tree.archive / "scripts",
            tree.root / "archive" / "ARCHIVE-NOTE.md",
        )
        for path in required:
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
    if f"archive/{ARCHIVE_VERSION}" in active_text:
        errors.append("active SKILL/references must not depend on archived workflow path")
    if "archive/" in skill_text:
        errors.append("SKILL.md must not route through archive/")


def outline(text: str) -> tuple[list[str], list[tuple[int, int, str]]]:
    """Split into lines plus every heading outside a code fence.

    A template block that shows `## 复盘门禁` is documentation of a heading, not
    a heading, so fenced lines are dropped before the headings are collected.
    """

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
    """Each heading with only the lines written directly under it.

    sections() nests, so an H2 body contains its H3s and the file's H1 body is
    the whole file. Counting stage numbers over a nested body would count the
    lifecycle itself: every stage list in the tree sits somewhere under one H1.
    The block an author actually typed is the unit that can be a pasted policy.
    """

    lines, marks = outline(text)
    blocks = [("(before the first heading)", LF.join(lines[:marks[0][0]] if marks else lines))]
    for index, (start, _depth, title) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else len(lines)
        blocks.append((title, LF.join(lines[start + 1:end])))
    return blocks


def check_policy_anchors(texts: dict[str, str], errors: list[str]) -> None:
    """Anchors that name a heading must find a section that still has content.

    A substring check passes on a file that keeps every heading and deletes the
    procedure underneath, which is exactly the edit this guard exists to catch.
    """

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
                "".join(line.split())  # visible characters only
                for line in found[title].split(LF)
                if line.strip() and not HEADING.match(line)
            )
            gate = "门禁" in title or "Definition of Done" in title
            minimum = MIN_GATE_CHARS if gate else MIN_BODY_CHARS
            if len(body) < minimum:
                errors.append(
                    f"{source} section '{title}' has {len(body)} characters of body, "
                    f"under the {minimum} this policy needs; the heading is not the policy"
                )


def check_single_authority(texts: dict[str, str], errors: list[str]) -> None:
    """A rule lives in one file; a verbatim copy of it elsewhere is an error.

    Each phrase is checked from both sides. It must still be in the file that
    owns the rule, or the table guards wording that no longer exists and stops
    guarding anything. And it must be nowhere else, because the second copy is
    the one that drifts: a router copy of the LEAN list that says clean-clone
    verification can be skipped reads as authoritative to whoever loads the
    router, and the two documents then disagree with nothing to break.

    What this does not do: recognize the same rule in different words. The
    comparison is substring equality, so "09 不要求合同测试" is caught and
    "09 可以省掉合同测试" is not. Read a green run as "nobody pasted it", not
    as "the rule is still in one place".
    """

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


def check_restated_tier_policy(texts: dict[str, str], errors: list[str]) -> None:
    """Catch a tier policy retyped in the author's own words.

    check_single_authority sees copy-paste only. Every rewrite that walked past
    it in review looked the same in shape: a run of bare stage numbers, each
    carrying a "you may drop this" or "you must add this". That shape is what a
    rewrite cannot drop, so it is what gets counted here instead of a sentence.

    The failure being prevented: a reader who loads 04 or the router finds a
    per-stage list there, treats it as the rule, and never opens the file that
    owns it. When the owning file is later corrected the pasted list is not, and
    the pair disagrees with nothing left to notice.

    Two limits worth knowing before trusting a green run. This reads only
    SKILL.md and references/, so a copy in README.md or AGENTS.md is invisible
    to it. And it recognizes a per-stage list, not a single rule: the claim
    rules in 07-vertical-slice.md have no stage numbers to count, so a reworded
    copy of those still gets past both guards.
    """

    for source, text in texts.items():
        if source in TIER_POLICY_OWNERS:
            continue
        for title, body in own_bodies(text):
            hits: dict[str, str] = {}
            for match in STAGE_NUMBER.finditer(body):
                window = body[match.end():match.end() + TIER_POLICY_REACH].split(LF)[0]
                for verb in TIER_POLICY_VERBS:
                    if verb in window:
                        hits.setdefault(match[0], verb)
                        break
            if len(hits) < TIER_POLICY_STAGES:
                continue
            listed = "、".join(f"{stage} {verb}" for stage, verb in sorted(hits.items()))
            errors.append(
                f"{source} section '{title}' reads as a per-stage tier policy "
                f"({listed}); LEAN exemptions are owned by references/00-lean-path.md "
                "and HIGH-RISK deepening by references/00-project-profile.md, so name "
                "the owning file here instead of listing the stages again"
            )


def check_scripts(tree: Tree, texts: dict[str, str], errors: list[str]) -> None:
    """The router calls the status script every session with existing state.

    The archive's scripts were asserted while the live one was not, so deleting
    it left the checker green and every stateful session broken.
    """

    if not (tree.root / "scripts" / "workflow_status.py").is_file():
        errors.append("missing scripts/workflow_status.py; the router invokes it every session")
    if not (tree.root / "tests").is_dir():
        errors.append("missing tests/; scripts/ changes are only gated by them")
    mentioned: set[str] = set()
    for text in texts.values():
        mentioned |= set(SCRIPT_PATH.findall(text))
    for name in sorted(mentioned):
        if not (tree.root / name).is_file():
            errors.append(f"SKILL/references reference a script that does not exist: {name}")


def check_size_budgets(texts: dict[str, str], errors: list[str], warnings: list[str]) -> None:
    """Keep the entry path small and stage documents load-on-demand.

    A stage rule restated in SKILL.md is a second authority that drifts, and a
    stage document that absorbs a neighbouring stage stops being loadable on
    demand. Both show up first as size growth, so the budgets are the cheap
    mechanical guard; exceeding one means split the file or push detail down,
    not raise the number.
    """

    for name, text in texts.items():
        # read_text already normalized the newlines, so this is the same count
        # for an LF and a CRLF checkout of the same document.
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
        "--root", default=str(DEFAULT_ROOT),
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
    del mapped  # The function reports map mismatches; no second interpretation here.
    check_mentions(texts, actual, errors)
    if skill_text:
        check_reachability(skill_text, texts, actual, map_start, errors)
    check_stage_order(skill_text, texts.get("00-progress-router.md", ""), errors)
    check_archive(tree, skill_text, texts, errors, notes)
    check_policy_anchors(texts, errors)
    check_single_authority(texts, errors)
    check_restated_tier_policy(texts, errors)
    check_scripts(tree, texts, errors)
    check_size_budgets(texts, errors, warnings)

    # Empty active references are almost always an accidental placeholder.
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
