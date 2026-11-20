# 工作流状态与会话交接

从零到交付跨越多次会话，也可能随时加入第二个人。状态不落盘，每次接手都要重新推导；不**分片**落盘，第二个人一加入就抢同一个文件。

## 状态文件是游标和索引，不是第二份真相

- 记**现在在哪、下一步做什么、谁在做、谁还欠一个决策**；
- 用**指针**引用需求、ADR、测试和发布证据的权威位置，不复制内容；
- 与仓库事实冲突时，**仓库事实赢**，然后修正状态。

## 为什么分片

一个文件放全部状态会撞在两处：甲在切片 A 做阶段 8、乙在切片 B 做阶段 5，两边都对，可一个 `stage` 只能写一个值——**这不是合并冲突，是模型表达不了**；两人在同一张表末尾追加，插在同一位置。于是一条原则：**把最频繁变更的内容，拆到每份只有一个写者的文件里。**

## 布局

```text
docs/workflow/
  project.md        ← 罕见变更
  backlog.md        ← A-ID 归属哪条切片
  slices/S-01.md    ← 单一 owner 独占
  slices/R-01.md    ← 重构切片，格式在 00-refactor-path.md
  slices/S-00.md    ← 接手基线，无 owner，见 00-brownfield-entry.md
```

一条切片一个文件：没人认领半条，按 A-ID 拆只多出几十个碎文件。单人项目也用这套布局，等第二个人来再拆更贵。

## project.md

~~~markdown
# Project
updated: <YYYY-MM-DD> / <commit>

- state_version: 2
- lifecycle: IDEA | DEFINED | ARCHITECTURE-READY | BOOTSTRAPPED | SLICE-READY | BUILDING | RELEASE-CANDIDATE | OPERATING | PAUSED | CANCELLED
- tier: LEAN | STANDARD | HIGH-RISK
- path: lean | full
- next_action: <下一个可执行动作及其验证命令>
- acceptance_source: <项目相对路径.md#验收所在标题；尚无验收时填 ->
- delivery_target: <完成边界指针> / <implementation-and-tests | release-ready | deployed:环境>

## Authoritative sources
一行一个指针：需求与验收、约束与风险、ADR、变更记录、测试证据、发布记录。

## Confirmed decisions
仅追加，一行一条：<日期> <决策> → <ADR-xxxx / 提交>

## Open decisions
只列会改变行为、范围、安全或成本的项目级事项，切片内阻塞写在切片文件：
- <ID> <一句话问题> | 阻塞: <哪条路径> | 需要: 用户决定 / 实验 / 外部信息
~~~

`state_version` 声明按哪版语义读写，缺失或不等于 `2` 是错误，迁移见下节。`lifecycle`、`tier`、`path` 按枚举校验，`BUILDNG` 这类拼错以前能一路通过。`lifecycle` 是项目级的，**`stage` 不在这里**，它属于切片。

`next_action` 是阶段 1–6 的游标。`lifecycle` 太粗：卡在阶段 5 中途的项目换人接手，只能从 ADR 反推哪几个决策已做完，推错就重做或漏做。必填有前提——**开始记台账之后**（backlog 有行、有切片，或 `lifecycle` 已过 IDEA/DEFINED），没有在途切片且范围未完成就必须已填；草稿期不挡，`lifecycle: IDEA` 配空 backlog 和 `next_action: -` 退出码是 0。切片出现后游标交给 `stage`，可留空。

`delivery_target` 写成 `<指针> / <终点>`，两半都必须有，含义见“范围完成与任务结束”。终点取自用户已给的授权，不由 skill 扩大：脚本取最后一个 ` / ` 之后的片段，必须是模板那三个终点之一，但不验证授权本身；以前只查非空，“差不多做完就行”也能当完成边界。指针也不能省：收尾要核对的承诺和证据都在它指的文档里，只有终点的状态说得出停在哪，说不出交什么。

并入 00-project-profile.md 的画像时，`lifecycle` 和 `tier` 两边都有，**只写一次**：同一字段两次脚本报 `set twice`。其余字段搬进来即可，脚本只读这七个。

### 状态格式版本

状态语义改过两次，那时的文件没有版本标记，脚本分不出“字段写漏了”和“旧格式”。`state_version: 2` 就是这个标记，断言三件事：`next_action` 在，evidence 带箭头和锚点，`delivery_target` 两半齐全。

