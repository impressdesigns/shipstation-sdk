"""Tests for the ShipStation API v2 client."""

import json
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from http import HTTPStatus
from typing import Any

import pytest
from niquests import Response

from shipstation_sdk import ShipStationClient
from shipstation_sdk.client import (
    DEFAULT_RETRY_AFTER_SECONDS,
    MAX_RETRY_AFTER_SECONDS,
    RETRY_ATTEMPTS,
    _retry_after_seconds,
)
from shipstation_sdk.parameters import ShipmentListParameters

MINIMAL_SHIPMENT: dict[str, Any] = {"shipment_id": "se-28529731", "shipment_status": "pending"}


def _response(
    status_code: int,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Response:
    """Build a niquests Response without touching the network."""
    response = Response()
    response.status_code = status_code
    response._content = json.dumps(body or {}).encode()  # noqa: SLF001 -- no public way to seed a canned body
    response.headers.update(headers or {})
    return response


class _SessionRecorder:
    """Stand-in for ``Session.request`` serving canned responses and recording calls."""

    def __init__(self, responses: list[Response]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> Response:  # noqa: ANN401 -- mirrors Session.request's open signature
        self.calls.append(kwargs)
        return self.responses.pop(0)


def _record(client: ShipStationClient, monkeypatch: pytest.MonkeyPatch, responses: list[Response]) -> _SessionRecorder:
    """Route the client's session requests through a recorder."""
    recorder = _SessionRecorder(responses)
    monkeypatch.setattr(client.session, "request", recorder.request)
    return recorder


def _shipments_page(page: int, pages: int, shipments: list[dict[str, Any]]) -> Response:
    """Build a shipments list response."""
    return _response(200, {"shipments": shipments, "total": len(shipments) * pages, "page": page, "pages": pages})


def test_session_carries_the_api_key_header() -> None:
    """The session authenticates every request with the ``api-key`` header."""
    client = ShipStationClient(api_key="test-key")

    assert client.session.headers["api-key"] == "test-key"


def test_list_shipments_sends_parameters_as_query_params(monkeypatch: pytest.MonkeyPatch) -> None:
    """List parameters serialize 1:1 onto the ``/v2/shipments`` query params."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_shipments_page(1, 1, [MINIMAL_SHIPMENT])])

    shipments_list = client.list_shipments(
        ShipmentListParameters(shipment_status="pending", store_id="se-521526", page_size=100),
    )

    assert shipments_list.shipments[0].shipment_id == "se-28529731"
    call = recorder.calls[0]
    assert call["method"] == "GET"
    assert call["url"] == "/v2/shipments"
    assert call["params"] == {"shipment_status": "pending", "store_id": "se-521526", "page_size": 100}


def test_iter_shipments_walks_every_page(monkeypatch: pytest.MonkeyPatch) -> None:
    """The pagination helper follows ``page``/``pages`` to the end."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(
        client,
        monkeypatch,
        [
            _shipments_page(1, 3, [{"shipment_id": "se-1"}]),
            _shipments_page(2, 3, [{"shipment_id": "se-2"}]),
            _shipments_page(3, 3, [{"shipment_id": "se-3"}]),
        ],
    )

    shipment_ids = [shipment.shipment_id for shipment in client.iter_shipments()]

    assert shipment_ids == ["se-1", "se-2", "se-3"]
    assert [call["params"]["page"] for call in recorder.calls] == [1, 2, 3]


def test_iter_shipments_does_not_mutate_the_callers_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    """The pagination helper pages on a copy of the caller's parameters."""
    client = ShipStationClient(api_key="test-key")
    _record(client, monkeypatch, [_shipments_page(1, 2, [MINIMAL_SHIPMENT])])
    parameters = ShipmentListParameters(shipment_status="pending")

    next(client.iter_shipments(parameters))

    assert parameters.page is None


def test_make_request_retries_rate_limited_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 429 is retried after the ``Retry-After`` delay until a request succeeds."""
    sleeps: list[float] = []
    monkeypatch.setattr("shipstation_sdk.client.time.sleep", sleeps.append)
    client = ShipStationClient(api_key="test-key")
    _record(
        client,
        monkeypatch,
        [
            _response(429, headers={"Retry-After": "7"}),
            _response(200, {"carriers": [{"carrier_id": "se-1", "carrier_code": "ups"}]}),
        ],
    )

    carriers_list = client.list_carriers()

    assert sleeps == [7.0]
    assert carriers_list.carriers[0].carrier_code == "ups"


def test_make_request_gives_up_after_three_rate_limited_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Persistent 429s are returned to the caller after the retry budget is spent."""
    monkeypatch.setattr("shipstation_sdk.client.time.sleep", lambda _seconds: None)
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_response(429) for _ in range(RETRY_ATTEMPTS)])

    response = client.make_request("GET", "/v2/shipments")

    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert len(recorder.calls) == RETRY_ATTEMPTS


