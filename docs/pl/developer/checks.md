[en](../../en-gb/developer/checks.md) | [de](../../de/developer/checks.md) | [nl](../../nl/developer/checks.md) | [fr](../../fr/developer/checks.md) | [zh](../../zh-hans/developer/checks.md) | [es](../../es/developer/checks.md) | [it](../../it/developer/checks.md) | pl | [sv](../../sv/developer/checks.md)

# Sprawdzenia

Co uruchamia każdy cel make, jak zawęzić uruchomienie i jakie zasady stosuje każde sprawdzenie.

## Cele make

Każda czynność to cel make, a CI wywołuje te same cele, więc przejście lokalnie i przejście w CI znaczą to samo. Nowy krok CI zaczyna jako cel make. `make help` wymienia każdy cel w jednym wierszu, a `make help ARGS=<target>` opisuje jeden cel: co cel uruchamia, co wypisuje po powodzeniu i po niepowodzeniu, co robi `ARGS` i, dla celu grupującego, jakie kroki cel uruchamia.

`make ci` uruchamia każdy krok sprawdzania i jest definicją ukończenia pracy. GitHub uruchamia samo `make ci` w jednym zadaniu `checks` pliku [ci.yml](../../../.github/workflows/ci.yml), obok wspólnych zadań `roquerodrigo/workflows` (`lint`, `tests`, `validate`) i zadania `hacs`, więc krok dodany do `make ci` działa w GitHubie bez zmiany przepływu pracy. Podczas iteracji uruchamiaj węższe cele.

`make build` to jedyna produkcyjna kompilacja frontendu. `make test` uruchamia każdy zestaw testów, a każdy zestaw ma własny cel, aby można było uruchomić jeden zestaw osobno:

| Cel | Zestaw |
| --- | --- |
| `make test-python` | Testy jednostkowe pytest biblioteki, integracji, symulatora i uruchamiacza sprawdzeń, bez `tests/mock-integration` i `tests/scripts/test_runner_processes.py`, z bramką pokrycia 100 % wierszy i gałęzi. Pełne uruchomienie to dwa uruchomienia pytest do jednego pliku danych pokrycia z rdzeniem `ctrace` i kontekstem pokrycia dla każdego testu: `tests/saj`, `tests/mock` i `tests/scripts` bez wtyczki Home Assistanta i z zablokowanymi gniazdami, a potem `tests/saj-integration` z wtyczką i bramką na połączonych danych. Krok kończy się też niepowodzeniem dla ciała każdego testu, który trwa ponad 200 ms, bez liczenia przygotowania i sprzątania fixture. |
| `make test-frontend` | Testy jednostkowe Vitest kart, z bramką pokrycia. |
| `make test-modules` | Każdy moduł z logiką (dowolna funkcja, metoda lub gałąź) względem samych plików testów jednostkowych przypisanych do modułu, z wymaganym pokryciem 100 % wierszy i gałęzi dla każdego modułu. Bramka czyta dane pokrycia z `make test-python`, więc `make test-modules` najpierw uruchamia `make test-python`. Moduł z logiką i bez pliku testów jednostkowych kończy się niepowodzeniem, a moduł bez logiki, na przykład pusty moduł lub tabela danych, jest pomijany. |
| `make test-isolated` | Testy `tests/saj` i `tests/mock` w środowisku bez Home Assistanta, co dowodzi granicy między biblioteką, symulatorem i Home Assistantem. Pokrycie jest bramkowane na modułach, które testują pliki testów. |
| `make test-runner-processes` | Testy uruchamiacza sprawdzeń z prawdziwymi procesami w `tests/scripts/test_runner_processes.py`, które uruchamiają prawdziwe procesy i są poza pokryciem. |
| `make test-browser-controlled` | Playwright na zbudowanym pakiecie z kontrolowanymi danymi, bez Home Assistanta. |
| `make test-browser-home-assistant` | Playwright na jednorazowym Home Assistancie z symulatorem HS3 i symulatorem H2, co dowodzi, że karty ładują się i działają w prawdziwym frontendzie. Cel najpierw uruchamia `make build` i `make mock-build`, bo obraz Home Assistanta kopiuje pakiet kart z drzewa roboczego, a symulatory używają obrazu `saj-local-mock`. |
| `make mock-smoke` | Kontener symulatora odpowiada klientowi, a potem uruchamiają się testy w `tests/mock-integration`. Cel najpierw uruchamia `make mock-build` i uruchamia scenariusze z obrazu `saj-local-mock`. |

