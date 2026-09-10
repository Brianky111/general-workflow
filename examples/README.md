# 示例：两份能被脚本读的工作流状态

这里是两个假想项目的完整状态目录，不是模板片段。它们存在的理由很具体：`tests/` 里的回归测试自己
合成状态文件，那些文件跑完就删，没人看得到；仓库 README 只有截出来的几行。于是模板改了一个
字段、脚本多了一条拒绝规则，谁都不会先撞到红灯。这两个目录把模板固定成实例，
`tests/test_examples.py` 每次对它们各跑一遍状态脚本，模板一漂测试就红。

- `greenfield/`：用本流程从零建起来的项目，一个内部报表导出 CLI。档位 LEAN，路径 lean，
  交付终点 `implementation-and-tests`。
- `takeover/`：接手一个不是本流程建的旧仓库，一个用了三年的内部账单工具。走
  `references/00-brownfield-entry.md`：跑起来、全量读、反向出需求文档、用户审阅、基线。
  档位 STANDARD，路径 full。

## greenfield/：从零建起来的项目

假想的项目是一个内部用的报表导出 CLI：运营自己按日期区间导出订单明细 CSV，不再提工单等工程师
跑 SQL。

### 怎么跑

在仓库根目录：

```powershell
python -X utf8 scripts/workflow_status.py --root examples/greenfield
```

预期退出码 0，输出：

```text
lifecycle BUILDING | tier LEAN | path lean
  S-01  owner=alice  stage=8 真实代码实现  delivered=1 in-slice=1
  unclaimed: A-03
  deferred/dropped: A-04, A-05
still owed: 2 acceptance ids
delivery target: docs/contract.md#完成边界 / implementation-and-tests
next action: -
0 error(s)
```

加 `--json` 看机器读的那份：`scope_verified` 为 true，`scope_complete` 为 false。

### 文件

```text
greenfield/
├── docs/contract.md                  # 权威验收来源：完成边界、A-ID 表、一页架构决策
├── docs/changes.md                   # 变更记录，C-01（延后）和 C-02（取消）在这里
└── docs/workflow/
    ├── project.md                    # 七个字段：state_version 到 delivery_target
    ├── backlog.md                    # 每个 A-ID 归属哪条切片，或 - / deferred / dropped
    └── slices/S-01.md                # owner、write_scope、Slice map、验收与证据
```

### 它证明了什么

backlog 归属列的四种取值——切片 ID、`-`、`deferred`、`dropped`——各占一行，切片文件的两种
status 也各占一行，每一行卡住一条规则：

| 这一行 | 在哪 | 少了它就漏掉哪条规则 |
| --- | --- | --- |
| A-01 `delivered` | S-01.md | evidence 必须写成 `<调用> → <观察到的结果> @ <ref>`。只写命令、只贴一条 CI 链接、写「代码已完成」都会被拒——那些证明的是断言成立或代码存在，不是那个入口真的被调起来并返回了预期结果。锚点还必须落在箭头右边那半边的末尾：`curl https://api.example/orders → 200 OK` 里的 URL 说的是入口在，不是这次跑过。`@ 稍后`、`@ later` 被拒，因为那是承诺不是位置；`@ HEAD`、`@ main` 也被拒，因为它们指向「最后一次提交」，半年后签出来的是别的代码 |
| A-02 `in-slice` | S-01.md | 进度只写在切片文件里。它同时让 S-01 保持在途，于是 project.md 的 `next_action` 可以留空：游标交给切片的 `stage`，两处都写就会漂 |
| A-03 `-` | backlog.md | 未认领只记在 backlog，不进切片文件。它让 `scope_complete` 保持 false——还欠一条验收，台账就没清空 |
| A-04 `deferred` | backlog.md | note 必须指向变更记录，`docs/changes.md#C-01` 这样的文档路径、`C-01` 这样的编号或一条链接才算。「follow-up」「以后再说」不算；「ask/bob」「推迟到 v2/以后」也不算——带个斜杠不等于是路径。范围缩小是一个决策，不是一次静默删行 |
| A-05 `dropped` | backlog.md | 取消和延后走同一条 note 规则，脚本对两者一视同仁。区别写在变更记录里：C-01 有重开条件，C-02 没有。少了这一行，示例就只教了三种取值，而剩下那种正好是最想被静默处理的那种——不做了，顺手把行删掉，台账短一截，完成度好看一截 |

除此之外，这份状态还落到几条容易被忽略的判定上：

- `docs/contract.md` 的「验收场景」表有五个 A-ID，backlog 也是五行，两边集合相等，
  `scope_verified` 才为 true。把 A-04 或 A-05 从两边同时删掉照样能过脚本，但那是改考卷。
- `delivery_target` 写成 `<指针> / <终点>`。终点取最后一个 ` / ` 之后那段，必须是三种形状之一，
  这里是 `implementation-and-tests`，所以 09 之后就能收尾，不必进 10；指针指向
  `docs/contract.md#完成边界`，收尾时逐项核对的就是那张表。两半各修各的：只写终点会被拒，
  指针半边写成「见合同」也会被拒——它得是能打开的东西，路径、链接或 `C-<数字>`。
