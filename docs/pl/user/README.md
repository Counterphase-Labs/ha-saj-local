[en](../../en-gb/user/README.md) | [de](../../de/user/README.md) | [nl](../../nl/user/README.md) | [fr](../../fr/user/README.md) | [zh](../../zh-hans/user/README.md) | [es](../../es/user/README.md) | [it](../../it/user/README.md) | pl | [sv](../../sv/user/README.md)

# Dokumentacja użytkownika SAJ Local

SAJ Local to lokalna integracja Home Assistanta. SAJ Local odczytuje system solarny SAJ HS3 lub H2 prosto z falownika przez Modbus TCP w Twojej własnej sieci i, gdy zezwolisz na sterowanie, zmienia ustawienia falownika z Home Assistanta. SAJ Local nie wymaga konta w chmurze i ogranicza liczbę żądań do falownika, aby moduł komunikacyjny falownika nadal działał.

SAJ Local to nieoficjalna integracja tworzona przez społeczność. SAJ nie tworzy, nie wspiera ani nie popiera SAJ Local. Zobacz [zastrzeżenie](#zastrzeżenie).

SAJ Local jest w trakcie rozwoju i nie ma jeszcze opublikowanego wydania. Każda strona poniżej podaje, co nie jest jeszcze obsługiwane. Dokumentacja obejmuje HS3 i H2 i oznacza różnice uwagą, taką jak „tylko HS3”. Zrzuty ekranu pochodzą z symulowanych systemów, więc odczyty nie są prawdziwe.

## Zacznij tutaj

1. [Zainstaluj SAJ Local](installation.md) przez HACS.
2. Sprawdź, czy Twój falownik jest na liście [obsługiwanego wyposażenia](supported-equipment.md).
3. [Zaczynamy](getting-started.md): dodaj swój pierwszy system.
4. Przeczytaj o [wyposażeniu opcjonalnym](optional-equipment.md), które SAJ Local wykrywa za Ciebie.

## Zrozum swój system

- [Encje i prefiks](entities-and-prefix.md): czym są encje, jak powstają ID encji i jak dodać prefiks.
- [Opis encji](entities/README.md): każda encja, z ID encji, modelami, wyposażeniem i ustawieniem domyślnym. Generowany z integracji.
- [Odpytywanie](polling.md): jak często falownik jest odczytywany i jak odczytywać niektóre encje szybciej lub wolniej.
- [Ochrona falownika](protecting-the-inverter.md): limity, których SAJ Local przestrzega przy własnych żądaniach.

## Zmieniaj ustawienia

- [Zmiana ustawień](changing-settings.md): zezwól na sterowanie, zmieniaj ustawienia i używaj EMS.
- [Sterowanie mocą](power-control.md): utrzymuj baterię, przyłącze sieciowe lub falownik na zadanej mocy, ręcznie lub według harmonogramu.
- [Wymiana falownika](replacing-the-inverter.md): przenieś system na nowy falownik albo między H2 a HS3 i zachowaj historię.

## Pulpity

- [Karty pulpitu](cards/README.md): karty, funkcja karty kafelka i odznaka, które SAJ Local dodaje do Home Assistanta.

## Terminy

- [Nazewnictwo](nomenclature.md): terminy SAJ i Home Assistanta, których używają integracja, karty i dokumentacja, wraz z wyjaśnieniem.

## Gdy coś jest nie tak

- [Usterki urządzeń i naprawy](faults-and-repairs.md): usterki zgłaszane przez wyposażenie i problemy do naprawy, które zgłasza SAJ Local.
- [Rozwiązywanie problemów](troubleshooting.md): diagnostyka, rejestrowanie debugowania i gdzie prosić o pomoc.

## Co potrafi każda część

Listy funkcji podają, co jest dziś zbudowane: [integracja](../../../custom_components/saj_local/docs/features.md) i [karty](../../../frontend/docs/features.md).

Dla programistów: zobacz [dokumentację programisty](../developer/README.md).

## Zastrzeżenie

SAJ Local to niezależna integracja tworzona przez społeczność. SAJ Local nie jest powiązany z SAJ (Guangzhou Sanjing Electric Co., Ltd.), a SAJ oraz spółki zależne i podmioty powiązane SAJ nie autoryzowały, nie sponsorowały ani nie poparły SAJ Local.

SAJ, logo SAJ oraz wszystkie powiązane nazwy produktów, nazwy modeli i znaki towarowe są własnością odpowiednich właścicieli. Dokumentacja używa tych nazw wyłącznie do wskazania wyposażenia, z którym działa SAJ Local.

Oprogramowanie jest dostarczane w stanie, w jakim jest, bez gwarancji jakiegokolwiek rodzaju. Używasz SAJ Local na własne ryzyko: autorzy nie ponoszą odpowiedzialności za uszkodzenie sprzętu, utratę danych, utratę gwarancji ani żadne inne skutki używania SAJ Local. Ostrzeżenie dotyczy w szczególności zapisywania ustawień do Twojego falownika.

## Podziękowania

Obsługa H2 opiera się na badaniach rejestrów i testach terenowych stanus74 w [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). Dziękujemy.
