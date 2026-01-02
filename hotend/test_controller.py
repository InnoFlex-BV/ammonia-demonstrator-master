import time
import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_device, create_client
import PIDcontroller_control


mqtt_client = create_client()
mqtt_client.loop_start()

""" create objects """
hotend_controller = create_client
overshoot = 0

try:

    hotend_controller = create_device(slave_address=25)
    PIDcontroller_control.controller_initialization(hotend_controller)
    PIDcontroller_control.controller_setup(device=hotend_controller, SV=85, K_p=25, K_i=1, K_d=50, T=4, AR=50)

    while True:
        data = PIDcontroller_control.controller_read_status(device=hotend_controller, client=mqtt_client, mqtt_topic="master/inlet/hotend_temperature")
        if data > overshoot:
            overshoot = data
        time.sleep(5)

except KeyboardInterrupt:
    print("\n Exiting programm due to keyboard interrupt...")

except Exception as e:
    print(f"\nExiting program due to error: {e}")

finally:
    # cleanup all devices in RS485
    if hotend_controller is not None:
        try:
            PIDcontroller_control.controller_checkout(hotend_controller)
            time.sleep(0.1)
            print(f"Max value: {data} degree.")
            PIDcontroller_control.controller_stop(hotend_controller)
        except Exception as e:
            print(f"Error stopping hot-end: {e}")

    print("All devices cleaned up.")