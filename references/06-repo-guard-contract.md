# 仓库护栏契约与校验脚本

本工作流不要求目标项目维护多份流程台账或切片锁，只要求在项目根目录保留一个极轻的 `.guardrails/` 目录，让随 skill 分发的 `scripts/repo_guard.py` 能在任意会话里用确定性脚本核验代码库护栏与验证新鲜度。

## .guardrails/ 目录布局

```text
.guardrails/
  config.json        # 护栏版本、信任层级、检查命令、棘轮上限、禁止原语与目录边界规则
  feature-map.md     # 小型项目功能地图；若 config.json 配了 verify_skill，则改用分片验证 Skill
  verification.md    # 行为验证产物台账（起步层可选；非起步层必填）：Feature | Command | Observed | Artifact | Commit
```

这三份文件全部和源码一起提交进 Git，不建 `slices/` 锁文件，也不记繁琐过程阶段。若项目采用按功能域分片的 `verify_skill`（如 `.agents/skills/verify-<app>/`），不要再保留重复的 `.guardrails/feature-map.md`。

## config.json 契约

~~~json
{
  "guardrails_version": 2,
  "trust_level": "L1",
  "check_command": "python -X utf8 -B -m unittest discover -s tests -p \"test_*.py\"",
  "verify_cli": "python -X utf8 tools/verify.py",
  "verify_skill": ".agents/skills/verify-orders",
  "source_roots": ["src"],
  "exclude_dirs": [".git", "__pycache__", "node_modules", ".venv", ".guardrails"],
  "prose_files": ["AGENTS.md"],
  "prose_max_bytes": 6000,
  "require_fresh_head": false,
  "escape_hatches": {
    "max_allowed": 0,
    "extra_patterns": []
  },
  "anti_patterns": {
    "max_allowed": 0,
    "enabled": ["silent-catch", "blind-wait", "hardcoded-path", "hardcoded-localhost", "hardcoded-secret"],
    "allow_paths": ["tests"],
    "allow_by_category": {
      "blind-wait": ["src/runtime"]
    },
    "extra_rules": []
  },
  "forbidden_primitives": [
    {
      "id": "no-raw-sleep",
      "pattern": "\\btime\\.sleep\\s*\\(",
      "globs": ["src/**/*.py"],
      "allow_paths": ["src/runtime"],
      "message": "业务逻辑不要直接调用 time.sleep；请改用 src/runtime/clock.py 封装的受控等待原语，或在测试中使用可控时钟。"
    }
  ],
  "boundary_rules": [
    {
      "id": "ui-no-direct-storage",
      "from_dir": "src/ui",
      "forbid_import": "core/storage",
      "message": "src/ui 不得绕过 core/api 直接导入 core/storage；请通过 src/core/api.py 公开用例执行带幂等校验的操作。"
    }
  ]
}
~~~

关键字段硬性规则：

- `guardrails_version` 必须为整数 `2`；`trust_level` 仅接受枚举值 `L0`、`L1`、`L2`、`L3`（各层级的准入前提与自动化边界见 `05-outer-loop-factory.md`）。
- `check_command` 不能为空或占位词；高于起步层时，`verify_cli` 或 `verify_skill` 二者至少提供一个非占位入口。
- `verify_skill`（可选）：项目内分片验证 Skill 目录路径（见下节）；配置后优先作为功能地图单一事实源。
- `escape_hatches.max_allowed` 为非负整数；进入外循环层级前必须已清为 `0`（不带旧债进外循环）。
- `anti_patterns`（可选）：内置 5 类高置信度反模式静态扫描，带棘轮上限与白名单：
  - 类别枚举：`silent-catch`（空/静默返回兜底的 Python `except` 或 JS/TS `catch`）、`blind-wait`（`wait_for_timeout` / `waitForTimeout`、`new Promise(...setTimeout)`，显式开启时含 `time.sleep`/`asyncio.sleep` 与非零 `setTimeout`）、`hardcoded-path`（`C:\Users\...`、`/Users/...`、`/home/...`）、`hardcoded-localhost`（业务层散落的 `http(s)://localhost|127.0.0.1`，显式开启时生效）、`hardcoded-secret`（常见密钥字面量）。
  - 缺省不写 `anti_patterns` 时默认开启零误报子集（`silent-catch`、`hardcoded-path`、`hardcoded-secret` 与 Playwright/Promise 盲等）且上限为 `0`；显式配置后默认 5 类全开，支持 `allow_paths`、`allow_by_category` 与自定义 `extra_rules`，进入外循环层级前 `anti_patterns.max_allowed` 同样须降为 `0`。
- `require_fresh_head` 为布尔值；进入最高自治层级时必须为 `true`。
- 每条 `forbidden_primitives` 与 `boundary_rules` 的 `message` 不得为空或过短占位（至少 15 字符），必须写出根因与替代方案。

## feature-map.md 与 verification.md 格式

**方式 A（紧凑单表）**：`.guardrails/feature-map.md` 记录“用户怎么用、用什么命令测”：

~~~markdown
# Feature Map
| Feature | Entrypoint | Verify CLI | Artifact | Priority |
| --- | --- | --- | --- | --- |
| 导出订单报表 | `python -m src.ui.cli export` | `python tools/verify.py export` | `artifacts/export-csv.txt` | core |
~~~