Sprawdzenia, z których składa się `make ci`, mają też po jednym celu, aby można było uruchomić jedno narzędzie osobno:

| Cel | Sprawdzenie |
| --- | --- |
| `make ruff` | `ruff format --check` i `ruff check`. |
| `make mypy` | Ścisłe sprawdzenie typów. |
| `make import-lint` | Kontrakty import-linter. |
| `make complexipy` | Limit złożoności poznawczej. |
| `make copy-paste` | Wykrywanie zduplikowanego kodu i tekstu przez jscpd w całym repozytorium, łącznie z `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Formatowanie, sprawdzenie typów i lint frontendu. |
| `make build` | Produkcyjna kompilacja frontendu przez Vite. |
| `make release-check` | Archiwum HACS zawiera `asset-manifest.json` i zbudowany pakiet kart. Archiwum powstaje z plików w `custom_components/saj_local/`, więc zbudowany pakiet musi być w drzewie. Wersja w `custom_components/saj_local/manifest.json`, `pyproject.toml` i `frontend/package.json` to `X.Y.Z` lub `X.Y.ZbN` i jest taka sama we wszystkich trzech plikach, a tag na `HEAD` jest równy wersji. Bez tagu na `HEAD` porównanie z tagiem jest pomijane. |
| `make freeze-check` | Żaden klucz encji, ID encji, klucz zapisanego ustawienia ani typ karty nie jest usunięty, a żadna platforma encji, jednostka, klasa urządzenia, klasa stanu ani wartość stanu się nie zmienia, w porównaniu z najnowszym tagiem wydania stabilnego. Tagi bet są pomijane, więc beta nigdy nie zamraża powierzchni. Bez tagu wydania stabilnego krok przechodzi. |
| `make docs-check` | Wygenerowany opis encji, linki, obrazy, długość stron, pokrycie listy funkcji i pasek języków. Zobacz [stronę dokumentacji](documentation.md#sprawdzenia). |
| `make template-check` | `bug.yml` wymaga pobrania diagnostyki, każda etykieta, którą szablon zgłoszenia stosuje lub linkuje, istnieje w `.github/labels.yml`, a lista rozwijana modeli w `bug.yml` zgadza się z modelami w `translations/en.json`. |
| `make mock-build` | Obraz symulatora się buduje i nie zawiera bytecode. |
| `make validate` | hassfest na drzewie roboczym, w Dockerze. Walidacja HACS czyta wypchnięte repozytorium, więc tylko zadanie `hacs` przepływu pracy uruchamia walidację HACS. |

`make lint`, `make python-ci`, `make frontend-check` i `make frontend-ci` uruchamiają grupy tych celów.

Cztery kolejne cele nie są sprawdzeniami. `make setup` instaluje zależności Pythona i frontendu oraz Chromium, `make docs` generuje ponownie opis encji, `make docs-images` robi zrzuty ekranu dokumentacji, najpierw uruchamia `make build` i `make mock-build` jak test przeglądarkowy Home Assistanta i nie jest krokiem `make ci`, a `make up`, `make down` i `make logs` uruchamiają deweloperskiego Home Assistanta, zobacz [stronę środowiska](environment.md#uruchom-home-assistanta).

Każdy cel działa przez uruchamiacz sprawdzeń w `.github/scripts/`. Uruchamiacz wypisuje jeden wiersz `[x]` lub `[ ]` dla każdego kroku, ustalenia nieudanego kroku jako `file:line message` i końcowy wiersz wyniku. Uruchamiacz wykonuje każdy wybrany krok nawet po niepowodzeniu jednego i zgłasza przekroczenie czasu, sygnał lub brakujące narzędzie jako takie. Każdy krok ma limit czasu. Zwięzłe wyjście istnieje po to, aby człowiek lub agent czytał tylko to, co potrzeba do naprawy niepowodzenia.

Akcje GitHub Actions są przypięte do skrótu commita, aby przeniesiony tag nie mógł zmienić tego, co uruchamia CI.

## Opcje

- `ARGS="..."` przekazuje ścieżki i opcje do celu jednego narzędzia, na przykład `make test-python ARGS="tests/saj/test_poller.py -k decode"` lub `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<target>` mówi, co `ARGS` robi dla każdego celu.
- `ONLY=<step,...>` uruchamia podzbiór kroków celu grupującego, na przykład `make ci ONLY=ruff,mypy`. Nazwa, której cel nie uruchamia, jest błędem.
- `V=1` strumieniuje surowe wyjście narzędzia i wyłącza dla tego uruchomienia oszczędną konfigurację narzędzi i ustawienia środowiska.

## Pokrycie uruchomienia podzbioru

Pełne `make test-python` mierzy i bramkuje cały pakiet. Gdy `ARGS` wybiera pliki lub foldery testów, cel mierzy pokrycie tylko dla modułów, które testują pliki testów, dodaje do uruchomienia inne pliki testów jednostkowych przypisane do tych modułów i stosuje tę samą bramkę 100 % do tych modułów. Uruchomienie `tests/saj-integration/test_coordinator_write.py` uruchamia więc także `test_coordinator.py` i `test_coordinator_power.py` i bramkuje `coordinator.py`. Modułem jest plik o nazwie pliku testów bez prefiksu `test_`, wyszukiwany według folderu testów:

[Tabela folderów testów i folderów modułów](../../en-gb/developer/checks.md#coverage-of-a-subset-run) znajduje się na stronie angielskiej.

Pliki testów bez modułu o tej samej nazwie są wymienione w `.github/scripts/pytest_scope.json`, każdy z modułami, które plik testuje, a plik testów bez znanego modułu jest odrzucany, dopóki nie zostanie dodany tam. Mapowanie folderów jest w `.github/scripts/pytest_scope.py`. Wybieranie testów przez `-k`, `-m` lub `--lf` wymaga pliku testów w `ARGS`, aby pokrycie można było bramkować na module, który plik testuje.

Pełne `make test-python` zapisuje, który test uruchomił każdy wiersz i gałąź (kontekst pokrycia dla każdego testu), więc jedno uruchomienie zasila obie bramki. Rdzeń `ctrace` jest ustawiany tylko dla pełnego uruchomienia, w środowisku jego poleceń, bo domyślny rdzeń `sysmon` zapisuje wiersz dla pierwszego testu, który go uruchamia, i dlatego zostawia późniejsze testy bez kontekstu. To samo pełne uruchomienie mierzy czas ciała każdego testu, a każde ciało powyżej 200 ms kończy krok niepowodzeniem z ID testu i czasem. 200 ms pod pokryciem to około 50 ms w zwykłym uruchomieniu, powyżej 125 ms, które osiągają zdrowe testy pod pokryciem, więc bramka nie zawodzi losowo. Uruchomienie podzbioru zachowuje rdzeń `sysmon`, nie zapisuje kontekstów i nie stosuje bramki czasu.

`test-modules` działa w `make ci` i bramkuje każdy moduł na 100 % pokrycia wierszy i gałęzi z samych plików testów jednostkowych przypisanych do modułu. Bramka liczy tylko konteksty tych plików testów i kod uruchamiany przy imporcie modułu, więc pokrycie z testów innych modułów się nie liczy. `test-modules` czyta dane pokrycia z `test-python`, więc samo `make test-modules` najpierw uruchamia `test-python`, a `make ci` uruchamia testy raz. Moduł z logiką i bez pliku testów jednostkowych kończy krok niepowodzeniem, a moduł bez logiki jest pomijany, bo wymagania zabraniają testów stałych. Moduł, który przechodzi bramkę tylko w pełnym uruchomieniu `test-python`, oznacza, że inne testy pokrywają moduł przypadkiem, i to jest prawdziwa luka do naprawy. `test-isolated` bramkuje pokrycie tak samo jak każde uruchomienie podzbioru.

## Testowanie

Zasady są w [sekcji Testowanie wymagań globalnych](../../../.github/work/requirements.md#testing). Powody:

- **Pokrycie liczy tylko testy jednostkowe.** Test, który łączy prawdziwe moduły, podnosi wynik, nie dowodząc żadnego z modułów osobno.
- **Testy jednostkowe są szybkie i izolowane.** Bez gniazd, serwerów, plików fixture, prawdziwego czasu i długich symulacji. Czas, losowość i wejście-wyjście są w całym kodzie wstrzykiwane z tego powodu.
- **Testy integracyjne dowodzą tylko, że części się łączą.** Dla symulatora testem integracyjnym jest `make mock-smoke`.
- **Żadnych obejść w kodzie** sprawdzeń lintu, typów ani pokrycia. Zmień konfigurację, gdzie decyzja jest widoczna, albo przebuduj kod.
- **Sprawdzaj zachowanie, nie stałe.** Test, który powtarza adres rejestru, niczego nie dowodzi.

`tests/` zawiera dokładnie sześć folderów:

- `tests/saj`: testy jednostkowe biblioteki SAJ.
- `tests/saj-integration`: testy jednostkowe integracji Home Assistanta, a nie testy integracyjne.
- `tests/mock`: testy jednostkowe symulatora Modbus, z `profiles/` i `simulation/`.
- `tests/mock-integration`: skrypt smoke kontenera i test dostarczonych scenariuszy symulatora.
- `tests/playwright`: skrypty Dockera dla testów przeglądarkowych.
- `tests/scripts`: testy jednostkowe uruchamiacza sprawdzeń i jego testy z prawdziwymi procesami w `test_runner_processes.py`.

`tests/mock-integration` i `tests/scripts/test_runner_processes.py` są poza uruchomieniem jednostkowym i poza pokryciem.

## Stos

| Element | Dlaczego |
| --- | --- |
| Python z `uv` | Jeden plik blokady, te same instalacje lokalnie i w CI. |
| Ruff, wszystkie reguły włączone | Każdy wyjątek to widoczna decyzja w `[tool.ruff.lint]`. |
| mypy | Dekodowanie rejestrów sprzyja błędom skalowania, znaku i szerokości, które typy wyłapują. |
| import-linter | Sprawia, że granice ze [strony architektury](architecture.md#jak-projekt-jest-podzielony) są niepowodzeniem sprawdzenia. |
| complexipy, jscpd | Kod map rejestrów rośnie przez duplikację; limity zatrzymują ten wzrost. |
| pytest, 100 procent pokrycia gałęzi | Zobacz [Testowanie](#testowanie). |
| Lit, TypeScript, Vite | Frontend Home Assistanta to Lit, więc karty nie potrzebują drugiego frameworka. |
| Playwright | Steruje kartami w prawdziwej przeglądarce i w prawdziwym Home Assistancie oraz robi [zrzuty ekranu dokumentacji](documentation.md#zrzuty-ekranu). |
| Docker Compose | Zobacz [stronę środowiska](environment.md#docker). |

Home Assistant jest przypięty w kilku plikach, które muszą się zmieniać razem, w przeciwnym razie lint i testy działają na różnych rdzeniach. Kroki są na [stronie wydawania](releasing.md#podniesienie-wersji-home-assistanta).
