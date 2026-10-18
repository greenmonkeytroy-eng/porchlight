from app.clients.homeassistant import HomeAssistantClient


def test_mock_states_shape():
    states = HomeAssistantClient._mock_states()

    assert len(states) == 3
    ids = {s.entity_id for s in states}
    assert "sensor.porchlight_power_draw" in ids


async def test_fetch_states_falls_back_to_mock_when_unreachable():
    client = HomeAssistantClient(base_url="http://127.0.0.1:1")

    states = await client.fetch_states()

    assert states == HomeAssistantClient._mock_states()


async def test_get_state_falls_back_to_matching_mock_entity():
    client = HomeAssistantClient(base_url="http://127.0.0.1:1")

    state = await client.get_state("sensor.porchlight_power_draw")

    assert state is not None
    assert state.state == "1.42"


async def test_get_state_returns_none_for_unknown_entity_when_unreachable():
    client = HomeAssistantClient(base_url="http://127.0.0.1:1")

    state = await client.get_state("sensor.does_not_exist")

    assert state is None
