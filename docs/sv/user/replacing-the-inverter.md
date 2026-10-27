[en](../../en-gb/user/replacing-the-inverter.md) | [de](../../de/user/replacing-the-inverter.md) | [nl](../../nl/user/replacing-the-inverter.md) | [fr](../../fr/user/replacing-the-inverter.md) | [zh](../../zh-hans/user/replacing-the-inverter.md) | [es](../../es/user/replacing-the-inverter.md) | [it](../../it/user/replacing-the-inverter.md) | [pl](../../pl/user/replacing-the-inverter.md) | sv

# Byta växelriktare

Sidan Byta växelriktare förklarar hur du flyttar ett system till en ny växelriktare, eller mellan en H2 och en HS3, och behåller enheten, entiteterna och historiken. Den fullständiga listan finns i avsnittet [Modellbyte](../../../custom_components/saj_local/docs/features.md#model-replacement) i integrationens funktionslista.

## Flytta ett system med avsikt

1. Se till att den nya växelriktaren går att nå. Om den nya växelriktaren har en annan adress anger du adressen i nästa steg.
2. Öppna Konfigurera, kugghjulet på systemets rad på sidan för SAJ Local-integrationen.
3. Ändra värd, port eller enhets-ID om adressen ändrats. Låt Modell stå på Automatisk, eller välj modellen om växelriktaren inte känns igen.
4. Välj Skicka och bekräfta sedan bytet. Bekräftelsen anger den modell och det serienummer som SAJ Local hittade.

Efter att du bekräftat stannar enheten, entiteterna, entiteternas namn och historiken kvar hos systemet. En entitet behåller historiken över flytten när båda modellerna har entiteten. SAJ Local glömmer den utrustning som identifierades på den gamla växelriktaren och den gamla växelriktarens antal batteripack, och identifierar utrustningen igen på den nya växelriktaren.

## När växelriktaren på adressen byts utan att du gör det

SAJ Local kontrollerar växelriktarens identitet varje gång systemet läses in. När växelriktaren på adressen identifierar sig som en annan modell, eller har ett annat serienummer, läser SAJ Local inte in systemet och skapar ett reparationsärende. Åtgärden i reparationsärendet visar den modell och det serienummer som växelriktaren rapporterar nu och antar den växelriktare som du bekräftar.

- Entitets-ID:n, historik, Tillåt styrning och alla andra inställningar förblir oförändrade.
- När växelriktaren rapporterar något annat än det formuläret visade säger formuläret det och visar de nya värdena i stället för att spara de gamla värdena.
- När enheten på adressen inte är en modell som känns igen anger ett reparationsärende det och pekar på Konfigurera. Det finns inget att anta. Välj modellen för hand, se [kom igång](getting-started.md#när-växelriktaren-inte-känns-igen).

Reparationsärendena listas i [fel och reparationer](faults-and-repairs.md#reparationsärenden).

## Stöds inte ännu

- Att anta en växelriktare som redan tillhör ett annat system. SAJ Local nekar antagandet.
