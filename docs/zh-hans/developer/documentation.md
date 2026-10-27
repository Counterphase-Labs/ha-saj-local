[en](../../en-gb/developer/documentation.md) | [de](../../de/developer/documentation.md) | [nl](../../nl/developer/documentation.md) | [fr](../../fr/developer/documentation.md) | zh | [es](../../es/developer/documentation.md) | [it](../../it/developer/documentation.md) | [pl](../../pl/developer/documentation.md) | [sv](../../sv/developer/documentation.md)

# 文档

文档页面如何组织、实体参考和截图如何制作，以及 `make docs-check` 在什么情况下失败。

## 布局

用户页面位于 `docs/en-gb/user/`，开发者页面位于 `docs/en-gb/developer/`。每个文件夹都有一个 `README.md` 索引，每个页面涵盖一个主题。任何手写页面都不超过 300 行。每个事实只有一个负责页面，列在[来源](#来源)下，其他每个页面都链接到负责页面，而不是重述该事实。

截图位于 `docs/images/en-gb/`。每张图片都必须被某个页面引用。

英语页面用英式英语书写，采用 Counterphase 的语气，并使用集成的翻译向用户显示的术语。用户页面泛指 SAJ，并在 HS3 与 H2 不同之处标明差异。页面绝不会按型号拆分为每个型号一个页面。

## 先有功能列表

三个功能列表是每个页面的基础：[集成](../../../custom_components/saj_local/docs/features.md)、[卡片](../../../frontend/docs/features.md)和[模拟器](../../../mock/docs/features.md)。功能列表的一节说明已构建的内容，并在该节的 `Files:` 行中列出应阅读的文件。在记录每一条陈述之前，请对照这些文件确认。需求文档说明预期的内容，只用来了解意图。出现在需求文档中却不在任何功能列表中的行为尚未构建，用户页面不会把该行为描述为可用。功能列表与代码不一致时，用户得到的是代码，因此要在同一次更改中更正功能列表。

描述代码的页面会链接到其 `Files:` 行列出该代码的功能列表章节，而不重复文件列表。

某个能力的更改，要在同一次更改中更新该部分的功能列表以及每个链接到被更改章节的用户页面。根目录的 `AGENTS.md` 保存该规则。

## 生成的实体参考

`docs/en-gb/user/entities/` 为每个区域保存一个生成的页面，外加一个 `README.md` 索引。运行 `make docs` 重新生成这些页面，然后提交重新生成的页面。文字页面绝不手写实体名称；文字页面链接到生成的页面。生成的页面不受 300 行限制，因为读者是在某个区域（例如电池）中搜索，而不是通读该区域。

生成器是 `.github/scripts/docs_check.py`，由 `make docs` 以 `--write` 运行。生成器只导入 SAJ 库，并读取 `custom_components/saj_local/translations/en.json`，因此生成器不需要 Home Assistant。每个区域页面都以指向涵盖该区域的功能列表章节的链接和一行关于实体 ID 前缀的说明开头，然后每个实体一行，含 `en.json` 中的名称、不带前缀的实体 ID、类型、单位、拥有该实体的型号、必须安装的设备（任何相数、组串或电池包数量除外），以及该实体是否默认启用。两个型号定义不同（例如单位不同）的实体，每种定义各占一行。

### 实体来源

每个实体都来自下列来源之一，生成器会读取所有这些来源：

| 来源 | 代码 | 实体 |
| --- | --- | --- |
| 每个已发布型号的寄存器目录 | [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py) 中的 `catalogue_of`，针对 [profiles.py](../../../custom_components/saj_local/saj/profiles.py) 的 `PROFILES` 中的每个型号配置调用，跳过未公开的行 | 传感器、二元传感器（故障）、数值输入器、选择、开关、时间和按钮 |
| 允许控制传感器 | [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) 中的 `CONTROL_ALLOWED_KEY` | `binary_sensor.saj_control_allowed`，两个型号都有 |
| 功率控制开关和数值输入器 | 每个型号配置的 `power_control`（[hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) 和 [h2.py](../../../custom_components/saj_local/saj/models/h2.py)）、[models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) 中的 `PowerFunction` 键，以及 [power_control.py](../../../custom_components/saj_local/saj/power_control.py) 中的 `FUNCTION_EQUIPMENT`，由 [switch.py](../../../custom_components/saj_local/switch.py) 和 [number.py](../../../custom_components/saj_local/number.py) 创建 | 型号的每个功率功能各有一个开关和一个数值输入器：电池两个型号都有，电网和逆变器仅 HS3 有 |

当 `en.json` 的 `entity` 块中的某个实体不在任何区域页面上时，`make docs-check` 会失败，因此生成器未读取的实体来源会被立即发现。新的来源需要生成器读取该来源，并在上表中增加一行。

### 区域

实体归入第一个匹配的区域，顺序如下：

1. 目录之外的实体：集成添加的实体。
2. 目录中的二元传感器，即故障：故障。
3. 带有电池包编号的实体：电池包。
4. 可选设备的实体：电池、电网和电表 A、电表 B、充电桩或并机系统。
5. 没有设备的可写实体：设置。
6. 键以 `grid_` 开头的实体：电网和电表 A。
7. 其他所有实体：逆变器和光伏。

`.github/scripts/docs_check.py` 的 `AREAS` 表给出各区域的名称、摘要，以及每个区域页面所链接的功能列表章节。

## 检查

`make docs-check` 不带 `--write` 运行 `.github/scripts/docs_check.py`，每个发现报告一行：

- 与 `make docs` 将写入的内容不同的生成页面；
- `en.json` 中不在任何区域页面上的实体，以及在 `en.json` 中没有名称的生成实体；
- 页面、`README.md`、`CONTRIBUTING.md`、`SECURITY.md` 和每个 `AGENTS.md` 中无法解析的相对链接、图片或标题锚点，包括指向功能列表和需求文档的链接；
- `docs/images/` 中没有任何页面引用的图片；
- 超过 300 行的手写页面；
- 在[功能覆盖表](#功能覆盖表)中没有对应行的功能列表章节、表中提到而功能列表没有的章节、表中提到而不存在的页面，以及没有按该章节的标题锚点链接到该行所指功能列表章节的页面。

`make docs-check` 是 `make ci` 的一个步骤，而 GitHub 运行 `make ci`，因此该检查无需更改工作流。该检查除链接规则和孤立图片规则之外不读取任何截图，也不启动浏览器。

## 截图

`docs/images/<code>/` 中的每张截图都由 `make docs-images` 制作：在 Docker 中的真实 Home Assistant 上，把用户语言设为该文件夹的语言，或者取自同一次运行中的模拟器页面。`make docs-images` 运行每种语言，英语优先，每次运行都使用全新的容器，`ARGS=<code>` 选择一种语言。没有任何截图是手工编辑或手工截取的，因此每当界面变化时都可以重建整套截图。截图显示的是模拟器，因此截图中的每个读数都是模拟值。

该目标运行 `tests/playwright/run-docs-images.sh`，该脚本构建 [compose.playwright.yaml](../../../compose.playwright.yaml) 的 `homeassistant` 和 `playwright-docs` 服务，启动一次性的 Home Assistant 和两个模拟器，运行规格，然后移除容器、卷和本地镜像。该目标需要 Docker，时间限制与 `make test-browser-home-assistant` 相同，并通过 `ARGS` 接受选项，由脚本接收。Home Assistant 镜像由 `Dockerfile.playwright-home-assistant` 构建，该文件构建卡片包并把集成复制进镜像，因此不挂载任何集成代码。规格是 `frontend/tests/browser/docs/screenshots.spec.ts`，由 `frontend/playwright.docs.config.ts` 配置。

- **系统。** HS3 是使用 `mock/scenarios/hs3-full-house.yaml` 的模拟器 `mock-docs`，该场景安装了所有设备。H2 是使用 `mock/scenarios/h2-battery.yaml` 的模拟器 `mock-h2`，并使用实体前缀 `h2`。两个模拟器都不挂载状态文件夹，因此每次运行都从场景开始。
- **固定条件。** 视口为 1280 乘 800 像素，主题为浅色，时钟为真实时间。较高的对话框或卡片在 1600 像素高的窗口中截取，因为 Home Assistant 固定的页眉会遮住元素的顶部。
- **语言。** 每次运行都会设置 Home Assistant 服务器语言（在设置 SAJ Local 之前，使实体以该语言的名称创建）和用户语言（按语言代码而不是按语言选择器的标签）。当 SAJ Local 的实体名称不是该次运行的语言时，运行失败。图片保存到 `docs/images/<code>/`。规格通过 URL 路由打开界面，通过 `name` 属性查找 SAJ Local 表单的字段，并用运行时通过 `hass.localize` 从正在运行的 Home Assistant 读取的文字，查找只有文字的 Home Assistant 控件。规格不含任何标签表，因此每种语言运行相同的步骤。
- **命名。** 每个文件命名为 `<page>-<subject>.png`，其中 `<page>` 是把 `/` 替换为 `-` 的页面路径，例如 `cards-battery-card.png`，显示该图片的页面链接到该文件。
- **模拟器页面。** 模拟器页面的截图来自同一次运行中的两个模拟器 `mock-docs` 和 `mock-h2`，并使用名称前缀 `developer-simulator-page-`。这些截图最后截取，在每张 Home Assistant 截图之后，因此在模拟器页面上所做的任何操作都不会改变 Home Assistant 截图。规格在 HS3 页面上设置故障“Fan 1 fault”，修复截图使模拟器拒绝的寄存器保持被拒绝状态，因此 Link 视图、流量日志和状态栏中的变化都显示真实的变化。
- **设置。** 规格通过引导 API 创建用户，在浏览器中通过配置流程添加 HS3，通过配置流程 API 添加 H2，为两个系统开启“允许控制”，并通过 Home Assistant WebSocket API 为每个系统添加一个仪表盘，其中含有每张 SAJ Local 卡片和状态徽章。
- **全部成功或全部不写。** 规格最多等待两分钟，直到两个系统都报告光伏功率。规格只在每个步骤都通过之后才写入图片，因此失败的运行会让已提交的图片保持原样。
- **等待。** 规格通过检查界面所显示的状态来等待界面，绝不使用固定的休眠。
- **修复。** 修复截图显示被拒绝寄存器的修复。规格为逆变器温度添加一个间隔为 10 秒的轮询组，通过模拟器页面的 `POST /api/link` 使模拟器拒绝该寄存器，并最多等待两分钟，直到 `repairs/list_issues` 列出 SAJ Local 的 `registers_refused` 问题。当该问题没有出现时，运行会失败，并给出指出缺失问题的消息。
- **表单。** 前缀更改警告被截取后表单随即关闭，这会中止流程，因此不会保存任何前缀。“允许控制”警告被截取后随即确认，因为卡片需要允许控制。
- **失败。** HTML 报告位于 `frontend/playwright-report/docs/`，失败的运行会把 Home Assistant 日志保存为 `frontend/test-results/docs/home-assistant.log`。

截图不做逐像素比较，无论在 CI 还是在其他任何地方。Home Assistant 每次运行渲染的实时数值和字体都有所不同，因此逐像素比较会在没有真实变化的情况下失败。请通过查看图片来审阅发生变化的图片。

### 添加或更改截图

1. 在规格中添加或更改截取操作，文件名采用 `<page>-<subject>.png` 的形式。
2. 从解释该主题的页面引用该图片。
3. 运行 `make docs-images`，查看发生变化的图片，并提交这些图片。
4. 运行 `make docs-check`。没有任何页面引用的图片，以及指向不存在图片的链接，都会被报告。

`make docs-images` 不是 `make ci` 的步骤，CI 也不会重新生成图片。请在每次发布之前运行该目标，参见[发布页面](releasing.md)。

## 添加页面

1. 在 `docs/en-gb/user/` 或 `docs/en-gb/developer/` 下创建页面，并从该文件夹的索引链接到该页面。
2. 把该页面链接到其 `Files:` 行列出该页面所描述代码的功能列表章节。
3. 把该页面加入功能覆盖表中该章节的那一行，或者添加一行。新的功能列表章节需要一行，`make docs-check` 才能通过。
4. 运行 `make docs-check`。

保持页面有用：链接到保存某个事实的文件，而不是复制该事实；记录决定的原因，因为原因很少变化而细节不断变化；示例要少，并且示例每次变化时都要重新运行。

## 语言

文档提供英语以及[全局需求](../../../.github/work/requirements.md#language)中的每种目标语言。功能列表和需求文档只保留英语。

- **布局。** 每种语言都有同级文件夹 `docs/<code>/user/`、`docs/<code>/developer/` 和 `docs/images/<code>/`，每种语言的文件名相同。代码为 `en-gb`、`de`、`nl`、`fr`、`zh-hans`、`es`、`it`、`pl` 和 `sv`。在多种语言中相同的代码块保留在每个页面中，并用一对 `jscpd:ignore-start` 和 `jscpd:ignore-end` 标记包住，仅限用户在计划中批准的例外，如 `AGENTS.md` 所述。一对标记只包住一个代码块，不包其他任何内容。
- **生成器。** `make docs` 根据 `custom_components/saj_local/translations/` 中相应的文件，为每种语言写入 `docs/<code>/user/entities/`。设备名称来自同一个翻译文件，生成器的其他文字来自 `.github/scripts/docs_text/<code>.json`。
- **文档检查。** `make docs-check` 对每个语言文件夹运行每条规则。本页的[功能覆盖表](#功能覆盖表)以相同的页面名称适用于每种语言，孤立图片规则把 `docs/images/<code>/` 与同一种语言的页面进行核对。
- **语言栏。** `docs/<code>/user/` 和 `docs/<code>/developer/` 下每一页的第一行（包括生成的实体页面）都是语言栏 `en | de | nl | fr | zh | es | it | pl | sv`，顺序始终不变。除当前语言外，每个标签都链接到该语言文件夹中的同一页，当前语言为纯文本。`make docs` 写入语言栏，`make docs-check` 报告第一行不是预期语言栏的页面，以及语言栏中指向不存在页面的链接。
- **翻译的 README。** 仓库根目录的 `README.md` 保持英文，其译文位于 `docs/<code>/README.md`，其中的链接指向该语言的页面。根目录的 `README.md` 和每个 `docs/<code>/README.md` 都以相同的语言栏作为第一行，`make docs-check` 会报告缺失的 `docs/<code>/README.md`。
- **截图。** `make docs-images` 对每种语言各运行一次规格，英语优先，每次运行都使用全新的容器。`ARGS=<code>` 选择一种语言，参见[截图](#截图)。
- **术语表。** 每种语言的 `user/nomenclature.md` 页面是该语言中集成、卡片和页面的每一份译文所遵循的术语列表。英语的[术语表](../user/nomenclature.md)是源头。
- **更改英语。** 对英语文字、页面或截图的更改，要在同一次更改中更新每种语言。没有任何检查使各种语言保持同步。

## 功能覆盖表

每个功能列表章节都根据该章节的 `Files:` 行进行调查，并由这里列出的页面涵盖。每个列出的页面都按该章节的标题锚点链接到该章节。页面名称相对于 `docs/en-gb/`，并链接到该页面。该表只在英文页面 [文档](../../en-gb/developer/documentation.md#feature-coverage-table) 上，`docs-check` 从那里读取该表。该表在每种语言中适用于相同的页面名称，页面的添加、合并或拆分要在同一次更改中更新该表。

## 来源

| 事实 | 负责方 |
| --- | --- |
| SAJ Local 做什么，一段简短的摘要 | [用户索引](../user/README.md) |
| 每个部分能做什么 | 三个功能列表 |
| 支持的型号和设备 | [支持的设备](../user/supported-equipment.md) |
| 实体名称、实体 ID、型号、设备和默认值 | 目录和 `translations/en.json`，通过[实体参考](../user/entities/README.md) |
| 实体类型、默认启用规则和符号约定 | 集成功能列表的“设备与实体”一节 |
| 开发环境设置 | [环境](environment.md) |
| Make 目标和检查规则 | [检查](checks.md) |
| Home Assistant 版本升级 | [发布](releasing.md) |
| 站点概览截图 | `docs/images/en-gb/cards-power-flow-card.png`，每次发布时复制到 `website` 仓库中的 `assets/images/saj-local-power-flow.png`，参见[发布页面](releasing.md) |
| 如何报告安全问题 | `SECURITY.md` |
| 问题标签和标签规则 | `.github/labels.yml` 和 `CONTRIBUTING.md` |
| 许可条款 | `LICENSE` |
| 预期的产品行为 | `.github/work/requirements.md` 和三个部分的需求文档 |
