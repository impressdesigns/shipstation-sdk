"""ShipStation API models."""

from pydantic import BaseModel, Field


class ShipTo(BaseModel):
    """Model for the ShipTo address."""

    name: str
    company: str | None
    street1: str
    street2: str
    street3: str | None
    city: str
    state: str
    postal_code: str = Field(..., alias="postalCode")
    country: str
    phone: str | None
    residential: bool | None
    address_verified: bool | None = Field(..., alias="addressVerified")


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
    create_date: str = Field(..., alias="createDate")
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
    ship_to: ShipTo = Field(..., alias="shipTo")
    weight: Weight
    dimensions: Dimensions | None
    insurance_options: InsuranceOptions = Field(..., alias="insuranceOptions")
    advanced_options: AdvancedOptions = Field(..., alias="advancedOptions")
    shipment_items: None = Field(..., alias="shipmentItems")
    label_data: None = Field(..., alias="labelData")
    form_data: None = Field(..., alias="formData")


class ShipmentsResponse(BaseModel):
    """Response model for Shipments API."""

    shipments: list[Shipment]
    total: int
    page: int
    pages: int
