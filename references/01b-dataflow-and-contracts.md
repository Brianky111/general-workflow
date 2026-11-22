# 数据流、API 契约与切片移交

本文件承接 `01a-stack-and-architecture.md` 的模块地图，在动工写业务源码前把**状态单一真相源、端到端数据流、可粘贴代码级契约、失败上限矩阵**与**可执行垂直切片队列**落盘，并通过 `repo_guard.py --check-arch` 确定性门禁后两阶段无死锁交接至 `02-codebase-guardrails.md`。

> 注意目录隔离：`general-workflow` 架构产物统一放在根目录 `ARCHITECTURE.md` 与 `docs/arch/`，**严禁**使用 `docs/workflow/`（会被 `repo_guard.py` 判定为 `legacy_v1` 历史状态）。

## 状态所有权与数据流图（docs/arch/dataflow.md）

在 `docs/arch/dataflow.md`（`<= 8,000`B；属过程消费型产物，随测试与实现固化后可精简冗余段）写清两项核心事实：

1. **状态所有权表（Kleppmann 三列内核）**：覆盖系统每一类核心持久化与内存/客户端状态：

   | 状态 / 实体 | 单一真相源（SSOT） | 唯一写入模块 | 派生副本与重建路径 | 重复请求或部分失败语义 |
   | --- | --- | --- | --- | --- |
   | `<例：订单状态>` | `<Postgres orders 表>` | `<core/orders>` | `<搜索索引：由 outbox 全量/增量重放重建>` | `<按 idempotency_key 幂等收敛，超时可安全重放>` |

   - 凡出现“两个模块同时拥有同一份真相”“缓存兼任真相源却无重建路径”或“失败语义留空”的条目，当场打回重塑（多存储/异步任务按 `01c-distributed-and-sync.md` 深化，多源前端状态按 `01e-client-state-flow.md` 深化）。

2. **核心路径数据流图**：针对 `docs/intent.md` 中每条核心 `user_outcomes`，用 Mermaid（`flowchart LR` / `sequenceDiagram`）或 ASCII 画出端到端数据流，必须显式标出：
   - **系统边界解析点（Boundary Parse）**：外部非信任输入在何处被一次性解析成强类型领域模型；
   - **状态变更点**：唯一 SSOT 写入发生在哪一步；
   - **外部副作用出口**：发邮件、支付、Webhook、写文件等不可逆或外部调用在何处触发。

## 代码级 API 与 Schema 契约（docs/arch/contracts.md）

在 `docs/arch/contracts.md`（`<= 10,000`B；仅索引与契约定义，随切片落入源码后可清理已落地条目）用**选定技术栈的真实类型/Schema 语法**（如 TypeScript/Zod、Python Pydantic/TypedDict、OpenAPI、SQL DDL）写出可直接粘贴进源码的边界契约——覆盖所有跨进程边界、对外 HTTP/RPC/CLI 接口及核心深模块 Seam：

每份契约必须钉死五要素：
1. **输入与输出类型结构**（含必填、枚举、精度单位如分/毫秒）；
2. **枚举化错误集合**：通过收窄或重塑 API 语义把非法调用“定义没”（例如用精确查找与显式创建替代宽泛 upsert 吞错），列明业务可恢复错误码，禁止靠空 `catch` 降级；
3. **幂等键与并发版本语义**（适用写操作）；
4. **显式静态上限**（单次最大条目数、分页上限、Payload 字节上限、超时毫秒数，同步进入 `docs/intent.md` 的 `configurable_params`）；
5. **兼容演进规则**（字段增删策略、只增不破原则）。

## 失败模式与静态上限矩阵

并入 `docs/arch/dataflow.md`，融合 `gstack` `/plan-eng-review` 的边界审计与 `TigerStyle` 的静态上限约束，逐条覆盖所有关键链路与外部依赖：

| 失败 / 异常模式 | 检测信号 | 用户可见表现 | 重试 / 降级语义 | 显式静态上限（Bound） | 所护不变量 | 验证钩子（verify_cli / PBT） |
| --- | --- | --- | --- | --- | --- | --- |
| `<例：支付网关超时>` | `<HTTP 504 / 超时>` | `<订单置 pending 并提示查单>` | `<带 idempotency_key 指数退避>` | `<单请求 3s，最多 3 次，队列上限 1000>` | `<同单不双扣>` | `<tools/verify.py retry-timeout>` |

