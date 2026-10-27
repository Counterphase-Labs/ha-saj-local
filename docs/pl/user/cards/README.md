[en](../../../en-gb/user/cards/README.md) | [de](../../../de/user/cards/README.md) | [nl](../../../nl/user/cards/README.md) | [fr](../../../fr/user/cards/README.md) | [zh](../../../zh-hans/user/cards/README.md) | [es](../../../es/user/cards/README.md) | [it](../../../it/user/cards/README.md) | pl | [sv](../../../sv/user/cards/README.md)

# Karty pulpitu

Strona Karty pulpitu wyjaśnia, jak dodać karty SAJ Local do pulpitu i wybrać system, oraz wymienia, co pokazuje każdy element. Pełne listy są w sekcjach [Elementy i konfiguracja](../../../../frontend/docs/features.md#elements-and-setup) i [Motyw i język](../../../../frontend/docs/features.md#theme-and-language) listy funkcji kart oraz w sekcji [Karty](../../../../custom_components/saj_local/docs/features.md#cards) listy funkcji integracji.

SAJ Local udostępnia karty i rejestruje karty w Home Assistancie przy jego starcie. Karty pojawiają się w wyborze kart, więc nie trzeba dodawać zasobu ani czyścić pamięci podręcznej.

## Elementy

| Element | Co pokazuje element |
| --- | --- |
| [Karta przepływu mocy](power-flow-card.md) | Bieżąca moc między słońcem, baterią, siecią, domem i wyposażeniem opcjonalnym. |
| [Karta stanu](status-card.md) | Stan pracy, tryb aplikacji, kluczowe odczyty, dzisiejsza energia, podsumowanie usterek i informacja, czy sterowanie jest dozwolone. |
| [Karta usterek](faults-card.md) | Aktywne usterki każdego elementu wyposażenia i przycisk Wyczyść usterkę. |
| [Karta baterii](battery-card.md) | Stan naładowania z zaznaczonymi limitami, odczyty baterii i jedna grupa wierszy dla każdego modułu. |
| [Karta sterowania](controls-card.md) | Ustawienia systemu w sekcjach. |
| [Karta harmonogramu](schedule-card.md) | Przedziały ładowania, rozładowania i ładowarki EV, oś czasu tygodnia i edytor przedziału. |
| [Funkcja kafelka dni tygodnia](weekdays-feature.md) | Siedem przycisków dni na karcie kafelka, dla dni przedziału. |
| [Odznaka stanu](status-badge.md) | Odznaka ze stanem pracy i liczbą elementów wyposażenia z aktywną usterką. |

## Dodaj element

1. Edytuj pulpit i wybierz Dodaj kartę. Dla funkcji dni tygodnia dodaj kartę kafelka i otwórz funkcje karty kafelka. Dla odznaki edytuj odznaki pulpitu.
2. Wybierz element SAJ Local w wyborze. Sześć kart pokazuje podgląd na żywo.
3. Wybierz system w polu System edytora wizualnego. Nowa karta lub odznaka zaczyna od pierwszego systemu. Funkcja dni tygodnia nie ma edytora, bo funkcja używa encji karty kafelka.

Dom z dwoma systemami dodaje kartę raz dla każdego systemu. Tytuł karty to nazwa urządzenia systemu, a po niej model, na przykład SAJ HS3 (12000 W). SAJ Local dodaje numer seryjny tylko wtedy, gdy dwa systemy miałyby w przeciwnym razie identyczny tytuł. Zmień nazwę każdego urządzenia w Home Assistancie, jeśli chcesz innych tytułów.

Elementy znajdują encje systemu przez rejestr encji, a nie po ID encji, więc elementy działają dalej, gdy zmienisz [prefiks](../entities-and-prefix.md#prefiks).

## Co robi każdy element

- **Tylko to, co ma system.** Część, której encja nie istnieje albo jest wyłączona, nie jest rysowana, więc każda karta pokazuje tylko to, co ma system. Część dla jednego modelu pojawia się tylko na tym modelu, a strona każdego elementu wymienia części.
- **Pusta karta mówi dlaczego.** Karta, w której żadna z jej encji nie jest włączona, mówi, jakiego rodzaju encję włączyć, z linkiem do strony urządzenia systemu.
- **System, który nie odpowiada.** Karta mówi o tym i przyciemnia wartości.
- **Dotknij wartości.** Dotknięcie wartości otwiera szczegóły encji w Home Assistancie.
- **Zablokowane elementy sterowania.** Gdy [Zezwól na sterowanie](../changing-settings.md#zezwól-na-sterowanie) jest wyłączone dla systemu, każdy element sterowania jest wyłączony, a kłódka prowadzi do ustawień integracji. Włączenie Zezwól na sterowanie włącza też encje potrzebne kartom, zobacz [zestaw sterowania](../changing-settings.md#zestaw-sterowania).
- **Jedna zmiana na decyzję.** Suwak zmienia falownik, gdy puścisz suwak. Pole liczbowe zmienia falownik po Enter lub po opuszczeniu pola. Lista, przełącznik lub pole czasu zmienia falownik przy zmianie. Element sterowania pokazuje wtedy wartość, którą przechowuje falownik, a odmowa pojawia się pod elementem słowami integracji.

## Motyw i język

Elementy podążają za motywem Home Assistanta. Nazwy encji, wartości i stany używają formatowania i języka Home Assistanta. Teksty kart istnieją po angielsku, niemiecku, niderlandzku, francusku, chińsku uproszczonym, hiszpańsku, włosku, polsku i szwedzku. Pulpit w dowolnym innym języku pokazuje teksty kart po angielsku.

## Jeszcze nieobsługiwane

- Teksty kart w językach innych niż dziewięć powyższych.
