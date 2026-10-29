[en](../../README.md) | [de](../de/README.md) | [nl](../nl/README.md) | [fr](../fr/README.md) | [zh](../zh-hans/README.md) | [es](../es/README.md) | [it](../it/README.md) | [pl](../pl/README.md) | sv

# SAJ Local-integration för Home Assistant

![SAJ Local](../../images/header.png)

[![HACS anpassat](https://img.shields.io/badge/HACS-anpassat-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Utgåva](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local?label=Utg%C3%A5va)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![Aktiva anläggningar](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=Aktiva%20anl%C3%A4ggningar&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![Kontroller](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![Licens](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local?label=Licens)](../../LICENSE)

⭐ [Ge projektet en stjärna på GitHub](https://github.com/Counterphase-Labs/ha-saj-local): ditt stöd är en riktig motivation! 🙏😊

Ditt SAJ-solsystem i Home Assistant, avläst direkt från växelriktaren över ditt eget nätverk. Inget molnkonto, ingen tillverkarapp i mitten och ett avfrågningssätt som är utformat för att vara skonsamt mot hårdvaran.

Det här är en inofficiell integration, byggd av communityn. Den är inte gjord, stödd eller godkänd av SAJ. Se [friskrivningen](user/README.md#friskrivning).

> **Status: förhandsversion.** SAJ Local har ännu ingen stabil version. Varje version före `1.0.0` är en beta, och versionsinformationen för en beta nämner varje inkompatibel ändring. Se [betaversioner](user/installation.md#betaversioner).

## Varför SAJ Local

- **Förnuftiga standardval.** Lägg till din växelriktare och få en fungerande konfiguration utan att bläddra bland sidor med alternativ. Växelriktaren, batteriet och tillhörande utrustning upptäcks automatiskt.
- **Skonsam mot din växelriktare.** En anslutning och en förfrågan i taget, och ett fast tak för förfrågningar som ingen inställning, omladdning eller felsituation kan överskrida. Du väljer vad som läses av och hur ofta.
- **Skrivskyddad om du inte säger något annat.** Skrivning är ett aktivt val per anläggning, så ingenting ändras på din växelriktare av misstag.
- **Samma namn på alla modeller.** Instrumentpaneler och automationer skrivs en gång och fortsätter fungera över SAJ-modellerna, och klarar ett byte från en H2 till en HS3.
- **Flera system.** Anslut mer än ett SAJ-system till samma Home Assistant.
- **Kort för instrumentpanelen.** Kort för att visa information och för att ändra konfiguration, som läggs till från kortväljaren.
- **Tydliga fel och säker diagnostik.** När något går fel får du veta vad och varför, och felsökningsdumpar är byggda för att vara säkra att dela.
- **Helt lokalt.** Allt pratar med din växelriktare över ditt nätverk. Ingenting skickas till en molntjänst.

## Utrustning som stöds

SAJ HS3 och den enfasiga SAJ H2 stöds. Se [utrustning som stöds](user/supported-equipment.md) för hela listan och vad som ännu inte stöds.

## Dokumentation

- [Användardokumentation](user/README.md): installera, konfigurera och använd SAJ Local.
- [Utvecklardokumentation](developer/README.md): hur SAJ Local byggs, kontrolleras och ges ut.
- [Bidra](../../CONTRIBUTING.md): ställ in en utcheckning och skicka en ändring.

## Hjälp och återkoppling

Frågor, felrapporter och idéer är välkomna i [ärendehanteringen](https://github.com/Counterphase-Labs/ha-saj-local/issues).

Rapportera ett säkerhetsproblem privat, se [säkerhetspolicyn](../../SECURITY.md).

## Licens

[MIT](../../LICENSE)
