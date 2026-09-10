# Requirements (derived)

- status: reviewed 2026-09-10
- problem: 财务要按客户和时间段查账单、开账单、登记支付和作废；运营要导出明细；两家客户的对账系统按 `/api/v1` 拉账单核对。现有工具是三年前一个人写的，没人说得清全部入口。依据：README 缺失；路由名、CLI 帮助；用户 2026-09-10 审阅时改了一处（对账系统是硬兼容面，不只是「导出给人看」）
- primary_users: 财务 4 人（web 管理台）；运营 2 人（CLI）；客户对账系统 2 家（`/api/v1`）。依据：web/app.py 的登录角色、setup.py、客户合同（用户提供）
- entrypoints: 4 条页面路由、1 条对外 API、1 条 CLI、2 个 cron；清单在 docs/architecture-as-is.md#入口表
- non_goals_observed: 不开发票（schema 没有税务字段）；不做多币种（amount 单一 numeric）；不做权限分级（登录即全部）。依据：schema、web/app.py
- constraints_observed: Python 3.9；Postgres 13；`/api/v1/invoices` 的 JSON 字段名两家客户系统依赖，改名要走兼容窗口。依据：requirements.txt、客户合同

## 验收场景

低置信度的行排前面，审阅从最不确定的地方开始。basis 写这行怎么来的；confidence 取 verified（零成本真调用或走真实入口的测试绿）、high（测试绿但走替身）、low（仅代码）。

| A-ID | module | actor | entrypoint | action | observable result | basis | confidence | review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-04 | web | 财务 | `POST /invoices/<id>/void` | 对 open 或 paid 的账单点作废 | 302 回列表；invoices.status 变 void，其余不变 | 仅代码 web/app.py:112；无测试 | low | 改成：作废必须留痕，写 audit 行 → C-01，新行 A-10 |
| A-05 | web | 客户对账系统 | `GET /api/v1/invoices?customer=<id>` | 带 token 请求 | 200；JSON 每条 id/amount/issued_at/status，status 取值 open/paid/void | 仅代码 web/api.py:58；无测试；两家客户依赖字段名 | low | 保留 |
| A-08 | scripts | 系统 | scripts/nightly_reconcile.py | crontab 02:00 | payments 与 invoices 对平，差异写 reconcile_log | tests/test_reconcile.py 3 条红（断言过期）；要生产库快照 | low | 不知道：财务也说不准对平规则 → 按保留处理；调不了，C-03 deferred，登记 D-01 |
| A-09 | scripts | 系统 | scripts/daily_digest.py | crontab 07:00 | 给财务发当日账单摘要邮件 | 仅代码；SMTP 凭据明文；无测试 | low | 不要了：财务从没看过这封邮件 → C-02 |
| A-01 | web | 财务 | `GET /invoices?customer=&from=&to=` | 已登录，按客户和区间筛 | 200；表格列出区间内账单和合计 | tests/test_web.py::test_list_filters 绿，走 InMemoryLedger 替身 | high | 保留 |
| A-02 | web | 财务 | `POST /invoices` | body customer、amount | 302 到新账单页；invoices 新增 1 行 status=open | tests/test_web.py::test_create 绿，走替身 | high | 保留 |
| A-03 | web | 财务 | `POST /invoices/<id>/pay` | 对 open 账单登记全额支付 | 302；status 变 paid；payments 新增 1 行 | tests/test_web.py::test_pay 绿，走替身 | high | 保留 |
| A-06 | reports | 运营 | `ledger-export --from --to --out` | 合法区间 | 退出码 0；CSV 表头固定，行数等于区间内账单数 | tests/test_export.py::test_range 绿 @ 3f9e2c1，真实组合根 + 种子库 | verified | 保留 |
| A-07 | reports | 运营 | 同上 | --from 晚于 --to | 退出码 2；stderr 指明参数；不产出文件 | tests/test_export.py::test_bad_range 绿 @ 3f9e2c1 | verified | 保留 |
| A-10 | web | 财务 | `POST /invoices/<id>/void` | 同 A-04 | 302；status 变 void，且 audit 表新增 1 行记操作人和时间 | 用户 2026-09-10 审阅（C-01） | - | 新增，待认领 |

## 审阅结论

- 2026-09-10 用户逐行审阅，答案在 review 列。改：A-04 → C-01，新增 A-10（作废留痕）。不要了：A-09 → C-02。不知道：A-08，按保留处理，基线跑不了，C-03 deferred，登记 D-01。其余六行保留，进 S-00 基线。
- 项目做什么：用户改了一处——客户对账系统按 `/api/v1` 拉数是硬兼容面，不是「导出给人看」的附带功能。problem 一行的依据改为用户审阅。
- 结构偏离：用户圈定第一条（reports 和 scripts 直写 billing 的表）在 A-10 之后处理，届时开 R-01，`authorized_by` 指向本节；其余两条留在队列，不是授权。
- 交付终点：本批只要实现和测试，`implementation-and-tests`；发布仍走原来的手工部署，不在本批内。
