import json
import os

import time
from common_config import create_device, create_client
from sensor.read_HG803 import read_sensor as read_HG803
from fan.fan_control import FanControl
from fan.fan_auto_control import FanAutoControl
from heater.relay_control import RelayControl
from pump.pump_control import PumpControl
import hotend.PIDcontroller_control
from powermeter.read_powermeter import read_power



def load_devices_config(file_path = "./test/devices_config.json"):
    default_config = {
        "Inlet_Fan": False,
        "Heater": False,
        "HG803": False,
        "Pump": False,
        "Hot-end": False,
        "Powermeter":False
    }
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading config: {e}")
    return default_config


devices_config = load_devices_config("/home/innoflex/ammonia-demonstrator-master/test/devices_config.json")
print("Current Device Configuration:", devices_config)


mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
fan_in = None
heater_relay = None
ammonia_pump = None
HG803_sensor = create_device(slave_address=3)
hotend_controller = create_device(slave_address=25)
Powermeter = create_device(slave_address=60)



try:

    tasks = []

    """  initializations of devices """
    if devices_config.get("Inlet_Fan"):
        fan_in = FanControl(slave_address=4, mqtt_topic="master/inlet/fan_in_manual", client = mqtt_client)
        fan_in.fan_initialization()
        time.sleep(0.5)
        fan_controller = FanAutoControl(sp_flowrate=250, client=mqtt_client)
        time.sleep(0.5)
        tasks.append({"name": "Inlet Fan", "func": fan_in.fan_control, "interval": 5, "next_run": 0})

    if devices_config.get("Heater"):
        heater_relay = RelayControl(slave_address=5, mqtt_topic = "master/inlet/heater_relay", client = mqtt_client)
        heater_relay.relay_initialization()
        time.sleep(1)
        tasks.append({"name": "Heater Relay", "func": heater_relay.relay_control, "interval": 5, "next_run": 0})

    if devices_config.get("Pump"):
        ammonia_pump = PumpControl(slave_address=20, mqtt_topic = "master/inlet/ammonia_pump", client = mqtt_client)
        ammonia_pump.pump_initialzation()
        time.sleep(1)
        tasks.append({"name": "Peristaltic Pump", "func": ammonia_pump.pump_control, "interval": 5, "next_run": 0})

    """  set up hot-end """
    if devices_config.get("Hot-end"):
        hotend.PIDcontroller_control.controller_initialization(hotend_controller)
        hotend.PIDcontroller_control.controller_setup(device=hotend_controller, SV=85, K_p=5, K_i=10, K_d=9, T=0.2, AR=50)
        time.sleep(0.5)
        tasks.append({"name": "Hot-end", "func": lambda: hotend.PIDcontroller_control.controller_read_status(device=hotend_controller, client=mqtt_client, mqtt_topic="master/inlet/hotend_temperature"), "interval": 15, "next_run": 0})
    
    if devices_config.get("HG803"):
        tasks.append({"name": "HG803 Sensor", "func": lambda: read_HG803(device=HG803_sensor, client=mqtt_client), "interval": 10, "next_run": 0})

    if devices_config.get("Powermeter"):
        tasks.append({"name": "Powermeter", "func": lambda: read_power(device=Powermeter, client=mqtt_client), "interval": 30, "next_run": 0})

    print("Tasks checklist OVER")

    # """  start multi thread """

    while True:
        if not tasks:
            print("No tasks enabled. Sleeping...")
            time.sleep(5)
            continue

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
    hotend.PIDcontroller_control.controller_checkout(device=hotend_controller)
    hotend.PIDcontroller_control.controller_stop(device=hotend_controller)

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
       
    if ammonia_pump is not None:
        try:
            ammonia_pump.pump_stop()
        except Exception as e:
            print(f"Error stopping pump: {e}")


    # Cleanup MQTT client (only once, after all devices are stopped)
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("All devices cleaned up.")