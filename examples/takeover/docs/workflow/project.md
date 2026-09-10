# Project
updated: 2026-09-10 / 3f9e2c1

- state_version: 2
- lifecycle: BUILDING
- tier: STANDARD
- path: full
- next_action: 认领 A-10：建 S-01，先写「作废后 audit 表新增 1 行」的失败测试；验证：pytest tests/test_web.py -k void_audit 红，状态脚本退出 0 且 A-10 in-slice
- acceptance_source: docs/requirements.md#验收场景
- delivery_target: docs/requirements.md#审阅结论 / implementation-and-tests

接手走的是 `00-brownfield-entry.md`：第 0 步建这个文件时 `lifecycle` 是 IDEA、后两个字段是 `-`，
`next_action` 记梳理到了哪个模块；需求文档审阅完改成 DEFINED；基线跑完按事实跳到 BUILDING，因为
A-10 还欠着。这里保留的是跳完之后的样子。

## Authoritative sources

- 现状：`docs/architecture-as-is.md`（observed @ 3f9e2c1，含干净 clone 记录和结构偏离）
- 需求与验收：`docs/requirements.md`（reviewed 2026-09-10）
- 变更记录：`docs/changes.md`
- 接手基线：`docs/workflow/slices/S-00.md`

## Confirmed decisions

- 2026-09-10 档位 STANDARD：对外 API 两家客户、三年账单数据、单团队 → docs/architecture-as-is.md#画像
- 2026-09-10 作废必须留痕，由 A-10 承接，A-04 不再受保护 → docs/changes.md#C-01
- 2026-09-10 每日摘要邮件不要了 → docs/changes.md#C-02

## Open decisions

- D-01 nightly_reconcile 的对平规则是否仍正确 | 阻塞: 无，A-08 已按 C-03 记为未受保护 | 需要: 用户找财务确认规则，加一份脱敏快照
