import time
import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_client
from heater.relay_control import RelayControl



mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
heater_relay = None



try:

    """  initializations of devices """
    heater_relay = RelayControl(slave_address=5, mqtt_topic = "master/inlet/heater_relay", client = mqtt_client)
    heater_relay.relay_initialization()
    time.sleep(1)


    """  start multi thread """
    tasks = [
        {"name": "Heater Relay", "func": heater_relay.relay_control, "interval": 4, "next_run": 0},     
        # {"name": "Powermeter", "func": lambda: read_power(device=Powermeter, client=mqtt_client), "interval": 5, "next_run": 0}, 
    ]


    while True:
        now = time.time()
        for t in tasks:
            if now  >= t["next_run"]:
                try:
                    t["func"]()
                except Exception as e:
                    print(f"Error in [{t['name']}]. Task {t['func'].__name__} error: {e}")
                t["next_run"] = now + t["interval"]
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n Exiting programm due to keyboard interrupt...")

except Exception as e:
    print(f"\nExiting program due to error: {e}")

finally:
    # cleanup all devices in RS485

    if heater_relay is not None:
        try:
            heater_relay.relay_close()
        except Exception as e:
            print(f"Error closing heater relay: {e}")


    print("All devices cleaned up.")