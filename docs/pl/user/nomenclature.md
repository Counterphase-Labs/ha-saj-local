[en](../../en-gb/user/nomenclature.md) | [de](../../de/user/nomenclature.md) | [nl](../../nl/user/nomenclature.md) | [fr](../../fr/user/nomenclature.md) | [zh](../../zh-hans/user/nomenclature.md) | [es](../../es/user/nomenclature.md) | [it](../../it/user/nomenclature.md) | pl | [sv](../../sv/user/nomenclature.md)

# Nazewnictwo

Terminy, których używają SAJ Local, karty pulpitu i dokumentacja, każdy z jednozdaniowym wyjaśnieniem. Każde tłumaczenie integracji, kart i dokumentacji używa jednego terminu dla każdej wymienionej tu rzeczy. Sekcja [Języki](../../../custom_components/saj_local/docs/features.md#languages) listy funkcji integracji podaje języki, w których SAJ Local jest dostępny.

## Urządzenia SAJ i odczyty

| Termin | Znaczenie |
| --- | --- |
| Falownik | Urządzenie SAJ, które zamienia prąd stały z paneli słonecznych i baterii na prąd przemienny dla domu i sieci. |
| HS3 | Hybrydowy falownik SAJ HS3, model trójfazowy. |
| H2 | Hybrydowy falownik SAJ H2, model jednofazowy. |
| Model | Typ falownika, według którego SAJ Local wybiera listę rejestrów: Automatyczny, HS3 lub H2. |
| Automatyczny | Wybór modelu, który rozpoznaje model po typie urządzenia zgłaszanym przez falownik. |
| Wyposażenie opcjonalne | Wyposażenie, które instalacja może mieć lub nie: bateria, Licznik A, Licznik B, ładowarka EV albo system równoległy. |
| Zainstalowane | Ustawienie, które informuje SAJ Local, że element wyposażenia opcjonalnego jest zainstalowany. |
| Niezainstalowane | Ustawienie, które informuje SAJ Local, że element wyposażenia opcjonalnego nie jest zainstalowany. |
| Bateria | Magazyn energii podłączony do falownika. |
| Moduł baterii | Jeden moduł baterii, pokazywany jako Moduł z numerem. |
| Stan naładowania | Poziom naładowania baterii w procentach. |
| Rezerwa | Naładowanie baterii, które falownik zachowuje i poniżej którego jej nie rozładowuje. |
| Słońce | Moc wytwarzana przez panele słoneczne. |
| Ciąg paneli | Jedna grupa paneli słonecznych połączonych szeregowo i podłączonych do jednego wejścia falownika. |
| Faza | Jeden przewód zasilania prądem przemiennym. |
| Sieć | Publiczna sieć elektroenergetyczna, do której podłączony jest dom. |
| Pobór | Pobieranie mocy z sieci. |
| Oddawanie | Wysyłanie mocy do sieci. |
| Ładowanie | Wprowadzanie mocy do baterii. |
| Rozładowanie | Pobieranie mocy z baterii. |
| Dom | Moc, którą zużywa dom. |
| Odbiory awaryjne | Odbiory, które pozostają zasilane z baterii i paneli słonecznych, gdy zabraknie zasilania z sieci. |
| Licznik A | Pierwszy licznik energii, który można podłączyć do falownika. |
| Licznik B | Drugi licznik energii, który można podłączyć do falownika. |
| Ładowarka EV | Ładowarka pojazdów elektrycznych podłączona do falownika. |
| System równoległy | Kilka falowników pracujących razem jako jeden system. |
| Usterka | Problem zgłaszany przez urządzenie, z rejestrem i bitem. |
| Wyczyść usterkę | Przycisk, który prosi falownik o skasowanie zgłoszonej usterki. |
| Stan pracy | Stan, w którym znajduje się falownik, na przykład praca lub czuwanie. |
| Tryb | Tryb pracy falownika, na przykład taryfa czasowa. |
| Taryfa czasowa | Tryb, w którym bateria ładuje się i rozładowuje w ustawionych przez Ciebie przedziałach. |
| Przedział | Jeden okres harmonogramu taryfy czasowej dla ładowania, rozładowania lub ładowarki EV. |
| EMS | Funkcje systemu zarządzania energią falownika, które utrzymują zadaną moc z zewnątrz. |
| Sygnał życia EMS | Jak często SAJ Local odczytuje wartości zadane EMS, aby funkcje EMS pozostały aktywne. |
| Limit czasu EMS | Czas, po którym falownik kończy funkcję EMS, która nie jest podtrzymywana. |
| Ochrona przed prądem zwrotnym | Zabezpieczenie falownika przed przepływem mocy z powrotem do falownika, które funkcje EMS wyłączają. |
| Sterowanie mocą | Utrzymywanie baterii, przyłącza sieciowego lub falownika na zadanej mocy. |
| Moc zadana | Moc, którą utrzymuje funkcja sterowania mocą. |
| Harmonogram | Godziny, w których działa funkcja sterowania mocą. |
| Zezwól na sterowanie | Ustawienie, które pozwala Home Assistantowi zmieniać ustawienia falownika. |
| Sterowanie | Możliwość zmiany ustawień falownika, w przeciwieństwie do samego odczytu. |
| Rejestr | Numerowane miejsce w pamięci falownika, które przechowuje jeden odczyt lub jedno ustawienie. |
| Odrzucony rejestr | Rejestr, na który falownik odmawia odpowiedzi. |
| Modbus TCP | Protokół sieciowy, którego SAJ Local używa do komunikacji z falownikiem. |
| Host | Adres sieciowy falownika. |
| Port | Port sieciowy falownika, domyślnie 502. |
| ID jednostki | Adres Modbus falownika, od 1 do 247. |
| Moduł komunikacyjny | Część falownika, która odpowiada na żądania sieciowe. |
| Blok | Zakres rejestrów odczytywany jednym żądaniem. |
| Czas rzeczywisty | Blok odczytów, które zmieniają się z sekundy na sekundę. |
| Średnie pięciominutowe | Blok odczytów, które falownik uśrednia w ciągu pięciu minut. |
| Energia | Blok odczytów wyprodukowanej i zużytej energii, na przykład energii z dzisiaj. |
| Tożsamość | Model, numer seryjny i wersje zgłaszane przez falownik. |

## Pojęcia SAJ Local

| Termin | Znaczenie |
| --- | --- |
| System | Jeden falownik wraz z wyposażeniem, dodany do Home Assistanta. |
| Instalacja | Jeden wpis konfiguracji SAJ Local, czyli jeden system. |
| Prefiks | Opcjonalny tekst dodawany do identyfikatorów encji jednej instalacji, używany, gdy jest więcej niż jeden system. |
| Odpytywanie | Odczytywanie falownika w odstępach czasu. |
| Grupa odpytywania | Wybrany zestaw encji, które SAJ Local odczytuje szybciej lub wolniej niż domyślny odstęp. |
| Odstęp aktualizacji | Liczba sekund między dwoma odczytami falownika, pokazywana jako „Sekundy między aktualizacjami”. |
| Obciążenie żądaniami | Liczba żądań na minutę, które SAJ Local wysyła do falownika, wobec limitu 40 na 60 sekund. |
| Budżet | Limit obciążenia żądaniami. |
| Wymiana modelu | Przeniesienie systemu na nowy falownik albo między H2 a HS3 z zachowaniem historii. |
| Niezweryfikowany | Model wybrany ręcznie, którego nie dało się sprawdzić z typem urządzenia. |
| Pobranie diagnostyki | Plik z bezpiecznym dla prywatności zrzutem stanu systemu do zgłoszenia błędu. |
| Rejestrowanie debugowania | Opcja, która zapisuje szczegółowe wiersze dziennika do szukania problemu. |
| Karta pulpitu | Karta, którą SAJ Local dodaje do pulpitów Home Assistanta. |
| Karta przepływu mocy | Karta, która pokazuje bieżący przepływ mocy między słońcem, baterią, siecią i domem. |
| Karta stanu | Karta, która pokazuje stan pracy, tryb, kluczowe odczyty i usterki. |
| Karta usterek | Karta, która wymienia aktywne usterki. |
| Karta baterii | Karta, która pokazuje odczyty baterii i jeden wiersz dla każdego modułu. |
| Karta sterowania | Karta, która pokazuje wspólne elementy sterowania systemu. |
| Karta harmonogramu | Karta, która pokazuje przedziały z osią czasu tygodnia. |
| Funkcja kafelka dni tygodnia | Siedem przycisków dni, które można dodać do karty kafelka. |
| Odznaka stanu | Odznaka, która pokazuje stan pracy i liczbę aktywnych usterek. |

## Pojęcia Home Assistanta

| Termin | Znaczenie |
| --- | --- |
| Home Assistant | Oprogramowanie do automatyzacji domu, którego integracją jest SAJ Local. |
| Integracja | Oprogramowanie, które łączy rodzaj urządzenia lub usługi z Home Assistantem. |
| HACS | Home Assistant Community Store, służy do instalacji SAJ Local. |
| Niestandardowe repozytorium | Repozytorium, którego nie ma na domyślnej liście HACS i które dodaje się do HACS przez jego adres; plakietka „HACS niestandardowe” w plikach README oznacza SAJ Local jako takie repozytorium. |
| Przepływ konfiguracji | Okno konfiguracji, które dodaje system. |
| Wpis konfiguracji | Zapisana konfiguracja jednego systemu. |
| Podwpis | Część wpisu konfiguracji, którą dodaje się i zmienia osobno, na przykład grupa odpytywania lub harmonogram mocy. |
| Skonfiguruj | Przycisk integracji, który otwiera jej opcje. |
| Urządzenia i usługi | Strona ustawień Home Assistanta, która wymienia integracje, urządzenia i encje. |
| Ustawienia | Strona Home Assistanta do konfigurowania Home Assistanta. |
| Urządzenie | Zapis Home Assistanta o jednym elemencie wyposażenia, który zawiera encje. Każdy system to jedno urządzenie. |
| Encja | Jeden odczyt, jedno ustawienie lub jedno polecenie, które pokazuje Home Assistant. |
| ID encji | Unikalny identyfikator encji, na przykład sensor.saj_pv_power. |
| Sensor | Encja, która pokazuje odczyt. |
| Sensor binarny | Encja, która jest włączona albo wyłączona, na przykład usterka. |
| Liczba | Encja z liczbą, którą można zmienić. |
| Selektor | Encja z jednym wyborem z listy. |
| Przełącznik | Encja, którą można włączyć lub wyłączyć. |
| Czas | Encja z porą dnia. |
| Przycisk | Encja, która po naciśnięciu wykonuje akcję. |
| Włączona domyślnie | Czy encja jest włączona po dodaniu systemu. |
| Wyłączona | Encja, której Home Assistant nie odczytuje ani nie pokazuje. |
| Naprawa | Powiadomienie w Home Assistancie, że coś wymaga Twojego działania, z przyciskiem Napraw. |
| Pulpit | Ekran Home Assistanta złożony z kart. |
| Karta | Jeden blok na pulpicie. |
| Karta kafelka | Karta Home Assistanta, która pokazuje jedną encję i do której można dodawać funkcje. |
| Odznaka | Mały element w rzędzie odznak u góry pulpitu. |
| Automatyzacja | Reguła, która sprawia, że Home Assistant działa, gdy coś się wydarzy. |
| Pomocnik | Encja Home Assistanta, którą tworzysz sam, na przykład pomocnik harmonogramu. |
| Obszar | Pomieszczenie lub miejsce, w którym grupuje się urządzenia. |
| Motyw | Kolory interfejsu Home Assistanta. |
| Język | Język, który użytkownik Home Assistanta wybiera na stronie profilu. |
| Przeładowanie | Ponowne uruchomienie jednej integracji bez restartu Home Assistanta. |
| Restart | Ponowne uruchomienie Home Assistanta. |
| Narzędzia deweloperskie | Strony Home Assistanta do sprawdzania stanów i wywoływania akcji. |
| Dziennik | Zapis komunikatów Home Assistanta. |
