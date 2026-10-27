[en](../../../en-gb/user/entities/battery-packs.md) | [de](../../../de/user/entities/battery-packs.md) | [nl](../../../nl/user/entities/battery-packs.md) | [fr](../../../fr/user/entities/battery-packs.md) | zh | [es](../../../es/user/entities/battery-packs.md) | [it](../../../it/user/entities/battery-packs.md) | [pl](../../../pl/user/entities/battery-packs.md) | [sv](../../../sv/user/entities/battery-packs.md)

# 电池包

每个电池包的读数和标识。

集成功能列表在 [可选设备](../../../../custom_components/saj_local/docs/features.md#optional-equipment) 中说明了电池包实体。

58 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个电池包实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `sensor.saj_house_battery_pack1_soc`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 电池包 1 荷电状态 | `sensor.saj_battery_pack1_soc` | 传感器 | % | HS3, H2 | 电池 | 否 |
| 电池包 1 健康状态 | `sensor.saj_battery_pack1_soh` | 传感器 | % | HS3, H2 | 电池 | 否 |
| 电池包 1 电压 | `sensor.saj_battery_pack1_voltage` | 传感器 | V | HS3, H2 | 电池 | 否 |
| 电池包 1 电流 | `sensor.saj_battery_pack1_current` | 传感器 | A | HS3, H2 | 电池 | 否 |
| 电池包 1 温度 | `sensor.saj_battery_pack1_temperature` | 传感器 | °C | HS3, H2 | 电池 | 否 |
| 电池包 1 循环次数 | `sensor.saj_battery_pack1_cycles` | 传感器 | - | HS3, H2 | 电池 | 否 |
| 电池包 1 放电电量 | `sensor.saj_battery_pack1_discharged_energy` | 传感器 | kWh | HS3, H2 | 电池 | 否 |
| 电池包 1 BMS 类型 | `sensor.saj_battery_pack1_bms_type` | 传感器 | - | H2 | 电池 | 否 |
| 电池包 1 BMS 序列号 | `sensor.saj_battery_pack1_bms_serial_number` | 传感器 | - | H2 | 电池 | 否 |
| 电池包 1 BMS 软件版本 | `sensor.saj_battery_pack1_bms_software_version` | 传感器 | - | H2 | 电池 | 否 |
| 电池包 1 BMS 硬件版本 | `sensor.saj_battery_pack1_bms_hardware_version` | 传感器 | - | H2 | 电池 | 否 |
| 电池包 1 类型 | `sensor.saj_battery_pack1_type` | 传感器 | - | H2 | 电池 | 否 |
| 电池包 1 序列号 | `sensor.saj_battery_pack1_serial_number` | 传感器 | - | H2 | 电池 | 否 |
| 电池包 2 BMS 类型 | `sensor.saj_battery_pack2_bms_type` | 传感器 | - | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 BMS 序列号 | `sensor.saj_battery_pack2_bms_serial_number` | 传感器 | - | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 BMS 软件版本 | `sensor.saj_battery_pack2_bms_software_version` | 传感器 | - | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 BMS 硬件版本 | `sensor.saj_battery_pack2_bms_hardware_version` | 传感器 | - | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 类型 | `sensor.saj_battery_pack2_type` | 传感器 | - | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 序列号 | `sensor.saj_battery_pack2_serial_number` | 传感器 | - | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 3 BMS 类型 | `sensor.saj_battery_pack3_bms_type` | 传感器 | - | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 BMS 序列号 | `sensor.saj_battery_pack3_bms_serial_number` | 传感器 | - | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 BMS 软件版本 | `sensor.saj_battery_pack3_bms_software_version` | 传感器 | - | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 BMS 硬件版本 | `sensor.saj_battery_pack3_bms_hardware_version` | 传感器 | - | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 类型 | `sensor.saj_battery_pack3_type` | 传感器 | - | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 序列号 | `sensor.saj_battery_pack3_serial_number` | 传感器 | - | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 4 BMS 类型 | `sensor.saj_battery_pack4_bms_type` | 传感器 | - | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 BMS 序列号 | `sensor.saj_battery_pack4_bms_serial_number` | 传感器 | - | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 BMS 软件版本 | `sensor.saj_battery_pack4_bms_software_version` | 传感器 | - | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 BMS 硬件版本 | `sensor.saj_battery_pack4_bms_hardware_version` | 传感器 | - | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 类型 | `sensor.saj_battery_pack4_type` | 传感器 | - | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 序列号 | `sensor.saj_battery_pack4_serial_number` | 传感器 | - | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 5 BMS 类型 | `sensor.saj_battery_pack5_bms_type` | 传感器 | - | H2 | 电池; 电池包 5 及以上 | 否 |
| 电池包 5 BMS 序列号 | `sensor.saj_battery_pack5_bms_serial_number` | 传感器 | - | H2 | 电池; 电池包 5 及以上 | 否 |
| 电池包 5 BMS 软件版本 | `sensor.saj_battery_pack5_bms_software_version` | 传感器 | - | H2 | 电池; 电池包 5 及以上 | 否 |
| 电池包 5 BMS 硬件版本 | `sensor.saj_battery_pack5_bms_hardware_version` | 传感器 | - | H2 | 电池; 电池包 5 及以上 | 否 |
| 电池包 5 类型 | `sensor.saj_battery_pack5_type` | 传感器 | - | H2 | 电池; 电池包 5 及以上 | 否 |
| 电池包 5 序列号 | `sensor.saj_battery_pack5_serial_number` | 传感器 | - | H2 | 电池; 电池包 5 及以上 | 否 |
| 电池包 2 荷电状态 | `sensor.saj_battery_pack2_soc` | 传感器 | % | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 健康状态 | `sensor.saj_battery_pack2_soh` | 传感器 | % | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 电压 | `sensor.saj_battery_pack2_voltage` | 传感器 | V | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 电流 | `sensor.saj_battery_pack2_current` | 传感器 | A | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 温度 | `sensor.saj_battery_pack2_temperature` | 传感器 | °C | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 2 循环次数 | `sensor.saj_battery_pack2_cycles` | 传感器 | - | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 3 荷电状态 | `sensor.saj_battery_pack3_soc` | 传感器 | % | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 健康状态 | `sensor.saj_battery_pack3_soh` | 传感器 | % | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 电压 | `sensor.saj_battery_pack3_voltage` | 传感器 | V | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 电流 | `sensor.saj_battery_pack3_current` | 传感器 | A | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 温度 | `sensor.saj_battery_pack3_temperature` | 传感器 | °C | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 3 循环次数 | `sensor.saj_battery_pack3_cycles` | 传感器 | - | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 4 荷电状态 | `sensor.saj_battery_pack4_soc` | 传感器 | % | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 健康状态 | `sensor.saj_battery_pack4_soh` | 传感器 | % | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 电压 | `sensor.saj_battery_pack4_voltage` | 传感器 | V | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 电流 | `sensor.saj_battery_pack4_current` | 传感器 | A | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 温度 | `sensor.saj_battery_pack4_temperature` | 传感器 | °C | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 4 循环次数 | `sensor.saj_battery_pack4_cycles` | 传感器 | - | H2 | 电池; 电池包 4 及以上 | 否 |
| 电池包 2 放电电量 | `sensor.saj_battery_pack2_discharged_energy` | 传感器 | kWh | H2 | 电池; 电池包 2 及以上 | 否 |
| 电池包 3 放电电量 | `sensor.saj_battery_pack3_discharged_energy` | 传感器 | kWh | H2 | 电池; 电池包 3 及以上 | 否 |
| 电池包 4 放电电量 | `sensor.saj_battery_pack4_discharged_energy` | 传感器 | kWh | H2 | 电池; 电池包 4 及以上 | 否 |
