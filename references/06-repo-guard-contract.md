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
    "enabled": ["silent-catch", "blind-wait", "hardcoded-path", "hardcoded-localhost", "hardcoded-secret", "mock-in-prod"],
    "allow_paths": [],
    "allow_by_category": {
      "blind-wait": ["src/runtime"]
    },
    "extra_rules": []
  },
  "file_limits": {
    "max_lines": 600,
    "max_allowed": 0,
    "allow_paths": [],
    "baseline_files": {}
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
- `anti_patterns`（可选）：内置 6 类反模式扫描与棘轮：`silent-catch`（Python AST 检查 `except`/`suppress(Exception|BaseException)`、JS/TS 空/静默 `catch`、Promise `.catch` 与 `.then(_, 静默)`）、`blind-wait`（`wait_for_timeout`/`waitForTimeout`/`Promise(setTimeout)`、`await sleep/delay` 与正值 `minLoadingMs`/`AFTER_SYNC_REFRESH_MS` 常量，显式开启含裸非零 `sleep`/`setTimeout` 并豁免 `sleep(0)`）、`hardcoded-path`（本机、WSL `/mnt/*/Users/`、`/root/`、`file:///`）、`hardcoded-localhost`（显式开启时拦本地/内网 HTTP/WS/DB 地址与 `[::1]`）、`hardcoded-secret`、`mock-in-prod`（生产源码禁 `MOCK_*`/`FAKE_*`、`|| mockData` 及导入 `__mocks__`/`fixtures`/`seeds`）。前五类数据/语法规则自动豁免真实测试路径（`hardcoded-secret` 在测试内依然生效，`test_*.py` 仅豁免 Python 测试文件），并跳过 `.env*`/`*.log`/lockfiles 及根/包级构建产物目录；底层合法退避应收口单 `runtime` 模块并用 `allow_by_category` 放行。缺省开启除 `hardcoded-localhost` 外的 5 类，进入外循环层级前 `max_allowed` 须为 `0`。
- `file_limits`（可选）：`max_lines`（默认 `600`，按源码扩展名计且跳过 `.css`/`.json`/测试文件）、`max_allowed` 与按路径 `baseline_files` 行数天花板（旧巨石只许瘦不许再胖、新文件禁破 `max_lines`，进入外循环层级前须清为 `0` / `{}`）及 `allow_paths`。
- 缺少有效 `source_roots` 或匹配 `0` 个可读源码文件时立即判为 `invalid`，防止空扫假绿灯。
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

起步层若 `feature-map.md` 表尚空或缺失 `verification.md` 只发警告（便于 `--init` 冷启动立即通过）；高于起步层后，`core` 功能均须在二者中补齐，产物路径必须是存在且非空的文件（或 `https://` 链接），观察结果与锚点遵循 `03-verification-and-artifacts.md`。

## 运行 scripts/repo_guard.py

脚本随本 skill 分发，目标仓库无需拷贝，每次显式传入 `--root`：

```powershell
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" [--json] [--run-check] [--check-head]
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" [--scan | --init] [--max-lines 600] [--check-command "<cmd>"] [--json]
```

- 无参数只做静态护栏、文档体积、逃生舱、反模式、`file_limits`、Feature Map 与产物校验；
- `--scan`：只读启发式起草技术栈、`source_roots` 与 `check_command`，盘点逃生舱、6 类反模式与超长文件基线，不改动 `.guardrails/`；
- `--init`：预检可读源码非空与 `check_command` 有效后写入起步层 `.guardrails/` 草稿并锁初始 `max_allowed` 与 `baseline_files`（不覆盖已有目录或 `legacy_v1`；非标 workspace 须由 Agent 核对修正 `config.json`）；
- `--run-check`：执行 `config.json` 的 `check_command`；`--check-head`（或 `require_fresh_head: true`）核对 Git `HEAD` 与 `source_roots` 干净度；
- `guard_status` 取值：`uninitialized`、`baseline_scan`（`--scan`）、`legacy_v1`、`invalid`（退出 1）或 `ready`。

## 从 v1.x 状态目录迁移

当 `repo_guard.py` 检测到目标仓库缺少 `.guardrails/` 但存在 `docs/workflow/`、`docs/workflow-state.md` 或 `WORKFLOW-STATE.md` 时，返回 `guard_status: legacy_v1`。迁移按四步做，不直接删光丢历史：

1. 从原有合同和已交付/剩余 A-ID 中提炼用户视角功能与核心不变量，写入 `01-intent-and-invariants.md` 的一页意图合同及 `.guardrails/feature-map.md`；
2. 把原先写在切片 `evidence` 里的真实入口调用方式沉淀成 `.guardrails/config.json` 的 `verify_cli`；
3. 按 `01-intent-and-invariants.md` 跑一次 `repo_guard.py` 锁定当前逃生舱数量和边界规则，将已有真实测试/产物路径登记进 `.guardrails/verification.md`；
4. 确认 `repo_guard.py --run-check` 退出 0 后，归档或移除旧 `docs/workflow/`，不再维护双轨状态。

## 检查边界

必须清楚这套零依赖脚本能拦住什么、拦不住什么：

- **轻量启发式与浅层分析边界**：`--scan`/`--init` 拓扑探测及 `forbidden_primitives`、`anti_patterns`、`boundary_rules` 均属轻量启发式（通用正则、Python 缩减版 AST 与 JS 注释/字符串脱敏，非完整词法或构建图解析器）；复杂 monorepo 布局、路径别名与 AST 精确语义须由 Agent 核对 `config.json` 并交目标仓原生 `check_command` 与 `/architect`/人工产物审查接管。
- **逃生舱与注释检查靠规则词表**：能拦常见禁用指令与显式 `HACK`/`WORKAROUND` 标记，读不出换个委婉写法写的辩解注释；需要语义级猎杀与历史错例分析时，结合 `vendor/pstack/skills/no-comments/SKILL.md` 与 `vendor/pstack/skills/correct/SKILL.md` 执行。
- **产物与新鲜度只证明“在当前版本跑出过非空证据”**：磁盘文件存在且非空不代表视频画面让用户满意，测试命令退出 0 不代表测试断言理解对了需求——产品意图与体验好坏仍靠人审产物把关。

## 契约门禁

完成 `.guardrails/` 配置或迁移后，必须确认：

1. 高于起步层时三份文件均完整、无占位词且核心功能与验证记录齐备；起步层允许暂缺 `verification.md` 或保留空表 `feature-map.md`（仅发警告），不得在缺失可执行 `check_command` 时强留 `"TODO"`；
2. `python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --run-check` 退出码为 `0`；
3. 若仓库在 `L3` 或准备合入关键变更，`--check-head` 同样通过且不存在未锚定到当前 `HEAD` 的过时验证行。
