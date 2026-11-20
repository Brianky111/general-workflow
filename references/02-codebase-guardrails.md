# 代码库护栏设计

倒金字塔最底端（投入回报比最高的两层）是**代码库结构**与**确定性静态检查**。核心思路是直接改造目标仓库自身的类型、API、目录与原生 Linter，把“希望 Agent 记住的规范”变成“写错就编译失败或 Lint 直接报出正确用法”的物理边界。

## 目录即上下文

Agent 很容易在大型仓库里搞混一段代码到底运行在哪个进程、哪个信任域或哪个阶段。不要在文档里苦口婆心提醒“A 文件只在服务端运行”，直接把运行上下文写进顶层目录名，并用依赖规则锁死：

- **写前架构对比与单源真相**：非平凡改动动手前按 `vendor/pstack/skills/architect/SKILL.md` 对比至少两种接口/边界形状，优先选“每份状态只有一个所有者、每件事只有一种受支持做法、调用方需要知道最少”的方案，并用单一事实源替代手工同步列表。
- **进程与运行时边界**：如 `electron-main/` 与 `electron-renderer/`、`server/` 与 `client/`、`worker/` 与 `web/`；跨目录导入直接被工具拦掉，强制走明确声明的 IPC/API 契约。
- **领域与基础设施边界（Boundary Discipline）**：参照 `vendor/pstack/skills/principle-boundary-discipline/SKILL.md`，在系统边界（CLI 参数、配置、网络、外部 API）完成解析、类型收窄与错误处理，外部传输类型不外泄到公共接口；核心业务逻辑写成无框架依赖的纯函数，由 `core/api/` 暴露唯一安全入口，外部不得绕过直连 `core/storage/`。
- **共享原语约束**：`shared/` 只放无业务归属的纯类型或纯工具函数，防止成为绕过依赖方向的垃圾桶。

在 `repo_guard.py` 中用 `.guardrails/config.json` 的 `boundary_rules` 声明这些跨目录禁令；项目规模增大、出现路径别名或桶文件重导出时，再升级为 `dependency-cruiser`（JS/TS）或 `import-linter`（Python）等 AST 级依赖图工具并挂入 `check_command`。

## 业务层禁用高分寸感原语

有些语言或框架特性本身合法，但**需要极高的分寸感（nuance）才能写对**。人类靠多年经验避坑，Agent 却会频繁滥用并迅速放大成灾难：

- React 中的 `useEffect`（派生状态、竞态清理极易写错）→ 业务组件禁用，仅在 `src/runtime/` 或框架封装 hook 内白名单放行；
- 裸异步定时器 `setTimeout` / `requestAnimationFrame` / `time.sleep` → 禁止在业务逻辑里用它们“等一下凑时序”，由统一的事件/调度原语封装；
- 裸 SQL 字符串拼接、直接读写 `os.environ` / `process.env`、跳过状态机直接修改状态字段 → 统一收口到带校验的安全封装层。

同时落实类型与迁移纪律：按 `vendor/pstack/skills/principle-type-system-discipline/SKILL.md` 用类型系统把非法状态变成编译期错误、为易混原始值赋予独立品牌类型、由权威 Schema 派生类型；引入新内部 API 时按 `vendor/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md` 在同一波迁移全部调用方并删掉旧接口，绝不留兼容残骸让下一轮 Agent 复制。先做唯一正确的简洁 API，再用 `forbidden_primitives`（配 `allow_paths` 白名单）或原生 Lint 把危险原语彻底封杀。

## 反过度工程、反防御性吞错与反硬编码

AI 在无人约束时最容易把简单需求写重、用静默兜底把 Bug 藏起来，或者随手写死路径与等待时间（参见 `vendor/pstack/skills/principle-subtract-before-you-add/SKILL.md`）。本工作流对以下四类反模式实行零容忍（或旧仓棘轮收敛）：

1. **反过度工程化（先减后加 + 三次法则）**：先做出最小可用垂直切片再按需提炼；只有一个真实调用方时严禁提前抽出 Factory / Strategy / Adapter / DI 容器等空壳抽象；同一重复模式在代码中真实出现 **≥ 3 次**才允许抽象复用，优先删除死代码与投机式兼容层。
2. **反滥用防御性编码（边界单点校验，内部 Fail Fast）**：只在系统外部边界（HTTP/RPC 入参、用户输入、环境变量、数据库读取）校验与转换一次；进入内部逻辑后信任类型与契约，**严禁**用 `try/catch` / `except: pass` 静默吞掉异常或返回 `null`/`[]`/`{}`/假默认值来“保页面不崩”。内部非法状态必须立即抛出明确错误，绝不把真问题掩盖成“看起来没报错但算错了数”。
3. **反硬编码四红线**：
   - **禁止硬编码延时与盲等凑时序**：数据或接口就绪后严禁加 `minLoadingMs` / 强等 1.5s 再展示页面，严禁 `wait_for_timeout` / `waitForTimeout`、人工 `new Promise(r => setTimeout(r, 1500))` 或业务层裸 `sleep`，必须等待真实状态信号、完成事件或服务端版本号。
   - **禁止环境硬编码**：严禁把本机绝对路径（`C:\Users\...`、`/Users/...`、`/home/...`）、散落的 `http://localhost` / `127.0.0.1` 或密钥/Token 写进业务源码。
   - **禁止业务可变参数硬编码**：起算日、费率、阈值、开关等归口单一配置源，对照 `01-intent-and-invariants.md` 的 `configurable_params`。
   - **禁止主路径假数据与特判硬编码**：严禁在业务组件里塞写死 demo 数组或 `if (id === 'xxx')` 特判冒充真实状态；演示/测试数据只许走独立 seed 或 fixture。

