import random
import time
import json
import sys
from paho.mqtt import client as mqtt_client

broker = '145.137.22.244'
port = 1883
send_topic = "chariot/1/target"
receive_topic = "chariot/1/target"
client_id = f'publish-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", file=sys.stderr)
        else:
            print(f"Failed to connect, return code {rc}\n", file=sys.stderr)

    def on_message(client, userdata, msg):
        pass

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    return client

def publish(client):
    for i in range(50):
        xValue = random.randint(-8, 8)
        yValue = random.randint(-8, 8)
        msg = { "x": xValue, 
                "y": yValue, 
                "z": 0
                }
        client.subscribe(receive_topic)
        jsonMsg = json.dumps(msg)
        result = client.publish(send_topic, jsonMsg)
        status = result[0]
        if status == 0:
            print(f"Sent `{msg}` to topic `{send_topic}`", file=sys.stderr)
        else:
            print(f"Failed to send message to topic {send_topic}", file=sys.stderr)

        time.sleep(2)

    # Stop the MQTT client loop
    client.loop_stop()

if __name__ == '__main__':
    client = connect_mqtt()
    publish(client)