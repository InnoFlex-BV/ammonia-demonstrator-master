import paho.mqtt.client as mqtt
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

## set up influxDB

token = "tU_ekH0KlkbOorqrXywdO0RO7LgiQ2v5rQOcIIGKXnT2SUu9qWF0oWNMeWrL2TxcAp1knfqCjx3ZYdvD5S52Zg=="
org = "Ammonia demonstrator"
url = "http://192.168.0.207:8086"
write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)


bucket="ammonia demonstrator"
write_api = write_client.write_api(write_options=SYNCHRONOUS)



# master itself is the broker
broker_ip = "127.0.0.1"


topic_menu = {
    "slave/outlet/temperature":"temperature",
    "slave/outlet/humidity":"humidity",
}


def on_message(client, userdata, msg):


    try:
        payload = msg.payload.decode('utf-8').strip()
        value = float(payload)
    except ValueError:
        print("failed to convert")
        return


    measurement = topic_menu.get(msg.topic)
    point = (
        Point(measurement)              # name of parameter that get measured
        .tag("device", "slave")           # tag
        .tag("module", "outlet")
        .field("value", value)            # field
    )
    write_api.write(bucket=bucket, org=org, record=point)
    print("successfully stored in InfluxDB")



client = mqtt.Client("MasterSubscriber")
client.on_message = on_message

# connect to broker
client.connect(broker_ip, 1883, 60)


# subscribe for slave's channel
client.subscribe("slave/outlet/temperature")
client.subscribe("slave/outlet/humidity")


#client.loop_forever()
client.loop_start()

try:
    print("Subscriber running... Press Ctrl+C to exit.")
    while True:
        time.sleep(10)  # keep the programm running
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    client.disconnect()
