Changelog
=========

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
