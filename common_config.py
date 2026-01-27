import minimalmodbus
import paho.mqtt.client as mqtt
import threading
import serial
import time


serial_lock = threading.Lock()

# Configuration
BROKER_IP = "127.0.0.1"
BROKER_PORT = 1883
PORT = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B001G7E1-if00-port0"

# Shared state
devices = {}
_mqtt_client = None


def create_client():
    """Create or return the shared MQTT client with error handling."""
    global _mqtt_client
    if _mqtt_client is None:
        try:
            _mqtt_client = mqtt.Client(client_id="InletPi")
            _mqtt_client.connect(BROKER_IP, BROKER_PORT, 60)
            print(f"[MQTT] Connected to broker at {BROKER_IP}:{BROKER_PORT}")
        except Exception as e:
            print(f"[MQTT] Failed to connect to broker: {e}")
            raise
    return _mqtt_client


def create_device(slave_address):
    """Create or return a cached Modbus device for the given slave address."""
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