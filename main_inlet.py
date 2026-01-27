import time
from common_config import create_device, create_client
from sensor.read_HG803 import read_sensor as read_HG803
from fan.fan_control import FanControll
from heater.relay_control import RelayControl
from pump.pump_control import PumpControll
import hotend.PIDcontroller_control
from powermeter.read_powermeter import read_power



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

    """  initializations of devices """
    fan_in = FanControll(slave_address=4, mqtt_topic="master/inlet/fan_in", client = mqtt_client)
    fan_in.fan_initialization()
    time.sleep(1)

    heater_relay = RelayControl(slave_address=5, mqtt_topic = "master/inlet/heater_relay", client = mqtt_client)
    heater_relay.relay_initialization()
    time.sleep(1)

    ammonia_pump = PumpControll(slave_address=20, mqtt_topic = "master/inlet/ammonia_pump", client = mqtt_client)
    ammonia_pump.pump_initialization()
    time.sleep(1)

    """  set up hot-end """
    hotend.PIDcontroller_control.controller_initialization(hotend_controller)
    hotend.PIDcontroller_control.controller_setup(device=hotend_controller, SV=85, K_p=25, K_i=1, K_d=50, T=0.2, AR=50)

    """  start multi thread """
    tasks = [
        {"name": "HG803 Sensor", "func": lambda: read_HG803(device=HG803_sensor, client=mqtt_client), "interval": 3, "next_run": 0},
        {"name": "Heater Relay", "func": heater_relay.relay_control, "interval": 4, "next_run": 0},
        {"name": "Inlet Fan", "func": fan_in.fan_control, "interval": 5, "next_run": 0},
        {"name": "Peristaltic Pump", "func": ammonia_pump.pump_control, "interval": 5, "next_run": 0},
        {"name": "Hot-end", "func": lambda: hotend.PIDcontroller_control.controller_read_status(device=hotend_controller, client=mqtt_client, mqtt_topic="master/inlet/hotend_temperature"), "interval": 5, "next_run": 0},       
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