"""ShipStation API models."""

from datetime import date, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import AfterValidator, BaseModel, Field
from pydantic.functional_serializers import PlainSerializer

# https://www.shipstation.com/docs/api/requirements/#datetime-format-and-time-zone
LA_TIMEZONE = ZoneInfo("America/Los_Angeles")


def add_timezone(value: datetime | None) -> datetime | None:
    """Add timezone information to datetime fields."""
    if value:
        value = value.replace(tzinfo=LA_TIMEZONE)
    return value


def to_timezoneless_string(value: datetime | None) -> str | None:
    """Convert datetime to a string without timezone information."""
    if value:
        return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond * 10:07d}"
    return None


ShipStationDateTime = Annotated[datetime, AfterValidator(add_timezone), PlainSerializer(to_timezoneless_string)]


class Address(BaseModel):
    """Model for an address."""

    name: str | None
    company: str | None
    street1: str | None
    street2: str | None
    street3: str | None
    city: str | None
    state: str | None
    postal_code: str | None = Field(..., alias="postalCode")
    country: str | None
    phone: str | None
    residential: bool | None
    address_verified: str | None = Field(..., alias="addressVerified")


class Weight(BaseModel):
    """Model for the weight of the shipment."""

    value: float
    units: str
    weight_units: int = Field(..., alias="WeightUnits")


class Dimensions(BaseModel):
    """Model for the dimensions of the shipment."""

    units: str
    length: float
    width: float
    height: float


class InsuranceOptions(BaseModel):
    """Model for insurance options."""

    provider: str | None
    insure_shipment: bool = Field(..., alias="insureShipment")
    insured_value: float = Field(..., alias="insuredValue")


class ShipmentAdvancedOptions(BaseModel):
    """Model for advanced options."""

    bill_to_party: str | None = Field(..., alias="billToParty")
    bill_to_account: str | None = Field(..., alias="billToAccount")
    bill_to_postal_code: str | None = Field(..., alias="billToPostalCode")
    bill_to_country_code: str | None = Field(..., alias="billToCountryCode")
    store_id: int = Field(..., alias="storeId")


class Shipment(BaseModel):
    """Model for a shipment."""

    shipment_id: int = Field(..., alias="shipmentId")
    order_id: int = Field(..., alias="orderId")
    order_key: str = Field(..., alias="orderKey")
    user_id: str = Field(..., alias="userId")
    customer_email: str | None = Field(..., alias="customerEmail")
    order_number: str = Field(..., alias="orderNumber")
    create_date: ShipStationDateTime = Field(..., alias="createDate")
    ship_date: date = Field(..., alias="shipDate")
    shipment_cost: float = Field(..., alias="shipmentCost")
    insurance_cost: float = Field(..., alias="insuranceCost")
    tracking_number: str = Field(..., alias="trackingNumber")
    is_return_label: bool = Field(..., alias="isReturnLabel")
    batch_number: int | None = Field(..., alias="batchNumber")
    carrier_code: str = Field(..., alias="carrierCode")
    service_code: str = Field(..., alias="serviceCode")
    package_code: str | None = Field(..., alias="packageCode")
    confirmation: bool | None
    warehouse_id: int = Field(..., alias="warehouseId")
    voided: bool
    void_date: str | None = Field(..., alias="voidDate")
    marketplace_notified: bool = Field(..., alias="marketplaceNotified")
    notify_error_message: str | None = Field(..., alias="notifyErrorMessage")
    ship_to: Address = Field(..., alias="shipTo")
    weight: Weight
    dimensions: Dimensions | None
    insurance_options: InsuranceOptions = Field(..., alias="insuranceOptions")
    advanced_options: ShipmentAdvancedOptions = Field(..., alias="advancedOptions")
    shipment_items: None = Field(..., alias="shipmentItems")
    label_data: None = Field(..., alias="labelData")
    form_data: None = Field(..., alias="formData")


class ShipmentsList(BaseModel):
    """Response model for Shipments API."""

    shipments: list[Shipment]
    total: int
    page: int
    pages: int


class Option(BaseModel):
    """Model for an order item option."""

    name: str
    value: str


class Item(BaseModel):
    """Model for an order item."""

    order_item_id: int = Field(..., alias="orderItemId")
    line_item_key: str | None = Field(..., alias="lineItemKey")
    sku: str | None
    name: str
    image_url: str | None = Field(..., alias="imageUrl")
    weight: Weight | None
    quantity: int
    unit_price: float = Field(..., alias="unitPrice")
    tax_amount: float | None = Field(..., alias="taxAmount")
    shipping_amount: float | None = Field(..., alias="shippingAmount")
    warehouse_location: str | None = Field(..., alias="warehouseLocation")
    options: list[Option]
    product_id: int | None = Field(..., alias="productId")
    fulfillment_sku: str | None = Field(..., alias="fulfillmentSku")
    adjustment: bool
    upc: str | None
    create_date: str = Field(..., alias="createDate")
    modify_date: str = Field(..., alias="modifyDate")


