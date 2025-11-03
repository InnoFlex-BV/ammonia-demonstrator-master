import minimalmodbus
from time import sleep


fan = minimalmodbus.Instrument('/dev/ttyUSB0', 4)
fan.serial.baudrate = 9600
fan.serial.bytesize = 8
fan.serial.parity = minimalmodbus.serial.PARITY_NONE
fan.serial.stopbits = 1
fan.serial.timeout = 1
fan.mode = minimalmodbus.MODE_RTU


## Read input & holding registers. Reference: Modbus register map
print("Input Registers: \n")
for reg in range(0, 18):
    try:
        value = fan.read_register(registeraddress=reg, functioncode=4)
        print(f"Input Register No.{reg+1} | Address {reg:02d}: {value}")
    except Exception as e:
        print(f"Input Register No.{reg+1} | Address {reg:02d}: Error -> {e}")
        break


print("\n Holding Registers: \n")

for reg in range(0, 32):
    try:
        value = fan.read_register(registeraddress=reg, functioncode=3)
        print(f"Holding Register No.{reg+1} | Address {reg:02d}: {value}")
    except Exception as e:
        print(f"Holding Register No.{reg+1} | Address {reg:02d}: Error -> {e}")
        break

print("\n Done.")
