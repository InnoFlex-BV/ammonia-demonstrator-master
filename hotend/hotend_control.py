import time
import minimalmodbus
from common_config import create_device, clear_RS485, strong_clear_RS485, serial_lock



class HotEndControl:
    def __init__(self, slave_address=25):
        # create an object
        self.slave_address = slave_address
        self.relay = None
        self.lock = serial_lock
        self.old_status = False
        self.new_status = None

        minimalmodbus.DEBUG = True


    def relay_initialization(self):
        self.relay = create_device(self.slave_address)
        self.relay.serial.timeout = 1
        with self.lock:
            strong_clear_RS485(self.relay)
            self.relay.write_bit(registeraddress=0x0000, value=0, functioncode=5)
        time.sleep(0.25)
        print("Hot End initialization finished. Current status: OFF")


    def relay_on(self):
        with self.lock:
            strong_clear_RS485(self.relay)
            self.relay.write_bit(registeraddress=0, value=1, functioncode=5)
        print("[HotEndControl] Hot End ON")


    def relay_off(self):
        with self.lock:
            strong_clear_RS485(self.relay)
            self.relay.write_bit(registeraddress=0, value=0, functioncode=5)
        print("[HotEndControl] Hot End OFF")