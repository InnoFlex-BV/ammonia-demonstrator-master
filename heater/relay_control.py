import threading
import time
from common_config import create_client, create_device

serial_lock = threading.Lock()


class RelayControl:
    def __init__(self, slave_address=5, mqtt_topic = "master/inlet/heater_relay"):
        # create an object
        self.slave_address = slave_address
        self.relay = None
        self.lock = serial_lock
        self.old_status = False
        self.new_status = None

        # MQTT settings
        self.client = create_client()
        self.topic = mqtt_topic
        self.client.on_message = self.on_message
        self.client.subscribe(self.topic)
        self.client.loop_start()


    def relay_initialization(self):
        self.relay = create_device(self.slave_address)
        with self.lock:
            self.relay.write_bit(registeraddress=0, value=0, functioncode=5)
        time.sleep(0.25)
        print("heater initialization finished. Current status: OFF")

    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode().strip().lower() # all string turn into lower case letters
            self.new_status = payload_str == "true"
            print(f"[HeaterControl] received new status {self.new_status}")
        except Exception as e:
            print(f"Error: {e}")
        
    def relay_control(self):
        if self.relay is None:
            print("[HeaterControll] Heater is not initialized.")
            return

        if self.new_status is not None and self.new_status != self.old_status:
            with self.lock:
                if self.new_status:
                    self.relay.write_bit(registeraddress=0, value=1, functioncode=5)
                    time.sleep(0.1)
                    print(f"[HeaterControll] Heater ON")
                else:
                    self.relay.write_bit(registeraddress=0, value=0, functioncode=5)
                    time.sleep(0.1)
                    print(f"[HeaterControll] Heater OFF")
                self.old_status = self.new_status
    

    def relay_close(self):
        with self.lock:
            self.relay.write_bit(registeraddress=0, value=0, functioncode=5)
        self.relay.close()
        self.client.loop_stop()
        self.client.disconnect()
        print("[HeaterControl] Heater OFF")
