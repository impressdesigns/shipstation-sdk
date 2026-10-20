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


class Geolocation(BaseModel):
    """Model for one geolocation item of an address, such as a what3words location."""

    type: str | None = None
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
    geolocation: list[Geolocation] | None = None


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


class FedexFreight(BaseModel):
    """Model for the FedEx Freight options of a shipment."""

    shipper_load_and_count: str | None = None
    booking_confirmation: str | None = None


class CollectOnDelivery(BaseModel):
    """Model for a collect-on-delivery request: how and how much the recipient pays."""

    payment_type: str | None = None
    payment_amount: MonetaryValue | None = None


class DangerousGoodsContact(BaseModel):
    """Model for the contact to reach about a shipment's dangerous goods."""

    name: str | None = None
    phone: str | None = None


class WindsorFrameworkDetails(BaseModel):
    """Model for the Windsor Framework details of a shipment into Northern Ireland."""

    movement_indicator: str | None = None
    not_at_risk: bool | None = None


class NetstampsOptions(BaseModel):
    """Model for where on a Netstamps sheet a label prints."""

    row: int | None = None
    column: int | None = None


class TransparencyCode(BaseModel):
    """Model for the Amazon Transparency codes of one order item."""

    order_item_id: str | None = None
    codes: list[str] | None = None


class AdvancedShipmentOptions(BaseModel):
    """Model for advanced shipment options."""

    custom_field1: str | None = None
    custom_field2: str | None = None
    custom_field3: str | None = None
    bill_to_party: str | None = None
    bill_to_account: str | None = None
    bill_to_postal_code: str | None = None
    bill_to_country_code: str | None = None
    contains_alcohol: bool | None = None
    delivered_duty_paid: bool | None = None
    dry_ice: bool | None = None
    dry_ice_weight: Weight | None = None
    non_machinable: bool | None = None
    saturday_delivery: bool | None = None
    fedex_freight: FedexFreight | None = None
    use_ups_ground_freight_pricing: bool | None = None
    freight_class: str | None = None
    origin_type: str | None = None
    additional_handling: bool | None = None
    shipper_release: bool | None = None
    collect_on_delivery: CollectOnDelivery | None = None
    third_party_consignee: bool | None = None
    dangerous_goods: bool | None = None
    dangerous_goods_contact: DangerousGoodsContact | None = None
    movement_indicator: str | None = None
    windsor_framework_details: WindsorFrameworkDetails | None = None
    ancillary_endorsements_option: str | None = None
    return_pickup_attempts: int | None = None
    own_document_upload: bool | None = None
    limited_quantity: bool | None = None
    event_notification: bool | None = None
    fragile: bool | None = None
    delivery_as_addressed: bool | None = None
    return_after_first_attempt: bool | None = None
    regulated_content_type: str | None = None
    netstamps_options: NetstampsOptions | None = None
    suppress_carrier_generated_documents: list[str] | None = None
    transparency_codes: list[TransparencyCode] | None = None


class TaxIdentifier(BaseModel):
    """Model for a tax identifier on a customs declaration, such as a VAT or EORI number."""

    taxable_entity_type: str | None = None
    identifier_type: str | None = None
    issuing_authority: str | None = None
    value: str | None = None


class EstimatedImportCharges(BaseModel):
    """Model for the import taxes and duties a commercial invoice estimates."""

    taxes: MonetaryValue | None = None
    duties: MonetaryValue | None = None


class InvoiceAdditionalDetails(BaseModel):
    """Model for the charges a commercial invoice adds to the value of the goods."""

    freight_charge: MonetaryValue | None = None
    insurance_charge: MonetaryValue | None = None
    discount: MonetaryValue | None = None
    estimated_import_charges: EstimatedImportCharges | None = None
    other_charge: MonetaryValue | None = None
    other_charge_description: str | None = None


class CustomsItem(BaseModel):
    """Model for one line of a customs declaration; ``customs_item_id`` is ShipStation's own: read but never sent."""

    description: str | None = None
    quantity: int | None = None
    # A bare number here, with its currency alongside, unlike the monetary values elsewhere.
    value: float | None = None
    value_currency: str | None = None
    weight: Weight | None = None
    harmonized_tariff_code: str | None = None
    country_of_origin: str | None = None
    unit_of_measure: str | None = None
    sku: str | None = None
    sku_description: str | None = None
    customs_item_id: str | None = Field(default=None, exclude=True)


class CustomsOptions(BaseModel):
    """Model for the customs declaration of an international shipment."""

    contents: str | None = None
    contents_explanation: str | None = None
    non_delivery: str | None = None
    terms_of_trade_code: str | None = None
    declaration: str | None = None
    pending_documents: bool | None = None
    invoice_additional_details: InvoiceAdditionalDetails | None = None
    importer_of_record: Address | None = None
    customs_items: list[CustomsItem] | None = None


