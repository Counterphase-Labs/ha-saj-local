[en](../../../en-gb/user/entities/faults.md) | de | [nl](../../../nl/user/entities/faults.md) | [fr](../../../fr/user/entities/faults.md) | [zh](../../../zh-hans/user/entities/faults.md) | [es](../../../es/user/entities/faults.md) | [it](../../../it/user/entities/faults.md) | [pl](../../../pl/user/entities/faults.md) | [sv](../../../sv/user/entities/faults.md)

# Fehler

Fehler, die der Wechselrichter, die Batterie und die Wallbox melden.

Die Funktionsliste der Integration erklärt die Entitäten (Fehler) in [Gerätefehler und Reparaturen](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs).

139 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Fehler), zum Beispiel `binary_sensor.saj_house_battery_pack1_fault` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Batteriepack 1 Fehler | `binary_sensor.saj_battery_pack1_fault` | Binärsensor | - | HS3, H2 | Batterie | Ja |
| Batteriepack 1 Warnung | `binary_sensor.saj_battery_pack1_warning` | Binärsensor | - | HS3, H2 | Batterie | Ja |
| Batteriefehler | `binary_sensor.saj_battery_fault` | Binärsensor | - | HS3, H2 | Batterie | Ja |
| BMS-Hersteller der Batterie nicht kompatibel | `binary_sensor.saj_battery_fault_bms_incompatible` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie-Leistungsschalter offen | `binary_sensor.saj_battery_fault_breaker_open` | Binärsensor | - | HS3 | Batterie | Ja |
| Batteriezellen passen nicht zusammen | `binary_sensor.saj_battery_fault_cell_incompatible` | Binärsensor | - | HS3 | Batterie | Ja |
| Batteriezellen-Übertemperatur | `binary_sensor.saj_battery_fault_cell_over_temperature` | Binärsensor | - | HS3 | Batterie | Ja |
| Batteriezellen-Überspannung | `binary_sensor.saj_battery_fault_cell_overvoltage` | Binärsensor | - | HS3 | Batterie | Ja |
| Zellhersteller der Batterie passt nicht | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | Binärsensor | - | HS3 | Batterie | Ja |
| Temperaturunterschied der Batteriezellen zu groß | `binary_sensor.saj_battery_fault_cell_temperature_difference` | Binärsensor | - | HS3 | Batterie | Ja |
| Batteriezellen-Unterspannung | `binary_sensor.saj_battery_fault_cell_undervoltage` | Binärsensor | - | HS3 | Batterie | Ja |
| Spannungsunterschied der Batteriezellen zu groß, Stufe 1 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | Binärsensor | - | HS3 | Batterie | Ja |
| Spannungsunterschied der Batteriezellen zu groß, Stufe 2 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie zu kalt zum Laden | `binary_sensor.saj_battery_fault_charge_cold` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie zu heiß zum Laden | `binary_sensor.saj_battery_fault_charge_hot` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie-Ladeüberstrom | `binary_sensor.saj_battery_fault_charge_overcurrent` | Binärsensor | - | HS3 | Batterie | Ja |
| Überspannung am Ladeanschluss der Batterie | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie zu kalt zum Entladen | `binary_sensor.saj_battery_fault_discharge_cold` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie zu heiß zum Entladen | `binary_sensor.saj_battery_fault_discharge_hot` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie-Entladeüberstrom | `binary_sensor.saj_battery_fault_discharge_overcurrent` | Binärsensor | - | HS3 | Batterie | Ja |
| Sicherungsfehler der Batterie | `binary_sensor.saj_battery_fault_fuse` | Binärsensor | - | HS3 | Batterie | Ja |
| BMS-Hardwarefehler der Batterie | `binary_sensor.saj_battery_fault_hardware` | Binärsensor | - | HS3 | Batterie | Ja |
| BMS-Isolationsfehler der Batterie | `binary_sensor.saj_battery_fault_insulation` | Binärsensor | - | HS3 | Batterie | Ja |
| Interne BMS-Kommunikation der Batterie verloren | `binary_sensor.saj_battery_fault_internal_communication` | Binärsensor | - | HS3 | Batterie | Ja |
| Adressierungsfehler der Batteriepacks | `binary_sensor.saj_battery_fault_pack_sequence` | Binärsensor | - | HS3 | Batterie | Ja |
| Vorladefehler der Batterie | `binary_sensor.saj_battery_fault_precharge` | Binärsensor | - | HS3 | Batterie | Ja |
| BMS-Relaisfehler der Batterie | `binary_sensor.saj_battery_fault_relay` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie-Kurzschluss | `binary_sensor.saj_battery_fault_short_circuit` | Binärsensor | - | HS3 | Batterie | Ja |
| Batteriesystem gesperrt | `binary_sensor.saj_battery_fault_system_locked` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie-Gesamtspannung zu hoch | `binary_sensor.saj_battery_fault_total_overvoltage` | Binärsensor | - | HS3 | Batterie | Ja |
| Batterie-Gesamtspannung zu niedrig | `binary_sensor.saj_battery_fault_total_undervoltage` | Binärsensor | - | HS3 | Batterie | Ja |
| Abgleich der Batterie-Gesamtspannung fehlgeschlagen | `binary_sensor.saj_battery_fault_total_voltage_matching` | Binärsensor | - | HS3 | Batterie | Ja |
| Nicht erkannter Batteriefehler | `binary_sensor.saj_battery_fault_unrecognised` | Binärsensor | - | HS3, H2 | Batterie | Ja |
| Spannungsniveau der Batterie passt nicht | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | Binärsensor | - | HS3 | Batterie | Ja |
| Wallbox-Fehler | `binary_sensor.saj_ev_fault` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-AC-Überstrom | `binary_sensor.saj_ev_fault_ac_overcurrent` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-AC-Überfrequenz | `binary_sensor.saj_ev_fault_ac_overfrequency` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-AC-Überspannung | `binary_sensor.saj_ev_fault_ac_overvoltage` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-AC-Fehlerstrom | `binary_sensor.saj_ev_fault_ac_residual_current` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-AC-Unterfrequenz | `binary_sensor.saj_ev_fault_ac_underfrequency` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-AC-Unterspannung | `binary_sensor.saj_ev_fault_ac_undervoltage` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Bluetooth-Fehler | `binary_sensor.saj_ev_fault_bluetooth` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Steckerstromfehler | `binary_sensor.saj_ev_fault_connector_current` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Steckerverriegelungsfehler | `binary_sensor.saj_ev_fault_connector_lock` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Control-Pilot-Fehler (unter 2 V) | `binary_sensor.saj_ev_fault_control_pilot` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-DC-Fehlerstromfehler A | `binary_sensor.saj_ev_fault_dc_residual_current_a` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-DC-Fehlerstromfehler B | `binary_sensor.saj_ev_fault_dc_residual_current_b` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-DC-Fehlerstromfehler C | `binary_sensor.saj_ev_fault_dc_residual_current_c` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Not-Aus | `binary_sensor.saj_ev_fault_emergency_stop` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Erdungsfehler | `binary_sensor.saj_ev_fault_grounding` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Eingangsklemmen-Übertemperatur | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Zählerfehler | `binary_sensor.saj_ev_fault_meter` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Überlast | `binary_sensor.saj_ev_fault_overload` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Phasenfolgefehler | `binary_sensor.saj_ev_fault_phase_sequence` | Binärsensor | - | HS3 | Wallbox | Ja |
| RCD-Schaltungsfehler der Wallbox | `binary_sensor.saj_ev_fault_rcd_circuit` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Relaisfehler | `binary_sensor.saj_ev_fault_relay` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Relais-Übertemperatur | `binary_sensor.saj_ev_fault_relay_over_temperature` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-RS485-Kommunikations-Timeout | `binary_sensor.saj_ev_fault_rs485_timeout` | Binärsensor | - | HS3 | Wallbox | Ja |
| Stromversorgungsfehler der Wallbox | `binary_sensor.saj_ev_fault_supply` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wallbox-Untertemperatur | `binary_sensor.saj_ev_fault_under_temperature` | Binärsensor | - | HS3 | Wallbox | Ja |
| Nicht erkannter Wallbox-Fehler | `binary_sensor.saj_ev_fault_unrecognised` | Binärsensor | - | HS3 | Wallbox | Ja |
| Wechselrichterfehler | `binary_sensor.saj_inverter_fault` | Binärsensor | - | HS3, H2 | - | Ja |
| Kommunikation der Lichtbogenerkennungsplatine verloren | `binary_sensor.saj_inverter_fault_afci_communication` | Binärsensor | - | HS3 | - | Ja |
| Lichtbogenfehler | `binary_sensor.saj_inverter_fault_arc` | Binärsensor | - | HS3, H2 | - | Ja |
| Fehler der Lichtbogenerkennung | `binary_sensor.saj_inverter_fault_arc_device` | Binärsensor | - | HS3 | - | Ja |
| Autorisierung abgelaufen | `binary_sensor.saj_inverter_fault_authorisation_expired` | Binärsensor | - | HS3, H2 | - | Ja |
| Batterie-Ladespannung zu hoch | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Batterie-Entladespannung zu niedrig | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Batterie-Leerlauf | `binary_sensor.saj_inverter_fault_battery_open_circuit` | Binärsensor | - | HS3, H2 | - | Ja |
| Batterieanschluss-Überstrom | `binary_sensor.saj_inverter_fault_battery_overcurrent` | Binärsensor | - | HS3, H2 | - | Ja |
| Batterieanschluss-Überlast | `binary_sensor.saj_inverter_fault_battery_overload` | Binärsensor | - | HS3, H2 | - | Ja |
| Batterieanschluss-Überspannung | `binary_sensor.saj_inverter_fault_battery_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Zeitüberschreitung beim Batterie-Sanftanlauf | `binary_sensor.saj_inverter_fault_battery_soft_start` | Binärsensor | - | HS3, H2 | - | Ja |
| BMS-Kommunikation verloren | `binary_sensor.saj_inverter_fault_bms_communication` | Binärsensor | - | HS3, H2 | - | Ja |
| BMS-Gerätefehler | `binary_sensor.saj_inverter_fault_bms_device` | Binärsensor | - | HS3, H2 | - | Ja |
| Zwischenkreis-Hardware-Überspannung | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Zwischenkreis-Spannungsungleichgewicht | `binary_sensor.saj_inverter_fault_bus_imbalance` | Binärsensor | - | HS3, H2 | - | Ja |
| Speicherfehler des Controllers | `binary_sensor.saj_inverter_fault_controller_memory` | Binärsensor | - | HS3, H2 | - | Ja |
| CT-Gerätefehler | `binary_sensor.saj_inverter_fault_ct_device` | Binärsensor | - | HS3 | - | Ja |
| Stromsensorfehler | `binary_sensor.saj_inverter_fault_current_sensor` | Binärsensor | - | HS3, H2 | - | Ja |
| Fehler des Gleichstromeinspeisungssensors | `binary_sensor.saj_inverter_fault_dc_injection_device` | Binärsensor | - | HS3, H2 | - | Ja |
| Kommunikation der DC-DC-Einheit verloren | `binary_sensor.saj_inverter_fault_dcdc_communication` | Binärsensor | - | HS3 | - | Ja |
| Fehler der DC-DC-Einheit | `binary_sensor.saj_inverter_fault_dcdc_device` | Binärsensor | - | HS3 | - | Ja |
| Uhrfehler der Anzeigeplatine | `binary_sensor.saj_inverter_fault_display_clock` | Binärsensor | - | HS3, H2 | - | Ja |
| Kommunikation der Anzeigeplatine verloren | `binary_sensor.saj_inverter_fault_display_communication` | Binärsensor | - | HS3, H2 | - | Ja |
| Speicherfehler der Anzeigeplatine | `binary_sensor.saj_inverter_fault_display_memory` | Binärsensor | - | HS3, H2 | - | Ja |
| DRM0-Fehler | `binary_sensor.saj_inverter_fault_drm0` | Binärsensor | - | HS3, H2 | - | Ja |
| Wallbox-Kommunikation verloren | `binary_sensor.saj_inverter_fault_ev_charger_communication` | Binärsensor | - | HS3 | - | Ja |
| Lüfter-1-Fehler | `binary_sensor.saj_inverter_fault_fan_1` | Binärsensor | - | HS3, H2 | - | Ja |
| Lüfter-2-Fehler | `binary_sensor.saj_inverter_fault_fan_2` | Binärsensor | - | HS3, H2 | - | Ja |
| Lüfter-3-Fehler | `binary_sensor.saj_inverter_fault_fan_3` | Binärsensor | - | HS3, H2 | - | Ja |
| Lüfter-4-Fehler | `binary_sensor.saj_inverter_fault_fan_4` | Binärsensor | - | HS3, H2 | - | Ja |
| Überspannung 10-Minuten-Mittelwert Netz | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzausfall | `binary_sensor.saj_inverter_fault_grid_lost` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzüberfrequenz | `binary_sensor.saj_inverter_fault_grid_overfrequency` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase R Gleichstromeinspeisung zu hoch | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase R Gleichspannung zu hoch | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase R Überspannung | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase R Unterspannung | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase S Gleichstromeinspeisung zu hoch | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase S Gleichspannung zu hoch | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase S Überspannung | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase S Unterspannung | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase T Gleichstromeinspeisung zu hoch | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase T Gleichspannung zu hoch | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase T Überspannung | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzphase T Unterspannung | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Netzunterfrequenz | `binary_sensor.saj_inverter_fault_grid_underfrequency` | Binärsensor | - | HS3, H2 | - | Ja |
| Wechselrichter-Hardware-Überstrom | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | Binärsensor | - | HS3, H2 | - | Ja |
| Isolationsfehler | `binary_sensor.saj_inverter_fault_insulation` | Binärsensor | - | HS3, H2 | - | Ja |
| Interne Kommunikation verloren | `binary_sensor.saj_inverter_fault_internal_communication` | Binärsensor | - | HS3, H2 | - | Ja |
| Ableitstromfehler | `binary_sensor.saj_inverter_fault_leakage_current` | Binärsensor | - | HS3, H2 | - | Ja |
| Fehler des Ableitstromsensors | `binary_sensor.saj_inverter_fault_leakage_current_device` | Binärsensor | - | HS3, H2 | - | Ja |
| Zählerkommunikation verloren | `binary_sensor.saj_inverter_fault_meter_communication` | Binärsensor | - | HS3, H2 | - | Ja |
| Spannungsfehler Neutralleiter-Erde | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Ausgang (netzunabhängig) Unterspannung | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| Ausgang Überlast | `binary_sensor.saj_inverter_fault_output_overload` | Binärsensor | - | HS3, H2 | - | Ja |
| Übertemperatur | `binary_sensor.saj_inverter_fault_over_temperature` | Binärsensor | - | HS3, H2 | - | Ja |
| Kommunikation des Parallelsystems verloren | `binary_sensor.saj_inverter_fault_parallel_communication` | Binärsensor | - | HS3 | - | Ja |
| PV-Hardware-Überstrom | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | Binärsensor | - | HS3, H2 | - | Ja |
| PV-Eingangsfehler | `binary_sensor.saj_inverter_fault_pv_input` | Binärsensor | - | HS3, H2 | - | Ja |
| Fehler des PV-Eingangsmodus | `binary_sensor.saj_inverter_fault_pv_input_mode` | Binärsensor | - | HS3, H2 | - | Ja |
| Kommunikation des Solarzählers verloren | `binary_sensor.saj_inverter_fault_pv_meter_communication` | Binärsensor | - | HS3 | - | Ja |
| PV-Überspannung | `binary_sensor.saj_inverter_fault_pv_overvoltage` | Binärsensor | - | HS3, H2 | - | Ja |
| PV-Software-Überstrom | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | Binärsensor | - | HS3, H2 | - | Ja |
| Relaisfehler | `binary_sensor.saj_inverter_fault_relay` | Binärsensor | - | HS3, H2 | - | Ja |
| Kommunikation des Slave-Controllers verloren | `binary_sensor.saj_inverter_fault_slave_communication` | Binärsensor | - | HS3 | - | Ja |
| Untertemperatur | `binary_sensor.saj_inverter_fault_under_temperature` | Binärsensor | - | HS3, H2 | - | Ja |
| Nicht erkannter Wechselrichterfehler | `binary_sensor.saj_inverter_fault_unrecognised` | Binärsensor | - | HS3, H2 | - | Ja |
| Batteriepack 2 Fehler | `binary_sensor.saj_battery_pack2_fault` | Binärsensor | - | H2 | Batterie; Batteriepack 2 und höher | Ja |
| Batteriepack 2 Warnung | `binary_sensor.saj_battery_pack2_warning` | Binärsensor | - | H2 | Batterie; Batteriepack 2 und höher | Ja |
| Batteriepack 3 Fehler | `binary_sensor.saj_battery_pack3_fault` | Binärsensor | - | H2 | Batterie; Batteriepack 3 und höher | Ja |
| Batteriepack 3 Warnung | `binary_sensor.saj_battery_pack3_warning` | Binärsensor | - | H2 | Batterie; Batteriepack 3 und höher | Ja |
| Batteriepack 4 Fehler | `binary_sensor.saj_battery_pack4_fault` | Binärsensor | - | H2 | Batterie; Batteriepack 4 und höher | Ja |
| Batteriepack 4 Warnung | `binary_sensor.saj_battery_pack4_warning` | Binärsensor | - | H2 | Batterie; Batteriepack 4 und höher | Ja |
| Zwischenkreis-Überspannung | `binary_sensor.saj_inverter_fault_bus_overvoltage` | Binärsensor | - | H2 | - | Ja |
| Zwischenkreis-Unterspannung | `binary_sensor.saj_inverter_fault_bus_undervoltage` | Binärsensor | - | H2 | - | Ja |
| Netzphasenfehler | `binary_sensor.saj_inverter_fault_grid_phase` | Binärsensor | - | H2 | - | Ja |
| Inselbildung | `binary_sensor.saj_inverter_fault_islanding` | Binärsensor | - | H2 | - | Ja |
