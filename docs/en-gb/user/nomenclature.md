en | [de](../../de/user/nomenclature.md) | [nl](../../nl/user/nomenclature.md) | [fr](../../fr/user/nomenclature.md) | [zh](../../zh-hans/user/nomenclature.md) | [es](../../es/user/nomenclature.md) | [it](../../it/user/nomenclature.md) | [pl](../../pl/user/nomenclature.md) | [sv](../../sv/user/nomenclature.md)

# Nomenclature

The terms that SAJ Local, the dashboard cards and the documentation use, each with a one-line meaning. Every translation of the integration, the cards and the documentation uses one term for each thing listed here. The [Languages](../../../custom_components/saj_local/docs/features.md#languages) section of the integration feature list names the languages that SAJ Local ships.

## SAJ equipment and readings

| Term | Meaning |
| --- | --- |
| Inverter | The SAJ unit that turns the solar and battery direct current into alternating current for the home and the grid. |
| HS3 | The SAJ HS3 hybrid inverter model, a three-phase model. |
| H2 | The SAJ H2 hybrid inverter model, a single-phase model. |
| Model | The inverter type SAJ Local uses to choose the register list: Automatic, HS3 or H2. |
| Automatic | The model choice that recognises the model from the device type the inverter reports. |
| Optional equipment | Equipment an installation may or may not have: a battery, Meter A, Meter B, an EV charger or a parallel system. |
| Fitted | The setting that tells SAJ Local that a piece of optional equipment is installed. |
| Not fitted | The setting that tells SAJ Local that a piece of optional equipment is not installed. |
| Battery | The energy storage connected to the inverter. |
| Battery pack | One battery module in a battery, shown as Pack followed by a number. |
| State of charge | How full the battery is, as a percentage. |
| Reserve | The battery charge the inverter keeps back and does not discharge below. |
| Solar | The power produced by the solar panels. |
| Solar string | One group of solar panels wired in series and connected to one input of the inverter. |
| Phase | One conductor of the alternating current supply. |
| Grid | The public electricity network the home is connected to. |
| Importing | Taking power from the grid. |
| Exporting | Sending power to the grid. |
| Charging | Putting power into the battery. |
| Discharging | Taking power out of the battery. |
| Home | The power the home uses. |
| Backup load | The loads that stay powered from the battery and the solar panels when the grid fails. |
| Meter A | The first electricity meter that can be connected to the inverter. |
| Meter B | The second electricity meter that can be connected to the inverter. |
| EV charger | An electric vehicle charger that is connected to the inverter. |
| Parallel system | Several inverters working together as one system. |
| Fault | A problem that the equipment reports, with a register and a bit. |
| Clear fault | The button that asks the inverter to clear a reported fault. |
| Operating state | The state the inverter is in, such as running or standby. |
| Mode | The operating mode of the inverter, such as time-of-use. |
| Time-of-use | The mode in which the battery charges and discharges in the slots you set. |
| Slot | One time period of the time-of-use schedule for charging, discharging or the EV charger. |
| EMS | The energy management system functions of the inverter, which hold a power target from outside. |
| EMS heartbeat | How often SAJ Local reads the EMS targets to keep the EMS functions alive. |
| EMS timeout | The time after which the inverter ends an EMS function that is not kept alive. |
| Reverse-current protection | The inverter protection against power flowing back into the inverter, which the EMS functions switch off. |
| Power control | Holding the battery, the grid connection or the inverter at a set power. |
| Power target | The power that a power control function holds. |
| Schedule | The times at which a power control function runs. |
| Allow control | The setting that lets Home Assistant change the settings of the inverter. |
| Control | The ability to change the settings of the inverter, as opposed to only reading it. |
| Register | A numbered memory location of the inverter that holds one reading or setting. |
| Refused register | A register that the inverter refuses to answer. |
| Modbus TCP | The network protocol SAJ Local uses to talk to the inverter. |
| Host | The network address of the inverter. |
| Port | The network port of the inverter, 502 by default. |
| Unit ID | The Modbus address of the inverter, from 1 to 247. |
| Communication module | The part of the inverter that answers network requests. |
| Block | A range of registers that is read with one request. |
| Realtime | The block of readings that change from second to second. |
| Five-minute averages | The block of readings that the inverter averages over five minutes. |
| Energy | The block of readings of energy produced and used, such as today's energy. |
| Identity | The model, serial number and versions the inverter reports. |

## SAJ Local concepts

| Term | Meaning |
| --- | --- |
| System | One inverter, with its equipment, added to Home Assistant. |
| Installation | One SAJ Local config entry, which is one system. |
| Prefix | Optional text added to the entity IDs of one installation, used when there is more than one system. |
| Polling | Reading the inverter at intervals. |
| Polling group | A chosen set of entities that SAJ Local reads faster or slower than the default interval. |
| Update interval | The seconds between two reads of the inverter, shown as "Seconds between updates". |
| Request load | The number of requests per minute that SAJ Local sends the inverter, against the limit of 40 in 60 seconds. |
| Budget | The limit on the request load. |
| Model replacement | Moving a system to a new inverter, or between an H2 and an HS3, and keeping the history. |
| Unverified | A model that was chosen by hand and could not be checked against the device type. |
| Diagnostics download | The file that holds a privacy-safe snapshot of the system for a bug report. |
| Debug logging | The option that writes detailed log lines for finding a problem. |
| Dashboard card | A card that SAJ Local adds to Home Assistant dashboards. |
| Power flow card | The card that shows live power between solar, battery, grid and home. |
| Status card | The card that shows the operating state, the mode, key readings and faults. |
| Faults card | The card that lists the active faults. |
| Battery card | The card that shows the battery readings and one row per pack. |
| Controls card | The card that shows the shared controls of the system. |
| Schedule card | The card that shows the slots with a week timeline. |
| Weekdays tile card feature | The seven day buttons that can be added to a tile card. |
| Status badge | The badge that shows the operating state and the number of active faults. |

## Home Assistant concepts

| Term | Meaning |
| --- | --- |
| Home Assistant | The home automation software that SAJ Local is an integration of. |
| Integration | Software that connects a kind of device or service to Home Assistant. |
| HACS | The Home Assistant Community Store, used to install SAJ Local. |
| Custom repository | A repository that is not in the HACS default list, added to HACS by its address; the HACS Custom badge in the READMEs marks SAJ Local as one. |
| Config flow | The setup dialogue that adds a system. |
| Config entry | The saved setup of one system. |
| Subentry | A part of a config entry that is added and changed on its own, such as a polling group or a power schedule. |
| Configure | The button of an integration that opens its options. |
| Devices & services | The Home Assistant settings page that lists integrations, devices and entities. |
| Settings | The Home Assistant page for configuring Home Assistant. |
| Device | The Home Assistant record of one piece of equipment that holds entities. Each system is one device. |
| Entity | One reading, setting or command that Home Assistant shows. |
| Entity ID | The unique identifier of an entity, such as sensor.saj_pv_power. |
| Sensor | An entity that shows a reading. |
| Binary sensor | An entity that is either on or off, such as a fault. |
| Number | An entity that holds a number you can change. |
| Select | An entity that holds one choice from a list. |
| Switch | An entity that you can turn on or off. |
| Time | An entity that holds a time of day. |
| Button | An entity that runs an action when pressed. |
| Enabled by default | Whether an entity is switched on when the system is added. |
| Disabled | An entity that Home Assistant does not read or show. |
| Repair issue | A notice in Home Assistant that something needs your action, with a Fix button. |
| Dashboard | A Home Assistant screen made of cards. |
| Card | One block on a dashboard. |
| Tile card | A Home Assistant card that shows one entity, and that can have features added. |
| Badge | A small item in the badge row at the top of a dashboard. |
| Automation | A rule that makes Home Assistant act when something happens. |
| Helper | A Home Assistant entity that you create yourself, such as a schedule helper. |
| Area | A room or place that devices are grouped in. |
| Theme | The colours of the Home Assistant interface. |
| Language | The language that a Home Assistant user chooses on the profile page. |
| Reload | Restarting one integration without restarting Home Assistant. |
| Restart | Restarting Home Assistant. |
| Developer tools | The Home Assistant pages for checking states and calling actions. |
| Log | The Home Assistant record of messages. |
