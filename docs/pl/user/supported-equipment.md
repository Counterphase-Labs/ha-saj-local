[en](../../en-gb/user/supported-equipment.md) | [de](../../de/user/supported-equipment.md) | [nl](../../nl/user/supported-equipment.md) | [fr](../../fr/user/supported-equipment.md) | [zh](../../zh-hans/user/supported-equipment.md) | [es](../../es/user/supported-equipment.md) | [it](../../it/user/supported-equipment.md) | pl | [sv](../../sv/user/supported-equipment.md)

# Obsługiwane wyposażenie

Strona Obsługiwane wyposażenie wymienia produkty SAJ obsługiwane przez SAJ Local, wyposażenie opcjonalne, które może mieć każdy model, i to, co nie jest jeszcze obsługiwane. Pełna lista tego, co robi konfiguracja, jest w sekcji [Konfiguracja i wykrywanie](../../../custom_components/saj_local/docs/features.md#setup-and-detection) listy funkcji integracji.

## Obsługiwane modele

SAJ Local rozpoznaje model po typie urządzenia zgłaszanym przez falownik. Każdy inny typ urządzenia nie jest rozpoznawany.

| Model | Rozpoznawany jako | Wyposażenie opcjonalne, które wykrywa SAJ Local |
| --- | --- | --- |
| HS3 | Typ urządzenia `0x1610`, trzy fazy | Bateria, Licznik A, Licznik B, Ładowarka EV, system równoległy |
| H2, jedna faza, dwa ciągi paneli | Typ urządzenia `0x005a` | Bateria, Licznik A, Licznik B, system równoległy |
| H2, jedna faza, trzy ciągi paneli | Typ urządzenia `0x005b` | Bateria, Licznik A, Licznik B, system równoległy |

Różnice między modelami, które widać w użyciu:

- **Ładowarka EV:** tylko HS3. H2 nie ma encji ładowarki EV, przedziałów ładowarki EV ani sekcji ładowarki EV na karcie sterowania.
- **Moduły baterii:** H2 ma encje dla maksymalnie pięciu modułów baterii. HS3 ma encje dla jednego modułu baterii. Zobacz [wyposażenie opcjonalne](optional-equipment.md).
- **EMS:** tylko HS3. Zobacz [zmianę ustawień](changing-settings.md#ems).
- **Sterowanie mocą:** HS3 oferuje Baterię, Sieć i Falownik. H2 oferuje tylko Baterię. Zobacz [sterowanie mocą](power-control.md).

[Wyposażenie opcjonalne](optional-equipment.md) wyjaśnia, jak działa wykrywanie i jak je zastąpić. [Opis encji](entities/README.md) wymienia, jakiego modelu i jakiego wyposażenia wymaga każda encja.

## Jeszcze nieobsługiwane

- Automatyczne wykrywanie rozpoznaje tylko trzy typy urządzeń z tabeli. Inne produkty SAJ, takie jak HS2, H1 i AS1, nie są rozpoznawane.
- Inne warianty H2, takie jak trójfazowy H2, zgłaszają inne typy urządzeń i nie są rozpoznawane automatycznie. Możesz wybrać model ręcznie, a SAJ Local oznacza wtedy model jako niezweryfikowany. Odczyty mogą być błędne, bo SAJ Local nie może ich sprawdzić. Zobacz [zaczynamy](getting-started.md#gdy-falownik-nie-jest-rozpoznany).
- Zmiana ustawień w systemie z niezweryfikowanym modelem. Odczyt działa, a każda zmiana jest odrzucana.

## Na czym opiera się obsługa

Obsługa HS3 została zweryfikowana ręcznie na prawdziwym HS3. Obsługa H2 opiera się na dokumentacji protokołu SAJ i zgłoszeniach z terenu i nie została zweryfikowana ręcznie na H2. Zapisywanie ustawień i sterowanie mocą na H2 też opierają się na dokumentacji i zgłoszeniach z terenu.
