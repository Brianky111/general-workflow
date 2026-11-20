# Project
updated: 2026-09-09 / a1b2c3d

- state_version: 2
- lifecycle: BUILDING
- tier: LEAN
- path: lean
- next_action: -
- acceptance_source: docs/contract.md#验收场景
- delivery_target: docs/contract.md#完成边界 / implementation-and-tests

`next_action` 这里填 `-`，因为 S-01 正在途中，游标是它的 `stage`。台账已经开始记、没有在途切片、
范围又还没做完时，这一行必须写着下一个可执行动作及其验证命令，否则脚本报错——backlog 和
`slices/` 都还空着、`lifecycle` 还是 `IDEA` 的草稿期不受这条约束，那时没有什么可交接的。
写「继续」「下一步继续」则任何时候都报错：那只是说工作还没完，而这件事文件本身已经说了，
下一个人还是不知道从哪敲第一条命令。

`delivery_target` 的左半边是指针，右半边才是终点。只写 `implementation-and-tests` 会被拒——
收尾要拿完成边界逐项核对，指针没了就没有对照物，剩下的只有一句「差不多了」。

## Authoritative sources

- 需求、验收与完成边界：`docs/contract.md`
- 变更记录：`docs/changes.md`
- 架构决策与 H-ID：`docs/contract.md` 的「架构决策与假设」（LEAN 一页决策表，未单开 ADR 目录）
- 测试证据：切片文件 `## Acceptance` 表的 evidence 列

## Confirmed decisions

- 2026-09-08 走 LEAN：单人、单进程 CLI、只读数据、无对外兼容承诺 → docs/contract.md
- 2026-09-09 本版只出 CSV，xlsx 延后 → docs/changes.md 的 C-01

## Open decisions

- D-01 created_at 是本地时间还是 UTC | 阻塞: A-01 的区间边界断言 | 需要: 实验（对边界日各查一条已知订单）
