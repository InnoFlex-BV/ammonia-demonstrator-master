from common_config import create_device, create_client, clear_RS485, serial_lock
import numpy as np
import time

def read_sensor(client = None):
    device = create_device(slave_address=2)
    if client is None:
        client = create_client()
    
    with serial_lock:
        clear_RS485(device=device)
        values = np.array(device.read_registers(registeraddress=0x0000, number_of_registers=2, functioncode=3))
        clear_RS485(device=device)

    time.sleep(0.1)
    values = values*5/4095 # turn analog into 0-5V voltage
    values = (values - 0.6)*100/2.4 # and caliberate into ppm
    gas1 = values[0]
    gas2 = values[1]
    client.publish("master/inlet/ammonia1", gas1)
    client.publish("master/inlet/ammonia2", gas2)
    print(f"[ReadGas] gas1: {gas1:1f}, gas2: {gas2:1f}")



