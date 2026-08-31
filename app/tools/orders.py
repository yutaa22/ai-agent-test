
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
        """Normalize harmless whitespace, case, and punctuation."""

        if not isinstance(order_id, str):
            return ""

        value = order_id.strip().upper()

        value = re.sub(
            r"^[\s.,:;#]+|[\s.,:;]+$",
            "",
            value,
        )

        return value

    @staticmethod
    def is_valid_format(order_id: str) -> bool:
        """Validate the expected ORD-1234 format."""

        return bool(
            re.fullmatch(
                r"ORD-\d{4}",
                order_id,
            )
        )

    def lookup(self, order_id: str) -> dict:
        """
        Look up an order and return only customer-safe fields.
        """

        normalized = self.normalize_order_id(order_id)

        # Missing order ID.
        if not normalized:
            return {
                "found": False,
                "reason": "missing_order_id",
            }

        # Invalid order ID format.
        if not self.is_valid_format(normalized):
            return {
                "found": False,
                "reason": "malformed_order_id",
                "order_id": normalized,
            }

        order = self.orders.get(normalized)

        # Valid format but no matching order.
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

        # Only expose explicitly customer-safe fields.
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

        # Return only safe item information.
        if "items" in order:
            result["items"] = [
                {
                    key: item.get(key)
                    for key in [
                        "name",
                        "quantity",
                        "final_sale",
                    ]
                    if key in item
                }
                for item in order["items"]
            ]

        status = order.get("status")

        # Cancelled/returned orders must not expose stale
        # shipping information.
        if status in {"cancelled", "returned"}:
            result.pop("estimated_delivery", None)
            result.pop("carrier", None)
            result.pop("tracking_number", None)

        # Shipped orders without an ETA should explicitly indicate
        # that the estimate is unavailable.
        if (
            status == "shipped"
            and not order.get("estimated_delivery")
        ):
            result["delivery_note"] = (
                "Delivery estimate is unavailable."
            )

        # Delivery exceptions require human review.
        if status == "exception":
            result["handoff"] = True
            result["delivery_note"] = (
                "Support review is required."
            )

        return result

