en | [de](../../de/user/protecting-the-inverter.md) | [nl](../../nl/user/protecting-the-inverter.md) | [fr](../../fr/user/protecting-the-inverter.md) | [zh](../../zh-hans/user/protecting-the-inverter.md) | [es](../../es/user/protecting-the-inverter.md) | [it](../../it/user/protecting-the-inverter.md) | [pl](../../pl/user/protecting-the-inverter.md) | [sv](../../sv/user/protecting-the-inverter.md)

# Protecting the inverter

The Protecting the inverter page lists the limits SAJ Local keeps on everything SAJ Local sends, so the communication module of the inverter keeps serving Home Assistant. A module can stop serving a client that polls too hard, so no setting removes a limit. The full list is in the [Protecting the inverter](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) section of the integration feature list.

## The limits

- **One connection, one request at a time.** SAJ Local opens one connection to an inverter and waits for each answer before sending the next request, with a short pause between requests.
- **40 requests in any 60 seconds.** The limit applies per inverter address. SAJ Local counts across reloads, so a reload, a setup retry or a connection check cannot exceed the limit. A request over the limit waits.
- **Neighbouring registers share a request.** SAJ Local reads registers that sit close together in one request, never beyond a block the model documents. A request is never larger than 32 registers on the HS3 or 56 on the H2. Grouping entities that sit together costs less, see [polling](polling.md).
- **No retries within a cycle.** After a failed read, the wait before the next attempt doubles from the shortest interval, up to 5 minutes. The wait survives reloads. The first good cycle reads everything again.
- **Every wait has a time limit.** A stalled inverter ends a cycle as a failure and does not stop polling. A late or stray answer is discarded.
- **A closed connection is reopened once.** That cycle then reads every enabled entity again, so no value is older than the reconnect.
- **Two kinds of register read.** SAJ Local reads holding registers (Modbus function 03) and input registers (function 04). The HS3 serves the EV charger readings as input registers. Both kinds count against the 40 requests, and a refusal of one kind never suspends the other.
- **At most 20 changes in 60 seconds.** See [changing settings](changing-settings.md#what-happens-to-a-change). A change over the limit is refused and not queued.

## When the inverter refuses a reading

A refusal is an answer and not a failure. Only the entities in the refused request become unavailable, and the others keep updating.

1. SAJ Local splits the refused request in halves over the next cycles, until the refused entity is found.
2. An entity refused three times in a row is suspended. The entity shows as unavailable and is no longer read.
3. SAJ Local tries a suspended entity again once a day, and whenever the integration loads. The entity comes back when the register answers.
4. A repair issue lists the suspended entities. The fix of the issue disables the entities, so SAJ Local no longer reads the entities for good. See [faults and repairs](faults-and-repairs.md#repair-issues).

## When the inverter stops answering

A repair issue says when an inverter has not answered for 15 minutes. The issue goes away at the first good reading. Check the power of the inverter and of the communication module, the network, and that no other Modbus client holds the connection.

## Not supported yet

- Changing the limits. The limits protect the inverter, so no setting raises a limit.
