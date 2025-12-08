from read_temp import read_temp
from hotend_control import HotEndControl
import time

"""
This python code is used for control the temperature of hotend, which is a low logic loop and will not be included into main control loop of the ammonia demonstrator.
"""

""" set parameters """
set_point = 80
delta_t = 60
K_p = 0.5
K_i = 0.1
K_d = 0

""" create object """
hotend_relay = None

""" initialization """
total_error = 0
last_error = 0
hotend_relay = HotEndControl(slave_address=25)
hotend_relay.relay_initialization()

""" PID control """
def main():
    global total_error, last_error, hotend_relay


    try:
        while True:
            current_temp = read_temp()
            error = set_point - current_temp
            total_error = total_error+ error*delta_t

            P_term = K_p * error
            I_term = K_i * total_error

            contorl_output = P_term + I_term
            if contorl_output > 1:
                contorl_output = 1
                if error > 0:
                    total_error = total_error-error*delta_t # anti-windup
            elif contorl_output < 0:
                contorl_output = 0
                if error < 0:
                    total_error = total_error-error*delta_t

            t_on = contorl_output * delta_t
            t_off = delta_t - t_on

            if t_on > 0:
                hotend_relay.relay_on()
                time.sleep(t_on)
            if t_off > 0:
                hotend_relay.relay_off()
                time.sleep(t_off)



    except KeyboardInterrupt:
        hotend_relay.relay_off()
        print("[Hot End] KeyboardInterrupt. Exiting...")
    except Exception as e:
        hotend_relay.relay_off()
        print(f"[Hot End] Error: {e}")



if __name__ == "__main__":
    main()