# Labels & Tracking for DHL eCommerce Benelux: Configuratie en FAQ

Dit document beschrijft alles wat geconfigureerd moet worden om de module te
laten werken, welke data in Odoo hij nodig heeft, en de vragen die het meest
gesteld worden.

## Vereisten

- Odoo 17, 18 of 19 met de delivery-features geïnstalleerd (de module
  hangt af van `stock_delivery` en `sale`).
- Een actief **DHL eCommerce Benelux**-zakelijk account.
- **De API-rol toegekend aan dat account door DHL.** Dit is wat de meeste
  mensen missen. Een standaard DHL eCommerce Benelux-account heeft geen
  API-toegang uit de doos; de API-rol moet door DHL-personeel toegekend
  worden op verzoek. Zonder die rol toont het DHL-portaal geen API
  Keys-sectie en kan je geen credentials aanmaken. Zie "Waar haal ik de
  API-credentials?" hieronder voor hoe je die aanvraagt.
- API-credentials: een **User ID**, een **API Key**, plus het korte
  **Account ID** (klantnummer). Aan te maken in het portaal zodra de
  API-rol actief is.
- Om een levering als meerdere pakketten te versturen (multicollo): gebruik
  het **Number of parcels**-veld op de delivery (eenvoudigst, één DHL-piece
  met quantity=N) of activeer de **Packages**-feature (Inventory →
  Configuration → Settings → Operations → Packages) en gebruik **Put in
  Pack** om items per doos te splitsen. Met Put in Pack wordt elke package
  een aparte piece.

## De verzendmethode opzetten

Maak **één verzendmethode per parceltype** aan dat je wil aanbieden
(Brievenbuspakket, Pakket tot 10 kg, Pakket tot 20 kg, ...). Elke methode
staat voor één vast DHL-parceltype met zijn eigen prijs.

1. Installeer de module **Labels & Tracking for DHL eCommerce Benelux**.
2. Ga naar **Inventory → Configuration → Shipping Methods** en maak een
   nieuwe aan.
3. Zet **Provider** op **Labels & Tracking for DHL eCommerce Benelux**. Een tab
   **DHL Parcel** verschijnt.
4. Vul op die tab in:
   - **Credentials**: User ID, API Key, Account ID.
   - **Parcel type** (verplicht): het DHL-type voor alle zendingen onder
     deze methode, bv. Brievenbuspakket of Pakket tot 10 kg.
   - **Default weight (kg)**: het gewicht dat wordt gestuurd wanneer een
     pakket geen gewicht heeft (zie FAQ).
   - **Pricing mode**: Flat (met vaste prijs) of Weight-based rules.
5. Laat **Integration Level** op **Get Rate and Create Shipment** staan.
   Dit is vereist om bij validate effectief een label aan te maken.
6. **Countries**: kies de bestemmingen die deze methode dekt. De lijst is
   automatisch beperkt tot de 31 landen waar DHL Parcel levert, en verder
   ingeperkt op basis van het gekozen parceltype (Envelop 50 tot 500 g:
   alleen NL; Brievenbuspakket: alleen BE+NL).
7. Optioneel: **Website**. Bind de methode aan één webshop voor
   webshop-checkout, of laat leeg om ze overal beschikbaar te maken.

## DHL-side permissies en feature-gating

Naast de credentials hangen verschillende features af van wat DHL op je
API-key en contract heeft geactiveerd. Meestal wordt dit eenmalig geregeld
tijdens onboarding; contacteer je DHL-technisch contact bij twijfel.

**Vereist voor de basisflow (labels aanmaken):**
- Het JWT-token van de API-key moet de rol **`label-service.B2X`** bevatten.
  Zonder die rol faalt label-aanmaak. Als de module authenticatie- of
  "rejected the shipment"-fouten geeft die over permissies gaan, is dit
  het eerste om te verifiëren met DHL.

**Helemaal niet beschikbaar:**
- **Live tarieven via de API.** Bevestigd door DHL: de gateway heeft geen
  rating-endpoint, en het `price`-veld dat in het `/parcel-types`-schema
  verschijnt is bedoeld voor douaneaangiftes (valuta + aangegeven waarde),
  niet voor tarief-opvraging. Tarieven kan je in het DHL-portaal bekijken
  (vereist de Rate Manager-rol op je account) maar niet programmatisch
  ophalen. De module gebruikt daarom de geconfigureerde prijs op de
  carrier (vaste prijs of gewichtstaffel) voor de verzendkost op het
  sale order.

