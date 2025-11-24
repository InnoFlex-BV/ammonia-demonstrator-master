import minimalmodbus


motor = minimalmodbus.Instrument('/dev/ttyUSB0', 20)
motor.serial.baudrate = 9600
motor.serial.bytesize = 8
motor.serial.parity = minimalmodbus.serial.PARITY_NONE
motor.serial.stopbits = 1
# motor.serial.timeout = 1
motor.mode = minimalmodbus.MODE_RTU
# minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = False
# minimalmodbus._print_out = True

parameters = [
    "Bus mode",
    "Direction",
    "Speed",
    "Motor current",
    "Current limit",
    "Supply voltage",
    "Fault code",
    "Speed2 input",
    "Inputs",
    "-"
]

conversions = {
    "Speed": lambda x: x/2.55,
    "Motor current": lambda x: x/10,
    "Current limit": lambda x: x/10,
    "Supply voltage": lambda x: x/2.5

}

try:
    registers = motor.read_registers(registeraddress=0x044C, number_of_registers=5, functioncode=3)
    data_bytes = []
    for reg in registers:
        high = (reg >> 8) & 0xFF
        low = reg & 0xFF
        data_bytes.extend([high, low])

    status_dict = {}
    for name, value in zip(parameters, data_bytes):
        if name in conversions:
            status_dict[name] = conversions[name](value)
        else:
            status_dict[name] = value

    # print HEX
    hex_str = " ".join(f"{b:02X}" for b in data_bytes)
    print(f"Raw data bytes (10 HEX): {hex_str}")
    
    # print parameters status
    for name, value in status_dict.items():
        print(f"{name:15}: {value}")

except Exception as e:
    print(f"Error: {e}")