# 行为验证与验收产物

前两层护栏保证代码“结构没写烂”，但不能证明“做对了需求”。本文件定义低成本行为验证、真实场景驱动、独立验收与科学爬坡规范。

## 为什么审行为产物而不是逐行审 diff

Agent 能写出类型全对、Lint 全绿、单测全过，却把需求理解反了的代码（例如为修切换卡顿先清空消息再异步加载，导致用户每次看到半秒白屏）。且人眼逐行审大量 diff 跟不上吞吐。因此验收重心必须转向**审行为产物**（参见 `vendor/pstack/skills/principle-prove-it-works/SKILL.md` 与 `vendor/pstack/skills/principle-test-behavior-not-implementation/SKILL.md`）：

- 对比独立于实现的预期：**用户在什么前置条件下做了什么操作，应该观察到什么结果？**
- **早演示、早纠偏**：小切片完结即交出截图/录屏/试跑结果确认方向，核对无“就绪后人为干等”或“写死假数据”。
- **独立 Verifier 隔离验收**：大改动或高风险切片优先交给未参与编写该实现、不带实现滤镜的独立上下文子代理（见 `00-router.md`）按地图实跑挑刺并留证。
- **Bug 修复双面证伪与视觉像素对齐**：按 `vendor/pstack/skills/poteto-mode/playbooks/bug-fix.md` 在匹配真实表面复现 → 二分与运行时插桩排除假设 → 保持失败复现提交在修复提交之前；UI 重构或像素对齐按 `vendor/pstack/skills/poteto-mode/playbooks/visual-parity.md` 先截冻结基准图，图像 diff 归零才过关，禁改基准混过。
- 测试只断言用户或外部系统可观察结果，不绑死私有辅助函数或内部调用顺序。

## 用户视角 Feature Map

用用户视角地图消除 Agent 猜路径浪费的 token，按规模**二选一不双份维护**：

1. **紧凑单表模式（小型/早期应用）**：在 `.guardrails/feature-map.md` 记录 Feature、真实入口、`Verify CLI`、期望 `Artifact` 与 `core`/`secondary` 优先级。
2. **分片本地验证 Skill 模式（中大型应用推荐）**：按 `vendor/pstack/skills/create-verification-skill/SKILL.md` 生成项目本地 `verify-<app>`（如 `.agents/skills/verify-<app>/`）并配入 `config.json` `verify_skill`：
   - `SKILL.md`：含 YAML frontmatter 与 `Launch` / `Doctor` / `Drive` / `Evidence` / `Cleanup`；
   - `features/README.md`：索引所有功能文件，改哪个只读那一份；
   - `features/<slug>.md`：H1 功能名 + 固定四节 `Sub-features`、`How to get to it (user POV)`、`Driving it with <harness>`、`Gotchas`（次要标 `<!-- priority: secondary -->`）；
   - 应用演进后用 `vendor/pstack/skills/maintain-verification-skill/SKILL.md` 并发核查漂移并在单会话串行实跑全部路径。

新增或调整核心功能必须同步更新地图；前置缺失导致路径不通时按真实失败汇报，绝不削弱断言凑绿。

## 复用型验证 CLI 与调试通道

不要每次修改都让 Agent 现编临时脚本点界面。在项目内部（如 `tools/verify.py` 或 `scripts/verify/`）沉淀**可复用的场景驱动 CLI**：

- **禁止拿单测或浅探针冒充 `verify_cli`**：对于常规应用（默认 `project_kind: "app"` 且未配 `verify_skill`），禁止直接把 `pytest`/`vitest`/`npm test`、纯 `/api/health` `/healthz` `/ping` 探针或照抄 `check_command` 填进 `verify_cli` 或 `core` 行 Verify CLI（`repo_guard.py` 会在起步层发警告、在更高层级直接报错拦截）。纯底层库若确无独立场景驱动器，须在 `config.json` 显式声明 `"project_kind": "library"`。
- **真实驱动器必备能力**：干净启动并准备数据 → 确认可用而非仅端口监听 → 走完端到端用户路径 → 输出日志/耗时/截图/录屏；优先用 ARIA 标签、路由或稳定 ID，不用脆性像素坐标。
- **`Doctor` 只读自检**：提供只读子命令检查进程、构建匹配、端口与鉴权是否值得继续驱动；异常先跑 `Doctor`。
- **隔离与清理不毁证**：明确并行端口/数据目录隔离；`Cleanup` 只回收本次子进程与临时状态，保留产物文件；验证 CLI 自身纳入 `source_roots` 与静态检查保护。

