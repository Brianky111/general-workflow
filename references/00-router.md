# 路由与全局停止条件

本文件与 `SKILL.md` 常驻。先判提问或动手，再扫目标仓，每轮仅加载唯一业务 reference。

## 第一次判断

**问方法**直接答（不改仓）；**要动手**先跑 `repo_guard.py`：

```powershell
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --json
```

| `guard_status` | 含义 | 下一步 |
| --- | --- | --- |
| `invalid` | 护栏、驱动、地图或产物报错 | 先修报错，见 `06-repo-guard-contract.md` |
| `legacy_v1` | 缺 `.guardrails/` 但有旧状态 | 不覆盖旧文件，按 `06-repo-guard-contract.md` 迁移 |
| `uninitialized` | 无 `.guardrails/` 仓库 | 局部小改直入 `02`/`03` 最小实现并验证；建项走 `01-intent-and-invariants.md`，纳管旧仓先 `--scan` |
| `ready` | 护栏通过 | 按下表加载唯一 reference |

## 信任层级（L0–L3）

`config.json` 以 `trust_level` 标记信任阶段（唯一权威见 `05-outer-loop-factory.md`）：`L0` 起步棘轮、`L1` 产物内循环、`L2` 稳定外循环、`L3` 高信任自治。

## 路由表

每次按最紧迫缺口仅加载一份：

| 情境或信号 | 加载 |
| --- | --- |
| 未定意图/不变量/边界、Grill 追问、旧仓接管或 `prototype` | `01-intent-and-invariants.md` |
| 未定技术栈、跨模块深切分或编写 `ARCHITECTURE.md` | `01a-stack-and-architecture.md` |
| 状态真相源、数据流图/API 契约、失败上限或 `--check-arch` | `01b-dataflow-and-contracts.md` |
| 边界目录、防呆 API、Lint、重构减负或 `clean_scopes` | `02-codebase-guardrails.md` |
| Feature Map、`verify_cli`、修 Bug/性能/`hillclimb`/取证/PBT/TLA+ | `03-verification-and-artifacts.md` |
| 错重犯 `>= 2` 次、挖历史（`/reflect`/`/recall`）、质疑前提或瘦身 | `04-correction-and-gardening.md` |
| 升级层级、`clean_scopes` 解禁 Fuzz、双盲 `eval`、Bot 评论分流 | `05-outer-loop-factory.md` |
| 改 `.guardrails/`、`--check-arch`/`verify_cli` 报错或迁移 v1.x | `06-repo-guard-contract.md` |

仅在意图或不可逆边界改变时回 `01`；`01c`/`01d`/`01e` 仅由 `01a`/`01b` 按机械信号条件加载；测试或 `verify_cli` 不通回 `02`/`03` 修环境，不绕过。

## 主从分工与独立验收

多切片/跨模块任务（`vendor/pstack/skills/principle-guard-the-context-window/SKILL.md`）：主会话仅握意图、拆切片与跑 `repo_guard.py`；子代理写切片，交付前由独立 Verifier 按地图实跑留证。

## 内置 pstack 专项技能调度

按需加载 `vendor/pstack/`，不常驻：

