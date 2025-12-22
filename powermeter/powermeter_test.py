import time
import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_device, create_client
from read_powermeter import read_power


mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
powermeter = create_device(slave_address=60)



try:

    """  initializations of devices """



    """  start multi thread """
    tasks = [
        {"func": lambda: read_power(device=powermeter, client=mqtt_client), "interval": 3, "next_run": 0},
    ]


    while True:
        now = time.time()
        for t in tasks:
            if now  >= t["next_run"]:
                t["func"]()
                t["next_run"] = now + t["interval"]
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n Exiting programm due to keyboard interrupt...")

except Exception as e:
    print(f"\nExiting program due to error: {e}")

finally:
    # cleanup all devices in RS485

    print("All devices cleaned up.")