# 纠错下沉与主动除草

代码库是一座持续生长的花园：人工纠错若不下沉为确定性约束，下一轮仍会重犯；留存的坏样例与借口注释会被后续 Agent 指数级复制。

## 倒金字塔纠错阶梯

本节是本工作流中**纠错沉淀优先级阶梯的唯一权威**，其他文档只引用本节。

1. **纠错按倒金字塔从上到下尝试，最后才写 AGENTS.md**：每次你发现自己第二次提醒 Agent 同一个问题，立刻停下来做下沉（参见 `vendor/pstack/skills/principle-encode-lessons-in-structure/SKILL.md`），而不是给提示词加一句“请务必注意”。
2. **第一步：收窄或重写 API，让错误写法在结构上不可表达**：优先问“能不能改掉接口签名、私有化内部字段或合并原子操作，使错误调用连编译/类型检查都过不去？”能靠结构消灭的错，不留给检查器。
3. **第二步：加一条带根因修复提示的静态检查或依赖规则**：当语言类型表达不了时，优先加进目标项目的原生 Lint / AST 依赖检查并接进 `check_command`，再用 `.guardrails/config.json` 的 `forbidden_primitives` / `boundary_rules` 兜底，并按 `02-codebase-guardrails.md` 写明该改用哪个接口。
4. **第三步：清理仓库里同源旧坏样例，阻止后续 Agent 模仿**：规则写完立刻在仓内搜索同类旧写法并清理，或收紧棘轮上限。留着坏样例，下一批 Agent 还会照抄并试图用注释绕过检查。
5. **第四步：补运行时验证、PBT 或形式化不变量**：若问题是时序、并发或用户体感偏差，把复现脚本固化进 `verify_cli` / `verify_skill`，必要时补属性测试或状态机模型检测（见 `03-verification-and-artifacts.md`）。
6. **第五步：只有无法编码的主观判断才写入极简 AGENTS.md**：仅保留领域术语、产品审美取舍、外部协作流程等静态分析和运行时测试实在表达不了的内容。

反例对比：发现 UI 组件直接用 `setTimeout` 修竞态。差的做法是在 `AGENTS.md` 加“不要乱用定时器”；好的做法是封 `scheduleDebouncedAction` API → 原生 Lint / `forbidden_primitives` 禁裸 `setTimeout` → 清掉旧 `setTimeout` → `AGENTS.md` 一字不加。

## 历史错误聚类与旧错例证伪（/correct 闭环）

日常反复踩坑或接手老仓时，必须同时从**代码提交记录**与**会话转录历史**两条腿找证据：

1. **会话经验回流（`/reflect` 与 `/recall`）**：很多纠正发生在 `git commit` 之前的对话拉扯中，最终代码改好了，Commit 里却毫无痕迹。
   - **当场复盘用 `reflect`（`vendor/pstack/skills/reflect/SKILL.md`）**：会话结束或被人工打断纠偏后通读转录，只保留半年后仍成立的教训；**凡是能靠脚本或 Lint 拦住的，直接转入护栏 Backlog 走倒金字塔前两层，不写进散文**；只有流程/触发盲区才建议修改对应 Skill 并经用户批准后落盘。
   - **跨会话接手用 `recall`（`vendor/pstack/skills/recall/SKILL.md`）**：恢复长尾模块前，并行扫近期本工作区聊天转录与 Git/Issue 共有记录（用户反馈、曾被 revert 的修复），先摸清历史雷区再动手。
2. **代码错例聚类与证伪（`/correct`）**：按 `vendor/pstack/skills/correct/SKILL.md` 与 `vendor/pstack/skills/principle-fix-root-causes/SKILL.md` 汇总 commits、reverts、评审意见与 workaround 注释；**同类错误出现 ≥ 2 次即立项**，一类一提交：
   - **优先架构与最高层**：先改单状态所有者/唯一做法/删旧 API，再收窄类型，再加直指替代接口的原生 Lint（同时用 `/no-comments` 清衍生借口）；
   - **强制旧错例证伪回放**：每条新建类型约束、Lint、边界规则或回归测试交付前，**必须拿过去一次真实犯错提交或复现片段证伪它能红灯拦截**；旧错还能绿灯通过的检查一律作废重写；
   - **本地与 CI 同命令，例外带期限**：有豁免必须在违规行旁注明原因、过期日期与批准人，收尾说明历史证据、选定层级及高层无法消除的原因。

## 反深潜熔断与停放区（Anti-Rabbit-Hole）

防“越修越深、主线搁浅”与常规需求下的顺手重构扩项：

