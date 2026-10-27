[en](../../en-gb/user/supported-equipment.md) | [de](../../de/user/supported-equipment.md) | [nl](../../nl/user/supported-equipment.md) | [fr](../../fr/user/supported-equipment.md) | zh | [es](../../es/user/supported-equipment.md) | [it](../../it/user/supported-equipment.md) | [pl](../../pl/user/supported-equipment.md) | [sv](../../sv/user/supported-equipment.md)

# 支持的设备

“支持的设备”页面列出 SAJ Local 支持的 SAJ 产品、每个型号可以配备的可选设备，以及尚不支持的内容。设置过程所做事项的完整列表见集成功能列表的 [设置与检测](../../../custom_components/saj_local/docs/features.md#setup-and-detection) 一节。

## 支持的型号

SAJ Local 根据逆变器上报的设备类型识别型号。任何其他设备类型都无法识别。

| 型号 | 识别依据 | SAJ Local 检测的可选设备 |
| --- | --- | --- |
| HS3 | 设备类型 `0x1610`，三相 | 电池、电表 A、电表 B、充电桩、并机系统 |
| H2，单相，两路光伏组串 | 设备类型 `0x005a` | 电池、电表 A、电表 B、并机系统 |
| H2，单相，三路光伏组串 | 设备类型 `0x005b` | 电池、电表 A、电表 B、并机系统 |

使用中可以看到的型号差异：

- **充电桩：** 仅 HS3。H2 没有充电桩实体、充电桩时段，控制卡片上也没有充电桩部分。
- **电池包：** H2 最多有五个电池包的实体。HS3 有一个电池包的实体。参见[可选设备](optional-equipment.md)。
- **EMS：** 仅 HS3。参见[更改设置](changing-settings.md#ems)。
- **功率控制：** HS3 提供电池、电网和逆变器。H2 只提供电池。参见[功率控制](power-control.md)。

[可选设备](optional-equipment.md)说明检测的工作方式以及如何覆盖检测结果。[实体参考](entities/README.md)列出每个实体需要哪个型号和哪种设备。

## 尚不支持

- 自动检测只识别表中的三种设备类型。其他 SAJ 产品，例如 HS2、H1 和 AS1，无法识别。
- 其他 H2 变体，例如三相 H2，上报其他设备类型，无法自动识别。你可以手动选择型号，SAJ Local 随后会把该型号标记为未验证。读数可能有误，因为 SAJ Local 无法核对读数。参见[开始使用](getting-started.md#逆变器未被识别时)。
- 在型号未验证的系统上更改设置。读取可以进行，但每一次更改都会被拒绝。

## 支持的依据

HS3 的支持已在一台真实的 HS3 上手动验证。H2 的支持依据 SAJ 协议文档和现场反馈，尚未在 H2 上手动验证。H2 上的设置写入和功率控制同样依据文档和现场反馈。
