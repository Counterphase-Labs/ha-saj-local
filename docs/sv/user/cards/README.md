[en](../../../en-gb/user/cards/README.md) | [de](../../../de/user/cards/README.md) | [nl](../../../nl/user/cards/README.md) | [fr](../../../fr/user/cards/README.md) | [zh](../../../zh-hans/user/cards/README.md) | [es](../../../es/user/cards/README.md) | [it](../../../it/user/cards/README.md) | [pl](../../../pl/user/cards/README.md) | sv

# Instrumentpanelskort

Sidan Instrumentpanelskort förklarar hur du lägger till SAJ Local-korten på en instrumentpanel och väljer ett system, och listar vad varje element visar. De fullständiga listorna finns i avsnitten [Element och inställning](../../../../frontend/docs/features.md#elements-and-setup) och [Tema och språk](../../../../frontend/docs/features.md#theme-and-language) i kortens funktionslista, och i avsnittet [Kort](../../../../custom_components/saj_local/docs/features.md#cards) i integrationens funktionslista.

SAJ Local levererar korten och registrerar korten hos Home Assistant när Home Assistant startar. Korten visas i kortväljaren, så det finns ingen resurs att lägga till och ingen cache att rensa.

## Element

| Element | Vad elementet visar |
| --- | --- |
| [Effektflödeskort](power-flow-card.md) | Live-effekt mellan sol, batteri, nät, hem och den valfria utrustningen. |
| [Statuskort](status-card.md) | Driftläget, läget, viktiga avläsningar, dagens energi, en felsammanfattning och om styrning är tillåten. |
| [Felkort](faults-card.md) | De aktiva felen för varje del av utrustningen, och en knapp Rensa fel. |
| [Batterikort](battery-card.md) | Laddningsnivån med gränserna markerade, batteriavläsningarna och en radgrupp för varje pack. |
| [Styrkort](controls-card.md) | Systemets inställningar i sektioner. |
| [Schemakort](schedule-card.md) | Tidsluckorna för laddning, urladdning och elbilsladdare, en veckotidslinje och en tidsluckeditor. |
| [Veckodagar som funktion för bricka](weekdays-feature.md) | Sju dagknappar på ett brickkort, för en tidsluckas dagar. |
| [Statusmärke](status-badge.md) | Ett märke med driftläget och antalet delar av utrustningen med ett aktivt fel. |

## Lägg till ett element

1. Redigera en instrumentpanel och välj Lägg till kort. För funktionen veckodagar lägger du till ett brickkort och öppnar brickkortets funktioner. För märket redigerar du instrumentpanelens märken.
2. Välj SAJ Local-elementet i väljaren. De sex korten visar en live-förhandsvisning.
3. Välj systemet i fältet System i det visuella redigeringsverktyget. Ett nytt kort eller märke börjar med det första systemet. Funktionen veckodagar har inget redigeringsverktyg, eftersom funktionen använder brickkortets entitet.

Ett hem med två system lägger till ett kort per system. Ett korts titel är systemets enhetsnamn följt av modellen, till exempel SAJ HS3 (12000 W). SAJ Local lägger till serienumret bara när två system annars skulle få identiska titlar. Byt namn på varje enhet i Home Assistant om du vill ha andra titlar.

Elementen hittar ett systems entiteter via entitetsregistret, och inte via entitets-ID, så elementen fortsätter fungera när du ändrar ett [prefix](../entities-and-prefix.md#prefixet).

## Vad varje element gör

- **Bara det systemet har.** En del vars entitet inte finns eller är inaktiverad ritas inte, så varje kort visar bara det systemet har. En del för en modell visas bara på den modellen, och varje elementsida anger delarna.
- **Ett tomt kort säger varför.** Ett kort där ingen av kortets entiteter är aktiverad anger vilken sorts entitet du ska aktivera, med en länk till systemets enhetssida.
- **Ett system som inte svarar.** Ett kort säger det och tonar ned värdena.
- **Tryck på ett värde.** Ett tryck på ett värde öppnar entitetens detaljer i Home Assistant.
- **Låsta styrningar.** Medan [Tillåt styrning](../changing-settings.md#tillåt-styrning) är av för systemet är varje styrning inaktiverad och ett lås länkar till integrationens inställningar. Att slå på Tillåt styrning aktiverar också de entiteter som korten behöver, se [styrningsuppsättningen](../changing-settings.md#styrningsuppsättningen).
- **En ändring per beslut.** Ett reglage ändrar växelriktaren när du släpper reglaget. Ett nummerfält ändrar växelriktaren vid Enter eller när du lämnar fältet. En lista, en brytare eller ett tidsfält ändrar växelriktaren vid ändring. Styrningen visar sedan det värde som växelriktaren håller, och en nekad ändring visas under styrningen med integrationens ord.

## Tema och språk

Elementen följer Home Assistants tema. Entitetsnamn, värden och tillstånd använder Home Assistants formatering och språk. Kortens texter finns på engelska, tyska, nederländska, franska, förenklad kinesiska, spanska, italienska, polska och svenska. En instrumentpanel på något annat språk visar kortens texter på engelska.

## Stöds inte ännu

- Korttexter på andra språk än de nio ovan.
