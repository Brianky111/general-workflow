# 代码库护栏设计

倒金字塔最底端（投入回报比最高的两层）是**代码库结构**与**确定性静态检查**：直接改造目标仓库的类型、API、目录与原生 Linter，把规范变成“写错即编译失败或 Lint 直指修法”的物理边界。

## 目录即上下文

把运行上下文、信任域和状态归属写进顶层目录，并用依赖规则锁死：

- **写前对比、单源收敛与最小 diff**：非平凡改动先按 `vendor/pstack/skills/architect/SKILL.md`、`vendor/pstack/skills/principle-foundational-thinking/SKILL.md` 与 `vendor/pstack/skills/principle-laziness-protocol/SKILL.md` 定核心数据结构与并发共享面，对比至少两种方案，选“单状态所有者、唯一做法、最小变动”；
- **进程与运行时边界**：如 `electron-main/` 与 `electron-renderer/`、`server/` 与 `client/`、`worker/` 与 `web/`；禁止跨目录导入，强制走显式 IPC/API 契约；
- **领域建模与边界纪律**：参照 `vendor/pstack/skills/principle-boundary-discipline/SKILL.md` 在边界解析定型并信任内部类型；多分支与多布尔状态改用状态机、注册表或判别联合（`vendor/pstack/skills/principle-model-the-domain/SKILL.md`）；并发写入先拆分各自独立状态文件/键再聚合（`vendor/pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md`），生命周期命令按现状差量幂等收敛并原子替换临时文件（`vendor/pstack/skills/principle-make-operations-idempotent/SKILL.md`）；
- **共享原语与局部净土（`clean_scopes`）**：`shared/` 只放无业务归属的纯类型/纯函数；新建或彻底清理干净的模块目录立即写入 `.guardrails/config.json` 的 `clean_scopes` 锁死零逃生舱、零反模式与行数上限。

用 `boundary_rules` 声明跨目录禁令；规模增大或存在路径别名时，接入 `dependency-cruiser`（JS/TS）或 `import-linter`（Python）挂进 `check_command`。

## 业务层禁用高分寸感原语

需要极高分寸感才能写对的特性在业务层直接封杀，只保留极简安全封装：

- React `useEffect` → 业务组件禁用，仅 `src/runtime/` 或框架 hook 白名单放行；
- 裸异步定时器 `setTimeout` / `requestAnimationFrame` / `time.sleep` → 禁止业务代码靠“等一下”凑时序，由统一调度原语封装；
- 裸 SQL 拼接、散落直读 `os.environ` / `process.env`、跨过状态机直接改状态字段 → 收口到受控封装层。

同时按 `vendor/pstack/skills/principle-type-system-discipline/SKILL.md` 用类型/品牌类型封杀非法状态，按 `vendor/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md` 同一波迁完调用方并删旧接口，再通过 `forbidden_primitives`（配 `allow_paths`）或原生 Lint 彻底锁死。

## 反过度工程、反防御性吞错与反硬编码

参照 `vendor/pstack/skills/principle-subtract-before-you-add/SKILL.md` 与 `vendor/pstack/skills/principle-minimize-reader-load/SKILL.md`，坚持务实、最小化的工程风格，对以下红线实行零容忍（或旧仓棘轮收敛）：

