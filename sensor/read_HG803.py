import paho.mqtt.client as mqtt
import minimalmodbus
import serial
from time import sleep


## settings for RS485
HG803 = minimalmodbus.Instrument('/dev/ttyUSB0',3)
HG803.serial.baudrate = 9600
HG803.serial.bytesize = 8
HG803.serial.parity = minimalmodbus.serial.PARITY_NONE
HG803.serial.stopbits = 1
HG803.serial.timeout  = 0.5
HG803.mode = minimalmodbus.MODE_RTU


## settings for MQTT
broker_ip = "127.0.0.1"  # Master's broker
client = mqtt.Client(client_id="MasterPublisher")
client.connect(broker_ip, 1883, 60)



try:
    while True:
        data = HG803.read_registers(registeraddress=0x0000, number_of_registers=2, functioncode=3)
        temperature = data[0]/100 # sensor data type = magnified 100 times
        humidity = data[1]/100
        client.publish("master/inlet/temperature", temperature)
        client.publish("master/inlet/humidity", humidity)
        print(f"Temperature: {temperature} degree, Humidity: {humidity} %")
        sleep(2)


except KeyboardInterrupt:
    print("\nProgram interrupted by user. Exiting...")
finally:
    client.disconnect()
