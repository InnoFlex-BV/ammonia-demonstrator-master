import time

from sensor.read_gas import read_sensor as read_gas
from sensor.read_HG803 import read_sensor as read_HG803
from fan.fan_control import FanControll
from heater.relay_control import RelayControl
#from test import read_sensor as read_random

# initializations
fan_in = FanControll(slave_address=4, mqtt_topic="master/inlet/fan_in")
fan_in.fan_initialzation()

heater_relay = RelayControl(slave_address=5, mqtt_topic = "master/inlet/heater_relay")
heater_relay.relay_initialization()

tasks = [
    #{"func": read_gas, "interval": 2, "next_run": 0},
    #{"func": read_HG803, "interval": 3, "next_run": 0},
    #{"func": fan_in.fan_control, "interval": 5, "next_run": 0},
    {"func": heater_relay.relay_control, "interval": 3, "next_run": 0.1},
    #{"func": read_random, "interval": 1, "next_run": 0.4}
]

try:
    while True:
        now = time.time()
        for t in tasks:
            if now  >= t["next_run"]:
                t["func"]()
                t["next_run"] = now + t["interval"]
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n Exiting programm ...")
    fan_in.client.loop_stop()
    fan_in.client.disconnect()