- 若 `irreversible_boundaries` 涉及资金账务、不可恢复数据或自研存储协议，先对照 `01d-high-assurance-bounds.md` 补全守恒等式与读写成对断言验证钩子。
- **独立上下文对抗收尾**：在定稿前，拉起一个未参与起草的只读子代理（或切换到审阅者视角）专门挑刺三件事：1) 哪条状态行缺失重建或失败语义？2) 哪条失败行缺少静态上限或验证钩子？3) `ARCHITECTURE.md` 哪条负不变量还没有编译目标？

## 垂直切片队列与两阶段无死锁交接

1. **生成垂直切片队列（`docs/arch/slice-queue.md`，`<= 6,000`B）**：

   | 序号 | 用户可见结果与真实入口 | 穿过的模块 | 本切片落地的契约与负不变量 | 验证钩子 |
   | --- | --- | --- | --- | --- |
   | `S1` | `<端到端最小闭环，用户打开 X 可见 Y>` | `<ui -> core -> storage>` | `<契约 A + 负不变量 rule-1>` | `<verify_cli 场景 1>` |

   - **切片 1 铁律（Tracer Bullet）**：切片 1 必须是穿过全部部署单元与风险最高集成点的最薄可演示端到端闭环，其后按最大未知风险降序排列；
   - **禁横向分层切片**：出现 `schema`、`foundation`、`scaffolding`、`engine`、`database migrations` 等无用户可观察产物的切片一律判错；
   - 目录、契约与对应 `boundary_rules` 由**首次用到它的那个切片**落码创建；队列仅作有序清单，交接后按 `WIP=1` 取队首实现，做完划掉，清空即删。

2. **生成预编译护栏片段（`docs/arch/guardrails-fragment.json`）**：将 `ARCHITECTURE.md` 中可静检的负不变量预先写成标准 JSON（允许字段：`project_kind`、`prose_files`、`clean_scopes`、`boundary_rules`、`forbidden_primitives`，每条规则的 `message` 须 `>= 15` 字符且写明根因与正确接口）。

3. **跑通架构包确定性门禁（`--check-arch`）**：
   ```powershell
   python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --check-arch
   ```
   该检查在无源码的 0→1 仓库即可运行，校验 `docs/intent.md` 八字段非空无占位、`docs/adr/0001-stack.md`、`ARCHITECTURE.md`（`<= 6,000`B 且无行号引用）、`docs/arch/{dataflow,contracts,slice-queue}.md`（含 SSOT/流图/上限检查及横向切片拦截）与 `guardrails-fragment.json` 语法合规，通过返回 `arch_ready`。

4. **两阶段无死锁交接进 `02-codebase-guardrails.md`**：
   - **新仓（0 源码）严禁提前建 `.guardrails/`**：`repo_guard.py` 见到无 `config.json` 的 `.guardrails/` 会直接报错且拒绝 `--init`，且 `--init` 要求至少存在 1 个可读源码文件。正确顺序为：**`--check-arch` 通过 → 按 `S1` 写入首批可运行垂直切片源码与 `check_command` → 执行 `repo_guard.py --init`（自动识别根目录 `ARCHITECTURE.md` 并自动合并 `docs/arch/guardrails-fragment.json`）→ 将 `docs/intent.md` 迁入 `.guardrails/intent.md` 并删除一次性交接片段 → 跑通 `repo_guard.py --run-check`**。
   - **已有旧仓演进**：`boundary_rules` 无旧债棘轮，新边界规则随“迁完调用方并删旧接口”的那个切片写入 `.guardrails/config.json`。

## 契约与移交门禁

进入 `02-codebase-guardrails.md` 开始切片 1 编码前必须确认：

1. `docs/intent.md`（八字段齐备）、`docs/adr/0001-stack.md`、`ARCHITECTURE.md`、`docs/arch/dataflow.md`、`docs/arch/contracts.md`、`docs/arch/slice-queue.md`（与可选 `guardrails-fragment.json`）已全部落盘且通过独立视角挑刺；
2. `python "<skill绝对路径>/scripts/repo_guard.py" --root "<目标项目绝对路径>" --check-arch` 退出码为 `0`（`guard_status: arch_ready`）；
3. 已锁死切片 1（`S1`）的端到端演示入口与验证钩子，未提前创建残缺的 `.guardrails/` 目录。
