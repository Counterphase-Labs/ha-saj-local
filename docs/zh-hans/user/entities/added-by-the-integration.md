[en](../../../en-gb/user/entities/added-by-the-integration.md) | [de](../../../de/user/entities/added-by-the-integration.md) | [nl](../../../nl/user/entities/added-by-the-integration.md) | [fr](../../../fr/user/entities/added-by-the-integration.md) | zh | [es](../../../es/user/entities/added-by-the-integration.md) | [it](../../../it/user/entities/added-by-the-integration.md) | [pl](../../../pl/user/entities/added-by-the-integration.md) | [sv](../../../sv/user/entities/added-by-the-integration.md)

# 由集成添加

集成在寄存器目录之外添加的实体。

集成功能列表在 [更改设置](../../../../custom_components/saj_local/docs/features.md#changing-settings)和[功率控制](../../../../custom_components/saj_local/docs/features.md#power-control) 中说明了由集成添加实体。

7 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个由集成添加实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `binary_sensor.saj_house_control_allowed`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 允许控制 | `binary_sensor.saj_control_allowed` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池功率控制 | `switch.saj_battery_power_control` | 开关 | - | HS3, H2 | 电池 | 否 |
| 电池功率目标 | `number.saj_battery_power_target` | 数值输入器 | W | HS3, H2 | 电池 | 否 |
| 电网功率控制 | `switch.saj_grid_power_control` | 开关 | - | HS3 | 电表 A | 否 |
| 电网功率目标 | `number.saj_grid_power_target` | 数值输入器 | W | HS3 | 电表 A | 否 |
| 逆变器功率控制 | `switch.saj_inverter_power_control` | 开关 | - | HS3 | - | 否 |
| 逆变器功率目标 | `number.saj_inverter_power_target` | 数值输入器 | W | HS3 | - | 否 |
