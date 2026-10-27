[en](../../README.md) | [de](../de/README.md) | nl | [fr](../fr/README.md) | [zh](../zh-hans/README.md) | [es](../es/README.md) | [it](../it/README.md) | [pl](../pl/README.md) | [sv](../sv/README.md)

# SAJ Local Home Assistant-integratie

![SAJ Local](../../images/header.png)

[![HACS aangepast](https://img.shields.io/badge/HACS-aangepast-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Release](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local?label=Release)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![Actieve installaties](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=Actieve%20installaties&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![Controles](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![Licentie](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local?label=Licentie)](../../LICENSE)

⭐ [Geef het project een ster op GitHub](https://github.com/Counterphase-Labs/ha-saj-local): uw steun is een echte motivatie! 🙏😊

Uw SAJ-zonnesysteem in Home Assistant, rechtstreeks uit de omvormer uitgelezen via uw eigen netwerk. Geen cloudaccount, geen app van de fabrikant ertussen en een pollingaanpak die is ontworpen om de hardware te ontzien.

Dit is een onofficiële integratie, gebouwd door de community. Ze wordt niet gemaakt, ondersteund of goedgekeurd door SAJ. Zie de [disclaimer](user/README.md#disclaimer).

> **Status: in actieve ontwikkeling en nog niet uitgebracht.** Er is nog geen uitgebrachte versie.

## Waarom SAJ Local

- **Verstandige standaardwaarden.** Voeg uw omvormer toe en krijg een werkende opzet zonder door pagina's vol opties te hoeven ploeteren. De omvormer, de batterij en de bijbehorende apparatuur worden automatisch herkend.
- **Zacht voor uw omvormer.** Eén verbinding en één verzoek tegelijk, en een vast plafond voor verzoeken dat geen instelling, geen herlaadbeurt en geen storing kan overschrijden. U kiest wat er wordt uitgelezen en hoe vaak.
- **Alleen lezen, tenzij u anders aangeeft.** Schrijven is per installatie optioneel, zodat er niets per ongeluk op uw omvormer verandert.
- **Dezelfde namen op elk model.** Dashboards en automatiseringen schrijft u één keer en ze blijven werken op alle SAJ-modellen, ook na de overstap van een H2 naar een HS3.
- **Meerdere systemen.** Koppel meer dan één SAJ-systeem aan dezelfde Home Assistant.
- **Dashboardkaarten.** Kaarten om informatie te bekijken en om de configuratie te wijzigen, toegevoegd via de kaartkiezer.
- **Duidelijke fouten en veilige diagnostiek.** Als er iets misgaat, hoort u wat en waarom, en debugdumps zijn gemaakt om veilig te kunnen worden gedeeld.
- **Volledig lokaal.** Alles praat via uw netwerk met uw omvormer. Er wordt niets naar een clouddienst gestuurd.

## Ondersteunde apparatuur

De SAJ HS3 en de eenfasige SAJ H2 worden ondersteund. Zie [ondersteunde apparatuur](user/supported-equipment.md) voor de volledige lijst en wat nog niet wordt ondersteund.

## Documentatie

- [Gebruikersdocumentatie](user/README.md): SAJ Local installeren, instellen en bedienen.
- [Ontwikkelaarsdocumentatie](developer/README.md): hoe SAJ Local wordt gebouwd, gecontroleerd en uitgebracht.
- [Bijdragen](../../CONTRIBUTING.md): een checkout opzetten en een wijziging insturen.

## Hulp en feedback

Vragen, bugmeldingen en ideeën zijn welkom in de [issuetracker](https://github.com/Counterphase-Labs/ha-saj-local/issues).

Meld een beveiligingsprobleem privé, zie het [beveiligingsbeleid](../../SECURITY.md).

## Licentie

[MIT](../../LICENSE)
