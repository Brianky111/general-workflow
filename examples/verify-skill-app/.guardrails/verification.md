# Verification

| Feature | Command | Observed | Artifact | Commit |
| --- | --- | --- | --- | --- |
| Create order | `python -X utf8 tools/control_orders.py create` | 首次创建 `created=true` 且重放 `created=false`，`show` 返回 `open` | `artifacts/create-order.txt` | b2c3d4e |
| Cancel order | `python -X utf8 tools/control_orders.py cancel` | 首次取消 `changed=true` 且重放 `changed=false`，`show` 返回 `cancelled` | `artifacts/cancel-order.txt` | b2c3d4e |
