from common_config import create_device, create_client, clear_RS485, serial_lock
import time



class FanControll:
    def __init__(self, slave_address=4, mqtt_topic="master/inlet/fan_in", client = None):
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

        self.topic = mqtt_topic
        self.client.message_callback_add(self.topic, self.on_message)
        self.client.subscribe(self.topic)


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
        try:
            speed = int(float(msg.payload.decode()))
            # Validate speed bounds (0-100%)
            if speed < 0 or speed > 100:
                print(f"[FanControl] Invalid speed {speed}%, must be 0-100")
                return
            self.new_speed = speed
            print(f"[FanControl] Received new speed {self.new_speed}%")
        except Exception as e:
            print(f"[FanControl] Error parsing message: {e}")

    
    def fan_control(self):
        if self.device is None:
            print("[FanControl] Fan not initialized.")
            return

        # Copy to local variable to avoid race condition with MQTT callback
        speed = self.new_speed
        if speed is not None and speed != self.old_speed:
            with self.lock:
                self.device.write_register(registeraddress=30, value=speed, functioncode=6)
                time.sleep(0.1)
                print(f"[FanControl] Set fan speed to {speed}%")
                self.old_speed = speed
    

    def fan_stop(self):
        with self.lock:
            self.device.write_register(registeraddress=30, value=0, functioncode=6)
            time.sleep(0.1)
            print("[FanControl] Fan stopped. Speed = 0")