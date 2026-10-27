[en](../../en-gb/user/nomenclature.md) | [de](../../de/user/nomenclature.md) | [nl](../../nl/user/nomenclature.md) | [fr](../../fr/user/nomenclature.md) | [zh](../../zh-hans/user/nomenclature.md) | [es](../../es/user/nomenclature.md) | [it](../../it/user/nomenclature.md) | [pl](../../pl/user/nomenclature.md) | sv

# Nomenklatur

De termer som SAJ Local, instrumentpanelens kort och dokumentationen använder, var och en med en förklaring på en rad. Varje översättning av integrationen, korten och dokumentationen använder en term för varje sak som listas här. Avsnittet [Språk](../../../custom_components/saj_local/docs/features.md#languages) i integrationens funktionslista anger vilka språk SAJ Local levereras med.

## SAJ-utrustning och avläsningar

| Term | Betydelse |
| --- | --- |
| Växelriktare | SAJ-enheten som omvandlar likström från solcellerna och batteriet till växelström för hemmet och nätet. |
| HS3 | SAJ HS3, en hybridväxelriktare med tre faser. |
| H2 | SAJ H2, en hybridväxelriktare med en fas. |
| Modell | Växelriktartypen som SAJ Local använder för att välja registerlista: Automatisk, HS3 eller H2. |
| Automatisk | Modellvalet som känner igen modellen från den enhetstyp som växelriktaren rapporterar. |
| Valfri utrustning | Utrustning som en anläggning kan ha eller sakna: ett batteri, Mätare A, Mätare B, en elbilsladdare eller ett parallellsystem. |
| Installerad | Inställningen som talar om för SAJ Local att en valfri utrustning är installerad. |
| Inte installerad | Inställningen som talar om för SAJ Local att en valfri utrustning inte är installerad. |
| Batteri | Energilagret som är anslutet till växelriktaren. |
| Batteripack | En batterimodul i ett batteri, visas som Pack följt av ett nummer. |
| Laddningsnivå | Hur fullt batteriet är, i procent. |
| Reserv | Batteriladdningen som växelriktaren sparar och inte laddar ur under. |
| Sol | Effekten som solpanelerna producerar. |
| Solcellssträng | En grupp solpaneler seriekopplade och anslutna till en ingång på växelriktaren. |
| Fas | En ledare i växelströmsförsörjningen. |
| Nät | Det allmänna elnätet som hemmet är anslutet till. |
| Import | Att ta effekt från nätet. |
| Export | Att skicka effekt till nätet. |
| Laddar | Att föra in effekt i batteriet. |
| Laddar ur | Att ta ut effekt ur batteriet. |
| Hem | Effekten som hemmet använder. |
| Reservlast | Lasterna som fortsätter få ström från batteriet och solpanelerna när nätet faller bort. |
| Mätare A | Den första elmätaren som kan anslutas till växelriktaren. |
| Mätare B | Den andra elmätaren som kan anslutas till växelriktaren. |
| Elbilsladdare | En laddare för elfordon som är ansluten till växelriktaren. |
| Parallellsystem | Flera växelriktare som arbetar tillsammans som ett system. |
| Fel | Ett problem som utrustningen rapporterar, med ett register och en bit. |
| Rensa fel | Knappen som ber växelriktaren att rensa ett rapporterat fel. |
| Driftläge | Det tillstånd som växelriktaren befinner sig i, till exempel igång eller standby. |
| Läge | Växelriktarens driftsätt, till exempel tidsstyrning. |
| Tidsstyrning | Läget där batteriet laddas och laddas ur i de tidsluckor som du anger. |
| Tidslucka | En tidsperiod i tidsstyrningens schema för laddning, urladdning eller elbilsladdaren. |
| EMS | Växelriktarens funktioner för energihantering, som håller ett effektmål som kommer utifrån. |
| EMS-hjärtslag | Hur ofta SAJ Local läser EMS-målen för att hålla EMS-funktionerna vid liv. |
| EMS-tidsgräns | Tiden efter vilken växelriktaren avslutar en EMS-funktion som inte hålls vid liv. |
| Skydd mot omvänd ström | Växelriktarens skydd mot att effekt flödar tillbaka in i växelriktaren, som EMS-funktionerna stänger av. |
| Effektstyrning | Att hålla batteriet, nätanslutningen eller växelriktaren vid en inställd effekt. |
| Effektmål | Effekten som en effektstyrningsfunktion håller. |
| Schema | Tiderna då en effektstyrningsfunktion körs. |
| Tillåt styrning | Inställningen som låter Home Assistant ändra växelriktarens inställningar. |
| Styrning | Möjligheten att ändra växelriktarens inställningar, till skillnad från att bara läsa av den. |
| Register | En numrerad minnesplats i växelriktaren som håller ett värde eller en inställning. |
| Nekat register | Ett register som växelriktaren vägrar svara på. |
| Modbus TCP | Nätverksprotokollet som SAJ Local använder för att prata med växelriktaren. |
| Värd | Växelriktarens nätverksadress. |
| Port | Växelriktarens nätverksport, som standard 502. |
| Enhets-ID | Växelriktarens Modbus-adress, från 1 till 247. |
| Kommunikationsmodul | Den del av växelriktaren som svarar på nätverksförfrågningar. |
| Block | Ett registerintervall som läses med en enda förfrågan. |
| Realtid | Blocket med avläsningar som ändras från sekund till sekund. |
| Femminutersmedelvärden | Blocket med avläsningar som växelriktaren tar medelvärdet av över fem minuter. |
| Energi | Blocket med avläsningar av producerad och använd energi, till exempel dagens energi. |
| Identitet | Modellen, serienumret och versionerna som växelriktaren rapporterar. |

## SAJ Local-begrepp

| Term | Betydelse |
| --- | --- |
| System | En växelriktare, med sin utrustning, som lagts till i Home Assistant. |
| Anläggning | En SAJ Local-konfigurationspost, vilket är ett system. |
| Prefix | Valfri text som läggs till i entitets-ID:na för en anläggning, används när det finns fler än ett system. |
| Avfrågning | Att läsa av växelriktaren med jämna mellanrum. |
| Avfrågningsgrupp | En vald uppsättning entiteter som SAJ Local läser snabbare eller långsammare än standardintervallet. |
| Uppdateringsintervall | Sekunderna mellan två avläsningar av växelriktaren, visas som "Sekunder mellan uppdateringar". |
| Förfrågningsbelastning | Antalet förfrågningar per minut som SAJ Local skickar till växelriktaren, mot gränsen på 40 per 60 sekunder. |
| Budget | Gränsen för förfrågningsbelastningen. |
| Modellbyte | Att flytta ett system till en ny växelriktare, eller mellan en H2 och en HS3, och behålla historiken. |
| Overifierad | En modell som valts för hand och inte kunde kontrolleras mot enhetstypen. |
| Diagnostiknedladdning | Filen som innehåller en integritetssäker ögonblicksbild av systemet för en felrapport. |
| Felsökningsloggning | Alternativet som skriver detaljerade loggrader för att hitta ett problem. |
| Instrumentpanelskort | Ett kort som SAJ Local lägger till i Home Assistants instrumentpaneler. |
| Effektflödeskort | Kortet som visar live-effekt mellan sol, batteri, nät och hem. |
| Statuskort | Kortet som visar driftläget, läget, viktiga avläsningar och fel. |
| Felkort | Kortet som listar de aktiva felen. |
| Batterikort | Kortet som visar batteriets avläsningar och en rad per pack. |
| Styrkort | Kortet som visar systemets gemensamma styrningar. |
| Schemakort | Kortet som visar tidsluckorna med en veckotidslinje. |
| Veckodagar som funktion för bricka | De sju dagknapparna som kan läggas till i ett brickkort. |
| Statusmärke | Märket som visar driftläget och antalet aktiva fel. |

## Home Assistant-begrepp

| Term | Betydelse |
| --- | --- |
| Home Assistant | Hemautomationsprogramvaran som SAJ Local är en integration till. |
| Integration | Programvara som kopplar en sorts enhet eller tjänst till Home Assistant. |
| HACS | Home Assistant Community Store, används för att installera SAJ Local. |
| Anpassat arkiv | Ett arkiv som inte finns i HACS standardlista och som läggs till i HACS med sin adress; märket ”HACS anpassat” i README-filerna markerar SAJ Local som ett sådant arkiv. |
| Konfigurationsflöde | Installationsdialogen som lägger till ett system. |
| Konfigurationspost | Den sparade installationen av ett system. |
| Underpost | En del av en konfigurationspost som läggs till och ändras för sig, till exempel en avfrågningsgrupp eller ett effektschema. |
| Konfigurera | Knappen hos en integration som öppnar dess alternativ. |
| Enheter och tjänster | Home Assistants inställningssida som listar integrationer, enheter och entiteter. |
| Inställningar | Home Assistants sida för att konfigurera Home Assistant. |
| Enhet | Home Assistants post för en utrustning som håller entiteter. Varje system är en enhet. |
| Entitet | En avläsning, inställning eller ett kommando som Home Assistant visar. |
| Entitets-ID | Entitetens unika identifierare, till exempel sensor.saj_pv_power. |
| Sensor | En entitet som visar en avläsning. |
| Binär sensor | En entitet som antingen är på eller av, till exempel ett fel. |
| Nummer | En entitet som håller ett tal som du kan ändra. |
| Val | En entitet som håller ett val ur en lista. |
| Brytare | En entitet som du kan slå på eller av. |
| Tid | En entitet som håller en tid på dygnet. |
| Knapp | En entitet som kör en åtgärd när den trycks. |
| Aktiverad som standard | Om en entitet är påslagen när systemet läggs till. |
| Inaktiverad | En entitet som Home Assistant varken läser eller visar. |
| Reparationsärende | En avisering i Home Assistant om att något kräver din åtgärd, med en Åtgärda-knapp. |
| Instrumentpanel | En skärm i Home Assistant som består av kort. |
| Kort | Ett block på en instrumentpanel. |
| Brickkort | Ett Home Assistant-kort som visar en entitet och som kan få funktioner tillagda. |
| Märke | Ett litet objekt i märkesraden högst upp på en instrumentpanel. |
| Automation | En regel som får Home Assistant att agera när något händer. |
| Hjälpare | En Home Assistant-entitet som du skapar själv, till exempel en schemahjälpare. |
| Område | Ett rum eller en plats som enheter grupperas i. |
| Tema | Färgerna i Home Assistants gränssnitt. |
| Språk | Språket som en Home Assistant-användare väljer på profilsidan. |
| Läs in igen | Att starta om en integration utan att starta om Home Assistant. |
| Starta om | Att starta om Home Assistant. |
| Utvecklarverktyg | Home Assistants sidor för att kontrollera tillstånd och anropa åtgärder. |
| Logg | Home Assistants register över meddelanden. |
