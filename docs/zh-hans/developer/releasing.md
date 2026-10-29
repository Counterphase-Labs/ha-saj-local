[en](../../en-gb/developer/releasing.md) | [de](../../de/developer/releasing.md) | [nl](../../nl/developer/releasing.md) | [fr](../../fr/developer/releasing.md) | zh | [es](../../es/developer/releasing.md) | [it](../../it/developer/releasing.md) | [pl](../../pl/developer/releasing.md) | [sv](../../sv/developer/releasing.md)

# 发布

发布之前要做什么、发布如何公布，以及 Home Assistant 版本如何升级。推送版本标签会启动 `.github/workflows/release.yml` 中的 `Release` 工作流，该工作流检查标签、运行检查并创建 GitHub 发布草稿。

## 版本

发布是基于 `main` 上的版本标签制作的 GitHub 发布。标签没有 `v` 前缀，并且与 `custom_components/saj_local/manifest.json`、`pyproject.toml` 和 `frontend/package.json` 中的版本相同。稳定版为 `X.Y.Z`，测试版为 `X.Y.ZbN`，作为 GitHub 预发布版公布。第一个稳定版之前的测试版是 `1.0.0b1`、`1.0.0b2` 等等，第一个稳定版是 `1.0.0`，从 `1.0.0` 起适用语义化版本。发布说明只保存在 GitHub 发布中，测试版的说明要列出自上一个测试版以来对实体、已存储的设置、卡片类型或卡片设置的每一项更改。项目需求的 [发布](../../../.github/work/requirements.md#releases) 一节保存该规则。

## 发布之前

在 `main` 上按顺序执行下列步骤。

1. **运行 `make ci`。** [检查页面](checks.md)列出 `make ci` 运行什么。
2. **运行 `make docs-images`。** 用户文档显示界面，而 CI 不会重新生成图片，因此每次发布都需要一套新的图片。该目标需要 Docker。运行该目标，查看每一张改变的图片，提交 `docs/images/en-gb/` 中改变的图片，并运行 `make docs-check`。失败的运行不会写入任何图片，因此不要在运行失败的情况下发布。请阅读[截图](documentation.md#截图)，了解这次运行做什么，以及为什么图片中的每个读数都是模拟的。
3. **仅限维护者：更新站点截图。** 项目网站显示 `docs/images/en-gb/cards-power-flow-card.png` 的副本。请在同一步骤中更新该副本。本仓库中没有任何检查能发现过时的副本。
4. **运行 `make release-check`。** 该步骤用 `custom_components/saj_local/` 制作压缩包，当压缩包缺少 `asset-manifest.json`、构建出的卡片包或 `THIRD_PARTY_LICENSES.md`（卡片包中各库的许可证）时失败。卡片发生变化时，请先运行 `make build` 并提交该包和许可证文件。
5. **设置新版本。** 在 `custom_components/saj_local/manifest.json`、`pyproject.toml` 和 `frontend/package.json` 中设置版本。运行 `uv lock`，使 `uv.lock` 记录项目版本，并在 `frontend/` 中运行 `npm install --package-lock-only`，使 `frontend/package-lock.json` 记录该版本。运行 `make release-check`，提交到 `main`，并等待 CI 通过。

发布 `1.0.0` 时，还要移除预发布状态：每种语言中 `README.md` 和 `docs/<code>/README.md` 的状态行，以及 `docs/<code>/user/README.md` 和 `docs/<code>/user/installation.md` 中关于稳定版本的第一句。为 `1.0.0` 之后的测试版重写 `installation.md` 的测试版一节。

截图是发布中唯一 CI 无法检查的部分。增加或删除图片的更改会通过未使用图片规则和缺失图片规则使 `make docs-check` 失败。使某张图片过时的界面更改不会使任何检查失败，因此保持图片最新的是第 2 步。

## 公布发布

1. 推送标签：`git tag 1.0.0b1`，然后 `git push origin 1.0.0b1`。
2. 等待 `Release` 工作流。该工作流要求带标签的提交在 `main` 上，通过 `ci.yml` 运行 `make ci`，并用 GitHub 生成的说明创建发布草稿。
3. 打开发布草稿并编辑生成的说明。对于测试版，请列出自上一个测试版以来对实体、已存储的设置、卡片类型或卡片设置的每一项更改。
4. 点击“发布”。

失败的运行不会生成草稿。请用 `git push origin :refs/tags/<tag>` 和 `git tag -d <tag>` 删除标签，修复 `main`，然后重新打标签。

HACS 向开启了“显示测试版”的用户提供已公布的测试版，向所有用户提供已公布的稳定版。没有开启该开关的用户，在 `1.0.0` 存在之前得到的是 `main` 的最新提交，这就是 `main` 在每次推送之前都必须通过 `make ci` 的原因。

## 升级 Home Assistant 版本

Home Assistant 版本固定在多个文件中，这些文件必须一起更新，否则开发容器、浏览器测试和截图运行、CI、HACS 与测试框架会各自偏离：

1. `compose.yaml`：`ghcr.io/home-assistant/home-assistant:<X.Y.Z>`，即开发用的 Home Assistant 运行环境。
2. `Dockerfile.playwright-home-assistant`：`make test-browser-home-assistant` 和 `make docs-images` 所用镜像的 `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` 行。
3. `pyproject.toml`，`[dependency-groups] dev`：用于 CI lint 和 mypy 的 `homeassistant==<X.Y.Z>`，**以及** `pytest-homeassistant-custom-component==<matching release>`。该测试框架自带固定版本的 `homeassistant`，因此两个固定版本必须来自同一个 Home Assistant 发布，否则 lint 和测试会解析出不同的内核。
4. `hacs.json`：`"homeassistant": "<X.Y.Z>"`，即 HACS 强制要求的最低 Home Assistant 内核。
5. `uv.lock`：编辑 `pyproject.toml` 之后运行 `uv lock`，使锁文件记录新的固定版本。

提交之前请在 PyPI 上核对配对：`pytest-homeassistant-custom-component` 的 `requires_dist` 必须列出与 `pyproject.toml` 中固定的相同的 `homeassistant==<X.Y.Z>`。

升级之后，请运行 `make ci` 和 `make docs-images`，因为新的 Home Assistant 版本可能改变图片所显示的界面。
