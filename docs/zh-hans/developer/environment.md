[en](../../en-gb/developer/environment.md) | [de](../../de/developer/environment.md) | [nl](../../nl/developer/environment.md) | [fr](../../fr/developer/environment.md) | zh | [es](../../es/developer/environment.md) | [it](../../it/developer/environment.md) | [pl](../../pl/developer/environment.md) | [sv](../../sv/developer/environment.md)

# 开发环境

如何设置检出副本，并用模拟器运行开发用的 Home Assistant 实例。

## 设置检出副本

检出副本需要：用于 Python 工具的 [uv](https://docs.astral.sh/uv/)、用于卡片的 Node.js 和 npm、用于 Home Assistant 和模拟器的 Docker 及 Docker Compose，以及 `make`。所需版本在 `pyproject.toml` 和 `frontend/package.json` 中设定。克隆之后，`make setup` 会安装 Python 依赖、前端依赖，以及 Playwright 测试使用的 Chromium 浏览器。

## 运行 Home Assistant

`make up` 会启动带有该集成和两个 Modbus 模拟器（一个 HS3 和一个 H2）的 Home Assistant。`make logs` 跟踪 Home Assistant 日志，`make down` 停止所有服务。

Home Assistant 使用 8123 端口。HS3 模拟器在主机端口 5020 上应答 Modbus，H2 模拟器在 5021 上应答，模拟器页面在 5080 和 5081 上。在 Docker 内部，Home Assistant 通过服务名 `mock` 和 `mock-h2` 在 502 端口访问这些模拟器。不需要真实的逆变器。[模拟器页面](simulator.md)说明如何连接到这些模拟器，以及如何更改这些模拟器所模拟的内容。

要使用其他主机端口、其他时区或其他场景，请把 [compose.override.yaml.example](../../../compose.override.yaml.example) 复制为被忽略的 `compose.override.yaml`，并更改不同之处。不要为本地需求编辑 `compose.yaml`，因为 `make mock-smoke` 也会启动 `compose.yaml`。

## Docker

开发在容器中进行，因此 Home Assistant 是已知的、固定的版本，配置也是干净的。这些服务在下列文件中定义：

- [compose.yaml](../../../compose.yaml)：交互式环境，含 Home Assistant、HS3 模拟器 `mock` 和 H2 模拟器 `mock-h2`。该集成以只读方式挂载到 Home Assistant 中，因此容器绝不会写入源码树。模拟器把更改保存在 Git 忽略的 `mock/state/hs3/` 和 `mock/state/h2/` 中。
- [compose.playwright.yaml](../../../compose.playwright.yaml)：由 `Dockerfile.playwright-home-assistant` 构建的一次性 Home Assistant，含一个 HS3 模拟器、一个 H2 模拟器和 Playwright 运行器。`make test-browser-home-assistant` 使用服务 `homeassistant`、`mock`、`mock-h2` 和 `playwright`，证明每个端点都可以添加、加载、报告传感器值、在功率流卡片上显示光伏功率，并且在允许控制之后接受更改的设置。`make docs-images` 使用服务 `homeassistant`、`mock-docs`、`mock-h2` 和 `playwright-docs`，参见[截图](documentation.md#截图)。这些服务与交互式环境不共享任何状态。
- `compose.override.yaml`：你的机器的端口、时区和场景。Git 忽略该文件，`compose.override.yaml.example` 展示了其形式。

在 `config/` 下，Git 只跟踪 `configuration.yaml` 和 `config/dashboards/` 中的两个展示仪表盘。其余是本地 Home Assistant 状态。

[检查页面](checks.md)列出每个 make 目标运行什么，[前端页面](frontend.md#展示仪表盘)介绍这两个展示仪表盘。