class CustomsItem(BaseModel):
    """Model for customs item."""

    customs_item_id: int = Field(..., alias="customsItemId")
    description: str
    quantity: int
    value: float
    harmonized_tariff_code: str | None = Field(..., alias="harmonizedTariffCode")
    country_of_origin: str = Field(..., alias="countryOfOrigin")


class InternationalOptions(BaseModel):
    """Model for international shipping options."""

    contents: str | None
    customs_items: list[CustomsItem] | None = Field(..., alias="customsItems")
    non_delivery: str | None = Field(..., alias="nonDelivery")


class OrderAdvancedOptions(BaseModel):
    """Model for advanced options."""

    warehouse_id: int = Field(..., alias="warehouseId")
    non_machinable: bool = Field(..., alias="nonMachinable")
    saturday_delivery: bool = Field(..., alias="saturdayDelivery")
    contains_alcohol: bool = Field(..., alias="containsAlcohol")
    merged_or_split: bool = Field(..., alias="mergedOrSplit")
    merged_ids: list[int] = Field(..., alias="mergedIds")
    parent_id: int | None = Field(..., alias="parentId")
    store_id: int = Field(..., alias="storeId")
    custom_field_1: str | None = Field(..., alias="customField1")
    custom_field_2: str | None = Field(..., alias="customField2")
    custom_field_3: str | None = Field(..., alias="customField3")
    source: str | None = Field(..., alias="source")
    bill_to_party: str | None = Field(..., alias="billToParty")
    bill_to_account: str | None = Field(..., alias="billToAccount")
    bill_to_postal_code: str | None = Field(..., alias="billToPostalCode")
    bill_to_country_code: str | None = Field(..., alias="billToCountryCode")
    bill_to_my_other_account: int | None = Field(..., alias="billToMyOtherAccount")


class Order(BaseModel):
    """Model for an order."""

    order_id: int = Field(..., alias="orderId")
    order_number: str = Field(..., alias="orderNumber")
    order_key: str = Field(..., alias="orderKey")
    order_date: ShipStationDateTime = Field(..., alias="orderDate")
    create_date: ShipStationDateTime = Field(..., alias="createDate")
    modify_date: ShipStationDateTime = Field(..., alias="modifyDate")
    payment_date: ShipStationDateTime | None = Field(..., alias="paymentDate")
    ship_by_date: ShipStationDateTime | None = Field(..., alias="shipByDate")
    order_status: str | None = Field(..., alias="orderStatus")
    customer_id: int | None = Field(..., alias="customerId")
    customer_username: str | None = Field(..., alias="customerUsername")
    customer_email: str | None = Field(..., alias="customerEmail")
    bill_to: Address = Field(..., alias="billTo")
    ship_to: Address = Field(..., alias="shipTo")
    items: list[Item] | None
    order_total: float | None = Field(..., alias="orderTotal")
    amount_paid: float | None = Field(..., alias="amountPaid")
    tax_amount: float | None = Field(..., alias="taxAmount")
    shipping_amount: float | None = Field(..., alias="shippingAmount")
    customer_notes: str | None = Field(..., alias="customerNotes")
    internal_notes: str | None = Field(..., alias="internalNotes")
    gift: bool
    gift_message: str | None = Field(..., alias="giftMessage")
    payment_method: str | None = Field(..., alias="paymentMethod")
    requested_shipping_service: str | None = Field(..., alias="requestedShippingService")
    carrier_code: str | None = Field(..., alias="carrierCode")
    service_code: str | None = Field(..., alias="serviceCode")
    package_code: str | None = Field(..., alias="packageCode")
    confirmation: str
    ship_date: date | None = Field(..., alias="shipDate")
    hold_until_date: date | None = Field(..., alias="holdUntilDate")
    weight: Weight
    dimensions: Dimensions | None
    insurance_options: InsuranceOptions = Field(..., alias="insuranceOptions")
    international_options: InternationalOptions = Field(..., alias="internationalOptions")
    advanced_options: OrderAdvancedOptions = Field(..., alias="advancedOptions")
    tag_ids: list[int] | None = Field(..., alias="tagIds")
    user_id: list[str] | None = Field(..., alias="userId")
    externally_fulfilled: bool = Field(..., alias="externallyFulfilled")
    externally_fulfilled_by: str | None = Field(..., alias="externallyFulfilledBy")
    externally_fulfilled_by_id: int | None = Field(None, alias="externallyFulfilledById")
    externally_fulfilled_by_name: str | None = Field(None, alias="externallyFulfilledByName")
    label_messages: list[str] | None = Field(..., alias="labelMessages")


class OrdersList(BaseModel):
    """Model for a list of orders."""

    orders: list[Order]
    total: int
    page: int
    pages: int
