[en](../../README.md) | [de](../de/README.md) | [nl](../nl/README.md) | [fr](../fr/README.md) | zh | [es](../es/README.md) | [it](../it/README.md) | [pl](../pl/README.md) | [sv](../sv/README.md)

# SAJ Local Home Assistant 集成

![SAJ Local](../../images/header.png)

[![HACS 自定义](https://img.shields.io/badge/HACS-%E8%87%AA%E5%AE%9A%E4%B9%89-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![发布](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local?label=%E5%8F%91%E5%B8%83)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![活跃安装数](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=%E6%B4%BB%E8%B7%83%E5%AE%89%E8%A3%85%E6%95%B0&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![检查](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![许可证](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local?label=%E8%AE%B8%E5%8F%AF%E8%AF%81)](../../LICENSE)

⭐ [在 GitHub 上为项目点星](https://github.com/Counterphase-Labs/ha-saj-local)：你的支持是我们真正的动力！🙏😊

把你的 SAJ 光伏系统接入 Home Assistant，通过你自己的网络直接从逆变器读取数据。无需云账户，中间没有厂商应用，并采用对硬件友好的轮询方式。

这是一个非官方的社区集成，并非由 SAJ 制作、支持或认可。请参阅[免责声明](user/README.md#免责声明)。

> **状态：正在积极开发中，尚未发布。** 目前还没有已发布的版本。

## 为什么选择 SAJ Local

- **合理的默认设置。** 添加你的逆变器，即可得到可用的配置，无需翻阅大量选项。逆变器、电池及相关设备会被自动检测。
- **对逆变器友好。** 一次只有一个连接、一个请求，并设有硬性的请求上限，任何设置、重新加载或故障都无法超过。读取什么、多久读取一次，由你决定。
- **默认只读，除非你另有设定。** 写入按安装单独选择开启，因此逆变器上不会有任何意外更改。
- **所有型号使用相同的名称。** 仪表盘和自动化只需编写一次，即可在各种 SAJ 型号上继续使用，从 H2 换到 HS3 后也依然有效。
- **多个系统。** 可将多个 SAJ 系统连接到同一个 Home Assistant。
- **仪表盘卡片。** 用于查看信息和更改配置的卡片，可从卡片选择器中添加。
- **清晰的错误和安全的诊断。** 出现问题时，你会知道出了什么问题以及原因，调试转储也设计为可以放心分享。
- **完全本地。** 一切都通过你的网络与逆变器通信，不会向任何云服务发送数据。

## 支持的设备

支持 SAJ HS3 和单相 SAJ H2。完整列表以及尚不支持的设备，请参阅[支持的设备](user/supported-equipment.md)。

## 文档

- [用户文档](user/README.md)：安装、设置和操作 SAJ Local。
- [开发者文档](developer/README.md)：SAJ Local 如何构建、检查和发布。
- [参与贡献](../../CONTRIBUTING.md)：准备一份检出副本并提交更改。

## 帮助与反馈

欢迎在[问题跟踪器](https://github.com/Counterphase-Labs/ha-saj-local/issues)中提问、报告错误和提出想法。

请私下报告安全问题，请参阅[安全政策](../../SECURITY.md)。

## 许可证

[MIT](../../LICENSE)
