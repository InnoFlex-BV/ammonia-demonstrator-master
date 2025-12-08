from common_config import create_device, create_client, clear_RS485, serial_lock
import time

def read_temp(client = None):
    device = create_device(slave_address=2)
    if client is None:
        client = create_client()
    
    with serial_lock:
        clear_RS485(device=device)
        value = device.read_register(registeraddress=0x0000, functioncode=3)
        clear_RS485(device=device)

    time.sleep(0.1)
    temp = value
    print(f"[Hot-End] Temperature: {temp:1f}")
