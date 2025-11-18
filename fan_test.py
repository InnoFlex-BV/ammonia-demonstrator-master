import time
from common_config import create_client
from fan.fan_control import FanControll
#from test import read_sensor as read_random

mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
fan_in = None



try:

    """  initializations of devices """
    fan_in = FanControll(slave_address=4, mqtt_topic="master/inlet/fan_in", client = mqtt_client)
    fan_in.fan_initialzation()
    time.sleep(1)

    """  start multi thread """
    tasks = [
        {"func": fan_in.fan_control, "interval": 5, "next_run": 0},
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
    if fan_in is not None:
        try:
            fan_in.fan_stop()
        except Exception as e:
            print(f"Error stopping fan: {e}")

    print("All devices cleaned up.")