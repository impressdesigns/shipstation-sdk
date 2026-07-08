"""Parameters for ShipStation API requests."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

type ShipmentStatus = Literal[
    "pending",
    "processing",
    "label_purchased",
    "cancelled",
]

type ShipmentSortKey = Literal[
    "modified_at",
    "created_at",
]

type SortDirection = Literal[
    "asc",
    "desc",
]


class ShipmentListParameters(BaseModel, strict=True):
    """Parameters for listing shipments."""

    shipment_status: ShipmentStatus | None = None
    store_id: str | None = None
    batch_id: str | None = None
    tag: str | None = None
    sales_order_id: str | None = None
    shipment_number: str | None = None
    external_shipment_id: str | None = None
    item_keyword: str | None = None
    ship_to_name: str | None = None
    created_at_start: datetime | None = None
    created_at_end: datetime | None = None
    modified_at_start: datetime | None = None
    modified_at_end: datetime | None = None
    payment_date_start: datetime | None = None
    payment_date_end: datetime | None = None
    sort_by: ShipmentSortKey | None = None
    sort_dir: SortDirection | None = None
    page: int | None = Field(None, ge=1)
    page_size: int | None = Field(None, ge=1)
