import datetime

import httpx
import pytest

from app.clients.influx import InfluxClient, build_line_protocol


def test_build_line_protocol_with_tags_and_fixed_time():
    line = build_line_protocol(
        "power_draw",
        fields={"kw": 1.42},
        tags={"circuit": "main"},
        time=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
    )

    assert line == "power_draw,circuit=main kw=1.42 1767225600000000000"


def test_build_line_protocol_without_tags():
    line = build_line_protocol("water_flow", fields={"lpm": 2.1}, time=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC))

    assert line == "water_flow lpm=2.1 1767225600000000000"


def test_build_line_protocol_requires_at_least_one_field():
    with pytest.raises(ValueError):
        build_line_protocol("power_draw", fields={})


async def test_write_point_raises_when_unreachable():
    client = InfluxClient(base_url="http://127.0.0.1:1")

    with pytest.raises(httpx.HTTPError):
        await client.write_point("power_draw", fields={"kw": 1.0})


async def test_query_flux_raises_when_unreachable():
    client = InfluxClient(base_url="http://127.0.0.1:1")

    with pytest.raises(httpx.HTTPError):
        await client.query_flux('from(bucket:"telemetry") |> range(start: -5m)')


def test_parse_annotated_csv_skips_comment_lines():
    from app.clients.influx import _parse_annotated_csv

    csv_text = "#group,false,false\n#datatype,string,long\n,result,table\n,_result,0\n"
    rows = _parse_annotated_csv(csv_text)

    assert rows == [{"": "", "result": "_result", "table": "0"}]


def test_parse_annotated_csv_empty_input_returns_empty_list():
    from app.clients.influx import _parse_annotated_csv

    assert _parse_annotated_csv("") == []
