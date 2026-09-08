# 工作流状态与会话交接

从零到交付会跨越多次会话，也可能随时加入第二个人。状态必须落盘，否则每次接手都要重新推导；而且必须**分片**落盘，否则第二个人一加入就开始抢同一个文件。

## 状态文件是游标和索引，不是第二份真相

这条规则决定了状态的全部形态：

- 它记录**现在在哪、下一步做什么、谁在做、谁还欠一个决策**；
- 它用**指针**引用需求、ADR、测试和发布证据的权威位置，不复制内容；
- 状态与仓库事实冲突时，**仓库事实赢**，然后修正状态。

项目已有 issue、ADR 目录或发布系统时，状态只补它们没有的那部分：阶段游标、切片归属和证据入口，不把已有内容抄一遍。

## 为什么分片

一个文件放全部状态，两个人一起干活时会撞在两处：

- **游标**：甲在切片 A 做阶段 8，乙在切片 B 做阶段 5。两边都对，但一个 `stage` 只能写一个值——**这不是合并冲突，是模型表达不了**；
- **追加**：两人在同一张表末尾各加一行，插在同一位置。

分片的原则只有一条：**把最频繁变更的内容，拆到每份只有一个写者的文件里。**

## 布局

```text
docs/workflow/
  project.md          档位、路径、生命周期、权威来源、已确认决策   ← 罕见变更
  backlog.md          每个 A-ID 归属哪条切片，或未认领/已延后/已取消
  slices/
    S-01.md           owner、认领、stage、验收状态、证据、写入范围 ← 单一 owner 独占
    S-02.md
```

一条切片一个文件：切片是自然的所有权单位，没人会认领半条；按 A-ID 拆只会多出几十个碎文件。

单人项目也用同一套布局：多两个文件代价很小，而“随时能插入第二个人”一旦有条件就等于不支持。

## project.md

~~~markdown
# Project
updated: <YYYY-MM-DD> / <commit>

- lifecycle: IDEA | DEFINED | ARCHITECTURE-READY | BOOTSTRAPPED | SLICE-READY | BUILDING | RELEASE-CANDIDATE | OPERATING | PAUSED | CANCELLED
- tier: LEAN | STANDARD | HIGH-RISK
- path: lean | full
- acceptance_source: <项目相对路径.md#当前版本验收所在标题；尚无验收时填 ->
- delivery_target: <指向目标合同/一页合同的完成边界> / <implementation-and-tests | release-ready | deployed:环境>

## Authoritative sources
| 事实 | 权威位置 |
| --- | --- |
| 需求与验收 | <同 acceptance_source，或其对应的 issue> |
| 约束与质量目标 | <Q-ID 表 / 风险登记> |
| 架构决策 | <ADR 目录 / 决策表> |
| 变更记录 | <路径；见 03-scope-and-nongoals.md 的变更协议> |
| 测试与证据 | <CI 链接 / 命令> |
| 发布记录 | <release 页 / 部署日志> |

## Confirmed decisions
仅追加，一行一条，指向权威位置。
- <日期> <决策> → <ADR-xxxx / 提交>

## Open decisions
只列会改变行为、范围、数据含义、安全、兼容性、成本或不可逆效果的项目级事项。
切片内部的阻塞写在切片文件里。
- <ID> <一句话问题> | 阻塞: <哪条路径> | 需要: 用户决定 / 实验 / 外部信息
~~~

`lifecycle` 是项目级的；**`stage` 不在这里**，它属于切片。字段名与 00-project-profile.md 的画像输出一致，画像可整段并入。

`delivery_target` 的终点取自用户已给的授权，不由 skill 扩大；取值含义见“范围完成与任务结束”。脚本只检查它已填写，不验证授权本身。

### 可校验的验收来源

`acceptance_source` 直接指向当前版本的权威验收表，例如 `docs/contract.md#验收场景`；`#` 后是唯一标题的原文（非 URL slug），省略时读取整个文件。脚本读取所选范围内以 `A-ID` 为首列的 Markdown 表，忽略代码围栏中的示例。A-ID 形如 `A-` 加字母数字点下划线连字符。

