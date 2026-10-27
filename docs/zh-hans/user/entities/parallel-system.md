[en](../../../en-gb/user/entities/parallel-system.md) | [de](../../../de/user/entities/parallel-system.md) | [nl](../../../nl/user/entities/parallel-system.md) | [fr](../../../fr/user/entities/parallel-system.md) | zh | [es](../../../es/user/entities/parallel-system.md) | [it](../../../it/user/entities/parallel-system.md) | [pl](../../../pl/user/entities/parallel-system.md) | [sv](../../../sv/user/entities/parallel-system.md)

# 并机系统

并机系统的读数。

集成功能列表在 [可选设备](../../../../custom_components/saj_local/docs/features.md#optional-equipment) 中说明了并机系统实体。

63 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个并机系统实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `sensor.saj_house_parallel_id`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 并机机器 ID | `sensor.saj_parallel_id` | 传感器 | - | HS3, H2 | 并机系统 | 否 |
| 并机机器数量 | `sensor.saj_parallel_count` | 传感器 | - | HS3, H2 | 并机系统 | 否 |
| 并机系统电池荷电状态 | `sensor.saj_parallel_battery_soc` | 传感器 | % | HS3, H2 | 并机系统 | 是 |
| 并机系统电池容量 | `sensor.saj_parallel_battery_capacity` | 传感器 | Ah | HS3, H2 | 并机系统 | 否 |
| 并机系统电表 B 功率 | `sensor.saj_parallel_meter_b_power` | 传感器 | W | HS3 | 并机系统 | 否 |
| 并机系统光伏今日电量 | `sensor.saj_parallel_pv_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统光伏本月电量 | `sensor.saj_parallel_pv_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统光伏本年电量 | `sensor.saj_parallel_pv_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统光伏累计电量 | `sensor.saj_parallel_pv_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池充电今日电量 | `sensor.saj_parallel_battery_charge_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池充电本月电量 | `sensor.saj_parallel_battery_charge_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池充电本年电量 | `sensor.saj_parallel_battery_charge_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池充电累计电量 | `sensor.saj_parallel_battery_charge_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池放电今日电量 | `sensor.saj_parallel_battery_discharge_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池放电本月电量 | `sensor.saj_parallel_battery_discharge_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池放电本年电量 | `sensor.saj_parallel_battery_discharge_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电池放电累计电量 | `sensor.saj_parallel_battery_discharge_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 馈电今日电量 | `sensor.saj_parallel_grid_l1_export_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 馈电本月电量 | `sensor.saj_parallel_grid_l1_export_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 馈电本年电量 | `sensor.saj_parallel_grid_l1_export_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 馈电累计电量 | `sensor.saj_parallel_grid_l1_export_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 馈电今日电量 | `sensor.saj_parallel_grid_l2_export_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 馈电本月电量 | `sensor.saj_parallel_grid_l2_export_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 馈电本年电量 | `sensor.saj_parallel_grid_l2_export_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 馈电累计电量 | `sensor.saj_parallel_grid_l2_export_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 馈电今日电量 | `sensor.saj_parallel_grid_l3_export_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 馈电本月电量 | `sensor.saj_parallel_grid_l3_export_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 馈电本年电量 | `sensor.saj_parallel_grid_l3_export_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 馈电累计电量 | `sensor.saj_parallel_grid_l3_export_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 购电今日电量 | `sensor.saj_parallel_grid_l1_import_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 购电本月电量 | `sensor.saj_parallel_grid_l1_import_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 购电本年电量 | `sensor.saj_parallel_grid_l1_import_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L1 购电累计电量 | `sensor.saj_parallel_grid_l1_import_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 购电今日电量 | `sensor.saj_parallel_grid_l2_import_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 购电本月电量 | `sensor.saj_parallel_grid_l2_import_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 购电本年电量 | `sensor.saj_parallel_grid_l2_import_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L2 购电累计电量 | `sensor.saj_parallel_grid_l2_import_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 购电今日电量 | `sensor.saj_parallel_grid_l3_import_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 购电本月电量 | `sensor.saj_parallel_grid_l3_import_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 购电本年电量 | `sensor.saj_parallel_grid_l3_import_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网 L3 购电累计电量 | `sensor.saj_parallel_grid_l3_import_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统家庭负载今日电量 | `sensor.saj_parallel_load_energy_today` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统家庭负载本月电量 | `sensor.saj_parallel_load_energy_month` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统家庭负载本年电量 | `sensor.saj_parallel_load_energy_year` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统家庭负载累计电量 | `sensor.saj_parallel_load_energy_total` | 传感器 | kWh | HS3, H2 | 并机系统 | 否 |
| 并机系统电网购电今日电量 | `sensor.saj_parallel_grid_import_energy_today` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统电网购电本月电量 | `sensor.saj_parallel_grid_import_energy_month` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统电网购电本年电量 | `sensor.saj_parallel_grid_import_energy_year` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统电网购电累计电量 | `sensor.saj_parallel_grid_import_energy_total` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统电网馈电今日电量 | `sensor.saj_parallel_grid_export_energy_today` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统电网馈电本月电量 | `sensor.saj_parallel_grid_export_energy_month` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统电网馈电本年电量 | `sensor.saj_parallel_grid_export_energy_year` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统电网馈电累计电量 | `sensor.saj_parallel_grid_export_energy_total` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统光伏电表今日电量 | `sensor.saj_parallel_pv_meter_energy_today` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统光伏电表本月电量 | `sensor.saj_parallel_pv_meter_energy_month` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统光伏电表本年电量 | `sensor.saj_parallel_pv_meter_energy_year` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统光伏电表累计电量 | `sensor.saj_parallel_pv_meter_energy_total` | 传感器 | kWh | HS3 | 并机系统 | 否 |
| 并机系统备用负载功率 | `sensor.saj_parallel_backup_load_power` | 传感器 | W | HS3, H2 | 并机系统 | 否 |
| 并机系统电池功率 | `sensor.saj_parallel_battery_power` | 传感器 | W | HS3, H2 | 并机系统 | 是 |
| 并机系统电网负载功率 | `sensor.saj_parallel_grid_load_power` | 传感器 | W | HS3, H2 | 并机系统 | 否 |
| 并机系统电网功率 | `sensor.saj_parallel_grid_power` | 传感器 | W | HS3, H2 | 并机系统 | 是 |
| 并机系统家庭负载功率 | `sensor.saj_parallel_load_power` | 传感器 | W | HS3, H2 | 并机系统 | 是 |
| 并机系统光伏功率 | `sensor.saj_parallel_pv_power` | 传感器 | W | HS3, H2 | 并机系统 | 是 |
