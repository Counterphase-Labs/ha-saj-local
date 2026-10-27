[en](../../en-gb/developer/environment.md) | [de](../../de/developer/environment.md) | [nl](../../nl/developer/environment.md) | [fr](../../fr/developer/environment.md) | [zh](../../zh-hans/developer/environment.md) | [es](../../es/developer/environment.md) | [it](../../it/developer/environment.md) | pl | [sv](../../sv/developer/environment.md)

# Środowisko deweloperskie

Jak przygotować kopię roboczą i uruchomić deweloperską instancję Home Assistanta z symulatorami.

## Przygotuj kopię roboczą

Kopia robocza potrzebuje [uv](https://docs.astral.sh/uv/) dla narzędzi Pythona, Node.js i npm dla kart, Dockera z Docker Compose dla Home Assistanta i symulatorów oraz `make`. Wymagane wersje są ustawione w `pyproject.toml` i `frontend/package.json`. Po sklonowaniu `make setup` instaluje zależności Pythona, zależności frontendu i przeglądarkę Chromium, której używają testy Playwright.

## Uruchom Home Assistanta

`make up` uruchamia Home Assistanta z integracją i dwoma symulatorami Modbus, HS3 i H2. `make logs` śledzi dziennik Home Assistanta, a `make down` zatrzymuje wszystko.

Home Assistant jest na porcie 8123. Symulator HS3 odpowiada przez Modbus na porcie hosta 5020, a symulator H2 na 5021, natomiast strony symulatorów są na 5080 i 5081. Wewnątrz Dockera Home Assistant dociera do symulatorów po nazwach usług `mock` i `mock-h2` na porcie 502. Prawdziwy falownik nie jest potrzebny. [Strona symulatora](simulator.md) wyjaśnia, jak połączyć się z symulatorami i zmienić to, co symulują.

Aby użyć innych portów hosta, innej strefy czasowej lub innych scenariuszy, skopiuj [compose.override.yaml.example](../../../compose.override.yaml.example) do ignorowanego pliku `compose.override.yaml` i zmień to, co się różni. Nie edytuj `compose.yaml` pod lokalne potrzeby, bo `make mock-smoke` uruchamia także `compose.yaml`.

## Docker

Programowanie odbywa się w kontenerach, aby Home Assistant był znanym, przypiętym wydaniem z czystą konfiguracją. Usługi są zdefiniowane w tych plikach:

- [compose.yaml](../../../compose.yaml): środowisko interaktywne, z Home Assistantem, symulatorem HS3 `mock` i symulatorem H2 `mock-h2`. Integracja jest montowana w Home Assistancie tylko do odczytu, więc kontener nigdy nie zapisuje do drzewa źródeł. Symulatory zachowują swoje zmiany w `mock/state/hs3/` i `mock/state/h2/`, które Git ignoruje.
- [compose.playwright.yaml](../../../compose.playwright.yaml): jednorazowy Home Assistant zbudowany z `Dockerfile.playwright-home-assistant`, z symulatorem HS3, symulatorem H2 i uruchamiaczami Playwright. `make test-browser-home-assistant` używa usług `homeassistant`, `mock`, `mock-h2` i `playwright`, aby udowodnić, że każdy punkt końcowy można dodać, ładuje się, zgłasza wartości sensorów, pokazuje moc słoneczną na karcie przepływu mocy i, gdy sterowanie jest dozwolone, przyjmuje zmienione ustawienie. `make docs-images` używa usług `homeassistant`, `mock-docs`, `mock-h2` i `playwright-docs`, zobacz [Zrzuty ekranu](documentation.md#zrzuty-ekranu). Usługi nie dzielą stanu ze środowiskiem interaktywnym.
- `compose.override.yaml`: porty, strefa czasowa i scenariusze Twojej maszyny. Git ignoruje ten plik, a `compose.override.yaml.example` pokazuje jego kształt.

W `config/` Git śledzi tylko `configuration.yaml` i dwa pulpity demonstracyjne w `config/dashboards/`. Reszta to lokalny stan Home Assistanta.

[Strona sprawdzeń](checks.md) wymienia, co uruchamia każdy cel make, a [strona frontendu](frontend.md#pulpity-demonstracyjne) opisuje dwa pulpity demonstracyjne.
