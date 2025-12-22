import minimalmodbus
import struct
import time


powermeter = minimalmodbus.Instrument('/dev/ttyUSB0', 1) # dfault address
powermeter.serial.baudrate = 9600
powermeter.serial.bytesize = 8
powermeter.serial.parity = minimalmodbus.serial.PARITY_NONE # default
powermeter.serial.stopbits = 1 # default
powermeter.serial.timeout = 2
powermeter.mode = minimalmodbus.MODE_RTU



try:
    new_address = 60.0 # float
    hi, lo = struct.unpack('>HH', struct.pack('>f', new_address))
    powermeter.write_registers(registeraddress=20, values=[hi, lo], functioncode = 16) # address register 40021 = registeraddress:20
    time.sleep(0.5)
except Exception as e:
    print(f"Error -> {type(e).__name__}: {e}")

print("\n Done.")