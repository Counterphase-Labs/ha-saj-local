[en](../../en-gb/developer/frontend.md) | [de](../../de/developer/frontend.md) | [nl](../../nl/developer/frontend.md) | [fr](../../fr/developer/frontend.md) | [zh](../../zh-hans/developer/frontend.md) | [es](../../es/developer/frontend.md) | [it](../../it/developer/frontend.md) | pl | [sv](../../sv/developer/frontend.md)

# Frontend

Jak pakiet kart jest zorganizowany i budowany oraz jak obejrzeć każdą kartę w instancji deweloperskiej.

Pełna lista tego, co obejmuje frontend, jest w sekcjach listy funkcji [Karty](../../../custom_components/saj_local/docs/features.md#cards) integracji oraz [Elementy i konfiguracja](../../../frontend/docs/features.md#elements-and-setup) i [Motyw i język](../../../frontend/docs/features.md#theme-and-language) kart.

## Kompilacja

Karty, funkcja karty kafelka i odznaka to jeden pakiet Lit i TypeScript w `frontend/`. `make build` uruchamia Vite i zapisuje pakiet w `custom_components/saj_local/frontend/` jako `saj-local-<hash>.js` z `asset-manifest.json`, bo HACS dostarcza katalog integracji jako jedno archiwum. Git śledzi zbudowany pakiet i manifest, więc zmiana kart jest zatwierdzana razem z nową kompilacją. Integracja czyta manifest, udostępnia plik wskazany przez manifest i dodaje URL pliku do frontendu Home Assistanta, więc użytkownicy nie dodają żadnego zasobu pulpitu.

Hash zmienia się z każdą kompilacją, aby przeglądarka nigdy nie uruchamiała nieaktualnego pakietu. Kosztem jest to, że Home Assistant rejestruje nazwę pliku z hashem raz, przy starcie: nowy pakiet wymaga restartu Home Assistanta, zanim przeglądarka dostanie nowy plik. Instancja deweloperska montuje katalog integracji, więc uruchom `make build` i zrestartuj Home Assistanta, aby zobaczyć zmianę.

## Układ źródeł

Układ podąża za tym, co zmienia się razem:

- `src/system/` zawiera wszystko, co nie jest rysowaniem: znajdowanie encji systemu w `hass`, kierunek mocy, dni tygodnia, przedziały harmonogramu, usterki, blokadę sterowania i wywołania usług. Folder nigdy nie dotyka DOM, więc reguły są testowane bez przeglądarki.
- `src/ui/` zawiera części, które rysuje każda karta, stylizowane wyłącznie zmiennymi motywu Home Assistanta, bo frontend Home Assistanta nie obiecuje kartom niestandardowym żadnego elementu `ha-*`.
- `src/cards/`, `src/features/` i `src/badges/` zawierają elementy i rejestrują elementy w wyborze Home Assistanta.
- `src/i18n/` zawiera tekst potrzebny tylko kartom, jeden plik na język, nazwany kodem języka Home Assistanta jak pliki w folderze `translations/` integracji (angielski i osiem języków docelowych), z angielskim jako zapasowym dla każdego innego języka. Nazwy encji, stany i wartości pochodzą z Home Assistanta.
- `tests/fakes/` zawiera atrapę `hass`, zbudowaną z listy encji, oraz zamienniki modułów, których używa element. Każdy test jednostkowy sprawdza jeden moduł, w którym każdy współpracownik jest zastąpiony jedną z atrap.

Element znajduje encje systemu po urządzeniu i kluczu tłumaczenia, nigdy po ID encji, więc karta nigdy nie zależy od prefiksu ID encji.

## Testy

`make test-frontend` uruchamia testy jednostkowe Vitest z bramką pokrycia. `make test-browser-controlled` uruchamia Playwright na zbudowanym pakiecie z kontrolowanymi danymi, a `make test-browser-home-assistant` uruchamia Playwright na prawdziwym Home Assistancie, zobacz [stronę sprawdzeń](checks.md#cele-make). Zrzuty ekranu dokumentacji użytkownika pochodzą z trzeciej konfiguracji Playwright, zobacz [Zrzuty ekranu](documentation.md#zrzuty-ekranu).

## Pulpity demonstracyjne

Obejrzenie każdej karty w każdej opcji wymaga Home Assistanta z prawdziwymi systemami, więc środowisko deweloperskie deklaruje dwa pulpity, `saj-hs3` i `saj-h2`, z `config/dashboards/saj-hs3.yaml` i `config/dashboards/saj-h2.yaml`, przez blok `lovelace: dashboards:` w `config/configuration.yaml`. Pulpity to zwykły YAML pisany ręcznie, a żaden skrypt ich nie generuje. Każdy element SAJ Local to niestandardowy element skonfigurowany własnym YAML, więc każda karta, funkcja kafelka i odznaka jest wypisana osobno z ustawioną każdą opcją, pod nagłówkiem, który nazywa kartę i jej opcje.

- Każdy pulpit ma cztery widoki: Pulpit (karty typowego pulpitu systemu, wypisane jako zwykłe karty), Karty (każda karta w każdej kombinacji opcji), Funkcje i odznaki (karta kafelka z funkcją `custom:saj-local-weekdays-feature` dla każdej encji dni tygodnia przedziału oraz odznaka stanu) i Stany puste (każda karta bez `device` i z urządzeniem czegoś, co nie jest SAJ Local).
- Pulpity zawierają ID urządzeń jednej instancji deweloperskiej. Programista, którego instancja ma inne ID urządzeń, zastępuje dwa ID `device` w każdym pliku, ID systemu i ID urządzenia, które nie jest SAJ Local, dla widoku Stany puste, oraz ID encji dni tygodnia przedziałów, gdy prefiks ID encji jest inny.
- Home Assistant czyta deklaracje pulpitów przy starcie, więc zrestartuj Home Assistanta po zmianie `config/configuration.yaml`. Zmiana pliku pulpitu pokazuje się po przeładowaniu strony.
