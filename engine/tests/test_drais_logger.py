import datetime
import json

from app.services.drais_logger import DecisionRecord, emit_decision_record


def _record(**overrides):
    return DecisionRecord(
        component="test",
        action_type="UNIT_TEST_ACTION",
        decision_logic="DETERMINISTIC_TEST_LOGIC",
        inputs=overrides.pop("inputs", {"a": 1}),
        output={"b": 2},
        **overrides,
    )


def test_emit_decision_record_writes_valid_schema(tmp_path):
    path = emit_decision_record(_record(), log_dir=str(tmp_path))

    assert path.exists()
    assert path.name.startswith("dr_ais_test_") and path.suffix == ".json"

    data = json.loads(path.read_text())
    assert data["system"] == "Porchlight OS"
    assert data["drais_version"] == "1.0"
    assert data["action_type"] == "UNIT_TEST_ACTION"
    assert data["decision_logic"] == "DETERMINISTIC_TEST_LOGIC"
    assert data["inputs"] == {"a": 1}
    assert data["output"] == {"b": 2}
    assert data["human_override_available"] is True
    assert data["privacy_scope"] == "LOCAL_NETWORK_ONLY"
    assert datetime.datetime.fromisoformat(data["timestamp"]).tzinfo is not None


def test_records_are_immutable_and_never_overwritten(tmp_path):
    first = emit_decision_record(_record(inputs={"run": 1}), log_dir=str(tmp_path))
    second = emit_decision_record(_record(inputs={"run": 2}), log_dir=str(tmp_path))

    assert first != second
    assert len(list(tmp_path.iterdir())) == 2
    assert json.loads(first.read_text())["inputs"] == {"run": 1}


def test_human_override_available_can_be_overridden(tmp_path):
    path = emit_decision_record(_record(human_override_available=False), log_dir=str(tmp_path))

    assert json.loads(path.read_text())["human_override_available"] is False
