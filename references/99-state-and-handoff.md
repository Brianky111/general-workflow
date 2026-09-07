# 工作流状态与会话交接

从零到交付会跨越多次会话。没有落盘的状态，每次接手都要重新推导画像、阶段、已确认决策和证据链，既慢又容易漂移。本文件定义一份最小状态文件和它的更新规则。

## 状态文件是游标和索引，不是第二份真相

这条规则决定了状态文件的全部形态：

- 它记录**现在在哪、下一步做什么、谁还欠一个决策**；
- 它用**指针**引用需求、ADR、测试和发布证据的权威位置，不复制内容；
- 需求正文、架构决策、验收场景和测试结果各自留在自己的权威位置；
- 状态文件与仓库事实冲突时，**仓库事实赢**，然后修正状态文件。

如果项目已有 issue 跟踪、ADR 目录、项目看板或发布系统，状态文件只补它们没有的那部分：当前阶段游标、跨会话的未决问题和证据入口。不要为了填满模板而把已有系统里的内容抄一遍。

## 位置与规模

- 默认路径 `docs/workflow-state.md`；仓库没有 `docs/` 时用根目录 `WORKFLOW-STATE.md`。
- 一个项目只有一份，纳入版本控制，随代码一起提交。
- 目标 80 行以内，硬上限约 150 行。超出时压缩：已关闭的决策合并成一行并指向 ADR/提交，已完成的切片只留结论。
- 不写秘密、令牌、生产连接串或个人数据。
- 单人一次性脚本、探索性原型或用户明确说不要额外文件时，可以不建；此时在每轮结束的状态汇报中口头交接。

## 状态文件模板

~~~markdown
# Workflow State
updated: <YYYY-MM-DD> / <commit sha>

## Cursor
- lifecycle: IDEA | DEFINED | ARCHITECTURE-READY | BOOTSTRAPPED | SLICE-READY | BUILDING | RELEASE-CANDIDATE | OPERATING | PAUSED | CANCELLED
- stage: <当前阶段编号与名称>
- tier: LEAN | STANDARD | HIGH-RISK
- path: lean | full
- current_slice: <S-ID 名称，或 none>
- slice_acceptance: <该切片覆盖的 A-ID>

## Scope ledger
一行一个 A-ID。这是“还欠多少”和“做完了没有”的唯一权威答案。
只写 ID、状态和指针，不复制场景正文。
| A-ID | status | slice | evidence |
| --- | --- | --- | --- |
| A-01 | delivered | S-01 | <命令 / CI 链接 / 提交> |
| A-02 | in-slice | S-02 | - |
| A-03 | remaining | none | - |
| A-04 | deferred | none | <变更记录位置> |

## Authoritative sources
| 事实 | 权威位置 |
| --- | --- |
| 项目画像 | <路径或 none> |
| 需求与目标 | <路径 / issue 链接> |
| 验收场景 | <路径 / 测试文件> |
| 范围与非目标 | <路径> |
| 质量目标与风险 | <路径> |
| 架构决策 | <ADR 目录 / 决策表> |
| 测试与证据 | <CI 链接 / 命令> |
| 发布记录 | <release 页 / 部署日志> |

## Confirmed decisions
仅追加。一行一条，指向权威位置。
- <日期> <决策> → <ADR-xxxx / 提交 / 文档锚点>

## Open decisions
只列会改变行为、范围、数据含义、安全、兼容性、成本或不可逆效果的事项。
- <ID> <一句话问题> | 阻塞: <哪条路径> | 需要: 用户决定 / 实验 / 外部信息

## Evidence
- last_green: <命令> → <结果> @ <commit>
- ci: <最近一次流水线结论与链接>
- deployed: <环境 / 版本 / 时间，或 none>

## Next action
- <一个可执行动作>
- verify: <验证命令或可观察结果>
~~~

字段可以为空，但不要删除；空字段本身是信息，说明这一项还没有权威位置。

## 范围台账规则

四条规则决定这张表可不可信：

1. **状态只有五种**：`remaining`（未开始）、`in-slice`（在当前切片里）、`delivered`（已交付）、`deferred`（本版本不做，已走变更协议）、`dropped`（已取消，已走变更协议）。不要发明中间态。
2. **进入 delivered 的唯一条件是通过 09-testing-review-integration.md 的 Definition of Done**，并且同一行必须填上 evidence 指针。没有证据的 delivered 视为无效，按 remaining 处理。
3. **delivered 单调不可退**。已交付的 A-ID 不能改回 remaining。行为出问题时它是一个新缺陷，走 03-scope-and-nongoals.md 的变更协议决定是否重开范围，而不是把台账改回去。
4. **deferred 和 dropped 必须指向变更记录**。范围缩小是一个决策，不是一次静默的删行。

台账的行来自阶段 2 的验收矩阵（快路径来自一页合同的验收场景表）。新增 A-ID 只能由需求或范围变更产生，不能在实现过程中顺手添加。

“当前范围是否交付完毕”的判定：没有 `remaining`，也没有 `in-slice`。

## 会话开始：读取并校验

接手一个已有状态文件时，先做三次廉价校验，再相信它：

1. **游标对不对**：`current_slice` 和 `stage` 指向的代码/测试是否真的存在？
2. **绿色还在不在**：`last_green` 的命令现在是否仍然通过？
3. **有没有别人动过**：`updated` 的 commit 是否落后于当前 HEAD？落后就先看这段 diff 改了什么。
4. **台账对不对**：抽查一个 `delivered` 的 A-ID，它的 evidence 指向的命令或 CI 记录现在还成立吗？

任意一项对不上，以仓库为准修正状态文件，并在本轮汇报里说明差异。不要在一个已经失真的游标上继续推进。

状态文件缺失时，按 00-progress-router.md 正常推导阶段，并在本轮结束时建立它。

## 会话结束：更新

每轮结束、以及每次通过阶段门禁时更新：

- 游标推进到新的 lifecycle/stage/slice；
- 本轮确认的决策追加到 Confirmed decisions，指向 ADR 或提交；
- 已解决的 Open decisions 移走，新出现的加入；
- 范围台账按本轮实际结果推进：进入切片的改 in-slice，通过 09 门禁的改 delivered 并补上 evidence；
- Evidence 更新为本轮真实跑过的命令和结果，不写“应该能过”；
- Next action 只留一个，并带验证方式；
- 更新 `updated` 的日期和 commit。

状态文件的更新是提交的一部分，不是事后补记。如果本轮没有产生任何可验证的推进，写明原因（等用户决策、等外部依赖、实验失败），不要把游标往前挪。

## 反模式

- 把需求正文、验收场景或架构理由抄进状态文件，形成第二份会漂移的真相；
- 用状态文件声明“已完成”，但 Evidence 里没有命令、提交或运行结果；
- 让 Open decisions 无限增长，把不阻塞的想法也堆进去——那些属于后续队列；
- 把 A-ID 标成 delivered 却不填 evidence，或为了让台账好看把没做完的行删掉；
- 阶段没有真正通过门禁就先把游标改成下一阶段；
- 因为状态文件没建立就拒绝开工。
