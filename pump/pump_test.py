import time
import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_client
from pump.pump_control import PumpControll


mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
ammonia_pump = None



try:

    """  initializations of devices """

    ammonia_pump = PumpControll(slave_address=20, mqtt_topic = "master/inlet/ammonia_pump", client = mqtt_client)
    ammonia_pump.pump_initialzation()
    time.sleep(1)

    """  start multi thread """
    tasks = [
        {"func": ammonia_pump.pump_control, "interval": 5, "next_run": 0},
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
    if ammonia_pump is not None:
        try:
            ammonia_pump.pump_stop()
        except Exception as e:
            print(f"Error stopping pump: {e}")

    print("All devices cleaned up.")