"""Tests for the ShipStation API v2 client."""

import json
from http import HTTPStatus
from typing import Any

import pytest
from httpx import MockTransport, Request, Response

from shipstation_sdk import ShipStationClient
from shipstation_sdk.client import (
    DEFAULT_RETRY_AFTER_SECONDS,
    MAX_RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
    _retry_after_seconds,
)
from shipstation_sdk.parameters import ShipmentListParameters

MINIMAL_SHIPMENT: dict[str, Any] = {"shipment_id": "se-28529731", "shipment_status": "pending"}


def _shipments_page(page: int, pages: int, shipments: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a shipments list response body."""
    return {"shipments": shipments, "total": len(shipments) * pages, "page": page, "pages": pages}


def test_requests_carry_the_api_key_header() -> None:
    """Every request authenticates with the ``api-key`` header."""
    seen_headers: list[str | None] = []

    def handler(request: Request) -> Response:
        seen_headers.append(request.headers.get("api-key"))
        return Response(200, json={"tags": []})

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    client.list_tags()

    assert seen_headers == ["test-key"]


def test_list_shipments_sends_parameters_as_query_params() -> None:
    """List parameters serialize 1:1 onto the ``/v2/shipments`` query string."""
    seen_requests: list[Request] = []

    def handler(request: Request) -> Response:
        seen_requests.append(request)
        return Response(200, json=_shipments_page(1, 1, [MINIMAL_SHIPMENT]))

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    shipments_list = client.list_shipments(
        ShipmentListParameters(shipment_status="pending", store_id="se-521526", page_size=100),
    )

    assert shipments_list.shipments[0].shipment_id == "se-28529731"
    request = seen_requests[0]
    assert request.url.path == "/v2/shipments"
    assert request.url.params["shipment_status"] == "pending"
    assert request.url.params["store_id"] == "se-521526"
    assert request.url.params["page_size"] == "100"


def test_iter_shipments_walks_every_page() -> None:
    """The pagination helper follows ``page``/``pages`` to the end."""
    pages = {
        1: _shipments_page(1, 3, [{"shipment_id": "se-1"}]),
        2: _shipments_page(2, 3, [{"shipment_id": "se-2"}]),
        3: _shipments_page(3, 3, [{"shipment_id": "se-3"}]),
    }
    requested_pages: list[int] = []

    def handler(request: Request) -> Response:
        page = int(request.url.params["page"])
        requested_pages.append(page)
        return Response(200, json=pages[page])

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    shipment_ids = [shipment.shipment_id for shipment in client.iter_shipments()]

    assert shipment_ids == ["se-1", "se-2", "se-3"]
    assert requested_pages == [1, 2, 3]


def test_iter_shipments_does_not_mutate_the_callers_parameters() -> None:
    """The pagination helper pages on a copy of the caller's parameters."""

    def handler(_request: Request) -> Response:
        return Response(200, json=_shipments_page(1, 2, [MINIMAL_SHIPMENT]))

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    parameters = ShipmentListParameters(shipment_status="pending")
    iterator = client.iter_shipments(parameters)
    next(iterator)

    assert parameters.page is None


def test_make_request_retries_rate_limited_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 429 is retried after the ``Retry-After`` delay until a page succeeds."""
    responses = [
        Response(429, headers={"Retry-After": "7"}),
        Response(200, json={"carriers": [{"carrier_id": "se-1", "carrier_code": "ups"}]}),
    ]
    sleeps: list[float] = []
    monkeypatch.setattr("shipstation_sdk.client.time.sleep", sleeps.append)

    def handler(_request: Request) -> Response:
        return responses.pop(0)

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    carriers_list = client.list_carriers()

    assert sleeps == [7.0]
    assert carriers_list.carriers[0].carrier_code == "ups"


def test_make_request_gives_up_after_three_rate_limited_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Persistent 429s are returned to the caller after the retry budget is spent."""
    attempts: list[Request] = []
    monkeypatch.setattr("shipstation_sdk.client.time.sleep", lambda _seconds: None)

    def handler(request: Request) -> Response:
        attempts.append(request)
        return Response(429)

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    response = client.make_request("GET", "/v2/shipments")

    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert len(attempts) == RETRY_ATTEMPTS


def test_retry_after_header_is_bounded() -> None:
    """Missing, malformed, and oversized ``Retry-After`` headers are handled."""
    assert _retry_after_seconds(Response(429)) == DEFAULT_RETRY_AFTER_SECONDS
    assert _retry_after_seconds(Response(429, headers={"Retry-After": "junk"})) == DEFAULT_RETRY_AFTER_SECONDS
    assert _retry_after_seconds(Response(429, headers={"Retry-After": "3600"})) == MAX_RETRY_AFTER_SECONDS
    assert _retry_after_seconds(Response(429, headers={"Retry-After": "-1"})) == 0.0


def test_get_shipment_fetches_by_id() -> None:
    """``get_shipment`` GETs the shipment path and validates the bare body."""

    def handler(request: Request) -> Response:
        assert request.url.path == "/v2/shipments/se-28529731"
        return Response(200, json=MINIMAL_SHIPMENT)

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    shipment = client.get_shipment("se-28529731")

    assert shipment.shipment_id == "se-28529731"


def test_get_shipment_by_external_id_fetches_by_external_id() -> None:
    """``get_shipment_by_external_id`` GETs the external-id lookup path."""

    def handler(request: Request) -> Response:
        assert request.url.path == "/v2/shipments/external_shipment_id/my-order-123"
        return Response(200, json=MINIMAL_SHIPMENT)

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    shipment = client.get_shipment_by_external_id("my-order-123")

    assert shipment.shipment_id == "se-28529731"


def test_make_request_sends_json_bodies() -> None:
    """The generic escape hatch passes JSON bodies through."""

    def handler(request: Request) -> Response:
        assert json.loads(request.content) == {"example": True}
        return Response(200, json={})

    client = ShipStationClient(api_key="test-key", transport=MockTransport(handler))
    response = client.make_request("POST", "/v2/shipments", json={"example": True})

    assert response.status_code == HTTPStatus.OK
