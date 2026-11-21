# 仓库护栏契约与校验脚本

本工作流只在目标仓库根目录保留极轻的 `.guardrails/` 目录，让随 skill 分发的 `scripts/repo_guard.py` 在任意会话用确定性脚本核验代码库护栏、净土目录、反伪造校验与新鲜度。

## .guardrails/ 目录布局

```text
.guardrails/
  config.json        # 护栏版本、信任层级、工程类型、检查命令、棘轮与 clean_scopes、边界规则
  feature-map.md     # 小型项目功能地图；若 config.json 配了 verify_skill，则改用分片验证 Skill
  verification.md    # 行为验证产物台账（起步层可选；非起步层必填）：Feature | Command | Observed | Artifact | Commit
```

三份文件随源码进 Git，不建 `slices/` 锁文件。采用分片 `verify_skill` 时不再保留重复的 `.guardrails/feature-map.md`。

## config.json 契约

~~~json
{
  "guardrails_version": 2,
  "trust_level": "L1",
  "project_kind": "app",
  "check_command": "python -X utf8 -B -m unittest discover -s tests -p \"test_*.py\"",
  "verify_cli": "python -X utf8 tools/verify.py",
  "verify_skill": ".agents/skills/verify-orders",
  "source_roots": ["src"],
  "clean_scopes": ["src/core"],
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

- `guardrails_version` 必须为整数 `2`；`trust_level` 仅接受受控层级枚举（详见 `05-outer-loop-factory.md`）。
- `project_kind`（可选，默认 `"app"`）：仅接受 `"app"` 或 `"library"`。当为 `"app"` 且未配 `verify_skill` 时，顶层 `verify_cli` 与 `feature-map.md` 的 `Verify CLI` 均禁止照抄 `check_command`、只跑 `/health` `/healthz` `/ping` 浅探针，或直接填写 `pytest`/`vitest`/`npm test`/`cargo test`/`go test` 等测试运行器（起步层发警告，高于起步层的 `verify_cli` 及 `core` 行直接判错）；只有独立可复用库才可显式设为 `"library"` 放行测试运行器。
- `check_command` 不能为空或占位词；高于起步层时，`verify_cli` 或 `verify_skill` 至少提供一项有效非占位入口。
- `verify_skill`（可选）：项目本地分片验证 Skill 目录路径（见下节）；配置后作功能地图单一事实源。
- `clean_scopes`（可选，默认 `[]`）：已清理完毕的相对路径白名单目录/文件，须各自落在某个 `source_roots` 之下且匹配非零个可读源码文件。无论处于哪一层级，`clean_scopes` 内部对逃生舱、未被 `allow_by_category` 放行的 `anti_patterns` 以及超过 `file_limits.max_lines` 的文件**一律零容忍立即报错**；在存在 `baseline_files` 锁死仓外巨石的前提下，配置 `clean_scopes` 可先解锁外循环探索层级，但最高自治层级仍强制要求全仓棘轮清零。
- `escape_hatches.max_allowed`：非负整数；无 `clean_scopes` 的外循环层级及一切最高自治层级须降至 `0`。
- `anti_patterns`（可选）：内置 6 类扫描与棘轮：`silent-catch`、`blind-wait`、`hardcoded-path`、`hardcoded-localhost`、`hardcoded-secret`、`mock-in-prod`。前五类自动豁免真实测试/fixture 路径（`hardcoded-secret` 在测试内继续生效，`test_*` 仅豁免 Python 测试文件），并跳过 `.env*`/`*.log`/lockfiles 与根/包级构建产物目录；合法退避应收口单一 `runtime` 模块并用 `allow_by_category` 放行。缺省开启除 `hardcoded-localhost` 外的 5 类。
- `file_limits`（可选）：`max_lines`（默认 `600`，按源码扩展名计且跳过 `.css`/`.json`/测试文件）、`max_allowed` 与按路径 `baseline_files` 行数天花板（不得落在 `clean_scopes` 内，旧巨石只许瘦不许胖、新文件禁破阈值）。
- 缺少有效 `source_roots` 或匹配 `0` 个可读源码文件即判 `invalid`；`require_fresh_head` 在最高自治层级必须为 `true`。
- `forbidden_primitives` 与 `boundary_rules` 的 `message` 至少 15 字符且须写清根因与替代方案。

## feature-map.md 与 verification.md 格式

**方式 A（紧凑单表）**：`.guardrails/feature-map.md` 记录用户语言入口与驱动命令：

~~~markdown
# Feature Map
| Feature | Entrypoint | Verify CLI | Artifact | Priority |
| --- | --- | --- | --- | --- |
| 导出订单报表 | `python -m src.ui.cli export` | `python tools/verify.py export` | `artifacts/export-csv.txt` | core |
~~~

**方式 B（分片 `verify_skill`）**：配置 `"verify_skill": ".agents/skills/verify-<app>"`，`repo_guard.py` 校验四项：
1. `SKILL.md` 含非空 YAML `name`/`description` 与 `Launch`、`Doctor`、`Drive`、`Evidence`、`Cleanup` 五节；
2. `features/README.md` 与 `features/*.md` 双向对齐（无断链、无孤儿文件）；
3. 每个功能文件含非占位 H1 及顺序 `Sub-features`、`How to get to it`、`Driving it with`、`Gotchas`（次要标 `<!-- priority: secondary -->`）；
4. `verification.md` 用功能 H1 标题或文件主干名作匹配键。

起步层允许空表 `feature-map.md` 与暂缺 `verification.md`；高于起步层须补齐全部 `core` 行，产物非空且锚定不可变 commit（遵循 `03-verification-and-artifacts.md`）。

## 运行 scripts/repo_guard.py

脚本随 skill 分发，目标仓无需拷贝，显式传入 `--root`：

```powershell
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" [--json] [--run-check] [--check-head]
python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" [--scan | --init] [--max-lines 600] [--check-command "<cmd>"] [--json]
```

- 无参数：静态护栏、净土区、文档体积、逃生舱、反模式、`file_limits`、地图、防伪 `verify_cli` 与产物校验；
- `--scan`：只读起草技术栈、`source_roots`、`check_command` 与存量基线；
- `--init`：预检源码非空与 `check_command` 有效后生成起步层 `.guardrails/` 并锁初始棘轮；
- `--run-check`：执行 `check_command`；`--check-head`：核对 Git `HEAD` 与 `source_roots` 干净度；
- `guard_status`：`uninitialized`、`baseline_scan`、`legacy_v1`、`invalid`（退出 `1`）或 `ready`。

## 从 v1.x 状态目录迁移

检测到缺失 `.guardrails/` 但存在 `docs/workflow/`、`docs/workflow-state.md` 或 `WORKFLOW-STATE.md` 时返回 `legacy_v1`，分四步平滑迁移不覆盖历史：
1. 提炼一页意图合同与功能清单入 `01` 及 `.guardrails/feature-map.md`；
2. 将切片 `evidence` 的真实调用沉淀为场景驱动型 `verify_cli`；
3. 跑 `--init` 或手工建好配置锁定初始棘轮（干净模块入 `clean_scopes`）并登记已有产物；
4. `repo_guard.py --run-check` 退出 `0` 后归档或移除旧 `docs/workflow/`。

## 检查边界

- **轻量启发式边界**：`--scan`/`--init`、`forbidden_primitives`、`anti_patterns`、`boundary_rules` 与 `classify_fake_verify_cli` 均属零依赖轻量分析；复杂 monorepo、路径别名、语义级单实现空壳或跨进程业务误用仍须交由原生编译器/Linter、`/architect` 与产物审查接管。
- **语义注释与历史挖掘**：词表规则抓不住委婉借口注释，也查不到聊天里的口头纠错，需配合 `vendor/pstack/skills/no-comments/SKILL.md`、`correct/SKILL.md`、`reflect/SKILL.md` 与 `recall/SKILL.md`。
- **产物仅证“跑过且非空”**：文件非空与退出 `0` 不代表体验满意，意图与体感由人（或双盲 `eval` / 独立 Verifier）把关。

## 契约门禁

完成 `.guardrails/` 配置或迁移后核对：

1. 高于起步层时三份文件完整、无占位词、`project_kind` 与驱动 `verify_cli`（或 `verify_skill`）合规、`clean_scopes` 零违规；
2. `python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --run-check` 退出 `0`；
3. 最高自治层级或准备合入关键改动时 `--check-head` 同步通过。
