[en](../../en-gb/user/protecting-the-inverter.md) | [de](../../de/user/protecting-the-inverter.md) | [nl](../../nl/user/protecting-the-inverter.md) | [fr](../../fr/user/protecting-the-inverter.md) | [zh](../../zh-hans/user/protecting-the-inverter.md) | [es](../../es/user/protecting-the-inverter.md) | [it](../../it/user/protecting-the-inverter.md) | [pl](../../pl/user/protecting-the-inverter.md) | sv

# Skydda växelriktaren

Sidan Skydda växelriktaren listar de gränser som SAJ Local håller för allt som SAJ Local skickar, så att växelriktarens kommunikationsmodul fortsätter betjäna Home Assistant. En modul kan sluta betjäna en klient som avfrågar för hårt, så ingen inställning tar bort en gräns. Den fullständiga listan finns i avsnittet [Skydda växelriktaren](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) i integrationens funktionslista.

## Gränserna

- **En anslutning, en förfrågan i taget.** SAJ Local öppnar en anslutning till en växelriktare och väntar på varje svar innan nästa förfrågan skickas, med en kort paus mellan förfrågningarna.
- **40 förfrågningar under valfria 60 sekunder.** Gränsen gäller per växelriktaradress. SAJ Local räknar över omläsningar, så en omläsning, ett nytt installationsförsök eller en anslutningskontroll kan inte överskrida gränsen. En förfrågan över gränsen får vänta.
- **Angränsande register delar en förfrågan.** SAJ Local läser register som ligger nära varandra i en förfrågan, aldrig bortom ett block som modellen dokumenterar. En förfrågan är aldrig större än 32 register på HS3 eller 56 på H2. Att gruppera entiteter som ligger tillsammans kostar mindre, se [avfrågning](polling.md).
- **Inga nya försök inom en cykel.** Efter en misslyckad avläsning fördubblas väntan före nästa försök från det kortaste intervallet, upp till 5 minuter. Väntan består över omläsningar. Den första lyckade cykeln läser allt igen.
- **Varje väntan har en tidsgräns.** En växelriktare som hänger sig avslutar en cykel som ett misslyckande och stoppar inte avfrågningen. Ett sent eller förirrat svar kasseras.
- **En stängd anslutning öppnas igen en gång.** Den cykeln läser sedan varje aktiverad entitet igen, så inget värde är äldre än återanslutningen.
- **Två slags registerläsning.** SAJ Local läser hållregister (Modbus-funktion 03) och inregister (funktion 04). HS3 levererar elbilsladdarens mätvärden som inregister. Båda slagen räknas mot de 40 förfrågningarna, och en nekad läsning av ett slag stänger aldrig av det andra.
- **Högst 20 ändringar under 60 sekunder.** Se [ändra inställningar](changing-settings.md#vad-som-händer-med-en-ändring). En ändring över gränsen nekas och köas inte.

## När växelriktaren nekar en avläsning

En nekad avläsning är ett svar och inte ett misslyckande. Bara entiteterna i den nekade förfrågan blir otillgängliga, och de andra fortsätter uppdateras.

1. SAJ Local delar den nekade förfrågan på mitten under de följande cyklerna, tills den nekade entiteten hittats.
2. En entitet som nekats tre gånger i rad stängs av tillfälligt. Entiteten visas som otillgänglig och läses inte längre.
3. SAJ Local prövar en tillfälligt avstängd entitet igen en gång om dagen, och varje gång integrationen läses in. Entiteten kommer tillbaka när registret svarar.
4. Ett reparationsärende listar de avstängda entiteterna. Åtgärden i ärendet inaktiverar entiteterna, så att SAJ Local inte längre läser entiteterna för gott. Se [fel och reparationer](faults-and-repairs.md#reparationsärenden).

## När växelriktaren slutar svara

Ett reparationsärende anger när en växelriktare inte har svarat på 15 minuter. Ärendet försvinner vid den första lyckade avläsningen. Kontrollera strömmen till växelriktaren och kommunikationsmodulen, nätverket och att ingen annan Modbus-klient håller anslutningen.

## Stöds inte ännu

- Att ändra gränserna. Gränserna skyddar växelriktaren, så ingen inställning höjer en gräns.
