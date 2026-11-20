# clean-app

- 用户功能与入口清单见 `.guardrails/feature-map.md`；验证产物见 `.guardrails/verification.md`。
- 本文件只保留工具无法表达的业务约定：订单金额统一用整分（`amount_cents`）表示，不做浮点舍入。
- 目录边界、`time.sleep` 白名单与逃生舱禁令由 `.guardrails/config.json` 强制检查，不在此重复。
