{
    'name': "ParcelBridge for DHL eCommerce Benelux",
    'summary': "Ship from Odoo through DHL eCommerce Benelux - labels on delivery validation, verify contract per destination.",
    'description': """
        ParcelBridge is a native Odoo delivery-method plugin for
        DHL eCommerce Benelux (formerly DHL Parcel Benelux). It turns
        the DHL Parcel API (api-gw.dhlparcel.nl) into a first-class
        delivery.carrier provider so shipments, labels and trackers
        flow automatically through the standard Odoo shipping workflow.

        Suitable for Odoo webshops and B2B implementations shipping
        parcels from Belgium, the Netherlands or Luxembourg to any of
        the 31 destinations supported by DHL eCommerce Benelux
        (Belgium, Netherlands, Luxembourg, Germany, France, United
        Kingdom, Austria, Italy, Spain, Portugal, Poland, Denmark,
        Sweden, Finland, Ireland, Czech Republic, Hungary, Slovenia,
        Slovakia, Romania, Bulgaria, Croatia, Greece, Estonia, Latvia,
        Lithuania, Switzerland, Norway, Liechtenstein, Monaco and
        San Marino).

        Core features
        -------------

        - Native delivery.carrier provider (delivery_type = 'dhlparcel')
          integrated with Odoo's sale orders, Add Shipping wizard,
          website checkout and backorders.
        - All DHL parcel types supported: Envelope, Mailbox parcel,
          Parcel up to 10 kg, Parcel up to 20 kg, Parcel up to 31 kg,
          Pallet up to 1000 kg. Plus Mixed and Operator-picks-at-packing
          variants for shipments that combine different parcel types
          or where the operator decides the box size at packing time.
        - International DHL products (Parcel Connect, Europlus
          International, Parcel Connect 2C, Europlus Pallet) resolved
          automatically per destination country and recipient type
          (private vs business).
        - Customs declaration auto-added for non-EU shipments
          (post-Brexit United Kingdom, Switzerland, Norway).
        - Multicollo shipments via the Number of parcels field on the
          delivery, or via native Odoo Put-in-Pack for accurate per-box
          weights. One shipment, N pieces, N trackers, one combined
          multi-page label PDF attached to the picking.
        - Recipient-aware carrier filtering: consumer-only shipping
          methods (Envelope, Mailbox parcel) hidden from business
          customers, business-only Pallet methods hidden from
          consumers. Applies in both backend Add Shipping wizard and
          webshop checkout.

        Setup and troubleshooting
        -------------------------

        - Test Connection button on the shipping method: authenticates
          with DHL, decodes the JWT token, reports account, business
          unit, active roles and token expiry.
        - Verify Contract button: probes DHL's /products endpoint for
          each enabled destination country and recipient type, and
          reports whether the DHL product this carrier would use is
          actually active on your DHL contract. Setup problems (missing
          DHL products, contract gaps) caught at setup time instead of
          on the first customer shipment.
        - Sandbox / production detection: the module decodes the JWT
          claim on every save and warns with a red banner if a test
          key ends up in a carrier meant for real shipments.
        - Debug bundle export on each delivery: one-click JSON export
          of the full DHL context (config, resolved payload, recipient,
          shipper, last error, attachments) with API credentials
          redacted. Ready to share with support to diagnose a rejected
          shipment in one round-trip.
        - Every DHL API error surfaced in the chatter and stored on
          the carrier for later inspection.

        Pricing and licensing
        ---------------------

        - Customer pricing is set on the shipping method: flat price
          or weight-based rules (the DHL Parcel API does not expose
          live rates, confirmed with DHL). For the Mixed carrier a
          per-parcel-type tariff table replaces the flat/weight rules.
        - Access control: API credentials are protected by a dedicated
          DHL Parcel Administrator group; regular shipping-managers
          can use carriers without seeing the keys.
        - Available in four languages: English, Dutch (Nederlands),
          French, German.
        - Ships with a full user guide (English and Dutch) and a
          configuration + FAQ reference. See the module homepage at
          bartvenken.be/odoo-dhl-parcelbridge for the online
          documentation.
        - OPL-1 license, source-readable, redistribution not allowed.

        Requirements
        ------------

        - Odoo 17.0, 18.0 or 19.0 (community or enterprise).
        - The stock_delivery and sale modules (shipped with Odoo).
        - An active DHL eCommerce Benelux account with API access
          activated on the contract. API access is not enabled by
          default and has to be requested from your DHL contact;
          typically granted within one business day.
        - Ships from Belgium, the Netherlands or Luxembourg.

        Not affiliated with or endorsed by DHL. DHL is a trademark of
        Deutsche Post AG.
    """,
    'author': "Bart Venken",
    'website': "https://www.bartvenken.be/odoo-dhl-parcelbridge/",
    'license': 'OPL-1',
    'category': 'Inventory/Delivery',
    'price': 149.00,
    'currency': 'EUR',
    'support': 'dhlparcel.odoo@gmail.com',
    'images': ['static/description/main_screenshot.png'],
    'version': '18.0.1.0.5',
    'depends': ['stock_delivery', 'sale'],
    'data': [
        'security/dhl_parcel_security.xml',
        'security/ir.model.access.csv',
        'views/delivery_carrier_views.xml',
        'views/stock_picking_views.xml',
        'views/choose_delivery_carrier_views.xml',
    ],
    'installable': True,
    'application': False,
}
