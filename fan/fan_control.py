from common_config import create_device, create_client
import threading
import time

serial_lock = threading.lock()

class FanControll:
    def __init__(self, slave_address=4, mqtt_topic="master/inlet/fan_in"):
        # create an object
        self.slave_address = slave_address
        self.device = None
        self.old_speed = 0
        self.new_speed = None
        self.lock = serial_lock

        # MQTT settings
        self.client = create_client()
        self.topic = mqtt_topic
        self.client.message_callback_add(self.topic, self.on_message)
        self.client.subscribe(self.topic)


    def fan_initialzation(self):
        self.device = create_device(self.slave_address)
        
        self.device.write_register(registeraddress=6, value=1, functioncode=6)
        time.sleep(0.25)
        self.device.write_register(registeraddress=7, value=1, functioncode=6)
        time.sleep(0.25)    
        self.device.write_register(registeraddress=30, value=1, functioncode=6)
        time.sleep(0.25)
        print("fan_in initialization finished")


    def on_message(self, client, userdata, msg):
        try:
            speed = int(float(msg.payload.decode()))
            self.new_speed = speed
            print(f"received new speed {self.new_speed}%")
        except Exception as e:
            print(f"Error: {e}")

    
    def fan_control(self):
        if self.fan_device is None:
            print("[FanControll] Fan not initialized.")
            return

        if self.new_speed is not None and self.new_speed != self.old_speed:
            with self.lock:
                self.fan_device.write_register(registeraddress=30, value=self.new_speed, functioncode=6)
                print(f"[FanControll] Set fan speed to {self.new_speed}%")
                self.old_speed = self.new_speed