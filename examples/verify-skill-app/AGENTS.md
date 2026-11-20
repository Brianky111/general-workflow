# verify-skill-app

| Rule | Enforcer |
| --- | --- |
| Order status transitions stay inside `OrderStore` | `src/orders.py` domain methods + `tests/test_orders.py` |
| Every user flow keeps a sharded feature map and live proof | `.agents/skills/verify-orders/` + `repo_guard.py` |
| Zero lint suppressions or workaround comments | `.guardrails/config.json` (`escape_hatches.max_allowed: 0`) |
