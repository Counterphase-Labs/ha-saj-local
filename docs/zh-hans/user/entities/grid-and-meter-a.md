[en](../../../en-gb/user/entities/grid-and-meter-a.md) | [de](../../../de/user/entities/grid-and-meter-a.md) | [nl](../../../nl/user/entities/grid-and-meter-a.md) | [fr](../../../fr/user/entities/grid-and-meter-a.md) | zh | [es](../../../es/user/entities/grid-and-meter-a.md) | [it](../../../it/user/entities/grid-and-meter-a.md) | [pl](../../../pl/user/entities/grid-and-meter-a.md) | [sv](../../../sv/user/entities/grid-and-meter-a.md)

# 电网与电表 A

电网连接和电表 A（电网电表）。

集成功能列表在 [设备与实体](../../../../custom_components/saj_local/docs/features.md#devices-and-entities)和[可选设备](../../../../custom_components/saj_local/docs/features.md#optional-equipment) 中说明了电网与电表 A实体。

88 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个电网与电表 A实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `sensor.saj_house_grid_connection_countdown`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 并网倒计时 | `sensor.saj_grid_connection_countdown` | 传感器 | s | HS3, H2 | - | 否 |
| 电网 L1 电压 | `sensor.saj_grid_l1_voltage` | 传感器 | V | HS3, H2 | - | 是 |
| 电网 L1 电流 | `sensor.saj_grid_l1_current` | 传感器 | A | HS3, H2 | - | 否 |
| 电网 L1 频率 | `sensor.saj_grid_l1_frequency` | 传感器 | Hz | HS3, H2 | - | 是 |
| 电网 L1 直流电流 | `sensor.saj_grid_l1_dc_current` | 传感器 | mA | HS3, H2 | - | 否 |
| 电网 L1 功率 | `sensor.saj_grid_l1_power` | 传感器 | W | HS3, H2 | - | 否 |
| 电网 L1 视在功率 | `sensor.saj_grid_l1_apparent_power` | 传感器 | VA | HS3, H2 | - | 否 |
| 电网 L1 功率因数 | `sensor.saj_grid_l1_power_factor` | 传感器 | - | HS3, H2 | - | 否 |
| 电网 L2 电压 | `sensor.saj_grid_l2_voltage` | 传感器 | V | HS3, H2 | 第 2 相及以上 | 是 |
| 电网 L2 电流 | `sensor.saj_grid_l2_current` | 传感器 | A | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 频率 | `sensor.saj_grid_l2_frequency` | 传感器 | Hz | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 直流电流 | `sensor.saj_grid_l2_dc_current` | 传感器 | mA | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 功率 | `sensor.saj_grid_l2_power` | 传感器 | W | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 视在功率 | `sensor.saj_grid_l2_apparent_power` | 传感器 | VA | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 功率因数 | `sensor.saj_grid_l2_power_factor` | 传感器 | - | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L3 电压 | `sensor.saj_grid_l3_voltage` | 传感器 | V | HS3, H2 | 第 3 相及以上 | 是 |
| 电网 L3 电流 | `sensor.saj_grid_l3_current` | 传感器 | A | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 频率 | `sensor.saj_grid_l3_frequency` | 传感器 | Hz | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 直流电流 | `sensor.saj_grid_l3_dc_current` | 传感器 | mA | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 功率 | `sensor.saj_grid_l3_power` | 传感器 | W | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 视在功率 | `sensor.saj_grid_l3_apparent_power` | 传感器 | VA | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 功率因数 | `sensor.saj_grid_l3_power_factor` | 传感器 | - | HS3, H2 | 第 3 相及以上 | 否 |
| 电网输出 L1 电压 | `sensor.saj_grid_output_l1_voltage` | 传感器 | V | HS3, H2 | - | 否 |
| 电网输出 L1 电流 | `sensor.saj_grid_output_l1_current` | 传感器 | A | HS3, H2 | - | 否 |
| 电网输出 L1 频率 | `sensor.saj_grid_output_l1_frequency` | 传感器 | Hz | HS3, H2 | - | 否 |
| 电网输出 L1 功率 | `sensor.saj_grid_output_l1_power` | 传感器 | W | HS3, H2 | - | 否 |
| 电网输出 L2 电压 | `sensor.saj_grid_output_l2_voltage` | 传感器 | V | HS3, H2 | 第 2 相及以上 | 否 |
| 电网输出 L2 功率 | `sensor.saj_grid_output_l2_power` | 传感器 | W | HS3, H2 | 第 2 相及以上 | 否 |
| 电网输出 L3 电压 | `sensor.saj_grid_output_l3_voltage` | 传感器 | V | HS3, H2 | 第 3 相及以上 | 否 |
| 电网输出 L3 功率 | `sensor.saj_grid_output_l3_power` | 传感器 | W | HS3, H2 | 第 3 相及以上 | 否 |
| 电网功率 | `sensor.saj_grid_power` | 传感器 | W | HS3, H2 | - | 是 |
| 电网负载功率 | `sensor.saj_grid_load_power` | 传感器 | W | HS3, H2 | - | 否 |
| 电网 L1 馈电今日电量 | `sensor.saj_grid_l1_export_energy_today` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L1 馈电本月电量 | `sensor.saj_grid_l1_export_energy_month` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L1 馈电本年电量 | `sensor.saj_grid_l1_export_energy_year` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L1 馈电累计电量 | `sensor.saj_grid_l1_export_energy_total` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L1 购电今日电量 | `sensor.saj_grid_l1_import_energy_today` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L1 购电本月电量 | `sensor.saj_grid_l1_import_energy_month` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L1 购电本年电量 | `sensor.saj_grid_l1_import_energy_year` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L1 购电累计电量 | `sensor.saj_grid_l1_import_energy_total` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网 L2 馈电今日电量 | `sensor.saj_grid_l2_export_energy_today` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 馈电本月电量 | `sensor.saj_grid_l2_export_energy_month` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 馈电本年电量 | `sensor.saj_grid_l2_export_energy_year` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 馈电累计电量 | `sensor.saj_grid_l2_export_energy_total` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L3 馈电今日电量 | `sensor.saj_grid_l3_export_energy_today` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 馈电本月电量 | `sensor.saj_grid_l3_export_energy_month` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 馈电本年电量 | `sensor.saj_grid_l3_export_energy_year` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 馈电累计电量 | `sensor.saj_grid_l3_export_energy_total` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L2 购电今日电量 | `sensor.saj_grid_l2_import_energy_today` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 购电本月电量 | `sensor.saj_grid_l2_import_energy_month` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 购电本年电量 | `sensor.saj_grid_l2_import_energy_year` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L2 购电累计电量 | `sensor.saj_grid_l2_import_energy_total` | 传感器 | kWh | HS3, H2 | 第 2 相及以上 | 否 |
| 电网 L3 购电今日电量 | `sensor.saj_grid_l3_import_energy_today` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 购电本月电量 | `sensor.saj_grid_l3_import_energy_month` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 购电本年电量 | `sensor.saj_grid_l3_import_energy_year` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网 L3 购电累计电量 | `sensor.saj_grid_l3_import_energy_total` | 传感器 | kWh | HS3, H2 | 第 3 相及以上 | 否 |
| 电网购电今日电量 | `sensor.saj_grid_import_energy_today` | 传感器 | kWh | HS3, H2 | - | 是 |
| 电网购电本月电量 | `sensor.saj_grid_import_energy_month` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网购电本年电量 | `sensor.saj_grid_import_energy_year` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网购电累计电量 | `sensor.saj_grid_import_energy_total` | 传感器 | kWh | HS3, H2 | - | 是 |
| 电网馈电今日电量 | `sensor.saj_grid_export_energy_today` | 传感器 | kWh | HS3, H2 | - | 是 |
| 电网馈电本月电量 | `sensor.saj_grid_export_energy_month` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网馈电本年电量 | `sensor.saj_grid_export_energy_year` | 传感器 | kWh | HS3, H2 | - | 否 |
| 电网馈电累计电量 | `sensor.saj_grid_export_energy_total` | 传感器 | kWh | HS3, H2 | - | 是 |
| 电表 A L1 电压 | `sensor.saj_meter_a_l1_voltage` | 传感器 | V | HS3, H2 | 电表 A | 否 |
| 电表 A L1 电流 | `sensor.saj_meter_a_l1_current` | 传感器 | A | HS3, H2 | 电表 A | 否 |
| 电表 A L1 功率 | `sensor.saj_meter_a_l1_power` | 传感器 | W | HS3, H2 | 电表 A | 否 |
| 电表 A L1 视在功率 | `sensor.saj_meter_a_l1_apparent_power` | 传感器 | VA | HS3, H2 | 电表 A | 否 |
| 电表 A L1 功率因数 | `sensor.saj_meter_a_l1_power_factor` | 传感器 | - | HS3, H2 | 电表 A | 否 |
| 电表 A L1 频率 | `sensor.saj_meter_a_l1_frequency` | 传感器 | Hz | HS3, H2 | 电表 A | 否 |
| 电表 A L2 电压 | `sensor.saj_meter_a_l2_voltage` | 传感器 | V | HS3, H2 | 电表 A; 第 2 相及以上 | 否 |
| 电表 A L2 电流 | `sensor.saj_meter_a_l2_current` | 传感器 | A | HS3, H2 | 电表 A; 第 2 相及以上 | 否 |
| 电表 A L2 功率 | `sensor.saj_meter_a_l2_power` | 传感器 | W | HS3, H2 | 电表 A; 第 2 相及以上 | 否 |
| 电表 A L2 视在功率 | `sensor.saj_meter_a_l2_apparent_power` | 传感器 | VA | HS3, H2 | 电表 A; 第 2 相及以上 | 否 |
| 电表 A L2 功率因数 | `sensor.saj_meter_a_l2_power_factor` | 传感器 | - | HS3, H2 | 电表 A; 第 2 相及以上 | 否 |
| 电表 A L2 频率 | `sensor.saj_meter_a_l2_frequency` | 传感器 | Hz | HS3, H2 | 电表 A; 第 2 相及以上 | 否 |
| 电表 A L3 电压 | `sensor.saj_meter_a_l3_voltage` | 传感器 | V | HS3, H2 | 电表 A; 第 3 相及以上 | 否 |
| 电表 A L3 电流 | `sensor.saj_meter_a_l3_current` | 传感器 | A | HS3, H2 | 电表 A; 第 3 相及以上 | 否 |
| 电表 A L3 功率 | `sensor.saj_meter_a_l3_power` | 传感器 | W | HS3, H2 | 电表 A; 第 3 相及以上 | 否 |
| 电表 A L3 视在功率 | `sensor.saj_meter_a_l3_apparent_power` | 传感器 | VA | HS3, H2 | 电表 A; 第 3 相及以上 | 否 |
| 电表 A L3 功率因数 | `sensor.saj_meter_a_l3_power_factor` | 传感器 | - | HS3, H2 | 电表 A; 第 3 相及以上 | 否 |
| 电表 A L3 频率 | `sensor.saj_meter_a_l3_frequency` | 传感器 | Hz | HS3, H2 | 电表 A; 第 3 相及以上 | 否 |
| 电表 A L1 无功功率 | `sensor.saj_meter_a_l1_reactive_power` | 传感器 | var | HS3 | 电表 A | 否 |
| 电表 A L2 无功功率 | `sensor.saj_meter_a_l2_reactive_power` | 传感器 | var | HS3 | 电表 A; 第 2 相及以上 | 否 |
| 电表 A L3 无功功率 | `sensor.saj_meter_a_l3_reactive_power` | 传感器 | var | HS3 | 电表 A; 第 3 相及以上 | 否 |
| 电表 A 功率 | `sensor.saj_meter_a_power` | 传感器 | W | HS3, H2 | 电表 A | 是 |
| 电网类型 | `sensor.saj_grid_type` | 传感器 | - | H2 | - | 否 |
| 电网视在功率 | `sensor.saj_grid_apparent_power` | 传感器 | VA | H2 | - | 否 |
