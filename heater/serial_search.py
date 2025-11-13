import serial
import time
from calculate_crc import calc_crc


port_name = "/dev/ttyUSB0"
baudrates = [9600] # possible baudrate


def build_write_address_frame(addr):

    frame = bytearray()
    frame.append(addr)
    frame.append(0x10)
    frame += (0x0000).to_bytes(2, 'big')
    frame += (0x0001).to_bytes(2, 'big')
    frame.append(2)
    frame.append(0x00)
    frame.append(addr)
    frame += calc_crc(frame)
    return frame

for baud in baudrates:
    print(f"\nTesting baudrate: {baud}")
    ser = serial.Serial(port_name, baudrate=baud, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=0.2)
    for addr in range(1, 256):
        frame = build_write_address_frame(addr)
        try:
            ser.write(frame)
            time.sleep(0.1)
            resp = ser.read(11)
            if resp:
                print(f"Device responded at guessed address {addr}, baudrate {baud}, response: {resp.hex()}")
        except Exception as e:
            print(f"Error at address {addr}, baudrate {baud}: {e}")
    ser.close()