## 科学性能与指标爬坡（Hillclimb）

针对一次性性能修复与持续量化调优，均须以真实负载测量为依据而非凭读代码猜瓶颈：

1. **按成本排序的性能七步与数字七问**：一次性性能排障按 `vendor/pstack/skills/poteto-mode/playbooks/perf-issue.md` 依序尝试：*Don't do it → Don't do it again → Do it less → Do it later → When not looking → Concurrently → Cheaper*，早命中即停。信任或汇报任何延迟、吞吐、加速比或 Eval 数字前，先过 `vendor/pstack/skills/principle-explain-the-number/SKILL.md` 与 `vendor/pstack/skills/benchmark-checklist/SKILL.md`（限速器 *Why not double?*、生产态调优对等、理论算术上限、错误与真跑核验、`>= 5` 轮 A/B 交替中位数与端到端占比）；活体插桩或离线大体积火焰图/堆快照先按 `vendor/pstack/skills/poteto-mode/playbooks/runtime-forensics.md` 或 `vendor/pstack/skills/poteto-mode/playbooks/trace-forensics.md` 在子代理转入 SQLite 查询定位源码符号。
2. **Hillclimb 冻结基准爬坡循环**：针对持续调优按 `vendor/pstack/skills/poteto-mode/playbooks/hillclimb.md` 执行：先冻结可拉开好坏的测量脚本并绑回归门禁（迭代禁改口径），每次只验证一个假设，指标跨过噪声且门禁全绿才提交，否则完整回滚，每轮记入被 gitignore 的 `decision.tsv`，达到双停止条件即止，保留不降指标的简化删减。

## 行为产物与新鲜度门禁

本节是本工作流中**行为产物要求与校验新鲜度规则的唯一权威**，其他文档只引用本节。

1. **每条核心验证必须产出可复查的行为产物**：记录在 `.guardrails/verification.md` 时，只写“测试通过”“已验证正常”等同于未验证，必须同时给出真实执行命令、具体观察结果，以及指向真实存在且非空的产物文件（或可访问的运行记录链接）。
2. **视觉或复杂交互优先交录屏、截图或用户视角状态图**：对于 UI 渲染、动画转场、跨页面状态流，单纯一行文字或退出码判断不了体感是否突兀；必须附上录屏、关键帧截图或自动生成的用户视角状态转换图（State Chart），让人直接审查行为本身。
3. **验证记录必须锚定不可变 commit，代码改动后旧绿灯即失效**：“之前跑通过”不代表“现在这版代码也通过”。只要源码发生新提交或存在未提交修改，旧的验证记录就失去新鲜度；升到高信任自动合入或合并前，必须携带 `--check-head` 重验到当前 `HEAD`。
4. **禁止用 HEAD、main 或 later 冒充验证锚点**：提交列必须写具体不可变 SHA（如 `a1b2c3d`）或不可变发布 tag；任何会漂移的分支名、相对引用或“稍后补上”都会被 `repo_guard.py` 拒绝。

## 深度验证：PBT 与形式化验证

需要时用 `vendor/pstack/skills/create-formal-verification-skill/SKILL.md` 生成本地形式化验证 Skill，并用 `vendor/pstack/skills/maintain-formal-verification-skill/SKILL.md` 随提交同步，防模型假绿：

| 信号与风险 | 推荐武器 | 产出与检查方式 |
| --- | --- | --- |
| 复杂 UI 乱点/连击状态错乱 | **UI PBT**（Bombadil、fast-check） | 随机序列不崩不白屏，留可重放序列与录屏 |
| 账本计算、状态机、解析与幂等 | **属性测试**（Hypothesis、fast-check） | 验证 `01` 不变量在数千随机输入下成立 |
| 多端同步、通知并发乱序 | **TLA+** + `vendor/pstack/skills/statechart/SKILL.md` | 跑 `statechart.ts` 抓反例路径并导出状态图 |
| 高复杂度核心算法（虚拟列表/调度） | **Lean / 形式化证明** | 机器核查不变量并在破损变更上证明能红 |

## 验证门禁

声称功能交付前核对：

1. 全部 `core` 功能已入 `.guardrails/feature-map.md` 或 `verify_skill`，对应驱动命令实跑通过；
2. `.guardrails/verification.md` 覆盖全部 `core` 功能，均有观察结果、非空产物及不可变 commit 锚点；
3. 缺陷修复已双面证伪；高风险并发/状态流已补深度验证或状态图；
4. 运行 `python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --run-check` 退出 `0`（高信任分支同时加 `--check-head`）。
