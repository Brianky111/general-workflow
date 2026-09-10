# 现状文档（observed @ 3f9e2c1）

接手时看到的，不是应该有的。每行带位置和 commit；这里没有一条是决定。

## 跑起来

- 2026-09-10 临时目录 clone 3f9e2c1，`pip install -r requirements.txt` 通过（Python 3.9.19，Postgres 13 本地容器）
- `pytest -q` → 34 passed, 6 failed：3 条缺 `LEDGER_DB_URL`，3 条断言过期（tests/test_reconcile.py）。只记录，不修
- `flask run` 起得来，`GET /healthz` → 200；两个 cron 脚本本地不跑，需要生产库快照

## 画像

- shape: Flask web 管理台 + CLI + 两个 cron 脚本，单进程单库
- users: 财务 4 人（web）；运营 2 人（CLI）；客户对账系统 2 家（`/api/v1`）
- entrypoints: web/app.py 注册 4 条页面路由，web/api.py 1 条对外 API；setup.py console_scripts 一条 `ledger-export`；scripts/ 两个 cron
- compat_surface: `/api/v1/invoices` 的 JSON 字段名被两家客户系统依赖；Postgres 里三年账单数据；线上一台机器
- data: invoices、payments、customers、reconcile_log；amount 和客户联系方式敏感
- runtime_units: 一个 web 进程 + cron；无 worker、无队列
- tier: STANDARD。对外 API、线上数据、资金相关；单团队单发布节奏，不到 HIGH-RISK。用户 2026-09-10 确认
- 依据：README 缺失；以上来自代码、schema 和用户答复

## 入口表

| 入口 | 注册位置 | 调用方 | 现有测试 |
| --- | --- | --- | --- |
| `GET /invoices` | web/app.py:41 | 财务 | tests/test_web.py::test_list_filters 绿 |
| `POST /invoices` | web/app.py:67 | 财务 | tests/test_web.py::test_create 绿 |
| `POST /invoices/<id>/pay` | web/app.py:95 | 财务 | tests/test_web.py::test_pay 绿 |
| `POST /invoices/<id>/void` | web/app.py:112 | 财务 | 无 |
| `GET /api/v1/invoices?customer=` | web/api.py:58 | 客户对账系统 | 无 |
| `ledger-export --from --to --out` | setup.py console_scripts → reports/cli.py:12 | 运营 | tests/test_export.py 5 条，绿 |
| scripts/nightly_reconcile.py | crontab 注释 02:00 | 系统 | tests/test_reconcile.py 3 条，红（断言过期） |
| scripts/daily_digest.py | crontab 注释 07:00 | 系统，发邮件给财务 | 无 |

## 模块表

| 模块 | 职责 | 公开入口 | 拥有的数据 | 依赖 | 被依赖 |
| --- | --- | --- | --- | --- | --- |
| billing | 账单与支付的规则和写入 | billing/service.py 的 issue/pay/void | invoices、payments | psycopg | web、reports、scripts |
| reports | 导出与汇总 | reports/cli.py、reports/export.py | 无（只读） | billing 的表（直接 SQL） | web/app.py 的报表页 |
| web | 管理台和对外 API | web/app.py、web/api.py | customers（客户页直接写） | billing、reports | - |
| scripts | 两个 cron | 见入口表 | reconcile_log | billing 的表（直接 SQL）、SMTP | - |

## 数据与外部依赖

- Postgres 13：invoices、payments 由 billing 写；customers 由 web 的客户页直接写，没有归属模块；reconcile_log 由 scripts 写
- SMTP：scripts/daily_digest.py 直连，凭据在 config.py 明文
- 无消息队列、无缓存、无第三方 API

## 形态与依赖方向

| 项 | 现状 | 重评条件 |
| --- | --- | --- |
| 形态 | 简单单体 + cron。直接分层不彻底：billing 有 service 层，其余模块直接写 SQL | 出现第二个写入者或独立发布需求时 |
| 依赖方向 | web → billing、reports；reports → billing 的表；scripts → billing 的表 | 见结构偏离 |
| 数据所有权 | invoices/payments 归 billing；customers 没有归属 | 审阅后决定 |

## 结构偏离

| 事实 | 违反的规则 | 影响的入口 | 状态 |
| --- | --- | --- | --- |
| reports/export.py:88 和 scripts/nightly_reconcile.py:40 直接读写 billing 的表 | 05 依赖规则：模块之间只通过公开用例通信，不直接读取彼此的表 | A-06、A-08 | 未授权；用户审阅结论圈定，A-10 之后处理，见 docs/requirements.md#审阅结论 |
| config.py 明文 SMTP 凭据 | 06：秘密不入库 | A-09 | 未授权；A-09 不要了之后随脚本一起删，另立 A-ID |
| tests/conftest.py 用 InMemoryLedger 替换 billing.service，web 的 9 条测试只走替身 | 08：不创建只在测试中存在的替代实现 | A-01 到 A-04 | 未授权；基线用真实调用补了 web 三条的证据，测试本身留在队列 |
