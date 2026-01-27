from common_config import create_client, clear_RS485,serial_lock
import time


def read_sensor(device, client=None):
    if client is None:
        client = create_client()

    with serial_lock:
        clear_RS485(device)
        data = device.read_registers(registeraddress=0x0000, number_of_registers=2, functioncode=3)
        clear_RS485(device)

    time.sleep(0.1)  # avoid conflict with other devices in RS485 communication

    # Validate data has expected length
    if len(data) < 2:
        print(f"[ReadHG803] Error: Expected 2 registers, got {len(data)}")
        return

    temperature = data[0] / 100  # sensor data type = magnified 100 times
    humidity = data[1] / 100
    client.publish("master/inlet/temperature", temperature)
    client.publish("master/inlet/humidity", humidity)
    print(f"[ReadHG803] Temperature: {temperature} degree, Humidity: {humidity} %")