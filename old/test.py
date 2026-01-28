import random
import time

def read_sensor():
        t0 = time.time()
        test_value = random.randint(0, 5)
        #random_value = random.choice([True, False])
        #test_value = "true" if random_value else "false"
        print(f"random number generate time: [{time.time() - t0:.3f}s]")
        print(f"[Test] Published: {test_value}")