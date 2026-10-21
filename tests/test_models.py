"""Tests for the ShipStation API v2 models."""

from datetime import UTC, date, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from shipstation_sdk.models import (
    CarriersList,
    CreatedShipment,
    Label,
    Package,
    Shipment,
    ShipmentRequest,
    ShipmentsList,
    Tag,
    TrackingInfo,
    TrackWebhookEvent,
    Webhook,
    Weight,
)

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


def test_weight_accepts_both_unit_spellings() -> None:
    """The schema says ``unit`` but documented examples say ``units`` — both parse."""
    assert Weight.model_validate({"value": 9.6, "unit": "ounce"}).unit == "ounce"
    assert Weight.model_validate({"value": 9.6, "units": "ounce"}).unit == "ounce"


def test_ship_date_accepts_a_full_timestamp() -> None:
    """Documented examples carry timestamps for ``ship_date``; they truncate to the date."""
    shipment = Shipment.model_validate({"shipment_id": "se-1", "ship_date": "2024-07-25T05:00:00.000Z"})

    assert shipment.ship_date == date(2024, 7, 25)


def test_carriers_list_retains_partial_success_errors() -> None:
    """A 207 partial-success body keeps its ``errors`` alongside the carriers."""
    carriers_list = CarriersList.model_validate(
        {
            "carriers": [{"carrier_id": "se-1", "carrier_code": "ups"}],
            "errors": [{"error": "connection to stamps_com failed"}],
        },
    )

    assert [carrier.carrier_code for carrier in carriers_list.carriers] == ["ups"]
    assert carriers_list.errors == [{"error": "connection to stamps_com failed"}]


def test_a_package_read_back_is_sent_again_as_it_was() -> None:
    """A shipment's package keeps every field it was read with, except ShipStation's own read-only id."""
    package = {
        "shipment_package_id": "se-123456",
        "package_code": "package",
        "weight": {"value": 12.5, "unit": "pound"},
        "dimensions": {"unit": "inch", "length": 16, "width": 12, "height": 10},
        "insured_value": {"currency": "usd", "amount": 0},
        "label_messages": {"reference1": "PO 4500123", "reference2": None, "reference3": None},
        "external_package_id": "CTN12",
    }

    sent = Package.model_validate(package).model_dump(mode="json", exclude_none=True)

    assert sent == {
        "package_code": "package",
        "weight": {"value": 12.5, "unit": "pound"},
        "dimensions": {"unit": "inch", "length": 16.0, "width": 12.0, "height": 10.0},
        "insured_value": {"currency": "usd", "amount": 0.0},
        "label_messages": {"reference1": "PO 4500123"},
        "external_package_id": "CTN12",
    }


def test_a_label_reads_each_packages_tracking_number() -> None:
    """A multi-package label carries one tracking number per package, in shipment order."""
    label = Label.model_validate(
        {
            "label_id": "se-1095",
            "tracking_number": "794630698100",
            "packages": [
                {"package_id": 1, "tracking_number": "794630698100", "external_package_id": "CTN1", "sequence": 1},
                {"package_id": 2, "tracking_number": "794630698177", "external_package_id": "CTN2", "sequence": 2},
            ],
        },
    )

    assert [(package.external_package_id, package.tracking_number) for package in label.packages] == [
        ("CTN1", "794630698100"),
        ("CTN2", "794630698177"),
    ]


