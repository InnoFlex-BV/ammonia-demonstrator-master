import minimalmodbus
import struct
import time


powermeter = minimalmodbus.Instrument('/dev/ttyUSB0', 60)
powermeter.serial.baudrate = 9600
powermeter.serial.bytesize = 8
powermeter.serial.parity = minimalmodbus.serial.PARITY_NONE
powermeter.serial.stopbits = 1
powermeter.serial.timeout = 2
powermeter.mode = minimalmodbus.MODE_RTU


## read input & holding registers
print("Registers: \n")
regs = [0,6,12,18,24,30,36,70,72,74,76,78,84]
for reg in regs:
    try:
        raw_regs = powermeter.read_registers(registeraddress=reg, number_of_registers=2, functioncode=4)
        raw_bytes = struct.pack('>HH', raw_regs[0], raw_regs[1])
        value = struct.unpack('>f', raw_bytes)[0]  # turn into float
        print(f"Register No.{reg+1} | Address {reg:02d}: {value}")
        time.sleep(0.1)
    except Exception as e:
        print(f"Register No.{reg+1} | Address {reg:02d}: Error -> {type(e).__name__}: {e}")
        break


print("\n Done.")