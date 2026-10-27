[en](../../en-gb/user/faults-and-repairs.md) | [de](../../de/user/faults-and-repairs.md) | [nl](../../nl/user/faults-and-repairs.md) | [fr](../../fr/user/faults-and-repairs.md) | [zh](../../zh-hans/user/faults-and-repairs.md) | [es](../../es/user/faults-and-repairs.md) | [it](../../it/user/faults-and-repairs.md) | pl | [sv](../../sv/user/faults-and-repairs.md)

# Usterki urządzeń i naprawy

Strona Usterki urządzeń i naprawy wyjaśnia, jak SAJ Local pokazuje usterki zgłaszane przez falownik, baterię i ładowarkę EV oraz jakie problemy do naprawy SAJ Local zgłasza w Home Assistancie. Pełna lista zachowań usterek jest w sekcji [Usterki urządzeń i naprawy](../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) listy funkcji integracji. Każda encja usterki jest w [encjach usterek](entities/faults.md) opisu encji.

Usterki urządzeń i problemy do naprawy to osobne rzeczy. Usterka urządzenia to encja, która zgłasza to, co mówi wyposażenie. Problem do naprawy to kłopot z połączeniem SAJ Local z wyposażeniem albo z konfiguracją SAJ Local, a Home Assistant wymienia go w Ustawienia i Naprawy.

## Usterki urządzeń

Każda nazwana usterka falownika, baterii i ładowarki EV to sensor binarny z klasą urządzenia problem, domyślnie włączony. Usterka ma historię i może uruchomić automatyzację.

- **Podsumowanie:** falownik, bateria i ładowarka EV mają każde usterkę zbiorczą, na przykład Usterka falownika, która jest włączona, gdy wyposażenie zgłasza cokolwiek.
- **Nierozpoznana:** każdy element wyposażenia ma też usterkę nierozpoznaną, która jest włączona, gdy falownik ustawia bit bez udokumentowanego znaczenia. [Pobrana diagnostyka](troubleshooting.md#pobierz-diagnostykę) wymienia rejestr i bit, więc możesz zgłosić bit.
- **Jedno ID encji na każdym modelu:** usterka ma jedno ID encji na każdym modelu, który ją zgłasza. Usterka, której model nie zgłasza, nie ma na tym modelu encji.
- **Moduły baterii:** każdy moduł baterii ma encję usterki i encję ostrzeżenia. HS3 ma jeden moduł. H2 ma do czterech.
- **Wyposażenie, które nie jest zainstalowane:** usterki baterii istnieją tylko wtedy, gdy bateria jest zainstalowana, a usterki ładowarki EV tylko wtedy, gdy ładowarka EV jest zainstalowana. Zobacz [wyposażenie opcjonalne](optional-equipment.md).
- **Rejestr usterek, którego nie można odczytać:** usterki zależne od tego rejestru są niedostępne. SAJ Local nie zgaduje.
- **Dziennik:** usterka, która się włącza, zapisuje jedno ostrzeżenie z nazwą systemu i usterki. Gdy usterka ustępuje, SAJ Local zapisuje jeden wiersz informacyjny.

[Karta usterek](cards/faults-card.md) wymienia aktywne usterki systemu na pulpicie, z informacją, jak dawno każda się zaczęła. Przycisk Wyczyść usterkę na karcie wysyła polecenie Wyczyść bieżącą usterkę, które wymaga [Zezwól na sterowanie](changing-settings.md#zezwól-na-sterowanie).

## Zgłoszenia napraw

SAJ Local zgłasza problem do naprawy dla stanu, na który możesz zareagować.

| Problem do naprawy | Zgłaszany, gdy | Co możesz zrobić |
| --- | --- | --- |
| System ma ustawiony zły model | Falownik pod adresem identyfikuje się jako inny model niż wybrany. | Naprawa przyjmuje model, który znalazł SAJ Local. Zobacz [wymianę falownika](replacing-the-inverter.md). |
| System łączy się teraz z innym falownikiem | Falownik pod adresem ma inny numer seryjny. | Naprawa przyjmuje nowy falownik. Zobacz [wymianę falownika](replacing-the-inverter.md). |
| System łączy się z nierozpoznanym urządzeniem | Typ urządzenia nie jest rozpoznanym modelem. | Wybierz model w Skonfiguruj. SAJ Local używa wtedy modelu jako niezweryfikowanego. |
| System ma odczyty, których falownik odmawia | Falownik odmówił odczytów trzy razy z rzędu. | Naprawa wyłącza wymienione encje, więc SAJ Local przestaje je odczytywać. Zobacz [ochronę falownika](protecting-the-inverter.md#gdy-falownik-odmawia-odczytu). |
| System przestał odpowiadać | Falownik nie odpowiada od 15 minut. | Sprawdź zasilanie, sieć i innych klientów Modbus. Problem znika przy pierwszym poprawnym odczycie. |
| Wyposażenie nie jest już wykrywane | Wyposażenie, które SAJ Local wykrył wcześniej, nie jest już wykrywane. | Sprawdź wyposażenie albo ustaw je na Niezainstalowane w Skonfiguruj. Zobacz [wyposażenie opcjonalne](optional-equipment.md#gdy-zapamiętane-wyposażenie-nie-jest-już-wykrywane). |

![Problem do naprawy w Home Assistancie, który mówi, że SAJ HS3MOCK000000000003 ma odczyty, których falownik odmawia](../../images/pl/faults-and-repairs-repair-issue.png)

Pierwsze trzy problemy to problemy modelu. Dla systemu otwarty jest tylko jeden z problemów modelu, a problem, że system przestał odpowiadać, nie jest zgłaszany, gdy otwarty jest problem modelu.

Problem do naprawy znika, gdy kończy się jego przyczyna albo gdy usuniesz system. Problem odrzuconych odczytów znika też, gdy wyłączysz wymienioną encję.

## Jeszcze nieobsługiwane

- Problem do naprawy dla usterki urządzenia. Usterki urządzeń to encje, a integracja nie zgłasza problemu do naprawy dla usterki.
