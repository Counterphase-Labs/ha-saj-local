[en](../../en-gb/developer/releasing.md) | [de](../../de/developer/releasing.md) | nl | [fr](../../fr/developer/releasing.md) | [zh](../../zh-hans/developer/releasing.md) | [es](../../es/developer/releasing.md) | [it](../../it/developer/releasing.md) | [pl](../../pl/developer/releasing.md) | [sv](../../sv/developer/releasing.md)

# Releasen

Wat u voor een release doet, hoe een release wordt gepubliceerd en hoe de Home Assistant-versie wordt opgehoogd. Een versietag pushen start de workflow `Release` in `.github/workflows/release.yml`, die de tag controleert, de controles draait en een concept-GitHub-release aanmaakt.

## Versies

Een release is een GitHub-release gemaakt van een versietag op `main`. De tag heeft geen voorvoegsel `v` en is gelijk aan de versie in `custom_components/saj_local/manifest.json`, `pyproject.toml` en `frontend/package.json`. Een stabiele release is `X.Y.Z` en een bèta is `X.Y.ZbN`, gepubliceerd als een GitHub-pre-release. De bèta's voor de eerste stabiele release zijn `1.0.0b1`, `1.0.0b2` enzovoort, de eerste stabiele release is `1.0.0`, en Semantic Versioning geldt vanaf `1.0.0`. De releaseopmerkingen staan alleen in de GitHub-release, en de opmerkingen van een bèta noemen elke wijziging aan een entiteit, een opgeslagen instelling, een kaarttype of een kaartinstelling sinds de vorige bèta. De sectie [Releases](../../../.github/work/requirements.md#releases) van de projectrequirements bevat de regel.

## Voor een release

Doe dit op `main`, in volgorde.

1. **Draai `make ci`.** De [pagina Controles](checks.md) vermeldt wat `make ci` draait.
2. **Draai `make docs-images`.** De gebruikersdocumentatie toont de interface, en CI genereert de afbeeldingen niet opnieuw, dus elke release heeft een verse set nodig. De target heeft Docker nodig. Draai de target, bekijk elke gewijzigde afbeelding, leg de gewijzigde afbeeldingen in `docs/images/en-gb/` vast en draai `make docs-check`. Een run die mislukt schrijft geen afbeelding, dus release niet met een mislukte run. Lees [Schermafbeeldingen](documentation.md#schermafbeeldingen) voor wat de run doet en waarom elke meting in een afbeelding gesimuleerd is.
3. **Kopieer de sitescreenshot in dezelfde stap.** Kopieer `docs/images/en-gb/cards-power-flow-card.png` naar `assets/images/saj-local-power-flow.png` in de repository `website` en leg de kopie daar vast, omdat de SAJ Local-pagina op `counterphase.dev` een kopie van de afbeelding toont. Geen controle vangt een verouderde kopie, omdat CI in deze repository de websiterepository niet kan zien.
4. **Draai `make release-check`.** De stap maakt een archief van `custom_components/saj_local/` en faalt wanneer het archief `asset-manifest.json`, de gebouwde kaartbundel of `THIRD_PARTY_LICENSES.md`, de licenties van de bibliotheken in de bundel, mist. Draai `make build` en leg eerst de bundel en het licentiebestand vast wanneer de kaarten zijn gewijzigd.
5. **Stel de nieuwe versie in.** Stel de versie in in `custom_components/saj_local/manifest.json`, `pyproject.toml` en `frontend/package.json`. Draai `uv lock` zodat `uv.lock` de projectversie vastlegt, en draai `npm install --package-lock-only` in `frontend/` zodat `frontend/package-lock.json` de versie vastlegt. Draai `make release-check`, leg vast op `main` en wacht tot CI slaagt.

De schermafbeeldingen zijn het enige onderdeel van een release dat CI niet kan controleren. Een wijziging die een afbeelding toevoegt of verwijdert, faalt `make docs-check` via de regels voor ongebruikte en ontbrekende afbeeldingen. Een wijziging aan de interface die een afbeelding verouderd achterlaat, faalt nergens, dus stap 2 houdt de afbeeldingen actueel.

## Een release publiceren

1. Push de tag: `git tag 1.0.0b1`, dan `git push origin 1.0.0b1`.
2. Wacht op de workflow `Release`. De workflow eist dat de getagde commit op `main` staat, draait `make ci` via `ci.yml` en maakt een conceptrelease met de door GitHub gegenereerde opmerkingen.
3. Open de conceptrelease en bewerk de gegenereerde opmerkingen. Noem voor een bèta elke wijziging aan een entiteit, een opgeslagen instelling, een kaarttype of een kaartinstelling sinds de vorige bèta.
4. Druk op Publish.

Een mislukte run maakt geen concept. Verwijder de tag met `git push origin :refs/tags/<tag>` en `git tag -d <tag>`, herstel `main` en tag opnieuw.

HACS biedt een gepubliceerde bèta aan gebruikers die "Show beta versions" aanzetten en een gepubliceerde stabiele release aan elke gebruiker. Een gebruiker zonder de schakelaar krijgt de top van `main` totdat `1.0.0` bestaat, en daarom moet `main` `make ci` doorstaan vóór elke push.

## De Home Assistant-versie ophogen

De Home Assistant-versie is vastgepind in meerdere bestanden die samen moeten worden bijgewerkt, anders lopen de ontwikkelcontainer, de browsertests en de screenshotrun, CI, HACS en de testharnas uiteen:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, de ontwikkel-Home Assistant-runtime.
2. `Dockerfile.playwright-home-assistant`: de regel `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` van het image dat `make test-browser-home-assistant` en `make docs-images` gebruiken.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` voor CI-lint en mypy, **en** `pytest-homeassistant-custom-component==<bijpassende release>`. Het testharnas levert zijn eigen vastgepinde `homeassistant`, dus de twee pins moeten uit dezelfde Home Assistant-release komen, anders lossen lint en tests verschillende kernen op.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, de minimale Home Assistant-kern die HACS afdwingt.
5. `uv.lock`: draai `uv lock` na de bewerking van `pyproject.toml`, zodat het lockbestand de nieuwe pins vastlegt.

Controleer de combinatie op PyPI voordat u vastlegt: de `requires_dist` van `pytest-homeassistant-custom-component` moet dezelfde `homeassistant==<X.Y.Z>` vermelden die in `pyproject.toml` is vastgepind.

Draai na een ophoging `make ci` en `make docs-images`, omdat een nieuwe Home Assistant-versie de schermen kan wijzigen die de afbeeldingen tonen.
