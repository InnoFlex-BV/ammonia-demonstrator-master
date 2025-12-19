import time
import minimalmodbus
import serial


controller = minimalmodbus.Instrument('/dev/ttyUSB0', 25)
controller.serial.baudrate = 9600
controller.serial.bytesize = 8
controller.serial.parity = serial.PARITY_NONE
controller.serial.stopbits = 1
controller.serial.timeout = 0.5
controller.mode = minimalmodbus.MODE_RTU

controller.write_register(registeraddress=0x0002, value=100, functioncode=6)
print("Down.")