import time

from sensor.read_gas import read_sensor as read_gas
from sensor.read_HG803 import read_sensor as read_HG803
from fan.fan_control import FanControll
from test import read_sensor as read_random


fan_in = FanControll(slave_address=4, mqtt_topic="master/inlet/fan_in")
fan_in.fan_initialzation()

tasks = [
    {"func": read_gas, "interval": 2, "next_run": 0},
    {"func": read_HG803, "interval": 3, "next_run": 0},
    {"func": fan_in.fan_control, "interval": 2, "next_run": 0},
    #{"func": read_fan, "interval": 10, "next_run": 0},
    {"func": read_random, "interval": 1, "next_run": 0}
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