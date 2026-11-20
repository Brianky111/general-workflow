# 示例：三个可运行的护栏项目

这里放三个真实可运行、带 `.guardrails/` 护栏和 `tests/` 的小型 Python 项目。`tests/test_examples.py` 每次都会对它们真跑一遍 `scripts/repo_guard.py --run-check`，并与本页贴出的预期输出逐行核对。

- `clean-app/`：从零按护栏建起来的订单导出 CLI。信任层级 `L1`，零逃生舱（`0/0`），含 `time.sleep` 原语白名单与 `src/ui` → `core/storage` 目录边界规则，并附可复用的 `tools/verify.py`。
- `weeding-brownfield/`：接手旧仓库起步的账单解析工具。信任层级 `L0`，先用 `escape_hatches.max_allowed: 1` 棘轮冻住 `src/legacy/parser.py` 里的 1 条旧 `# HACK` 注释，防止新增坏模式扩散。
- `verify-skill-app/`：使用项目本地分片验证 Skill（`.agents/skills/verify-orders/`）替代单表 `feature-map.md` 的订单 CLI。信任层级 `L1`，由 `config.json` 的 `verify_skill` 指向并校验 `SKILL.md` 与 `features/*.md` 四节契约。

## clean-app/：L1 内循环示例

在仓库根目录运行（带 `--run-check` 实跑单测）：

```powershell
python -X utf8 scripts/repo_guard.py --root examples/clean-app --run-check
```

预期退出码 0，输出：

```text
trust_level L1 | guard_status ready | fresh_head false
  scan: files=4 escape_hatches=0/0 primitive_violations=0 boundary_violations=0
  features: total=3 core=2 verified=2
  prose: AGENTS.md bytes=381 prohibitions=0
  check_run: PASS (exit 0)
0 error(s), 0 warning(s)
```

也可以直接跑它的复用型验证 CLI 重新生成产物：

```powershell
python -X utf8 examples/clean-app/tools/verify.py
```

### 目录与规则要点

```text
clean-app/
├── AGENTS.md                        # 极薄说明（381 bytes），零自然语言重复禁令
├── artifacts/
│   ├── export-csv.txt               # 验证 CLI 产出的导出结果样本
│   └── state-chart.md               # 用户视角状态图产物
├── src/
│   ├── runtime/clock.py             # 唯一允许调用 time.sleep 的白名单目录
│   ├── core/storage.py              # 内部存储，禁止 ui/ 直接导入
│   ├── core/api.py                  # 安全公共 API（带 batch_key 幂等转换）
│   └── ui/cli.py                    # 入口 CLI，仅导入 src.core.api
├── tools/verify.py                  # 可复用验证 CLI
├── tests/test_app.py
└── .guardrails/
    ├── config.json
    ├── feature-map.md
    └── verification.md
```

### 它不证明什么

- `verification.md` 里的 `a1b2c3d` 是示例占位 SHA（本示例不是独立 Git 仓库，因此 `require_fresh_head` 为 `false`）；真实项目在 `L3` 下必须开启 `require_fresh_head: true` 并以 `--check-head` 锚定当前 `HEAD`。

## weeding-brownfield/：L0 旧仓棘轮示例

在仓库根目录运行：

```powershell
python -X utf8 scripts/repo_guard.py --root examples/weeding-brownfield --run-check
```

预期退出码 0，输出：

```text
trust_level L0 | guard_status ready | fresh_head false
  scan: files=2 escape_hatches=1/1 primitive_violations=0 boundary_violations=0
  features: total=2 core=1 verified=1
  prose: AGENTS.md bytes=240 prohibitions=0
  check_run: PASS (exit 0)
0 error(s), 0 warning(s)
```

### 它证明了什么

- 旧仓接入不必停工重写全部历史代码：先把现存 1 处 `# HACK` 锁在 `max_allowed: 1`，阻止任何新提交新增绕过；等用正式 CSV 解析器替掉它后，把 `max_allowed` 降回 `0` 即可向 `L2`/`L3` 演进。

## verify-skill-app/：分片项目本地验证 Skill 示例

在仓库根目录运行：

```powershell
python -X utf8 scripts/repo_guard.py --root examples/verify-skill-app --run-check
```

预期退出码 0，输出：

```text
trust_level L1 | guard_status ready | fresh_head false
  scan: files=1 escape_hatches=0/0 primitive_violations=0 boundary_violations=0
  features: total=2 core=2 verified=2
  verify_skill: .agents/skills/verify-orders (name=verify-orders, features=2)
  prose: AGENTS.md bytes=393 prohibitions=0
  check_run: PASS (exit 0)
0 error(s), 0 warning(s)
```

也可以直接运行它的只读自检与验证驱动重新产出产物：

```powershell
python -X utf8 examples/verify-skill-app/tools/control_orders.py doctor
python -X utf8 examples/verify-skill-app/tools/control_orders.py all
```

### 它证明了什么

- 当应用功能增多时，不必维护单张膨胀的 `feature-map.md`：在 `.guardrails/config.json` 配置 `verify_skill` 即可让 `repo_guard.py` 直接校验 `.agents/skills/verify-orders/` 的 `SKILL.md`（`Launch` / `Doctor` / `Drive` / `Evidence` / `Cleanup`）、`features/README.md` 索引卫生，以及各 `features/*.md` 的 4-H2 契约。
