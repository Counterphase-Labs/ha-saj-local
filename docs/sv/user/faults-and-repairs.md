[en](../../en-gb/user/faults-and-repairs.md) | [de](../../de/user/faults-and-repairs.md) | [nl](../../nl/user/faults-and-repairs.md) | [fr](../../fr/user/faults-and-repairs.md) | [zh](../../zh-hans/user/faults-and-repairs.md) | [es](../../es/user/faults-and-repairs.md) | [it](../../it/user/faults-and-repairs.md) | [pl](../../pl/user/faults-and-repairs.md) | sv

# Enhetsfel och reparationer

Sidan Enhetsfel och reparationer förklarar hur SAJ Local visar de fel som växelriktaren, batteriet och elbilsladdaren rapporterar, och vilka reparationsärenden SAJ Local skapar i Home Assistant. Den fullständiga listan över felbeteende finns i avsnittet [Enhetsfel och reparationer](../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) i integrationens funktionslista. Varje felentitet finns i [felentiteterna](entities/faults.md) i entitetsreferensen.

Enhetsfel och reparationsärenden är åtskilda. Ett enhetsfel är en entitet som rapporterar vad utrustningen säger. Ett reparationsärende är ett problem med SAJ Locals anslutning till utrustningen eller med SAJ Locals inställningar, och Home Assistant listar ärendet under Inställningar och Reparationer.

## Enhetsfel

Varje namngivet fel hos växelriktaren, batteriet och elbilsladdaren är en binär sensor med enhetsklassen problem, aktiverad som standard. Ett fel har historik och kan utlösa en automation.

- **Sammanfattning:** växelriktaren, batteriet och elbilsladdaren har var sitt sammanfattande fel, till exempel Växelriktarfel, som är på när utrustningen rapporterar något.
- **Okänt:** varje del av utrustningen har också ett okänt fel som är på när växelriktaren sätter en bit utan dokumenterad betydelse. [Diagnostiknedladdningen](troubleshooting.md#ladda-ner-diagnostik) listar registret och biten, så att du kan rapportera biten.
- **Ett entitets-ID på varje modell:** ett fel har ett entitets-ID på varje modell som rapporterar felet. Ett fel som en modell inte rapporterar har ingen entitet på den modellen.
- **Batteripack:** varje batteripack har en felentitet och en varningsentitet. En HS3 har ett pack. En H2 har upp till fyra.
- **Utrustning som inte är installerad:** batterifel finns bara när ett batteri är installerat, och elbilsladdarfel bara när en elbilsladdare är installerad. Se [valfri utrustning](optional-equipment.md).
- **Ett felregister som inte kan läsas:** de fel som beror på registret är otillgängliga. SAJ Local gissar inte.
- **Loggen:** ett fel som slås på loggar en varning som anger systemet och felet. När felet försvinner loggar SAJ Local en informationsrad.

[Felkortet](cards/faults-card.md) listar ett systems aktiva fel på en instrumentpanel, med hur länge sedan varje fel började. Knappen Rensa fel på kortet skickar kommandot Rensa aktuellt fel, som kräver [Tillåt styrning](changing-settings.md#tillåt-styrning).

## Reparationsärenden

SAJ Local skapar ett reparationsärende för ett tillstånd som du kan åtgärda.

| Reparationsärende | Skapas när | Vad du kan göra |
| --- | --- | --- |
| Systemet är inställt på fel modell | Växelriktaren på adressen identifierar sig som en annan modell än den valda. | En åtgärd antar den modell som SAJ Local hittade. Se [byta växelriktare](replacing-the-inverter.md). |
| Systemet når nu en annan växelriktare | Växelriktaren på adressen har ett annat serienummer. | En åtgärd antar den nya växelriktaren. Se [byta växelriktare](replacing-the-inverter.md). |
| Systemet når en enhet som inte känns igen | Enhetstypen är ingen modell som känns igen. | Välj modellen i Konfigurera. SAJ Local använder då modellen overifierad. |
| Systemet har avläsningar som växelriktaren nekar | Växelriktaren nekade avläsningarna tre gånger i rad. | En åtgärd inaktiverar de listade entiteterna, så att SAJ Local inte längre läser entiteterna. Se [skydda växelriktaren](protecting-the-inverter.md#när-växelriktaren-nekar-en-avläsning). |
| Systemet har slutat svara | Växelriktaren har inte svarat på 15 minuter. | Kontrollera strömmen, nätverket och andra Modbus-klienter. Ärendet försvinner vid den första lyckade avläsningen. |
| Utrustning identifieras inte längre | Utrustning som SAJ Local tidigare identifierat identifieras inte längre. | Kontrollera utrustningen, eller ställ in utrustningen som Inte installerad i Konfigurera. Se [valfri utrustning](optional-equipment.md#när-utrustning-som-kommer-ihåg-inte-längre-identifieras). |

![Ett reparationsärende i Home Assistant som säger att SAJ HS3MOCK000000000003 har avläsningar som växelriktaren nekar](../../images/sv/faults-and-repairs-repair-issue.png)

De tre första ärendena är modellärendena. Bara ett av modellärendena är öppet för ett system, och ärendet att systemet har slutat svara skapas inte medan ett modellärende är öppet.

Ett reparationsärende försvinner när ärendets tillstånd upphör, eller när du tar bort systemet. Ärendet om nekade avläsningar försvinner också när du inaktiverar en listad entitet.

## Stöds inte ännu

- Ett reparationsärende för ett enhetsfel. Enhetsfel är entiteter, och integrationen skapar inget reparationsärende för ett fel.
