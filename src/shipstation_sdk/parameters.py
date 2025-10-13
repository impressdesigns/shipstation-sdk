"""Parameters for ShipStation API requests."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

type OrderStatus = Literal[
    "awaiting_payment",
    "awaiting_shipment",
    "pending_fulfillment",
    "shipped",
    "on_hold",
    "cancelled",
    "rejected_fulfillment",
]

type OrderSortKey = Literal[
    "OrderDate",
    "ModifyDate",
    "CreateDate",
]

type SortDirection = Literal[
    "ASC",
    "DESC",
]


class OrderListParameters(BaseModel, strict=True):
    """Parameters for listing orders."""

    customer_name: str | None = Field(None, alias="customerName")
    item_keyword: str | None = Field(None, alias="itemKeyword")
    create_date_start: date | None = Field(None, alias="createDateStart")
    create_date_end: date | None = Field(None, alias="createDateEnd")
    modify_date_start: date | None = Field(None, alias="modifyDateStart")
    modify_date_end: date | None = Field(None, alias="modifyDateEnd")
    order_date_start: date | None = Field(None, alias="orderDateStart")
    order_date_end: date | None = Field(None, alias="orderDateEnd")
    order_number: str | None = Field(None, alias="orderNumber")
    order_status: OrderStatus | None = Field(None, alias="orderStatus")
    payment_date_start: date | None = Field(None, alias="paymentDateStart")
    payment_date_end: date | None = Field(None, alias="paymentDateEnd")
    store_id: int | None = Field(None, alias="storeId")
    sort_by: OrderSortKey | None = Field(None, alias="sortBy")
    sort_dir: SortDirection | None = Field(None, alias="sortDir")
    page: int | None = Field(None, alias="page")
    page_size: int | None = Field(None, ge=1, le=500, alias="pageSize")