def test_retry_after_header_is_bounded() -> None:
    """Missing, malformed, and oversized ``Retry-After`` headers are handled."""
    assert _retry_after_seconds(_response(429)) == DEFAULT_RETRY_AFTER_SECONDS
    assert _retry_after_seconds(_response(429, headers={"Retry-After": "junk"})) == DEFAULT_RETRY_AFTER_SECONDS
    assert _retry_after_seconds(_response(429, headers={"Retry-After": "3600"})) == MAX_RETRY_AFTER_SECONDS
    assert _retry_after_seconds(_response(429, headers={"Retry-After": "-1"})) == 0.0


def test_get_shipment_fetches_by_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """``get_shipment`` GETs the shipment path and validates the bare body."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_response(200, MINIMAL_SHIPMENT)])

    shipment = client.get_shipment("se-28529731")

    assert shipment.shipment_id == "se-28529731"
    assert recorder.calls[0]["url"] == "/v2/shipments/se-28529731"


def test_get_shipment_by_external_id_fetches_by_external_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """``get_shipment_by_external_id`` GETs the external-id lookup path."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_response(200, MINIMAL_SHIPMENT)])

    shipment = client.get_shipment_by_external_id("my-order-123")

    assert shipment.shipment_id == "se-28529731"
    assert recorder.calls[0]["url"] == "/v2/shipments/external_shipment_id/my-order-123"


def test_get_shipment_by_external_id_escapes_url_metacharacters(monkeypatch: pytest.MonkeyPatch) -> None:
    """Caller-defined external IDs (e.g. marketplace ``gid://...``) are path-escaped."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_response(200, MINIMAL_SHIPMENT)])

    client.get_shipment_by_external_id("gid://shopify/Order/1?x=1#frag")

    assert recorder.calls[0]["url"] == (
        "/v2/shipments/external_shipment_id/gid%3A%2F%2Fshopify%2FOrder%2F1%3Fx%3D1%23frag"
    )


def test_list_shipments_serializes_the_tag_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ``tag`` filter (documented in the list-shipments guide) reaches the query params."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_shipments_page(1, 1, [MINIMAL_SHIPMENT])])

    client.list_shipments(ShipmentListParameters(tag="Rush"))

    assert recorder.calls[0]["params"] == {"tag": "Rush"}


def test_make_request_passes_json_bodies_through(monkeypatch: pytest.MonkeyPatch) -> None:
    """The generic escape hatch passes JSON bodies through untouched."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_response(200)])

    response = client.make_request("POST", "/v2/shipments", json={"example": True})

    assert response.status_code == HTTPStatus.OK
    assert recorder.calls[0]["json"] == {"example": True}


def test_retry_after_accepts_an_http_date() -> None:
    """RFC 9110 allows an HTTP-date ``Retry-After``; it converts to a bounded delay."""
    future = format_datetime(datetime.now(tz=UTC) + timedelta(seconds=30), usegmt=True)
    past = format_datetime(datetime.now(tz=UTC) - timedelta(seconds=30), usegmt=True)

    future_delay = _retry_after_seconds(_response(429, headers={"Retry-After": future}))
    past_delay = _retry_after_seconds(_response(429, headers={"Retry-After": past}))

    assert 20.0 < future_delay <= 30.0
    assert past_delay == 0.0


def test_list_tags_fetches_the_account_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    """``list_tags`` GETs the tags path and validates the envelope."""
    client = ShipStationClient(api_key="test-key")
    recorder = _record(client, monkeypatch, [_response(200, {"tags": [{"name": "Rush"}]})])

    tags_list = client.list_tags()

    assert recorder.calls[0]["method"] == "GET"
    assert recorder.calls[0]["url"] == "/v2/tags"
    assert [tag.name for tag in tags_list.tags] == ["Rush"]
