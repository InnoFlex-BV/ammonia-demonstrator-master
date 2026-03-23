from common_config import create_device, create_client, clear_RS485, serial_lock
import time



class FanControl:
    def __init__(self, slave_address=4, mqtt_topic="master/inlet/fan_in_manual", client = None):
        # create an object
        self.slave_address = slave_address
        self.device = None
        self.old_speed = 0
        self.new_speed = None
        self.lock = serial_lock

        # MQTT settings
        if client is None:
            self.client = create_client()
            self.client.loop_start()
        else:
            self.client = client

        self.manual_topic = mqtt_topic
        self.client.message_callback_add(self.manual_topic, self.on_message)
        self.client.subscribe(self.manual_topic)

        # Manual Control vs PID Control
        self.is_manual = True
        self.mode_topic = "master/inlet/fan_mode_manual"
        self.client.message_callback_add(self.mode_topic, self.on_mode_message)
        self.client.subscribe(self.mode_topic)

        self.auto_topic = "master/inlet/fan_in_auto"
        self.client.message_callback_add(self.auto_topic, self.on_message)
        self.client.subscribe(self.auto_topic)


    def fan_initialization(self):
        self.device = create_device(self.slave_address)

        with self.lock:
            self.device.write_register(registeraddress=6, value=1, functioncode=6)
            time.sleep(0.25)
            self.device.write_register(registeraddress=7, value=1, functioncode=6)
            time.sleep(0.25)
            self.device.write_register(registeraddress=30, value=1, functioncode=6)
            time.sleep(0.25)
            print("[FanControl] Initialization finished. Current speed: 0")


    def on_message(self, client, userdata, msg):
        # print(f"[DEBUG] Received Topic: {msg.topic}, Payload: {msg.payload.decode()}")
        try:
            topic = msg.topic
            speed = int(float(msg.payload.decode()))
            if speed < 0 or speed > 100:
                print(f"[FanControl] Invalid speed {speed}%, must be 0-100")
                return
            # Validate speed bounds (0-100%)
            # If it is in manual-mode, then only listen to manual control commands, vice versa
            if self.is_manual:
                if topic == self.manual_topic:
                    self.new_speed = speed
                    print(f"[FanControl] Received new speed {self.new_speed}%")
                else: # ignore the speed from auto-control
                    pass
            else:
                if topic == self.auto_topic:
                    self.new_speed = speed
                else: # ignore the speed from manual control
                    pass


        except Exception as e:
            print(f"[FanControl] Error parsing message: {e}")
            self.client.publish("master/inlet/error", f"[FanControl] Error parsing message: {e}")


    def on_mode_message(self, client, userdata, msg): # check to mode is auto or manual
        mode_message = msg.payload.decode().lower()
        self.is_manual = (mode_message=="true")
        print(f"[FanControl] Control mode changed: Manual = {self.is_manual}")
        

    
    def fan_control(self):
        if self.device is None:
            print("[FanControl] Fan not initialized.")
            self.client.publish("master/inlet/error", "[FanControl] Fan not initialized.")
            return

        # Copy to local variable to avoid race condition with MQTT callback
        speed = self.new_speed
        if speed is not None and speed != self.old_speed:
            # if abs(speed-self.old_speed>=1):
                with self.lock:
                    self.device.write_register(registeraddress=30, value=speed, functioncode=6)
                    time.sleep(0.1)
                    self.client.publish("master/inlet/fan_output", speed)
                    print(f"[FanControl] Set fan speed to {speed}%")
                    self.old_speed = speed
    

    def fan_stop(self):
        with self.lock:
            self.device.write_register(registeraddress=30, value=0, functioncode=6)
            time.sleep(0.1)
            print("[FanControl] Fan stopped. Speed = 0")