- **Annuleren via API.** De publieke DHL-API heeft geen gedocumenteerd
  endpoint om een zending programmatisch te annuleren. Hun OpenAPI-spec
  bevat wel `GET /intervention-options` (om te vragen of interventies
  toegestaan zijn) maar biedt geen POST-endpoint om een cancel effectief
  uit te voeren. Annuleren gebeurt in het DHL-portaal. De cancel-actie
  van de module reflecteert dit: hij plaatst een chatter-note op de
  delivery met de instructie om in het portaal te annuleren, en laat de
  lokale tracking-referentie staan zodat de operator ze kan opzoeken.
  Dit is geen tijdelijke beperking - zo is de publieke API opgevat.

**Optioneel, elk apart gegated door een DHL-instelling:**

- **Internationale verzendingen** (Parcel Connect / Europlus / Europlus
  Pallet / Europlus International). Die vereisen dat de overeenkomstige
  producten in je DHL-contract zitten. Bevestig met DHL welke producten
  op je account actief zijn voor je de module configureert voor
  niet-Benelux-bestemmingen.

- **Retours** (`returnLabel: true` en de `ADD_RETURN_LABEL`-optie). Het
  `/shipments`-endpoint accepteert die zonder extra permissie, op
  voorwaarde dat je DHL-contract het passende return-product bevat
  (DFY-RETURN / EPL-RETURN / RETURN-CON).

**Hoe de module reageert wanneer een permissie ontbreekt:**
- Geen `label-service.B2X`: een duidelijke UserError wijst naar
  credentials/permissies.
