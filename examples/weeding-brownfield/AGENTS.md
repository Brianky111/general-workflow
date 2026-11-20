# weeding-brownfield

- 本仓处于 `L0` 棘轮收敛期：`.guardrails/config.json` 锁定 `escape_hatches.max_allowed: 1`。
- 清掉 `src/legacy/parser.py` 的旧解析绕过后，同步把 `max_allowed` 降至 `0` 再升级到 `L2`。
