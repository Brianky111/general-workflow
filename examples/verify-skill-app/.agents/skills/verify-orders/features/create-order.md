# Create order

Create order persists a new order in `open` state from the CLI and ignores identical retries idempotently.

## Sub-features

- `create-fresh` creates a new order in `open` status with `created: true`.
- `create-replay` returns the existing record with `created: false` when retried with the same item.

## How to get to it (user POV)

- Run `python -X utf8 -m src.orders --db <store> create --id <order_id> --item <item>`.
- Confirm persisted state with `python -X utf8 -m src.orders --db <store> show --id <order_id>`.

## Driving it with control_orders.py

Preconditions:

- `python -X utf8 tools/control_orders.py doctor` exits `0`.

- **Create and replay.** Run `python -X utf8 tools/control_orders.py create`. It creates `ORD-101`, replays the same command, verifies via `show`, and writes `artifacts/create-order.txt`.

## Gotchas

- Creating an existing order ID with a different `--item` exits `1` rather than overwriting the stored item.
