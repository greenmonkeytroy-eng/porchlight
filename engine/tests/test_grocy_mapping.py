import httpx

from app.clients.provisions import ProvisionsClient, map_grocy_stock

GROUPS = [{"id": 1, "name": "Food & Nutrition"}, {"id": 2, "name": "Pet Care"}]
STOCK = [
    {
        "product_id": 5, "amount": "2", "value": "7.0", "best_before_date": "2026-10-20",
        "product": {"id": 5, "name": "Milk", "product_group_id": 1, "min_stock_amount": "1", "calories": "1200"},
    },
    {
        "product_id": 9, "amount": 1.5, "value": 67.5, "best_before_date": "2999-12-31",
        "product": {"id": 9, "name": "Kibble", "product_group_id": 2, "min_stock_amount": 0.5, "calories": None},
    },
    {
        "product_id": 11, "amount": 0, "value": 0, "best_before_date": None,
        "product": {"id": 11, "name": "Mystery", "product_group_id": None},
    },
]


def test_maps_grocy_stock_rows_to_provision_items():
    milk, kibble, mystery = map_grocy_stock(STOCK, GROUPS)

    assert (milk.id, milk.name, milk.category) == ("GROCY_5", "Milk", "Food & Nutrition")
    assert (milk.quantity, milk.unit_price_usd, milk.min_buffer_qty, milk.calories_per_unit) == (2.0, 3.5, 1.0, 1200.0)
    assert milk.best_before == "2026-10-20"

    assert kibble.category == "Pet Care"
    assert kibble.best_before is None, "Grocy's 2999-12-31 means 'never expires'"
    assert kibble.calories_per_unit is None

    assert mystery.category == "Uncategorized"
    assert mystery.unit_price_usd == 0.0, "zero stock must not divide by zero"


async def test_fetch_uses_live_grocy_data_when_available(monkeypatch):
    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient",
        lambda **kw: real_client(transport=httpx.MockTransport(
            lambda req: httpx.Response(200, json={"/api/stock": STOCK, "/api/objects/product_groups": GROUPS}[req.url.path])
        ), **kw),
    )

    items = await ProvisionsClient(base_url="http://grocy.test").fetch_provisions_inventory()

    assert [i.name for i in items] == ["Milk", "Kibble", "Mystery"]


async def test_unexpected_grocy_shape_falls_back_to_mock_instead_of_crashing(monkeypatch):
    real_client = httpx.AsyncClient
    bad_rows = [{"id": "1", "product_id": "5", "amount": "2"}]  # raw /objects/stock shape, no "product"
    monkeypatch.setattr(
        httpx, "AsyncClient",
        lambda **kw: real_client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=bad_rows)), **kw),
    )

    items = await ProvisionsClient(base_url="http://grocy.test").fetch_provisions_inventory()

    assert items == ProvisionsClient._mock_inventory()
