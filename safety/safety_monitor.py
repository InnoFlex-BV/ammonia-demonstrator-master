from common_config import create_client
from collections import deque



class FireDetection:
    def __init__(self, client, inlet_temp_topic = "master/inlet/temperature", outlet_temp_topic = "slave/outlet/temperature"):
        if client is None:
            self.client = create_client()
        
        self.client = client
        self.inlet_temp = None # average temperature (from 3 previous sampling) of Inlet Module
        self.outlet_temp = None
        self.inlet_history = deque(maxlen=3)
        self.outlet_history = deque(maxlen=3)
        self.is_safe = True
        self.error_reason = ""

        self.client.message_callback_add(inlet_temp_topic, self.on_temp_message)
        self.client.message_callback_add(outlet_temp_topic, self.on_temp_message)
        self.client.subscribe(inlet_temp_topic)
        self.client.subscribe(outlet_temp_topic)
    

    def on_temp_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode().strip()
            new_temp = float(payload_str)

            if msg.topic == "master/inlet/temperature":
                self.inlet_history.append(new_temp)
                # print(f"New temp @ Inlet Module: {new_temp}")
                self.inlet_temp = sum(self.inlet_history)/len(self.inlet_history)
            else:
                self.outlet_history.append(new_temp)
                # print(f"New temp @ Outlet Module: {new_temp}")
                self.outlet_temp = sum(self.outlet_history)/len(self.outlet_history)
            
            if self.inlet_temp is not None and self.outlet_temp is not None:
                self._check_fire()
            
        except ValueError:
            print(f"[FireDetection] Receoved non-number data: {msg.payload}")
        except Exception as e:
            print(f"[FireDetection] Error during detection: {e}")
    

    def _check_fire(self):
        max_inlet_temp = 50
        max_outlet_temp = 70
        max_temp_diff = 20

        if len(self.inlet_history)<3 or len(self.outlet_history)<3:
            return

        if self.inlet_temp > max_inlet_temp:
            self.is_safe = False
            self.error_reason = f"Inlet Module high temperature detected: {self.inlet_temp} °C"
            # print(self.inlet_history)
        elif self.outlet_temp > max_outlet_temp:
            self.is_safe = False
            self.error_reason = f"Outlet Module high temperature detected: {self.outlet_temp} °C"
            # print(self.outlet_history)
        elif abs(self.inlet_temp - self.outlet_temp) > max_temp_diff:
            self.is_safe = False
            self.error_reason = f"FIRE? Abnormal temperature difference detected: {abs(self.inlet_temp-self.outlet_temp)} °C"
            # print(self.inlet_history, self.outlet_history)
        else:
            self.is_safe = True
