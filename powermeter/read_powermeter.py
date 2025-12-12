from common_config import create_client, clear_RS485, serial_lock
import struct
import time

def read_power(device, client = None):
    if client is None:
        client = create_client()
    
    with serial_lock:
        clear_RS485(device)
        raw_values = device.read_registers(registeraddress=72, number_of_registers=4, functioncode=4)
        clear_RS485(device)

    time.sleep(0.1)
    import_bytes = struct.pack('>HH', raw_values[0], raw_values[1])
    export_bytes = struct.pack('>HH', raw_values[2], raw_values[3])
    total_import = struct.unpack('>f', import_bytes)[0]
    total_export = struct.unpack('>f', export_bytes)[0]

    client.publish("slave/powerbox/total_import", total_import)
    client.publish("slave/powerbox/total_export", total_export)
    print(f"[Powermeter] Total Import: {total_import} kWh; Total Export:L {total_export} kWh")
