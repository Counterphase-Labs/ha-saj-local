[en](../../../en-gb/user/entities/README.md) | [de](../../../de/user/entities/README.md) | [nl](../../../nl/user/entities/README.md) | [fr](../../../fr/user/entities/README.md) | [zh](../../../zh-hans/user/entities/README.md) | [es](../../../es/user/entities/README.md) | [it](../../../it/user/entities/README.md) | [pl](../../../pl/user/entities/README.md) | sv

# Entiteter

Varje entitet som SAJ Local kan skapa, en sida för varje område. Avsnittet [Enheter och entiteter](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) i integrationens funktionslista förklarar entitetstyperna, vilka entiteter som är aktiverade som standard och tecknet på effektavläsningar.

Ett system får bara de entiteter som passar dess modell, dess installerade utrustning och dess antal faser, solcellssträngar och batteripack. Kolumnen Modeller anger vilka modeller som har en entitet, och kolumnen Utrustning och antal anger vad som måste vara installerat.

Genereras av `make docs`. Redigera inte för hand.

| Område | Entiteter | Vad området innehåller |
| --- | --- | --- |
| [Växelriktare och PV](inverter-and-pv.md) | 244 | Växelriktarens utgång, solcellssträngar, reservport, energiräknare, versioner och hushållets last |
| [Nät och Mätare A](grid-and-meter-a.md) | 101 | Nätanslutningen och Mätare A, nätmätaren |
| [Mätare B](meter-b.md) | 22 | Mätare B, den andra mätaren som mäter en solcellsväxelriktare |
| [Batteri](battery.md) | 138 | Batteriet som helhet |
| [Batteripack](battery-packs.md) | 58 | Avläsningar och identitet för varje batteripack |
| [Elbilsladdare](ev-charger.md) | 87 | Elbilsladdaren och dess laddningsstyrningar |
| [Parallellsystem](parallel-system.md) | 63 | Avläsningarna från ett parallellt maskinsystem |
| [Inställningar](settings.md) | 22 | Inställningar och kommandon som ändrar växelriktaren |
| [Fel](faults.md) | 139 | Fel som växelriktaren, batteriet och elbilsladdaren rapporterar |
| [Tillagt av integrationen](added-by-the-integration.md) | 7 | Entiteter som integrationen lägger till utanför registerkatalogen |
