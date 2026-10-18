from app.clients.firefly import FireflyClient
from app.metrics.property_metrics import Occupant, calculate_occupant_settlement, calculate_pfor

FIXED_COSTS = FireflyClient._mock_fixed_costs()


def test_pfor_matches_known_scenario():
    metrics = calculate_pfor(FIXED_COSTS, total_monthly_spend=2800.00)

    assert metrics.total_fixed_house_overhead_usd == 870.0
    assert metrics.pfor_percentage == 31.07


def test_pfor_zero_spend_does_not_divide_by_zero():
    metrics = calculate_pfor(FIXED_COSTS, total_monthly_spend=0.0)

    assert metrics.pfor_percentage == 0.0


def test_occupant_settlement_matches_known_scenario():
    occupants = [
        Occupant(id="OCC_A", name="Occupant A", direct_spending=420.00, submetered_utility=95.00),
        Occupant(id="OCC_B", name="Occupant B", direct_spending=310.00, submetered_utility=85.00),
    ]
    settlements = calculate_occupant_settlement(FIXED_COSTS, occupants)

    assert len(settlements) == 2
    assert settlements[0].fixed_overhead_share == 435.0
    assert settlements[0].total_monthly_due_usd == 950.0
    assert settlements[1].total_monthly_due_usd == 830.0


def test_occupant_settlement_empty_occupants_returns_empty_list():
    assert calculate_occupant_settlement(FIXED_COSTS, []) == []
