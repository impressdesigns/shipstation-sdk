"""Interacting with ShipStation."""

from datetime import date
from typing import Any

from httpx import Client, Response

from .models import ShipmentsResponse


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
    ) -> ShipmentsResponse:
        """Get a list of shipments."""
        params = {}
        if ship_date_start:
            params["shipDateStart"] = ship_date_start.isoformat()
        if ship_date_end:
            params["shipDateEnd"] = ship_date_end.isoformat()
        response = self.make_request("GET", "/shipments", params=params)
        response.raise_for_status()
        return ShipmentsResponse.model_validate(response.json())
