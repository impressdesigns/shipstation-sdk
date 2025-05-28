"""ShipStation API models."""

from datetime import date, datetime

from pydantic import BaseModel, Field


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


class AdvancedOptions(BaseModel):
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
    create_date: datetime = Field(..., alias="createDate")
    ship_date: str = Field(..., alias="shipDate")
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
    advanced_options: AdvancedOptions = Field(..., alias="advancedOptions")
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
    sku: str
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


class Order(BaseModel):
    """Model for an order."""

    order_id: int = Field(..., alias="orderId")
    order_number: str = Field(..., alias="orderNumber")
    order_key: str = Field(..., alias="orderKey")
    order_date: str = Field(..., alias="orderDate")
    create_date: str = Field(..., alias="createDate")
    modify_date: str = Field(..., alias="modifyDate")
    payment_date: str | None = Field(..., alias="paymentDate")
    ship_by_date: str | None = Field(..., alias="shipByDate")
    order_status: str | None = Field(..., alias="orderStatus")
    customer_id: int | None = Field(..., alias="customerId")
    customer_username: str | None = Field(..., alias="customerUsername")
    customer_email: str | None = Field(..., alias="customerEmail")
    bill_to: Address | None = Field(..., alias="billTo")
    ship_to: Address | None = Field(..., alias="shipTo")
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
    ship_date: str | None = Field(..., alias="shipDate")
    hold_until_date: date | None = Field(..., alias="holdUntilDate")
    weight: Weight
    dimensions: Dimensions | None
    insurance_options: InsuranceOptions = Field(..., alias="insuranceOptions")
    international_options: InternationalOptions = Field(..., alias="internationalOptions")
    advanced_options: AdvancedOptions = Field(..., alias="advancedOptions")
    tag_ids: list[str] | None = Field(..., alias="tagIds")
    user_id: list[str] | None = Field(..., alias="userId")
    externally_fulfilled: bool = Field(..., alias="externallyFulfilled")
    externally_fulfilled_by: str | None = Field(..., alias="externallyFulfilledBy")
    externally_fulfilled_by_id: int | None = Field(None, alias="externallyFulfilledById")
    externally_fulfilled_by_name: str | None = Field(None, alias="externallyFulfilledByName")


class OrdersList(BaseModel):
    """Model for a list of orders."""

    orders: list[Order]
    total: int
    page: int
    pages: int
