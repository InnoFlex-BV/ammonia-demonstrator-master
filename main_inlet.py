import time
from common_config import create_device, create_client
from sensor.read_HG803 import read_sensor as read_HG803
from fan.fan_control import FanControll
from heater.relay_control import RelayControl
from pump.pump_control import PumpControll
import hotend.PIDcontroller_control
# from powermeter.read_powermeter import read_power



mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
fan_in = None
heater_relay = None
ammonia_pump = None
HG803_sensor = create_device(slave_address=3)
hotend_controller = create_device(slave_address=25)
# Powermeter = create_device(slave_address=60)



try:

    """  initializations of devices """
    fan_in = FanControll(slave_address=4, mqtt_topic="master/inlet/fan_in", client = mqtt_client)
    fan_in.fan_initialzation()
    time.sleep(1)

    heater_relay = RelayControl(slave_address=5, mqtt_topic = "master/inlet/heater_relay", client = mqtt_client)
    heater_relay.relay_initialization()
    time.sleep(1)

    ammonia_pump = PumpControll(slave_address=20, mqtt_topic = "master/inlet/ammonia_pump", client = mqtt_client)
    ammonia_pump.pump_initialzation()
    time.sleep(1)

    """  set up hot-end """
    hotend.PIDcontroller_control.controller_initialization(hotend_controller)
    hotend.PIDcontroller_control.controller_setup(device=hotend_controller, SV=90, K_p=1, K_i=0.1, K_d=0.02)

    """  start multi thread """
    tasks = [
        {"func": lambda: read_HG803(device=HG803_sensor, client=mqtt_client), "interval": 3, "next_run": 0},
        # {"func": lambda: read_power(device=Powermeter, client=mqtt_client), "interval": 3, "next_run": 0},
        {"func": heater_relay.relay_control, "interval": 4, "next_run": 0},
        {"func": fan_in.fan_control, "interval": 5, "next_run": 0},
        {"func": ammonia_pump.pump_control, "interval": 5, "next_run": 0},
        {"func": lambda: hotend.PIDcontroller_control.controller_read_input(device=hotend_controller, client=mqtt_client, mqtt_topic="master/inlet/hotend_temperature"), "interval": 5, "next_run": 0},        
    ]


    while True:
        now = time.time()
        for t in tasks:
            if now  >= t["next_run"]:
                try:
                    t["func"]()
                except Exception as e:
                    print(f"Task {t['func'].__name__} error: {e}")
                t["next_run"] = now + t["interval"]
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n Exiting programm due to keyboard interrupt...")

except Exception as e:
    print(f"\nExiting program due to error: {e}")

finally:
    # cleanup all devices in RS485
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


    print("All devices cleaned up.")