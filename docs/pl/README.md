[en](../../README.md) | [de](../de/README.md) | [nl](../nl/README.md) | [fr](../fr/README.md) | [zh](../zh-hans/README.md) | [es](../es/README.md) | [it](../it/README.md) | pl | [sv](../sv/README.md)

# Integracja SAJ Local dla Home Assistanta

![SAJ Local](../../images/header.png)

[![HACS niestandardowe](https://img.shields.io/badge/HACS-niestandardowe-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Wydanie](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local?label=Wydanie)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![Aktywne instalacje](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=Aktywne%20instalacje&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![Sprawdzenia](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![Licencja](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local?label=Licencja)](../../LICENSE)

⭐ [Daj gwiazdkę projektowi na GitHubie](https://github.com/Counterphase-Labs/ha-saj-local): Twoje wsparcie to prawdziwa motywacja! 🙏😊

Twoja instalacja słoneczna SAJ w Home Assistancie, odczytywana prosto z falownika przez Twoją własną sieć. Bez konta w chmurze, bez aplikacji producenta pośrodku i z podejściem do odpytywania zaprojektowanym tak, by oszczędzać sprzęt.

To nieoficjalna integracja, tworzona przez społeczność. Nie jest wykonana, wspierana ani popierana przez SAJ. Zobacz [zastrzeżenie](user/README.md#zastrzeżenie).

> **Stan: w aktywnym rozwoju i jeszcze niewydana.** Nie ma jeszcze opublikowanego wydania.

## Dlaczego SAJ Local

- **Rozsądne ustawienia domyślne.** Dodaj swój falownik i uzyskaj działającą konfigurację bez przekopywania się przez strony opcji. Falownik, bateria i powiązane wyposażenie są wykrywane automatycznie.
- **Oszczędza Twój falownik.** Jedno połączenie i jedno żądanie naraz oraz sztywny limit żądań, którego nie przekroczy żadne ustawienie, ponowne wczytanie ani awaria. Ty wybierasz, co jest odczytywane i jak często.
- **Tylko odczyt, dopóki nie zdecydujesz inaczej.** Zapis włączasz osobno dla każdej instalacji, więc nic w Twoim falowniku nie zmieni się przez przypadek.
- **Te same nazwy w każdym modelu.** Pulpity i automatyzacje piszesz raz i działają one dalej w modelach SAJ, a także przetrwają przejście z H2 na HS3.
- **Wiele systemów.** Podłącz więcej niż jeden system SAJ do tego samego Home Assistanta.
- **Karty pulpitu.** Karty do podglądu informacji i do zmiany konfiguracji, dodawane z selektora kart.
- **Czytelne błędy i bezpieczna diagnostyka.** Gdy coś pójdzie nie tak, dowiesz się co i dlaczego, a zrzuty debugowania są zaprojektowane tak, by można je było bezpiecznie udostępniać.
- **W pełni lokalnie.** Wszystko komunikuje się z Twoim falownikiem przez Twoją sieć. Nic nie jest wysyłane do usługi w chmurze.

## Obsługiwane urządzenia

Obsługiwane są SAJ HS3 i jednofazowy SAJ H2. Zobacz [obsługiwane urządzenia](user/supported-equipment.md), aby poznać pełną listę oraz to, czego jeszcze nie obsługujemy.

## Dokumentacja

- [Dokumentacja użytkownika](user/README.md): zainstaluj, skonfiguruj i obsługuj SAJ Local.
- [Dokumentacja dla programistów](developer/README.md): jak SAJ Local jest budowany, sprawdzany i wydawany.
- [Współtworzenie](../../CONTRIBUTING.md): przygotuj kopię roboczą i wyślij zmianę.

## Pomoc i opinie

Pytania, zgłoszenia błędów i pomysły są mile widziane w [systemie zgłoszeń](https://github.com/Counterphase-Labs/ha-saj-local/issues).

Problem z bezpieczeństwem zgłoś prywatnie, zobacz [politykę bezpieczeństwa](../../SECURITY.md).

## Licencja

[MIT](../../LICENSE)