- `project.md` 用满共享契约的七个字段，写错 `lifecycle`、`tier`、`path` 的取值会直接报错；
  以前不校验，`BUILDNG` 拼错也能一路通过。

### 它不证明什么

- **这里没有 `src/` 和 `tests/`。** 示例演示的是状态文件本身。S-01 的 `write_scope` 指向
  `src/report` 和 `tests/report`，脚本不要求这些路径已经存在——认领发生在写第一行代码之前，
  那时目录通常还没建。
- **evidence 里的 `a1b2c3d` 和「表头加 3 行」是编的。** 示例能证明的只是这一行的形状过得了
  校验；真实项目里它必须来自真跑过的那次调用，否则第一层完成就是伪造的，而这一层正是最容易
  被叙述糊弄的一层。照抄这个目录时，先把 evidence 整列清空。

### 拿它当起点

复制 `docs/workflow/` 三个文件到你的项目，然后依次替换：`acceptance_source` 指向你自己的验收
表，backlog 换成你的 A-ID，切片文件只留头部字段和 `## Slice map`，evidence 清空、status 全改
`in-slice`。`docs/contract.md` 是 LEAN 一页合同的样子，用不用它取决于你的档位。每改一步跑一次
状态脚本，退出码 0 再往下走。

## takeover/：接手一个旧仓库

假想的旧仓库 ledger-tool：Flask 管理台给财务查账单、开账单、登记支付、作废，CLI 给运营导明细，
两个 cron 脚本夜里对账和发摘要邮件。没有 README，40 个测试 6 个红，两家客户的对账系统按
`/api/v1` 拉账单。用户说"先接手，之后作废要留痕"。

### 怎么跑

```powershell
python -X utf8 scripts/workflow_status.py --root examples/takeover
```

预期退出码 0，输出：

```text
lifecycle BUILDING | tier STANDARD | path full
  S-00  owner=-  stage=0 接手基线  delivered=6 in-slice=0
  unclaimed: A-10
  deferred/dropped: A-04, A-08, A-09
still owed: 1 acceptance ids
delivery target: docs/requirements.md#审阅结论 / implementation-and-tests
next action: 认领 A-10：建 S-01，先写「作废后 audit 表新增 1 行」的失败测试；验证：pytest tests/test_web.py -k void_audit 红，状态脚本退出 0 且 A-10 in-slice
0 error(s)
```

### 文件

```text
takeover/
├── docs/architecture-as-is.md        # 现状：跑起来的记录、画像、入口表、模块表、数据、形态、结构偏离
├── docs/requirements.md              # 反向需求文档：status reviewed，每行带依据、置信度和审阅答案
├── docs/changes.md                   # C-01 改、C-02 不要了、C-03 无环境可调
└── docs/workflow/
    ├── project.md                    # 跳完之后的样子：BUILDING，next_action 指向 A-10
    ├── backlog.md                    # 四种审阅答案落成四种取值
    └── slices/S-00.md                # 接手基线：无 owner，六行 delivered
```

### 它证明了什么

| 这一行 | 在哪 | 少了它就漏掉哪条规则 |
| --- | --- | --- |
| A-01 到 A-07 中保留的六行 | S-00.md | 保留的行在接手 commit 真调一次才算基线；`owner`、`claimed`、`write_scope` 全是 `-`，脚本照样通过，因为它不在途。web 那三条审阅时只有走替身的测试，这里的证据是它们第一次经过真实组合根 |
| A-04 改成… | backlog `dropped` → C-01；A-10 `-` | 改行为不是改旧行：旧行留作记录、指向 C-ID，新 A-ID 等认领。`scope_complete` 因此为 false——接手收口了，工作没完 |
| A-09 不要了 | backlog `dropped` → C-02 | 不要的行为也留一行，删行会让它从台账上消失；要删代码另立 A-ID |
| A-08 不知道 | backlog `deferred` → C-03；project.md 的 D-01 | 第四种答案：不确定就先保留并基线。这条调不了，于是 deferred 并写明未受保护，而不是留 `-` 让接手永远收不了口 |
| `status: reviewed` | requirements.md | 审阅前它是 derived，`acceptance_source` 不能指向一份没审过的文档 |
| 结构偏离三行 | architecture-as-is.md | 都标 `未授权`；用户在审阅结论里圈了一条，那一条才会变成 R- 切片，`authorized_by` 指向审阅结论 |

### 它不证明什么

- **没有 `src/`、`tests/`、模块 `AGENTS.md`。** 示例演示的是状态和文档；模块指引和代码不在这里。
- **commit `3f9e2c1`、行号和「表头加 41 行」是编的。** 真实项目里 basis 和 evidence 必须来自真
  跑过的测试和调用；照抄时先把 evidence 整列清空，把 `status` 改回 `derived`。
