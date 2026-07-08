"""Interacting with ShipStation."""

import time
from collections.abc import Iterator
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import niquests

from .models import CarriersList, Shipment, ShipmentsList, TagsList
from .parameters import ShipmentListParameters

RETRY_ATTEMPTS = 3
DEFAULT_RETRY_AFTER_SECONDS = 5.0
MAX_RETRY_AFTER_SECONDS = 60.0


def _retry_after_seconds(response: niquests.Response) -> float:
    """Determine how long to sleep before retrying a rate-limited request.

    Parameters
    ----------
    response
        The 429 response, whose ``Retry-After`` header is honored in either RFC 9110
        form -- delta-seconds or an HTTP-date -- capped at ``MAX_RETRY_AFTER_SECONDS``.
    """
    header = response.headers.get("Retry-After")
    if header is None:
        return DEFAULT_RETRY_AFTER_SECONDS
    try:
        seconds = float(header)
    except ValueError:
        try:
            seconds = (parsedate_to_datetime(header) - datetime.now(tz=UTC)).total_seconds()
        except (TypeError, ValueError):
            return DEFAULT_RETRY_AFTER_SECONDS
    return min(max(seconds, 0.0), MAX_RETRY_AFTER_SECONDS)


class ShipStationClient:
    """A class wrapping ShipStation API v2 interaction."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.shipstation.com",
        timeout: float = 60.0,
    ) -> None:
        """Initialize the ShipStationClient class.

        Parameters
        ----------
        api_key
            The ShipStation API v2 key, sent as the ``api-key`` header on every request.
        base_url
            The API host.
        timeout
            The request timeout in seconds.
        """
        self.session = niquests.Session(
            base_url=base_url,
            timeout=timeout,
        )
        self.session.headers["api-key"] = api_key

    def make_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> niquests.Response:
        """Make a request to ShipStation, retrying when rate-limited.

        Retries up to ``RETRY_ATTEMPTS`` total attempts on HTTP 429, sleeping the
        response's ``Retry-After`` (``DEFAULT_RETRY_AFTER_SECONDS`` when absent).
        """
        args: dict[str, Any] = {
            "url": path,
            "method": method,
        }

        if params is not None:
            args["params"] = params

        if json is not None:
            args["json"] = json

        response = self.session.request(**args)
        for _attempt in range(RETRY_ATTEMPTS - 1):
            if response.status_code != HTTPStatus.TOO_MANY_REQUESTS:
                break
            time.sleep(_retry_after_seconds(response))
            response = self.session.request(**args)
        return response

    def list_shipments(self, parameters: ShipmentListParameters | None = None) -> ShipmentsList:
        """Get a page of shipments."""
        params = parameters.model_dump(mode="json", exclude_none=True) if parameters else {}
        response = self.make_request("GET", "/v2/shipments", params=params)
        response.raise_for_status()
        return ShipmentsList.model_validate(response.json())

    def iter_shipments(self, parameters: ShipmentListParameters | None = None) -> Iterator[Shipment]:
        """Iterate over every shipment matching the parameters, following pagination."""
        parameters = parameters.model_copy() if parameters else ShipmentListParameters()
        parameters.page = parameters.page or 1
        while True:
            shipments_list = self.list_shipments(parameters)
            yield from shipments_list.shipments
            if shipments_list.page >= shipments_list.pages:
                return
            parameters.page = shipments_list.page + 1

    def get_shipment(self, shipment_id: str) -> Shipment:
        """Get a specific shipment."""
        response = self.make_request("GET", f"/v2/shipments/{shipment_id}")
        response.raise_for_status()
        return Shipment.model_validate(response.json())

    def get_shipment_by_external_id(self, external_shipment_id: str) -> Shipment:
        """Get a specific shipment by the external shipment ID it was created with.

        External shipment IDs are caller-defined and may contain URL metacharacters
        (e.g. marketplace IDs like ``gid://...``), so the path segment is escaped.
        """
        response = self.make_request(
            "GET",
            f"/v2/shipments/external_shipment_id/{quote(external_shipment_id, safe='')}",
        )
        response.raise_for_status()
        return Shipment.model_validate(response.json())

    def list_carriers(self) -> CarriersList:
        """Get the connected carrier accounts."""
        response = self.make_request("GET", "/v2/carriers")
        response.raise_for_status()
        return CarriersList.model_validate(response.json())

    def list_tags(self) -> TagsList:
        """Get the tags defined on the account."""
        response = self.make_request("GET", "/v2/tags")
        response.raise_for_status()
        return TagsList.model_validate(response.json())
