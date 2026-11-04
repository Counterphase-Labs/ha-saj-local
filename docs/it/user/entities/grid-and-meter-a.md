[en](../../../en-gb/user/entities/grid-and-meter-a.md) | [de](../../../de/user/entities/grid-and-meter-a.md) | [nl](../../../nl/user/entities/grid-and-meter-a.md) | [fr](../../../fr/user/entities/grid-and-meter-a.md) | [zh](../../../zh-hans/user/entities/grid-and-meter-a.md) | [es](../../../es/user/entities/grid-and-meter-a.md) | it | [pl](../../../pl/user/entities/grid-and-meter-a.md) | [sv](../../../sv/user/entities/grid-and-meter-a.md)

# Rete e Contatore A

Il collegamento alla rete e il Contatore A, il contatore di rete.

Le entità dell'area «Rete e Contatore A» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Dispositivi ed entità](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) e [Apparecchiature opzionali](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

101 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Rete e Contatore A», per esempio `sensor.saj_house_grid_connection_countdown` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| Conto alla rovescia del collegamento alla rete | `sensor.saj_grid_connection_countdown` | Sensore | s | HS3, H2 | - | No |
| Tensione rete L1 | `sensor.saj_grid_l1_voltage` | Sensore | V | HS3, H2 | - | Sì |
| Frequenza rete L1 | `sensor.saj_grid_l1_frequency` | Sensore | Hz | HS3, H2 | - | Sì |
| Corrente continua rete L1 | `sensor.saj_grid_l1_dc_current` | Sensore | mA | HS3, H2 | - | No |
| Tensione rete L2 | `sensor.saj_grid_l2_voltage` | Sensore | V | HS3, H2 | Fase 2 e successive | Sì |
| Frequenza rete L2 | `sensor.saj_grid_l2_frequency` | Sensore | Hz | HS3, H2 | Fase 2 e successive | No |
| Corrente continua rete L2 | `sensor.saj_grid_l2_dc_current` | Sensore | mA | HS3, H2 | Fase 2 e successive | No |
| Tensione rete L3 | `sensor.saj_grid_l3_voltage` | Sensore | V | HS3, H2 | Fase 3 e successive | Sì |
| Frequenza rete L3 | `sensor.saj_grid_l3_frequency` | Sensore | Hz | HS3, H2 | Fase 3 e successive | No |
| Corrente continua rete L3 | `sensor.saj_grid_l3_dc_current` | Sensore | mA | HS3, H2 | Fase 3 e successive | No |
| Tensione uscita rete L1 | `sensor.saj_grid_output_l1_voltage` | Sensore | V | HS3, H2 | - | No |
| Corrente uscita rete L1 | `sensor.saj_grid_output_l1_current` | Sensore | A | HS3, H2 | - | No |
| Frequenza uscita rete L1 | `sensor.saj_grid_output_l1_frequency` | Sensore | Hz | HS3, H2 | - | No |
| Potenza uscita rete L1 | `sensor.saj_grid_output_l1_power` | Sensore | W | HS3, H2 | - | No |
| Tensione uscita rete L2 | `sensor.saj_grid_output_l2_voltage` | Sensore | V | HS3, H2 | Fase 2 e successive | No |
| Potenza uscita rete L2 | `sensor.saj_grid_output_l2_power` | Sensore | W | HS3, H2 | Fase 2 e successive | No |
| Tensione uscita rete L3 | `sensor.saj_grid_output_l3_voltage` | Sensore | V | HS3, H2 | Fase 3 e successive | No |
| Potenza uscita rete L3 | `sensor.saj_grid_output_l3_power` | Sensore | W | HS3, H2 | Fase 3 e successive | No |
| Potenza del carico di rete | `sensor.saj_grid_load_power` | Sensore | W | HS3, H2 | - | No |
| Energia immessa in rete L1 oggi | `sensor.saj_grid_l1_export_energy_today` | Sensore | kWh | HS3, H2 | - | No |
| Energia immessa in rete L1 questo mese | `sensor.saj_grid_l1_export_energy_month` | Sensore | kWh | HS3, H2 | - | No |
| Energia immessa in rete L1 quest'anno | `sensor.saj_grid_l1_export_energy_year` | Sensore | kWh | HS3, H2 | - | No |
| Energia immessa in rete L1 totale | `sensor.saj_grid_l1_export_energy_total` | Sensore | kWh | HS3, H2 | - | No |
| Energia prelevata dalla rete L1 oggi | `sensor.saj_grid_l1_import_energy_today` | Sensore | kWh | HS3, H2 | - | No |
| Energia prelevata dalla rete L1 questo mese | `sensor.saj_grid_l1_import_energy_month` | Sensore | kWh | HS3, H2 | - | No |
| Energia prelevata dalla rete L1 quest'anno | `sensor.saj_grid_l1_import_energy_year` | Sensore | kWh | HS3, H2 | - | No |
| Energia prelevata dalla rete L1 totale | `sensor.saj_grid_l1_import_energy_total` | Sensore | kWh | HS3, H2 | - | No |
| Energia immessa in rete L2 oggi | `sensor.saj_grid_l2_export_energy_today` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia immessa in rete L2 questo mese | `sensor.saj_grid_l2_export_energy_month` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia immessa in rete L2 quest'anno | `sensor.saj_grid_l2_export_energy_year` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia immessa in rete L2 totale | `sensor.saj_grid_l2_export_energy_total` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia immessa in rete L3 oggi | `sensor.saj_grid_l3_export_energy_today` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia immessa in rete L3 questo mese | `sensor.saj_grid_l3_export_energy_month` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia immessa in rete L3 quest'anno | `sensor.saj_grid_l3_export_energy_year` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia immessa in rete L3 totale | `sensor.saj_grid_l3_export_energy_total` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia prelevata dalla rete L2 oggi | `sensor.saj_grid_l2_import_energy_today` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia prelevata dalla rete L2 questo mese | `sensor.saj_grid_l2_import_energy_month` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia prelevata dalla rete L2 quest'anno | `sensor.saj_grid_l2_import_energy_year` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia prelevata dalla rete L2 totale | `sensor.saj_grid_l2_import_energy_total` | Sensore | kWh | HS3, H2 | Fase 2 e successive | No |
| Energia prelevata dalla rete L3 oggi | `sensor.saj_grid_l3_import_energy_today` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia prelevata dalla rete L3 questo mese | `sensor.saj_grid_l3_import_energy_month` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia prelevata dalla rete L3 quest'anno | `sensor.saj_grid_l3_import_energy_year` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia prelevata dalla rete L3 totale | `sensor.saj_grid_l3_import_energy_total` | Sensore | kWh | HS3, H2 | Fase 3 e successive | No |
| Energia prelevata dalla rete oggi | `sensor.saj_grid_import_energy_today` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia prelevata dalla rete questo mese | `sensor.saj_grid_import_energy_month` | Sensore | kWh | HS3, H2 | - | No |
| Energia prelevata dalla rete quest'anno | `sensor.saj_grid_import_energy_year` | Sensore | kWh | HS3, H2 | - | No |
| Energia prelevata dalla rete totale | `sensor.saj_grid_import_energy_total` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia immessa in rete oggi | `sensor.saj_grid_export_energy_today` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia immessa in rete questo mese | `sensor.saj_grid_export_energy_month` | Sensore | kWh | HS3, H2 | - | No |
| Energia immessa in rete quest'anno | `sensor.saj_grid_export_energy_year` | Sensore | kWh | HS3, H2 | - | No |
| Energia immessa in rete totale | `sensor.saj_grid_export_energy_total` | Sensore | kWh | HS3, H2 | - | Sì |
| Tensione contatore A L1 | `sensor.saj_meter_a_l1_voltage` | Sensore | V | HS3, H2 | Contatore A | No |
| Corrente contatore A L1 | `sensor.saj_meter_a_l1_current` | Sensore | A | HS3, H2 | Contatore A | No |
| Potenza contatore A L1 | `sensor.saj_meter_a_l1_power` | Sensore | W | HS3, H2 | Contatore A | No |
| Potenza apparente contatore A L1 | `sensor.saj_meter_a_l1_apparent_power` | Sensore | VA | HS3, H2 | Contatore A | No |
| Fattore di potenza contatore A L1 | `sensor.saj_meter_a_l1_power_factor` | Sensore | - | HS3, H2 | Contatore A | No |
| Frequenza contatore A L1 | `sensor.saj_meter_a_l1_frequency` | Sensore | Hz | HS3, H2 | Contatore A | No |
| Tensione contatore A L2 | `sensor.saj_meter_a_l2_voltage` | Sensore | V | HS3, H2 | Contatore A; Fase 2 e successive | No |
| Corrente contatore A L2 | `sensor.saj_meter_a_l2_current` | Sensore | A | HS3, H2 | Contatore A; Fase 2 e successive | No |
| Potenza contatore A L2 | `sensor.saj_meter_a_l2_power` | Sensore | W | HS3, H2 | Contatore A; Fase 2 e successive | No |
| Potenza apparente contatore A L2 | `sensor.saj_meter_a_l2_apparent_power` | Sensore | VA | HS3, H2 | Contatore A; Fase 2 e successive | No |
| Fattore di potenza contatore A L2 | `sensor.saj_meter_a_l2_power_factor` | Sensore | - | HS3, H2 | Contatore A; Fase 2 e successive | No |
| Frequenza contatore A L2 | `sensor.saj_meter_a_l2_frequency` | Sensore | Hz | HS3, H2 | Contatore A; Fase 2 e successive | No |
| Tensione contatore A L3 | `sensor.saj_meter_a_l3_voltage` | Sensore | V | HS3, H2 | Contatore A; Fase 3 e successive | No |
| Corrente contatore A L3 | `sensor.saj_meter_a_l3_current` | Sensore | A | HS3, H2 | Contatore A; Fase 3 e successive | No |
| Potenza contatore A L3 | `sensor.saj_meter_a_l3_power` | Sensore | W | HS3, H2 | Contatore A; Fase 3 e successive | No |
| Potenza apparente contatore A L3 | `sensor.saj_meter_a_l3_apparent_power` | Sensore | VA | HS3, H2 | Contatore A; Fase 3 e successive | No |
| Fattore di potenza contatore A L3 | `sensor.saj_meter_a_l3_power_factor` | Sensore | - | HS3, H2 | Contatore A; Fase 3 e successive | No |
| Frequenza contatore A L3 | `sensor.saj_meter_a_l3_frequency` | Sensore | Hz | HS3, H2 | Contatore A; Fase 3 e successive | No |
| Potenza reattiva contatore A L1 | `sensor.saj_meter_a_l1_reactive_power` | Sensore | var | HS3 | Contatore A | No |
| Potenza reattiva contatore A L2 | `sensor.saj_meter_a_l2_reactive_power` | Sensore | var | HS3 | Contatore A; Fase 2 e successive | No |
| Potenza reattiva contatore A L3 | `sensor.saj_meter_a_l3_reactive_power` | Sensore | var | HS3 | Contatore A; Fase 3 e successive | No |
| Potenza apparente rete L1 | `sensor.saj_grid_l1_apparent_power` | Sensore | VA | HS3 | Contatore A | No |
| Corrente rete L1 | `sensor.saj_grid_l1_current` | Sensore | A | HS3 | Contatore A | No |
| Potenza rete L1 | `sensor.saj_grid_l1_power` | Sensore | W | HS3 | Contatore A | No |
| Fattore di potenza rete L1 | `sensor.saj_grid_l1_power_factor` | Sensore | - | HS3 | Contatore A | No |
| Potenza apparente rete L2 | `sensor.saj_grid_l2_apparent_power` | Sensore | VA | HS3 | Contatore A; Fase 2 e successive | No |
| Corrente rete L2 | `sensor.saj_grid_l2_current` | Sensore | A | HS3 | Contatore A; Fase 2 e successive | No |
| Potenza rete L2 | `sensor.saj_grid_l2_power` | Sensore | W | HS3 | Contatore A; Fase 2 e successive | No |
| Fattore di potenza rete L2 | `sensor.saj_grid_l2_power_factor` | Sensore | - | HS3 | Contatore A; Fase 2 e successive | No |
| Potenza apparente rete L3 | `sensor.saj_grid_l3_apparent_power` | Sensore | VA | HS3 | Contatore A; Fase 3 e successive | No |
| Corrente rete L3 | `sensor.saj_grid_l3_current` | Sensore | A | HS3 | Contatore A; Fase 3 e successive | No |
| Potenza rete L3 | `sensor.saj_grid_l3_power` | Sensore | W | HS3 | Contatore A; Fase 3 e successive | No |
| Fattore di potenza rete L3 | `sensor.saj_grid_l3_power_factor` | Sensore | - | HS3 | Contatore A; Fase 3 e successive | No |
| Potenza della rete | `sensor.saj_grid_power` | Sensore | W | HS3 | Contatore A | Sì |
| Potenza del contatore A | `sensor.saj_meter_a_power` | Sensore | W | HS3, H2 | Contatore A | Sì |
| Tipo di rete | `sensor.saj_grid_type` | Sensore | - | H2 | - | No |
| Corrente rete L1 | `sensor.saj_grid_l1_current` | Sensore | A | H2 | - | No |
| Potenza rete L1 | `sensor.saj_grid_l1_power` | Sensore | W | H2 | - | No |
| Potenza apparente rete L1 | `sensor.saj_grid_l1_apparent_power` | Sensore | VA | H2 | - | No |
| Fattore di potenza rete L1 | `sensor.saj_grid_l1_power_factor` | Sensore | - | H2 | - | No |
| Corrente rete L2 | `sensor.saj_grid_l2_current` | Sensore | A | H2 | Fase 2 e successive | No |
| Potenza rete L2 | `sensor.saj_grid_l2_power` | Sensore | W | H2 | Fase 2 e successive | No |
| Potenza apparente rete L2 | `sensor.saj_grid_l2_apparent_power` | Sensore | VA | H2 | Fase 2 e successive | No |
| Fattore di potenza rete L2 | `sensor.saj_grid_l2_power_factor` | Sensore | - | H2 | Fase 2 e successive | No |
| Corrente rete L3 | `sensor.saj_grid_l3_current` | Sensore | A | H2 | Fase 3 e successive | No |
| Potenza rete L3 | `sensor.saj_grid_l3_power` | Sensore | W | H2 | Fase 3 e successive | No |
| Potenza apparente rete L3 | `sensor.saj_grid_l3_apparent_power` | Sensore | VA | H2 | Fase 3 e successive | No |
| Fattore di potenza rete L3 | `sensor.saj_grid_l3_power_factor` | Sensore | - | H2 | Fase 3 e successive | No |
| Potenza della rete | `sensor.saj_grid_power` | Sensore | W | H2 | - | Sì |
| Potenza apparente della rete | `sensor.saj_grid_apparent_power` | Sensore | VA | H2 | - | No |
