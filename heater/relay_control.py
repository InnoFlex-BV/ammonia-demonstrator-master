import time
import minimalmodbus
from common_config import create_client, create_device, clear_RS485, strong_clear_RS485, serial_lock



class RelayControl:
    def __init__(self, slave_address=5, mqtt_topic = "master/inlet/heater_relay", client = None):
        # create an object
        self.slave_address = slave_address
        self.relay = None
        self.lock = serial_lock
        self.old_status = False
        self.new_status = None

        minimalmodbus.DEBUG = True

        # MQTT settings
        if client is None:
            self.client = create_client()
            self.client.loop_start()
        else:
            self.client = client

        self.topic = mqtt_topic
        self.client.message_callback_add(self.topic, self.on_message)
        self.client.subscribe(self.topic)


    def relay_initialization(self):
        self.relay = create_device(self.slave_address)
        self.relay.serial.timeout = 1
        with self.lock:
            strong_clear_RS485(self.relay)
            self.relay.write_bit(registeraddress=0x0000, value=0, functioncode=5)
        time.sleep(0.25)
        print("heater initialization finished. Current status: OFF")


    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode().strip().lower() # all string turn into lower case letters
            # self.new_status = payload_str == "true"
            if payload_str == "true":
                self.new_status = True
            elif payload_str == "false":
                self.new_status = False
            else:
                print(f"[HeaterControl] Invalid payload: {payload_str}")
                return            
            print(f"[HeaterControl] received new status: {self.new_status}")
        except Exception as e:
            print(f"Error: {e}")
        
    def relay_control(self):
        if self.relay is None:
            print("[HeaterControl] Heater is not initialized.")
            return
        if self.new_status is None or self.new_status == self.old_status:
            return

        with self.lock:
            try:
                strong_clear_RS485(self.relay)
                if self.new_status:
                    self.relay.write_bit(registeraddress=0, value=1, functioncode=5)
                    time.sleep(0.1)
                    print("[HeaterControl] Heater ON")
                else:
                    self.relay.write_bit(registeraddress=0, value=0, functioncode=5)
                    time.sleep(0.1)
                    print("[HeaterControl] Heater OFF")
                self.old_status = self.new_status
            except Exception as e:
                print(f"[HeaterControl] Relay write error: {e}")
    

    def relay_close(self):
        with self.lock:
            strong_clear_RS485(self.relay)
            self.relay.write_bit(registeraddress=0, value=0, functioncode=5)
        print("[HeaterControl] Heater OFF")