class Dimensions(BaseModel):
    """Model for a package's dimensions: ShipStation needs all three sides and the unit."""

    length: float
    width: float
    height: float
    unit: str = "inch"


class LabelMessages(BaseModel):
    """Model for the custom messages printed on one package's label.

    How many lines print, and how long each may be, depends on the carrier: ShipStation documents three
    for USPS and FedEx and two for UPS and OnTrac.
    """

    reference1: str | None = None
    reference2: str | None = None
    reference3: str | None = None


class DangerousAmount(BaseModel):
    """Model for the amount of a dangerous good in a package."""

    amount: float | None = None
    unit: str | None = None


class DangerousGoods(BaseModel):
    """Model for the dangerous goods details of one product in a package."""

    id_number: str | None = None
    shipping_name: str | None = None
    technical_name: str | None = None
    product_class: str | None = None
    product_class_subsidiary: str | None = None
    packaging_group: str | None = None
    dangerous_amount: DangerousAmount | None = None
    quantity: int | None = None
    packaging_instruction: str | None = None
    packaging_instruction_section: str | None = None
    packaging_type: str | None = None
    transport_mean: str | None = None
    transport_category: str | None = None
    regulation_authority: str | None = None
    regulation_level: str | None = None
    radioactive: bool | None = None
    reportable_quantity: bool | None = None
    tunnel_code: str | None = None
    additional_description: str | None = None


class CpscCertificate(BaseModel):
    """Model for a US Consumer Product Safety Commission eFiling certificate of a product."""

    certifier_id: str | None = None
    certificate_version_id: str | None = None


class CpscDisclaim(BaseModel):
    """Model for a product's disclaimer of the CPSC eFiling requirement, and why."""

    disclaim_code: str | None = None
    intended_use_code: str | None = None
    intended_use_description: str | None = None


class PackageProduct(BaseModel):
    """Model for one product in a package, as a customs declaration describes it."""

    description: str | None = None
    quantity: int | None = None
    value: MonetaryValue | None = None
    weight: Weight | None = None
    harmonized_tariff_code: str | None = None
    country_of_origin: str | None = None
    unit_of_measure: str | None = None
    sku: str | None = None
    sku_description: str | None = None
    mid_code: str | None = None
    product_url: str | None = None
    vat_rate: float | None = None
    dangerous_goods: list[DangerousGoods] | None = None
    manufacturer_product_id_type: str | None = None
    manufacturer_product_id: str | None = None
    manufacturer_ns_product_id: str | None = None
    cpsc_certificates: list[CpscCertificate] | None = None
    cpsc_disclaim: CpscDisclaim | None = None


class Package(BaseModel):
    """Model for one package of a shipment, as a request sends it and a shipment returns it.

    Every field ShipStation documents for a shipment's package is here, so a shipment read back and
    sent again (an update replaces the whole shipment) keeps what was set on it. ``shipment_package_id``
    is ShipStation's own and read-only: it is read but never sent.
    """

    weight: Weight
    dimensions: Dimensions | None = None
    package_id: str | None = None
    package_code: str | None = None
    package_name: str | None = None
    insured_value: MonetaryValue | None = None
    label_messages: LabelMessages | None = None
    external_package_id: str | None = None
    content_description: str | None = None
    products: list[PackageProduct] | None = None
    shipment_package_id: str | None = Field(default=None, exclude=True)


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
    packages: list[Package] = []
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
    customs: CustomsOptions | None = None
    tax_identifiers: list[TaxIdentifier] | None = None
    batch_ids: list[str] = []


class PaginationLink(BaseModel):
    """Model for a single pagination link."""

    href: str | None = None
    type: str | None = None


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


class CarrierService(BaseModel):
    """Model for one shipping service a carrier offers."""

    carrier_id: str | None = None
    carrier_code: str | None = None
    service_code: str | None = None
    name: str | None = None
    domestic: bool | None = None
    international: bool | None = None
    is_multi_package_supported: bool | None = None
    send_rates: bool | None = None


class PackageType(BaseModel):
    """Model for one package type a carrier offers, such as a flat-rate box."""

    package_id: str | None = None
    package_code: str | None = None
    name: str | None = None
    dimensions: Dimensions | None = None
    description: str | None = None


class CarrierOption(BaseModel):
    """Model for one advanced option a carrier supports, and its default."""

    name: str | None = None
    default_value: str | None = None
    description: str | None = None