**方式 B（分片 `verify_skill`）**：在 `config.json` 配置 `"verify_skill": ".agents/skills/verify-<app>"`，由 `repo_guard.py` 校验四项硬约束：
1. `SKILL.md` 必须含 YAML frontmatter（非空 `name`/`description`）以及 `Launch`、`Doctor`、`Drive`、`Evidence`、`Cleanup` 五个非空章节；
2. `features/README.md` 必须与同级 `features/*.md` 双向对齐（无断链、无未索引的孤儿功能文件）；
3. 每个功能文件必须有非占位 H1 功能标题，且按顺序包含四个非空 H2：`Sub-features`、`How to get to it`、`Driving it with`、`Gotchas`（可用 `<!-- priority: secondary -->` 标次要功能，默认 `core`）；
4. `verification.md` 可写功能 H1 标题或文件主干名（如 `create-order`）作为匹配键。

`verification.md` 记录“最近一次真跑过什么、看见了什么、落在哪个不可变提交上”（起步层缺失只报警告，进入更高层级后必填）：

~~~markdown
# Verification
| Feature | Command | Observed | Artifact | Commit |
| --- | --- | --- | --- | --- |
| 导出订单报表 | `python tools/verify.py export` | 导出 2 条明细且状态转为 exported | `artifacts/export-csv.txt` | a1b2c3d |
~~~

在高于起步层的阶段，`core` 功能均须在 `verification.md` 有对应记录；产物路径必须是项目内实际存在且大于 0 字节的文件（或有效 `https://` 运行链接）。观察结果写法与锚点限制遵循 `03-verification-and-artifacts.md`（不写“passed/完成”空话，不填移动分支名）。

## 运行 scripts/repo_guard.py

脚本随本 skill 分发，目标仓库无需拷贝，每次显式传入 `--root`：

```powershell
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" [--json] [--run-check] [--check-head]
```

- 无参数只做静态护栏、文档体积、逃生舱计数、Feature Map 与产物存在性校验；
- `--run-check`：在目标根目录真实执行 `config.json` 的 `check_command`，非零退出即失败；
- `--check-head`（或 `require_fresh_head: true` 时自动触发）：核对 Git `HEAD` 与工作区干净度，确认 `verification.md` 每行 `Commit` 前缀匹配当前 `HEAD` 且 `source_roots` 下无未提交改动，源码改动后自动把旧绿灯判失效；
- `guard_status` 取四值：`uninitialized`（可起步，退出 0）、`legacy_v1`（发现旧版状态目录，退出 0 并提示迁移）、`invalid`（校验失败，退出 1）、`ready`（全部通过，退出 0）。

## 从 v1.x 状态目录迁移

当 `repo_guard.py` 检测到目标仓库缺少 `.guardrails/` 但存在 `docs/workflow/`、`docs/workflow-state.md` 或 `WORKFLOW-STATE.md` 时，返回 `guard_status: legacy_v1`。迁移按四步做，不直接删光丢历史：

1. 从原有合同和已交付/剩余 A-ID 中提炼用户视角功能与核心不变量，写入 `01-intent-and-invariants.md` 的一页意图合同及 `.guardrails/feature-map.md`；
2. 把原先写在切片 `evidence` 里的真实入口调用方式沉淀成 `.guardrails/config.json` 的 `verify_cli`；
3. 按 `01-intent-and-invariants.md` 跑一次 `repo_guard.py` 锁定当前逃生舱数量和边界规则，将已有真实测试/产物路径登记进 `.guardrails/verification.md`；
4. 确认 `repo_guard.py --run-check` 退出 0 后，归档或移除旧 `docs/workflow/`，不再维护双轨状态。

## 检查边界

必须清楚这套零依赖脚本能拦住什么、拦不住什么：

- **模式匹配不是完整 AST**：`forbidden_primitives`、`anti_patterns` 和 `boundary_rules` 使用通用语法/正则与导入路径匹配，零依赖拦截高置信度坏模式（如静默 `catch`/`except: pass`、盲等延时、本机路径与散落 `localhost`），但分辨不出复杂路径别名或语义层过度工程/假数据数组（后两者结合人工审查产物、`no-comments` 与 `check_command` 原生 Linter/AST 工具覆盖）。
- **逃生舱与注释检查靠规则词表**：能拦常见禁用指令与显式 `HACK`/`WORKAROUND` 标记，读不出换个委婉写法写的辩解注释；需要语义级猎杀与历史错例分析时，结合 `vendor/pstack/skills/no-comments/SKILL.md` 与 `vendor/pstack/skills/correct/SKILL.md` 执行。
- **产物与新鲜度只证明“在当前版本跑出过非空证据”**：磁盘文件存在且非空不代表视频画面让用户满意，测试命令退出 0 不代表测试断言理解对了需求——产品意图与体验好坏仍靠人审产物把关。

## 契约门禁

完成 `.guardrails/` 配置或迁移后，必须确认：

1. 三份文件均按上述格式落盘且字段完整，没有占位词或空表；
2. `python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --run-check` 退出码为 `0`；
3. 若仓库在 `L3` 或准备合入关键变更，`--check-head` 同样通过且不存在未锚定到当前 `HEAD` 的过时验证行。
