[en](../../en-gb/developer/checks.md) | [de](../../de/developer/checks.md) | [nl](../../nl/developer/checks.md) | [fr](../../fr/developer/checks.md) | zh | [es](../../es/developer/checks.md) | [it](../../it/developer/checks.md) | [pl](../../pl/developer/checks.md) | [sv](../../sv/developer/checks.md)

# 检查

每个 make 目标运行什么、如何缩小一次运行的范围，以及每项检查遵循的规则。

## Make 目标

每个操作都是一个 make 目标，CI 调用同样的目标，因此在本地通过和在 CI 中通过含义相同。新的 CI 步骤先从一个 make 目标开始。`make help` 以一行列出每个目标，`make help ARGS=<target>` 描述一个目标：该目标运行什么、成功和失败时打印什么、`ARGS` 的作用，对于分组目标，还有该目标运行的步骤。

`make ci` 运行每个检查步骤，是完成的定义。GitHub 在 [ci.yml](../../../.github/workflows/ci.yml) 唯一的 `checks` 作业中直接运行 `make ci`，同时运行共享的 `roquerodrigo/workflows` 作业（`lint`、`tests`、`validate`）和 `hacs` 作业，因此添加到 `make ci` 的步骤无需更改工作流就会在 GitHub 中运行。迭代时请运行范围更窄的目标。

`make build` 是前端唯一的生产构建。`make test` 运行每个测试套件，每个套件都有自己的目标，因此可以单独运行一个套件：

| 目标 | 套件 |
| --- | --- |
| `make test-python` | 库、集成、模拟器和检查运行器的 pytest 单元测试，不含 `tests/mock-integration` 和 `tests/scripts/test_runner_processes.py`，带有 100 % 行和分支覆盖率门槛。完整运行是两次 pytest 运行写入同一个覆盖率数据文件，使用 `ctrace` 内核，并为每个测试设置一个覆盖率上下文：先运行不带 Home Assistant 插件且阻止套接字的 `tests/saj`、`tests/mock` 和 `tests/scripts`，再运行带插件的 `tests/saj-integration`，并对合并后的数据应用门槛。任何测试主体耗时超过 200 毫秒（不计夹具的准备和清理）也会使该步骤失败。 |
| `make test-frontend` | 卡片的 Vitest 单元测试，带覆盖率门槛。 |
| `make test-modules` | 每个含逻辑（任何函数、方法或分支）的模块，仅对照映射到该模块的单元测试文件，要求每个模块 100 % 的行和分支覆盖率。该门槛读取 `make test-python` 的覆盖率数据，因此 `make test-modules` 会先运行 `make test-python`。含逻辑而没有单元测试文件的模块会失败，不含逻辑的模块（例如空模块或数据表）会被跳过。 |
| `make test-isolated` | 在没有 Home Assistant 的环境中运行 `tests/saj` 和 `tests/mock` 测试，用来证明库、模拟器与 Home Assistant 之间的边界。覆盖率针对这些测试文件所测试的模块设置门槛。 |
| `make test-runner-processes` | `tests/scripts/test_runner_processes.py` 中检查运行器的真实进程测试，这些测试会启动真实的进程，不计入覆盖率。 |
| `make test-browser-controlled` | 针对构建出的包和受控数据运行 Playwright，不使用 Home Assistant。 |
| `make test-browser-home-assistant` | 针对一次性的 Home Assistant 运行 Playwright，其中有一个 HS3 模拟器和一个 H2 模拟器，用来证明卡片在真实的前端中加载并工作。该目标会先运行 `make build` 和 `make mock-build`，因为 Home Assistant 镜像从工作树复制卡片包，而模拟器使用 `saj-local-mock` 镜像。 |
| `make mock-smoke` | 模拟器容器应答客户端，然后运行 `tests/mock-integration` 中的测试。该目标会先运行 `make mock-build`，并从 `saj-local-mock` 镜像运行场景。 |

构成 `make ci` 的各项检查也各有一个目标，因此可以单独运行一个工具：

