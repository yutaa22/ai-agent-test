import json
import re
from pathlib import Path


class OrderLookup:
    """Safe customer-facing order lookup."""

    SAFE_FIELDS = {
        "order_id",
        "membership_tier",
        "items",
        "placed_at",
        "status",
        "status_updated_at",
        "shipped_at",
        "delivered_at",
        "carrier",
        "tracking_number",
        "estimated_delivery",
        "customer_safe_message",
    }

    def __init__(self, path="data/orders.json"):
        self.path = Path(path)

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.orders = data.get("orders", data)

        if isinstance(self.orders, list):
            self.orders = {
                order["order_id"]: order
                for order in self.orders
                if "order_id" in order
            }

    @staticmethod
    def normalize_order_id(order_id: str) -> str:
        if not isinstance(order_id, str):
            return ""

        value = order_id.strip().upper()

        # Remove harmless surrounding punctuation.
        value = re.sub(r"^[\s.,:;#]+|[\s.,:;]+$", "", value)

        return value

    @staticmethod
    def is_valid_format(order_id: str) -> bool:
        return bool(re.fullmatch(r"ORD-\d{4}", order_id))

    def lookup(self, order_id: str) -> dict:
        normalized = self.normalize_order_id(order_id)

        if not normalized:
            return {
                "found": False,
                "reason": "missing_order_id",
            }

        if not self.is_valid_format(normalized):
            return {
                "found": False,
                "reason": "malformed_order_id",
                "order_id": normalized,
            }

        order = self.orders.get(normalized)

        if not order:
            return {
                "found": False,
                "reason": "order_not_found",
                "order_id": normalized,
            }

        result = {
            "found": True,
            "order_id": normalized,
        }

        # Minimum necessary customer-safe information.
        for field in [
            "membership_tier",
            "placed_at",
            "status",
            "status_updated_at",
            "shipped_at",
            "delivered_at",
            "carrier",
            "tracking_number",
            "estimated_delivery",
            "customer_safe_message",
        ]:
            if field in order:
                result[field] = order[field]

        if "items" in order:
            result["items"] = [
                {
                    key: item.get(key)
                    for key in ["name", "quantity", "final_sale"]
                    if key in item
                }
                for item in order["items"]
            ]

        # Status is authoritative.
        if order.get("status") in {"cancelled", "returned"}:
            result.pop("estimated_delivery", None)
            result.pop("carrier", None)
            result.pop("tracking_number", None)

        if (
            order.get("status") == "shipped"
            and not order.get("estimated_delivery")
        ):
            result["delivery_note"] = "Delivery estimate is unavailable."

        if order.get("status") == "exception":
            result["handoff"] = True
            result["delivery_note"] = "Support review is required."

        return result