import minimalmodbus
from time import sleep


device = minimalmodbus.Instrument('/dev/ttyUSB0', 39)
device.serial.baudrate = 9600
device.serial.bytesize = 8
device.serial.parity = minimalmodbus.serial.PARITY_NONE
device.serial.stopbits = 1
device.serial.timeout = 2
device.mode = minimalmodbus.MODE_RTU


## read input & holding registers
try:
    for addr in [*range(0, 7),12]:
        if addr == 22:
            value = device.read_float(registeraddress=0x0016, functioncode=3)
            print(f"result {addr+1}: = {value:.4f}") # result 23 -> pressure difference, only reflect 4-digit
            sleep(0.1)        
        else:
            value = device.read_register(addr)
            print(f"result {addr+1}: = {value}") # result 23 -> pressure difference, only reflect 4-digit
            sleep(0.1)

except Exception as e:
    print(f"{type(e).__name__}: {e}")


print("\n Done.")