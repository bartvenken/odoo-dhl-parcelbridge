# ParcelBridge for DHL eCommerce Benelux - User Guide

This guide covers how to install, configure and use the
**ParcelBridge for DHL eCommerce Benelux** module in the day-to-day
Odoo workflow.

> **Module version:** 17.0.1.0.0 / 18.0.1.0.0 / 19.0.1.0.0 (functionally identical)
> **For Odoo:** 17.0 / 18.0 / 19.0 (community and enterprise)

---

## Contents

1. [Introduction](#1-introduction)
2. [Quick start](#2-quick-start)
3. [Concepts](#3-concepts)
4. [What you need on the DHL side](#4-what-you-need-on-the-dhl-side)
5. [Installation](#5-installation)
6. [Creating shipping methods](#6-creating-shipping-methods)
7. [Pricing](#7-pricing)
8. [Daily workflow](#8-daily-workflow)
9. [Multicollo (multiple parcels in one shipment)](#9-multicollo-multiple-parcels-in-one-shipment)
10. [Put in Pack explained](#10-put-in-pack-explained)
11. [Label and tracking](#11-label-and-tracking)
12. [Cancelling](#12-cancelling)
13. [When things go wrong](#13-when-things-go-wrong)
14. [Languages](#14-languages)
15. [Short FAQ](#15-short-faq)

---

## 1. Introduction

This module connects Odoo to **DHL eCommerce Benelux** through the API
at `api-gw.dhlparcel.nl`. When you validate a delivery
(`stock.picking`) in Odoo, the module automatically creates a shipment
with DHL, fetches the shipping label as a PDF, attaches it to the
delivery, and stores the tracking codes on the picking.

The module supports:

- **Outbound from BE, NL and LU** to 31 European destinations.
- **Returns** from the same 31 countries back to your Benelux warehouse.
- **Multicollo**: one order = one DHL shipment with N parcels (one
  multi-page PDF and N trackers).
- **Mixed shipments**: different parcel types within one shipment.
- **Two carrier-level pricing modes**: flat price (`flat`) or
  weight-based tier (`rule`), chosen via the **DHL pricing mode**
  field. MIX carriers additionally use a per-type tariff table on the
  DHL Tariffs tab.

The module does not:

- **Fetch live rates** - the DHL Parcel gateway has no rate endpoint.
  You configure prices on the carrier itself.
- **Cancel shipments via the API** - DHL's public API offers no cancel
  endpoint. Cancellation happens in the My DHL Parcel portal (see
  chapter 12).
- **Ship from countries outside BE/NL/LU** - that requires a different
  DHL contract and a different module.

---

## 2. Quick start

For those who want to get started immediately. Five steps from zero to
your first label:

1. **Install** the module via Apps → search *ParcelBridge for DHL* →
   Install.
2. Go to **Inventory → Configuration → Shipping Methods → New**.
3. Provider = **ParcelBridge for DHL eCommerce Benelux**. A "DHL Parcel" tab appears.
4. On that tab: fill in **User ID**, **API Key**, **Account ID** (see
   section 4 for where to get them). Pick a **Parcel type** (e.g.
   *Parcel up to 10kg*) and set a **Flat price**. Select **Countries**
   (the list is automatically restricted to the 31 supported
   destinations).
5. On your first real order: click **Add Shipping**, pick this method,
   confirm the order, go to the generated delivery, **Validate** - DHL
   creates the label and you find the PDF attached to the delivery.
   Done.

For the full explanation and advanced usage: read on.

---

## 3. Concepts

Three ideas that make the module clearer:

### One shipping method per parcel type

DHL has six parcel types (Envelope, Mailbox parcel, Parcel up to 10kg,
up to 20kg, up to 31kg, Pallet up to 1000kg). The module follows the
Odoo pattern of *"one shipping method per distinct product"*: for each
parcel type you want to offer, you create a separate shipping method.
The type choice therefore happens when picking the shipping method,
not later in the flow.

For the exceptional case where you want to combine different parcel
types in **one shipment**, there is the special **Mixed** (MIX)
option, see sections 6 and 9.

### Multicollo

One Odoo delivery always becomes one DHL shipment, even if that
shipment consists of multiple parcels. DHL then returns one tracker
per parcel and **one multi-page PDF** containing all labels. That's
what "multicollo" means.

The number of parcels can be determined in two ways - see section 9.

### Prices are computed locally

DHL's API does not return prices. The price appearing on the order
comes from the carrier configuration: flat price, weight tier, or (for
MIX) a table of tariffs per parcel type.

---

## 4. What you need on the DHL side

### A DHL eCommerce Benelux account

The kind of contract you need is called **DHL eCommerce Benelux**.
Other DHL branches (DHL Express, DHL Parcel DE, ...) don't work with
this module.

### API credentials

Two steps are needed: **first** DHL has to activate API access on your
account, **then** you create the credentials yourself in the portal.

#### Step 1 - DHL has to grant the API role on your account

API access is not a standard part of a DHL eCommerce Benelux account.
Before you can create an API key in the portal, your DHL contact (or
DHL eCommerce support) has to grant the **API role** on your account.
This happens manually on DHL's side - you can't force it yourself.

How to request it:

- Email your DHL account manager or DHL eCommerce support.
- Mention your DHL customer number (the same number that will later
  become your Account ID).
- Explicitly ask to activate "API access" / "the API role" on your
  account so you can create API keys via the portal.

Until DHL confirms the role is granted, the portal only shows a
"Connections" page - no API Keys section. That's the signal that step 1
is not yet done.

#### Step 2 - Create an API key in the My DHL Parcel portal

Once DHL has granted the role: log into the My DHL Parcel portal and
go to **Settings → API Keys**. Here you create your credentials and
copy three values:

- **User ID** - a UUID like `87dcdd1b-0999-4d96-afaa-09f16a201263`
- **API Key** - a UUID
- **Account ID** - your short DHL customer number, e.g. `40051608`

You'll later enter these three values on the DHL Parcel tab of the
shipping method in Odoo.

### Required JWT role: `label-service.B2X`

The API key must contain this role in its JWT token to be able to
create labels. If you get `"DHL Parcel rejected the shipment"` errors
that mention permissions, this is the first thing to have DHL verify.

### Optional items (per feature)

| Feature | What DHL has to provide |
|---|---|
| Cancellation via API | Not supported by the public API - only via the portal |
| International routes (Parcel Connect, Europlus International) | The correct contract products (CON / EPL-INT / EPL-PAL) |
| Returns (`returnLabel: true`) | The corresponding return product (DFY-RETURN / EPL-RETURN / RETURN-CON) |

### What absolutely does NOT work via the API

- **Live rates**. Confirmed by DHL: their gateway has no rate
  endpoint. Tariffs can only be viewed in the portal (with the
  *Rate Manager* role). You're responsible for prices on the Odoo
  carrier yourself.
- **Address book export**. The address book in My DHL Parcel is not
  accessible via the API.
- **Shipment history queries**. The gateway is transactional (create
  a label, fetch one shipment), not for historical queries.

---

## 5. Installation

### Requirements

- Odoo 17, 18 or 19 (community or enterprise)
- The `stock_delivery` and `sale` modules (shipped with Odoo). These transitively pull in `sale_stock`, `stock`, `product` and `delivery` if not yet installed - the module brings its own dependency chain.
- Internet access to `api-gw.dhlparcel.nl`

### Installing

Two options:

**From the Odoo UI:** Apps → Update Apps List → search *ParcelBridge
for DHL* → click Install.

**From the command line:**
```bash
odoo-bin -d <database> -i parcelbridge_dhl_benelux
```

### Optional but recommended: enable the Packages feature

If you want to do multicollo via Put in Pack (and not just via the
*Number of parcels* field), enable the Packages feature:

**Inventory → Configuration → Settings → Operations → Packages → Save.**

Without this setting, the "Put in Pack" button is not visible on
deliveries.

### Upgrading the module after an update

Whenever you pull a new version of the module (git pull or marketplace
update), go to **Apps → ParcelBridge for DHL eCommerce Benelux → Upgrade**. A regular server restart isn't enough if new fields or models were
added.

### Access control: who can see the API credentials?

The three credential fields (User ID, API Key, Account ID) are
protected via a dedicated group **DHL Parcel Administrator**. Odoo
admins get this group automatically upon install.

**What this means concretely:**

- **Members** of the group (admin + added users): see the credentials
  on the carrier form, can edit them via UI, XML-RPC and ORM.
- **Non-members** (e.g. a dedicated shipping manager without admin
  rights): do **not** see the 3 credential fields on the form. A
  direct XML-RPC/ORM request on those fields returns a clear security
  error mentioning the required group.
- Internal module flows (validate delivery, fetch label PDF, Test
  Connection by the admin, debug bundle export) keep working for
  everyone - the module uses `sudo()` internally for credential reads,
  so the operator doesn't need to "know" the creds to create shipments.

**Adding extra users to the group:**

**Settings → Users & Companies → Users → *[the user]* → Access Rights
→ tab *Other* → check *DHL Parcel Administrator* → Save.**

Downsides of the restriction: if you have a dedicated shipping manager
who wants to configure carriers themselves, you must explicitly add
that user to the group. To avoid that step, just give the user admin
rights - although a separate group is cleaner in terms of auditability.

---

## 6. Creating shipping methods

### Publish rule: frontend vs backend

Before you start: understand the difference between carriers that the
customer picks via the webshop and carriers used only internally.

- **Frontend / webshop carriers** (customers pick them themselves at
  checkout) **MUST be published**. Set the toggle at the top of the
  carrier form to **Published**. Without it, the method doesn't appear
  in the checkout list, even if you configure its Website field
  correctly.

- **Backend-only carriers** (you or the warehouse picks them via Add
  Shipping on a sale order or picking) **MUST NOT be published**.
  Unpublished carriers are simply available in the backend via the Add
  Shipping wizard. Publishing them makes them *also* visible in the
  webshop, where they don't belong.

Practically: if you have a carrier you deliberately want only an
operator to pick (e.g. an expensive Express option that you add
manually for important B2B customers), leave it Unpublished.

**Special case - MIX carriers CAN'T be published.** The module
blocks publishing on MIX because customers cannot fill in the
per-parcel table at checkout. Want a single webshop carrier where the
operator later picks the type? Use a carrier with parcel type =
**Operator picks at packing** (OPEN) - that one can be published. See
also section 9, Option 4.

### Strategy: one method per parcel type + optionally a MIX

For the common case, you create one Odoo shipping method per DHL
parcel type you want to offer. Customers (or you in the backend) then
pick the method matching the desired parcel category.

A typical webshop configuration:

- **DHL Mailbox parcel** (XSMALL, BE+NL)
- **DHL Parcel up to 10kg** (SMALL, all 31 destinations)
- **DHL Parcel up to 20kg** (SMALL_MEDIUM)
- **DHL Parcel up to 31kg** (MEDIUM)
- **DHL Pallet** (PALLET, business only)

For B2B customers where one shipment often contains multiple parcel
types: add a **DHL Mixed** method as well, see further.

### Creating a method - step by step

1. Go to **Inventory → Configuration → Shipping Methods → New**.
2. Give the method a recognisable name (e.g. *DHL Parcel up to 10kg*).
3. Provider = **ParcelBridge for DHL eCommerce Benelux**. A **DHL Parcel** tab appears.
4. On the DHL Parcel tab:
   - **Credentials** - User ID, API Key, Account ID. The same three
     values for all your DHL methods if they share the same DHL
     account. Multi-account setups: fill in the correct creds per
     method.
   - **Parcel type** - pick the DHL category (e.g. *Parcel up to
     10kg*) or **Mixed** for a mix method.
   - **Default weight (kg)** - fallback weight when a parcel has no
     weight. Default is 1 kg. DHL rejects a 0 kg shipment, so this
     field prevents that.
   - **Pricing mode** + **DHL flat price** or **Pricing rules** - see
     section 7.
5. **Integration Level** (on the main section of the carrier): leave
   on **Get Rate and Create Shipment**. With *Get Rate* only, no label
   is created on Validate.
6. **Countries**: pick the destinations. The dropdown is automatically
   restricted to the 31 supported destinations, and further narrowed
   based on the picked parcel type:
   - Envelope → NL only
   - Mailbox parcel → BE + NL only
   - Parcel / Pallet → all 31
7. Optional: **Website**. Bind the method to one webshop, or leave
   empty to make it available everywhere.
8. **Delivery Product** - Odoo requires a product that represents the
   shipping cost on the order. Create one (e.g. *DHL Shipping Cost*)
   or reuse an existing shipping product. Make sure the product has
   **no specific Company** (leave that field empty) unless you want to
   work per company.
9. **Save**.

### Verifying contract coverage

After saving a method: click **Verify Contract** in the *Contract
check* section. The module then does a live probe against DHL's
`/products` endpoint for each selected destination country and each
relevant recipient type (consumer / business). The report shows per
route which DHL product the module would use (DFY / CON / EPL-INT /
CON2C / EPL-PAL) and whether that product is effectively active on
your DHL contract.

- **OK** - the route is covered.
- **NOT IN CONTRACT** - the product isn't in your contract; that route
  will fail on label creation. Resolve by asking your DHL contact to
  activate the product, or uncheck the country on your carrier.
- **ERROR** - the probe couldn't get an answer from DHL (network
  problem, invalid credentials, ...).

Repeat this check after any contract change on DHL's side, or when in
doubt whether a newly added destination actually works.

This is a read-only call. No shipment is created and nothing is logged
in the DHL portal beyond the usual API authentications.

### For MIX: parcel type = Mixed

Specifically for the MIX method:

- The **Countries** list shows all 31 destinations (no type
  restriction at the carrier level, because types are picked per
  parcel).
- **Pricing mode** and **Flat price** are hidden - a MIX method always
  uses the tariff table.
- An **extra notebook tab "DHL Tariffs"** appears: fill in the price
  you charge customers for each parcel type (from your DHL rate card).
  The six types are added automatically when you pick "Mixed".

---

## 7. Pricing

The DHL Parcel API doesn't return prices. The price on the order is
computed locally based on what you configure on the carrier.

Three modes:

### Flat price

One fixed price per shipment, regardless of weight or number of
parcels. Good for B2C webshops with simple pricing.

**Configuration:** Pricing mode = **Flat price**, and fill in **DHL
flat price** (e.g. €4.85).

### Weight-based rules

Weight tier: you define prices based on the total weight of the
shipment. Below each threshold = price X, above = price Y, etc.

**Configuration:** Pricing mode = **Weight-based rules**. On the
**Pricing** tab you define price-rules with `weight` as the variable.

Example:
| Variable | Operator | Value | Price |
|---|---|---|---|
| weight | <= | 2 | 4.85 |
| weight | <= | 10 | 6.50 |
| weight | <= | 20 | 9.80 |

### Per-type tariff (MIX only)

For a MIX carrier the shipping cost is computed as
`sum(quantity × tariff_for_type)` over all parcels on the delivery.
You set the tariffs in the **DHL Tariffs** tab on the carrier.

**Workflow**:
1. Enter the tariffs on the carrier (once, e.g. €4.85 for Mailbox
   parcel).
2. Order gets a MIX carrier via Add Shipping → price is initially 0
   (no parcels defined yet on the delivery).
3. Warehouse fills in the DHL Parcels tab on the delivery.
4. Go back to the order, click **Add Shipping** again → the price is
   updated based on the filled parcels.
5. Validate the delivery.

> ⚠ This requires back-and-forth between SO and delivery because the
> price is only known after the warehouse work. For the simple
> *Number of parcels* flow this isn't needed - the price is fixed at
> Add Shipping there.

---

## 8. Daily workflow

Three typical scenarios:

### A. Webshop B2C (fully automatic)

1. Customer places order in the webshop, picks a DHL method at
   checkout.
2. Order automatically gets a delivery line with the correct price and
   `carrier_id` set.
3. On confirmation of the order, the generated delivery gets the same
   carrier.
4. Warehouse picks and validates the delivery → label is created.

No extra clicks needed - the Add Shipping step is implicit in
checkout.

### B. Backend B2B with prepaid shipping (Add Shipping on the order)

1. Salesperson creates SO in the backend.
2. Click **Add Shipping** on the SO → pick the right DHL method →
   wizard adds a delivery line with the price.
3. Confirm the SO → delivery is created with the same carrier.
4. Warehouse picks and validates → label is created.

For uniform shipments (one parcel type, one or more identical
parcels): optionally set **Number of parcels** on the delivery before
Validate.

### C. Backend B2B with post-shipment invoicing

Some B2B customers are invoiced after shipping. You can then skip Add
Shipping entirely:

1. SO has no carrier and no shipping line.
2. Warehouse opens the delivery, sets the **Carrier** in the
   *Additional Info* tab.
3. Optionally fills in **Number of parcels** or the DHL Parcels tab.
4. Validates → label is created.
5. Shipping cost is added manually to the final invoice.

> Note: in this flow there is no shipping-cost line on the SO. If you
> later still do Add Shipping on the SO, it might pick a different
> carrier than what's on the picking. Keep discipline or work
> consistently in one flow.

---

## 9. Multicollo (multiple parcels in one shipment)

There are four ways to indicate that a delivery consists of multiple
parcels. Which one you use depends on the situation.

**Precedence rule:** as soon as you've used **Put in Pack** on the
delivery (so `package_ids` exist on the picking), those packages are
followed - the field **Number of parcels** is then ignored. If you
didn't do Put in Pack, **Number of parcels** counts. A MIX or OPEN
carrier overrules both via the DHL Parcels tab.

### Option 1: Number of parcels (simplest, identical parcels)

**When:** you're shipping N identical parcels of the carrier type.
E.g. *3 mailbox parcels* or *2 Parcels up to 10kg*. Doesn't matter
which item is in which parcel (books, DVDs, ...).

**How:** on the delivery you see a **Number of parcels** field next to
the Carrier. Default 1. Set it to e.g. `3` and save.

**Result:** One DHL shipment with 3 pieces, all of the carrier type.
DHL returns 3 trackers and one multi-page PDF with 3 labels. Weight
per piece = total weight / N, with fallback to the carrier default if
products have no weight.

### Option 2: Put in Pack (mixed contents, identical type, per-box weight)

**When:** you want to put specific items in specific boxes (e.g.
fragile items separately), or you want to specify an **exact weight**
per box (operator weighs each box on the scale). All boxes are of the
same type.

**How:** see section 10.

**Result:** one DHL piece per real package, with the weight of that
package. The Number of parcels field is ignored.

### Option 3: MIX carrier + DHL Parcels tab (different types)

**When:** you need different parcel types in one shipment. E.g. 2
mailbox parcels + 1 parcel up to 10kg in one delivery.

**How:**
1. Use a **MIX carrier** (parcel type = Mixed).
2. On the delivery a **DHL Parcels** tab appears. Add one row per
   parcel: type + quantity + (optional) weight.
3. The type list adapts automatically: a private recipient sees
   Envelope/Mailbox/Parcel; a business recipient sees Parcel/Pallet.
4. Validate → DHL creates one shipment with the specified pieces.

**Not available on the webshop**: a MIX carrier cannot be published -
customers can't fill in that table.

### Option 4: OPEN carrier (one webshop price, type picked at packing)

**When:** you want to offer a single webshop shipping method with one
price, and let the operator decide at packing which parcel type is
physically used.

**How:**
1. Use a carrier with parcel type = **Operator picks at packing**
   (OPEN). Can be published on the webshop.
2. Customer picks this carrier at checkout, pays the flat/weight
   price.
3. When packing, the operator fills in the **DHL Parcels tab** on the
   picking (one row is enough for one box; more rows for more boxes).
4. Validate → DHL shipment with the pieces specified in the tab.

Same mechanism as MIX, but publish-mode is allowed and there is no
recipient restriction (both consumer and business customers see the
option).

**What the customer does NOT see:** there is no parcel-type dropdown
at checkout. The customer only sees your carrier name and the price,
and pays. The name "Operator picks at packing" refers to the operator
- not the customer. The type choice is *open until packing*, where
the operator fills it in. For the customer, this is invisible and
gives the impression of a standard flat-fee shipping.

---

## 10. Put in Pack explained

**Put in Pack** is Odoo's mechanism to organise the items of a
delivery into one or more *packages* (boxes). For our module you use
it to indicate *which specific items go into which specific box*.

### How it works

A delivery has one or more **move lines**: the rows saying "X units of
product Y". At the top of the delivery you see these rows with a
*Demand* (requested quantity) and a *Done* (actual picked quantity).

When you click **Put in Pack**:
1. Odoo takes **all current Done quantities** that aren't in a package
   yet.
2. Makes one `stock.quant.package` (package) out of them.
3. Attaches that package to the move lines.

A Done = 0 on a line means: that line does not (yet) go into this
package.

### Example - 1 package with everything

You have a delivery with 5× *Book A* and 3× *Book B*. Both rows have
Done = 5 and Done = 3 (default: everything is "ready"). One click on
Put in Pack → all 8 items go into pack 1. Done.

### Example - 2 packages with distributed items

You want 3× Book A in package 1, and 2× Book A + 3× Book B in package
2.

1. Open the delivery, go to **Detailed Operations** (or click on the
   row to see the quantities).
2. On the Book A row: set **Done** to `3` (instead of the full 5).
3. On the Book B row: set **Done** to `0`.
4. Click **Put in Pack** → pack 1 is created with 3× Book A.
5. Now set **Done** = `2` (the remainder) on the Book A row, and
   Book B = `3`.
6. Click **Put in Pack** → pack 2 with 2× Book A + 3× Book B.

### Common error

> **"Invalid Operation: There is nothing eligible to put in a pack."**

This means: there are currently no Done quantities that aren't already
in a package. Solution: go to Detailed Operations and set some extra
Done on the rows you want to put in a next package.

### When NOT to use Put in Pack

- **All packages are identical in content-type**: just use *Number of
  parcels* on the delivery. Much less clicking.
- **Different parcel types in one shipment**: use a MIX carrier + the
  DHL Parcels tab. There you specify a type per parcel, without Put in
  Pack.

### What the module does with packages

When you Validate, the module decides in this order:

1. **MIX or OPEN carrier** → one piece per row in the DHL Parcels tab,
   with the type and quantity from the row. Number of parcels and Put
   in Pack are not used in this case.
2. **Fixed-type carrier with Put in Pack** (`picking.package_ids`
   exists): one piece per real package, with the carrier type and the
   weight of that package. The Number of parcels field is ignored.
3. **Fixed-type carrier without Put in Pack**: one piece with
   `quantity = Number of parcels` (default 1) and weight = total
   weight / N (or the carrier default if there's no product weight).

The choice between 2 and 3 is simply: did you click Put in Pack? If
yes, packages win. If not, the count field applies.

---

## 11. Label and tracking

When you validate a DHL delivery:

1. The module calls the DHL API to create the shipment.
2. DHL returns a **trackerCode** per piece.
3. The module fetches the label (PDF).
4. **The PDF is attached to the delivery.** One PDF, even for
   multicollo (all labels are in the same multi-page PDF).
5. **The tracker codes** land on `carrier_tracking_ref` of the picking
   (comma-separated for multiple pieces).

Finding the label: open the delivery → "Documents" tab or the
paperclip icon → the PDF is typically named `DHL-<shipmentId>.pdf`.
Print and stick on the boxes.

Track & trace for your customer: DHL's public tracker page is
`https://my.dhlecommerce.nl/home/tracktrace/<trackerCode>/<postcode>`.
**Important**: since mid-2025 DHL requires both the tracker code and
the **recipient postcode** - both are in the URL. The old
`dhlparcel.nl/consument/traceer-uw-zending?tt=...` URL no longer
works.

The module uses this URL automatically in
`dhlparcel_get_tracking_link` (the link that appears in the portal
email to your customer); you don't need to do anything yourself unless
your customer manually tracks.

---

## 12. Cancelling

> **Cancellation always happens in the My DHL Parcel portal.**
> DHL's public API offers no endpoint to programmatically cancel
> shipments. Their OpenAPI spec only has a read-only
> `GET /intervention-options` to check whether a cancel would be
> allowed, but no POST to actually execute the cancel. This is not a
> temporary limitation - it is the design of the Business API.

The cancel action in Odoo:

- Posts a chatter note on the delivery with the instruction to cancel
  in the portal. Important: the note contains the **tracking code
  before it is wiped**, so you can still retrieve it from the chatter.
- Odoo's standard cancel flow then wipes the `carrier_tracking_ref`
  field on the picking (that's core behaviour, not something the
  module does).
- Does not call the DHL API.

**What you must do:** log into My DHL Parcel, copy the tracker code
from the chatter note of the delivery, find the shipment there, and
cancel it.

---

## 13. When things go wrong

A list of the most common errors and what they mean:

### When saving a carrier

> **"Pick a Parcel type on the DHL shipping method '...'"**

The Parcel type field is required for DHL carriers. Pick one.

> **"DHL Parcel does not deliver to the following countries: ..."**

You have a country in the Countries list that DHL Parcel does not
serve. Remove it.

> **"The parcel type '...' is only available for shipments to ..."**

Type-vs-country mismatch. E.g. Envelope = NL only, Mailbox parcel =
BE+NL only. Adjust the Countries or pick a different type.

### When validating a delivery

> **"The delivery has no customer address."**

`partner_id` is empty on the picking. Set a Customer.

> **"Customer '...' has no country set."**

Set a country on the partner.

> **"Customer '...' address is incomplete (street / zip / city required)."**

Fill in Street, ZIP and City on the partner.

> **"The warehouse / company address is incomplete"**

Your warehouse (`stock.warehouse.partner_id`) or company address is
missing data. Fill in street, zip, city, country.

> **"The parcel type '...' is only available for private recipients.
> '...' is a company."**

You've used a consumer-only type (Envelope, Mailbox parcel) on a
carrier used for a business customer address. Use a different type or
a different carrier.

> **"Add at least one parcel in the DHL Parcels tab on this delivery"**

You are validating a MIX delivery without rows in the DHL Parcels tab.
Fill in the tab.

> **"DHL Parcel rejected the shipment (HTTP 400): capabilities_retrieve_empty"**

DHL couldn't match a product/route/type combo. Most likely: parcel
type doesn't fit the recipient (consumer-only to a company, or vice
versa). Local guards normally catch this before the API call.

### Authentication / permissions

> **"DHL Parcel authentication returned no accessToken"**

Wrong User ID or API Key. Check both in My DHL Parcel.

> **HTTP 401/403 errors about labels**

Your API Key is missing the role `label-service.B2X`. Contact DHL.

### Browser cache

> **"Invalid field '...' on model 'delivery.carrier'"** or similar

Usually a browser cache of an old view. Hard refresh (Ctrl+Shift+R) or
clear site data in dev-tools. If that doesn't help: did you upgrade
the module after the last code update?

---

## 14. Languages

The module is available in:

- **English** (`i18n/en.po`)
- **Dutch** (source)
- **French** (`i18n/fr.po`)
- **German** (`i18n/de.po`)

The displayed language follows the **user language** of the Odoo user.
Change it in **Preferences → Language**.

Need a language that isn't shipped? You can translate strings within
Odoo itself via **Settings → Translations → Translated Terms**,
filtered on the module. These translations apply to your database;
they are not automatically included in the module.

---

## 15. Short FAQ

**Do I need a delivery product?**
Yes. Odoo requires every carrier to have a delivery product (on which
the shipping cost is booked as an order line). Create one like *DHL
Shipping Cost*. Leave the Company empty unless you want a separate
one per company.

**My carrier isn't visible on Add Shipping.**
Two most common causes: (1) the destination of the order falls
outside the Countries list of the carrier; (2) company mismatch - the
carrier inherits its company from the delivery product; check the
Company there.

**Can I ship from Germany or Spain?**
Not with this module. Your sender must be in BE, NL or LU. To ship
from another country you need a DHL contract for that region (DHL
Parcel DE, ES, ...) and a matching module.

**Does the module work with multi-company?**
Yes. Credentials are per carrier, so each company can have its own
DHL account. One database can therefore serve three DHL accounts (one
per company).

**How do I know which parcel type fits what I'm shipping?**
DHL's rules:
- *Envelope* (max 500g, NL only): letters, small documents.
- *Mailbox parcel* (max 2kg, BE/NL, B2C): small parcels that fit
  through the letterbox.
- *Parcel up to 10/20/31 kg*: standard parcels, dimensions up to
  80x50x35cm.
- *Pallet up to 1000 kg*: business only, for heavy shipments.

**Test vs production environment?**
DHL Parcel uses one API URL for both. Whether you're in test or live
depends only on which API key you enter. The *Test Environment*
button on the carrier does nothing for this provider.

---

## Appendix A - Supported destinations (31 countries)

For senders in BE, NL or LU:

Austria, Belgium, Bulgaria, Croatia, Czech Republic, Denmark, Estonia,
Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia,
Liechtenstein, Lithuania, Luxembourg, Monaco, Netherlands, Norway,
Poland, Portugal, Romania, San Marino, Slovakia, Slovenia, Spain,
Sweden, Switzerland, United Kingdom.

Returns come from the same 31 countries back to your Benelux
warehouse.
