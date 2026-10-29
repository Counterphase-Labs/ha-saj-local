[en](../../en-gb/developer/documentation.md) | [de](../../de/developer/documentation.md) | [nl](../../nl/developer/documentation.md) | [fr](../../fr/developer/documentation.md) | [zh](../../zh-hans/developer/documentation.md) | [es](../../es/developer/documentation.md) | [it](../../it/developer/documentation.md) | pl | [sv](../../sv/developer/documentation.md)

# Dokumentacja

Jak strony dokumentacji są zorganizowane, jak powstają opis encji i zrzuty ekranu oraz na czym kończy się niepowodzeniem `make docs-check`.

## Układ

Strony użytkownika są w `docs/en-gb/user/`, a strony programisty w `docs/en-gb/developer/`. Każdy folder ma indeks `README.md`, a każda strona obejmuje jeden temat. Żadna pisana strona nie ma więcej niż 300 wierszy. Każdy fakt ma jednego właściciela, wymienionego w sekcji [Źródła](#źródła), a każda inna strona linkuje do właściciela zamiast powtarzać fakt.

Zrzuty ekranu są w `docs/images/en-gb/`. Każdy obraz musi być przywołany przez stronę.

Pisz strony w brytyjskim angielskim, w tonie głosu Counterphase, i używaj terminów, które tłumaczenia integracji pokazują użytkownikom. Strony użytkownika opisują SAJ ogólnie i w miejscu różnicy zaznaczają, czym różnią się HS3 i H2. Strona nigdy nie dzieli się na jedną stronę dla każdego modelu.

## Najpierw listy funkcji

Trzy listy funkcji są podstawą każdej strony: [integracji](../../../custom_components/saj_local/docs/features.md), [kart](../../../frontend/docs/features.md) i [symulatora](../../../mock/docs/features.md). Sekcja listy funkcji mówi, co jest zbudowane, i wymienia pliki do przeczytania w wierszu `Files:` sekcji. Potwierdź każde stwierdzenie w tych plikach, zanim je udokumentujesz. Dokumenty wymagań mówią, co jest zamierzone, i są czytane tylko dla intencji. Zachowanie, które występuje w dokumencie wymagań, ale w żadnej liście funkcji, nie jest zbudowane, a strona użytkownika nie opisuje go jako dostępnego. Gdy lista funkcji i kod się różnią, użytkownicy dostają to, co robi kod, więc popraw listę funkcji w tej samej zmianie.

Strona, która opisuje kod, linkuje do sekcji listy funkcji, której wiersz `Files:` wymienia kod, i nie powtarza listy plików.

Zmiana możliwości aktualizuje listę funkcji części i każdą stronę użytkownika, która linkuje do zmienionej sekcji, w tej samej zmianie. Zasadę przechowuje główny `AGENTS.md`.

## Wygenerowany opis encji

`docs/en-gb/user/entities/` zawiera jedną wygenerowaną stronę dla każdego obszaru i indeks `README.md`. Uruchom `make docs`, aby wygenerować strony ponownie, a potem zatwierdź wygenerowane strony. Pisane strony nigdy nie wymieniają encji ręcznie; linkują do wygenerowanych stron. Wygenerowane strony są wyłączone z limitu 300 wierszy, bo czytelnicy szukają obszaru, na przykład baterii, zamiast go czytać.

Generatorem jest `.github/scripts/docs_check.py`, uruchamiany z `--write` przez `make docs`. Generator importuje tylko bibliotekę SAJ i czyta `custom_components/saj_local/translations/en.json`, więc nie potrzebuje Home Assistanta. Każda strona obszaru zaczyna się od linku do sekcji listy funkcji, które obejmują obszar, i wiersza o prefiksie ID encji, a potem ma po jednym wierszu dla każdej encji z nazwą z `en.json`, ID encji bez prefiksu, typem, jednostką, modelami, które mają encję, wyposażeniem, które musi być zainstalowane przy dowolnej liczbie faz, ciągów paneli lub modułów baterii, oraz informacją, czy encja jest włączona domyślnie. Encja, którą dwa modele definiują inaczej, na przykład z inną jednostką, dostaje jeden wiersz dla każdej definicji.

### Źródła encji

Każda encja pochodzi z jednego z tych źródeł, a generator czyta wszystkie:

| Źródło | Kod | Encje |
| --- | --- | --- |
| Katalog rejestrów każdego dostarczanego modelu | `catalogue_of` w [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), wywoływane dla każdego profilu w `PROFILES` w [profiles.py](../../../custom_components/saj_local/saj/profiles.py), z pominięciem wierszy, które nie są udostępniane | Sensory, sensory binarne (usterki), liczby, selektory, przełączniki, czasy i przyciski |
| Sensor zezwolenia na sterowanie | `CONTROL_ALLOWED_KEY` w [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, na obu modelach |
| Przełączniki i liczby sterowania mocą | `power_control` każdego profilu ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) i [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), klucze `PowerFunction` w [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) i `FUNCTION_EQUIPMENT` w [power_control.py](../../../custom_components/saj_local/saj/power_control.py), tworzone przez [switch.py](../../../custom_components/saj_local/switch.py) i [number.py](../../../custom_components/saj_local/number.py) | Przełącznik i liczba dla każdej funkcji mocy modelu: bateria na obu modelach, sieć i falownik na HS3 |

`make docs-check` kończy się niepowodzeniem, gdy encji z bloku `entity` w `en.json` nie ma na żadnej stronie obszaru, więc źródło encji, którego generator nie czyta, wychodzi od razu. Nowe źródło wymaga, aby generator je czytał, i wiersza w tabeli powyżej.

### Obszary

Encja trafia do pierwszego pasującego obszaru, w tej kolejności:

1. Encje spoza katalogu: Dodane przez integrację.
2. Sensory binarne z katalogu, czyli usterki: Usterki.
3. Encje z indeksem modułu baterii: Moduły baterii.
4. Encje wyposażenia opcjonalnego: Bateria, Sieć i Licznik A, Licznik B, Ładowarka EV lub System równoległy.
5. Encje z możliwością zapisu bez wyposażenia: Ustawienia.
6. Encje, których klucz zaczyna się od `grid_`: Sieć i Licznik A.
7. Wszystko inne: Falownik i PV.

Tabela `AREAS` w `.github/scripts/docs_check.py` nazywa obszary, ich podsumowania i sekcje listy funkcji, do których linkuje każda strona obszaru.

## Sprawdzenia

`make docs-check` uruchamia `.github/scripts/docs_check.py` bez `--write` i zgłasza jeden wiersz dla każdego ustalenia:

- wygenerowana strona, która różni się od tego, co zapisałoby `make docs`;
- encja w `en.json`, której nie ma na żadnej stronie obszaru, oraz wygenerowana encja bez nazwy w `en.json`;
- względny link, obraz lub kotwica nagłówka, które nie wskazują celu, na stronach, w `README.md`, `CONTRIBUTING.md`, `SECURITY.md` i każdym `AGENTS.md`, łącznie z linkami do list funkcji i dokumentów wymagań;
- obraz w `docs/images/`, do którego nie odwołuje się żadna strona;
- pisana strona ponad 300 wierszy;
- sekcja listy funkcji bez wiersza w [Tabeli pokrycia funkcji](#tabela-pokrycia-funkcji), sekcja wymieniona w tabeli, której lista funkcji nie ma, strona wymieniona w tabeli, która nie istnieje, oraz strona, która nie linkuje do sekcji listy funkcji wskazanej w wierszu, przez kotwicę nagłówka sekcji.

`make docs-check` jest krokiem `make ci`, a GitHub uruchamia `make ci`, więc sprawdzenie nie wymaga zmiany przepływu pracy. Sprawdzenie nie czyta żadnego zrzutu ekranu poza regułami linków i osieroconych obrazów i nie uruchamia przeglądarki.

## Zrzuty ekranu

Każdy zrzut ekranu w `docs/images/<code>/` powstaje przez `make docs-images` z prawdziwego Home Assistanta w Dockerze z językiem użytkownika ustawionym na język folderu albo ze stron symulatorów z tego samego uruchomienia. `make docs-images` uruchamia każdy język, najpierw angielski, ze świeżymi kontenerami dla każdego uruchomienia, a `ARGS=<code>` wybiera jeden język. Żaden zrzut ekranu nie jest edytowany ani robiony ręcznie, więc zestaw można odbudować po każdej zmianie interfejsu. Zrzuty ekranu pokazują symulatory, więc każdy odczyt na zrzucie ekranu jest wartością symulowaną.

Cel uruchamia `tests/playwright/run-docs-images.sh`, który buduje usługi `homeassistant` i `playwright-docs` z [compose.playwright.yaml](../../../compose.playwright.yaml), uruchamia jednorazowego Home Assistanta i dwa symulatory, uruchamia specyfikację, a potem usuwa kontenery, wolumeny i lokalne obrazy. Cel wymaga Dockera, ma ten sam limit czasu co `make test-browser-home-assistant` i przyjmuje opcje przez `ARGS`, które skrypt otrzymuje. Obraz Home Assistanta jest budowany z `Dockerfile.playwright-home-assistant`, który buduje pakiet kart i kopiuje integrację do obrazu, więc żaden kod integracji nie jest montowany. Specyfikacją jest `frontend/tests/browser/docs/screenshots.spec.ts`, skonfigurowana przez `frontend/playwright.docs.config.ts`.

- **Systemy.** HS3 to symulator `mock-docs` na `mock/scenarios/hs3-full-house.yaml`, który ma zainstalowane całe wyposażenie. H2 to symulator `mock-h2` na `mock/scenarios/h2-battery.yaml` z prefiksem encji `h2`. Żaden symulator nie montuje folderu stanu, więc każde uruchomienie zaczyna od scenariusza.
- **Stałe warunki.** Okno ma 1280 na 800 pikseli, motyw jest jasny, a zegar prawdziwy. Wysokie okno dialogowe lub kartę robi się w oknie wysokim na 1600 pikseli, bo stały nagłówek Home Assistanta zasłaniałby górę elementu.
- **Język.** Każde uruchomienie ustawia zarówno język serwera Home Assistanta, przed konfiguracją SAJ Local, aby encje powstały z nazwami w tym języku, jak i język użytkownika, przez kod języka, a nie przez etykietę z listy wyboru języka. Uruchomienie kończy się błędem, gdy nazwa encji SAJ Local nie jest w języku uruchomienia. Obrazy trafiają do `docs/images/<code>/`. Specyfikacja otwiera ekrany przez trasę URL, znajduje pola formularzy SAJ Local po atrybucie `name` i znajduje kontrolki Home Assistanta, które mają tylko tekst, po tekście odczytanym w czasie działania z działającego Home Assistanta przez `hass.localize`. Specyfikacja nie ma tabeli etykiet, więc każdy język wykonuje te same kroki.
- **Nazwy.** Każdy plik nazywa się `<page>-<subject>.png`, gdzie `<page>` to ścieżka strony z `/` zastąpionym przez `-`, na przykład `cards-battery-card.png`, a strona, która pokazuje obraz, linkuje do pliku.
- **Strony symulatorów.** Zrzuty ekranu stron symulatorów pochodzą z dwóch symulatorów tego samego uruchomienia, `mock-docs` i `mock-h2`, i mają prefiks nazwy `developer-simulator-page-`. Są robione na końcu, po każdym zrzucie ekranu Home Assistanta, aby nic zrobione na stronie symulatora nie zmieniło zrzutu Home Assistanta. Specyfikacja ustawia usterkę „Fan 1 fault” na stronie HS3, a rejestr, który zrzut naprawy każe symulatorowi odrzucać, pozostaje odrzucany, więc widok Link, dziennik ruchu i zmiany na pasku stanu pokazują prawdziwe zmiany.
- **Przygotowanie.** Specyfikacja tworzy użytkownika przez API wdrożenia, dodaje HS3 przez przepływ konfiguracji w przeglądarce, dodaje H2 przez API przepływu konfiguracji, włącza Zezwól na sterowanie w obu systemach i dodaje po jednym pulpicie dla każdego systemu z każdą kartą SAJ Local i odznaką stanu, przez API WebSocket Home Assistanta.
- **Wszystko albo nic.** Specyfikacja czeka do dwóch minut, aż oba systemy zgłoszą moc słoneczną. Specyfikacja zapisuje obrazy dopiero po przejściu każdego kroku, więc nieudane uruchomienie zostawia zatwierdzone obrazy bez zmian.
- **Oczekiwanie.** Specyfikacja czeka na ekran, sprawdzając stan, który ekran pokazuje, nigdy przez stały sen.
- **Naprawa.** Zrzut ekranu naprawy pokazuje naprawę odrzuconych rejestrów. Specyfikacja dodaje grupę odpytywania dla temperatury falownika z odstępem 10 sekund, sprawia, że symulator odrzuca ten rejestr przez `POST /api/link` strony symulatora, i czeka do dwóch minut, aż `repairs/list_issues` wymieni problem `registers_refused` SAJ Local. Uruchomienie kończy się niepowodzeniem z komunikatem nazywającym brakujący problem, gdy problem się nie pojawi.
- **Formularze.** Ostrzeżenie o zmianie prefiksu jest zapisywane na zrzucie, a potem formularz jest zamykany, co przerywa przepływ, więc żaden prefiks nie jest zapisany. Ostrzeżenie Zezwól na sterowanie jest zapisywane na zrzucie, a potem potwierdzane, bo karty wymagają dozwolonego sterowania.
- **Niepowodzenia.** Raport HTML jest w `frontend/playwright-report/docs/`, a nieudane uruchomienie zapisuje dziennik Home Assistanta jako `frontend/test-results/docs/home-assistant.log`.

Zrzuty ekranu nie są porównywane piksel po pikselu, ani w CI, ani gdzie indziej. Home Assistant renderuje żywe wartości i czcionki inaczej między uruchomieniami, więc porównanie pikseli zawodziłoby bez prawdziwej zmiany. Zmieniony obraz sprawdź, patrząc na obraz.

### Dodawanie lub zmiana zrzutu ekranu

1. Dodaj lub zmień zrzut w specyfikacji, z nazwą pliku w postaci `<page>-<subject>.png`.
2. Odwołaj się do obrazu ze strony, która wyjaśnia temat.
3. Uruchom `make docs-images`, obejrzyj zmienione obrazy i zatwierdź zmienione obrazy.
4. Uruchom `make docs-check`. Obraz, do którego nie odwołuje się żadna strona, i link do obrazu, który nie istnieje, są zgłaszane.

`make docs-images` nie jest krokiem `make ci`, a CI nie generuje obrazów ponownie. Uruchom cel przed każdym wydaniem, zobacz [stronę wydawania](releasing.md).

## Dodawanie strony

1. Utwórz stronę w `docs/en-gb/user/` lub `docs/en-gb/developer/` i podlinkuj stronę z indeksu folderu.
2. Podlinkuj stronę do sekcji listy funkcji, której wiersz `Files:` wymienia kod opisywany przez stronę.
3. Dodaj stronę do wiersza tej sekcji w Tabeli pokrycia funkcji albo dodaj wiersz. Nowa sekcja listy funkcji potrzebuje wiersza, zanim `make docs-check` przejdzie.
4. Uruchom `make docs-check`.

Utrzymuj strony użyteczne: linkuj do pliku, który przechowuje fakt, zamiast kopiować fakt, zapisuj powód decyzji, bo powody zmieniają się rzadko, a szczegóły ciągle, i trzymaj mało przykładów oraz uruchamiaj każdy przykład ponownie, gdy się zmieni.

## Języki

Dokumentacja istnieje po angielsku i w każdym języku docelowym z [wymagań globalnych](../../../.github/work/requirements.md#language). Listy funkcji i dokumenty wymagań pozostają tylko po angielsku.

- **Układ.** Każdy język ma siostrzane foldery `docs/<code>/user/`, `docs/<code>/developer/` i `docs/images/<code>/`, z tymi samymi nazwami plików w każdym języku. Kody to `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` i `sv`. Blok kodu taki sam w kilku językach zostaje w tekście każdej strony i jest otoczony parą znaczników `jscpd:ignore-start` i `jscpd:ignore-end`, tylko w ramach wyjątku, który użytkownik zatwierdził w planie, jak mówi `AGENTS.md`. Para znaczników otacza jeden blok kodu i nic więcej.
- **Generator.** `make docs` zapisuje `docs/<code>/user/entities/` dla każdego języka z pasującego pliku w `custom_components/saj_local/translations/`. Nazwy wyposażenia pochodzą z tego samego pliku tłumaczeń, a pozostałe teksty generatora z `.github/scripts/docs_text/<code>.json`.
- **Sprawdzenie dokumentacji.** `make docs-check` uruchamia każdą regułę na każdym folderze języka. [Tabela pokrycia funkcji](#tabela-pokrycia-funkcji) na tej stronie dotyczy każdego języka pod tymi samymi nazwami stron, a reguła osieroconych obrazów sprawdza `docs/images/<code>/` względem stron tego samego języka.
- **Pasek języków.** Pierwszy wiersz każdej strony w `docs/<code>/user/` i `docs/<code>/developer/`, łącznie z wygenerowanymi stronami encji, to pasek języków `en | de | nl | fr | zh | es | it | pl | sv`, zawsze w tej kolejności. Każda etykieta poza bieżącym językiem prowadzi do tej samej strony w folderze tego języka, a bieżący język jest zwykłym tekstem. `make docs` zapisuje pasek języków, a `make docs-check` zgłasza stronę, której pierwszy wiersz nie jest oczekiwanym paskiem języków, oraz odnośnik paska do strony, która nie istnieje.
- **Przetłumaczony README.** Plik `README.md` w katalogu głównym repozytorium pozostaje po angielsku i jest przetłumaczony w `docs/<code>/README.md`, którego odnośniki prowadzą do stron w danym języku. Główny `README.md` i każdy `docs/<code>/README.md` mają ten sam pasek języków w pierwszym wierszu, a `make docs-check` zgłasza brakujący `docs/<code>/README.md`.
- **Zrzuty ekranu.** `make docs-images` uruchamia specyfikację raz dla każdego języka, najpierw angielski, ze świeżymi kontenerami dla każdego uruchomienia. `ARGS=<code>` wybiera jeden język, zobacz [Zrzuty ekranu](#zrzuty-ekranu).
- **Nazewnictwo.** Strona `user/nomenclature.md` każdego języka jest listą terminów, których przestrzega każde tłumaczenie integracji, kart i stron języka. Źródłem jest angielska strona [Nazewnictwo](../../en-gb/user/nomenclature.md).
- **Zmiana angielskiego.** Zmiana angielskiego tekstu, strony lub zrzutu ekranu aktualizuje każdy język w tej samej zmianie. Żadne sprawdzenie nie pilnuje zgodności języków.

## Tabela pokrycia funkcji

Każda sekcja listy funkcji jest badana na podstawie wiersza `Files:` sekcji i pokrywana przez strony wymienione tutaj. Każda wymieniona strona linkuje do sekcji przez kotwicę nagłówka sekcji. Nazwa strony jest względna wobec `docs/en-gb/` i linkuje do strony. Tabela znajduje się tylko na angielskiej stronie [Dokumentacja](../../en-gb/developer/documentation.md#feature-coverage-table), a `docs-check` czyta tabelę stamtąd. Tabela obowiązuje w każdym języku dla tych samych nazw stron, a strona dodana, scalona lub podzielona aktualizuje tabelę w tej samej zmianie.

## Źródła

| Fakt | Właściciel |
| --- | --- |
| Co robi SAJ Local, w jednym krótkim podsumowaniu | [indeks użytkownika](../user/README.md) |
| Co może każda część | trzy listy funkcji |
| Obsługiwane modele i wyposażenie | [obsługiwane wyposażenie](../user/supported-equipment.md) |
| Nazwy encji, ID encji, modele, wyposażenie i wartości domyślne | katalog i `translations/en.json`, przez [opis encji](../user/entities/README.md) |
| Typy encji, zasady włączenia domyślnego i konwencje znaku | sekcja Urządzenia i encje listy funkcji integracji |
| Konfiguracja środowiska deweloperskiego | [środowisko](environment.md) |
| Cele make i zasady sprawdzeń | [sprawdzenia](checks.md) |
| Wydawanie i podniesienie wersji Home Assistanta | [wydawanie](releasing.md) |
| Zrzut ekranu przeglądu dla strony | `docs/images/en-gb/cards-power-flow-card.png`, kopiowany przez opiekunów na stronę internetową projektu przy każdym wydaniu, zobacz [stronę wydawania](releasing.md) |
| Jak zgłosić problem z bezpieczeństwem | `SECURITY.md` |
| Etykiety zgłoszeń i zasady dla etykiet | `.github/labels.yml` i `CONTRIBUTING.md` |
| Warunki licencji | `LICENSE` |
| Zamierzone zachowanie produktu | `.github/work/requirements.md` i trzy dokumenty wymagań części |
