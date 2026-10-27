[en](../../en-gb/user/replacing-the-inverter.md) | [de](../../de/user/replacing-the-inverter.md) | [nl](../../nl/user/replacing-the-inverter.md) | [fr](../../fr/user/replacing-the-inverter.md) | [zh](../../zh-hans/user/replacing-the-inverter.md) | [es](../../es/user/replacing-the-inverter.md) | [it](../../it/user/replacing-the-inverter.md) | pl | [sv](../../sv/user/replacing-the-inverter.md)

# Wymiana falownika

Strona Wymiana falownika wyjaśnia, jak przenieść system na nowy falownik albo między H2 a HS3 i zachować urządzenie, encje i historię. Pełna lista jest w sekcji [Wymiana modelu](../../../custom_components/saj_local/docs/features.md#model-replacement) listy funkcji integracji.

## Przenieś system celowo

1. Upewnij się, że nowy falownik jest osiągalny. Jeśli nowy falownik ma inny adres, wpisujesz adres w następnym kroku.
2. Otwórz Skonfiguruj, czyli koło zębate w wierszu systemu na stronie integracji SAJ Local.
3. Zmień host, port lub ID jednostki, jeśli adres się zmienił. Zostaw Model na Automatyczny albo wybierz model, jeśli falownik nie jest rozpoznany.
4. Wybierz Zatwierdź, a potem potwierdź wymianę. Potwierdzenie podaje model i numer seryjny, które znalazł SAJ Local.

Po potwierdzeniu urządzenie, encje, nazwy encji i historia zostają przy systemie. Encja zachowuje historię po przeniesieniu, gdy oba modele mają tę encję. SAJ Local zapomina wyposażenie wykryte na starym falowniku i liczbę modułów baterii starego falownika i wykrywa wyposażenie ponownie na nowym falowniku.

## Gdy falownik pod adresem zmienia się bez Twojego udziału

SAJ Local sprawdza tożsamość falownika przy każdym ładowaniu systemu. Gdy falownik pod adresem identyfikuje się jako inny model albo ma inny numer seryjny, SAJ Local nie ładuje systemu i zgłasza problem do naprawy. Naprawa tego problemu pokazuje model i numer seryjny, które falownik zgłasza teraz, i przyjmuje falownik, który potwierdzisz.

- ID encji, historia, Zezwól na sterowanie i każde inne ustawienie pozostają bez zmian.
- Gdy falownik zgłasza coś innego, niż pokazał formularz, formularz mówi o tym i pokazuje nowe wartości zamiast zapisywać stare.
- Gdy urządzenie pod adresem nie jest rozpoznanym modelem, problem do naprawy mówi o tym i wskazuje Skonfiguruj. Nie ma czego przyjąć. Wybierz model ręcznie, zobacz [zaczynamy](getting-started.md#gdy-falownik-nie-jest-rozpoznany).

Problemy do naprawy są wymienione w [usterkach i naprawach](faults-and-repairs.md#zgłoszenia-napraw).

## Jeszcze nieobsługiwane

- Przyjęcie falownika, który już należy do innego systemu. SAJ Local odrzuca przyjęcie.
