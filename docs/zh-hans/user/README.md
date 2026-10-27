[en](../../en-gb/user/README.md) | [de](../../de/user/README.md) | [nl](../../nl/user/README.md) | [fr](../../fr/user/README.md) | zh | [es](../../es/user/README.md) | [it](../../it/user/README.md) | [pl](../../pl/user/README.md) | [sv](../../sv/user/README.md)

# SAJ Local 用户文档

SAJ Local 是一个本地 Home Assistant 集成。SAJ Local 通过你自己网络上的 Modbus TCP，直接从逆变器读取 SAJ HS3 或 H2 太阳能系统，并在你允许控制时，从 Home Assistant 更改逆变器的设置。SAJ Local 不需要云账户，并且会限制发往逆变器的请求，使逆变器的通信模块保持正常工作。

SAJ Local 是非官方的、由社区构建的集成。SAJ 不制作、不支持也不认可 SAJ Local。参见[免责声明](#免责声明)。

SAJ Local 仍在开发中，尚无已发布的版本。下面的每个页面都会说明哪些内容尚不支持。文档涵盖 HS3 和 H2，并用“仅 HS3”这样的注释标出差异。截图来自模拟系统，因此读数并不真实。

## 从这里开始

1. 用 HACS [安装 SAJ Local](installation.md)。
2. 确认你的逆变器在[支持的设备](supported-equipment.md)之列。
3. [开始使用](getting-started.md)：添加你的第一个系统。
4. 了解 SAJ Local 会为你检测的[可选设备](optional-equipment.md)。

## 了解你的系统

- [实体和前缀](entities-and-prefix.md)：实体是什么、实体 ID 如何构成，以及如何添加前缀。
- [实体参考](entities/README.md)：每个实体，含实体 ID、型号、设备和默认值。由集成生成。
- [轮询](polling.md)：多久读取一次逆变器，以及如何让某些实体读取得更快或更慢。
- [保护逆变器](protecting-the-inverter.md)：SAJ Local 对自身请求所设的限制。

## 更改内容

- [更改设置](changing-settings.md)：允许控制、更改设置和使用 EMS。
- [功率控制](power-control.md)：手动或按计划让电池、电网连接或逆变器保持在设定的功率。
- [更换逆变器](replacing-the-inverter.md)：把系统迁移到新的逆变器，或在 H2 与 HS3 之间迁移，并保留历史记录。

## 仪表盘

- [仪表盘卡片](cards/README.md)：SAJ Local 添加到 Home Assistant 的卡片、磁贴卡片功能和徽章。

## 术语

- [术语表](nomenclature.md)：集成、卡片和文档使用的 SAJ 和 Home Assistant 术语及其含义。

## 出现问题时

- [设备故障和修复问题](faults-and-repairs.md)：设备上报的故障，以及 SAJ Local 提出的修复问题。
- [故障排查](troubleshooting.md)：诊断、调试日志，以及到哪里寻求帮助。

## 各部分能做什么

功能列表说明目前已构建的内容：[集成](../../../custom_components/saj_local/docs/features.md)和[卡片](../../../frontend/docs/features.md)。

开发人员：参见[开发者文档](../developer/README.md)。

## 免责声明

SAJ Local 是一个独立的、由社区构建的集成。SAJ Local 与 SAJ（广州三晶电气股份有限公司）没有关联，SAJ 及其子公司和关联公司没有授权、赞助或认可 SAJ Local。

SAJ、SAJ 徽标以及所有相关的产品名称、型号名称和商标均为各自所有者的财产。文档使用这些名称，只是为了标明 SAJ Local 所适用的设备。

软件按“原样”提供，不附带任何形式的保证。使用 SAJ Local 的风险由你自己承担：对于因使用 SAJ Local 造成的设备损坏、数据丢失、保修失效或任何其他后果，作者概不负责。该警告尤其适用于向你的逆变器写入设置。

## 致谢

H2 支持建立在 stanus74 在 [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus) 中的寄存器研究和现场测试的基础之上。谢谢。
