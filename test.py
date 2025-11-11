import random
import time

def read_sensor():
        test_value = random.randint(0, 5)
        #random_value = random.choice([True, False])
        #test_value = "true" if random_value else "false"
        print(f"[Master] Published: {test_value}")
        time.sleep(0.01)