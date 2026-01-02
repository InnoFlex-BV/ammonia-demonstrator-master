from common_config import serial_lock, create_client, clear_RS485, strong_clear_RS485
import minimalmodbus
import time



def controller_initialization(device:minimalmodbus.Instrument):
    with serial_lock:
        device.write_register(registeraddress=0x0009, value=0, functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x000A, value=0, functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x000B, value=0, functioncode=6)
        time.sleep(0.1)
    print("[HotEndControl] Hot End initialized.")

def controller_setup(device:minimalmodbus.Instrument, 
                     SV = None, 
                     K_p = None, 
                     K_i = None, 
                     K_d = None,
                     T = None, # Control cycle
                     AR = None): # Integral limit [%]
    with serial_lock:
        device.write_register(registeraddress=0x0002, value=SV, functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x0009, value=K_p, functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x000A, value=K_i, functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x000B, value=K_d, functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x000D, value=round(T*0.5), functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x000C, value=AR, functioncode=6)
        time.sleep(0.1)
        device.write_register(registeraddress=0x0004, value=True, functioncode=6) # turn on self-tuning of PID parameters
        time.sleep(0.1)
    print("[HotEndControl] Hot End control parameter set.")


def controller_read_status(device:minimalmodbus.Instrument,
                          client = None,
                          mqtt_topic = None):
    if client is None:
        client  =create_client()
    with serial_lock:
        clear_RS485(device)
        data = device.read_register(registeraddress=0x0000, functioncode=3)
        output = device.read_register(registeraddress=0x0003, functioncode=3)
        clear_RS485(device)
    time.sleep(0.1)
    client.publish(mqtt_topic, data)
    print(f"[HotEndControl] Hot End temperature {data} degree. Hot End output: {output}%.")
    return data


def controller_checkout(device: minimalmodbus.Instrument):
    with serial_lock:
        clear_RS485(device)
        Pp = device.read_register(registeraddress=0x0009, functioncode=3)
        Ii = device.read_register(registeraddress=0x000A, functioncode=3)
        Dd = device.read_register(registeraddress=0x000B, functioncode=3)
        Tt = device.read_register(registeraddress=0x000D, functioncode=3)
        print(f"P: {Pp}, I: {Ii}, D: {Dd}, T: {Tt}")


def controller_stop(device: minimalmodbus.Instrument):
    with serial_lock:
        strong_clear_RS485(device)
        device.write_register(registeraddress=0x0004, value=False, functioncode=6) # turn off self-tuning
        time.sleep(0.1)
        device.write_register(registeraddress=0x0009, value=0, functioncode=6) # K_p=0 --> stop PID control
        strong_clear_RS485(device)
    print("[HotEndControl] Hot End has been turned off.")
