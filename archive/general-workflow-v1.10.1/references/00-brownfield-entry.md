# 接手旧项目入口

接手一个不是本流程建起来的仓库，缺的不是阶段，是事实：没有合同、没有 A-ID、没人说得清它做什么，而代码已经在跑。本文件不是第十二个阶段，是 P0 到 07 的另一种走法：同一套模板，来源从对话换成仓库。全部产出落成带指针的文件——agent 的理解在会话结束时就没了，文件不会。

**先读全量，再调用。** 每个注册入口一行、每个模块一行，都进文档；内部函数不写。审阅前只读，审阅后只对用户保留的行真调用。读便宜，调用贵，贵的只花在定下来的行上。

## 入口条件

同时成立才走本文件：

- 目标仓库已有代码，没有 `docs/workflow/`，也没有 99-state-and-handoff.md 说的旧单文件状态；
- 用户要接手、继续开发、整理或重构它，不是只问方法。

本流程建的项目不走这里：状态脚本退出 0 就按 00-progress-router.md 的阶段选择表进阶段。迁移和线上故障修复仍在流程之外；接手时发现的兼容面，在第 1 步的画像里确认，不静默扩大范围。

## 第 0 步：跑起来，建游标

06-scaffolding-and-ci.md 的干净 clone 验证原样执行：临时目录 clone，按仓库自己的说明跑安装、检查、测试，记录命令、版本、结果和失败原因。红的测试只记录不修，那是范围防火墙的事；跑不起来就是接手的第一个阻塞，写进 Open decisions，不往下猜。

同一轮建 `docs/workflow/`，布局按 99-state-and-handoff.md：

- `lifecycle: IDEA`。接手的合同还不存在，这是事实，不是委屈；
- `tier` 按已知的明显事实先定：有线上用户、外部调用方、资金或隐私数据就不是 LEAN；`path` 随之；
- `acceptance_source` 和 `delivery_target` 草稿期填 `-`，backlog 只有表头，`slices/` 为空；
- `next_action` 写梳理到了哪个模块和怎么验证。它是梳理的游标：仓库大到一个会话读不完时，下个会话从这里续，不从头再读。

## 第 1 步：全量读

产出一份现状文档，例如 `docs/architecture-as-is.md`，登记进 project.md 的 Authoritative sources。它记**看到的**，不记应该的；每行带文件位置和 `@ <commit>`。六节：

1. **画像**。按 00-project-profile.md 的模板填，来源是仓库不是对话；`compat_surface` 写实际兼容面，请用户确认后 `tier` 定稿。填完回本文件，不进 01。
2. **入口表**。从组合根反查，不从目录名猜：路由注册、console_scripts、消费者、调度器、cron 注释。每条记入口、注册位置、调用方、现有测试。它是后面 A-ID 的候选池，缺一条就少一条验收。
3. **模块表**。每个顶层模块一行：职责、公开入口、拥有的数据、依赖谁、被谁依赖。有独立职责、特殊约束或验证方式的模块按 07-vertical-slice.md 的模块 `AGENTS.md` 模板建文件，基于观察的写 `observed @ <commit>`；没有额外规则的目录不建。
4. **数据与外部依赖**。存储、表或集合的写入者、敏感字段、外部系统及其替身。
5. **形态与依赖方向**。用 05-architecture-design.md 的表填现状：形态、边界、所有权、依赖方向。不写 ADR，没人做过决定；写一行重评条件。
6. **结构偏离**。对照 05 的依赖规则、06 的门禁和 08 的真实入口规则列事实：跨模块直写表、循环依赖、只有测试会走的平行实现、秘密入库、没有组合根。每行记事实、违反的规则、影响的入口，状态写 `未授权`。这一节只是清单，进 03-scope-and-nongoals.md 的后续队列；变成工作要用户或 C-ID 授权，00-refactor-path.md 的 `authorized_by` 在这里落地。

## 第 2 步：agent 先下结论，反向出需求文档

不等用户开口，agent 先写它认为的答案，但每条带依据：来自 README、路由名、测试名，还是纯读代码。用户能分辨它是看来的还是猜的，才审得动。

文件例如 `docs/requirements.md`，形状沿用 01-requirements-and-goals.md 的目标合同和 02-scenarios-and-acceptance.md 的验收矩阵，多两样：status 行和依据列。

~~~markdown
# Requirements (derived)
- status: derived @ <commit> | reviewed <YYYY-MM-DD>
- problem: <agent 的结论；依据：README 第几节 / 测试名 / 仅代码>
- primary_users: <同上，带依据>
- entrypoints: <入口表的汇总>
- non_goals_observed: <代码里明确拒绝或没有的事，带依据>
- constraints_observed: <平台、版本、外部合同，带依据>

