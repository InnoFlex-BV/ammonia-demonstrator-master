import serial
import time
from calculate_crc import calc_crc


ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=1)

# read register
request_addr = bytearray([0xFE, 0x03, 0x00, 0x00, 0x00, 0x01])
request_baud = bytearray([0xFE, 0x03, 0x03, 0xE9, 0x00, 0x01])
request_relay = bytearray([0xFE, 0x01, 0x00, 0x00, 0x00, 0x01])

#
try:
    request_addr += calc_crc(request_addr)
    ser.write(request_addr)
    time.sleep(0.1)
    return_addr = ser.read(7)  # read return
    if return_addr:
        print("Raw response (address):", return_addr.hex())
        if len(return_addr) >= 5:
            val = int.from_bytes(return_addr[3:5], 'big')
            print("Device address value:", val)


    request_baud += calc_crc(request_baud)
    ser.write(request_baud)
    time.sleep(0.1)
    return_baud = ser.read(9)  # read return
    if return_baud:
        print("Raw response (baudrate):", return_baud.hex())
        if len(return_baud) >= 5:
            val = int.from_bytes(return_baud[3:5], 'big')
            print("Baudrate register value:", val)

    request_relay += calc_crc(request_relay)
    ser.write(request_relay)
    time.sleep(0.1)
    return_relay = ser.read(6)  # read return
    if return_addr:
        print("Raw response (relay):", return_relay.hex())
        relay_status = return_relay[3]
        if relay_status & 0x01:
            print("Relay status: ON")
        else:
            print("Relay status: OFF")

except Exception as e:
    print(f"Error -> {e}")

finally:
    ser.close()
