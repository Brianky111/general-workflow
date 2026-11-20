"""Internal storage layer; UI modules must never import this module directly."""

from dataclasses import dataclass


@dataclass
class OrderRecord:
    order_id: str
    amount_cents: int
    status: str = "draft"


class OrderStore:
    def __init__(self) -> None:
        self._rows: dict[str, OrderRecord] = {
            "ord-101": OrderRecord("ord-101", 2500),
            "ord-102": OrderRecord("ord-102", 4200),
        }

    def list_rows(self) -> list[OrderRecord]:
        return list(self._rows.values())

    def mark_exported(self, order_id: str) -> OrderRecord:
        row = self._rows[order_id]
        row.status = "exported"
        return row
