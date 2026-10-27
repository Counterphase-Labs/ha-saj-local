[en](../../en-gb/user/installation.md) | [de](../../de/user/installation.md) | [nl](../../nl/user/installation.md) | [fr](../../fr/user/installation.md) | zh | [es](../../es/user/installation.md) | [it](../../it/user/installation.md) | [pl](../../pl/user/installation.md) | [sv](../../sv/user/installation.md)

# 安装

“安装”页面介绍如何通过 HACS（Home Assistant 社区商店）安装 SAJ Local。设置过程所做事项的完整列表见集成功能列表的 [设置与检测](../../../custom_components/saj_local/docs/features.md#setup-and-detection) 一节。

SAJ Local 尚未发布正式版本。安装前请先查看[支持的设备](supported-equipment.md)。

## 你需要什么

- 版本不低于 [`hacs.json`](../../../hacs.json) 中所列最低版本的 Home Assistant，以及 HACS。
- 一台在本地网络上应答 Modbus TCP 的受支持 SAJ 逆变器。你需要逆变器的地址；端口或单元 ID 不是默认值时，还需要端口和单元 ID。
- 不需要其他任何东西。SAJ Local 直接与逆变器通信，不向任何云服务发送数据。

## 安装步骤

1. 用下方第一个按钮在 HACS 中打开 SAJ Local。如果该仓库尚未列出，HACS 会要求你添加该仓库。
2. 在 HACS 中下载 SAJ Local。
3. 重启 Home Assistant。
4. 用下方第二个按钮添加你的系统，或按[开始使用](getting-started.md)操作。

[![打开你的 Home Assistant 实例，并在 HACS 中打开 SAJ Local 仓库。](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![打开你的 Home Assistant 实例，并开始设置 SAJ Local。](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local 自带仪表盘卡片，因此无需添加卡片资源。参见[仪表盘卡片](cards/README.md)。

## 测试版

在第一个稳定版发布之前，SAJ Local 的每个版本都是测试版。在 HACS 中打开 SAJ Local，打开菜单，选择“重新下载”，开启“显示测试版”，然后下载最新的测试版。不开启该开关时，HACS 会安装 SAJ Local 的开发版本。
