DOMAIN = "saj_local"
INTEGRATION_TITLE = "SAJ Local"
DEFAULT_PORT = 502
MIN_UNIT_ID = 1
MAX_UNIT_ID = 247
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 30
REQUEST_TIMEOUT = 5
PLATFORMS = ("sensor",)
SENSOR_KEYS = (
    "operating_mode",
    "pv_power",
    "battery_power",
    "battery_soc",
    "grid_power",
    "load_power",
)
