[en](../../../en-gb/user/entities/faults.md) | [de](../../../de/user/entities/faults.md) | [nl](../../../nl/user/entities/faults.md) | [fr](../../../fr/user/entities/faults.md) | zh | [es](../../../es/user/entities/faults.md) | [it](../../../it/user/entities/faults.md) | [pl](../../../pl/user/entities/faults.md) | [sv](../../../sv/user/entities/faults.md)

# 故障

逆变器、电池和充电桩上报的故障。

集成功能列表在 [设备故障和修复问题](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) 中说明了故障实体。

139 个实体。由 `make docs` 生成，请勿手动编辑。

在“配置”中设置的前缀会加在每个故障实体 ID 中 `saj_` 之后，例如前缀为 `house` 时为 `binary_sensor.saj_house_battery_pack1_fault`。

| 名称 | 实体 ID | 类型 | 单位 | 型号 | 设备和数量 | 默认启用 |
| --- | --- | --- | --- | --- | --- | --- |
| 电池包 1 故障 | `binary_sensor.saj_battery_pack1_fault` | 二元传感器 | - | HS3, H2 | 电池 | 是 |
| 电池包 1 警告 | `binary_sensor.saj_battery_pack1_warning` | 二元传感器 | - | HS3, H2 | 电池 | 是 |
| 电池故障 | `binary_sensor.saj_battery_fault` | 二元传感器 | - | HS3, H2 | 电池 | 是 |
| 电池 BMS 厂商不兼容 | `binary_sensor.saj_battery_fault_bms_incompatible` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池断路器断开 | `binary_sensor.saj_battery_fault_breaker_open` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体不匹配 | `binary_sensor.saj_battery_fault_cell_incompatible` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体过温 | `binary_sensor.saj_battery_fault_cell_over_temperature` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体过压 | `binary_sensor.saj_battery_fault_cell_overvoltage` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体厂商不匹配 | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体温差过大 | `binary_sensor.saj_battery_fault_cell_temperature_difference` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体欠压 | `binary_sensor.saj_battery_fault_cell_undervoltage` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体压差过大，1 级 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池单体压差过大，2 级 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池温度过低，无法充电 | `binary_sensor.saj_battery_fault_charge_cold` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池温度过高，无法充电 | `binary_sensor.saj_battery_fault_charge_hot` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池充电过流 | `binary_sensor.saj_battery_fault_charge_overcurrent` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池充电端口过压 | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池温度过低，无法放电 | `binary_sensor.saj_battery_fault_discharge_cold` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池温度过高，无法放电 | `binary_sensor.saj_battery_fault_discharge_hot` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池放电过流 | `binary_sensor.saj_battery_fault_discharge_overcurrent` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池熔断器故障 | `binary_sensor.saj_battery_fault_fuse` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池 BMS 硬件故障 | `binary_sensor.saj_battery_fault_hardware` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池 BMS 绝缘故障 | `binary_sensor.saj_battery_fault_insulation` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池 BMS 内部通信丢失 | `binary_sensor.saj_battery_fault_internal_communication` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池包寻址故障 | `binary_sensor.saj_battery_fault_pack_sequence` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池预充故障 | `binary_sensor.saj_battery_fault_precharge` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池 BMS 继电器故障 | `binary_sensor.saj_battery_fault_relay` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池短路 | `binary_sensor.saj_battery_fault_short_circuit` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池系统已锁定 | `binary_sensor.saj_battery_fault_system_locked` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池总电压过高 | `binary_sensor.saj_battery_fault_total_overvoltage` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池总电压过低 | `binary_sensor.saj_battery_fault_total_undervoltage` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池总电压匹配失败 | `binary_sensor.saj_battery_fault_total_voltage_matching` | 二元传感器 | - | HS3 | 电池 | 是 |
| 电池未识别的故障 | `binary_sensor.saj_battery_fault_unrecognised` | 二元传感器 | - | HS3, H2 | 电池 | 是 |
| 电池电压等级不匹配 | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | 二元传感器 | - | HS3 | 电池 | 是 |
| 充电桩故障 | `binary_sensor.saj_ev_fault` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩交流过流 | `binary_sensor.saj_ev_fault_ac_overcurrent` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩交流过频 | `binary_sensor.saj_ev_fault_ac_overfrequency` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩交流过压 | `binary_sensor.saj_ev_fault_ac_overvoltage` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩交流剩余电流 | `binary_sensor.saj_ev_fault_ac_residual_current` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩交流欠频 | `binary_sensor.saj_ev_fault_ac_underfrequency` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩交流欠压 | `binary_sensor.saj_ev_fault_ac_undervoltage` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩蓝牙故障 | `binary_sensor.saj_ev_fault_bluetooth` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩连接器电流故障 | `binary_sensor.saj_ev_fault_connector_current` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩连接器锁故障 | `binary_sensor.saj_ev_fault_connector_lock` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩控制导引故障（低于 2 V） | `binary_sensor.saj_ev_fault_control_pilot` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩直流剩余电流故障 A | `binary_sensor.saj_ev_fault_dc_residual_current_a` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩直流剩余电流故障 B | `binary_sensor.saj_ev_fault_dc_residual_current_b` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩直流剩余电流故障 C | `binary_sensor.saj_ev_fault_dc_residual_current_c` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩急停 | `binary_sensor.saj_ev_fault_emergency_stop` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩接地故障 | `binary_sensor.saj_ev_fault_grounding` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩输入端子过温 | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩电表故障 | `binary_sensor.saj_ev_fault_meter` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩过载 | `binary_sensor.saj_ev_fault_overload` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩相序故障 | `binary_sensor.saj_ev_fault_phase_sequence` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩 RCD 回路故障 | `binary_sensor.saj_ev_fault_rcd_circuit` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩继电器故障 | `binary_sensor.saj_ev_fault_relay` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩继电器过温 | `binary_sensor.saj_ev_fault_relay_over_temperature` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩 RS485 通信超时 | `binary_sensor.saj_ev_fault_rs485_timeout` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩供电故障 | `binary_sensor.saj_ev_fault_supply` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩低温 | `binary_sensor.saj_ev_fault_under_temperature` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 充电桩未识别的故障 | `binary_sensor.saj_ev_fault_unrecognised` | 二元传感器 | - | HS3 | 充电桩 | 是 |
| 逆变器故障 | `binary_sensor.saj_inverter_fault` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电弧检测板通信丢失 | `binary_sensor.saj_inverter_fault_afci_communication` | 二元传感器 | - | HS3 | - | 是 |
| 电弧故障 | `binary_sensor.saj_inverter_fault_arc` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电弧检测设备故障 | `binary_sensor.saj_inverter_fault_arc_device` | 二元传感器 | - | HS3 | - | 是 |
| 授权已过期 | `binary_sensor.saj_inverter_fault_authorisation_expired` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池充电电压过高 | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池放电电压过低 | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池开路 | `binary_sensor.saj_inverter_fault_battery_open_circuit` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池端口过流 | `binary_sensor.saj_inverter_fault_battery_overcurrent` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池端口过载 | `binary_sensor.saj_inverter_fault_battery_overload` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池端口过压 | `binary_sensor.saj_inverter_fault_battery_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池软启动超时 | `binary_sensor.saj_inverter_fault_battery_soft_start` | 二元传感器 | - | HS3, H2 | - | 是 |
| BMS 通信丢失 | `binary_sensor.saj_inverter_fault_bms_communication` | 二元传感器 | - | HS3, H2 | - | 是 |
| BMS 设备故障 | `binary_sensor.saj_inverter_fault_bms_device` | 二元传感器 | - | HS3, H2 | - | 是 |
| 直流母线硬件过压 | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 直流母线电压不平衡 | `binary_sensor.saj_inverter_fault_bus_imbalance` | 二元传感器 | - | HS3, H2 | - | 是 |
| 控制器存储器故障 | `binary_sensor.saj_inverter_fault_controller_memory` | 二元传感器 | - | HS3, H2 | - | 是 |
| CT 设备故障 | `binary_sensor.saj_inverter_fault_ct_device` | 二元传感器 | - | HS3 | - | 是 |
| 电流传感器故障 | `binary_sensor.saj_inverter_fault_current_sensor` | 二元传感器 | - | HS3, H2 | - | 是 |
| 直流注入传感器故障 | `binary_sensor.saj_inverter_fault_dc_injection_device` | 二元传感器 | - | HS3, H2 | - | 是 |
| DC-DC 单元通信丢失 | `binary_sensor.saj_inverter_fault_dcdc_communication` | 二元传感器 | - | HS3 | - | 是 |
| DC-DC 单元故障 | `binary_sensor.saj_inverter_fault_dcdc_device` | 二元传感器 | - | HS3 | - | 是 |
| 显示板时钟故障 | `binary_sensor.saj_inverter_fault_display_clock` | 二元传感器 | - | HS3, H2 | - | 是 |
| 显示板通信丢失 | `binary_sensor.saj_inverter_fault_display_communication` | 二元传感器 | - | HS3, H2 | - | 是 |
| 显示板存储器故障 | `binary_sensor.saj_inverter_fault_display_memory` | 二元传感器 | - | HS3, H2 | - | 是 |
| DRM0 故障 | `binary_sensor.saj_inverter_fault_drm0` | 二元传感器 | - | HS3, H2 | - | 是 |
| 充电桩通信丢失 | `binary_sensor.saj_inverter_fault_ev_charger_communication` | 二元传感器 | - | HS3 | - | 是 |
| 风扇 1 故障 | `binary_sensor.saj_inverter_fault_fan_1` | 二元传感器 | - | HS3, H2 | - | 是 |
| 风扇 2 故障 | `binary_sensor.saj_inverter_fault_fan_2` | 二元传感器 | - | HS3, H2 | - | 是 |
| 风扇 3 故障 | `binary_sensor.saj_inverter_fault_fan_3` | 二元传感器 | - | HS3, H2 | - | 是 |
| 风扇 4 故障 | `binary_sensor.saj_inverter_fault_fan_4` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 10 分钟平均过压 | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网丢失 | `binary_sensor.saj_inverter_fault_grid_lost` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网过频 | `binary_sensor.saj_inverter_fault_grid_overfrequency` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 R 相直流注入过高 | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 R 相直流电压过高 | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 R 相过压 | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 R 相欠压 | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 S 相直流注入过高 | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 S 相直流电压过高 | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 S 相过压 | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 S 相欠压 | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 T 相直流注入过高 | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 T 相直流电压过高 | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 T 相过压 | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网 T 相欠压 | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电网欠频 | `binary_sensor.saj_inverter_fault_grid_underfrequency` | 二元传感器 | - | HS3, H2 | - | 是 |
| 逆变器硬件过流 | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | 二元传感器 | - | HS3, H2 | - | 是 |
| 绝缘故障 | `binary_sensor.saj_inverter_fault_insulation` | 二元传感器 | - | HS3, H2 | - | 是 |
| 内部通信丢失 | `binary_sensor.saj_inverter_fault_internal_communication` | 二元传感器 | - | HS3, H2 | - | 是 |
| 漏电流故障 | `binary_sensor.saj_inverter_fault_leakage_current` | 二元传感器 | - | HS3, H2 | - | 是 |
| 漏电流传感器故障 | `binary_sensor.saj_inverter_fault_leakage_current_device` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电表通信丢失 | `binary_sensor.saj_inverter_fault_meter_communication` | 二元传感器 | - | HS3, H2 | - | 是 |
| 零地电压故障 | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 离网输出欠压 | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| 输出过载 | `binary_sensor.saj_inverter_fault_output_overload` | 二元传感器 | - | HS3, H2 | - | 是 |
| 过温 | `binary_sensor.saj_inverter_fault_over_temperature` | 二元传感器 | - | HS3, H2 | - | 是 |
| 并机系统通信丢失 | `binary_sensor.saj_inverter_fault_parallel_communication` | 二元传感器 | - | HS3 | - | 是 |
| PV 硬件过流 | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | 二元传感器 | - | HS3, H2 | - | 是 |
| PV 输入故障 | `binary_sensor.saj_inverter_fault_pv_input` | 二元传感器 | - | HS3, H2 | - | 是 |
| PV 输入模式故障 | `binary_sensor.saj_inverter_fault_pv_input_mode` | 二元传感器 | - | HS3, H2 | - | 是 |
| 光伏电表通信丢失 | `binary_sensor.saj_inverter_fault_pv_meter_communication` | 二元传感器 | - | HS3 | - | 是 |
| PV 过压 | `binary_sensor.saj_inverter_fault_pv_overvoltage` | 二元传感器 | - | HS3, H2 | - | 是 |
| PV 软件过流 | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | 二元传感器 | - | HS3, H2 | - | 是 |
| 继电器故障 | `binary_sensor.saj_inverter_fault_relay` | 二元传感器 | - | HS3, H2 | - | 是 |
| 从控制器通信丢失 | `binary_sensor.saj_inverter_fault_slave_communication` | 二元传感器 | - | HS3 | - | 是 |
| 低温 | `binary_sensor.saj_inverter_fault_under_temperature` | 二元传感器 | - | HS3, H2 | - | 是 |
| 逆变器未识别的故障 | `binary_sensor.saj_inverter_fault_unrecognised` | 二元传感器 | - | HS3, H2 | - | 是 |
| 电池包 2 故障 | `binary_sensor.saj_battery_pack2_fault` | 二元传感器 | - | H2 | 电池; 电池包 2 及以上 | 是 |
| 电池包 2 警告 | `binary_sensor.saj_battery_pack2_warning` | 二元传感器 | - | H2 | 电池; 电池包 2 及以上 | 是 |
| 电池包 3 故障 | `binary_sensor.saj_battery_pack3_fault` | 二元传感器 | - | H2 | 电池; 电池包 3 及以上 | 是 |
| 电池包 3 警告 | `binary_sensor.saj_battery_pack3_warning` | 二元传感器 | - | H2 | 电池; 电池包 3 及以上 | 是 |
| 电池包 4 故障 | `binary_sensor.saj_battery_pack4_fault` | 二元传感器 | - | H2 | 电池; 电池包 4 及以上 | 是 |
| 电池包 4 警告 | `binary_sensor.saj_battery_pack4_warning` | 二元传感器 | - | H2 | 电池; 电池包 4 及以上 | 是 |
| 直流母线过压 | `binary_sensor.saj_inverter_fault_bus_overvoltage` | 二元传感器 | - | H2 | - | 是 |
| 直流母线欠压 | `binary_sensor.saj_inverter_fault_bus_undervoltage` | 二元传感器 | - | H2 | - | 是 |
| 电网相位故障 | `binary_sensor.saj_inverter_fault_grid_phase` | 二元传感器 | - | H2 | - | 是 |
| 孤岛 | `binary_sensor.saj_inverter_fault_islanding` | 二元传感器 | - | H2 | - | 是 |
