from app.services.rates_allocator import EXAMPLE_PROFILE_PATH, load_household_profile


def test_loads_a_custom_profile(tmp_path):
    path = tmp_path / "household.json"
    path.write_text(
        '{"total_monthly_spend": 1000, "utility_variable_spend": 50, "kwh_consumed": 200,'
        ' "occupants": [{"id": "X", "name": "Solo", "direct_spending": 10, "submetered_utility": 5}]}'
    )

    profile = load_household_profile(path)

    assert profile.total_monthly_spend == 1000
    assert [o.name for o in profile.occupants] == ["Solo"]


def test_missing_profile_falls_back_to_committed_example(tmp_path):
    profile = load_household_profile(tmp_path / "does-not-exist.json")

    assert EXAMPLE_PROFILE_PATH.exists()
    assert profile.total_monthly_spend == 2800.00
    assert len(profile.occupants) == 2
