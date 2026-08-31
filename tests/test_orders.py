from app.tools.orders import OrderLookup


def test_valid_order():
    tool = OrderLookup()

    result = tool.lookup("ORD-1007")

    assert result["found"] is True
    assert result["order_id"] == "ORD-1007"
    assert result["status"] == "shipped"


def test_lowercase_order():
    tool = OrderLookup()

    result = tool.lookup(" ord-1007 ")

    assert result["found"] is True
    assert result["order_id"] == "ORD-1007"


def test_unknown_order():
    tool = OrderLookup()

    result = tool.lookup("ORD-9999")

    assert result["found"] is False
    assert result["reason"] == "order_not_found"


def test_missing_order():
    tool = OrderLookup()

    result = tool.lookup("")

    assert result["found"] is False
    assert result["reason"] == "missing_order_id"


def test_malformed_order():
    tool = OrderLookup()

    result = tool.lookup("HELLO")

    assert result["found"] is False
    assert result["reason"] == "malformed_order_id"


def test_private_data_not_exposed():
    tool = OrderLookup()

    result = tool.lookup("ORD-1007")

    serialized = str(result).lower()

    assert "email" not in serialized
    assert "address" not in serialized
    assert "risk" not in serialized
    assert "internal" not in serialized
    