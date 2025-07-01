"""Test for datetime serialization in ShipStation SDK models."""

from datetime import datetime

from pydantic import BaseModel, Field

from shipstation_sdk.models import LA_TIMEZONE, ShipStationDateTime


class Example(BaseModel):
    """Test model to validate datetime serialization."""

    order_date: ShipStationDateTime = Field(..., alias="orderDate")


def test_datetime_serialization() -> None:
    """Test the serialization of datetime fields."""
    test_instance = Example.model_validate({"orderDate": "2025-06-05T12:52:00.0000000"})

    serialized = test_instance.model_dump(by_alias=True)
    assert serialized["orderDate"] == "2025-06-05T12:52:00.0000000"

    deserialized = Example.model_validate(serialized)
    assert deserialized.order_date == datetime(2025, 6, 5, 12, 52, 0, tzinfo=LA_TIMEZONE)
