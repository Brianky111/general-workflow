# 路由与全局停止条件

本文件与 `SKILL.md` 常驻上下文。每轮先判断该不该写文件，再用状态脚本读出目标仓库现状，最后只加载一份业务 reference。

## 第一次判断

先分清用户是在**问方法**还是**要动手**：只问方法或原理时直接回答，不在目标仓库新建或改动任何文件；要改代码、建护栏或验收时才进入检查与写入路径。

动手前，先对目标仓库运行随本 skill 分发的检查脚本（`--root` 显式指向目标项目绝对路径）：

```powershell
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --json
```

根据返回的 `guard_status` 决定入口：

| `guard_status` | 含义 | 下一步 |
| --- | --- | --- |
| `invalid` | 存在 `.guardrails/`，但护栏检查、逃生舱上限、特征地图或产物门禁报错 | 先修报错再推进新功能；契约问题看 `06-repo-guard-contract.md` |
| `legacy_v1` | 未建 `.guardrails/`，但发现旧版 `docs/workflow/` 或 `WORKFLOW-STATE.md` | 不覆盖旧文件；按 `06-repo-guard-contract.md` 迁移后再继续 |
| `uninitialized` | 新仓库或尚无 `.guardrails/` 的已有仓库 | 加载 `01-intent-and-invariants.md`，立一页意图并建最小护栏 |
| `ready` | `.guardrails/` 配置和基础校验通过 | 对照下表选一份 reference 执行本轮任务 |

## 信任层级（L0–L3）

`config.json` 用 `trust_level` 标记目标仓库所处的工程信任阶段：

| 层级 | 状态标签 | 说明去处 |
| --- | --- | --- |
| `L0` | 起步与棘轮期 | 详细前置与约束见 `05-outer-loop-factory.md` |
| `L1` | 产物审查内循环期 | 同上，以该文件为唯一权威 |
| `L2` | 稳定基线外循环期 | 同上，以该文件为唯一权威 |
| `L3` | 高信任自治期 | 同上，以该文件为唯一权威 |

本表只作状态索引，不在此重复定义各层级的权限、自动化边界或升级门禁。

## 路由表

按当前最紧急的工程缺口选一份加载；一轮只读一份，不递归预加载其余文件：

| 当前情境或信号 | 加载 |
| --- | --- |
| 新项目尚未说清用户、核心结果、不变量与不可逆边界；或接手无 `.guardrails/` 的旧仓 | `01-intent-and-invariants.md` |
| 需要拆分跨进程/运行时目录、封装防呆 API、加自定义 Lint 或依赖边界规则 | `02-codebase-guardrails.md` |
| 需要建立 Feature Map、封装验证 CLI、产出录屏/截图/状态图，或评估 PBT/TLA+/Lean | `03-verification-and-artifacts.md` |
| 同一类错误或坏习惯出现第二次、评审反复抓到同类问题、要集中除草或给 `AGENTS.md` 瘦身 | `04-correction-and-gardening.md` |
| 准备升级 `trust_level`、接入发版后 Fuzzing 或规则自动合入、复盘回退率与体验指标 | `05-outer-loop-factory.md` |
| 初始化或修改 `.guardrails/` 文件、排查 `repo_guard.py` 报错、迁移 v1.x 状态目录 | `06-repo-guard-contract.md` |

注意防伪：

- 只有需求、核心不变量、安全边界明确改变时，才回 `01-intent-and-invariants.md` 更新意图；日常加检查与修实现直接去 `02`/`03`/`04`。
- 如果发现已有 `L1`–`L3` 项目的测试命令、`verify_cli` 或 `verify_skill` 无法在本地运行，先回到 `02` 或 `03` 修通可重复环境，不绕过检查硬推进。

## 内置 pstack 专项技能调度

仓库内置 `vendor/pstack/`（Lauren Tan 的核心 `pstack` 技能集）；除本文件与 `SKILL.md` 外，按当前任务按需加载对应技能文件：

| 专项任务 | 读取内置技能文件 | 说明 |
| --- | --- | --- |
| 历史错例聚类与结构化根治 | `vendor/pstack/skills/correct/SKILL.md` | 翻 commits/reverts/注释，按倒金字塔落架构/类型/Lint 并做旧错例证伪 |
| 清理借口注释与抑制指令 | `vendor/pstack/skills/no-comments/SKILL.md` | 配合 `vendor/pstack/agents/comment-sicko.md` 猎杀冗余注释并修根因 |
| 写前架构对比（2 种方案） | `vendor/pstack/skills/architect/SKILL.md` | 对比类型、签名与边界，选出单状态所有者与唯一做法 |
| 追溯历史设计原因 | `vendor/pstack/skills/why/SKILL.md` | 读提交记录与 PR 讨论，区分已证实事实与推断 |
| 生成项目本地验证 Skill | `vendor/pstack/skills/create-verification-skill/SKILL.md` | 生成带 `features/*.md` 的 `verify-<app>` 并当场试跑 |
| 巡检维护验证 Skill | `vendor/pstack/skills/maintain-verification-skill/SKILL.md` | 并行源读 + 串行实跑全部功能，区分文档漂移与产品回归 |
| 生成与维护形式化验证 Skill | `vendor/pstack/skills/create-formal-verification-skill/SKILL.md` | 配合 `vendor/pstack/skills/maintain-formal-verification-skill/SKILL.md` |
| 跑 TLA+ 状态图与反例路径 | `vendor/pstack/skills/statechart/SKILL.md` | 运行 `vendor/pstack/skills/statechart/scripts/statechart.ts` 输出 Mermaid 图 |

跨工具适配（Claude Code / Codex / OpenCode / T3 Code）：生成项目本地验证 Skill 时使用中立目录（如 `.agents/skills/verify-<app>`）并在 `.guardrails/config.json` 的 `verify_skill` 登记；若当前宿主没有命名 `comment-sicko` 子 Agent，直接把 `vendor/pstack/agents/comment-sicko.md` 作为只审注释的子 Agent 提示词传入。

## 全局停止条件

遇到以下任意一条立即停下并向用户确认，不用猜测替用户做主：

- **意图或核心不变量歧义**：同一句话有两种会改变用户可见结果或数据正确性的解释；
- **不可逆边界**：改动涉及资金/账务、隐私合规、鉴权放宽、不可逆数据迁移/删库或破坏性公共 API；
- **校验环境损坏**：基础构建、测试或依赖无法安装运行，需要外部凭据或修改环境前提；
- **试图抬高旧债上限**：当前改动唯一能过 `repo_guard.py` 的方式是调大 `escape_hatches.max_allowed` 或关掉既有检查（永远不允许静默抬限）。

向用户提问只用以下四行，不问“请确认全部细节”：

```markdown
决策：<会改变意图、不变量、安全或不可逆效果的具体问题>
候选：<2–3 个可选项及各自行为差异>
推荐：<推荐选项及一句话理由>
代价：<接受什么、放弃什么；若涉及不可逆操作需明写>
```

一般性的命名偏好、内部文件拆分方式、非核心优化不阻塞推进，做完后在汇报中附带说明即可。
