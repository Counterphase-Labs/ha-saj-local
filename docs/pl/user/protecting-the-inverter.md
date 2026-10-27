[en](../../en-gb/user/protecting-the-inverter.md) | [de](../../de/user/protecting-the-inverter.md) | [nl](../../nl/user/protecting-the-inverter.md) | [fr](../../fr/user/protecting-the-inverter.md) | [zh](../../zh-hans/user/protecting-the-inverter.md) | [es](../../es/user/protecting-the-inverter.md) | [it](../../it/user/protecting-the-inverter.md) | pl | [sv](../../sv/user/protecting-the-inverter.md)

# Ochrona falownika

Strona Ochrona falownika wymienia limity, których SAJ Local przestrzega przy wszystkim, co wysyła, aby moduł komunikacyjny falownika nadal obsługiwał Home Assistanta. Moduł może przestać obsługiwać klienta, który odpytuje zbyt intensywnie, więc żadne ustawienie nie usuwa limitu. Pełna lista jest w sekcji [Ochrona falownika](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) listy funkcji integracji.

## Limity

- **Jedno połączenie, jedno żądanie naraz.** SAJ Local otwiera jedno połączenie z falownikiem i czeka na każdą odpowiedź przed wysłaniem następnego żądania, z krótką przerwą między żądaniami.
- **40 żądań w dowolnych 60 sekundach.** Limit dotyczy adresu falownika. SAJ Local liczy między przeładowaniami, więc przeładowanie, ponowna próba konfiguracji ani sprawdzenie połączenia nie mogą przekroczyć limitu. Żądanie ponad limit czeka.
- **Sąsiednie rejestry dzielą żądanie.** SAJ Local odczytuje rejestry leżące blisko siebie jednym żądaniem, nigdy poza blokiem opisanym dla modelu. Żądanie nigdy nie jest większe niż 32 rejestry w HS3 lub 56 w H2. Grupowanie encji leżących razem kosztuje mniej, zobacz [odpytywanie](polling.md).
- **Bez ponowień w jednym cyklu.** Po nieudanym odczycie czekanie przed następną próbą podwaja się od najkrótszego odstępu, do 5 minut. Czekanie przetrwa przeładowania. Pierwszy udany cykl odczytuje wszystko od nowa.
- **Każde czekanie ma limit czasu.** Zawieszony falownik kończy cykl jako niepowodzenie i nie zatrzymuje odpytywania. Spóźniona lub zabłąkana odpowiedź jest odrzucana.
- **Zamknięte połączenie jest otwierane raz.** Ten cykl odczytuje wtedy ponownie każdą włączoną encję, więc żadna wartość nie jest starsza niż ponowne połączenie.
- **Najwyżej 20 zmian w 60 sekundach.** Zobacz [zmianę ustawień](changing-settings.md#co-się-dzieje-ze-zmianą). Zmiana ponad limit jest odrzucana i nie trafia do kolejki.

## Gdy falownik odmawia odczytu

Odmowa to odpowiedź, a nie niepowodzenie. Tylko encje z odrzuconego żądania stają się niedostępne, a pozostałe nadal się aktualizują.

1. SAJ Local dzieli odrzucone żądanie na połowy w kolejnych cyklach, aż znajdzie odrzuconą encję.
2. Encja odrzucona trzy razy z rzędu jest zawieszana. Encja pokazuje się jako niedostępna i nie jest już odczytywana.
3. SAJ Local próbuje ponownie zawieszoną encję raz dziennie i przy każdym ładowaniu integracji. Encja wraca, gdy rejestr odpowie.
4. Problem do naprawy wymienia zawieszone encje. Naprawa tego problemu wyłącza encje, więc SAJ Local przestaje je odczytywać na stałe. Zobacz [usterki i naprawy](faults-and-repairs.md#zgłoszenia-napraw).

## Gdy falownik przestaje odpowiadać

Problem do naprawy informuje, że falownik nie odpowiada od 15 minut. Problem znika przy pierwszym poprawnym odczycie. Sprawdź zasilanie falownika i modułu komunikacyjnego, sieć oraz to, czy żaden inny klient Modbus nie zajmuje połączenia.

## Jeszcze nieobsługiwane

- Zmiana limitów. Limity chronią falownik, więc żadne ustawienie nie podnosi limitu.
