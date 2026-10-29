[en](../../en-gb/user/installation.md) | [de](../../de/user/installation.md) | [nl](../../nl/user/installation.md) | [fr](../../fr/user/installation.md) | [zh](../../zh-hans/user/installation.md) | [es](../../es/user/installation.md) | [it](../../it/user/installation.md) | pl | [sv](../../sv/user/installation.md)

# Instalacja

Strona Instalacja instaluje SAJ Local przez HACS, czyli Home Assistant Community Store. Pełna lista tego, co robi konfiguracja, jest w sekcji [Konfiguracja i wykrywanie](../../../custom_components/saj_local/docs/features.md#setup-and-detection) listy funkcji integracji.

SAJ Local nie ma jeszcze stabilnego wydania. Każde wydanie przed `1.0.0` jest wersją beta, zobacz [wersje beta](#wersje-beta). Przed instalacją sprawdź [obsługiwane wyposażenie](supported-equipment.md).

## Czego potrzebujesz

- Home Assistanta w minimalnej wersji podanej w [`hacs.json`](../../../hacs.json) oraz HACS.
- Obsługiwanego falownika SAJ, który odpowiada na Modbus TCP w Twojej sieci lokalnej. Potrzebujesz adresu falownika oraz portu i ID jednostki, gdy port lub ID jednostki nie jest domyślny.
- Niczego więcej. SAJ Local komunikuje się z falownikiem bezpośrednio i nic nie wysyła do usługi w chmurze.

## Instalacja krok po kroku

1. Otwórz SAJ Local w HACS pierwszym przyciskiem poniżej. HACS prosi o dodanie repozytorium, jeśli repozytorium nie jest jeszcze na liście.
2. Pobierz SAJ Local w HACS.
3. Zrestartuj Home Assistanta.
4. Dodaj swój system drugim przyciskiem poniżej albo skorzystaj ze strony [zaczynamy](getting-started.md).

[![Otwórz swoją instancję Home Assistanta i otwórz repozytorium SAJ Local w HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Otwórz swoją instancję Home Assistanta i rozpocznij konfigurację SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local udostępnia karty pulpitu, więc nie trzeba dodawać żadnego zasobu karty. Zobacz [karty pulpitu](cards/README.md).

## Wersje beta

Do pierwszego stabilnego wydania każde wydanie SAJ Local jest wersją beta. W HACS otwórz SAJ Local, otwórz menu, wybierz Pobierz ponownie, włącz „Pokaż wersje beta” i pobierz najnowszą wersję beta. Bez tego przełącznika HACS instaluje wersję rozwojową SAJ Local.
