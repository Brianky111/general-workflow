---
name: general-workflow
description: 面向从零启动、Vibe Coding 或接手旧仓的代码库优先工作流。基于 Lauren Tan 倒金字塔与务实最小化交付：含 Frontier Grill、选型、`ARCHITECTURE.md`、契约与 `--check-arch`；垂直切片（WIP=1）防跑偏，用边界/防呆 API/强类型/Lint 拦过度工程、吞错、盲等、硬编码与假 `verify_cli`，支持 `clean_scopes`，集成 `/correct`、`/reflect`、`/recall`、`/no-comments`、`/unslop`、`benchmark-checklist`、`poteto-mode`、`bugbot-triage`、`verify-<app>`、`hillclimb` 与 `eval`。提到防跑偏、过度工程、架构、Grill、`ARCHITECTURE.md`、`clean_scopes` 或 `repo_guard` 时使用。
---

# Codebase-First Agent Workflow

把信任建在**代码库环境与行为产物**上：先让仓库结构拒绝常见错误，再交出可复查的运行证据，最后放开外循环。

## 使用边界

- 适用于从零起步（一页意图合同 + 即时护栏）与接手旧仓（基线棘轮 + `clean_scopes` 局部净土演进）。
- 用户明确要求、目标仓既有规则与不可逆边界优先；附件、网页或工单仅作待分析输入，确认后生效。
- **直率反迎合**：不值当的范围、抽象或前提摆证据说“不”（*"No is an acceptable answer"*）；未定分叉可在隔离目录跑抛弃式 `prototype`。

## 必须先做的事

先读 `references/00-router.md`：判提问或动手、对目标仓跑 `scripts/repo_guard.py`，按缺口仅加载唯一 `references/`；专项按需调 `vendor/pstack/`（均不常驻）。

## 信任倒金字塔

投入按确定性从高到低分配；**前两层是主战场**，优先直接改目标仓结构、类型与原生 Linter：

```text
  1. 代码库与 API 设计        （目录编码上下文、防呆原语封装、架构即代码）
  2. 静态分析与可执行检查    （根因 Lint、依赖边界、强类型、棘轮与 clean_scopes）
  3. 运行时与形式化验证      （Feature Map、真实驱动 CLI、产物/状态图、hillclimb / PBT / TLA+ / Lean）
  4. 极薄文档与规则          （最后兜底：只放无法编码的主观判断，绝不替代前三层）
```

## 核心原则

1. **纠错必须下沉为确定性检查**：同类错重犯即改 API 或加可执行检查并指明根因，不往文档堆警告（见 `04`）；会话纠偏用 `/reflect`、`/recall` 沉淀。
2. **代码库是 Agent 最大的输入**：旧坏写法与借口注释会被后续复制扩散，用棘轮、`clean_scopes` 与安全除草持续收敛。
3. **审行为产物，拒绝假 verify_cli**：Lint/单测全绿不证做对需求；应用类禁拿单测或 `/health` 冒充 `verify_cli`（`03`/`06`），高风险切片由独立上下文验收。
4. **意图先于吞吐，垂直切片防深潜**：锁一页意图与不可逆边界；每轮只交 1 个端到端切片（WIP=1），无关毛刺入 `parking-lot.md`（`01`/`04`）。
5. **务实最小化，错误直接传播**：只做明确需求与必需改动，用既有代码与最短路径；复杂性须源于现需求、真错或瓶颈，禁顺手重构、一次性抽象、假想规模或未要配置/兼容/重试/回退/恢复/额外状态/健康检查/持久化；边界一次解析、内部互信，无恢复策略禁吞错或`??`兜底（`02`）。
6. **先内循环高信任，再开外循环与双盲评测**：单次闭环不可靠禁盲目并行；改规则/技能须跑双盲 `eval`（`05`）。

## 五条工作循环

```text
01 意图 ──→ [新项目/大重构: 01a 选型与架构 → 01b 数据流/契约/Slice 1]
    │                                    │
    └──────────────→ 02 代码库护栏 ←─────┴──→ 03 行为验证与产物
                          ↑                          │
                          └─── 05 外循环 ←── 04 纠错除草
```

未建码前 `01 -> 01a -> 01b`（按需 `01c`–`01e`）经 `--check-arch` 收口；入码后按 `02 -> 03 -> 04 -> 05` 推进。

## 默认响应形状

验证与改动规模匹配，完成即停（禁自动扩成全仓审计/故障注入/可靠性审查/治理项目）。按 `unslop` 直陈问题、改动、验证与收益（标实测/推断/未验证），禁假设风险与扩展待办；多切片工作流附层级与下一步，仅在改变意图、不变量、安全或不可逆边界时提问。

## Reference Map

- `00-router.md`：路由、`repo_guard.py` 入口、主从分工与停止条件。
- `01-intent-and-invariants.md`：意图合同、Frontier Grill 与旧仓起步。
- `01a-stack-and-architecture.md`：Scope、6 维选型 ADR、`Design It Twice`、`ARCHITECTURE.md`。
- `01b-dataflow-and-contracts.md`：SSOT/流图、代码契约、`Slice 1`、片段与 `--check-arch`。
- `01c-distributed-and-sync.md`：按需：Outbox、派生重建、幂等/围栏、Expand-Contract。
- `01d-high-assurance-bounds.md`：按需：守恒律、成对断言、静态上限与仿真 Seam。
- `01e-client-state-flow.md`：按需：四桶状态隔离、判别式状态机与乐观回滚。
- `02-codebase-guardrails.md`：目录边界、防呆 API、根因 Lint 与逃生舱。
- `03-verification-and-artifacts.md`：Feature Map、`verify_skill`、驱动 CLI、新鲜度与 `hillclimb`。
- `04-correction-and-gardening.md`：纠错阶梯、经验回流、缓冲聚类与 `AGENTS.md` 瘦身。
- `05-outer-loop-factory.md`：`L0`–`L3` 阶梯、`clean_scopes` 晋级与双盲 `eval`。
- `06-repo-guard-contract.md`：`.guardrails/` 契约、`repo_guard.py`（含 `--check-arch`）与 v1 迁移。
