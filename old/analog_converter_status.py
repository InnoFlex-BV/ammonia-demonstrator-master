import minimalmodbus
from time import sleep


device = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
device.serial.baudrate = 9600
device.serial.bytesize = 8
device.serial.parity = minimalmodbus.serial.PARITY_NONE
device.serial.stopbits = 1
device.serial.timeout = 1
device.mode = minimalmodbus.MODE_RTU



# change settings
try:
    # device.write_register(registeraddress=0x07d1, value=2, functioncode=6) # change baudrate
    device.write_register(registeraddress=0x07d0, value=2, functioncode=6) # change slave address
    sleep(0.1)
except Exception as e:
    print(f"{type(e).__name__}: {e}")

print("\n Done.")