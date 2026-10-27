[en](../../../en-gb/user/cards/status-badge.md) | [de](../../../de/user/cards/status-badge.md) | [nl](../../../nl/user/cards/status-badge.md) | [fr](../../../fr/user/cards/status-badge.md) | zh | [es](../../../es/user/cards/status-badge.md) | [it](../../../it/user/cards/status-badge.md) | [pl](../../../pl/user/cards/status-badge.md) | [sv](../../../sv/user/cards/status-badge.md)

# 状态徽章

“状态徽章”页面说明状态徽章，该徽章在仪表盘的徽章行中显示系统的状态。完整列表见卡片功能列表的 [状态徽章](../../../../frontend/docs/features.md#status-badge) 一节。[添加元素](README.md#添加元素)说明如何添加该徽章并选择系统。

![运行状态为“运行”的状态徽章](../../../images/zh-hans/cards-status-badge.png)

## 徽章显示什么

- 运行状态（按状态的健康程度着色），以及有当前故障的设备数量。只有当有故障时，徽章才显示该数量，因此截图只显示状态。
- 当系统不应答时，徽章显示“无响应”。
- 点按徽章会打开运行状态的详细信息。

## 选项

| 编辑器中的选项 | YAML 键 | 默认值 |
| --- | --- | --- |
| 系统 | `device` | 第一个系统 |

```yaml
type: custom:saj-local-status-badge
device: 0123456789abcdef0123456789abcdef
```

`device` 的值是 Home Assistant 中该设备的 ID。可视化编辑器会为你填入该值。

## 尚不支持

- 系统以外的选项。
