import sys
import paho.mqtt.client as mqtt
import subprocess
import signal
import socket
import time


broker_ip = "ammonia-master.local"
topic_control = "master/inlet/control"
topic_status = "slave/inlet/status"
main_script_path  = "/home/innoflex/ammonia-demonstrator-master/main_inlet.py"

Inlet_process = None


def on_message(client, userdata, msg):
    global Inlet_process
    command = msg.payload.decode().upper()

    if command == "START":
        if Inlet_process is None or Inlet_process.poll() is not None:
            print("Starting main_inlet.py ...")
            Inlet_process = subprocess.Popen(["python3", "-u", main_script_path],
                                             stdout=sys.stdout,
                                             stderr=sys.stderr)
            client.publish(topic_status, "RUNNING", retain=True)

    elif command == "STOP":
        if Inlet_process and Inlet_process.poll() is None:
            print("Stopping main_inlet.py ...")
            Inlet_process.send_signal(signal.SIGINT)
            Inlet_process.wait()
            Inlet_process = None
            client.publish(topic_status, "STOPPED", retain=True)
            print("Inlet Module Stopped")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic_control)
    client.publish(topic_status, "STOPPED", retain=True)

"""initialize MQTT"""
client = mqtt.Client(client_id="InletPi_manager")
client.on_connect = on_connect
client.on_message = on_message
client.will_set(topic_status, "OFFLINE", retain=True) # in case of that Inlet_pi is not working


"""Re-do if DNS or MQTT went wrong"""
while True:
    try:
        print("Trying to connect to MQTT broker...")
        client.connect(broker_ip, 1883, 60)
        print("MQTT Connected")
        break
    except socket.gaierror:
        print("DNS not ready.")
    except Exception as e:
        print(f"MQTT Connect failed: {e}")

    time.sleep(5)

client.loop_forever()