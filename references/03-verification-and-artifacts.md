# 行为验证与验收产物

前两层护栏保证了代码“结构没写烂、没违规”，但完全不能证明“做对了用户要的东西”。本文件定义如何低成本地验证真实行为、产出让人一眼看懂的产物，并在高风险处使用深度验证。

## 为什么审行为产物而不是逐行审 diff

Agent 完全可以写出格式完美、类型全对、Lint 全绿、单元测试全过，却把用户需求理解反了的代码。举个常见例子：你让 Agent“修一下切换聊天时的卡顿”。它先把旧消息清空再异步加载，点击回调确实快了，单测也全绿——但用户每次切换都要看半秒白屏闪动。

只看代码 diff 很难一眼发现这种体验缺陷；或者反过来，人为审查几千行 PR diff 根本跟不上 Agent 的产出速度。因此审查的重心必须从“逐行看源码”转向**审行为产物**（对照 `vendor/pstack/skills/principle-prove-it-works/SKILL.md` 与 `vendor/pstack/skills/principle-test-behavior-not-implementation/SKILL.md`）：

- 对比独立于实现的预期：**用户在什么前置条件下做了什么操作，应该观察到什么结果？**
- **早演示、早纠偏**：每个小垂直切片完成后立即交出截图/录屏/试跑结果让用户确认产品方向，同时当场核对不存在“数据已就绪却人为干等（如 1.5s 固定遮罩）”或“页面写死假数据冒充成功”。
- 针对可复现的 bug 修复，执行**证伪检查**：把新写的验证或复现测试放回修复前的提交跑一遍，它必须失败；放回当前修复后，它必须通过。旧提交也绿的测试不能证明修复有效。
- 测试只断言用户或外部系统可观察的结果，不绑死私有辅助函数或内部调用顺序；能用两类破坏性假设检验每一条测试——打坏行为时必须失败、只改内部实现时必须保持通过。

## 用户视角 Feature Map

`AGENT` 在写代码或验证时最常浪费 token 的地方，是靠猜去翻整个仓库找“用户说的左边栏那个导出按钮到底对应哪段代码”。按仓库规模选一种形态作为人与 Agent 的共享词汇表，**二选一不双份维护**：

1. **紧凑单表模式（小型应用 / 早期起步）**：在 `.guardrails/feature-map.md` 维护一张用户语言清单（功能名、真实入口、`Verify CLI`、期望 `Artifact` 与 `core`/`secondary` 优先级）。
2. **分片项目本地验证 Skill 模式（中大型应用推荐）**：按 `vendor/pstack/skills/create-verification-skill/SKILL.md` 生成项目本地的 `verify-<app>` 目录（如 `.agents/skills/verify-<app>/`），并在 `.guardrails/config.json` 配置 `verify_skill` 路径：
   - `SKILL.md`：含 YAML frontmatter 与 `Launch` / `Doctor` / `Drive` / `Evidence` / `Cleanup` 章节；
   - `features/README.md`：索引同目录下所有功能文件，修改哪个功能就只读那一份；
   - `features/<slug>.md`：每个用户可见功能一份文件（H1 为功能名，固定顺序四节：`Sub-features`、`How to get to it (user POV)`、`Driving it with <harness>`、`Gotchas`；非核心功能可加 `<!-- priority: secondary -->`）。
   - 应用变更后用 `vendor/pstack/skills/maintain-verification-skill/SKILL.md` 巡检：为每个 feature 并发派出只读源读 Agent，再由协调者用单个会话串行实跑全部功能，严格区分文档漂移（改 map）与产品回归（报缺陷不掩盖）。

每次新增或调整核心用户功能，必须同步更新对应地图；前置条件或种子数据缺失导致路径不可达时，按真实失败汇报并将前置记录到 `Gotchas`，绝不为凑通过而削弱验证路径。

## 复用型验证 CLI 与调试通道

不要每次修改都让 Agent 现编一段临时 Playwright/curl 脚本去点界面——那样既费 token，又极其脆弱，每次会话都要重摸一遍。参考 Grok Bot 与 `create-verification-skill` 的做法，在项目内部（例如 `tools/verify.py` 或 `scripts/verify/`）沉淀一个**可复用的验证 CLI / Driver**：

