Changelog
=========

- :release:`1.5.0 <21st October 2026>`
- :feature:`-` Track packages: ``start_tracking`` and ``stop_tracking`` subscribe to and unsubscribe
  from a package's tracking updates, and ``get_tracking`` reads its status and events as a
  ``TrackingInfo`` (with ``TrackEvent`` events)
- :feature:`-` ``TrackWebhookEvent`` reads the body of a ``track`` (``API_TRACK``) or
  ``track_event_v2`` (``TRACK_EVENT_V2``) webhook call

- :release:`1.4.0 <20th October 2026>`
- :feature:`-` Every field ShipStation API v2 documents is on the SDK's models: shipments (customs,
  tax identifiers, batch ids), advanced options, addresses (geolocation), packages (products, with
  dangerous goods and CPSC details), labels (downloads, refund details, rate details, delivery
  prediction, the shipment), label packages, carriers (services, package types, options) and the
  carriers list envelope
- :feature:`-` ``Shipment.packages``, ``Shipment.customs`` and ``Shipment.tax_identifiers`` are
  models instead of dicts; ``customs_item_id``, like ``shipment_package_id``, is read but never sent
- :feature:`-` ``ShipmentRequest`` and ``ShipmentRequestItem`` take every documented writable field,
  including ``validate_address``; fields left ``None`` still stay off the wire
- :feature:`-` A created shipment reads its ``address_validation`` and its errors as the strings
  ShipStation documents; a webhook reads the integer ``store_id`` ShipStation documents

- :release:`1.3.0 <20th October 2026>`
- :feature:`-` ``Package`` carries every field ShipStation documents for a shipment's package
  (dimensions, label messages, external package id, insured value, content description, products),
  so a shipment read back and sent again keeps them
- :feature:`-` ``Label.packages``: each package's tracking number, sequence and external package id

- :release:`1.2.0 <9th October 2026>`
- :feature:`-` ``ShipmentRequest.create_sales_order``, which a new shipment needs to show in
  ShipStation's Orders tab

- :release:`1.1.0 <8th October 2026>`
- :feature:`-` Create shipments and update a shipment that has no label yet
- :feature:`-` List and iterate labels, and follow a ``label_created_v2`` webhook's
  ``resource_url`` (refused unless it is a labels list on ``api.shipstation.com``)
- :feature:`-` List webhooks and create one, with the headers ShipStation sends on every call

- :release:`1.0.0 <8th July 2026>`
- :feature:`-` Rewrite as a ShipStation API v2 client: ``api-key`` header auth against
  ``https://api.shipstation.com``, shipments list/get/iterate (v2 shipments are v1 orders),
  connected-carrier and tag listing, and rate-limit-aware retries
- :feature:`-` Remove every v1 (legacy) endpoint and model, including orders and the
  ``America/Los_Angeles`` datetime handling; v1 consumers should pin ``<1``
- :feature:`-` HTTP via Niquests instead of HTTPX, matching the in-house SDKs

- :release:`0.8.0 <30th January 2026>`
- :bug:`-` Item option name is nullable
- :bug:`-` Order user ID is a string

- :release:`0.7.1 <14th October 2025>`
- :bug:`-` Item SKU is nullable

- :release:`0.7.0 <13th October 2025>`
- :feature:`-` Add support for all query parameters
- :feature:`-` Add support for fetching a specific order

- :release:`0.6.0 <1st July 2025>`
- :feature:`-` Fixup order to type to match current API response

- :release:`0.5.0 <18th June 2025>`
- :feature:`-` Set the timezone on ``shipment.create_date``
- :feature:`-` Parse ``shipment.ship_date`` as a date

- :release:`0.4.0 <29th May 2025>`
- :feature:`-` Fix various data types

- :release:`0.3.0 <28th May 2025>`
- :feature:`-` Add support for fetching orders

- :release:`0.2.0 <13th May 2025>`
- :feature:`-` Make ``shipment.create_date`` an actual datetime field

- :release:`0.1.0 <6th May 2025>`
- :feature:`-` Initial release
