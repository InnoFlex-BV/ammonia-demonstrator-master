from common_config import create_device


def read_sensor():
        device, client = create_device(slave_address=3)

        data = device.read_registers(registeraddress=0x0000, number_of_registers=2, functioncode=3)
        temperature = data[0]/100 # sensor data type = magnified 100 times
        humidity = data[1]/100
        client.publish("master/inlet/temperature", temperature)
        client.publish("master/inlet/humidity", humidity)
        print(f"Temperature: {temperature} degree, Humidity: {humidity} %")

        client.disconnect()