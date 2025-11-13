from common_config import create_device, create_client, serial_lock
import time


def read_sensor():
        device = create_device(slave_address=3)
        client = create_client()

        with serial_lock:
                #t0 = time.time()
                data = device.read_registers(registeraddress=0x0000, number_of_registers=2, functioncode=3)
                #print(f"HG803 read time: [{time.time() - t0:.3f}s]")
        time.sleep(0.1) # avoid conflict with other devices in RS485 communication
        temperature = data[0]/100 # sensor data type = magnified 100 times
        humidity = data[1]/100
        client.publish("master/inlet/temperature", temperature)
        client.publish("master/inlet/humidity", humidity)
        print(f"Temperature: {temperature} degree, Humidity: {humidity} %")