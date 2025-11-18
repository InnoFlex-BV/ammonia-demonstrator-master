import time
from heater.relay_control import RelayControl

"""  initializations of devices """
heater_relay = RelayControl(slave_address=5, mqtt_topic = "master/inlet/heater_relay")
heater_relay.relay_initialization()


"""  start multi thread """
tasks = [
    {"func": heater_relay.relay_control, "interval": 4, "next_run": 0},
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
    if heater_relay.relay is not None:
        heater_relay.relay_close()