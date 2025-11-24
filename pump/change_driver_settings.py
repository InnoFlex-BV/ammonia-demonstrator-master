import minimalmodbus
import time

minimalmodbus.DEBUG = True

motor = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # current slave address
motor.serial.baudrate = 9600
motor.serial.bytesize = 8
motor.serial.parity   = minimalmodbus.serial.PARITY_NONE
motor.serial.stopbits = 1
motor.serial.timeout  = 0.5
motor.mode = minimalmodbus.MODE_RTU


# print("done")
new_address = 20
params = [0]*23

params[0]  = 0     # command mode
params[1]  = 1     # start condition
params[2]  = 0     # input logic
params[3]  = 100   # running speed-1 (0-100%)
params[4]  = 0     # not in use
params[5]  = 30    # current limit FW (1-250)
params[6]  = 30    # current limit REV (1-250)
params[7]  = 1     # Trip combinations
params[8]  = 20    # I-trip delay
params[9]  = 1     # Fault output combinations
params[10] = 35    # Overvoltage limit
params[11] = 0     # Load compensation
params[12] = 0     # Timeout
params[13] = 0     # Reset start/hour-counter
params[14] = 100   # Start ramp
params[15] = 100   # Stop ramp
params[16] = 0     # Start kick
params[17] = 0     # I-trip auto reversing
params[18] = 0     # Freewheel options
params[19] = 1     # PWM frequency
params[20] = 0     # Brake out mode
params[21] = 1     # Serial port configuration 9600 8N1
params[22] = new_address    # Modbus address (slave_address)

# turn value into msb & lsb
registers = [(0 << 8) + val for val in params]

# overwrite into registers
motor.write_registers(registeraddress=0x0064, values=registers)

# parameters are saved to memory which can tak eabout 50ms - 150ms
time.sleep(0.2)

print("All parameters setted")