def test_an_international_shipment_read_back_sends_its_customs_without_shipstations_ids() -> None:
    """Customs, tax identifiers and package products parse as models, and re-send minus read-only ids."""
    shipment = Shipment.model_validate(
        {
            "shipment_id": "se-1",
            "customs": {
                "contents": "merchandise",
                "non_delivery": "return_to_sender",
                "invoice_additional_details": {"freight_charge": {"currency": "usd", "amount": 12.5}},
                "importer_of_record": {"name": "Importer Ltd", "country_code": "GB"},
                "customs_items": [
                    {"customs_item_id": "se-77", "description": "Robe", "quantity": 2, "value": 40, "sku": "ROBE-L"},
                ],
            },
            "tax_identifiers": [
                {"taxable_entity_type": "shipper", "identifier_type": "eori", "issuing_authority": "GB", "value": "X1"},
            ],
            "packages": [
                {
                    "shipment_package_id": "se-9",
                    "weight": {"value": 2, "unit": "pound"},
                    "products": [{"description": "Robe", "quantity": 2, "value": {"currency": "usd", "amount": 40}}],
                },
            ],
            "batch_ids": ["se-batch"],
        },
    )
    assert shipment.customs is not None
    assert shipment.customs.customs_items is not None
    assert shipment.customs.customs_items[0].customs_item_id == "se-77"
    assert shipment.packages[0].products is not None
    assert shipment.packages[0].products[0].value is not None
    assert shipment.batch_ids == ["se-batch"]

    request = ShipmentRequest(
        customs=shipment.customs,
        tax_identifiers=shipment.tax_identifiers,
        packages=shipment.packages,
    )
    sent = request.model_dump(mode="json", exclude_none=True)

    assert sent["customs"]["customs_items"] == [{"description": "Robe", "quantity": 2, "value": 40.0, "sku": "ROBE-L"}]
    assert sent["customs"]["importer_of_record"] == {"name": "Importer Ltd", "country_code": "GB"}
    assert sent["tax_identifiers"][0]["identifier_type"] == "eori"
    assert "shipment_package_id" not in sent["packages"][0]


def test_a_shipment_request_sends_only_the_fields_it_names() -> None:
    """New request fields stay off the wire until set."""
    request = ShipmentRequest(validate_address="no_validation", tags=[Tag(name="Rush")])

    assert request.model_dump(mode="json", exclude_none=True) == {
        "validate_address": "no_validation",
        "tags": [{"name": "Rush"}],
    }


def test_a_created_shipment_reads_string_errors_and_address_validation() -> None:
    """The create response documents its errors as strings and reports how the address validated."""
    created = CreatedShipment.model_validate(
        {
            "shipment_id": "se-1",
            "errors": ["Parameter value is out of range."],
            "address_validation": {
                "status": "warning",
                "matched_address": {"city_locality": "Dallas"},
                "messages": [{"code": "a1004", "message": "Address not found", "type": "warning"}],
            },
        },
    )

    assert created.errors == ["Parameter value is out of range."]
    assert created.address_validation is not None
    assert created.address_validation.messages[0].code == "a1004"


def test_a_label_reads_its_downloads_refund_and_shipment() -> None:
    """A label carries its download links, refund details and the shipment it was bought for."""
    label = Label.model_validate(
        {
            "label_id": "se-1095",
            "label_download": {"href": "https://x.test/l.pdf", "pdf": "https://x.test/l.pdf"},
            "refund_details": {"refund_status": "approved", "amount_credited": {"currency": "usd", "amount": 8.5}},
            "shipment": {"shipment_id": "se-1", "external_shipment_id": "AS-1"},
            "packages": [{"package_id": 1, "alternative_identifiers": [{"type": "last_mile", "value": "92"}]}],
        },
    )

    assert label.label_download is not None
    assert label.label_download.pdf == "https://x.test/l.pdf"
    assert label.refund_details is not None
    assert label.refund_details.amount_credited is not None
    assert label.shipment is not None
    assert label.shipment.external_shipment_id == "AS-1"
    assert label.packages[0].alternative_identifiers is not None
    assert label.packages[0].alternative_identifiers[0].value == "92"


def test_a_carrier_reads_its_services_and_package_types() -> None:
    """A connected carrier lists the services and package types it offers."""
    carriers_list = CarriersList.model_validate(
        {
            "carriers": [
                {
                    "carrier_id": "se-1",
                    "carrier_code": "ups",
                    "services": [{"service_code": "ups_ground", "domestic": True}],
                    "packages": [
                        {"package_code": "ups_10_kg_box", "dimensions": {"length": 1, "width": 1, "height": 1}},
                    ],
                },
            ],
            "request_id": "aa3d8e8e-462b-4476-9618-72db7f7b7009",
        },
    )

    carrier = carriers_list.carriers[0]
    assert [service.service_code for service in carrier.services] == ["ups_ground"]
    assert carrier.packages[0].dimensions is not None


