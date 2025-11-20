import time
from common_config import create_client
from sensor.read_gas import read_sensor as read_gas
from sensor.read_HG803 import read_sensor as read_HG803
from fan.fan_control import FanControll
from heater.relay_control import RelayControl


mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
fan_in = None
heater_relay = None



try:

    """  initializations of devices """
    fan_in = FanControll(slave_address=4, mqtt_topic="master/inlet/fan_in", client = mqtt_client)
    fan_in.fan_initialzation()
    time.sleep(1)

    heater_relay = RelayControl(slave_address=5, mqtt_topic = "master/inlet/heater_relay", client = mqtt_client)
    heater_relay.relay_initialization()
    time.sleep(1)

    """  start multi thread """
    tasks = [
        {"func": lambda: read_gas(client=mqtt_client), "interval": 2, "next_run": 0},
        {"func": lambda: read_HG803(client=mqtt_client), "interval": 3, "next_run": 0},
        
        {"func": heater_relay.relay_control, "interval": 4, "next_run": 0},
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

    if heater_relay is not None:
        try:
            heater_relay.relay_close()
        except Exception as e:
            print(f"Error closing heater relay: {e}")

    print("All devices cleaned up.")