1. **只做明确需求与必需改动**：只实现明确要求的功能和完成它所必需的改动；禁顺手重构无关代码、禁擅加配置项/开关、禁扩展未要求的兼容性或设计未来功能。每项新增复杂性必须对应当前需求、已确认错误或现有实测瓶颈（“以后可能需要”“这样更稳健”不能单独成为理由）。
2. **优先既有能力与最短路径**：不为一次性操作创建通用抽象，不为假想规模设计架构；优先使用现有代码和框架能力，选择最短、最清晰的实现路径。单实现禁套 `IXxx`/`XxxImpl`/Factory，单调用方禁纯透传 Wrapper/Manager，同模式真实重复 **≥ 3 次**才抽复用。遵循 `vendor/pstack/skills/poteto-mode/playbooks/refactoring.md`：重构必须先写特征测试钉死契约再删死码，新读者须在 30 秒内追出值来源与可变点；多步迁移直奔终态不留过渡兼容壳（`vendor/pstack/skills/principle-outcome-oriented-execution/SKILL.md`），非琐碎迁移先建可重跑脚本作交付杠杆（`vendor/pstack/skills/principle-build-the-lever/SKILL.md`），并用 `file_limits`（默认 `max_lines: 600` + 旧仓 `baseline_files` 棘轮）卡死巨石文件。
3. **边界一次解析，内部完全信任（Parse, Don't Validate）**：必要校验集中在系统外部边界一次性解析成强类型；信任已明确的内部类型、调用约定与框架保证，不在内部各层重复检查，不防御按现有契约不可能出现的状态。
4. **无明确恢复策略时让错误直接传播（Fail Fast）**：禁止用宽泛 `try/except`（如 `except Exception`、`except: pass`、`suppress(Exception)`）、空 `catch`、`.catch(() => {})` / `.catch(() => null | [])`、静默默认值（`val ?? fallback`）、空结果或多级 fallback 掩盖问题。
5. **禁主动增加未要求的韧性与状态机制**：不主动增加重试、回退、恢复流程、额外状态、健康检查或新的持久化机制；只有当前需求或已确认问题直接需要它们时才添加。
6. **反硬编码四红线**：
   - **禁盲等延时与人为最小加载**：就绪后严禁 `minLoadingMs` / `artificialDelay`、`wait_for_timeout` / `waitForTimeout`、`await sleep(1500)`、`Promise(setTimeout)` 或业务裸 `sleep`/`setTimeout`，改等真实状态信号或版本号；
   - **禁环境硬编码与散落读环境**：禁本机及 WSL 路径（`C:\Users\...`、`/Users/...`、`/home/<user>/...`、`/mnt/*/Users/`、`/root/`、`file:///Users/...`）、本地/内网 IP 与密钥字面量进源码；环境变量只收口单一入口；
   - **禁参数硬编码与擅增开关**：仅将当前需求**明确要求可变的业务参数**（对齐 `01` `configurable_params`）收口单一配置源，不写死魔法常量，也不把固定行为擅自抽成未要求的新配置；
   - **禁生产假数据与回退造假（`mock-in-prod`）**：生产源码禁定义 `MOCK_*`/`FAKE_*`/`mockXxxData`、写 `rows || mockData` 兜底或导入 `__mocks__`/`fixtures`。

以上 `repo_guard.py` 规则属零依赖启发式兜底；复杂 AST/语义问题由挂入 `check_command` 的原生编译器/Linter、`/architect` 与产物审查协同拦截（边界见 `06-repo-guard-contract.md`）。

## 根因导向的自定义 Lint

原生编译器、强类型、原生 Linter 与 AST 依赖检查永远是第一优先级；`repo_guard.py` 作跨语言兜底网。只喊“禁止 XXX”的报错会让 Agent 换马甲绕过——每条规则的 `message` 必须指明正确接口与根因修法：

```text
坏报错：Error: Direct import of core.storage is forbidden in ui/
好报错：ui/ 不得直接导入 core/storage。请改用 core/api.py 的 export_orders，
        避免绕过幂等与事务校验；缺少能力请在 core/api.py 新增受控方法。
```

每条新增规则须拿真实历史错例证伪验证（见 `04-correction-and-gardening.md`）。

## 注释与逃生舱策略

本节是本工作流中**注释、抑制指令与逃生舱规则的唯一权威**，其他文档只引用本节。

1. **默认禁止解释 workaround 的注释**：99% 的解释性注释只会过时并成为坏样例的通行证。Agent 在碰到架构冲突时最爱塞一个补丁再写一大段“为什么只能这样”，下一轮 Agent 读到就会照抄成全仓惯例。
2. **不得用 lint-disable、noqa 或 @ts-ignore 绕过检查**：`eslint-disable`、`@ts-ignore`、`@ts-expect-error`、`# noqa`、`# type: ignore`、`// nolint`、`#[allow(...)]` 与 `HACK` / `WORKAROUND` / `临时方案` 一律视为**逃生舱**，必须修根因或补正式类型。
3. **注释不是可执行约束，能写成类型、API 或 lint 就删掉注释**：把警告变成私有字段、枚举转换或编译检查。
4. **极窄的合法例外**：仅放行对外公开契约文档注释、许可证头、以及无法改变的外部平台怪癖说明；不得已保留的行内抑制必须旁注**原因、过期日期与人工批准人**。
5. **语义级注释猎杀与根因清理**：发现 `IMPORTANT`、`do not remove`、`too risky`、`fine for now` 等辩解词时，按 `vendor/pstack/skills/no-comments/SKILL.md` 启动 `vendor/pstack/agents/comment-sicko.md` 独立审查，配合 `vendor/pstack/skills/why/SKILL.md` 追溯求证；未经外部约束证实的自有怪癖一律重构替换。

## 护栏门禁

完成代码库护栏建设或变更后核对：

1. 核心运行上下文与模块边界已通过目录结构表达，并接入依赖边界检查；新建或净化的模块已登记进 `clean_scopes`；
2. 易误用底层原语已封装（合法退避收口单一 `runtime` 白名单），`repo_guard.py` 静态/反模式/行限扫描与原生 Linter 已覆盖；
3. `.guardrails/config.json` 的 `escape_hatches`、`anti_patterns`、`file_limits`（含 `baseline_files`）已锁定，必要时已过 `/no-comments` 复核；
4. 项目级 `check_command` 能在干净命令行一键退出 `0`。
