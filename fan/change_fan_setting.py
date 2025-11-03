import minimalmodbus
import serial


device = minimalmodbus.Instrument('/dev/ttyUSB0', 4)  # current slave address
device.serial.baudrate = 9600
device.serial.bytesize = 8
device.serial.parity   = serial.PARITY_NONE
device.serial.stopbits = 1
device.serial.timeout  = 0.5
device.mode = minimalmodbus.MODE_RTU

# overwrite above settings
device.write_register(registeraddress=0x0000, value=4, functioncode=6) # value = new slave address, e.g. 1~247
#device.write_register(registeraddress=0x0001, value=1, functioncode=6) # change baudrate
#device.write_register(registeraddress=0x0002, value=0, functioncode=6) # change parity 0=8N1

print("new settings has been set")
