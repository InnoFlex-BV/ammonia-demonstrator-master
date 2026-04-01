from common_config import create_client, clear_RS485,serial_lock
import time


def read_sensor(device, client=None):
    if client is None:
        client = create_client()

    with serial_lock:
        clear_RS485(device)
        pressure_difference = device.read_float(registeraddress=0x0016, functioncode=3)
        clear_RS485(device)

    time.sleep(0.1)  # avoid conflict with other devices in RS485 communication

    # pressure_difference = data
    client.publish("master/inlet/pressure_difference", pressure_difference)
    print(f"[Diff P Sensor] Pressure different: {pressure_difference} Pa")