- 来源必须是项目内、`docs/workflow/` 外的 UTF-8 Markdown 文件；不要从 backlog 反向生成“权威清单”。若权威在 issue 系统，先导出当前版本验收表，状态只指向该导出。
- 选中范围保留本版本所有已纳入的 A-ID，包括后来 deferred/dropped 的行；未纳入的候选放在别的章节。来源集合与 backlog 必须相等，缺行、额外行、重复 ID、缺失或空表都阻止完成判定。
- IDEA/DEFINED 且还没有台账行和切片时可填 `-`；这是未定义范围，`scope_verified=false`、`scope_complete=false`，不阻止继续澄清。验收形成后填写来源再建立台账。
- 来源与台账同时被错误删改时脚本无法证明原承诺；它只检查当前文件的一致性，范围变更仍须保留决策和 diff。

旧项目首次使用新版脚本时，从已有合同补 `acceptance_source`，从现有请求补 `delivery_target`；保留既有 ID 和证据，按差异补回台账，不重新定义承诺来消除错误。

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

**backlog 只记归属，不记状态。** 这是分片能生效的关键：最频繁的操作——改状态——只动单一 owner 的 `S-01.md`。

`slice` 列取切片 ID、`-`（未认领）、`deferred`、`dropped`；后两者必须在 note 里指向变更记录。

行来自阶段 2 的验收矩阵（快路径来自一页合同）；新增只能由需求或范围变更产生。

## slices/S-0N.md

~~~markdown
# Slice S-01: <名称>
- owner: <稳定且唯一的个人/agent 标识>
- claimed: <YYYY-MM-DD> / <commit>
- stage: <编号与名称>
- write_scope: <项目相对路径，多个路径用逗号或分号分隔；例如 src/items; tests/items>
- architecture_hypothesis: <H-ID，或 none>

## Acceptance
| A-ID | status | evidence |
| --- | --- | --- |
| A-01 | delivered | <调用> → <观察到的结果> @ <commit> |
| A-02 | in-slice | - |

## Blockers
- <本切片内部的阻塞；没有就删掉本节>
~~~

这是切片文件的唯一格式。07-vertical-slice.md 的切片地图字段写进本文件的 `## Slice map` 一节，不另建文件。

**字段只在第一个 `##` 之前生效。** Blockers 里的 `- owner: 等 X 确认` 是叙述不是认领；同一字段不要出现两次，脚本对重复报错。

## 范围台账规则

台账分布在 backlog 与切片文件中：

1. **两列，五种取值**：切片文件的 `status` 只取 `in-slice` 和 `delivered`；backlog 的 `slice` 列取切片 ID、`-`（即 remaining）、`deferred`、`dropped`。不要发明中间态，也不要把 `deferred`/`dropped` 写进切片文件。
2. **进入 delivered 的唯一条件是通过 09-testing-review-integration.md 的“单条 A-ID：可以标 delivered”**，并在同一行填上 evidence。evidence 记的是一次真实调用及其结果，写成 `<调用> → <观察到的结果> @ <commit>`，格式和各形态的调用方式见 09。只写命令、只写占位（`无`、`待补`、`TODO`、`-`）或"代码已完成"，脚本都会拒绝。
3. **delivered 单调不可退**。行为出问题是一个新缺陷，走 03-scope-and-nongoals.md 的变更协议决定是否重开范围，而不是把台账改回去。
4. **deferred 和 dropped 必须指向变更记录。** 范围缩小是一个决策，不是一次静默删行。
5. **进度只写在切片文件里，归属与终止只写在 backlog。** 同一个事实不要两处都写。

## 范围完成与任务结束

这里是完成判定的权威定义，其余阶段引用本节：

1. **验收范围完成**：权威 A-ID 集合已读取且与 backlog 相等，校验无错误，没有 remaining 和 in-slice，所有 delivered 都有证据指针。同时成立脚本才输出 `scope_complete=true`；来源未定义或不可验证时不得判完成。
2. **任务结束**：验收范围完成后，对照原始请求及已接受变更，逐项核对 `delivery_target` 所指合同完成边界的全部承诺结果、必要约束和实际证据。`delivery_target` 的终点决定收尾位置：`implementation-and-tests` 可在 09 后结束；`release-ready` 必须完成 10 的 Release Ready；`deployed:环境` 必须完成该环境的发布及观察窗口。台账清空不证明需求拆解完整，脚本退出码 0 也只表示状态有效。

完成边界在 01 或 LEAN 合同中确定，按 03 的变更协议维护，状态只存指针。收尾发现承诺遗漏时，按原因回 02 补验收、08 补实现，意图歧义回 P0；保留已有 ID 和证据补项，不能删改承诺凑完成。

