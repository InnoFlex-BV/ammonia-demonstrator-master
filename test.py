import paho.mqtt.client as mqtt
import random
import time

broker_ip = "127.0.0.1"  # Master's broker

client = mqtt.Client(client_id="MasterPublisher")
client.connect(broker_ip, 1883, 60)

try:
    while True:
        test_value = random.randint(0, 5)
        client.publish("master/test", test_value)
        print(f"[Master] Published: {test_value}")
        time.sleep(2)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.disconnect()
