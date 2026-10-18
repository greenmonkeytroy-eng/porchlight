from app.clients.provisions import ProvisionItem, ProvisionsClient
from app.metrics.provisions_metrics import calculate_provisions_metrics


def test_mock_inventory_valuation_and_reorder_alerts():
    metrics = calculate_provisions_metrics(ProvisionsClient._mock_inventory())

    assert metrics.total_items_tracked == 6
    assert metrics.total_inventory_valuation_usd == 140.2
    assert metrics.reorder_alerts_count == 2
    assert {a.name for a in metrics.items_needing_reorder} == {
        "Recycled Paper Towels (12 Rolls)",
        "MERV-13 HVAC Air Filter (2-pack)",
    }


def test_food_specific_metrics():
    metrics = calculate_provisions_metrics(ProvisionsClient._mock_inventory())

    food = metrics.food_specific_metrics
    assert food.food_valuation_usd == 19.0
    assert food.total_calories_kcal == 13800.0
    assert food.cost_per_2000_kcal_usd == 2.75
    assert "Organic Whole Milk (2L)" in food.expiring_food_items
    assert "Rolled Oats (1kg)" not in food.expiring_food_items


def test_category_breakdown_percentages_sum_to_100():
    metrics = calculate_provisions_metrics(ProvisionsClient._mock_inventory())

    percentages = [c.percentage_of_total_stock for c in metrics.secondary_category_breakdown.values()]
    assert round(sum(percentages), 1) == 100.0
    assert metrics.secondary_category_breakdown["Pet Care"].valuation_usd == 67.5


def test_empty_inventory_does_not_divide_by_zero():
    metrics = calculate_provisions_metrics([])

    assert metrics.total_items_tracked == 0
    assert metrics.total_inventory_valuation_usd == 0.0
    assert metrics.food_specific_metrics.cost_per_2000_kcal_usd == 0.0
    assert metrics.secondary_category_breakdown == {}


def test_reorder_alert_triggers_at_exact_buffer_boundary():
    item = ProvisionItem(
        id="X1", name="Test Item", category="Household & Cleaning", sub_category="Test",
        quantity=1.0, unit_price_usd=10.0, min_buffer_qty=1.0,
    )
    metrics = calculate_provisions_metrics([item])

    assert metrics.reorder_alerts_count == 1
