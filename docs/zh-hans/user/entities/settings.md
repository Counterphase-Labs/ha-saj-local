[en](../../../en-gb/user/entities/settings.md) | [de](../../../de/user/entities/settings.md) | [nl](../../../nl/user/entities/settings.md) | [fr](../../../fr/user/entities/settings.md) | zh | [es](../../../es/user/entities/settings.md) | [it](../../../it/user/entities/settings.md) | [pl](../../../pl/user/entities/settings.md) | [sv](../../../sv/user/entities/settings.md)

# 设置

更改逆变器的设置和命令。

集成功能列表在 [更改设置](../../../../custom_components/saj_local/docs/features.md#changing-settings) 中说明了设置实体。

22 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个设置实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `number.saj_house_passive_mode`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 被动模式 | `number.saj_passive_mode` | 数值输入器 | - | HS3, H2 | - | 否 |
| 被动模式电网充电功率 | `number.saj_passive_grid_charge_power` | 数值输入器 | % | HS3, H2 | - | 否 |
| 被动模式电网放电功率 | `number.saj_passive_grid_discharge_power` | 数值输入器 | % | HS3, H2 | - | 否 |
| 应用模式 | `select.saj_application_mode` | 选择 | - | HS3, H2 | - | 是 |
| 电网购电功率限制 | `number.saj_grid_import_power_limit` | 数值输入器 | % | HS3, H2 | - | 否 |
| 电网馈电功率限制 | `number.saj_grid_export_power_limit` | 数值输入器 | % | HS3, H2 | - | 否 |
| 馈电限制功率 | `number.saj_export_limit_power` | 数值输入器 | % | HS3, H2 | - | 否 |
| 馈电限制电流 | `number.saj_export_limit_current` | 数值输入器 | A | HS3, H2 | - | 否 |
| 馈电限制模式 | `select.saj_export_limit_mode` | 选择 | - | HS3, H2 | - | 否 |
| 分时空闲模式 | `select.saj_time_of_use_idle_mode` | 选择 | - | HS3, H2 | - | 否 |
| 分时电网放电 | `switch.saj_time_of_use_grid_discharge` | 开关 | - | HS3, H2 | - | 否 |
| LED 模式 | `select.saj_led_mode` | 选择 | - | HS3, H2 | - | 否 |
| 充电桩已启用 | `switch.saj_ev_enabled` | 开关 | - | HS3 | - | 否 |
| 清除当前故障 | `button.saj_clear_current_fault` | 按钮 | - | HS3, H2 | - | 否 |
| 重启逆变器 | `button.saj_restart_inverter` | 按钮 | - | HS3, H2 | - | 否 |
| 同步时钟 | `button.saj_synchronise_clock` | 按钮 | - | HS3, H2 | - | 否 |
| EMS 超时 | `number.saj_ems_timeout` | 数值输入器 | s | HS3 | - | 否 |
| EMS 逆变器输入功率限制 | `number.saj_ems_inverter_import_power_limit` | 数值输入器 | % | HS3 | - | 否 |
| EMS 逆变器输出功率限制 | `number.saj_ems_inverter_export_power_limit` | 数值输入器 | % | HS3 | - | 否 |
| EMS 光伏功率限制 | `number.saj_ems_pv_power_limit` | 数值输入器 | % | HS3 | - | 否 |
| 移除 EMS 光伏功率限制 | `button.saj_ems_pv_power_limit_remove` | 按钮 | - | HS3 | - | 否 |
| 蜂鸣器 | `switch.saj_buzzer` | 开关 | - | H2 | - | 否 |
