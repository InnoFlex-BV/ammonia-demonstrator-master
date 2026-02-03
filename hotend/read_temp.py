import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_device, create_client, clear_RS485, serial_lock
import time

def read_temp():
    device = create_device(slave_address=25)
    
    with serial_lock:
        clear_RS485(device=device)
        # value = device.read_register(registeraddress=0x0000, functioncode=3)
        value = device.read_registers(registeraddress=0x0009, number_of_registers=5, functioncode=3)
        clear_RS485(device=device)

    time.sleep(0.1)
    print(f"[Hot-End] Temperature: {value} degree.")


if __name__ == "__main__":
    read_temp()
