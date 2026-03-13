import time
import random
import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_device, create_client
from safety.safety_monitor import FireDetection



mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
fire_monitor = FireDetection(client=mqtt_client)



try:

    """  initializations of devices """
    print("Set up: Fan")
    time.sleep(0.1)

    print("Set up: Heater")
    time.sleep(0.1)

    print("Set up: Pump")
    time.sleep(0.1)

    """  set up hot-end """
    print("Set up: Hot-end")
    time.sleep(0.1)

    """  start multi thread """
    tasks = [
        # {"name": "HG803 Sensor", "func": lambda: print(f"[HG803] test: {random.uniform(20.0, 25.0):.2f}°C"), "interval": 5, "next_run": 0},
        # {"name": "Heater Relay", "func": lambda: print(f"[Heater] test: {random.uniform(0, 100)}%"), "interval": 5, "next_run": 0},
        # {"name": "Inlet Fan", "func": lambda: print(f"[Fan] test: {random.uniform(30, 100)}%"), "interval": 5, "next_run": 0},
        # {"name": "Peristaltic Pump", "func": lambda: print(f"[Pump] test: {random.uniform(0, 100)}%"), "interval": 5, "next_run": 0},
        # {"name": "Hot-end", "func": lambda: print(f"[HotEndControl] test: {random.uniform(25, 85)}°C"), "interval": 15, "next_run": 0},       
        # {"name": "Powermeter", "func": lambda: print(f"[Powermeter] test: {random.uniform(1, 2):.2f}kW"), "interval": 15, "next_run": 0}, 
        {"name": "Test", "func": lambda: print(f"[Test] test: Ruuning well."), "interval": 5, "next_run": 0}, 
    ]


    while True:
        now = time.time()

        # fire detection
        if not fire_monitor.is_safe:
            print(f"STOPPED: {fire_monitor.error_reason}")
            break

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
    print("[Hotend] Hotend check out")
    time.sleep(0.1)
    print("[Fan] Fan OFF")
    time.sleep(0.1)
    print("[Heater] Heater OFF")
    time.sleep(0.1)
    print("[Pump] Pump OFF")


    # Cleanup MQTT client (only once, after all devices are stopped)
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("All devices cleaned up.")