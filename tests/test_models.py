"""Tests for the ShipStation API v2 models."""

from datetime import UTC, datetime
from typing import Any

from shipstation_sdk.models import Shipment, ShipmentsList

# A realistic v2 shipment, hand-built from the published OpenAPI schema.
SHIPMENT_JSON: dict[str, Any] = {
    "shipment_id": "se-28529731",
    "external_shipment_id": "9f8c6b1e-6a2f-4c1e-a2c8-1c1d2e3f4a5b",
    "shipment_number": "AS-10001",
    "external_order_id": "1234567890",
    "shipment_status": "pending",
    "created_at": "2026-07-01T16:30:00Z",
    "modified_at": "2026-07-01T16:31:00Z",
    "ship_by_date": "2026-07-07T00:00:00Z",
    "store_id": "se-521526",
    "order_source_code": "shopify",
    "carrier_id": "se-123456",
    "service_code": "ups_ground",
    "requested_shipment_service": "UPS Ground",
    "amount_paid": {"currency": "usd", "amount": 45.5},
    "tax_paid": {"currency": "usd", "amount": 3.5},
    "ship_to": {
        "name": "Jane Doe",
        "phone": "555-555-5555",
        "email": "jane@example.com",
        "company_name": "Example Corp",
        "address_line1": "123 Main St",
        "address_line2": "Suite 4",
        "city_locality": "Dallas",
        "state_province": "TX",
        "postal_code": "75001",
        "country_code": "US",
        "address_residential_indicator": "no",
    },
    "items": [
        {
            "name": "Robe - Large",
            "sku": "ROBE-L",
            "upc": "012345678905",
            "quantity": 2,
            "unit_price": 20.0,
            "sales_order_id": "se-987",
            "sales_order_item_id": "se-654",
            "external_order_item_id": "gid://shopify/LineItem/1",
            "options": [
                {"name": "Embroidery Text", "value": "Jane"},
                {"name": "Embroidery Color", "value": "Red"},
            ],
        },
    ],
    "tags": [{"name": "Rush"}],
    "packages": [{"package_code": "package", "weight": {"value": 1.5, "unit": "pound"}}],
    "total_weight": {"value": 1.5, "unit": "pound"},
    "notes_from_buyer": "Please hurry!",
    "is_gift": False,
    "advanced_options": {"custom_field1": "AS-10001", "bill_to_party": "recipient"},
    "confirmation": "none",
    "insurance_provider": "none",
}


def test_shipment_round_trip() -> None:
    """A realistic v2 shipment body validates with the expected field types."""
    shipment = Shipment.model_validate(SHIPMENT_JSON)

    assert shipment.shipment_id == "se-28529731"
    assert shipment.created_at == datetime(2026, 7, 1, 16, 30, tzinfo=UTC)
    assert shipment.store_id == "se-521526"
    assert shipment.amount_paid is not None
    assert shipment.amount_paid.amount == 45.5
    assert shipment.ship_to is not None
    assert shipment.ship_to.city_locality == "Dallas"
    assert shipment.items[0].options[1].value == "Red"
    assert [tag.name for tag in shipment.tags] == ["Rush"]
    assert shipment.advanced_options is not None
    assert shipment.advanced_options.custom_field1 == "AS-10001"


def test_shipments_list_envelope() -> None:
    """The list envelope parses pagination fields and links."""
    shipments_list = ShipmentsList.model_validate(
        {
            "shipments": [SHIPMENT_JSON],
            "total": 1990,
            "page": 1,
            "pages": 20,
            "links": {
                "first": {"href": "https://api.shipstation.com/v2/shipments?page=1"},
                "last": {"href": "https://api.shipstation.com/v2/shipments?page=20"},
                "prev": {},
                "next": {"href": "https://api.shipstation.com/v2/shipments?page=2"},
            },
        },
    )

    assert shipments_list.total == 1990
    assert shipments_list.pages == 20
    assert shipments_list.links is not None
    assert shipments_list.links.next is not None
    assert shipments_list.links.next.href is not None
    assert shipments_list.links.prev is not None
    assert shipments_list.links.prev.href is None


def test_shipment_parses_with_minimal_fields() -> None:
    """Only ``shipment_id`` is required; everything else defaults."""
    shipment = Shipment.model_validate({"shipment_id": "se-1"})

    assert shipment.items == []
    assert shipment.tags == []
    assert shipment.store_id is None
