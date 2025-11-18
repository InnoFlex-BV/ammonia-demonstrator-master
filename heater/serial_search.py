import serial
import time
from calculate_crc import calc_crc


""" check by scan through the broadcast address """
port_name = "/dev/ttyUSB0"

frame = bytearray([0x00,0x03,0x00,0x00,0x00,0x01])
frame += calc_crc(frame)

for baud in [4800, 9600]:
    print(f"Testing baurate {baud}:")
    ser = serial.Serial("/dev/ttyUSB0", baudrate=baud, timeout=1)
    ser.write(frame)
    time.sleep(0.01)
    resp = ser.read(32)
    print("Response:", resp.hex())   
    ser.close()

""" check addresses ONE-BY-ONE """
# port_name = "/dev/ttyUSB0"
# for baud in [4800, 9600]:
#     print(f"Testing baudrate {baud}:")
#     ser = serial.Serial(port_name, baudrate=baud, timeout=0.5)
#     for addr in range(5, 248):
#         frame = bytearray([addr, 0x03, 0x00, 0x00, 0x00, 0x01])
#         frame += calc_crc(frame)
#         ser.reset_input_buffer()
#         ser.reset_output_buffer()
#         ser.write(frame)
#         time.sleep(0.05)
#         resp = ser.read(32)
#         if resp:
#             print(f"Device responded at address {addr}, response: {resp.hex()}")
#     ser.close()
