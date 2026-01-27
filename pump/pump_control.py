from common_config import create_device, create_client, clear_RS485, serial_lock
import time



class PumpControll:
    def __init__(self, slave_address=20, mqtt_topic="master/inlet/ammonia_pump", client = None):
        # create an object
        self.slave_address = slave_address
        self.device = None
        self.old_pump_pwm = 0
        self.new_pump_pwm = None
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

        self.stop_reg1 = (1 << 8) + 2
        self.stop_reg2 = (0 << 8) + 10


    def pump_initialzation(self):
        self.device = create_device(self.slave_address)

        with self.lock:
            # busmode = 1
            # ini_direction = 2
            # ini_speed = 0
            # current_limit = 10
            # ini_reg1 = (busmode << 8) + ini_direction
            # ini_reg2 = (ini_speed << 8) + current_limit
            # self.device.write_registers(registeraddress=0x03e8, values = [ini_reg1, ini_reg2])
            self.device.write_registers(registeraddress=0x03e8, values=[self.stop_reg1, self.stop_reg2])
            time.sleep(0.2)
            print("[PumpControll] ammonia_pump initialization finished. Current PWM: 0%")


    def on_message(self, client, userdata, msg):
        try:
            pump_pwm = int(float(msg.payload.decode()))
            # Validate PWM bounds (0-100%)
            if pump_pwm < 0 or pump_pwm > 100:
                print(f"[PumpControl] Invalid PWM {pump_pwm}%, must be 0-100")
                return
            self.new_pump_pwm = pump_pwm
            print(f"[PumpControl] Received new PWM {self.new_pump_pwm}%")
        except Exception as e:
            print(f"[PumpControl] Error parsing message: {e}")

    
    def pump_control(self):
        if self.device is None:
            print("[PumpControl] Pump not initialized.")
            return

        # Copy to local variable to avoid race condition with MQTT callback
        pwm = self.new_pump_pwm
        if pwm is not None and pwm != self.old_pump_pwm:
            with self.lock:
                pump_speed = int(2.55 * pwm)  # 0%-100% -> 0-255
                reg1 = (1 << 8) + 1
                reg2 = (pump_speed << 8) + 10
                self.device.write_registers(registeraddress=0x03e8, values=[reg1, reg2])
                time.sleep(0.2)
                print(f"[PumpControl] Set PWM to {pwm}%")
                self.old_pump_pwm = pwm
    

    def pump_stop(self):
        with self.lock:
            self.device.write_registers(registeraddress=0x03e8, values=[self.stop_reg1, self.stop_reg2])
            print("[PumpControl] Pump stopped. PWM = 0%")