1. **主线高于重构，常规需求禁顺手重塑**：常规功能或修 Bug 回合**禁止顺手重构无关代码、扩张范围或主动发起全仓除草治理**；主流程未跑通或当前垂直切片未交出可看结果前，**严禁**开启纯内部重构；护栏与 `/correct` 只在**当前需求明确要求治理**、**加规则收口同源违规**或**同源痛点已重犯 `>= 2` 次**时介入。
2. **缓冲聚类停放区（`.guardrails/parking-lot.md`）**：推进主线时撞见的非阻塞旧债、P2/P3 毛刺，仅在仓内已启用 `.guardrails/` 时追加一行记入 `.guardrails/parking-lot.md`（来源/路径/现象）而不当场散弹打补丁；需求满足并验证通过即停。同类条目攒够 **≥ 2 条** 且获处理授权时再集中走 `/architect` + `/correct` 根治。
3. **单模块 2 轮止损与质疑前提（`attack-the-premise`）**：同一内部模块连改 2 轮仍无用户可见推进，或共享同一前提的修复连续 `>= 2` 次败在同一门禁时，立即停手写补丁，按 `vendor/pstack/skills/principle-attack-the-premise/SKILL.md` 用一句话写出共同前提并直接观测证伪它，再决定换极简替代方案或升级回报。
4. **拒绝重型脚手架失衡**：十几行小改动不配数百行特征测试或繁重兼容层，维持最小可验证变动，验证与改动规模匹配即停。
5. **非琐碎除草先造可重跑杠杆**：多处同源清理或结构检查按 `vendor/pstack/skills/principle-build-the-lever/SKILL.md` 先在首个单元验通，再写成可重跑脚本/codemod 执行并随证保留。

## 主动除草与棘轮协议

旧工程惯例要求“改功能不碰旁边的旧代码”，在 Agent 时代会产生致命副作用：脏代码留在上下文里就会被下一轮模仿。但需严格区分**常规需求回合**与**专责加规则/除草回合**：

- **常规需求回合**：禁顺手重构无关旧码；已启用 `.guardrails/` 时只记入 `parking-lot.md`，当前需求完成且必要验证通过即停；
- **安全除草（仅在新增某条规则、`/correct` 治理重犯 `>= 2` 次的错例或明确除草任务时执行）**：在全绿检查保护下，把明确违规的同源坏模式机械替换成受控新 API，拔除空壳包装、历史兼容垫片或拆分超长巨石文件（`file_limits`），不改变公开契约与用户可见结果；
- **涉及行为变更的清理**：会改变接口语义或用户流程的改动走 `01-intent-and-invariants.md` 确认后正常验证交付。

体量较大的老仓采用**三维棘轮协议（Ratchet）**，覆盖 `escape_hatches`、`anti_patterns` 与 `file_limits`（含逐文件 `baseline_files`）：

1. 用 `--scan` / `--init` 把当前存量锁定进各自 `max_allowed` 与 `baseline_files`；
2. 任何新改动不得突破上限，已建档巨石文件只许变瘦、新文件不得超过 `max_lines`；
3. 清理一批旧债或把目录彻底净化并加入 `clean_scopes` 后，立即按 `repo_guard.py` 提示下调 `max_allowed` 并从 `baseline_files` 摘除；
4. 直到全仓归零（或局部干净目录先锁死 `clean_scopes` 享受局部自动化）。

## AGENTS.md 瘦身规则

`AGENTS.md` 只维护一张简洁的 **`Rule | Enforcer`** 对照表：

- 某条 `Enforcer` 标为 `unenforced` 的规则只要再被纠正一次，**必须在同一变更内**按倒金字塔推进到结构/类型/Lint 层；
- 已被结构彻底消灭的禁令（旧 API 已删、类型已卡死）**立即从表和文档删掉**。

`repo_guard.py` 默认将受检文档限制在 `6,000` 字节以内，并在出现 ≥ 3 条自然语言禁令时发出警告。

## 除草门禁

纠错或除草收尾前核对：

1. 重复问题已下沉至目标仓 API、强类型或原生确定性检查，而非只加提示词；聊天中产生的新规律已用 `/reflect` 分流进 Backlog 或特定 Skill；
2. 每条新建检查均经过**真实历史错例证伪回放**，带清楚根因修法，同源旧坏样例已清理或锁入棘轮/`clean_scopes`；
3. `AGENTS.md` 体积未超标且无已过时禁令；`.guardrails/parking-lot.md` 未演变成失控的散弹重构；
4. 运行 `repo_guard.py --run-check` 退出码为 `0`，行为改动已同步更新 `.guardrails/verification.md`。
