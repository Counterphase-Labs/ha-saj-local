[en](../../en-gb/user/supported-equipment.md) | [de](../../de/user/supported-equipment.md) | [nl](../../nl/user/supported-equipment.md) | [fr](../../fr/user/supported-equipment.md) | [zh](../../zh-hans/user/supported-equipment.md) | [es](../../es/user/supported-equipment.md) | [it](../../it/user/supported-equipment.md) | [pl](../../pl/user/supported-equipment.md) | sv

# Utrustning som stöds

Sidan Utrustning som stöds listar de SAJ-produkter som SAJ Local stöder, den valfria utrustning som varje modell kan ha och vad som inte stöds ännu. Den fullständiga listan över vad installationen gör finns i avsnittet [Installation och identifiering](../../../custom_components/saj_local/docs/features.md#setup-and-detection) i integrationens funktionslista.

## Modeller som stöds

SAJ Local känner igen en modell från den enhetstyp som växelriktaren rapporterar. Alla andra enhetstyper känns inte igen.

| Modell | Känns igen som | Valfri utrustning som SAJ Local identifierar |
| --- | --- | --- |
| HS3 | Enhetstyp `0x1610`, tre faser | Batteri, Mätare A, Mätare B, Elbilsladdare, Parallellsystem |
| H2, en fas, två solcellssträngar | Enhetstyp `0x005a` | Batteri, Mätare A, Mätare B, Parallellsystem |
| H2, en fas, tre solcellssträngar | Enhetstyp `0x005b` | Batteri, Mätare A, Mätare B, Parallellsystem |

Skillnaderna mellan modellerna som du märker i användningen:

- **Elbilsladdare:** bara HS3. H2 har inga entiteter för elbilsladdare, inga elbilsladdartidsluckor och ingen avdelning för elbilsladdare på styrkortet.
- **Batteripack:** en H2 har entiteter för upp till fem batteripack. En HS3 har entiteter för ett batteripack. Se [valfri utrustning](optional-equipment.md).
- **EMS:** bara HS3. Se [ändra inställningar](changing-settings.md#ems).
- **Effektstyrning:** HS3 erbjuder Batteri, Nät och Växelriktare. H2 erbjuder bara Batteri. Se [effektstyrning](power-control.md).

[Valfri utrustning](optional-equipment.md) förklarar hur identifieringen fungerar och hur du åsidosätter den. [Entitetsreferensen](entities/README.md) listar vilken modell och vilken utrustning varje entitet kräver.

## Stöds inte ännu

- Automatisk identifiering känner bara igen de tre enhetstyperna i tabellen. Andra SAJ-produkter, som HS2, H1 och AS1, känns inte igen.
- Andra H2-varianter, som H2 med tre faser, rapporterar andra enhetstyper och känns inte igen automatiskt. Du kan välja modellen för hand, och SAJ Local markerar då modellen som overifierad. Avläsningarna kan vara felaktiga, eftersom SAJ Local inte kan kontrollera dem. Se [kom igång](getting-started.md#när-växelriktaren-inte-känns-igen).
- Att ändra inställningar i ett system vars modell är overifierad. Avläsning fungerar, och varje ändring nekas.

## Vad stödet vilar på

HS3-stödet har verifierats för hand på en riktig HS3. H2-stödet vilar på SAJ:s protokolldokumentation och fältrapporter och har inte verifierats för hand på en H2. Att skriva inställningar och effektstyrning på H2 vilar också på dokumentation och fältrapporter.
