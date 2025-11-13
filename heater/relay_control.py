import serial
import paho.mqtt.client as mqtt
import threading
import time
from common_config import create_client, create_device
from heater.calculate_crc import calc_crc

serial_lock = threading.Lock()


class RelayControl:
    def __init__(self, serial_port = "/dev/ttyUSB0", mqtt_topic = "master/inlet/heater_relay"):
        self.relay = None
        self.lock = serial_lock
        self.serial_port = serial_port

        # initialize MQTT
        self.client = create_client()
        self.topic = mqtt_topic
        self.client.on_message = self.on_message
        self.client.subscribe(self.topic)
        self.client.loop_start()

        # initialize relay status
        self.old_status = False
        self.new_status = None

        # create commmands
        # turn on relay command
        self.request_on = bytearray([0xFE, 0x05, 0x00, 0x00, 0xFF, 0x00])
        self.request_on += calc_crc(self.request_on)

        # turn off relay command
        self.request_off = bytearray([0xFE, 0x05, 0x00, 0x00, 0x00, 0x00])
        self.request_off += calc_crc(self.request_off)


    def relay_initialization(self):
        self.relay = serial.Serial(
            self.serial_port,
            baudrate=9600, 
            bytesize=8, 
            parity=serial.PARITY_NONE, 
            stopbits=1, 
            timeout=1
        )
        with self.lock:
            self.relay.write(self.request_off)
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
                    self.relay.write(self.request_on)
                    time.sleep(0.1)
                    print(f"[HeaterControll] Heater ON")
                    resp = self.relay.read(len(self.request_on))  # 尝试读取返回帧
                    if resp:
                        print(f"[HeaterControll] Heater ON, device responded: {resp.hex()}")
                    else:
                        print(f"[HeaterControll] WARNING: Heater ON command sent, but no response from relay")

                else:
                    self.relay.write(self.request_off)
                    time.sleep(0.1)
                    print(f"[HeaterControll] Heater OFF")
                self.old_status = self.new_status
    

    def relay_close(self):
        with self.lock:
            self.relay.write(self.request_off)
        self.relay.close()
        self.client.loop_stop()
        self.client.disconnect()
        print("[HeaterControl] Heater OFF")
