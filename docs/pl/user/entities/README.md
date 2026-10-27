[en](../../../en-gb/user/entities/README.md) | [de](../../../de/user/entities/README.md) | [nl](../../../nl/user/entities/README.md) | [fr](../../../fr/user/entities/README.md) | [zh](../../../zh-hans/user/entities/README.md) | [es](../../../es/user/entities/README.md) | [it](../../../it/user/entities/README.md) | pl | [sv](../../../sv/user/entities/README.md)

# Encje

Każda encja, którą SAJ Local może utworzyć, po jednej stronie dla każdego obszaru. Sekcja [Urządzenia i encje](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) listy funkcji integracji wyjaśnia typy encji, które encje są włączone domyślnie i znak odczytów mocy.

System dostaje tylko encje pasujące do jego modelu, zainstalowanego wyposażenia oraz liczby faz, ciągów paneli i modułów baterii. Kolumna Modele mówi, które modele mają daną encję, a kolumna Wyposażenie i liczba mówi, co musi być zainstalowane.

Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

| Obszar | Encje | Co zawiera |
| --- | --- | --- |
| [Falownik i PV](inverter-and-pv.md) | 241 | Wyjście falownika, ciągi paneli, port awaryjny, liczniki energii, wersje i obciążenie gospodarstwa domowego |
| [Sieć i Licznik A](grid-and-meter-a.md) | 88 | Przyłącze sieciowe i Licznik A, licznik sieci |
| [Licznik B](meter-b.md) | 22 | Licznik B, drugi licznik, który mierzy falownik fotowoltaiczny |
| [Bateria](battery.md) | 133 | Bateria jako całość |
| [Moduły baterii](battery-packs.md) | 58 | Odczyty i tożsamość każdego modułu baterii |
| [Ładowarka EV](ev-charger.md) | 87 | Ładowarka EV i jej elementy sterowania ładowaniem |
| [System równoległy](parallel-system.md) | 63 | Odczyty równoległego systemu maszyn |
| [Ustawienia](settings.md) | 22 | Ustawienia i polecenia, które zmieniają falownik |
| [Usterki](faults.md) | 139 | Usterki zgłaszane przez falownik, baterię i ładowarkę EV |
| [Dodane przez integrację](added-by-the-integration.md) | 7 | Encje, które integracja dodaje poza katalogiem rejestrów |
