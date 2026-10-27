[en](../../en-gb/developer/releasing.md) | [de](../../de/developer/releasing.md) | [nl](../../nl/developer/releasing.md) | [fr](../../fr/developer/releasing.md) | [zh](../../zh-hans/developer/releasing.md) | [es](../../es/developer/releasing.md) | [it](../../it/developer/releasing.md) | pl | [sv](../../sv/developer/releasing.md)

# Wydawanie

Co zrobić przed wydaniem, jak wydanie jest publikowane i jak podnosi się wersję Home Assistanta. Wypchnięcie tagu wersji uruchamia przepływ pracy `Release` w `.github/workflows/release.yml`, który sprawdza tag, uruchamia sprawdzenia i tworzy szkic wydania GitHub.

## Wersje

Wydanie to wydanie GitHub zrobione z tagu wersji na `main`. Tag nie ma prefiksu `v` i jest równy wersji w `custom_components/saj_local/manifest.json`, `pyproject.toml` i `frontend/package.json`. Wydanie stabilne to `X.Y.Z`, a beta to `X.Y.ZbN`, publikowana jako wstępne wydanie GitHub. Bety przed pierwszym wydaniem stabilnym to `1.0.0b1`, `1.0.0b2` i tak dalej, pierwsze wydanie stabilne to `1.0.0`, a Semantic Versioning obowiązuje od `1.0.0`. Uwagi do wydania żyją tylko w wydaniu GitHub, a uwagi bety nazywają każdą zmianę encji, zapisanego ustawienia, typu karty lub ustawienia karty od poprzedniej bety. Zasadę przechowuje sekcja [Wydania](../../../.github/work/requirements.md#releases) wymagań projektu.

## Przed wydaniem

Wykonaj to na `main`, w kolejności.

1. **Uruchom `make ci`.** [Strona sprawdzeń](checks.md) wymienia, co uruchamia `make ci`.
2. **Uruchom `make docs-images`.** Dokumentacja użytkownika pokazuje interfejs, a CI nie generuje obrazów ponownie, więc każde wydanie potrzebuje świeżego zestawu. Cel wymaga Dockera. Uruchom cel, obejrzyj każdy zmieniony obraz, zatwierdź zmienione obrazy w `docs/images/en-gb/` i uruchom `make docs-check`. Uruchomienie, które się nie powiedzie, nie zapisuje żadnego obrazu, więc nie wydawaj z nieudanym uruchomieniem. Przeczytaj [Zrzuty ekranu](documentation.md#zrzuty-ekranu), by dowiedzieć się, co robi uruchomienie i dlaczego każdy odczyt na obrazie jest symulowany.
3. **Skopiuj zrzut ekranu strony w tym samym kroku.** Skopiuj `docs/images/en-gb/cards-power-flow-card.png` do `assets/images/saj-local-power-flow.png` w repozytorium `website` i zatwierdź kopię tam, bo strona SAJ Local na `counterphase.dev` pokazuje kopię obrazu. Żadne sprawdzenie nie wyłapie nieaktualnej kopii, bo CI w tym repozytorium nie widzi repozytorium strony.
4. **Uruchom `make release-check`.** Krok tworzy archiwum z `custom_components/saj_local/` i kończy się niepowodzeniem, gdy w archiwum brakuje `asset-manifest.json` lub zbudowanego pakietu kart. Uruchom `make build` i najpierw zatwierdź pakiet, gdy karty się zmieniły.
5. **Ustaw nową wersję.** Ustaw wersję w `custom_components/saj_local/manifest.json`, `pyproject.toml` i `frontend/package.json`. Uruchom `uv lock`, aby `uv.lock` zapisał wersję projektu, i uruchom `npm install --package-lock-only` w `frontend/`, aby `frontend/package-lock.json` zapisał wersję. Uruchom `make release-check`, zatwierdź na `main` i poczekaj, aż CI przejdzie.

Zrzuty ekranu to jedyna część wydania, której CI nie może sprawdzić. Zmiana, która dodaje lub usuwa obraz, kończy `make docs-check` niepowodzeniem przez reguły nieużywanego i brakującego obrazu. Zmiana interfejsu, która pozostawia obraz nieaktualny, nie powoduje żadnego niepowodzenia, więc to krok 2 utrzymuje obrazy aktualnymi.

## Publikowanie wydania

1. Wypchnij tag: `git tag 1.0.0b1`, a potem `git push origin 1.0.0b1`.
2. Poczekaj na przepływ pracy `Release`. Przepływ pracy wymaga, aby otagowany commit był na `main`, uruchamia `make ci` przez `ci.yml` i tworzy szkic wydania z uwagami wygenerowanymi przez GitHub.
3. Otwórz szkic wydania i zmień wygenerowane uwagi. Dla bety nazwij każdą zmianę encji, zapisanego ustawienia, typu karty lub ustawienia karty od poprzedniej bety.
4. Naciśnij Publish.

Nieudane uruchomienie nie tworzy szkicu. Usuń tag przez `git push origin :refs/tags/<tag>` i `git tag -d <tag>`, napraw `main` i otaguj ponownie.

HACS oferuje opublikowaną betę użytkownikom, którzy włączą „Pokaż wersje beta”, a opublikowane wydanie stabilne każdemu użytkownikowi. Użytkownik bez przełącznika dostaje szczyt `main`, dopóki `1.0.0` nie istnieje, dlatego `main` musi przechodzić `make ci` przed każdym wypchnięciem.

## Podniesienie wersji Home Assistanta

Wersja Home Assistanta jest przypięta w kilku plikach, które trzeba zaktualizować razem, w przeciwnym razie kontener deweloperski, testy przeglądarkowe i uruchomienie zrzutów ekranu, CI, HACS i środowisko testowe rozjadą się:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, środowisko uruchomieniowe deweloperskiego Home Assistanta.
2. `Dockerfile.playwright-home-assistant`: wiersz `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` obrazu, którego używają `make test-browser-home-assistant` i `make docs-images`.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` dla lint i mypy w CI, **oraz** `pytest-homeassistant-custom-component==<pasujące wydanie>`. Środowisko testowe dostarcza własny przypięty `homeassistant`, więc oba przypięcia muszą pochodzić z tego samego wydania Home Assistanta, w przeciwnym razie lint i testy rozwiązują różne rdzenie.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, minimalny rdzeń Home Assistanta, który wymusza HACS.
5. `uv.lock`: uruchom `uv lock` po edycji `pyproject.toml`, aby plik blokady zapisał nowe przypięcia.

Zweryfikuj parowanie w PyPI przed zatwierdzeniem: `requires_dist` pakietu `pytest-homeassistant-custom-component` musi wymieniać to samo `homeassistant==<X.Y.Z>` przypięte w `pyproject.toml`.

Po podniesieniu uruchom `make ci` i `make docs-images`, bo nowa wersja Home Assistanta może zmienić ekrany, które pokazują obrazy.
