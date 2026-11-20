---
name: verify-orders
description: "Project-local verification skill for the Orders CLI (create, cancel, and idempotent persistence checks)."
---

# Verify Orders

Drive the real `src.orders` CLI through `tools/control_orders.py` using isolated temporary stores and record behavioral artifacts under `artifacts/`.

## Launch

This is a short-lived Python CLI with no background daemon. Each verification drive runs in an isolated temporary directory via `python -X utf8 tools/control_orders.py <subcommand>` from the project root.

## Doctor

Run the read-only health check before driving any feature:

```powershell
python -X utf8 tools/control_orders.py doctor
```

Expect exit code `0` and `doctor: OK python+orders CLI ready`.

## Drive

Select the feature file under `features/` matching the change, then drive it via `tools/control_orders.py create`, `tools/control_orders.py cancel`, or `tools/control_orders.py all`.

## Evidence

Every verification run must exercise the real `src.orders` CLI, verify the persisted state via a read-only `show` call, and retain non-empty proof logs in `artifacts/create-order.txt` and `artifacts/cancel-order.txt`.

## Cleanup

Temporary `orders.json` stores created via `tempfile.TemporaryDirectory` are automatically removed when each drive finishes; proof artifacts under `artifacts/` are never deleted during cleanup.

## Helpers

`tools/control_orders.py` accepts `doctor`, `create`, `cancel`, or `all` (default).
