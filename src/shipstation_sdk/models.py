"""ShipStation API v2 models."""

from datetime import date, datetime
from typing import Annotated, Any

from pydantic import AliasChoices, BaseModel, BeforeValidator, Field


def _date_from_timestamp(value: object) -> object:
    """Accept full ISO timestamps for date fields, truncating to the calendar date.

    ShipStation's schema declares plain dates, but documented response examples carry
    full timestamps (e.g. ``2024-07-25T05:00:00.000Z``), which pydantic would reject
    for a ``date`` field.
    """
    if isinstance(value, str) and "T" in value:
        return datetime.fromisoformat(value).date()
    return value


ShipStationDate = Annotated[date, BeforeValidator(_date_from_timestamp)]


class MonetaryValue(BaseModel):
    """Model for a monetary amount and its currency."""

    currency: str
    amount: float


class Weight(BaseModel):
    """Model for a weight."""

    value: float
    # The schema says ``unit`` but documented response examples say ``units``.
    unit: str = Field(validation_alias=AliasChoices("unit", "units"))


class Tag(BaseModel):
    """Model for a shipment tag."""

    name: str


class ItemOption(BaseModel):
    """Model for a shipment item option."""

    name: str | None = None
    value: str | None = None


class Address(BaseModel):
    """Model for a shipping address."""

    name: str | None = None
    phone: str | None = None
    email: str | None = None
    company_name: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    address_line3: str | None = None
    city_locality: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country_code: str | None = None
    address_residential_indicator: str | None = None
    instructions: str | None = None


class ShipmentItem(BaseModel):
    """Model for a shipment item (an order line)."""

    name: str | None = None
    sku: str | None = None
    bundle_sku: str | None = None
    upc: str | None = None
    asin: str | None = None
    quantity: int = 0
    unit_price: float | None = None
    tax_amount: float | None = None
    shipping_amount: float | None = None
    weight: Weight | None = None
    sales_order_id: str | None = None
    sales_order_item_id: str | None = None
    external_order_id: str | None = None
    external_order_item_id: str | None = None
    item_id: str | None = None
    product_id: str | None = None
    # The double-l spelling is the ShipStation API's, not ours.
    fullfilment_sku: str | None = None
    allocation_status: str | None = None
    inventory_location: str | None = None
    image_url: str | None = None
    order_source_code: str | None = None
    options: list[ItemOption] = []


class AdvancedShipmentOptions(BaseModel):
    """Model for advanced shipment options."""

    custom_field1: str | None = None
    custom_field2: str | None = None
    custom_field3: str | None = None
    bill_to_party: str | None = None
    bill_to_account: str | None = None
    bill_to_postal_code: str | None = None
    bill_to_country_code: str | None = None


class Shipment(BaseModel):
    """Model for a shipment (the v2 equivalent of a v1 order)."""

    shipment_id: str
    external_shipment_id: str | None = None
    shipment_number: str | None = None
    external_order_id: str | None = None
    shipment_status: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    ship_date: ShipStationDate | None = None
    ship_by_date: datetime | None = None
    hold_until_date: datetime | None = None
    deliver_by_date: datetime | None = None
    store_id: str | None = None
    order_source_code: str | None = None
    carrier_id: str | None = None
    service_code: str | None = None
    requested_shipment_service: str | None = None
    comparison_rate_type: str | None = None
    zone: int | None = None
    warehouse_id: str | None = None
    amount_paid: MonetaryValue | None = None
    shipping_paid: MonetaryValue | None = None
    tax_paid: MonetaryValue | None = None
    retail_rate: MonetaryValue | None = None
    ship_to: Address | None = None
    ship_from: Address | None = None
    return_to: Address | None = None
    items: list[ShipmentItem] = []
    tags: list[Tag] = []
    packages: list[dict[str, Any]] = []
    total_weight: Weight | None = None
    notes_from_buyer: str | None = None
    notes_to_buyer: str | None = None
    notes_for_gift: str | None = None
    internal_notes: str | None = None
    is_gift: bool | None = None
    is_return: bool | None = None
    assigned_user: str | None = None
    display_scheme: str | None = None
    confirmation: str | None = None
    insurance_provider: str | None = None
    advanced_options: AdvancedShipmentOptions | None = None
    customs: dict[str, Any] | None = None
    tax_identifiers: list[dict[str, Any]] | None = None


class PaginationLink(BaseModel):
    """Model for a single pagination link."""

    href: str | None = None


class PaginationLinks(BaseModel):
    """Model for the pagination links of a list response."""

    first: PaginationLink | None = None
    last: PaginationLink | None = None
    prev: PaginationLink | None = None
    next: PaginationLink | None = None


class ShipmentsList(BaseModel):
    """Response model for the shipments list API."""

    shipments: list[Shipment]
    total: int
    page: int
    pages: int
    links: PaginationLinks | None = None


class Carrier(BaseModel):
    """Model for a connected carrier account."""

    carrier_id: str
    carrier_code: str
    friendly_name: str | None = None
    nickname: str | None = None
    account_number: str | None = None


class CarriersList(BaseModel):
    """Response model for the carriers list API.

    The endpoint documents a 207 partial-success response; ``errors`` carries the
    details of any carrier accounts that could not be returned.
    """

    carriers: list[Carrier]
    errors: list[dict[str, Any]] = []


class TagsList(BaseModel):
    """Response model for the tags list API."""

    tags: list[Tag]