旧状态由人迁移。**还是单文件的先按“布局”拆分，再做下面三条**：更早的版本一切都在 `docs/workflow-state.md`（或根目录 `WORKFLOW-STATE.md`），`## Cursor` 的 lifecycle/tier/path 进 project.md、`stage` 进 `current_slice` 指的切片文件；`## Scope ledger` 拆两处，`slice` 列进 backlog（`remaining` 写 `-`）、`status` 与 `evidence` 进切片文件；其余小节按同名搬进 project.md。脚本认得 `docs/workflow-state.md` 和 `WORKFLOW-STATE.md` 这两个名字：没有 `docs/workflow/` 而它们在时报 `state_status=legacy`，明说这不是新项目。换个名字或换个位置放的旧状态它看不见，仍报 `uninitialized`——那时别急着另建一套空的，先自己在 `docs/` 下找一遍。

- 补上版本行，从已有合同补 `acceptance_source`、现有请求补 `delivery_target`，没有在途切片时补 `next_action`；
- evidence 改写成模板那一行的形状，“已完成”“见 PR”都不够，找不回当时的调用就重跑一次；
- 三个枚举、以及 deferred/dropped 那条指向变更记录的 note，各校一遍：以前都不查，拼错和 `follow-up` 就一直躺在旧状态里。

既有 A-ID 和证据保留；最后一条漏了也迁得过去，脚本会逐条报错。

### 可校验的验收来源

`acceptance_source` 指向当前版本的权威验收表，例如 `docs/contract.md#验收场景`：`#` 后是唯一标题的原文（非 URL slug），省略时读整个文件；脚本读该范围内以 `A-ID` 为首列的 Markdown 表，忽略代码围栏里的示例。

- 来源是项目内、`docs/workflow/` 外的 UTF-8 Markdown 文件，不要从 backlog 反向生成“权威清单”；权威在 issue 系统时先导出，指向导出。
- 选中范围保留本版本已纳入的全部 A-ID（含后来 deferred/dropped 的行），未纳入的候选放别处。缺行、额外行、重复 ID、空表都阻止完成判定；backlog 的新增只能来自需求或范围变更。
- IDEA/DEFINED 且还没有台账行和切片时填 `-`：未定义范围不判完成，但不阻止继续澄清；验收形成后再建台账。

## backlog.md

~~~markdown
# Backlog
| A-ID | slice | note |
| --- | --- | --- |
| A-01 | S-01 | |
| A-05 | - | 未认领 |
| A-09 | deferred | 变更记录 C-03 |
| A-11 | dropped | 变更记录 C-02 |
~~~

`slice` 列取切片 ID、`-`（未认领）、`deferred`、`dropped`。后两者的 note 必须指向变更记录，脚本要求有 `C-<数字>`、路径或 URL：范围缩小是一个决策，不是静默删行；“以后再说”不算，三个月后没人能从这行还原当初为什么不做。

## slices/S-0N.md

~~~markdown
# Slice S-01: <名称>
- owner: <稳定且唯一的个人/agent 标识>
- claimed: <YYYY-MM-DD> / <commit>
- stage: <编号与名称>
- write_scope: <项目相对路径，逗号或分号分隔；例如 src/items; tests/items>
- architecture_hypothesis: <H-ID，或 none>

## Acceptance
| A-ID | status | evidence |
| --- | --- | --- |
| A-01 | delivered | <调用> → <观察到的结果> @ <commit> |
| A-02 | in-slice | - |

## Blockers
- <本切片内部的阻塞；没有就删掉本节>
~~~

这是功能切片的唯一格式：07-vertical-slice.md 的切片地图字段写进本文件的 `## Slice map` 一节，不另建文件。重构切片以 `R-` 开头，格式和规则在 00-refactor-path.md。**字段只在第一个 `##` 之前生效**：Blockers 里的 `- owner: 等 X 确认` 是叙述不是认领；写两次报错。

## 范围台账规则

1. **两列，五种取值**：切片文件的 `status` 只取 `in-slice` 和 `delivered`；backlog 的 `slice` 列取切片 ID、`-`（即 remaining）、`deferred`、`dropped`。不要发明中间态，也别把后两者写进切片文件。
2. **进入 delivered 的唯一条件是通过 09-testing-review-integration.md 的“单条 A-ID：可以标 delivered”**，并在同一行填 evidence：一次真实调用及其结果，写成 `<调用> → <观察到的结果> @ <commit>`。箭头两侧都要有内容，结果那半的结尾还要带定位锚点（`@ <ref>` 或链接），调用里的 URL 不算。只写命令、只写占位（`无`、`待补`、`TODO`）或“代码已完成”都会被拒；边界见文末。
3. **delivered 单调不可退**。行为出问题是新缺陷，走 03-scope-and-nongoals.md 的变更协议决定是否重开范围，不是把台账改回去。
4. **进度只写在切片文件里，归属与终止只写在 backlog。** 同一个事实不写两处。这也是分片生效的关键：改状态最频繁，这样只动单一 owner 的 `S-01.md`。

