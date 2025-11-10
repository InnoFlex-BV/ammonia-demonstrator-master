import paho.mqtt.client as mqtt
import random
import time

broker_ip = "127.0.0.1"  # Master's broker

client = mqtt.Client(client_id="Test")
client.connect(broker_ip, 1883, 60)

interval = 2
next_run = time.time()

try:
    while True:
        now = time.time()
        if now>= next_run:
            test_value = random.randint(0, 5)
        #random_value = random.choice([True, False])
        #test_value = "true" if random_value else "false"
            client.publish("master/inlet/heater_relay", test_value)
            print(f"[Master] Published: {test_value}")
            next_run = now + interval
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.disconnect()
