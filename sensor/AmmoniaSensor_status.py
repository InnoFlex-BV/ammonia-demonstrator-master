import minimalmodbus
from time import sleep


AmmoSensor = minimalmodbus.Instrument('/dev/ttyUSB0', 7)
AmmoSensor.serial.baudrate = 9600
AmmoSensor.serial.bytesize = 8
AmmoSensor.serial.parity = minimalmodbus.serial.PARITY_NONE
AmmoSensor.serial.stopbits = 1
AmmoSensor.serial.timeout = 1
AmmoSensor.mode = minimalmodbus.MODE_RTU
AmmoSensor.debug = True

## read status & show frames
print("Read Satus: \n")
try:
    value = AmmoSensor.read_registers(registeraddress=0x0000, number_of_registers=5, functioncode=3)
    sleep(0.1)
except Exception as e:
    print(f"Failed to read registers: Error -> {e}")

print(value)
Ammo_concentration = value[4]/100
print(f"Ammonia concentration: {Ammo_concentration} ppm.")

print("\n Done.")