import minimalmodbus
import serial
import time
import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_device, clear_RS485, strong_clear_RS485
from calculate_crc import calc_crc





""" using serial """
# ser = serial.Serial('/dev/ttyUSB0', 9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=1)
# ser.reset_input_buffer()
# ser.reset_output_buffer()
# time.sleep(0.05)
# # #request = bytes([0x00, 0x10, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x05]) # change slave address to 5, current is FF=255
# request = bytes([0x05, 0x05, 0x00, 0x00, 0xFF, 0x00]) # turn on relay 1
# request += calc_crc(request) # add crc

# ser.reset_input_buffer()
# ser.reset_output_buffer()
# time.sleep(0.05)

# ser.write(request)
# ser.flush()
# time.sleep(0.2)

# response = ser.read(11)
# print("Response:", response)
# ser.close()





""" using minimalmodbus RTU """
minimalmodbus.DEBUG = True
print("1")
relay = create_device(slave_address=5)
print("1.5")
relay.serial.timeout = 1
print("2")
#clear_RS485(relay)
strong_clear_RS485(relay)
time.sleep(0.5)
print("3")
print(f"device address {relay.address}")

try:
    #clear_RS485(relay)
    strong_clear_RS485(relay)
    print("4")
    print(f"before write - port open {relay.serial.is_open}")
    print(f"before write - in_waiting {relay.serial.in_waiting}")
    relay.write_bit(registeraddress=0, value=0, functioncode=5) # turn relay 1
    time.sleep(0.2)
    print("change finished")

except Exception as e:
    print("change failed", e)
    print(f"Error type: {type(e).__name__}")
finally:
    clear_RS485(relay)
    #strong_clear_RS485(relay)