# Labels & Tracking for DHL eCommerce Benelux

Odoo delivery-method module for DHL eCommerce Benelux. Creates the DHL label
and tracker(s) when a delivery is validated in Odoo.

This branch is for **Odoo 19.0**. Other branches:
[17.0](https://github.com/bartvenken/odoo-dhl-parcelbridge/tree/17.0),
[18.0](https://github.com/bartvenken/odoo-dhl-parcelbridge/tree/18.0),
[19.0](https://github.com/bartvenken/odoo-dhl-parcelbridge/tree/19.0).

## What it does

- Native `delivery.carrier` provider integrated with sale orders, Add Shipping
  wizard, website checkout and backorders.
- All DHL parcel types: Envelope, Mailbox parcel, Parcel up to 10 / 20 / 31 kg,
  Pallet up to 1000 kg. Plus Mixed and Operator-picks-at-packing variants.
- International DHL products (Parcel Connect, Europlus International, Parcel
  Connect 2C, Europlus Pallet) resolved automatically per destination country
  and recipient type.
- Customs declaration added automatically for non-EU shipments (United
  Kingdom, Switzerland, Norway).
- Multicollo via the Number of parcels field on the delivery, or via native
  Put in Pack for per-box weights.
- Recipient-aware carrier filtering.
- Test Connection and Verify Contract buttons on the carrier form.
- Debug bundle export with credentials redacted.
- Available in English, Dutch, French and German.
- OPL-1 license.

## Requirements

- Odoo 19.0 (community or enterprise) with `stock_delivery` and `sale`.
- An active DHL eCommerce Benelux account with API access activated on the
  contract.
- Sender in Belgium, the Netherlands or Luxembourg.

## Where to get it

Available on the Odoo Apps Store:
https://apps.odoo.com/apps/modules/19.0/parcelbridge_dhl_benelux

Price: 49 EUR. License: OPL-1.

## Documentation

- User guide (English): https://www.bartvenken.be/odoo-dhl-parcelbridge/guide.html
- Handleiding (Nederlands): https://www.bartvenken.be/odoo-dhl-parcelbridge/handleiding.html
- Configuration and FAQ (English): https://www.bartvenken.be/odoo-dhl-parcelbridge/faq.html
- Configuratie en FAQ (Nederlands): https://www.bartvenken.be/odoo-dhl-parcelbridge/faq-nl.html

## Contact

dhlparcel.odoo@gmail.com