class Carrier(BaseModel):
    """Model for a connected carrier account."""

    carrier_id: str
    carrier_code: str
    friendly_name: str | None = None
    nickname: str | None = None
    account_number: str | None = None
    connection_status: str | None = None
    requires_funded_amount: bool | None = None
    balance: float | None = None
    funding_source_id: str | None = None
    primary: bool | None = None
    has_multi_package_supporting_services: bool | None = None
    supports_label_messages: bool | None = None
    disabled_by_billing_plan: bool | None = None
    services: list[CarrierService] = []
    packages: list[PackageType] = []
    options: list[CarrierOption] = []
    send_rates: bool | None = None
    supports_user_managed_rates: bool | None = None


class CarriersList(BaseModel):
    """Response model for the carriers list API.

    The endpoint documents a 207 partial-success response; ``errors`` carries the
    details of any carrier accounts that could not be returned.
    """

    carriers: list[Carrier]
    errors: list[dict[str, Any]] = []
    request_id: str | None = None
    total: int | None = None
    page: int | None = None
    pages: int | None = None
    links: PaginationLinks | None = None


class TagsList(BaseModel):
    """Response model for the tags list API."""

    tags: list[Tag]


class LabelDownload(BaseModel):
    """Model for where a label's file can be downloaded, in each format ShipStation offers."""

    href: str | None = None
    pdf: str | None = None
    png: str | None = None
    zpl: str | None = None


class PaperlessDownload(BaseModel):
    """Model for a paperless label: where to download it and how to hand the package off without it."""

    href: str | None = None
    instructions: str | None = None
    handoff_code: str | None = None


class AlternativeIdentifier(BaseModel):
    """Model for another identifier a carrier gives a label, such as a last-mile tracking number."""

    type: str | None = None
    value: str | None = None


class LabelPackage(BaseModel):
    """Model for one package of a bought label: its own tracking number and where it falls in the shipment."""

    package_id: int | None = None
    package_code: str | None = None
    weight: Weight | None = None
    dimensions: Dimensions | None = None
    insured_value: MonetaryValue | None = None
    tracking_number: str | None = None
    label_download: LabelDownload | None = None
    form_download: PaginationLink | None = None
    qr_code_download: PaginationLink | None = None
    paperless_download: PaperlessDownload | None = None
    label_messages: LabelMessages | None = None
    external_package_id: str | None = None
    content_description: str | None = None
    sequence: int | None = None
    has_label_documents: bool | None = None
    has_form_documents: bool | None = None
    has_qr_code_documents: bool | None = None
    has_paperless_label_documents: bool | None = None
    alternative_identifiers: list[AlternativeIdentifier] | None = None


class ShipmentRequestItem(BaseModel):
    """Model for one item on a shipment request: what a packer sees on the pick list."""

    name: str
    quantity: int
    sku: str | None = None
    unit_price: float | None = None
    external_order_item_id: str | None = None
    sales_order_id: str | None = None
    sales_order_item_id: str | None = None
    bundle_sku: str | None = None
    external_order_id: str | None = None
    asin: str | None = None
    order_source_code: str | None = None
    item_id: str | None = None
    allocation_status: str | None = None
    image_url: str | None = None
    weight: Weight | None = None
    tax_amount: float | None = None
    shipping_amount: float | None = None
    inventory_location: str | None = None
    options: list[ItemOption] | None = None
    product_id: str | None = None
    # The double-l spelling is the ShipStation API's, not ours.
    fullfilment_sku: str | None = None
    upc: str | None = None


class ShipmentRequest(BaseModel):
    """Model for the body of one shipment to create or update.

    ``ship_from`` and ``warehouse_id`` are alternatives: ShipStation refuses both. Fields left
    ``None`` are left off the wire, so an update changes only what it names.

    ``create_sales_order`` is read on create only: without it, ShipStation keeps the shipment out
    of its Orders tab. ShipStation documents a narrower body for create than for update; the
    fields here are the union, and ShipStation's own read-only fields (ids, timestamps, total
    weight, batch ids) are not here at all. ``shipment_status`` is settable on create only.
    """

    ship_to: Address | None = None
    ship_from: Address | None = None
    warehouse_id: str | None = None
    store_id: str | None = None
    create_sales_order: bool | None = None
    external_shipment_id: str | None = None
    shipment_number: str | None = None
    carrier_id: str | None = None
    service_code: str | None = None
    requested_shipment_service: str | None = None
    ship_by_date: datetime | None = None
    items: list[ShipmentRequestItem] | None = None
    packages: list[Package] | None = None
    advanced_options: AdvancedShipmentOptions | None = None
    internal_notes: str | None = None
    notes_to_buyer: str | None = None
    validate_address: str | None = None
    external_order_id: str | None = None
    shipment_status: str | None = None
    ship_date: ShipStationDate | None = None
    hold_until_date: datetime | None = None
    deliver_by_date: datetime | None = None
    order_source_code: str | None = None
    comparison_rate_type: str | None = None
    zone: int | None = None
    amount_paid: MonetaryValue | None = None
    shipping_paid: MonetaryValue | None = None
    tax_paid: MonetaryValue | None = None
    retail_rate: MonetaryValue | None = None
    return_to: Address | None = None
    tags: list[Tag] | None = None
    notes_from_buyer: str | None = None
    notes_for_gift: str | None = None
    is_gift: bool | None = None
    is_return: bool | None = None
    assigned_user: str | None = None
    display_scheme: str | None = None
    confirmation: str | None = None
    insurance_provider: str | None = None
    customs: CustomsOptions | None = None
    tax_identifiers: list[TaxIdentifier] | None = None


