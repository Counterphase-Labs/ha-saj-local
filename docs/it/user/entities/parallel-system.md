[en](../../../en-gb/user/entities/parallel-system.md) | [de](../../../de/user/entities/parallel-system.md) | [nl](../../../nl/user/entities/parallel-system.md) | [fr](../../../fr/user/entities/parallel-system.md) | [zh](../../../zh-hans/user/entities/parallel-system.md) | [es](../../../es/user/entities/parallel-system.md) | it | [pl](../../../pl/user/entities/parallel-system.md) | [sv](../../../sv/user/entities/parallel-system.md)

# Sistema in parallelo

Le letture di un sistema di macchine in parallelo.

Le entità dell'area «Sistema in parallelo» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Apparecchiature opzionali](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

63 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Sistema in parallelo», per esempio `sensor.saj_house_parallel_id` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| ID della macchina in parallelo | `sensor.saj_parallel_id` | Sensore | - | HS3, H2 | Sistema in parallelo | No |
| Numero di macchine in parallelo | `sensor.saj_parallel_count` | Sensore | - | HS3, H2 | Sistema in parallelo | No |
| Stato di carica della batteria del sistema in parallelo | `sensor.saj_parallel_battery_soc` | Sensore | % | HS3, H2 | Sistema in parallelo | Sì |
| Capacità della batteria del sistema in parallelo | `sensor.saj_parallel_battery_capacity` | Sensore | Ah | HS3, H2 | Sistema in parallelo | No |
| Potenza del contatore B del sistema in parallelo | `sensor.saj_parallel_meter_b_power` | Sensore | W | HS3 | Sistema in parallelo | No |
| Energia solare del sistema in parallelo oggi | `sensor.saj_parallel_pv_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia solare del sistema in parallelo questo mese | `sensor.saj_parallel_pv_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia solare del sistema in parallelo quest'anno | `sensor.saj_parallel_pv_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia solare del sistema in parallelo totale | `sensor.saj_parallel_pv_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di carica della batteria del sistema in parallelo oggi | `sensor.saj_parallel_battery_charge_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di carica della batteria del sistema in parallelo questo mese | `sensor.saj_parallel_battery_charge_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di carica della batteria del sistema in parallelo quest'anno | `sensor.saj_parallel_battery_charge_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di carica della batteria del sistema in parallelo totale | `sensor.saj_parallel_battery_charge_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di scarica della batteria del sistema in parallelo oggi | `sensor.saj_parallel_battery_discharge_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di scarica della batteria del sistema in parallelo questo mese | `sensor.saj_parallel_battery_discharge_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di scarica della batteria del sistema in parallelo quest'anno | `sensor.saj_parallel_battery_discharge_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia di scarica della batteria del sistema in parallelo totale | `sensor.saj_parallel_battery_discharge_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L1 del sistema in parallelo oggi | `sensor.saj_parallel_grid_l1_export_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L1 del sistema in parallelo questo mese | `sensor.saj_parallel_grid_l1_export_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L1 del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_l1_export_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L1 del sistema in parallelo totale | `sensor.saj_parallel_grid_l1_export_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L2 del sistema in parallelo oggi | `sensor.saj_parallel_grid_l2_export_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L2 del sistema in parallelo questo mese | `sensor.saj_parallel_grid_l2_export_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L2 del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_l2_export_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L2 del sistema in parallelo totale | `sensor.saj_parallel_grid_l2_export_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L3 del sistema in parallelo oggi | `sensor.saj_parallel_grid_l3_export_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L3 del sistema in parallelo questo mese | `sensor.saj_parallel_grid_l3_export_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L3 del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_l3_export_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia immessa in rete L3 del sistema in parallelo totale | `sensor.saj_parallel_grid_l3_export_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L1 del sistema in parallelo oggi | `sensor.saj_parallel_grid_l1_import_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L1 del sistema in parallelo questo mese | `sensor.saj_parallel_grid_l1_import_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L1 del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_l1_import_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L1 del sistema in parallelo totale | `sensor.saj_parallel_grid_l1_import_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L2 del sistema in parallelo oggi | `sensor.saj_parallel_grid_l2_import_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L2 del sistema in parallelo questo mese | `sensor.saj_parallel_grid_l2_import_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L2 del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_l2_import_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L2 del sistema in parallelo totale | `sensor.saj_parallel_grid_l2_import_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L3 del sistema in parallelo oggi | `sensor.saj_parallel_grid_l3_import_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L3 del sistema in parallelo questo mese | `sensor.saj_parallel_grid_l3_import_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L3 del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_l3_import_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete L3 del sistema in parallelo totale | `sensor.saj_parallel_grid_l3_import_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia del carico domestico del sistema in parallelo oggi | `sensor.saj_parallel_load_energy_today` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia del carico domestico del sistema in parallelo questo mese | `sensor.saj_parallel_load_energy_month` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia del carico domestico del sistema in parallelo quest'anno | `sensor.saj_parallel_load_energy_year` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia del carico domestico del sistema in parallelo totale | `sensor.saj_parallel_load_energy_total` | Sensore | kWh | HS3, H2 | Sistema in parallelo | No |
| Energia prelevata dalla rete del sistema in parallelo oggi | `sensor.saj_parallel_grid_import_energy_today` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia prelevata dalla rete del sistema in parallelo questo mese | `sensor.saj_parallel_grid_import_energy_month` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia prelevata dalla rete del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_import_energy_year` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia prelevata dalla rete del sistema in parallelo totale | `sensor.saj_parallel_grid_import_energy_total` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia immessa in rete del sistema in parallelo oggi | `sensor.saj_parallel_grid_export_energy_today` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia immessa in rete del sistema in parallelo questo mese | `sensor.saj_parallel_grid_export_energy_month` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia immessa in rete del sistema in parallelo quest'anno | `sensor.saj_parallel_grid_export_energy_year` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia immessa in rete del sistema in parallelo totale | `sensor.saj_parallel_grid_export_energy_total` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia del contatore solare del sistema in parallelo oggi | `sensor.saj_parallel_pv_meter_energy_today` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia del contatore solare del sistema in parallelo questo mese | `sensor.saj_parallel_pv_meter_energy_month` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia del contatore solare del sistema in parallelo quest'anno | `sensor.saj_parallel_pv_meter_energy_year` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Energia del contatore solare del sistema in parallelo totale | `sensor.saj_parallel_pv_meter_energy_total` | Sensore | kWh | HS3 | Sistema in parallelo | No |
| Potenza dei carichi di backup del sistema in parallelo | `sensor.saj_parallel_backup_load_power` | Sensore | W | HS3, H2 | Sistema in parallelo | No |
| Potenza della batteria del sistema in parallelo | `sensor.saj_parallel_battery_power` | Sensore | W | HS3, H2 | Sistema in parallelo | Sì |
| Potenza del carico di rete del sistema in parallelo | `sensor.saj_parallel_grid_load_power` | Sensore | W | HS3, H2 | Sistema in parallelo | No |
| Potenza della rete del sistema in parallelo | `sensor.saj_parallel_grid_power` | Sensore | W | HS3, H2 | Sistema in parallelo | Sì |
| Potenza del carico domestico del sistema in parallelo | `sensor.saj_parallel_load_power` | Sensore | W | HS3, H2 | Sistema in parallelo | Sì |
| Potenza solare del sistema in parallelo | `sensor.saj_parallel_pv_power` | Sensore | W | HS3, H2 | Sistema in parallelo | Sì |
