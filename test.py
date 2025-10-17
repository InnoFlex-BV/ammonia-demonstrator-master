import paho.mqtt.client as mqtt
import random
import time

broker_ip = "127.0.0.1"  # Master's broker

client = mqtt.Client("MasterPublisher")
client.connect(broker_ip, 1883, 60)

try:
    while True:
        fan_value = random.randint(0, 5)
        client.publish("master/inlet/fan1", fan_value)
        #print(f"[Master] Published: {fan_value}")
        time.sleep(2)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.disconnect()
