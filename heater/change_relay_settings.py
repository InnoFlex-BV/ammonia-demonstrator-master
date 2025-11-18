import minimalmodbus
import serial
import time
import sys
sys.path.append('/home/innoflex/ammonia-demonstrator-master')
from common_config import create_device, clear_RS485
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
relay = create_device(slave_address=5)
clear_RS485(relay)
relay.serial.timeout = 1
time.sleep(1)

try:
    clear_RS485(relay)
    relay.write_bit(registeraddress=0, value=1, functioncode=5) # turn relay 1
    time.sleep(0.2)
    print("change finished")
except Exception as e:
    print("change failed", e)
finally:
    clear_RS485(relay)