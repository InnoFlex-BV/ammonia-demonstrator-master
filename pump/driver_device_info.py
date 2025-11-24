import minimalmodbus


motor = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
motor.serial.baudrate = 9600
motor.serial.bytesize = 8
motor.serial.parity = minimalmodbus.serial.PARITY_NONE
motor.serial.stopbits = 1
# motor.serial.timeout = 1
motor.mode = minimalmodbus.MODE_RTU


try:
    registers = motor.read_registers(registeraddress=0x0000, number_of_registers=10, functioncode=3)


    data_bytes = []
    for reg in registers:
        high = (reg >> 8) & 0xFF
        low = reg & 0xFF
        data_bytes.extend([high, low])

    # print HEX
    hex_str = " ".join(f"{b:02X}" for b in data_bytes)
    print(f"Raw data bytes (10 HEX): {hex_str}")
    

except Exception as e:
    print(f"Error: {e}")