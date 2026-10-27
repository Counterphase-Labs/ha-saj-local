[en](../../en-gb/developer/frontend.md) | [de](../../de/developer/frontend.md) | [nl](../../nl/developer/frontend.md) | [fr](../../fr/developer/frontend.md) | zh | [es](../../es/developer/frontend.md) | [it](../../it/developer/frontend.md) | [pl](../../pl/developer/frontend.md) | [sv](../../sv/developer/frontend.md)

# 前端

卡片包如何组织和构建，以及如何在开发实例中查看每张卡片。

前端涵盖内容的完整列表见功能列表中的以下几节：集成的 [卡片](../../../custom_components/saj_local/docs/features.md#cards)，以及卡片的 [元素与设置](../../../frontend/docs/features.md#elements-and-setup) 和 [主题与语言](../../../frontend/docs/features.md#theme-and-language)。

## 构建

卡片、磁贴卡片功能和徽章是 `frontend/` 下的一个 Lit 和 TypeScript 包。`make build` 运行 Vite，把包写入 `custom_components/saj_local/frontend/`，文件名为 `saj-local-<hash>.js`，并附带一个 `asset-manifest.json`，因为 HACS 把集成目录作为一个压缩包发布。Git 跟踪构建出的包和清单，因此对卡片的更改要与新的构建一起提交。集成读取清单，提供清单所指的文件，并把该文件的 URL 添加到 Home Assistant 前端，因此用户无需添加仪表盘资源。

哈希值随每次构建而变化，使浏览器绝不会运行过时的包。代价是 Home Assistant 在启动时只注册一次带哈希的文件名：新的包需要重启 Home Assistant，浏览器才会得到新的文件。开发实例挂载集成目录，因此请运行 `make build` 并重启 Home Assistant 来查看更改。

## 源码布局

布局遵循一同变化的内容：

- `src/system/` 保存所有与绘制无关的内容：在 `hass` 中查找系统的实体、功率方向、星期、计划时段、故障、控制锁和服务调用。该文件夹从不接触 DOM，因此这些规则无需浏览器即可测试。
- `src/ui/` 保存每张卡片都会绘制的部分，只用 Home Assistant 的主题变量设置样式，因为 Home Assistant 前端不向自定义卡片承诺提供任何 `ha-*` 元素。
- `src/cards/`、`src/features/` 和 `src/badges/` 保存各个元素，并把这些元素注册到 Home Assistant 选择器。
- `src/i18n/` 保存只有卡片需要的文字，每种语言一个文件，以 Home Assistant 语言代码命名，与集成的 `translations/` 文件夹中的文件一样（英语和八种目标语言），对其他任何语言以英语作为后备。实体名称、状态和数值来自 Home Assistant。
- `tests/fakes/` 保存由实体列表构建的模拟 `hass`，以及元素所用模块的替代品。每个单元测试用其中的模拟对象替换所有协作者，只测试一个模块。

元素通过设备和翻译键查找系统的实体，绝不通过实体 ID，因此卡片绝不依赖实体 ID 前缀。

## 测试

`make test-frontend` 运行带覆盖率门槛的 Vitest 单元测试。`make test-browser-controlled` 用受控数据对构建出的包运行 Playwright，`make test-browser-home-assistant` 对真实的 Home Assistant 运行 Playwright，参见[检查页面](checks.md#make-目标)。用户文档的截图来自第三个 Playwright 配置，参见[截图](documentation.md#截图)。

## 展示仪表盘

要以每个选项查看每张卡片，需要一个带有真实系统的 Home Assistant，因此开发环境通过 `config/configuration.yaml` 的 `lovelace: dashboards:` 块，从 `config/dashboards/saj-hs3.yaml` 和 `config/dashboards/saj-h2.yaml` 声明了两个仪表盘 `saj-hs3` 和 `saj-h2`。这些仪表盘是手写的纯 YAML，没有任何脚本生成这些仪表盘。每个 SAJ Local 元素都是由其自身 YAML 配置的自定义元素，因此每张卡片、磁贴功能和徽章都单独写出，并设置了每个选项，标题下标明卡片及其选项。

- 每个仪表盘有四个视图：仪表盘（典型系统仪表盘的卡片，以普通卡片写出）、卡片（每张卡片的每种选项组合）、功能和徽章（每个时段星期实体对应一张带 `custom:saj-local-weekdays-feature` 功能的磁贴卡片，以及状态徽章）和空状态（每张卡片分别不带 `device`，以及带有一个不是 SAJ Local 的设备的 `device`）。
- 这些仪表盘保存一个开发实例的设备 ID。设备 ID 不同的开发人员，需要替换每个文件中的两个 `device` ID（系统的 ID，以及空状态视图所用的、不是 SAJ Local 的设备的 ID），当实体 ID 前缀不同时，还要替换时段星期实体的 ID。
- Home Assistant 在启动时读取仪表盘声明，因此更改 `config/configuration.yaml` 之后请重启 Home Assistant。对仪表盘文件的更改在重新加载页面后生效。
