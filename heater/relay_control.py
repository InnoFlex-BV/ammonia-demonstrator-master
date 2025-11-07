import serial
import time
from calculate_crc import calc_crc


ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=1)

# turn on relay
request_on = bytearray([0x05, 0x05, 0x00, 0x00, 0x00, 0x00])

try:
    request_on += calc_crc(request_on)
    ser.write(request_on)
    time.sleep(0.1)
    print(f"change finished")

except Exception as e:
    print(f"Error -> {e}")

finally:
    ser.close()
