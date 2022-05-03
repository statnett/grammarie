from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pendulum import UTC, DateTime
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError

from grammarie.types import (
    Decimal1,
    Decimal2,
    FloatTimestampMS,
    FloatTimestampS,
    IntTimestampMS,
    IntTimestampS,
    LowercaseStr,
    StrTimestampISO,
    TimeZone,
    TimeZoneString,
    UppercaseStr,
    WholeNumberDecimal,
)


@pytest.fixture
def string_inputs():
    return [
        "UPPERCASE",
        "lowercase",
        "MiXeDcAsE",
    ]


@pytest.fixture
def datetime_inputs():
    return [
        DateTime(2022, 5, 3, 11, 15, 1, tzinfo=UTC),
        datetime(2022, 5, 3, 11, 15, 1, tzinfo=timezone.utc),
        "2022-05-03T11:15:01Z",
        "2022-05-03 11:15:01Z",
        1651576501,
        1651576501.0,
        1651576501000,
        1651576501000.0,
    ]


def test_WholeNumberDecimal():
    type_adapter = TypeAdapter(WholeNumberDecimal)

    assert type_adapter.validate_python("1") == Decimal("1.0")
    assert type_adapter.validate_python("1.0001") == Decimal("1.0")
    assert type_adapter.validate_python(1) == Decimal("1.0")
    assert type_adapter.validate_python(1.0) == Decimal("1.0")
    assert type_adapter.validate_python(Decimal("1.0")) == Decimal("1.0")
    assert type_adapter.validate_python(1.0001) == Decimal("1.0")
    assert type_adapter.validate_python(Decimal("1.0001")) == Decimal("1.0")
    assert type_adapter.validate_python(0.9) == Decimal("1.0")
    assert type_adapter.validate_python(1.1) == Decimal("1.0")


def test_Decimal1():
    type_adapter = TypeAdapter(Decimal1)

    assert type_adapter.validate_python("1") == Decimal("1.0")
    assert type_adapter.validate_python("1.0001") == Decimal("1.0")
    assert type_adapter.validate_python(1) == Decimal("1.0")
    assert type_adapter.validate_python(1.0) == Decimal("1.0")
    assert type_adapter.validate_python(Decimal("1.0")) == Decimal("1.0")
    assert type_adapter.validate_python(1.0001) == Decimal("1.0")
    assert type_adapter.validate_python(Decimal("1.0001")) == Decimal("1.0")
    assert type_adapter.validate_python(0.9) == Decimal("0.9")
    assert type_adapter.validate_python(1.1) == Decimal("1.1")


def test_Decimal2():
    type_adapter = TypeAdapter(Decimal2)

    assert type_adapter.validate_python("1") == Decimal("1.00")
    assert type_adapter.validate_python("1.0001") == Decimal("1.00")
    assert type_adapter.validate_python(1) == Decimal("1.00")
    assert type_adapter.validate_python(1.0) == Decimal("1.00")
    assert type_adapter.validate_python(Decimal("1.0")) == Decimal("1.00")
    assert type_adapter.validate_python(1.0001) == Decimal("1.00")
    assert type_adapter.validate_python(Decimal("1.0001")) == Decimal("1.00")
    assert type_adapter.validate_python(0.9) == Decimal("0.90")
    assert type_adapter.validate_python(1.1) == Decimal("1.10")
    assert type_adapter.validate_python(1.12) == Decimal("1.12")


def test_LowercaseStr(string_inputs):
    type_adapter = TypeAdapter(LowercaseStr)

    for s in string_inputs:
        assert type_adapter.validate_python(s) == s.lower()


def test_UpperCaseStr(string_inputs):
    type_adapter = TypeAdapter(UppercaseStr)

    for s in string_inputs:
        assert type_adapter.validate_python(s) == s.upper()


def test_IntTimestampS(datetime_inputs):
    type_adapter = TypeAdapter(IntTimestampS)

    for ts in datetime_inputs:
        assert type_adapter.validate_python(ts) == 1651576501


def test_IntTimestampMS(datetime_inputs):
    type_adapter = TypeAdapter(IntTimestampMS)

    for ts in datetime_inputs:
        assert type_adapter.validate_python(ts) == 1651576501000


def test_FloatTimestampS(datetime_inputs):
    type_adapter = TypeAdapter(FloatTimestampS)

    for ts in datetime_inputs:
        assert type_adapter.validate_python(ts) == pytest.approx(1651576501.0)


def test_FloatTimestampS_default_is_validated(datetime_inputs):
    class Model(BaseModel):
        ts: FloatTimestampS = datetime_inputs[0]

    assert Model().ts == pytest.approx(1651576501.0)


def test_FloatTimestampMS(datetime_inputs):
    type_adapter = TypeAdapter(FloatTimestampMS)

    for ts in datetime_inputs:
        assert type_adapter.validate_python(ts) == pytest.approx(1651576501000.0)


def test_StrTimestampISO(datetime_inputs):
    type_adapter = TypeAdapter(StrTimestampISO)

    for ts in (dt for dt in datetime_inputs if isinstance(dt, str)):
        assert type_adapter.validate_python(ts) == "2022-05-03 11:15:01+00:00"


def test_StrTimestampISO_non_string(datetime_inputs):
    type_adapter = TypeAdapter(StrTimestampISO)

    for ts in (dt for dt in datetime_inputs if not isinstance(dt, str)):
        with pytest.raises(ValidationError):
            type_adapter.validate_python(ts)


def test_TimeZone():
    class Model(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        tz: TimeZone

    assert Model(tz="Europe/Oslo").tz == ZoneInfo("Europe/Oslo")
    assert Model(tz="UTC").tz == ZoneInfo("UTC")
    with pytest.raises(ValueError):
        Model(tz="foo")


def test_TimeZoneString():
    type_adapter = TypeAdapter(TimeZoneString)

    assert type_adapter.validate_python("Europe/Oslo") == "Europe/Oslo"
    assert type_adapter.validate_python("UTC") == "UTC"
    with pytest.raises(ValueError):
        type_adapter.validate_python("foo")
