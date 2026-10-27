[en](../../../en-gb/user/entities/meter-b.md) | [de](../../../de/user/entities/meter-b.md) | [nl](../../../nl/user/entities/meter-b.md) | [fr](../../../fr/user/entities/meter-b.md) | [zh](../../../zh-hans/user/entities/meter-b.md) | [es](../../../es/user/entities/meter-b.md) | it | [pl](../../../pl/user/entities/meter-b.md) | [sv](../../../sv/user/entities/meter-b.md)

# Contatore B

Il Contatore B, il secondo contatore che misura un inverter solare.

Le entità dell'area «Contatore B» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Apparecchiature opzionali](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

22 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Contatore B», per esempio `sensor.saj_house_meter_b_l1_voltage` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| Tensione contatore B L1 | `sensor.saj_meter_b_l1_voltage` | Sensore | V | HS3, H2 | Contatore B | No |
| Corrente contatore B L1 | `sensor.saj_meter_b_l1_current` | Sensore | A | HS3, H2 | Contatore B | No |
| Potenza contatore B L1 | `sensor.saj_meter_b_l1_power` | Sensore | W | HS3, H2 | Contatore B | No |
| Potenza apparente contatore B L1 | `sensor.saj_meter_b_l1_apparent_power` | Sensore | VA | HS3, H2 | Contatore B | No |
| Fattore di potenza contatore B L1 | `sensor.saj_meter_b_l1_power_factor` | Sensore | - | HS3, H2 | Contatore B | No |
| Frequenza contatore B L1 | `sensor.saj_meter_b_l1_frequency` | Sensore | Hz | HS3, H2 | Contatore B | No |
| Tensione contatore B L2 | `sensor.saj_meter_b_l2_voltage` | Sensore | V | HS3, H2 | Contatore B; Fase 2 e successive | No |
| Corrente contatore B L2 | `sensor.saj_meter_b_l2_current` | Sensore | A | HS3, H2 | Contatore B; Fase 2 e successive | No |
| Potenza contatore B L2 | `sensor.saj_meter_b_l2_power` | Sensore | W | HS3, H2 | Contatore B; Fase 2 e successive | No |
| Potenza apparente contatore B L2 | `sensor.saj_meter_b_l2_apparent_power` | Sensore | VA | HS3, H2 | Contatore B; Fase 2 e successive | No |
| Fattore di potenza contatore B L2 | `sensor.saj_meter_b_l2_power_factor` | Sensore | - | HS3, H2 | Contatore B; Fase 2 e successive | No |
| Frequenza contatore B L2 | `sensor.saj_meter_b_l2_frequency` | Sensore | Hz | HS3, H2 | Contatore B; Fase 2 e successive | No |
| Tensione contatore B L3 | `sensor.saj_meter_b_l3_voltage` | Sensore | V | HS3, H2 | Contatore B; Fase 3 e successive | No |
| Corrente contatore B L3 | `sensor.saj_meter_b_l3_current` | Sensore | A | HS3, H2 | Contatore B; Fase 3 e successive | No |
| Potenza contatore B L3 | `sensor.saj_meter_b_l3_power` | Sensore | W | HS3, H2 | Contatore B; Fase 3 e successive | No |
| Potenza apparente contatore B L3 | `sensor.saj_meter_b_l3_apparent_power` | Sensore | VA | HS3, H2 | Contatore B; Fase 3 e successive | No |
| Fattore di potenza contatore B L3 | `sensor.saj_meter_b_l3_power_factor` | Sensore | - | HS3, H2 | Contatore B; Fase 3 e successive | No |
| Frequenza contatore B L3 | `sensor.saj_meter_b_l3_frequency` | Sensore | Hz | HS3, H2 | Contatore B; Fase 3 e successive | No |
| Potenza reattiva contatore B L1 | `sensor.saj_meter_b_l1_reactive_power` | Sensore | var | HS3 | Contatore B | No |
| Potenza reattiva contatore B L2 | `sensor.saj_meter_b_l2_reactive_power` | Sensore | var | HS3 | Contatore B; Fase 2 e successive | No |
| Potenza reattiva contatore B L3 | `sensor.saj_meter_b_l3_reactive_power` | Sensore | var | HS3 | Contatore B; Fase 3 e successive | No |
| Potenza del contatore B | `sensor.saj_meter_b_power` | Sensore | W | HS3, H2 | Contatore B | Sì |
