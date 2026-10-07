DEVICE_TYPE_WIDTH = 6


def format_device_type(device_type: int) -> str:
    return f"{device_type:#0{DEVICE_TYPE_WIDTH}x}"
