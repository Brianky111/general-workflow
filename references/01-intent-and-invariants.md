# 意图、不变量与起步入口

高吞吐的代码生成如果没有清晰的目标和不变量，只会用更高的速度造出方向错误的产品。本文件保留工作流里最薄的一层意图锚点，并给出从零建项与接手旧仓的起步路径。

## 为什么只留一页意图合同

v1.x 的多阶段文档体系在 0→1 阶段能防需求漂移，但把大量精力花在 R-ID / A-ID / Q-ID / K-ID / H-ID 交叉台账与切片锁上，反而和快速迭代冲突。v2 保留**只此一页**的意图与不变量合同，砍掉繁琐编号矩阵，理由有三点：

1. **防方向跑偏**：Agent 在写第一行代码前，必须知道给谁用、从哪个真实入口进去、做完后用户能观察到什么；
2. **直接喂给验证层**：写清“哪些不变量必须永远成立、哪些副作用绝对禁止”，这些句子能直接翻译成属性测试（PBT）、TLA+ 模型或自定义 Lint；
3. **划出永久人工边界**：把“不可逆操作”在起步时挑出来，后续即使自动化升到最高档，这些边界仍由人把关。

文档只写一页，写完立即进 `02-codebase-guardrails.md` 搭好目录边界和可执行检查，不在文档里反复推演实现细节。

## 意图与不变量模板

建议写在项目根目录 `docs/intent.md` 或 `.guardrails/intent.md`（也可并入项目 README 的核心章节），内容精简到一屏能读完：

```markdown
# Intent & Invariants
- problem: <谁在什么情境下遇到什么问题，现有做法哪里不够>
- primary_users: <直接用户、管理员或外部调用方>
- entrypoints: <真实入口：Web 路由 / 桌面窗口 / CLI 命令 / 后台任务>
- user_outcomes:
  - <可观察结果 1：用户做了什么后，看见或拿到什么>
  - <可观察结果 2：关键失败或无权限时的可见表现>
- invariants:
  - <必须始终成立的不变量，例如：重复提交同一请求不产生第二条扣款/第二行数据>
  - <禁止效果，例如：渲染进程不得读取本地密钥或阻塞主循环>
- non_goals:
  - <本阶段明确不做的一到三件事>
- configurable_params:
  - <起算日、费率、阈值、开关、外部地址等业务可变项，必须进单一配置源，禁写死在业务逻辑>
- irreversible_boundaries:
  - <不可逆操作清单：资金、权限放开、破坏性迁移、对外公共契约>
```

检验标准很简单：对照每一条 `user_outcomes` 和 `invariants`，看一眼就知道在 `03-verification-and-artifacts.md` 该测什么、该截什么产物；对照 `configurable_params`，确保从第一天起就没有业务常数散落硬编码；如果写着“系统更加稳定、体验流畅”这类空话，立刻重写成可观察结果。

## 垂直可演示切片与决策分工

面向不亲自写代码、靠体验验收的 Vibe Coding 工作方式，必须同时防住“按技术层拆成永不收口的半成品”与“把用户拉进底层技术评审泥潭”（参见 `vendor/pstack/skills/principle-sequence-verifiable-units/SKILL.md`）：

1. **只切端到端可演示的垂直增量（WIP = 1）**：每轮任务动工前先钉死一句话——“这一轮做完，用户打开哪个页面或跑哪个命令，能亲眼看到什么新变化？”严禁按 `schema / foundation / engine` 横向拆层而不交付可用闭环；当前主线垂直切片未交出可看结果前，不得同时开启多个平行分支或皮肤方案，也**严禁**为单一具体切片预建多 Provider/Plugin/Factory 扩展架子。
2. **人看演示、Agent 扛技术；配置进单源禁硬编码**：内部函数怎么拆、超时设几秒、局部单测怎么组织，由 Agent 选**最简可逆方案**自己拍板完成；**绝不**抛出几十条待逐行审阅的内部条目消耗用户注意力。只有会改变用户可见行为、业务口径或不可逆边界的问题，才用通俗人话向用户提问（每轮最多 1–2 个选择题）。同时从首个切片起，所有 `configurable_params` 统一收口进单一配置模块，严禁业务文件散落直读 `process.env` / `os.environ` 或写死魔法常量。

## 接手已有仓库（Brownfield 起步）

面对一个不是本工作流建起来的旧仓库，不要停下来全仓反推十几页需求书再动工。按以下三步在一个会话内把护栏和基线立起来：

1. **一键冷启动起草与核对基线（`--scan` / `--init`）**：先运行 `repo_guard.py --root "<目标项目绝对路径>" --scan` 启发式识别常规技术栈、`source_roots` 与 `check_command`，盘点现有逃生舱、6 类反模式及超长文件数量；该扫描只产出草稿而非完整构建图求解，**必须**随即阅读目标仓真实构建清单（`package.json`、`pnpm-workspace.yaml`、`pyproject.toml`、CI / Makefile）并在 `--init` 前后明确核对修改 `.guardrails/config.json` 的 `source_roots` 与 `check_command`（补全非标子包或 `scripts/`、避免根聚合脚本与子包重复）。确认无误后执行 `repo_guard.py --root "<目标项目绝对路径>" --init`（按需加 `--check-command` / `--max-lines`）生成起步层 `.guardrails/` 并锁定棘轮，同时按 `vendor/pstack/skills/correct/SKILL.md` 排查最近重复错误作为首批护栏目标。
2. **锁定三维棘轮上限（`max_allowed`）**：`--init` 会把当前真实的 `escape_hatches.max_allowed`、`anti_patterns.max_allowed` 与 `file_limits.max_allowed` 锁定为**天花板棘轮**。以后只许往下清、不许往上涨；如何逐步清零见 `04-correction-and-gardening.md`。`L0` 起步期 `.guardrails/feature-map.md` 空表与缺失 `.guardrails/verification.md` 仅发警告不阻塞启动，升入 `L1` 前补全。
3. **按真实入口写出第一版 Feature Map**：从组合根或路由表列出核心用户功能——小型项目可直接填入 `.guardrails/feature-map.md`；中大型或交互复杂的应用建议直接用 `vendor/pstack/skills/create-verification-skill/SKILL.md` 生成按功能域拆分的项目本地 `verify-<app>` skill，并在 `config.json` 配置 `verify_skill` 路径。`trust_level` 从 `L0` 起步，若已有完整自动化检查和核心功能验证产物也可直接设为 `L1`。

对于暂时没有接入测试的旧模块，不用停下全仓重测；哪天要改它或往那条边界加护栏，再按 `03-verification-and-artifacts.md` 先补行为验证与对比基线。

## 意图门禁

离开本文件进入 `02-codebase-guardrails.md` 或写业务代码前，必须确认：

1. 新项目已写出一页可观察的用户结果、核心不变量、至少一条明确的非目标、`configurable_params` 可变配置清单与不可逆边界；
2. 已有仓库已完成三步起步：有可跑的 `check_command`、已锁定 `escape_hatches.max_allowed` 初始棘轮值、已列出 `.guardrails/feature-map.md` 或 `verify_skill` 的首批核心入口；
3. 本轮要做的第一个垂直切片已明确“做完后用户能亲眼看到什么”，且会改变核心结果或不可逆边界的歧义已以通俗选择题向用户确认。
