"""Interacting with ShipStation."""

from datetime import date
from typing import Any

from httpx import Client, Response

from .models import OrdersList, ShipmentsList


class ShipStationClient:
    """A class wrapping ShipStation interaction."""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        timeout: float,
    ) -> None:
        """Initialize the ShipStationClient class."""
        self.client = Client(
            base_url=base_url,
            auth=(client_id, client_secret),
            timeout=timeout,
        )

    def make_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Response:
        """Make a request to ShipStation."""
        args: dict[str, str | dict[str, str]] = {
            "url": path,
            "method": method,
        }

        if params is not None:
            args["params"] = params

        if json is not None:
            args["json"] = json

        return self.client.request(**args)  # type: ignore[arg-type]

    def get_shipments(
        self,
        ship_date_start: date | None = None,
        ship_date_end: date | None = None,
    ) -> ShipmentsList:
        """Get a list of shipments."""
        params = {}
        if ship_date_start:
            params["shipDateStart"] = ship_date_start.isoformat()
        if ship_date_end:
            params["shipDateEnd"] = ship_date_end.isoformat()
        response = self.make_request("GET", "/shipments", params=params)
        response.raise_for_status()
        return ShipmentsList.model_validate(response.json())

    def get_orders(
        self,
        create_date_start: date | None = None,
        create_date_end: date | None = None,
    ) -> OrdersList:
        """Get a list of orders."""
        params = {}
        if create_date_start:
            params["createDateStart"] = create_date_start.isoformat()
        if create_date_end:
            params["createDateEnd"] = create_date_end.isoformat()
        response = self.make_request("GET", "/orders", params=params)
        response.raise_for_status()
        return OrdersList.model_validate(response.json())