def test_a_webhook_reads_the_integer_store_id_the_schema_documents() -> None:
    """The webhook schema's ``store_id`` is an integer, not an ``se-`` string."""
    webhook = Webhook.model_validate(
        {"webhook_id": "se-1", "url": "https://x.test/hook", "event": "label_created_v2", "store_id": 123456},
    )

    assert webhook.store_id == 123456


# Shaped like ShipStation's documented track webhook payload, with invented values.
TRACK_WEBHOOK_JSON: dict[str, Any] = {
    "resource_url": "https://api.shipstation.com/v2/labels/se-1234/track",
    "resource_type": "API_TRACK",
    "data": {
        "tracking_number": "1ZTEST0000000002",
        "tracking_url": "https://carrier.example/track?n=1ZTEST0000000002",
        "status_code": "DE",
        "status_detail_code": "DELIVERED",
        "status_detail_description": "Your shipment has been delivered.",
        "carrier_code": "ups",
        "carrier_id": 3,
        "carrier_detail_code": "D",
        "status_description": "Delivered",
        "carrier_status_code": "D",
        "carrier_status_description": "Delivered",
        "ship_date": "2026-10-18T00:00:00Z",
        "estimated_delivery_date": "2026-10-21T00:00:00",
        "actual_delivery_date": "2026-10-20T17:05:00Z",
        "exception_description": None,
        "events": [
            {
                "occurred_at": "2026-10-20T17:05:00Z",
                "carrier_occurred_at": "2026-10-20T12:05:00",
                "description": "Delivered",
                "city_locality": "Testville",
                "state_province": "TX",
                "postal_code": "00000",
                "country_code": "US",
                "company_name": None,
                "signer": "FRONT DOOR",
                "event_code": "KB",
                "carrier_detail_code": "D",
                "status_code": "DE",
                "status_detail_code": "DELIVERED",
                "status_detail_description": "Your shipment has been delivered.",
                "status_description": "Delivered",
                "carrier_status_code": "D",
                "carrier_status_description": "Delivered",
                "proof_of_delivery_url": None,
                "latitude": 30.5,
                "longitude": -97.5,
            },
        ],
    },
}


def test_a_track_webhook_reads_the_packages_tracking_info() -> None:
    """A ``track`` webhook body carries the tracking info as the tracking endpoint returns it."""
    event = TrackWebhookEvent.model_validate(TRACK_WEBHOOK_JSON)

    assert event.resource_type == "API_TRACK"
    assert event.data.status_code == "DE"
    assert event.data.carrier_id == 3
    assert event.data.actual_delivery_date == datetime(2026, 10, 20, 17, 5, tzinfo=UTC)
    assert event.data.estimated_delivery_date == datetime(2026, 10, 21)  # noqa: DTZ001 -- documented without an offset
    track_event = event.data.events[0]
    assert track_event.signer == "FRONT DOOR"
    assert track_event.status_detail_code == "DELIVERED"
    assert (track_event.latitude, track_event.longitude) == (30.5, -97.5)


def test_a_track_event_v2_webhook_parses_too() -> None:
    """The ``track_event_v2`` webhook names its own resource type around the same tracking info."""
    event = TrackWebhookEvent.model_validate({**TRACK_WEBHOOK_JSON, "resource_type": "TRACK_EVENT_V2"})

    assert event.data.tracking_number == "1ZTEST0000000002"


def test_a_track_webhook_refuses_another_events_body() -> None:
    """A label webhook's body is not mistaken for a tracking one."""
    with pytest.raises(ValidationError):
        TrackWebhookEvent.model_validate({**TRACK_WEBHOOK_JSON, "resource_type": "LABEL_CREATED_V2"})


def test_tracking_info_refuses_an_undocumented_status_code() -> None:
    """The high-level status is one of the eight codes ShipStation documents."""
    with pytest.raises(ValidationError):
        TrackingInfo.model_validate({"tracking_number": "1ZTEST0000000003", "status_code": "ZZ"})
