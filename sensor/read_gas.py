from common_config import create_device


def read_sensor():
    device, client = create_device(slave_address=2)
    
    values = device.read_registers(registeraddress=0x0000, number_of_registers=2, functioncode=3)
    gas1 = values[0]*5/4095 # turn analog into 0-5V voltage
    gas2 = values[1]*5/4095
    client.publish("master/inlet/ammonia1", gas1)
    client.publish("master/inlet/ammonia2", gas2)
    print(f"gas1: {gas1:1f}, gas2: {gas2:1f}")
    
    client.disconnect()



