import serial
import paho.mqtt.client as mqtt
import time
from calculate_crc import calc_crc


relay = serial.Serial('/dev/ttyUSB0', baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=1)

## setting for MQTT
broker_ip = "127.0.0.1"  # IP of Master
topic = "master/inlet/heater_relay"


def on_message(client, userdata, msg):
    global heater_relay
    payload_str = msg.payload.decode().strip().lower() # all string turn into lower case letters
    heater_relay = payload_str == "true"



client = mqtt.Client(client_id="MasterSubscriber", callback_api_version=1)
client.on_message = on_message
client.connect(broker_ip, 1883, 60)
client.subscribe(topic)
client.loop_start()



# turn on relay command
request_on = bytearray([0x05, 0x05, 0x00, 0x00, 0xFF, 0x00])
request_on += calc_crc(request_on)

# turn off relay command
request_off = bytearray([0x05, 0x05, 0x00, 0x00, 0x00, 0x00])
request_off += calc_crc(request_off)

## initialization
heater_relay = False
current_state=None

try:
    while True:
        if heater_relay != current_state:
            if heater_relay:
                relay.write(request_on)
                print(f"heater relay ON")
            else:
                relay.write(request_off)
                print(f"heater relay OFF")
            current_state = heater_relay
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program...")
    relay.write(request_off)

finally:
    relay.close()
    client.loop_stop()
    client.disconnect()
