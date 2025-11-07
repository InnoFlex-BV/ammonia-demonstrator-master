import serial
import time
from calculate_crc import calc_crc

ser = serial.Serial('/dev/ttyUSB0', 9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=1)


request = bytes([0xFF, 0x10, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x05]) # change slave address to 5, current is FF=255
#request = bytes([0xFF, 0x10, 0x03, 0xE9, 0x00, 0x01, 0x02, 0x00, 0x03])

## add crc
request += calc_crc(request)


ser.write(frame)
time.sleep(0.1)
response = ser.read(11)
print("Response:", response)
