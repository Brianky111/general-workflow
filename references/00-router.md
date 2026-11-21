# 路由与全局停止条件

本文件与 `SKILL.md` 常驻上下文。先判断提问还是动手，再扫描目标仓库，每轮只加载唯一一份业务 reference。

## 第一次判断

分清**问方法**（直接回答，不改动目标仓）还是**要动手**（先运行 `repo_guard.py` 检查现状）：

```powershell
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --json
```

| `guard_status` | 含义 | 下一步 |
| --- | --- | --- |
| `invalid` | `.guardrails/` 存在，但护栏、驱动校验、地图或产物门禁报错 | 先修报错再推进；契约看 `06-repo-guard-contract.md` |
| `legacy_v1` | 缺 `.guardrails/`，但存在 `docs/workflow/` 或 `WORKFLOW-STATE.md` | 不覆盖旧文件；按 `06-repo-guard-contract.md` 迁移 |
| `uninitialized` | 新仓或未建护栏旧仓 | 跑 `--scan` / `--init` 锁棘轮，再进 `01-intent-and-invariants.md` |
| `ready` | 护栏校验通过 | 对照路由表加载唯一一份 reference |

## 信任层级（L0–L3）

`config.json` 用 `trust_level` 标记仓库信任阶段，本表只作状态索引：

| 层级 | 状态标签 | 说明去处 |
| --- | --- | --- |
| `L0` | 起步与棘轮期 | 唯一权威见 `05-outer-loop-factory.md` |
| `L1` | 产物审查内循环期 | 同上 |
| `L2` | 稳定基线外循环期 | 同上 |
| `L3` | 高信任自治期 | 同上 |

## 路由表

按当前最紧迫缺口每次只加载一份，禁止递归预加载：

| 当前情境或信号 | 加载 |
| --- | --- |
| 新项目未定意图/不变量/不可逆边界；或旧仓首次接管 | `01-intent-and-invariants.md` |
| 拆分边界目录、封装防呆 API、加原生 Lint 或配置 `clean_scopes` | `02-codebase-guardrails.md` |
| 建 Feature Map、写场景驱动型 `verify_cli`、做 `hillclimb` 爬坡或 PBT/TLA+/Lean | `03-verification-and-artifacts.md` |
| 同类错重犯 `>= 2` 次、挖对话历史（`/reflect`/`/recall`）、缓冲聚类或 `AGENTS.md` 瘦身 | `04-correction-and-gardening.md` |
| 升级信任层级、用 `clean_scopes` 局部解禁 Fuzzing、做双盲 `eval` 或复盘回退率 | `05-outer-loop-factory.md` |
| 修改 `.guardrails/`、处理 `project_kind`/`verify_cli` 报错或迁移 v1.x | `06-repo-guard-contract.md` |

- 仅当核心意图或不可逆边界改变时回 `01-intent-and-invariants.md`；日常加护栏和修实现去 `02`/`03`/`04`。
- 本地测试、`verify_cli` 或 `verify_skill` 跑不通时先回 `02`/`03` 修通可重复环境，禁绕过。

## 主从分工与独立验收

多切片或跨模块任务且宿主支持子代理时（参见 `vendor/pstack/skills/principle-guard-the-context-window/SKILL.md`）：

- **主会话（Coordinator）**：只握意图、拆原子切片与跑最终 `repo_guard.py` 门禁，不在海量细节探索或大批量改码中填满主上下文。
- **实现（Worker）与验收（Verifier）隔离**：尽量用干净上下文的子代理编写切片；交付前优先拉起未参与编写、无实现滤镜的独立 Verifier 子代理，按 `feature-map.md` / `verify_skill` 实跑找茬并截留产物。

## 内置 pstack 专项技能调度

按需加载 `vendor/pstack/`，绝不常驻：

| 专项任务 | 读取内置文件 | 核心用途 |
| --- | --- | --- |
| 错例聚类与证伪 | `vendor/pstack/skills/correct/SKILL.md` | 查提交/注释，改架构/Lint 并证伪旧错例 |
| 会话经验回流 | `vendor/pstack/skills/reflect/SKILL.md` | 审当前会话纠偏，规则进 Backlog、流程改 Skill |
| 跨会话记忆重建 | `vendor/pstack/skills/recall/SKILL.md` | 并行扫历史转录与 Git/Issue，输出一页当前状态胶囊 |
| 借口注释清理 | `vendor/pstack/skills/no-comments/SKILL.md` | 配合 `vendor/pstack/agents/comment-sicko.md` 改根因 |
| 写前架构对比 | `vendor/pstack/skills/architect/SKILL.md` | 对比两方案，选单状态所有者与唯一做法 |
| 追溯设计历史 | `vendor/pstack/skills/why/SKILL.md` | 查提交与讨论，区分证据与推断 |
| 单指标科学爬坡 | `vendor/pstack/skills/poteto-mode/playbooks/hillclimb.md` | 固定基准、单变量尝试、赢提交输回滚 |
| 规则/技能双盲评测 | `vendor/pstack/skills/poteto-mode/playbooks/eval.md` | 盲目录+去提示词漏泄+异构 Judge 盲评 |
| 生成/维护验证 Skill | `vendor/pstack/skills/create-verification-skill/SKILL.md` | 建 `verify-<app>`；维护用 `vendor/pstack/skills/maintain-verification-skill/SKILL.md` |
| 生成/维护形式化验证 | `vendor/pstack/skills/create-formal-verification-skill/SKILL.md` | 建形式化检查；维护用 `vendor/pstack/skills/maintain-formal-verification-skill/SKILL.md` |
| TLA+ 状态图检查 | `vendor/pstack/skills/statechart/SKILL.md` | 跑 `vendor/pstack/skills/statechart/scripts/statechart.ts` 输出状态图 |

跨工具适配：项目验证 Skill 放 `.agents/skills/verify-<app>`；无命名子 Agent 的宿主传入 `vendor/pstack/agents/comment-sicko.md` 作提示词；运行 `/recall` 时按当前宿主选转录根路径（Cursor `~/.cursor/projects/`、Claude `~/.claude/projects/`、Codex `~/.codex/sessions/`、Pi `~/.pi/agent/sessions/`，仅限当前工作区）。

## 全局停止条件

遇到以下任一条立即停下并确认，不用猜测做主：

- **意图或不变量歧义**：同一句话有两种改变用户结果或数据正确性的解释；
- **不可逆边界**：涉及资金/账务、隐私、鉴权放宽、不可逆迁移/删库或破坏性公共契约；
- **校验环境损坏**：测试或构建无法运行，需外部凭据或改环境前提；
- **试图抬高旧债上限**：唯一过检方式是调大 `escape_hatches`、`anti_patterns` 或 `file_limits` 的 `max_allowed`；
- **单模块深潜止损**：同一内部模块连改 2 轮仍无用户可见进展，或主线未通却想扩成多轮内部重构；
- **顺手发现进停放区**：非阻塞旧债或 P2/P3 毛刺只追加一行到 `.guardrails/parking-lot.md`（见 `04`），严禁当场顺藤深挖。

提问限四行且每次最多 1–2 个通俗选择题（技术内部选型由 Agent 选最简可逆方案拍板）：

```markdown
决策：<会改变意图、不变量、安全或不可逆效果的具体问题>
候选：<2–3 个可选项及各自行为差异>
推荐：<推荐选项及一句话理由>
代价：<接受什么、放弃什么；若涉及不可逆操作需明写>
```