- 封装好“从空数据目录干净启动并完成迁移/种子数据 → 确认可用而非仅端口监听 → 走完用户真实路径 → 抓取日志/性能数字/截图/录屏”的固定命令，优先使用 ARIA 标签、路由等稳定句柄而非易碎的坐标或 CSS 选择器；
- **`Doctor` 只读自检**：提供一条快速只读命令回答“当前实例是否值得继续驱动”（进程存活、版本/构建匹配、端口归属、鉴权有效），任何异常先跑 `Doctor` 再重跑；
- **实例隔离与清理不毁证**：明确多实例能否并行（端口、数据目录、profile）；`Cleanup` 只回收本次启动的进程与临时状态（不按进程名误杀），且必须保留证明产物文件；
- 验证 CLI 自身也是仓库代码的一部分，受同一套测试与静态检查保护，每次修 bug 或加功能顺手给它加一个子命令。

## 行为产物与新鲜度门禁

本节是本工作流中**行为产物要求与校验新鲜度规则的唯一权威**，其他文档只引用本节。

1. **每条核心验证必须产出可复查的行为产物**：记录在 `.guardrails/verification.md` 时，只写“测试通过”“已验证正常”等同于未验证，必须同时给出真实执行命令、具体观察结果，以及指向真实存在且非空的产物文件（或可访问的运行记录链接）。
2. **视觉或复杂交互优先交录屏、截图或用户视角状态图**：对于 UI 渲染、动画转场、跨页面状态流，单纯一行文字或退出码判断不了体感是否突兀；必须附上录屏、关键帧截图或自动生成的用户视角状态转换图（State Chart），让人直接审查行为本身。
3. **验证记录必须锚定不可变 commit，代码改动后旧绿灯即失效**：“之前跑通过”不代表“现在这版代码也通过”。只要源码发生新提交或存在未提交修改，旧的验证记录就失去新鲜度；升到高信任自动合入或合并前，必须携带 `--check-head` 重验到当前 `HEAD`。
4. **禁止用 HEAD、main 或 later 冒充验证锚点**：提交列必须写具体不可变 SHA（如 `a1b2c3d`）或不可变发布 tag；任何会漂移的分支名、相对引用或“稍后补上”都会被 `repo_guard.py` 拒绝。

## 深度验证：PBT 与形式化验证

过去属性测试（Property-Based Testing）和形式化方法因为编写与维护太昂贵，只在少数底层系统里出现；Agent 把编写成本打下来之后，它们变成了高性价比的防线。需要时可用 `vendor/pstack/skills/create-formal-verification-skill/SKILL.md` 生成并证明项目本地形式化验证 Skill，用 `vendor/pstack/skills/maintain-formal-verification-skill/SKILL.md` 随代码提交同步，禁止“代码已改但旧模型继续假绿”。

| 信号与风险 | 推荐武器 | 产出与检查方式 |
| --- | --- | --- |
| 复杂 UI 交互、任意乱点/快速连击导致状态错乱或白屏 | **UI 属性测试（PBT）**，如 Bombadil、fast-check 驱动交互序列 | 随机动作序列不得触发崩溃、白屏或非法 UI 状态，失败保留可重放序列与录屏 |
| 账本计算、状态机转换、解析器/序列化、幂等重试 | **属性测试（PBT）**，如 Hypothesis、fast-check | 直接验证 `01` 写下的不变量在数千组随机输入下成立，失败用例固化成回归单测 |
| 多端同步、通知投递、并发乱序、分布式状态协作 | **TLA+ 模型检测** + `vendor/pstack/skills/statechart/SKILL.md` | 运行 `vendor/pstack/skills/statechart/scripts/statechart.ts` 抓反例最短路径并导出用户视角 Mermaid 状态图 |
| 高复杂度核心自研算法（如虚拟列表、布局排布、调度器） | **Lean / 形式化证明** | 对关键无闪烁、单调性或不变量做机器可核查证明，在破损变更上证明能红并记录同步 commit |

## 验证门禁

离开本阶段或声称某项功能交付前，逐项核对：

1. 所有 `core` 级功能已登记在 `.guardrails/feature-map.md` 或 `verify_skill` 目录，且对应验证命令已当场跑通（`verify_skill` 须满足索引卫生、4-H2 结构与清理留证）；
2. `.guardrails/verification.md` 覆盖全部 `core` 功能，每行均有具体观察结果、非空磁盘产物（或运行链接）及不可变提交锚点；
3. 若本次是修可复现缺陷，已确认新校验在旧提交失败、在当前提交通过；涉及并发/状态机/复杂 UI 的已补相应深度验证与状态图；
4. 运行 `python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --run-check` 退出码为 `0`（高信任分支同时加 `--check-head`）。
