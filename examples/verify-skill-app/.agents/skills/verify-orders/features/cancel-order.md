# Cancel order

Cancel order transitions an `open` order to `cancelled` and keeps repeated cancel calls idempotent.

## Sub-features

- `cancel-open` moves an `open` order to `cancelled` with `changed: true`.
- `cancel-replay` leaves a `cancelled` order unchanged with `changed: false`.

## How to get to it (user POV)

- Run `python -X utf8 -m src.orders --db <store> cancel --id <order_id>`.
- Confirm persisted state with `python -X utf8 -m src.orders --db <store> show --id <order_id>`.

## Driving it with control_orders.py

Preconditions:

- `python -X utf8 tools/control_orders.py doctor` exits `0`.

- **Cancel and verify.** Run `python -X utf8 tools/control_orders.py cancel`. It seeds `ORD-102`, cancels it twice, reads back `status == "cancelled"` via `show`, and writes `artifacts/cancel-order.txt`.

## Gotchas

- Cancelling a nonexistent order ID exits `1`; seed or create an order first.
