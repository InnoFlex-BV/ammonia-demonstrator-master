from common_config import create_client, clear_RS485, serial_lock
import minimalmodbus
import struct
import time

def read_power(device: minimalmodbus.Instrument,
               client=None):
    if client is None:
        client = create_client()
    
    try:
        with serial_lock:
            clear_RS485(device)
            current = device.read_float(registeraddress=6, number_of_registers=2, functioncode=4)
            current = round(current, 2)
            active_power = device.read_float(registeraddress=12, number_of_registers=2, functioncode=4)
            active_power = round(active_power, 2)
            clear_RS485(device)
    except Exception as e:
        print(f"[Powermeter] Error -> {type(e).__name__}: {e}")

    client.publish("slave/powerbox/active_power", active_power)
    client.publish("slave/powerbox/current", current)
    print(f"[Powermeter] Active power: {active_power} W; Current: {current} A")
