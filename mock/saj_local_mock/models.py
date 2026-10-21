import dataclasses

HS3 = "hs3"
H2 = "h2"
MAX_PV_STRINGS = 4


@dataclasses.dataclass(frozen=True, slots=True)
class ModelSpec:
    name: str
    device_type: int
    rated_powers_w: tuple[int, ...]
    default_rated_power_w: int
    phases: int
    max_battery_modules: int
    supports_ev_charger: bool
    battery_pack_voltage_v: float
    battery_protocol_setting: int
    battery_protocol_active: int
    default_serial_number: str
    max_fault_packs: int


MODELS: dict[str, ModelSpec] = {
    HS3: ModelSpec(
        name=HS3,
        device_type=0x1610,
        rated_powers_w=(5000, 6000, 8000, 10000, 12000),
        default_rated_power_w=12000,
        phases=3,
        max_battery_modules=8,
        supports_ev_charger=True,
        battery_pack_voltage_v=444.0,
        battery_protocol_setting=24,
        battery_protocol_active=24,
        default_serial_number="HS3MOCK0000000000001",
        max_fault_packs=1,
    ),
    H2: ModelSpec(
        name=H2,
        device_type=0x005A,
        rated_powers_w=(3000, 3680, 4000, 5000, 6000),
        default_rated_power_w=6000,
        phases=1,
        max_battery_modules=5,
        supports_ev_charger=False,
        battery_pack_voltage_v=51.2,
        battery_protocol_setting=22,
        battery_protocol_active=13,
        default_serial_number="H2MOCK00000000000001",
        max_fault_packs=4,
    ),
}