## 范围完成与任务结束

完成判定的权威定义在这里，其余阶段引用本节：

1. **验收范围完成**：权威 A-ID 集合已读取且与 backlog 相等，校验无错误，没有 remaining 和 in-slice，delivered 都有证据指针——同时成立才输出 `scope_complete=true`。来源未定义或不可验证时不得判完成。
2. **任务结束**：再对照原始请求及已接受变更，逐项核对 `delivery_target` 指向的承诺、约束和证据。终点决定收尾位置：`implementation-and-tests` 可在 09 后结束，`release-ready` 要过 10 的 Release Ready，`deployed:环境` 要完成该环境的发布和观察窗口。台账清空不证明需求拆解完整，退出码 0 也只说明状态有效。有在途的重构切片时不结束任务，先按 00-refactor-path.md 收口它。

完成边界在 01 或 LEAN 合同里确定，按 03 的变更协议维护，状态只存指针。收尾发现遗漏按 00-progress-router.md 的“结束与回流”回到成因阶段，保留已有 ID 和证据。用户只要设计或骨架就以该阶段产出收尾，留着未完成台账；被外部条件挡住就记阻塞和下一动作，不伪造完成。

## 会话开始：读取并校验

脚本在本次加载的 `SKILL.md` 所在目录下，目标项目不自带；调用时显式传入目标项目，别漏 `--root`：

```powershell
python "<skill绝对路径>/scripts/workflow_status.py" --root "<目标项目绝对路径>" --json
```

它给出当前切片、owner、未认领项和违规项，退出码非零先修状态。没有状态目录返回 `state_status=uninitialized`（旁边有旧单文件状态则返回 `legacy`）且范围未完成，有目录却缺文件报错，两种都仍输出 JSON。`uninitialized` 只说明没有 `docs/workflow/`：先看 `docs/` 下有没有旧单文件状态，有就按“状态格式版本”迁移；确实没有：仓库已有代码走 00-brownfield-entry.md，空仓库按 00-progress-router.md 推导阶段并在本轮结束前建。

认领与归还的规则见 07-vertical-slice.md：规则跟着阶段 7 走，本文件常驻上下文，不替它背这一段。

脚本查不出的三件事，自己动手：

1. **游标对不对**：`stage`（还没有切片时是 `next_action`）指向的代码或测试真的存在吗？
2. **绿色还在不在**：最近一次 evidence 的调用现在还返回同样结果吗？
3. **有没有别人动过**：`updated` 的 commit 落后于当前 HEAD 就先看这段 diff。

任意一项对不上，以仓库为准修状态、汇报里说明差异，别在失真的游标上继续推进。

## 会话结束：更新

每轮结束、每次通过阶段门禁时更新：

- 切片文件的 `stage` 推进，还没有切片时改写 `next_action`；
- 通过 09 单条门禁的 A-ID 改 `delivered`，evidence 写本轮真实的调用和结果；
- 本轮确认的项目级决策追加到 project.md 并指向 ADR 或提交，已解决的 Open decisions 移走；
- 更新 `updated` 的日期和 commit，再跑状态脚本，退出码为零才算收尾。

状态更新是提交的一部分。本轮没有可验证的推进就写明原因，不要把游标往前挪。

## 反模式

- 把需求正文或架构理由抄进状态；把不阻塞的想法堆进 Open decisions；
- 门禁没真正通过就先把 `stage` 改成下一阶段，或用一句“下一步继续”当 `next_action`；
- 因为状态目录没建立就拒绝开工，或反过来，把 `uninitialized` 读成“旁边没有旧状态”。

`next_action` 的占位词和 evidence 的定位锚点都是**词表法**：命中表里的写法才拒，表外的说法就过。“下一步继续”被拒后改成“继续推进登录模块”一样能过；`@ HEAD`、`@ main` 这类会移动的引用已单列出来，可 `@ dev`、`@ feature/x` 同样会移动，分支名列不完。脚本读不出动作能不能执行，也读不出锚点是不是钉在固定的一次提交上——两道检查到此为止，后面靠阶段门禁和接手时那三次廉价校验。
