[en](../../../en-gb/user/entities/README.md) | [de](../../../de/user/entities/README.md) | [nl](../../../nl/user/entities/README.md) | [fr](../../../fr/user/entities/README.md) | zh | [es](../../../es/user/entities/README.md) | [it](../../../it/user/entities/README.md) | [pl](../../../pl/user/entities/README.md) | [sv](../../../sv/user/entities/README.md)

# 实体

SAJ Local 可以创建的所有实体，每个区域一页。集成功能列表的 [设备与实体](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) 一节说明了实体类型、默认启用的实体和功率读数的正负号。

系统只会得到与其型号、已安装设备以及相数、光伏组串数和电池包数相符的实体。“型号”列说明哪些型号有该实体，“设备和数量”列说明需要安装什么。

由 `make docs` 生成，请勿手动编辑。

| 区域 | 实体 | 包含内容 |
| --- | --- | --- |
| [逆变器与光伏](inverter-and-pv.md) | 241 | 逆变器输出、光伏组串、备用端口、电量计数器、版本和家庭负载 |
| [电网与电表 A](grid-and-meter-a.md) | 88 | 电网连接和电表 A（电网电表） |
| [电表 B](meter-b.md) | 22 | 电表 B，测量光伏逆变器的第二块电表 |
| [电池](battery.md) | 133 | 电池整体 |
| [电池包](battery-packs.md) | 58 | 每个电池包的读数和标识 |
| [充电桩](ev-charger.md) | 87 | 充电桩及其充电控制 |
| [并机系统](parallel-system.md) | 63 | 并机系统的读数 |
| [设置](settings.md) | 22 | 更改逆变器的设置和命令 |
| [故障](faults.md) | 139 | 逆变器、电池和充电桩上报的故障 |
| [由集成添加](added-by-the-integration.md) | 7 | 集成在寄存器目录之外添加的实体 |
