"""Interacting with ShipStation."""

import time
from collections.abc import Iterator
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qsl, quote, urlsplit

import niquests

from .models import (
    CarriersList,
    CreateShipmentsResponse,
    Label,
    LabelsList,
    Shipment,
    ShipmentRequest,
    ShipmentsList,
    TagsList,
    Webhook,
    WebhookHeader,
)
from .parameters import LabelListParameters, ShipmentListParameters

#: The only host a webhook's ``resource_url`` may name: anything else is not ShipStation's.
API_HOST = "api.shipstation.com"

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

    def create_shipments(self, shipments: list[ShipmentRequest]) -> CreateShipmentsResponse:
        """Create shipments; each comes back with its id, or with the errors that stopped it.

        A shipment ShipStation refuses does not fail the call: check ``has_errors`` and each
        shipment's ``errors``.
        """
        body = {"shipments": [shipment.model_dump(mode="json", exclude_none=True) for shipment in shipments]}
        response = self.make_request("POST", "/v2/shipments", json=body)
        response.raise_for_status()
        return CreateShipmentsResponse.model_validate(response.json())

    def update_shipment(self, shipment_id: str, shipment: ShipmentRequest) -> Shipment:
        """Update a shipment that has no label yet; fields left ``None`` are left as they are."""
        response = self.make_request(
            "PUT",
            f"/v2/shipments/{shipment_id}",
            json=shipment.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return Shipment.model_validate(response.json())

    def list_labels(self, parameters: LabelListParameters | None = None) -> LabelsList:
        """Get a page of labels."""
        params = parameters.model_dump(mode="json", exclude_none=True) if parameters else {}
        response = self.make_request("GET", "/v2/labels", params=params)
        response.raise_for_status()
        return LabelsList.model_validate(response.json())

    def iter_labels(self, parameters: LabelListParameters | None = None) -> Iterator[Label]:
        """Iterate over every label matching the parameters, following pagination."""
        parameters = parameters.model_copy() if parameters else LabelListParameters()
        parameters.page = parameters.page or 1
        while True:
            labels_list = self.list_labels(parameters)
            yield from labels_list.labels
            if labels_list.page >= labels_list.pages:
                return
            parameters.page = labels_list.page + 1

    def iter_labels_at(self, resource_url: str) -> Iterator[Label]:
        """Iterate over the labels a ``label_created_v2`` webhook's ``resource_url`` names.

        The URL is ``https://api.shipstation.com/v2/labels?batch_id=...``. Its query becomes
        list parameters, so the request goes to this client's own host with its own key:
        a URL naming any other host or path is refused rather than sent the key.

        Raises
        ------
        ValueError
            If the URL is not a labels list on ShipStation's API host.
        """
        url = urlsplit(resource_url)
        if url.scheme != "https" or url.hostname != API_HOST or url.path.rstrip("/") != "/v2/labels":
            msg = f"Not a ShipStation labels URL: {resource_url!r}"
            raise ValueError(msg)
        filters = dict(parse_qsl(url.query))
        known = set(LabelListParameters.model_fields)
        parameters = LabelListParameters.model_validate(
            {key: value for key, value in filters.items() if key in known and key not in {"page", "page_size"}},
            strict=False,
        )
        yield from self.iter_labels(parameters)

    def list_webhooks(self) -> list[Webhook]:
        """Get the account's webhook subscriptions."""
        response = self.make_request("GET", "/v2/environment/webhooks")
        response.raise_for_status()
        return [Webhook.model_validate(webhook) for webhook in response.json()]

    def create_webhook(
        self,
        *,
        name: str,
        event: str,
        url: str,
        headers: list[WebhookHeader] | None = None,
        store_id: str | None = None,
    ) -> Webhook:
        """Subscribe ``url`` to ``event`` (such as ``label_created_v2``).

        ``headers`` are sent with every call, which is how a listener tells ShipStation's
        calls from anyone else's.
        """
        body: dict[str, Any] = {"name": name, "event": event, "url": url}
        if headers:
            body["headers"] = [header.model_dump() for header in headers]
        if store_id is not None:
            body["store_id"] = store_id
        response = self.make_request("POST", "/v2/environment/webhooks", json=body)
        response.raise_for_status()
        return Webhook.model_validate(response.json())
