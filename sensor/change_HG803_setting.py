import minimalmodbus
import serial


device = minimalmodbus.Instrument('/dev/ttyUSB0', 3)  # current slave address
device.serial.baudrate = 9600
device.serial.bytesize = 8
device.serial.parity   = serial.PARITY_NONE
device.serial.stopbits = 1
device.serial.timeout  = 0.5
device.mode = minimalmodbus.MODE_RTU

# overwrite above settings
#device.write_register(registeraddress=0x0100, value=3, functioncode=6) # value = new slave address, e.g. 1~247
#device.write_register(registeraddress=0x0101, value=1, functioncode=6) # change baudrate

print("new settings has been set")