class AddressValidationMessage(BaseModel):
    """Model for one finding of address validation."""

    code: str | None = None
    message: str | None = None
    type: str | None = None
    detail_code: str | None = None


class AddressValidationResult(BaseModel):
    """Model for the outcome of validating a shipment's address: the address as sent, as matched, and why."""

    status: str | None = None
    original_address: Address | None = None
    matched_address: Address | None = None
    messages: list[AddressValidationMessage] = []


class CreatedShipment(Shipment):
    """Model for one shipment in a create response, with the errors ShipStation found in it."""

    # The schema documents these as plain strings; they were modelled as objects before it was read.
    errors: list[str | dict[str, Any]] | None = None
    address_validation: AddressValidationResult | None = None


class CreateShipmentsResponse(BaseModel):
    """Response model for the create shipments API."""

    has_errors: bool = False
    shipments: list[CreatedShipment]


class DeliveryPrediction(BaseModel):
    """Model for when ShipStation predicts a label's package will be delivered, and how sure it is."""

    delivery_date: ShipStationDate | None = None
    confidence_level: str | None = None


class RefundDetails(BaseModel):
    """Model for the refund of a voided label: its status and the amounts paid, asked for, approved and credited."""

    refund_status: str | None = None
    request_date: datetime | None = None
    amount_paid: MonetaryValue | None = None
    amount_requested: MonetaryValue | None = None
    amount_approved: MonetaryValue | None = None
    amount_credited: MonetaryValue | None = None


class RateDetail(BaseModel):
    """Model for one line of what a label cost, as the carrier billed it."""

    rate_detail_type: str | None = None
    carrier_description: str | None = None
    carrier_billing_code: str | None = None
    carrier_memo: str | None = None
    amount: MonetaryValue | None = None
    billing_source: str | None = None


class Label(BaseModel):
    """Model for a shipping label: what was bought, for which shipment, and its tracking numbers (one per package)."""

    label_id: str
    status: str | None = None
    shipment_id: str | None = None
    external_shipment_id: str | None = None
    external_order_id: str | None = None
    ship_date: ShipStationDate | None = None
    created_at: datetime | None = None
    shipment_cost: MonetaryValue | None = None
    tracking_number: str | None = None
    tracking_url: str | None = None
    tracking_status: str | None = None
    is_return_label: bool | None = None
    batch_id: str | None = None
    carrier_id: str | None = None
    carrier_code: str | None = None
    service_code: str | None = None
    voided: bool | None = None
    voided_at: datetime | None = None
    ship_to: Address | None = None
    packages: list[LabelPackage] = []
    shipment: Shipment | None = None
    delivery_prediction: DeliveryPrediction | None = None
    insurance_cost: MonetaryValue | None = None
    requested_comparison_amount: MonetaryValue | None = None
    rma_number: str | None = None
    is_international: bool | None = None
    charge_event: str | None = None
    outbound_label_id: str | None = None
    test_label: bool | None = None
    package_code: str | None = None
    validate_address: str | None = None
    void_type: str | None = None
    refund_details: RefundDetails | None = None
    label_download_type: str | None = None
    label_format: str | None = None
    display_scheme: str | None = None
    label_layout: str | None = None
    trackable: bool | None = None
    label_image_id: str | None = None
    confirmation: str | None = None
    label_download: LabelDownload | None = None
    form_download: PaginationLink | None = None
    qr_code_download: PaginationLink | None = None
    paperless_download: PaperlessDownload | None = None
    insurance_claim: PaginationLink | None = None
    alternative_identifiers: list[AlternativeIdentifier] | None = None
    rate_details: list[RateDetail] = []


class LabelsList(BaseModel):
    """Response model for the labels list API."""

    labels: list[Label]
    total: int
    page: int
    pages: int
    links: PaginationLinks | None = None


class WebhookHeader(BaseModel):
    """Model for one header ShipStation sends with every call of a webhook."""

    key: str
    value: str


class Webhook(BaseModel):
    """Model for a webhook subscription."""

    webhook_id: str
    url: str
    event: str
    name: str | None = None
    # The schema documents an integer store id here, unlike the ``se-`` strings everywhere else.
    store_id: int | str | None = None
    headers: list[WebhookHeader] = []