| 目标 | 检查 |
| --- | --- |
| `make ruff` | `ruff format --check` 和 `ruff check`。 |
| `make mypy` | 严格类型检查。 |
| `make import-lint` | import-linter 契约。 |
| `make complexipy` | 认知复杂度上限。 |
| `make copy-paste` | jscpd 重复代码和文本检测，范围是包括 `docs/` 在内的整个仓库。 |
| `make prettier`、`make tsc`、`make eslint` | 前端的格式化、类型检查和 lint。 |
| `make build` | 前端的 Vite 生产构建。 |
| `make release-check` | HACS 压缩包含有 `asset-manifest.json` 和构建出的卡片包。压缩包由 `custom_components/saj_local/` 中的文件制作，因此构建出的包必须在树中。`custom_components/saj_local/manifest.json`、`pyproject.toml` 和 `frontend/package.json` 中的版本为 `X.Y.Z` 或 `X.Y.ZbN`，并且三个文件相同，`HEAD` 上的标签等于该版本。`HEAD` 上没有标签时，会跳过标签比较。 |
| `make freeze-check` | 与最新的稳定发布标签相比，没有移除任何实体键、实体 ID、已存储的设置键或卡片类型，也没有更改任何实体平台、单位、设备类别、状态类别或状态值。测试版标签会被跳过，因此测试版绝不会冻结接口。没有稳定发布标签时，该步骤通过。 |
| `make docs-check` | 生成的实体参考、链接、图片、每个页面的语言栏、页面长度和功能列表覆盖情况。参见[文档页面](documentation.md#检查)。 |
| `make template-check` | `bug.yml` 要求附上诊断下载，问题模板应用或链接的每个标签都存在于 `.github/labels.yml` 中，并且 `bug.yml` 的型号下拉列表与 `translations/en.json` 中的型号一致。 |
| `make mock-build` | 模拟器镜像可以构建，并且不含字节码。 |
| `make validate` | 在 Docker 中对工作树运行 hassfest。HACS 验证读取已推送的仓库，因此只有 `hacs` 工作流作业运行 HACS 验证。 |

`make lint`、`make python-ci`、`make frontend-check` 和 `make frontend-ci` 运行这些目标的组合。

另有四个目标不是检查。`make setup` 安装 Python 和前端依赖以及 Chromium，`make docs` 重新生成实体参考，`make docs-images` 制作文档截图（与 Home Assistant 浏览器测试一样，先运行 `make build` 和 `make mock-build`，并且不是 `make ci` 的步骤），`make up`、`make down` 和 `make logs` 运行开发用的 Home Assistant，参见[环境页面](environment.md#运行-home-assistant)。

每个目标都通过 `.github/scripts/` 中的检查运行器运行。运行器为每个步骤打印一行 `[x]` 或 `[ ]`，把失败步骤的发现以 `file:line message` 的形式打印出来，并打印最终结果行。即使有步骤失败，运行器也会运行每个选定的步骤，并把超时、信号或缺失的工具如实报告。每个步骤都有时间限制。简洁的输出是为了让人或代理只读取修复失败所需的内容。

GitHub Actions 固定到提交哈希，因此被移动的标签无法改变 CI 运行的内容。

## 选项

- `ARGS="..."` 把路径和选项传给单工具目标，例如 `make test-python ARGS="tests/saj/test_poller.py -k decode"` 或 `make ruff ARGS="custom_components/saj_local/coordinator.py"`。`make help ARGS=<target>` 说明 `ARGS` 对每个目标的作用。
- `ONLY=<step,...>` 运行分组目标的一部分步骤，例如 `make ci ONLY=ruff,mypy`。目标不运行的名称会报错。
- `V=1` 流式输出原始的工具输出，并在该次运行中关闭精简的工具配置和环境设置。

## 子集运行的覆盖率

完整的 `make test-python` 测量整个包并设置门槛。当 `ARGS` 选择测试文件或文件夹时，该目标只测量这些测试文件所测试的模块的覆盖率，把映射到这些模块的其他单元测试文件加入运行，并对这些模块应用同样的 100 % 门槛。因此，运行 `tests/saj-integration/test_coordinator_write.py` 也会运行 `test_coordinator.py` 和 `test_coordinator_power.py`，并对 `coordinator.py` 设置门槛。模块是与测试文件同名（去掉 `test_` 前缀）的文件，按测试文件夹查找：

[测试文件夹与模块文件夹对照表](../../en-gb/developer/checks.md#coverage-of-a-subset-run)在英文页面上。

没有同名模块的测试文件列在 `.github/scripts/pytest_scope.json` 中，每个都带有该文件所测试的模块，没有已知模块的测试文件会被拒绝，直到该文件被添加到那里。文件夹映射在 `.github/scripts/pytest_scope.py` 中。用 `-k`、`-m` 或 `--lf` 选择测试需要在 `ARGS` 中有测试文件，这样才能对该文件所测试的模块设置覆盖率门槛。

完整的 `make test-python` 会记录每一行和每个分支是由哪个测试运行的（每个测试一个覆盖率上下文），因此一次运行同时满足两个门槛。`ctrace` 内核只为完整运行设置，设在其命令的环境中，因为默认的 `sysmon` 内核只为第一个运行某一行的测试记录该行，从而使后面的测试没有上下文。同一次完整运行还测量每个测试主体的耗时，任何超过 200 毫秒的主体都会使该步骤失败，并给出测试 ID 和时间。在覆盖率测量下的 200 毫秒约相当于正常运行中的 50 毫秒，高于健康测试在覆盖率测量下达到的 125 毫秒，因此该门槛不会随机失败。子集运行保持使用 `sysmon` 内核，不记录上下文，也不应用耗时门槛。

`test-modules` 在 `make ci` 中运行，仅用映射到每个模块的单元测试文件，对每个模块设置 100 % 的行和分支覆盖率门槛。该门槛只计入这些测试文件的上下文以及导入该模块时运行的代码，因此其他模块的测试带来的覆盖率不计入。`test-modules` 读取 `test-python` 的覆盖率数据，因此单独运行 `make test-modules` 会先运行 `test-python`，而 `make ci` 只运行一次测试。含逻辑而没有单元测试文件的模块会使该步骤失败，不含逻辑的模块会被跳过，因为需求禁止对常量写测试。只在完整的 `test-python` 运行中才通过门槛的模块，意味着其他测试偶然覆盖了该模块，这是需要修复的真实缺口。`test-isolated` 设置覆盖率门槛的方式与任何子集运行相同。

## 测试

规则在[全局需求的“测试”一节](../../../.github/work/requirements.md#testing)中。原因如下：

- **覆盖率只计单元测试。** 把真实模块连接在一起的测试会提高数字，却无法证明其中任何一个模块。
- **单元测试快速且相互隔离。** 没有套接字、服务器、夹具文件、真实时间或长时间的模拟。为此，时间、随机性和 I/O 在整个代码中都是注入的。
- **集成测试只证明各部分已连接。** 对模拟器而言，集成测试是 `make mock-smoke`。
- **不允许内联绕过** lint、类型或覆盖率检查。请更改配置（决定在那里清晰可见），或重构代码。
- **断言行为，而不是常量。** 重述寄存器地址的测试什么也证明不了。

`tests/` 恰好有六个文件夹：

- `tests/saj`：SAJ 库的单元测试。
- `tests/saj-integration`：Home Assistant 集成的单元测试，不是集成测试。
- `tests/mock`：Modbus 模拟器的单元测试，含 `profiles/` 和 `simulation/`。
- `tests/mock-integration`：模拟器的容器冒烟脚本和随附场景的测试。
- `tests/playwright`：浏览器测试的 Docker 脚本。
- `tests/scripts`：检查运行器的单元测试，以及 `test_runner_processes.py` 中的真实进程测试。

`tests/mock-integration` 和 `tests/scripts/test_runner_processes.py` 不在单元测试运行之内，也不计入覆盖率。

## 技术栈

| 组件 | 原因 |
| --- | --- |
| Python 与 `uv` | 一个锁文件，本地和 CI 中的安装相同。 |
| Ruff，所有规则全开 | 每个例外都是 `[tool.ruff.lint]` 中清晰可见的决定。 |
| mypy | 寄存器解码容易出现缩放、符号和宽度方面的错误，类型可以发现这些错误。 |
| import-linter | 使[架构页面](architecture.md#项目如何划分)上的边界成为会失败的检查。 |
| complexipy、jscpd | 寄存器映射代码会因重复而膨胀，这些限制可以阻止膨胀。 |
| pytest，100 % 分支覆盖率 | 参见[测试](#测试)。 |
| Lit、TypeScript、Vite | Home Assistant 的前端是 Lit，因此卡片不需要第二种框架。 |
| Playwright | 在真实的浏览器和真实的 Home Assistant 中驱动卡片，并制作[文档截图](documentation.md#截图)。 |
| Docker Compose | 参见[环境页面](environment.md#docker)。 |

Home Assistant 固定在多个必须一起更改的文件中，否则 lint 和测试会针对不同的内核运行。步骤见[发布页面](releasing.md#升级-home-assistant-版本)。
