import minimalmodbus
import paho.mqtt.client as mqtt

def create_device(port = "/dev/ttyUSB0", slave_address = 1, broker_ip = "127.0.0.1"):
    # initialiation of RS485 device
    device = minimalmodbus.Instrument(port, slave_address)
    device.serial.baudrate = 9600
    device.serial.parity = minimalmodbus.serial.PARITY_NONE
    device.serial.stopbits = 1
    device.serial.bytesize = 8
    device.serial.timeout = 0.5
    device.mode = minimalmodbus.MODE_RTU

    # initialization of MQTT
    client = mqtt.Client(client_id="InletPi")
    client.connect(broker_ip, 1883, 60)
    return device, client