用户限定只做设计或骨架时，以该阶段约定的产出收尾，保留未完成台账。权限或外部条件阻塞时记录阻塞与下一动作，不伪造完成。

## 认领规则

第二个人加入的第一分钟：跑一次状态脚本，看见哪些 A-ID 未认领，认领一条，开工。

1. **认领即在自己的切片文件里写上 owner 和 claimed**，同时把 backlog 中对应 A-ID 的 slice 列指向该切片。认领会修改共享 backlog；开始工作前同步认领记录并重跑校验，不能把文件分片当作跨分支的原子锁。
2. **不要抢一个 owner 有新鲜证据的切片**（近期提交、CI 运行、刚更新的 evidence）。接手先与该 owner 或用户确认。
3. **在途切片必须有 owner、有效 claimed 日期和 write_scope。** 路径是项目内的真实文件/目录，不支持 glob；`.` 表示整个项目，只在没有其他在途切片时可用。脚本解析 `.`、`..`、已有链接及 Windows 大小写后检查重叠；重叠先调整边界或排序，不同时开工。
4. **一次一条。** 同一 owner（忽略大小写）只能持有一条**在途**切片。在途 = 有 in-slice 行，或已写上 owner 但还没有任何 delivered 行——认领发生在验收行写下之前，空切片一样占住 write_scope。全部行 delivered 后该切片释放路径，可以认领下一条。
5. 接手一条 stale 切片（owner 已久无证据）时，在该切片文件里记录交接原因和日期。
6. **归还与改判。** 不做这条切片了：把未完成的 A-ID 行从切片文件删掉，backlog 对应格改回 `-`，或改成 `deferred`/`dropped` 并指向变更记录，原因写进 Blockers。这不是“删行凑完成”——A-ID 仍在来源和 backlog 里，完成度是变远不是变近。已 delivered 的行不参与归还。
7. **范围中途变化。** 要动 write_scope 之外的路径时就地修订并重跑脚本。与在途切片重叠时由两个 owner 约定边界：一方收窄，或把这处改动交给该路径的 owner，结论写进 Blockers。

## 会话开始：读取并校验

定位本次加载的 `SKILL.md` 所在目录，从那里调用脚本并显式传入目标项目。替换下面的绝对路径；目标项目不自带此脚本，也不要切到 skill 目录后漏掉 `--root`：

```powershell
python "<skill绝对路径>/scripts/workflow_status.py" --root "<目标项目绝对路径>" --json
```

它给出当前切片、owner、未认领项和违规项；退出码非零先修状态。没有状态目录时返回 `state_status=uninitialized` 且范围未完成；已有目录却缺必需文件时报错。两种情况都仍输出 JSON。旧状态缺字段时按上面的迁移说明补齐。

脚本给不出的部分靠三次廉价校验：

1. **游标对不对**：切片文件里的 `stage` 和 A-ID 指向的代码/测试是否真的存在？
2. **绿色还在不在**：最近一次 evidence 的调用现在是否仍返回同样结果？
3. **有没有别人动过**：`updated` 的 commit 是否落后于当前 HEAD？落后就先看这段 diff。

任意一项对不上，以仓库为准修正状态，并在本轮汇报里说明差异。不要在一个已经失真的游标上继续推进。

状态目录缺失时，按 00-progress-router.md 正常推导阶段，并在本轮结束时建立它。

## 会话结束：更新

每轮结束、以及每次通过阶段门禁时更新：

- 切片文件的 `stage` 推进；通过 09 单条门禁的 A-ID 改 `delivered` 并补 evidence；
- 本轮确认的项目级决策追加到 project.md，指向 ADR 或提交；
- 已解决的 Open decisions 移走，新出现的加入；
- evidence 写本轮真实发起的调用和观察到的结果，不写“应该能过”；
- 更新 `updated` 的日期和 commit；
- 再跑一次状态脚本，退出码为零才算收尾。

状态更新是提交的一部分。本轮没有可验证的推进时写明原因，不要把游标往前挪。

## 反模式

- 把需求正文、验收场景或架构理由抄进状态文件，形成第二份会漂移的真相；
- 让 Open decisions 无限增长，把不阻塞的想法也堆进去；
- 阶段没有真正通过门禁就先把 `stage` 改成下一阶段；
- 因为状态目录没建立就拒绝开工。