| 任务 | 读取文件 | 用途 |
| --- | --- | --- |
| 错例证伪 | `vendor/pstack/skills/correct/SKILL.md` | 聚历史错例，改架构/Lint 并证伪 |
| 会话回流 | `vendor/pstack/skills/reflect/SKILL.md` | 纠偏入 Backlog，流程改 Skill |
| 跨会话记忆 | `vendor/pstack/skills/recall/SKILL.md` | 扫转录与 Git/Issue 输出胶囊 |
| 清借口注释 | `vendor/pstack/skills/no-comments/SKILL.md` | 配 `vendor/pstack/agents/comment-sicko.md` 拔根 |
| 去 AI 腔 | `vendor/pstack/skills/unslop/SKILL.md` | 短句直陈汇报与 PR 描述 |
| 写前对比 | `vendor/pstack/skills/architect/SKILL.md` | 比两方案，选单所有者与唯一做法 |
| 追溯历史 | `vendor/pstack/skills/why/SKILL.md` | 查提交讨论，区分证据与推断 |
| 缺陷排障 | `vendor/pstack/skills/poteto-mode/playbooks/bug-fix.md` | 真表面复现→二分插桩→红在前提交 |
| 性能优化 | `vendor/pstack/skills/poteto-mode/playbooks/perf-issue.md` | 七步低成本排序优化，早中即停 |
| 基准核验 | `vendor/pstack/skills/benchmark-checklist/SKILL.md` | 七问验限速器、调优、上限与中位 |
| 保行为重构 | `vendor/pstack/skills/poteto-mode/playbooks/refactoring.md` | 特征测试→删死码→降读者负担 |
| 抛弃原型 | `vendor/pstack/skills/poteto-mode/playbooks/prototype.md` | 隔离目录带开关变体，唯一反转阈值 |
| 运行取证 | `vendor/pstack/skills/poteto-mode/playbooks/runtime-forensics.md` | 活体插桩，离线看 `trace-forensics.md` |
| 离线取证 | `vendor/pstack/skills/poteto-mode/playbooks/trace-forensics.md` | 火焰图/堆快照转 SQLite 查符号 |
| 视觉对齐 | `vendor/pstack/skills/poteto-mode/playbooks/visual-parity.md` | 锁截图基准，像素 diff 归零 |
| 指标爬坡 | `vendor/pstack/skills/poteto-mode/playbooks/hillclimb.md` | 冻结基准、单变量、赢提交输回滚 |
| 双盲评测 | `vendor/pstack/skills/poteto-mode/playbooks/eval.md` | 盲目录+去泄露+异构 Judge |
| Bot 分流 | `vendor/pstack/skills/poteto-mode/references/bugbot-triage.md` | `fix / dismiss / ask` 核查，不盲从 |
| 验证 Skill | `vendor/pstack/skills/create-verification-skill/SKILL.md` | 建 `verify-<app>`；维护用 `maintain-verification-skill/SKILL.md` |
| 形式化/TLA+ | `vendor/pstack/skills/create-formal-verification-skill/SKILL.md` | 维护 `maintain-*`；状态图用 `statechart/SKILL.md` |

**跨工具屏蔽**：忽略 Cursor 私有项（`cursor-team-kit`、`/loop`、`origin pr`、`poteto-agent`、模型 slug）。`control-*`→`verify_cli`/宿主工具；`/deslop`→`unslop`+`no-comments`；`tdd`/`arena`→`03`/`architect`；未要 PR 跳过开 PR；`verify-<app>` 放 `.agents/skills/`；无命名子代理用 `comment-sicko.md`；`/recall` 仅扫本仓会话目录。

## 全局停止条件

遇以下任一条立即停下或交还：
- **完成即停（禁擅自扩项）**：明确需求与匹配验证通过即停，禁顺手重构无关代码、列假设待办或扩成全仓治理；
- **意图/不变量歧义**：同一句话有两种改变结果或数据正确性的解释；
- **不可逆边界**：资金/账务、隐私、鉴权放宽、不可逆迁移/删库或破坏公共契约；
- **环境损坏**：测试或构建无法运行，需外部凭据或改环境前提；
- **试图抬高旧债上限**：调大 `escape_hatches`、`anti_patterns` 或 `file_limits` 的 `max_allowed`；
- **单模块深潜止损**：同一模块连改 2 轮无进展，或主线未通想扩成内部重构；
- **顺手发现进停放区**：非阻塞旧债只追加一行到 `.guardrails/parking-lot.md`（见 `04`），不散弹深挖。

提问限四行、最多 1–2 个选择题（内部选型由 Agent 选最简可逆方案）：

```markdown
决策：<影响意图、不变量、安全或不可逆效果的问题>
候选：<2–3 项及差异>
推荐：<推荐项及理由>
代价：<所得与放弃；不可逆操作须明写>
```
