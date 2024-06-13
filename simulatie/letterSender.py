# Test script to send paths to chariots

import random
import time
import json
import sys
from paho.mqtt import client as mqtt_client

broker = '145.24.238.180'
port = 1883
client_id = f'publish-{random.randint(0, 1000)}'

chariot1TargetTopic = "chariot/1/target"
chariot2TargetTopic = "chariot/2/target"
chariot3TargetTopic = "chariot/3/target"
chariot4TargetTopic = "chariot/4/target"
chariot5TargetTopic = "chariot/5/target"
chariot6TargetTopic = "chariot/6/target"
chariotTargetTopics = [chariot1TargetTopic, chariot2TargetTopic, chariot3TargetTopic, chariot4TargetTopic, chariot5TargetTopic, chariot6TargetTopic]

L = [
    [{"x": 9, "y": 9, "z": 0}],
    [{"x": -1, "y": 0, "z": 0}],
    [{"x": -8, "y": 9, "z": 0}],
    [{"x": 4, "y": 2, "z": 0}],
    [{"x": -2, "y": -8, "z": 0}],
    [{"x": 3, "y": 0, "z": 0}]
]

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
    for i, path in enumerate(L):
        topic = chariotTargetTopics[i]
        msg = path
        jsonMsg = json.dumps(msg)
        result = client.publish(topic, jsonMsg)
        status = result[0]
        if status == 0:
            print(f"Sent `{msg}` to topic `{topic}`", file=sys.stderr)
        else:
            print(f"Failed to send message to topic {topic}", file=sys.stderr)
        time.sleep(1)
    
    client.loop_stop()

if __name__ == '__main__':
    client = connect_mqtt()
    time.sleep(5)
    publish(client)