## 验收场景
| A-ID | module | actor | entrypoint | action | observable result | basis | confidence | review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-01 | reports | ops | `ledger-export` | --from --to | exit 0，CSV | tests/test_export.py 绿 @ abc123 | verified | - |
| A-02 | billing | web | POST /invoices | body {...} | 201，invoices 新增 1 行 | 仅代码 web/app.py:41 | low | - |

## 审阅结论
<用户审阅后由 agent 填：日期、每行的答案、改动的行及其 C-ID、决定修的结构偏离>
~~~

每个入口行为一条 A-ID，按模块分组，低置信度的行排前面。basis 写这行怎么来的：第 0 步跑绿的测试、`--help`、只读的 GET 这类零成本调用可以用作依据，标 `verified`；除此之外不在审阅前做调用。

写完把 `next_action` 改成「用户审阅 docs/requirements.md 的 N 条 A-ID」，`lifecycle` 仍是 IDEA。**停在这里等用户**：不建切片，不改代码。

## 第 3 步：用户审阅

用户对每行给一个答案，写进 review 列：

| 答案 | agent 的动作 |
| --- | --- |
| 保留 | 行不动，进第 4 步基线 |
| 改成… | 走 03-scope-and-nongoals.md 的变更协议记 C-ID；新 A-ID 加进表等认领；旧行保留作记录，backlog 标 dropped 指向该 C-ID |
| 不要了 | 记 C-ID；行保留，backlog 标 dropped；要删代码另立 A-ID |
| 不知道 | 按保留处理并基线，另记一条 Open decision |

第四种必须有：没有它，用户会在不确定时被迫选保留，偏差就藏进了「已确认」。项目做什么、给谁用两项也在这一步定：用户改了，agent 的结论就换成用户的，依据写「用户 <日期>」。

审阅完：`status` 改 `reviewed`，`lifecycle` 改 DEFINED，`acceptance_source` 指向这份文件的验收场景表，backlog 每个 A-ID 一行、slice 列全部 `-`，`delivery_target` 用用户接手时给的终点。这一步在现有规则里就是一次整仓库的 P0 回流：指出差异、解决含义、同步权威记录，只是一次做完。

## 第 4 步：基线，再调偏差

保留的行在接手 commit 上各真调一次，evidence 写成 99-state-and-handoff.md 要求的 `<调用> → <观察到的结果> @ <commit>`，进一条特征切片 `slices/S-00.md`：格式同功能切片，`owner`、`claimed`、`write_scope` 都填 `-`，`stage` 写 `0 接手基线`，全部行 delivered，不需要 `## Slice map`。它没有 owner，因为没人认领过它；它的行 delivered，因为行为已经存在并且被调过。

调不了的行——没有环境、没有数据、入口只在生产存在——不留 `-` 等着，那会让接手永远收不了口。backlog 标 `deferred`，C-ID 写明「无环境可调，未受保护」；它是已接受的风险，进 04-constraints-quality-risks.md 的风险登记。

之后 00-progress-router.md 接管。要改的行等认领，走 07 到 09；用户在审阅结论里圈定要修的结构偏离，开 `R-` 切片，`authorized_by` 指向 `docs/requirements.md#审阅结论`，保护表从 S-00 拿。

## 收口门禁

接手收口，以下全部成立：

1. 干净 clone 的记录在，或阻塞已写进 Open decisions；
2. 现状文档六节齐全，入口表每行有注册位置；
3. 需求文档 `status` 为 reviewed，审阅结论已填；
4. 保留的行都进了 S-00 或 deferred，evidence 和 C-ID 的形状过脚本；
5. 状态脚本退出 0；
6. `lifecycle` 按事实跳：有要改的行进 BUILDING，已发布且无欠账进 OPERATING。中间几级的事实——架构有记录、干净 clone 跑过、入口打通——现状文档和第 0 步已经给了，不补文档。

## 停止条件

- 干净 clone 跑不起来，修法要改代码：记阻塞，问用户，不在梳理里修；
- 项目做什么仓库说不清：结论照写，标 low，等审阅，不补造；
- 入口靠运行时动态注册、反查不出注册点：入口表标「未能枚举」，写明方法，不假装全；
- 用户审阅未回：停在第 2 步，不建切片，不动代码；
- 梳理中想顺手修偏离：进后续队列，回到第 1 步第 6 节的规则。

档位只改证据量：LEAN 的减免行在 00-lean-path.md，HIGH-RISK 的加深行在 00-project-profile.md，本文件不复制。
