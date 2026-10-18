import datetime
import json

from app.services.drais_logger import DecisionRecord, emit_decision_record


def test_emit_decision_record_writes_valid_schema(tmp_path):
    record = DecisionRecord(
        component="test",
        action_type="UNIT_TEST_ACTION",
        decision_logic="DETERMINISTIC_TEST_LOGIC",
        inputs={"a": 1},
        output={"b": 2},
    )

    path = emit_decision_record(record, log_dir=str(tmp_path))

    assert path.exists()
    today = datetime.date.today().strftime("%Y%m%d")
    assert path.name == f"dr_ais_test_{today}.json"

    data = json.loads(path.read_text())
    assert data["system"] == "Porchlight OS"
    assert data["drais_version"] == "1.0"
    assert data["action_type"] == "UNIT_TEST_ACTION"
    assert data["decision_logic"] == "DETERMINISTIC_TEST_LOGIC"
    assert data["inputs"] == {"a": 1}
    assert data["output"] == {"b": 2}
    assert data["human_override_available"] is True
    assert data["privacy_scope"] == "LOCAL_NETWORK_ONLY"
    # Must be a real, parseable ISO-8601 UTC timestamp.
    datetime.datetime.fromisoformat(data["timestamp"])


def test_human_override_available_can_be_overridden(tmp_path):
    record = DecisionRecord(
        component="test",
        action_type="UNIT_TEST_ACTION",
        decision_logic="DETERMINISTIC_TEST_LOGIC",
        inputs={},
        output={},
        human_override_available=False,
    )

    path = emit_decision_record(record, log_dir=str(tmp_path))
    data = json.loads(path.read_text())

    assert data["human_override_available"] is False
