from app.clients.firefly import FireflyClient
from app.metrics.energy_metrics import calculate_eur

FIXED_COSTS = FireflyClient._mock_fixed_costs()


def test_eur_matches_known_scenario():
    metrics = calculate_eur(FIXED_COSTS, utility_variable_spend=180.00, kwh_consumed=600.0)

    assert metrics.effective_utility_rate_per_kwh == 0.375


def test_eur_zero_consumption_does_not_divide_by_zero():
    metrics = calculate_eur(FIXED_COSTS, utility_variable_spend=180.00, kwh_consumed=0.0)

    assert metrics.effective_utility_rate_per_kwh == 0.0