高置信度的静默吞错、盲等延时、本机路径、`localhost` 与密钥字面量由 `repo_guard.py` 的 `anti_patterns` 门禁直接扫描拦截（配置语法见 `06-repo-guard-contract.md`）。

## 根因导向的自定义 Lint

原生编译器、强类型检查、项目既有 Linter（ESLint / Ruff / Clippy）和 AST 依赖检查（`dependency-cruiser` / `import-linter`）挂进 `check_command` 永远是**第一优先级**；`repo_guard.py` 提供的 `forbidden_primitives` / `boundary_rules` 是跨语言的快速零依赖兜底网。无论使用哪一种，只会喊“禁止使用 XXX”的规则效果都很差——Agent 看不懂该怎么改，往往会换个马甲绕过去，或者打上逃生舱注释强行过关。每一条自定义 Lint、依赖边界或原语禁令的报错信息，都必须**指出正确的接口与根因修法**：

```text
坏报错：Error: Direct import of core.storage is forbidden in ui/
好报错：ui/ 不得直接导入 core/storage。请改用 core/api.py 提供的用例接口（如 export_orders），
        避免在界面层绕过幂等与事务校验；若缺少所需能力，请在 core/api.py 新增受控方法。
```

好报错把“去哪里改、为什么这样设计”直接喂回 Agent 的错误上下文，让它当场自愈，而不必靠人解释；每新增一条规则都必须拿真实历史错例证伪验证（见 `04-correction-and-gardening.md`）。

## 注释与逃生舱策略

本节是本工作流中**注释、抑制指令与逃生舱规则的唯一权威**，其他文档只引用本节。

1. **默认禁止解释 workaround 的注释**：99% 的解释性注释只会过时并成为坏样例的通行证。在 Grok Bot 与 Cursor 的实践里，Agent 在被迫处理架构冲突时，最常干的事就是塞一个定时器或 hack，再写一大段“为什么这里必须临时这样做”的注释——下一轮 Agent 读到这段注释，会以为这是团队认可的惯例并照抄到全仓。
2. **不得用 lint-disable、noqa 或 @ts-ignore 绕过检查**：`eslint-disable`、`@ts-ignore`、`@ts-expect-error`、`# noqa`、`# type: ignore`、`// nolint`、`#[allow(...)]` 以及 `HACK` / `WORKAROUND` / `临时方案` 注释一律视为**逃生舱**。遇到报错必须修根因或补正式类型/封装，严禁把红灯盖住。
3. **注释不是可执行约束，能写成类型、API 或 lint 就删掉注释**：想提醒后续修改者“这里不能直接改状态”，就把状态字段私有化或变成枚举转换函数，而不是留三行警告注释。
4. **极窄的合法例外**：只有三类注释默认放行——对外公开 API/库契约的文档注释、机器可解析的许可证头、以及无法改变的外部依赖/平台/协议怪癖说明（或引用外部规范/Issue 链接）；任何不得已留下的行内抑制例外，必须直接在违规行旁写明**原因、过期日期与人工批准人**。
5. **语义级注释猎杀与根因清理**：当代码出现 `IMPORTANT`、`do not remove`、`too risky`、`fine for now` 等辩解词时，按 `vendor/pstack/skills/no-comments/SKILL.md` 启动 `vendor/pstack/agents/comment-sicko.md` 对变更范围做独立审查，配合 `vendor/pstack/skills/why/SKILL.md` 追溯提交记录求证；未经外部约束证实的自有代码怪癖必须标记重构并用最小根因修复替代，不把长辩解改写成短借口。

## 护栏门禁

完成代码库护栏建设或变更后，检查以下四条是否全部成立：

1. 核心运行上下文与模块边界已通过目录结构表达，并接入可自动运行的依赖边界检查（原生图检查器优先，或 `boundary_rules`）；
2. 已识别的易误用底层原语已封装进受控模块，未引入单调用方空壳抽象、静默吞错或四类硬编码（`repo_guard.py` 的 `anti_patterns` 门禁通过）；
3. `.guardrails/config.json` 的 `escape_hatches.max_allowed` 与 `anti_patterns.max_allowed` 已设定（绿地项目为 `0`），运行 `repo_guard.py` 确认无新增逃生舱、反模式或绕过注释，必要时已过 `/no-comments` 语义复核；
4. 项目级 `check_command`（format + lint + typecheck + unit/integration）能在干净命令行一键退出 0。
