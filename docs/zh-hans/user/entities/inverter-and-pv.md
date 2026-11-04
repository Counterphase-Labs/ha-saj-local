[en](../../../en-gb/user/entities/inverter-and-pv.md) | [de](../../../de/user/entities/inverter-and-pv.md) | [nl](../../../nl/user/entities/inverter-and-pv.md) | [fr](../../../fr/user/entities/inverter-and-pv.md) | zh | [es](../../../es/user/entities/inverter-and-pv.md) | [it](../../../it/user/entities/inverter-and-pv.md) | [pl](../../../pl/user/entities/inverter-and-pv.md) | [sv](../../../sv/user/entities/inverter-and-pv.md)

# 逆变器与光伏

逆变器输出、光伏组串、备用端口、电量计数器、版本和家庭负载。

集成功能列表在 [设备与实体](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) 中说明了逆变器与光伏实体。

241 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个逆变器与光伏实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `sensor.saj_house_ethernet_protocol_version`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 以太网协议版本 | `sensor.saj_ethernet_protocol_version` | 传感器 | - | HS3 | - | 否 |
| 以太网 MAC 地址 | `sensor.saj_ethernet_mac_address` | 传感器 | - | HS3 | - | 否 |
| 以太网模式 | `sensor.saj_ethernet_mode` | 传感器 | - | HS3 | - | 否 |
| 以太网 IP 地址 | `sensor.saj_ethernet_ip_address` | 传感器 | - | HS3 | - | 否 |
| 以太网子网掩码 | `sensor.saj_ethernet_subnet_mask` | 传感器 | - | HS3 | - | 否 |
| 以太网网关 | `sensor.saj_ethernet_gateway` | 传感器 | - | HS3 | - | 否 |
| 以太网首选 DNS | `sensor.saj_ethernet_dns_primary` | 传感器 | - | HS3 | - | 否 |
| 以太网备用 DNS | `sensor.saj_ethernet_dns_secondary` | 传感器 | - | HS3 | - | 否 |
| 设置序号 | `sensor.saj_settings_sequence` | 传感器 | - | HS3, H2 | - | 否 |
| 设置协议版本 | `sensor.saj_settings_protocol_version` | 传感器 | - | HS3 | - | 否 |
| 电表配置 | `sensor.saj_meter_configuration` | 传感器 | - | HS3, H2 | - | 否 |
| 电表地址 | `sensor.saj_meter_address` | 传感器 | - | HS3, H2 | - | 否 |
| RS485 地址 | `sensor.saj_rs485_address` | 传感器 | - | HS3, H2 | - | 否 |
| RS485 波特率 | `sensor.saj_rs485_baud_rate` | 传感器 | - | HS3, H2 | - | 否 |
| 电池协议 | `sensor.saj_battery_protocol` | 传感器 | - | HS3, H2 | - | 否 |
| RS485 从站地址 | `sensor.saj_rs485_slave_address` | 传感器 | - | HS3 | - | 否 |
| RS485 从站波特率 | `sensor.saj_rs485_slave_baud_rate` | 传感器 | - | HS3 | - | 否 |
| 逆变器时钟 | `sensor.saj_inverter_clock` | 传感器 | - | HS3, H2 | - | 否 |
| 运行模式 | `sensor.saj_operating_mode` | 传感器 | - | HS3, H2 | - | 是 |
| 逆变器温度 | `sensor.saj_inverter_temperature` | 传感器 | °C | HS3, H2 | - | 是 |
| 环境温度 | `sensor.saj_ambient_temperature` | 传感器 | °C | HS3, H2 | - | 否 |
| 漏电流 | `sensor.saj_leakage_current` | 传感器 | mA | HS3, H2 | - | 否 |
| PV1 绝缘电阻 | `sensor.saj_pv1_insulation_resistance` | 传感器 | kΩ | HS3, H2 | - | 否 |
| PV2 绝缘电阻 | `sensor.saj_pv2_insulation_resistance` | 传感器 | kΩ | HS3, H2 | 光伏组串 2 及以上 | 否 |
| 逆变器放电功率设定值 | `sensor.saj_inverter_discharge_power_setpoint` | 传感器 | W | HS3, H2 | - | 否 |
| 逆变器充电功率设定值 | `sensor.saj_inverter_charge_power_setpoint` | 传感器 | W | HS3, H2 | - | 否 |
| 电池协议（生效中） | `sensor.saj_battery_protocol_active` | 传感器 | - | HS3, H2 | - | 否 |
| 电表配置（生效中） | `sensor.saj_meter_configuration_active` | 传感器 | - | HS3, H2 | - | 否 |
| 逆变器 L1 电压 | `sensor.saj_inverter_l1_voltage` | 传感器 | V | HS3, H2 | - | 否 |
| 逆变器 L1 电流 | `sensor.saj_inverter_l1_current` | 传感器 | A | HS3, H2 | - | 否 |
| 逆变器 L1 频率 | `sensor.saj_inverter_l1_frequency` | 传感器 | Hz | HS3, H2 | - | 否 |
| 逆变器 L1 功率 | `sensor.saj_inverter_l1_power` | 传感器 | W | HS3, H2 | - | 否 |
| 逆变器 L1 视在功率 | `sensor.saj_inverter_l1_apparent_power` | 传感器 | VA | HS3, H2 | - | 否 |
| 逆变器 L2 电压 | `sensor.saj_inverter_l2_voltage` | 传感器 | V | HS3, H2 | 第 2 相及以上 | 否 |
| 逆变器 L2 电流 | `sensor.saj_inverter_l2_current` | 传感器 | A | HS3, H2 | 第 2 相及以上 | 否 |
| 逆变器 L2 频率 | `sensor.saj_inverter_l2_frequency` | 传感器 | Hz | HS3, H2 | 第 2 相及以上 | 否 |
| 逆变器 L2 功率 | `sensor.saj_inverter_l2_power` | 传感器 | W | HS3, H2 | 第 2 相及以上 | 否 |
| 逆变器 L2 视在功率 | `sensor.saj_inverter_l2_apparent_power` | 传感器 | VA | HS3, H2 | 第 2 相及以上 | 否 |
| 逆变器 L3 电压 | `sensor.saj_inverter_l3_voltage` | 传感器 | V | HS3, H2 | 第 3 相及以上 | 否 |
| 逆变器 L3 电流 | `sensor.saj_inverter_l3_current` | 传感器 | A | HS3, H2 | 第 3 相及以上 | 否 |
| 逆变器 L3 频率 | `sensor.saj_inverter_l3_frequency` | 传感器 | Hz | HS3, H2 | 第 3 相及以上 | 否 |
| 逆变器 L3 功率 | `sensor.saj_inverter_l3_power` | 传感器 | W | HS3, H2 | 第 3 相及以上 | 否 |
| 逆变器 L3 视在功率 | `sensor.saj_inverter_l3_apparent_power` | 传感器 | VA | HS3, H2 | 第 3 相及以上 | 否 |
| 备用 L1 电压 | `sensor.saj_backup_l1_voltage` | 传感器 | V | HS3, H2 | - | 否 |
| 备用 L1 电流 | `sensor.saj_backup_l1_current` | 传感器 | A | HS3, H2 | - | 否 |
| 备用 L1 频率 | `sensor.saj_backup_l1_frequency` | 传感器 | Hz | HS3, H2 | - | 否 |
| 备用 L1 直流电压 | `sensor.saj_backup_l1_dc_voltage` | 传感器 | mV | HS3, H2 | - | 否 |
| 备用 L1 功率 | `sensor.saj_backup_l1_power` | 传感器 | W | HS3, H2 | - | 否 |
| 备用 L1 视在功率 | `sensor.saj_backup_l1_apparent_power` | 传感器 | VA | HS3, H2 | - | 否 |
| 备用 L2 电压 | `sensor.saj_backup_l2_voltage` | 传感器 | V | HS3, H2 | 第 2 相及以上 | 否 |
| 备用 L2 电流 | `sensor.saj_backup_l2_current` | 传感器 | A | HS3, H2 | 第 2 相及以上 | 否 |
| 备用 L2 频率 | `sensor.saj_backup_l2_frequency` | 传感器 | Hz | HS3, H2 | 第 2 相及以上 | 否 |
| 备用 L2 直流电压 | `sensor.saj_backup_l2_dc_voltage` | 传感器 | mV | HS3, H2 | 第 2 相及以上 | 否 |
| 备用 L2 功率 | `sensor.saj_backup_l2_power` | 传感器 | W | HS3, H2 | 第 2 相及以上 | 否 |
| 备用 L2 视在功率 | `sensor.saj_backup_l2_apparent_power` | 传感器 | VA | HS3, H2 | 第 2 相及以上 | 否 |
| 备用 L3 电压 | `sensor.saj_backup_l3_voltage` | 传感器 | V | HS3, H2 | 第 3 相及以上 | 否 |
| 备用 L3 电流 | `sensor.saj_backup_l3_current` | 传感器 | A | HS3, H2 | 第 3 相及以上 | 否 |
| 备用 L3 频率 | `sensor.saj_backup_l3_frequency` | 传感器 | Hz | HS3, H2 | 第 3 相及以上 | 否 |
| 备用 L3 直流电压 | `sensor.saj_backup_l3_dc_voltage` | 传感器 | mV | HS3, H2 | 第 3 相及以上 | 否 |
| 备用 L3 功率 | `sensor.saj_backup_l3_power` | 传感器 | W | HS3, H2 | 第 3 相及以上 | 否 |
| 备用 L3 视在功率 | `sensor.saj_backup_l3_apparent_power` | 传感器 | VA | HS3, H2 | 第 3 相及以上 | 否 |
| 直流母线电压 | `sensor.saj_dc_bus_voltage` | 传感器 | V | HS3, H2 | - | 否 |
| 直流母线从机电压 | `sensor.saj_dc_bus_slave_voltage` | 传感器 | V | HS3, H2 | - | 否 |
| PV1 电压 | `sensor.saj_pv1_voltage` | 传感器 | V | HS3, H2 | - | 是 |
| PV1 电流 | `sensor.saj_pv1_current` | 传感器 | A | HS3, H2 | - | 是 |
| PV1 功率 | `sensor.saj_pv1_power` | 传感器 | W | HS3, H2 | - | 是 |
| PV2 电压 | `sensor.saj_pv2_voltage` | 传感器 | V | HS3, H2 | 光伏组串 2 及以上 | 是 |
| PV2 电流 | `sensor.saj_pv2_current` | 传感器 | A | HS3, H2 | 光伏组串 2 及以上 | 是 |
| PV2 功率 | `sensor.saj_pv2_power` | 传感器 | W | HS3, H2 | 光伏组串 2 及以上 | 是 |
| 光伏功率 | `sensor.saj_pv_power` | 传感器 | W | HS3, H2 | - | 是 |
| 逆变器功率 | `sensor.saj_inverter_power` | 传感器 | W | HS3, H2 | - | 是 |
| 光伏今日电量 | `sensor.saj_pv_energy_today` | 传感器 | kWh | HS3, H2 | - | 是 |
| 光伏本月电量 | `sensor.saj_pv_energy_month` | 传感器 | kWh | HS3, H2 | - | 否 |
| 光伏本年电量 | `sensor.saj_pv_energy_year` | 传感器 | kWh | HS3, H2 | - | 否 |
| 光伏累计电量 | `sensor.saj_pv_energy_total` | 传感器 | kWh | HS3, H2 | - | 是 |
| 家庭负载今日电量 | `sensor.saj_load_energy_today` | 传感器 | kWh | HS3, H2 | - | 是 |
| 家庭负载本月电量 | `sensor.saj_load_energy_month` | 传感器 | kWh | HS3, H2 | - | 否 |
| 家庭负载本年电量 | `sensor.saj_load_energy_year` | 传感器 | kWh | HS3, H2 | - | 否 |
| 家庭负载累计电量 | `sensor.saj_load_energy_total` | 传感器 | kWh | HS3, H2 | - | 是 |
| 备用负载今日电量 | `sensor.saj_backup_load_energy_today` | 传感器 | kWh | HS3, H2 | - | 是 |
| 备用负载本月电量 | `sensor.saj_backup_load_energy_month` | 传感器 | kWh | HS3, H2 | - | 否 |
| 备用负载本年电量 | `sensor.saj_backup_load_energy_year` | 传感器 | kWh | HS3, H2 | - | 否 |
| 备用负载累计电量 | `sensor.saj_backup_load_energy_total` | 传感器 | kWh | HS3, H2 | - | 是 |
| 并机模式 | `sensor.saj_parallel_mode` | 传感器 | - | HS3, H2 | - | 否 |
| 在线并机机器数 | `sensor.saj_parallel_online_count` | 传感器 | - | HS3, H2 | - | 否 |
| 电网功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_power` | 传感器 | W | HS3 | - | 否 |
| 电网 L1 功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l1_power` | 传感器 | W | HS3 | - | 否 |
| 电网 L1 电压（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l1_voltage` | 传感器 | V | HS3 | - | 否 |
| 电网 L1 电流（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l1_current` | 传感器 | A | HS3 | - | 否 |
| 电网 L1 频率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l1_frequency` | 传感器 | Hz | HS3 | - | 否 |
| 电网 L2 功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l2_power` | 传感器 | W | HS3 | 第 2 相及以上 | 否 |
| 电网 L2 电压（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l2_voltage` | 传感器 | V | HS3 | 第 2 相及以上 | 否 |
| 电网 L2 电流（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l2_current` | 传感器 | A | HS3 | 第 2 相及以上 | 否 |
| 电网 L2 频率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l2_frequency` | 传感器 | Hz | HS3 | 第 2 相及以上 | 否 |
| 电网 L3 功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l3_power` | 传感器 | W | HS3 | 第 3 相及以上 | 否 |
| 电网 L3 电压（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l3_voltage` | 传感器 | V | HS3 | 第 3 相及以上 | 否 |
| 电网 L3 电流（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l3_current` | 传感器 | A | HS3 | 第 3 相及以上 | 否 |
| 电网 L3 频率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_l3_frequency` | 传感器 | Hz | HS3 | 第 3 相及以上 | 否 |
| 逆变器功率（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_power` | 传感器 | W | HS3 | - | 否 |
| 逆变器 L1 功率（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l1_power` | 传感器 | W | HS3 | - | 否 |
| 逆变器 L1 电压（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l1_voltage` | 传感器 | V | HS3 | - | 否 |
| 逆变器 L1 电流（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l1_current` | 传感器 | A | HS3 | - | 否 |
| 逆变器 L1 频率（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l1_frequency` | 传感器 | Hz | HS3 | - | 否 |
| 逆变器 L2 功率（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l2_power` | 传感器 | W | HS3 | 第 2 相及以上 | 否 |
| 逆变器 L2 电压（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l2_voltage` | 传感器 | V | HS3 | 第 2 相及以上 | 否 |
| 逆变器 L2 电流（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l2_current` | 传感器 | A | HS3 | 第 2 相及以上 | 否 |
| 逆变器 L2 频率（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l2_frequency` | 传感器 | Hz | HS3 | 第 2 相及以上 | 否 |
| 逆变器 L3 功率（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l3_power` | 传感器 | W | HS3 | 第 3 相及以上 | 否 |
| 逆变器 L3 电压（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l3_voltage` | 传感器 | V | HS3 | 第 3 相及以上 | 否 |
| 逆变器 L3 电流（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l3_current` | 传感器 | A | HS3 | 第 3 相及以上 | 否 |
| 逆变器 L3 频率（5 分钟平均值） | `sensor.saj_five_minute_average_inverter_l3_frequency` | 传感器 | Hz | HS3 | 第 3 相及以上 | 否 |
| 家庭负载功率（5 分钟平均值） | `sensor.saj_five_minute_average_load_power` | 传感器 | W | HS3 | - | 否 |
| 家庭负载 L1 功率（5 分钟平均值） | `sensor.saj_five_minute_average_load_l1_power` | 传感器 | W | HS3 | - | 否 |
| 家庭负载 L1 电压（5 分钟平均值） | `sensor.saj_five_minute_average_load_l1_voltage` | 传感器 | V | HS3 | - | 否 |
| 家庭负载 L1 电流（5 分钟平均值） | `sensor.saj_five_minute_average_load_l1_current` | 传感器 | A | HS3 | - | 否 |
| 家庭负载 L1 频率（5 分钟平均值） | `sensor.saj_five_minute_average_load_l1_frequency` | 传感器 | Hz | HS3 | - | 否 |
| 家庭负载 L2 功率（5 分钟平均值） | `sensor.saj_five_minute_average_load_l2_power` | 传感器 | W | HS3 | 第 2 相及以上 | 否 |
| 家庭负载 L2 电压（5 分钟平均值） | `sensor.saj_five_minute_average_load_l2_voltage` | 传感器 | V | HS3 | 第 2 相及以上 | 否 |
| 家庭负载 L2 电流（5 分钟平均值） | `sensor.saj_five_minute_average_load_l2_current` | 传感器 | A | HS3 | 第 2 相及以上 | 否 |
| 家庭负载 L2 频率（5 分钟平均值） | `sensor.saj_five_minute_average_load_l2_frequency` | 传感器 | Hz | HS3 | 第 2 相及以上 | 否 |
| 家庭负载 L3 功率（5 分钟平均值） | `sensor.saj_five_minute_average_load_l3_power` | 传感器 | W | HS3 | 第 3 相及以上 | 否 |
| 家庭负载 L3 电压（5 分钟平均值） | `sensor.saj_five_minute_average_load_l3_voltage` | 传感器 | V | HS3 | 第 3 相及以上 | 否 |
| 家庭负载 L3 电流（5 分钟平均值） | `sensor.saj_five_minute_average_load_l3_current` | 传感器 | A | HS3 | 第 3 相及以上 | 否 |
| 家庭负载 L3 频率（5 分钟平均值） | `sensor.saj_five_minute_average_load_l3_frequency` | 传感器 | Hz | HS3 | 第 3 相及以上 | 否 |
| 电网负载功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_power` | 传感器 | W | HS3 | - | 否 |
| 电网负载 L1 功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l1_power` | 传感器 | W | HS3 | - | 否 |
| 电网负载 L1 电压（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l1_voltage` | 传感器 | V | HS3 | - | 否 |
| 电网负载 L1 电流（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l1_current` | 传感器 | A | HS3 | - | 否 |
| 电网负载 L1 频率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l1_frequency` | 传感器 | Hz | HS3 | - | 否 |
| 电网负载 L2 功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l2_power` | 传感器 | W | HS3 | 第 2 相及以上 | 否 |
| 电网负载 L2 电压（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l2_voltage` | 传感器 | V | HS3 | 第 2 相及以上 | 否 |
| 电网负载 L2 电流（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l2_current` | 传感器 | A | HS3 | 第 2 相及以上 | 否 |
| 电网负载 L2 频率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l2_frequency` | 传感器 | Hz | HS3 | 第 2 相及以上 | 否 |
| 电网负载 L3 功率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l3_power` | 传感器 | W | HS3 | 第 3 相及以上 | 否 |
| 电网负载 L3 电压（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l3_voltage` | 传感器 | V | HS3 | 第 3 相及以上 | 否 |
| 电网负载 L3 电流（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l3_current` | 传感器 | A | HS3 | 第 3 相及以上 | 否 |
| 电网负载 L3 频率（5 分钟平均值） | `sensor.saj_five_minute_average_grid_load_l3_frequency` | 传感器 | Hz | HS3 | 第 3 相及以上 | 否 |
| 备用功率（5 分钟平均值） | `sensor.saj_five_minute_average_backup_power` | 传感器 | W | HS3 | - | 否 |
| 备用 L1 功率（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l1_power` | 传感器 | W | HS3 | - | 否 |
| 备用 L1 电压（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l1_voltage` | 传感器 | V | HS3 | - | 否 |
| 备用 L1 电流（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l1_current` | 传感器 | A | HS3 | - | 否 |
| 备用 L1 频率（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l1_frequency` | 传感器 | Hz | HS3 | - | 否 |
| 备用 L2 功率（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l2_power` | 传感器 | W | HS3 | 第 2 相及以上 | 否 |
| 备用 L2 电压（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l2_voltage` | 传感器 | V | HS3 | 第 2 相及以上 | 否 |
| 备用 L2 电流（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l2_current` | 传感器 | A | HS3 | 第 2 相及以上 | 否 |
| 备用 L2 频率（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l2_frequency` | 传感器 | Hz | HS3 | 第 2 相及以上 | 否 |
| 备用 L3 功率（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l3_power` | 传感器 | W | HS3 | 第 3 相及以上 | 否 |
| 备用 L3 电压（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l3_voltage` | 传感器 | V | HS3 | 第 3 相及以上 | 否 |
| 备用 L3 电流（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l3_current` | 传感器 | A | HS3 | 第 3 相及以上 | 否 |
| 备用 L3 频率（5 分钟平均值） | `sensor.saj_five_minute_average_backup_l3_frequency` | 传感器 | Hz | HS3 | 第 3 相及以上 | 否 |
| 光伏功率（5 分钟平均值） | `sensor.saj_five_minute_average_pv_power` | 传感器 | W | HS3 | - | 否 |
| PV1 电压（5 分钟平均值） | `sensor.saj_five_minute_average_pv1_voltage` | 传感器 | V | HS3 | - | 否 |
| PV1 电流（5 分钟平均值） | `sensor.saj_five_minute_average_pv1_current` | 传感器 | A | HS3 | - | 否 |
| PV1 功率（5 分钟平均值） | `sensor.saj_five_minute_average_pv1_power` | 传感器 | W | HS3 | - | 否 |
| PV2 电压（5 分钟平均值） | `sensor.saj_five_minute_average_pv2_voltage` | 传感器 | V | HS3 | 光伏组串 2 及以上 | 否 |
| PV2 电流（5 分钟平均值） | `sensor.saj_five_minute_average_pv2_current` | 传感器 | A | HS3 | 光伏组串 2 及以上 | 否 |
| PV2 功率（5 分钟平均值） | `sensor.saj_five_minute_average_pv2_power` | 传感器 | W | HS3 | 光伏组串 2 及以上 | 否 |
| 发电机功率（5 分钟平均值） | `sensor.saj_five_minute_average_generator_power` | 传感器 | W | HS3 | - | 否 |
| 发电机 L1 功率（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l1_power` | 传感器 | W | HS3 | - | 否 |
| 发电机 L1 电压（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l1_voltage` | 传感器 | V | HS3 | - | 否 |
| 发电机 L1 电流（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l1_current` | 传感器 | A | HS3 | - | 否 |
| 发电机 L1 频率（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l1_frequency` | 传感器 | Hz | HS3 | - | 否 |
| 发电机 L2 功率（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l2_power` | 传感器 | W | HS3 | 第 2 相及以上 | 否 |
| 发电机 L2 电压（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l2_voltage` | 传感器 | V | HS3 | 第 2 相及以上 | 否 |
| 发电机 L2 电流（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l2_current` | 传感器 | A | HS3 | 第 2 相及以上 | 否 |
| 发电机 L2 频率（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l2_frequency` | 传感器 | Hz | HS3 | 第 2 相及以上 | 否 |
| 发电机 L3 功率（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l3_power` | 传感器 | W | HS3 | 第 3 相及以上 | 否 |
| 发电机 L3 电压（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l3_voltage` | 传感器 | V | HS3 | 第 3 相及以上 | 否 |
| 发电机 L3 电流（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l3_current` | 传感器 | A | HS3 | 第 3 相及以上 | 否 |
| 发电机 L3 频率（5 分钟平均值） | `sensor.saj_five_minute_average_generator_l3_frequency` | 传感器 | Hz | HS3 | 第 3 相及以上 | 否 |
| 产品代码 | `sensor.saj_product_code` | 传感器 | - | HS3, H2 | - | 否 |
| 显示板软件版本 | `sensor.saj_display_software_version` | 传感器 | - | HS3, H2 | - | 否 |
| 主控软件版本 | `sensor.saj_master_software_version` | 传感器 | - | HS3, H2 | - | 否 |
| 从控软件版本 | `sensor.saj_slave_software_version` | 传感器 | - | HS3, H2 | - | 否 |
| 显示板硬件版本 | `sensor.saj_display_hardware_version` | 传感器 | - | HS3, H2 | - | 否 |
| 控制板硬件版本 | `sensor.saj_control_hardware_version` | 传感器 | - | HS3, H2 | - | 否 |
| 功率板硬件版本 | `sensor.saj_power_hardware_version` | 传感器 | - | HS3, H2 | - | 否 |
| 电池包数量 | `sensor.saj_battery_pack_count` | 传感器 | - | HS3, H2 | - | 否 |
| 电表 A 状态 | `sensor.saj_meter_a_status` | 传感器 | - | HS3, H2 | - | 否 |
| 电表 B 状态 | `sensor.saj_meter_b_status` | 传感器 | - | HS3, H2 | - | 否 |
| 备用负载功率 | `sensor.saj_backup_load_power` | 传感器 | W | HS3, H2 | - | 是 |
| 家庭负载功率 | `sensor.saj_load_power` | 传感器 | W | HS3, H2 | - | 是 |
| 逆流模式 | `sensor.saj_reverse_flow_mode` | 传感器 | - | H2 | - | 否 |
| FCAS 频率回差 | `sensor.saj_fcas_frequency_hysteresis` | 传感器 | Hz | H2 | - | 否 |
| 并机角色 | `sensor.saj_parallel_role` | 传感器 | - | H2 | - | 否 |
| 并机编号 | `sensor.saj_parallel_number` | 传感器 | - | H2 | - | 否 |
| 并机配置模式 | `sensor.saj_parallel_configured_mode` | 传感器 | - | H2 | - | 否 |
| 电池输入模式 | `sensor.saj_battery_input_mode` | 传感器 | - | H2 | - | 否 |
| PV 输入模式 | `sensor.saj_pv_input_mode` | 传感器 | - | H2 | - | 否 |
| 离网模式 | `sensor.saj_off_grid_mode` | 传感器 | - | H2 | - | 否 |
| 离网输出电压 | `sensor.saj_off_grid_output_voltage` | 传感器 | V | H2 | - | 否 |
| 离网输出频率 | `sensor.saj_off_grid_output_frequency` | 传感器 | Hz | H2 | - | 否 |
| 电机使能 | `sensor.saj_motor_enable` | 传感器 | - | H2 | - | 否 |
| 机器型号 | `sensor.saj_machine_model` | 传感器 | - | H2 | - | 否 |
| 额定功率 | `sensor.saj_rated_power` | 传感器 | W | H2 | - | 否 |
| 功能标志 1 | `sensor.saj_function_flags_1` | 传感器 | - | H2 | - | 否 |
| 功能标志 2 | `sensor.saj_function_flags_2` | 传感器 | - | H2 | - | 否 |
| 最大直流电流分量 | `sensor.saj_max_dc_current_component` | 传感器 | mA | H2 | - | 否 |
| 最大直流电压分量 | `sensor.saj_max_dc_voltage_component` | 传感器 | V | H2 | - | 否 |
| 绝缘电阻限值 | `sensor.saj_insulation_resistance_limit` | 传感器 | kΩ | H2 | - | 否 |
| 最大漏电流 | `sensor.saj_max_leakage_current` | 传感器 | mA | H2 | - | 否 |
| 逆变器停机 | `sensor.saj_inverter_stop` | 传感器 | - | H2 | - | 否 |
| PV 启动电压 | `sensor.saj_pv_start_voltage` | 传感器 | V | H2 | - | 否 |
| PV 关机电压 | `sensor.saj_pv_shutdown_voltage` | 传感器 | V | H2 | - | 否 |
| MPPT 电压上限 | `sensor.saj_mppt_voltage_high` | 传感器 | V | H2 | - | 否 |
| MPPT 电压下限 | `sensor.saj_mppt_voltage_low` | 传感器 | V | H2 | - | 否 |
| MPPT 扫描时间 | `sensor.saj_mppt_scan_time` | 传感器 | min | H2 | - | 否 |
| 逆变器错误计数 | `sensor.saj_inverter_error_count` | 传感器 | - | H2 | - | 否 |
| PV3 绝缘电阻 | `sensor.saj_pv3_insulation_resistance` | 传感器 | kΩ | H2 | 光伏组串 3 及以上 | 否 |
| PV4 绝缘电阻 | `sensor.saj_pv4_insulation_resistance` | 传感器 | kΩ | H2 | 光伏组串 4 及以上 | 否 |
| DRM 硬件状态 | `sensor.saj_drm_hardware_status` | 传感器 | - | H2 | - | 否 |
| DRM 软件状态 | `sensor.saj_drm_software_status` | 传感器 | - | H2 | - | 否 |
| 故障记录序号 | `sensor.saj_fault_record_sequence` | 传感器 | - | H2 | - | 否 |
| 应用模式（生效中） | `sensor.saj_application_mode_active` | 传感器 | - | H2 | - | 否 |
| PV3 电压 | `sensor.saj_pv3_voltage` | 传感器 | V | H2 | 光伏组串 3 及以上 | 是 |
| PV3 电流 | `sensor.saj_pv3_current` | 传感器 | A | H2 | 光伏组串 3 及以上 | 是 |
| PV3 功率 | `sensor.saj_pv3_power` | 传感器 | W | H2 | 光伏组串 3 及以上 | 是 |
| PV4 电压 | `sensor.saj_pv4_voltage` | 传感器 | V | H2 | 光伏组串 4 及以上 | 是 |
| PV4 电流 | `sensor.saj_pv4_current` | 传感器 | A | H2 | 光伏组串 4 及以上 | 是 |
| PV4 功率 | `sensor.saj_pv4_power` | 传感器 | W | H2 | 光伏组串 4 及以上 | 是 |
| CT 电网功率 | `sensor.saj_ct_grid_power` | 传感器 | W | H2 | - | 否 |
| CT 电网视在功率 | `sensor.saj_ct_grid_apparent_power` | 传感器 | VA | H2 | - | 否 |
| CT 光伏功率 | `sensor.saj_ct_pv_power` | 传感器 | W | H2 | - | 否 |
| CT 光伏视在功率 | `sensor.saj_ct_pv_apparent_power` | 传感器 | VA | H2 | - | 否 |
| 逆变器视在功率 | `sensor.saj_inverter_apparent_power` | 传感器 | VA | H2 | - | 否 |
| 备用负载视在功率 | `sensor.saj_backup_load_apparent_power` | 传感器 | VA | H2 | - | 否 |
| 光伏今日发电时长 | `sensor.saj_pv_generation_time_today` | 传感器 | h | H2 | - | 否 |
| 光伏累计发电时长 | `sensor.saj_pv_generation_time_total` | 传感器 | h | H2 | - | 否 |
| 逆变器今日电量 | `sensor.saj_inverter_energy_today` | 传感器 | kWh | H2 | - | 否 |
| 逆变器本月电量 | `sensor.saj_inverter_energy_month` | 传感器 | kWh | H2 | - | 否 |
| 逆变器本年电量 | `sensor.saj_inverter_energy_year` | 传感器 | kWh | H2 | - | 否 |
| 逆变器累计电量 | `sensor.saj_inverter_energy_total` | 传感器 | kWh | H2 | - | 否 |
| PV2 今日电量 | `sensor.saj_pv2_energy_today` | 传感器 | kWh | H2 | 光伏组串 2 及以上 | 否 |
| PV2 本月电量 | `sensor.saj_pv2_energy_month` | 传感器 | kWh | H2 | 光伏组串 2 及以上 | 否 |
| PV2 本年电量 | `sensor.saj_pv2_energy_year` | 传感器 | kWh | H2 | 光伏组串 2 及以上 | 否 |
| PV2 累计电量 | `sensor.saj_pv2_energy_total` | 传感器 | kWh | H2 | 光伏组串 2 及以上 | 否 |
| PV3 今日电量 | `sensor.saj_pv3_energy_today` | 传感器 | kWh | H2 | 光伏组串 3 及以上 | 否 |
| PV3 本月电量 | `sensor.saj_pv3_energy_month` | 传感器 | kWh | H2 | 光伏组串 3 及以上 | 否 |
| PV3 本年电量 | `sensor.saj_pv3_energy_year` | 传感器 | kWh | H2 | 光伏组串 3 及以上 | 否 |
| PV3 累计电量 | `sensor.saj_pv3_energy_total` | 传感器 | kWh | H2 | 光伏组串 3 及以上 | 否 |
| 标识协议版本 | `sensor.saj_identity_protocol_version` | 传感器 | - | H2 | - | 否 |
