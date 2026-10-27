[en](../../../en-gb/user/entities/ev-charger.md) | [de](../../../de/user/entities/ev-charger.md) | [nl](../../../nl/user/entities/ev-charger.md) | [fr](../../../fr/user/entities/ev-charger.md) | zh | [es](../../../es/user/entities/ev-charger.md) | [it](../../../it/user/entities/ev-charger.md) | [pl](../../../pl/user/entities/ev-charger.md) | [sv](../../../sv/user/entities/ev-charger.md)

# 充电桩

充电桩及其充电控制。

集成功能列表在 [可选设备](../../../../custom_components/saj_local/docs/features.md#optional-equipment) 中说明了充电桩实体。

87 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个充电桩实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `sensor.saj_house_ev_serial_number`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 充电桩序列号 | `sensor.saj_ev_serial_number` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩型号 | `sensor.saj_ev_model` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩软件版本 | `sensor.saj_ev_software_version` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩硬件版本 | `sensor.saj_ev_hardware_version` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩相数 | `sensor.saj_ev_phase_count` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩最小功率 | `sensor.saj_ev_minimum_power` | 传感器 | W | HS3 | 充电桩 | 否 |
| 充电桩最大功率 | `sensor.saj_ev_maximum_power` | 传感器 | W | HS3 | 充电桩 | 否 |
| 充电桩工作模式 | `sensor.saj_ev_work_mode` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩状态 | `sensor.saj_ev_status` | 传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩 L1 电压 | `sensor.saj_ev_l1_voltage` | 传感器 | V | HS3 | 充电桩 | 否 |
| 充电桩 L1 电流 | `sensor.saj_ev_l1_current` | 传感器 | A | HS3 | 充电桩 | 否 |
| 充电桩 L2 电压 | `sensor.saj_ev_l2_voltage` | 传感器 | V | HS3 | 充电桩 | 否 |
| 充电桩 L2 电流 | `sensor.saj_ev_l2_current` | 传感器 | A | HS3 | 充电桩 | 否 |
| 充电桩 L3 电压 | `sensor.saj_ev_l3_voltage` | 传感器 | V | HS3 | 充电桩 | 否 |
| 充电桩 L3 电流 | `sensor.saj_ev_l3_current` | 传感器 | A | HS3 | 充电桩 | 否 |
| 充电桩功率 | `sensor.saj_ev_power` | 传感器 | W | HS3 | 充电桩 | 是 |
| 电动汽车充电时长 | `sensor.saj_ev_charge_duration` | 传感器 | min | HS3 | 充电桩 | 否 |
| 充电桩本次充电电量 | `sensor.saj_ev_session_energy` | 传感器 | kWh | HS3 | 充电桩 | 是 |
| 充电桩累计电量 | `sensor.saj_ev_total_energy` | 传感器 | kWh | HS3 | 充电桩 | 是 |
| 充电桩控制导引电压 | `sensor.saj_ev_control_pilot_voltage` | 传感器 | V | HS3 | 充电桩 | 否 |
| 充电桩占空比 | `sensor.saj_ev_duty_cycle` | 传感器 | % | HS3 | 充电桩 | 否 |
| 充电桩远程控制 | `sensor.saj_ev_remote_control` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩电流设定值 | `sensor.saj_ev_current_setpoint` | 传感器 | A | HS3 | 充电桩 | 否 |
| 充电桩本次充电开始 | `sensor.saj_ev_session_start` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩本次充电结束 | `sensor.saj_ev_session_end` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩设置协议版本 | `sensor.saj_ev_settings_protocol_version` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩地址 | `sensor.saj_ev_address` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩波特率 | `sensor.saj_ev_baud_rate` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩数量 | `sensor.saj_ev_charger_count` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩通信超时 | `sensor.saj_ev_communication_timeout` | 传感器 | s | HS3 | 充电桩 | 否 |
| 充电桩端口模式 | `sensor.saj_ev_port_mode` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩端口地址 | `sensor.saj_ev_port_address` | 传感器 | - | HS3 | 充电桩 | 否 |
| 充电桩模式 | `select.saj_ev_mode` | 选择 | - | HS3 | 充电桩 | 是 |
| 电动汽车充电功率 | `number.saj_ev_charge_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩时段 1 开始时间 | `time.saj_ev_slot_1_start` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 1 结束时间 | `time.saj_ev_slot_1_end` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 1 模式 | `select.saj_ev_slot_1_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 1 电网充电 | `switch.saj_ev_slot_1_grid_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 1 电池放电 | `switch.saj_ev_slot_1_battery_discharge` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 1 星期 | `number.saj_ev_slot_1_days` | 数值输入器 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 1 功率 | `number.saj_ev_slot_1_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩时段 2 开始时间 | `time.saj_ev_slot_2_start` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 2 结束时间 | `time.saj_ev_slot_2_end` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 2 模式 | `select.saj_ev_slot_2_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 2 电网充电 | `switch.saj_ev_slot_2_grid_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 2 电池放电 | `switch.saj_ev_slot_2_battery_discharge` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 2 星期 | `number.saj_ev_slot_2_days` | 数值输入器 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 2 功率 | `number.saj_ev_slot_2_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩时段 3 开始时间 | `time.saj_ev_slot_3_start` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 3 结束时间 | `time.saj_ev_slot_3_end` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 3 模式 | `select.saj_ev_slot_3_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 3 电网充电 | `switch.saj_ev_slot_3_grid_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 3 电池放电 | `switch.saj_ev_slot_3_battery_discharge` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 3 星期 | `number.saj_ev_slot_3_days` | 数值输入器 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 3 功率 | `number.saj_ev_slot_3_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩时段 4 开始时间 | `time.saj_ev_slot_4_start` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 4 结束时间 | `time.saj_ev_slot_4_end` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 4 模式 | `select.saj_ev_slot_4_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 4 电网充电 | `switch.saj_ev_slot_4_grid_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 4 电池放电 | `switch.saj_ev_slot_4_battery_discharge` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 4 星期 | `number.saj_ev_slot_4_days` | 数值输入器 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 4 功率 | `number.saj_ev_slot_4_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩时段 5 开始时间 | `time.saj_ev_slot_5_start` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 5 结束时间 | `time.saj_ev_slot_5_end` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 5 模式 | `select.saj_ev_slot_5_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 5 电网充电 | `switch.saj_ev_slot_5_grid_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 5 电池放电 | `switch.saj_ev_slot_5_battery_discharge` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 5 星期 | `number.saj_ev_slot_5_days` | 数值输入器 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 5 功率 | `number.saj_ev_slot_5_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩时段 6 开始时间 | `time.saj_ev_slot_6_start` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 6 结束时间 | `time.saj_ev_slot_6_end` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 6 模式 | `select.saj_ev_slot_6_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 6 电网充电 | `switch.saj_ev_slot_6_grid_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 6 电池放电 | `switch.saj_ev_slot_6_battery_discharge` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 6 星期 | `number.saj_ev_slot_6_days` | 数值输入器 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 6 功率 | `number.saj_ev_slot_6_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩时段 7 开始时间 | `time.saj_ev_slot_7_start` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 7 结束时间 | `time.saj_ev_slot_7_end` | 时间 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 7 模式 | `select.saj_ev_slot_7_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 7 电网充电 | `switch.saj_ev_slot_7_grid_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 7 电池放电 | `switch.saj_ev_slot_7_battery_discharge` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 7 星期 | `number.saj_ev_slot_7_days` | 数值输入器 | - | HS3 | 充电桩 | 否 |
| 充电桩时段 7 功率 | `number.saj_ev_slot_7_power` | 数值输入器 | W | HS3 | 充电桩 | 否 |
| 充电桩最小电流充电 | `switch.saj_ev_minimum_current_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩 EMS 充电 | `switch.saj_ev_ems_charging` | 开关 | - | HS3 | 充电桩 | 否 |
| 充电桩 EMS 相模式 | `select.saj_ev_ems_phase_mode` | 选择 | - | HS3 | 充电桩 | 否 |
| 充电桩 EMS 充电电流 | `number.saj_ev_ems_charge_current` | 数值输入器 | A | HS3 | 充电桩 | 否 |
