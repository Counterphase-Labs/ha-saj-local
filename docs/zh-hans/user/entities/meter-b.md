[en](../../../en-gb/user/entities/meter-b.md) | [de](../../../de/user/entities/meter-b.md) | [nl](../../../nl/user/entities/meter-b.md) | [fr](../../../fr/user/entities/meter-b.md) | zh | [es](../../../es/user/entities/meter-b.md) | [it](../../../it/user/entities/meter-b.md) | [pl](../../../pl/user/entities/meter-b.md) | [sv](../../../sv/user/entities/meter-b.md)

# 电表 B

电表 B，测量光伏逆变器的第二块电表。

集成功能列表在 [可选设备](../../../../custom_components/saj_local/docs/features.md#optional-equipment) 中说明了电表 B实体。

22 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个电表 B实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `sensor.saj_house_meter_b_l1_voltage`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 电表 B L1 电压 | `sensor.saj_meter_b_l1_voltage` | 传感器 | V | HS3, H2 | 电表 B | 否 |
| 电表 B L1 电流 | `sensor.saj_meter_b_l1_current` | 传感器 | A | HS3, H2 | 电表 B | 否 |
| 电表 B L1 功率 | `sensor.saj_meter_b_l1_power` | 传感器 | W | HS3, H2 | 电表 B | 否 |
| 电表 B L1 视在功率 | `sensor.saj_meter_b_l1_apparent_power` | 传感器 | VA | HS3, H2 | 电表 B | 否 |
| 电表 B L1 功率因数 | `sensor.saj_meter_b_l1_power_factor` | 传感器 | - | HS3, H2 | 电表 B | 否 |
| 电表 B L1 频率 | `sensor.saj_meter_b_l1_frequency` | 传感器 | Hz | HS3, H2 | 电表 B | 否 |
| 电表 B L2 电压 | `sensor.saj_meter_b_l2_voltage` | 传感器 | V | HS3, H2 | 电表 B; 第 2 相及以上 | 否 |
| 电表 B L2 电流 | `sensor.saj_meter_b_l2_current` | 传感器 | A | HS3, H2 | 电表 B; 第 2 相及以上 | 否 |
| 电表 B L2 功率 | `sensor.saj_meter_b_l2_power` | 传感器 | W | HS3, H2 | 电表 B; 第 2 相及以上 | 否 |
| 电表 B L2 视在功率 | `sensor.saj_meter_b_l2_apparent_power` | 传感器 | VA | HS3, H2 | 电表 B; 第 2 相及以上 | 否 |
| 电表 B L2 功率因数 | `sensor.saj_meter_b_l2_power_factor` | 传感器 | - | HS3, H2 | 电表 B; 第 2 相及以上 | 否 |
| 电表 B L2 频率 | `sensor.saj_meter_b_l2_frequency` | 传感器 | Hz | HS3, H2 | 电表 B; 第 2 相及以上 | 否 |
| 电表 B L3 电压 | `sensor.saj_meter_b_l3_voltage` | 传感器 | V | HS3, H2 | 电表 B; 第 3 相及以上 | 否 |
| 电表 B L3 电流 | `sensor.saj_meter_b_l3_current` | 传感器 | A | HS3, H2 | 电表 B; 第 3 相及以上 | 否 |
| 电表 B L3 功率 | `sensor.saj_meter_b_l3_power` | 传感器 | W | HS3, H2 | 电表 B; 第 3 相及以上 | 否 |
| 电表 B L3 视在功率 | `sensor.saj_meter_b_l3_apparent_power` | 传感器 | VA | HS3, H2 | 电表 B; 第 3 相及以上 | 否 |
| 电表 B L3 功率因数 | `sensor.saj_meter_b_l3_power_factor` | 传感器 | - | HS3, H2 | 电表 B; 第 3 相及以上 | 否 |
| 电表 B L3 频率 | `sensor.saj_meter_b_l3_frequency` | 传感器 | Hz | HS3, H2 | 电表 B; 第 3 相及以上 | 否 |
| 电表 B L1 无功功率 | `sensor.saj_meter_b_l1_reactive_power` | 传感器 | var | HS3 | 电表 B | 否 |
| 电表 B L2 无功功率 | `sensor.saj_meter_b_l2_reactive_power` | 传感器 | var | HS3 | 电表 B; 第 2 相及以上 | 否 |
| 电表 B L3 无功功率 | `sensor.saj_meter_b_l3_reactive_power` | 传感器 | var | HS3 | 电表 B; 第 3 相及以上 | 否 |
| 电表 B 功率 | `sensor.saj_meter_b_power` | 传感器 | W | HS3, H2 | 电表 B | 是 |
