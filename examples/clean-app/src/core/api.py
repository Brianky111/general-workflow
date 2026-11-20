"""Safe public API enforcing idempotent order export transitions."""

from src.core.storage import OrderRecord, OrderStore


class OrderService:
    def __init__(self, store: OrderStore | None = None) -> None:
        self._store = store or OrderStore()
        self._exported_batches: dict[str, str] = {}

    def export_csv(self, batch_key: str) -> tuple[str, int]:
        if batch_key in self._exported_batches:
            return self._exported_batches[batch_key], 0
        lines = ["order_id,amount_cents,status"]
        changed = 0
        for row in self._store.list_rows():
            updated = self._transition_to_exported(row)
            changed += 1
            lines.append(f"{updated.order_id},{updated.amount_cents},{updated.status}")
        payload = "\n".join(lines)
        self._exported_batches[batch_key] = payload
        return payload, changed

    def summary(self) -> dict[str, int]:
        rows = self._store.list_rows()
        exported = sum(1 for row in rows if row.status == "exported")
        return {"total": len(rows), "exported": exported}

    def _transition_to_exported(self, row: OrderRecord) -> OrderRecord:
        if row.status == "exported":
            return row
        return self._store.mark_exported(row.order_id)
