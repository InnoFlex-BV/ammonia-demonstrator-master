import minimalmodbus
import paho.mqtt.client as mqtt
import threading
import serial
import time


serial_lock = threading.Lock()


# initialize MQTT client
broker_ip = "127.0.0.1"
common_client = mqtt.Client(client_id="InletPi")
common_client.connect(broker_ip, 1883, 60)

PORT = "/dev/ttyUSB0"

devices = {}

def create_device(slave_address):
    if slave_address in devices:
        return devices[slave_address]
    common_device = minimalmodbus.Instrument(PORT, slave_address)
    common_device.serial.baudrate = 9600
    common_device.serial.bytesize = 8
    common_device.serial.parity = minimalmodbus.serial.PARITY_NONE
    common_device.serial.stopbits = 1
    common_device.serial.timeout = 0.5
    common_device.mode = minimalmodbus.MODE_RTU

    devices[slave_address] = common_device
    return common_device

def create_client():
    return common_client


def clear_RS485(device: minimalmodbus.Instrument):
    try:
        device.serial.reset_input_buffer()
        device.serial.reset_output_buffer()
    
    except Exception as e:
        print(f"clear RS485 warning: {e}")


def strong_clear_RS485(device: minimalmodbus.Instrument):
    try:
        device.serial.reset_input_buffer()
        device.serial.reset_output_buffer()

        device.serial.write(b'\xFF' * 4)
        time.sleep(0.05) 
        
    except Exception as e:
        print(f"Strong clear RS485 warning: {e}")