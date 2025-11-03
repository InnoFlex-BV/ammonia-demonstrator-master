import paho.mqtt.client as mqtt
import minimalmodbus
import serial
import time

## setting for RS485
device = minimalmodbus.Instrument('/dev/ttyUSB0', 3)
device.serial.baudrate = 9600
device.serial.bytesize = 8
device.serial.parity = serial.PARITY_NONE
device.serial.stopbits = 1
device.serial.timeout = 0.5
device.mode = minimalmodbus.MODE_RTU


## setting for MQTT
broker_ip = "127.0.0.1"  # Master's broker
client = mqtt.Client(client_id="MasterPublisher")
client.connect(broker_ip, 1883, 60)



try:
    while True:
        values = device.read_registers(registeraddress=0x0000, number_of_registers=2, functioncode=3)
        gas1 = values[0]*5/4095 # turn analog into 0-5V voltage
        gas2 = values[1]*5/4095
        client.publish("master/inlet/ammonia1", gas1)
        client.publish("master/inlet/ammonia2", gas2)
        print(f"gas1: {gas1:1f}, gas2: {gas2:1f}")
        time.sleep(2)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.disconnect()



