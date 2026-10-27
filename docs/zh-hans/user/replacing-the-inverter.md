[en](../../en-gb/user/replacing-the-inverter.md) | [de](../../de/user/replacing-the-inverter.md) | [nl](../../nl/user/replacing-the-inverter.md) | [fr](../../fr/user/replacing-the-inverter.md) | zh | [es](../../es/user/replacing-the-inverter.md) | [it](../../it/user/replacing-the-inverter.md) | [pl](../../pl/user/replacing-the-inverter.md) | [sv](../../sv/user/replacing-the-inverter.md)

# 更换逆变器

“更换逆变器”页面说明如何把系统迁移到新的逆变器，或在 H2 与 HS3 之间迁移，并保留设备、实体和历史记录。完整列表见集成功能列表的 [更换型号](../../../custom_components/saj_local/docs/features.md#model-replacement) 一节。

## 主动迁移系统

1. 确认新的逆变器可以访问。如果新的逆变器地址不同，你要在下一步输入该地址。
2. 打开“配置”，即 SAJ Local 集成页面上该系统所在行的齿轮。
3. 如果地址变了，请更改主机、端口或单元 ID。把“型号”保持为“自动”；如果逆变器未被识别，则选择型号。
4. 选择“提交”，然后确认更换。确认内容会指出 SAJ Local 发现的型号和序列号。

你确认之后，设备、实体、实体的名称和历史记录都保留在系统中。当两个型号都有某个实体时，该实体的历史记录在迁移前后保持连续。SAJ Local 会忘记在旧逆变器上检测到的设备以及旧逆变器的电池包数量，并在新逆变器上重新检测设备。

## 该地址上的逆变器未经你操作而变化时

SAJ Local 在系统每次加载时检查逆变器的标识。当该地址上的逆变器识别为另一个型号，或序列号不同时，SAJ Local 不加载系统，并提出一个修复问题。该修复问题的修复会显示逆变器现在上报的型号和序列号，并采用你确认的逆变器。

- 实体 ID、历史记录、允许控制和其他所有设置保持不变。
- 当逆变器上报的内容与表单显示的不同时，表单会指出这一点，并显示新的值，而不是保存旧的值。
- 当该地址上的设备不是已识别的型号时，修复问题会指出这一点并指向“配置”。没有可采用的内容。请手动选择型号，参见[开始使用](getting-started.md#逆变器未被识别时)。

这些修复问题列在[故障和修复](faults-and-repairs.md#修复问题)中。

## 尚不支持

- 采用已经属于另一个系统的逆变器。SAJ Local 会拒绝这种采用。
