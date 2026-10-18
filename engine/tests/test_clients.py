from app.clients.firefly import FireflyClient
from app.clients.provisions import ProvisionsClient


async def test_firefly_client_returns_mock_fixed_costs():
    costs = await FireflyClient().fetch_monthly_fixed_costs()

    assert costs.council_rates_monthly == 220.00
    assert costs.total == 870.0


def test_provisions_mock_inventory_shape():
    inventory = ProvisionsClient._mock_inventory()

    assert len(inventory) == 6
    assert inventory[0].id == "PROV_FOOD_1"
    assert {item.category for item in inventory} == {
        "Food & Nutrition",
        "Household & Cleaning",
        "Pet Care",
        "Building & Maintenance",
    }


async def test_provisions_client_falls_back_to_mock_when_unreachable():
    client = ProvisionsClient(base_url="http://127.0.0.1:1")

    inventory = await client.fetch_provisions_inventory()

    assert len(inventory) == 6
    assert inventory == ProvisionsClient._mock_inventory()
