import minimalmodbus
from time import sleep


HG803 = minimalmodbus.Instrument('/dev/ttyUSB0', 3)
HG803.serial.baudrate = 9600
HG803.serial.bytesize = 8
HG803.serial.parity = minimalmodbus.serial.PARITY_NONE
HG803.serial.stopbits = 1
HG803.serial.timeout = 1
HG803.mode = minimalmodbus.MODE_RTU


## read input & holding registers
print("Input Registers: \n")
for reg in range(0, 6):
    try:
        value = HG803.read_register(registeraddress=reg, functioncode=3)
        print(f"Input Register No.{reg+1} | Address {reg:02d}: {value}")
        sleep(0.1)
    except Exception as e:
        print(f"Input Register No.{reg+1} | Address {reg:02d}: Error -> {e}")
        break


print("\n Holding Registers: \n")

address = HG803.read_register(registeraddress=0x0100, functioncode=3)
print(f"Holding Register 0x0100 | Slave address: {address}")
sleep(0.1)

baudrate_mode = HG803.read_register(registeraddress=0x0101, functioncode=3)
baudrate_table = {1:1200,2:2400,3:4800,4:9600,5:19200,6:115200}
print(f"Holding Register 0x0101 | Baudrate: {baudrate_table.get(baudrate_mode,'Unknown')}")


print("\n Done.")
