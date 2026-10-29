[en](../../en-gb/user/README.md) | [de](../../de/user/README.md) | [nl](../../nl/user/README.md) | [fr](../../fr/user/README.md) | [zh](../../zh-hans/user/README.md) | [es](../../es/user/README.md) | [it](../../it/user/README.md) | [pl](../../pl/user/README.md) | sv

# Användardokumentation för SAJ Local

SAJ Local är en lokal Home Assistant-integration. SAJ Local läser av ett SAJ HS3- eller H2-solcellssystem direkt från växelriktaren över Modbus TCP i ditt eget nätverk och, när du tillåter styrning, ändrar växelriktarens inställningar från Home Assistant. SAJ Local behöver inget molnkonto och begränsar förfrågningarna till växelriktaren så att växelriktarens kommunikationsmodul fortsätter fungera.

SAJ Local är en inofficiell integration som byggts av communityn. SAJ tillverkar, stöder eller rekommenderar inte SAJ Local. Se [friskrivningen](#friskrivning).

SAJ Local har ännu ingen stabil version. Varje version före `1.0.0` är en beta, se [betaversioner](installation.md#betaversioner). Varje sida nedan anger vad som inte stöds ännu. Dokumentationen omfattar HS3 och H2 och markerar skillnaderna med en anmärkning som "Endast HS3". Skärmbilderna kommer från simulerade system, så avläsningarna är inte verkliga.

## Börja här

1. [Installera SAJ Local](installation.md) med HACS.
2. Kontrollera att din växelriktare finns bland den [utrustning som stöds](supported-equipment.md).
3. [Kom igång](getting-started.md): lägg till ditt första system.
4. Läs om [valfri utrustning](optional-equipment.md), som SAJ Local identifierar åt dig.

## Förstå ditt system

- [Entiteter och prefixet](entities-and-prefix.md): vad entiteterna är, hur entitets-ID:na bildas och hur du lägger till ett prefix.
- [Entitetsreferens](entities/README.md): varje entitet, med entitets-ID, modeller, utrustning och standardvärde. Genereras från integrationen.
- [Avfrågning](polling.md): hur ofta växelriktaren läses av och hur du läser av vissa entiteter snabbare eller långsammare.
- [Skydda växelriktaren](protecting-the-inverter.md): de gränser som SAJ Local håller för sina egna förfrågningar.

## Ändra saker

- [Ändra inställningar](changing-settings.md): tillåt styrning, ändra inställningar och använd EMS.
- [Effektstyrning](power-control.md): håll batteriet, nätanslutningen eller växelriktaren vid en inställd effekt, för hand eller med ett schema.
- [Byta växelriktare](replacing-the-inverter.md): flytta ett system till en ny växelriktare, eller mellan en H2 och en HS3, och behåll historiken.

## Instrumentpaneler

- [Instrumentpanelskort](cards/README.md): korten, funktionen för brickkort och statusmärket som SAJ Local lägger till i Home Assistant.

## Termer

- [Nomenklatur](nomenclature.md): de SAJ- och Home Assistant-termer som integrationen, korten och dokumentationen använder, med deras betydelse.

## När något är fel

- [Enhetsfel och reparationer](faults-and-repairs.md): de fel som utrustningen rapporterar och de reparationsärenden som SAJ Local skapar.
- [Felsökning](troubleshooting.md): diagnostik, felsökningsloggning och var du ber om hjälp.

## Vad varje del kan göra

Funktionslistorna anger vad som är byggt i dag: [integrationen](../../../custom_components/saj_local/docs/features.md) och [korten](../../../frontend/docs/features.md).

Utvecklare: se [utvecklardokumentationen](../developer/README.md).

## Friskrivning

SAJ Local är en oberoende integration som byggts av communityn. SAJ Local har ingen anknytning till SAJ (Guangzhou Sanjing Electric Co., Ltd.), och SAJ samt SAJ:s dotterbolag och närstående bolag har inte godkänt, sponsrat eller rekommenderat SAJ Local.

SAJ, SAJ-logotypen och alla relaterade produktnamn, modellnamn och varumärken tillhör sina respektive ägare. Dokumentationen använder namnen bara för att ange den utrustning som SAJ Local fungerar med.

Programvaran tillhandahålls i befintligt skick, utan någon form av garanti. Du använder SAJ Local på egen risk: upphovspersonerna tar inget ansvar för skador på utrustning, förlust av data, förlorad garanti eller någon annan följd av att använda SAJ Local. Varningen gäller särskilt när inställningar skrivs till din växelriktare.

## Tack

H2-stödet bygger på registerforskningen och fälttesterna av stanus74 i [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). Tack.