- Cancel-actie: plaatst altijd een chatter-note ("annuleer in het
  portaal"); belt de API nooit. Zie hierboven waarom.
- Contract-gaten (ontbrekend product, ontbrekende route): het foutbericht
  van de API zelf wordt letterlijk in de chatter getoond, wat meestal
  aangeeft welk contract-probleem er is.

**Als je een permissie-probleem vermoedt:**
De rollen op je token kan je inspecteren door debug-logging aan te zetten
op de `parcelbridge_dhl_benelux`-logger en de authenticatie-response te
bekijken. Deel de rollen die je hebt met je DHL-technisch contact en
vraag welke bijkomende rol de ontbrekende feature activeert.

## Vereiste data in Odoo (vaak vergeten)

- **Het magazijnadres moet compleet zijn** (bedrijfsnaam, straat, huisnummer,
  postcode, stad, land). Dit wordt op het label gedrukt als afzender en
  gebruikt voor retours. Een onvolledig magazijnadres blokkeert
  shipment-aanmaak.
- **Productgewichten**: producten horen een gewicht te hebben. Zonder
  gewicht is het pakketgewicht 0, wat DHL weigert. Zie de FAQ-entry over
  het default gewicht.
- **Klantadres**: het huisnummer wordt gelezen uit het **street2**-veld
  (Belgische conventie) of geparsed uit het einde van **street**. Een
  ontbrekend huisnummer laat DHL de zending markeren voor manuele check.
- Alle adresvelden moeten enkel het **Latijnse alfabet** gebruiken. Dit
  is een DHL-beperking.

## FAQ

**Het pakket kan niet aangemaakt worden omdat het totaalgewicht van de
producten op de picking 0.0 kg is.**
De producten hebben geen gewicht ingesteld, dus Odoo bouwt geen pakket. Ofwel
zet je gewichten op de producten, ofwel val je terug op het
**Default weight (kg)**-veld van de carrier, dat wordt gestuurd wanneer het
pakketgewicht 0 is. Merk op dat een onnauwkeurig aangegeven gewicht kan
leiden tot een herweging bij DHL en een correctie op de factuur.

**Hoe wordt het parceltype gekozen?**
Het parceltype is vast bepaald door de verzendmethode. Elke methode staat
voor één DHL-parceltype (Brievenbuspakket / Pakket tot 10 kg / ... / Pallet
tot 1000 kg), dus het type wordt beslist zodra jij (of de klant) de methode
kiest. Maak één verzendmethode per type dat je wil aanbieden. Een gewoon
pakket gaat tot 31 kg; boven die grens gebruik je een Pallet-methode.

Voor zendingen die verschillende parceltypes in één levering mixen (zoals
het DHL-portaal ondersteunt), maak je een methode met
**Parcel type = Mixed (MIX)**. Op deliveries met die methode verschijnt een
**DHL Parcels**-tab waar je één rij per pakket toevoegt en per rij het type
kiest. De type-lijst past zich aan op basis van of de ontvanger een
particulier of een bedrijf is.

**Waar stel ik de verzendprijs in? Het Fixed Price-veld lijkt genegeerd.**
De DHL Parcel-API geeft geen live tarieven, dus de prijs wordt op de carrier
zelf ingesteld. Kies **Pricing mode = Flat** en vul **DHL flat price** in,
of **Pricing mode = Weight-based rules** en definieer de tiers op de
**Pricing**-tab (gebruik `weight` als variabele). Het generieke "Fixed
Price"-veld van de basis-carrier wordt door deze provider niet gebruikt.

**De DHL-methode ontbreekt / ik kan ze niet selecteren op een delivery.**
Een verzendmethode wordt gefilterd op company: de Company is **overgenomen
van het delivery-product**, dus je kan die niet direct op de carrier
wijzigen. Als het delivery-product een company heeft ingesteld, verschijnt
de carrier alleen voor deliveries van die company. Fix: open het
delivery-product en maak z'n Company leeg (blank = alle companies), of zet
'm op de company waar je vanuit verzendt. Ook het bestemmingsland telt: de
methode toont zich alleen voor landen die op de carrier staan.

**Waarom zien sommige webshop-klanten geen DHL-optie bij checkout?**
De module filtert DHL-carriers in webshop-checkout op basis van de
particulier-vs-zakelijk-status van de ontvanger, bovenop Odoo's standaard
filters (published, website, land, prijs-beschikbaarheid). De filter
spiegelt de backend Add Shipping-wizard zodat overal dezelfde set carriers
wordt aangeboden.

Concreet: een carrier rond een **consumer-only** parceltype (Envelop 50 tot
500 g, Brievenbuspakket) is verborgen voor zakelijke klanten, en een
carrier rond een **business-only** parceltype (Pallet tot 1000 kg) is
verborgen voor particuliere klanten. De drie "Pakket tot X kg"-types
(10/20/31) hebben geen ontvanger-restrictie en verschijnen voor beide.

Als klanten melden "er verschijnt geen DHL-optie", check dan of je minstens
één gepubliceerde DHL-carrier hebt die past bij het ontvanger-type dat ze
zijn. De veiligste setup voor een webshop die beide doelgroepen bedient is
één carrier met een "Pakket tot X kg"-type (geen ontvanger-restrictie);
voeg daarbovenop Envelop / Brievenbus / Pallet varianten toe als je een
rijker aanbod wil, wetende dat die automatisch verbergen voor de doelgroep
die er niet bij past.

**Er gebeurt niets als ik de delivery valideer.**
Controleer dat **Integration Level** op **Get Rate and Create Shipment**
staat. Met alleen "Get Rate" wordt er geen label aangemaakt bij validate.

**Wat doet de Test Environment / Production Environment-knop?**
Voor deze provider: niets. DHL Parcel gebruikt één API-adres voor zowel
test als productie. Of je in test of live zit hangt alleen af van welke
API-key je invoert.

**Kan ik een standaard verzendmethode op orders instellen?**
Zet het **Delivery Method**-veld op de klant (Contacts → klant → Sales
and Purchase tab). Nieuwe orders voor die klant nemen dat over als
default. Er is geen enkelvoudige globale default voor alle orders zonder
customization. Voor webshop-orders kiest de klant de methode bij checkout.

**Één order wordt verzonden vanuit twee magazijnen. Wat gebeurt er?**
Odoo maakt een aparte delivery per magazijn, en elk wordt een eigen
DHL-shipment met het correcte afzenderadres. Één label kan slechts één
afzender bevatten, dus verschillende magazijnen betekenen altijd
verschillende shipments.

**Hoe declareer ik snel verschillende pakketten?**
Op een DHL-delivery is er een **Number of parcels**-veld. Zet het op het
aantal identieke pakketten dat je wil versturen; de module stuurt één
DHL-shipment met dat aantal pieces, allemaal van het parceltype van de
carrier. DHL geeft één tracker per piece en één gecombineerde
multi-page label-PDF. Geen Put in Pack nodig als alle pieces hetzelfde
type zijn.

**Ik zie geen "Put in Pack"-knop op de delivery.**
Activeer de Packages-feature: Inventory → Configuration → Settings →
Operations → Packages, en bewaar. De knop verschijnt daarna op de
delivery.

**Hoe stop ik sommige producten in één doos en de rest in een andere?**
Odoo pakt op basis van hoeveelheid. In Detailed Operations: zet de
hoeveelheid alleen op de regels voor de eerste doos (de andere op 0),
klik Put in Pack, en zet dan de resterende regels in en klik opnieuw Put
in Pack. Elke Put in Pack bundelt wat op dat moment een hoeveelheid heeft
en nog niet gepakt is.

**De Package Type-dropdown is leeg.**
Dat is OK; package type wordt door deze module niet gebruikt. Het
DHL-parceltype ligt vast door de verzendmethode.

**Een order wordt in verschillende dozen gepakt (met verschillende items
per doos).**
Gebruik native **Put in Pack**: splits de hoeveelheden zo dat de items
voor doos 1 eerst "Done" zijn, klik Put in Pack, en zet dan de resterende
hoeveelheden en klik opnieuw Put in Pack. Elke package wordt één piece in
de DHL-shipment, allemaal van het parceltype van de carrier. Elke piece
krijgt z'n eigen tracking-code, en alle labels komen terug in één
multi-page PDF die aan de delivery hangt. Als het je niet uitmaakt welke
items in welke doos zitten, gebruik dan gewoon het **Number of
parcels**-veld (eenvoudiger - één klik).

**Naar welke bestemmingen kan ik verzenden?**
Alle 31 Europese bestemmingen die DHL eCommerce Benelux dekt. Zie
"Welke bestemmingen ondersteunt de module, en hoe wordt het DHL-product
gekozen?" hieronder voor de volledige lijst en de product-resolutie-logica.

**Hangt het parceltype af van of de klant een particulier of een bedrijf
is?**
Nee. De parceltype-catalogus van DHL is dezelfde ongeacht de ontvanger; het
verschil tussen zakelijk en particulier wordt geregeld door het product dat
DHL automatisch selecteert (een home-delivery-product voor consumenten,
een zakelijk product anders).

**Hoe annuleer ik een shipment?**
In het DHL-portaal - er is geen programmatische alternatief. De publieke
DHL-API heeft geen cancel-endpoint, alleen een read-only
`GET /intervention-options` die rapporteert of een cancel toegestaan zou
zijn. De cancel-actie van de module plaatst een note op de delivery (met
de tracking-referentie nog leesbaar zodat je ze kan opzoeken in het
portaal).

Nota van DHL: een label dat aangemaakt werd maar waarvan het pakket het
DHL-netwerk nooit binnenkwam (dus je annuleerde voor drop-off) wordt
niet gefactureerd. Je hoeft enkel in het portaal te annuleren als je de
zending uit je MDP shipment-lijst wil verwijderen voor de netheid.

**Verschijnen shipments die via de API aangemaakt zijn in het
DHL-dashboard?**
Ja voor productie-keys: shipments die via de API aangemaakt worden
verschijnen in het DHL-portaal onder je account, precies alsof je
ze manueel had ingevoerd. Sandbox-shipments verschijnen NIET in het
productie-portaal (dat is net de bedoeling van sandbox: labels worden
gegenereerd en tracker-codes teruggegeven, maar het pakket komt het
DHL-netwerk nooit binnen en wordt niet gefactureerd).

**Het portaal heeft een "save this customer"-tickbox wanneer je een
zending invoert. Gebruikt de module die?**
Nee, en dat kan ook niet: de publieke DHL Parcel-API heeft geen
adresboek- / customer-endpoints. De "save customer"-tickbox in het
DHL-portaal is een portaal-interne feature die enkel telt wanneer je
zendingen manueel invoert via de portaal-UI. In onze flow zijn Odoo's
`res.partner`-records de klantendatabase: elke delivery stuurt zijn
receiver-adres rechtstreeks van de partner naar DHL, dus er is geen
tweede kopie van het adres nodig in het DHL-portaal. De tickbox mag
genegeerd worden bij gebruik van deze module.

**Waar haal ik de API-credentials?**
Er zijn twee stappen: eerst moet DHL API-toegang activeren op het
account, dan maak je de eigenlijke keys zelf aan in het portaal.

1. **DHL kent de API-rol toe aan je account.** API-toegang is geen
   standaardonderdeel van een DHL eCommerce Benelux-contract. Voor je
   een API Key kan aanmaken in het portaal, moet je DHL-contact (of DHL
   eCommerce support) de **API-rol** toekennen aan je account. Dit is
   een manuele actie aan DHL-kant - je kan het zelf niet triggeren. Mail
   je DHL-accountmanager met je klantnummer en vraag expliciet om
   API-toegang op je account te activeren zodat je API keys kan aanmaken
   via het portaal.

   Tot die rol toegekend is, toont het DHL-portaal alleen een
   "Connections"-pagina en geen API Keys-sectie. Dat is het signaal dat
   stap 1 nog niet rond is.

2. **Maak de keys aan in het portaal.** Zodra DHL bevestigt dat de rol
   actief is: log in op het DHL-portaal en ga naar **Settings → API
   Keys**. Kopieer de **User ID** en **API Key** die daar staan. Het
   **Account ID** is het korte klantnummer dat op facturen en in je
   account-details te vinden is.

**Waarom kan mijn shipping manager de DHL API-credentials niet zien?**
Sinds module-versie 17.0.0.8.8 zijn de drie credential-velden (User ID,
API Key, Account ID) beperkt tot een dedicated group **DHL Parcel
Administrator**. Odoo-administrators worden automatisch toegevoegd. Andere
users die die velden moeten instellen of lezen moeten manueel aan de
group toegevoegd worden: **Settings → Users & Companies → Users → [de
user] → Access Rights → tab Other → DHL Parcel Administrator**. Leden van
die group behouden hun gewone toegang tot al de rest; de group ontsluit
enkel de credential-velden.

Niet-leden kunnen nog steeds DHL Parcel-carriers aanmaken, bewerken en
gebruiken - ze zien de credential-velden gewoon niet op de form en
kunnen ze niet lezen via XML-RPC/ORM. Alle interne reads door de module
zelf gebruiken `sudo()`, dus dagelijkse operaties (deliveries valideren,
labels printen, Test Connection getriggerd door de admin die de setup
deed) werken onafhankelijk van de group-lidmaatschap van de operator.

**Welke bestemmingen ondersteunt de module, en hoe wordt het
DHL-product gekozen?**
De module ondersteunt outbound vanuit BE / NL / LU naar 31 Europese
bestemmingen. De Countries-dropdown op de carrier is gefilterd op die
lijst (en verder ingeperkt door parceltype: Envelop = alleen NL,
Brievenbuspakket = alleen BE + NL, andere pakketten + Pallet = alle 31).

Voor elke shipment resolvet de module het juiste DHL-product op basis van
het bestemmingsland en het klanttype (zakelijk / consumer):

- Benelux (BE / NL / LU): blanco product-code; DHL resolvet DFY /
  Europlus / Parcel Connect automatisch aan hun kant.
- Niet-Benelux EU: **CON** (Parcel Connect) voor particuliere
  ontvangers, **EPL-INT** (Europlus International) voor zakelijke
  ontvangers.
- Buiten EU (post-Brexit UK, Zwitserland, Noorwegen, ...): **CON2C**
  (Parcel Connect 2C) voor particulier, **EPL-INT** voor zakelijk. Een
  bulk-douaneaangifte wordt automatisch aan de request toegevoegd.
- Palletzendingen (Pallet tot 1000 kg): **EPL-PAL** (Europlus Pallet).

**Hoe weet ik welke DHL-producten in mijn contract zitten?**
Gebruik de **Verify Contract**-knop in de *Contract check*-sectie van
de DHL Parcel-tab op de carrier. Die queryt DHL's `/products`-endpoint
voor elk aangevinkt bestemmingsland + relevant klanttype, en
rapporteert of het product dat deze carrier zou gebruiken effectief
actief is op je DHL-contract. Landen gemarkeerd als NOT IN CONTRACT
zullen falen bij label-aanmaak; vraag DHL om het ontbrekende product
te activeren, of vink die landen uit op de carrier. Dit is een read-only
call - er wordt niks verzonden en er verschijnt niks in het
DHL-portaal.

## Notes voor de integrator

- Credentials staan op het verzendmethode-record, niet in globale
  settings, dus één Odoo-database kan meerdere DHL-accounts bedienen
  (één carrier per account).
- Het afzenderadres komt van het uitgaande magazijn in Odoo, niet van de
  default in het DHL-dashboard. Dat houdt multi-warehouse en retours
  correct.
- De label-PDF wordt van DHL opgehaald en aan de delivery gehangen zoals
  ze is. De module doet zelf geen label-rendering, dus elke wijziging
  van de DHL-label-layout wordt automatisch opgepikt.
