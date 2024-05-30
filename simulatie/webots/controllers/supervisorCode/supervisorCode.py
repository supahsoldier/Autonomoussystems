import random
import json
import time
import sys
import threading
from paho.mqtt import client as mqtt_client
from controller import Supervisor

broker = '145.137.22.244'
port = 1883

chariotPositionTopics = ["chariot/1/position", "chariot/2/position", "chariot/3/position", "chariot/4/position", "chariot/5/position", "chariot/6/position"]
chariotTargetTopics = ["chariot/1/target", "chariot/2/target", "chariot/3/target", "chariot/4/target", "chariot/5/target", "chariot/6/target"]
client_id = "MelleSimulatie"

supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

chariot_nodes = [supervisor.getFromDef(f'Kubes{i+1}') for i in range(6)]
chariot_busy_flags = [False] * 6

def getAllPositions():
    return [node.getPosition() for node in chariot_nodes]

def interpolate_positions(start, end, steps):
    return [[start[i] + (end[i] - start[i]) * t / steps for i in range(3)] for t in range(steps)]

def move_to_position(node, start, end, busy_flag, steps=50, delay=0.02):
    print(busy_flag[0])
    if busy_flag[0]:
        print("Chariot is busy, try again later.")
        return
    busy_flag[0] = True
    interpolated_positions = interpolate_positions(start, end, steps)
    for pos in interpolated_positions:
        roundedPos = [round(i, 0) for i in pos]
        node.getField('translation').setSFVec3f(roundedPos)
        supervisor.step(timestep)
        time.sleep(delay)
    busy_flag[0] = False

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", file=sys.stderr)
        else:
            print(f"Failed to connect, return code {rc}\n", file=sys.stderr)

    def on_message(client, userdata, msg):
        msgConverted = json.loads(msg.payload.decode())
        topic_index = chariotTargetTopics.index(msg.topic)
        threading.Thread(target=move_to_position, args=(chariot_nodes[topic_index], chariot_nodes[topic_index].getPosition(), [msgConverted['x'], msgConverted['y'], msgConverted['z']], [chariot_busy_flags[topic_index]])).start()

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.loop_start()
    return client

def subscribeToTopics(client):
    for topic in chariotTargetTopics:
        client.subscribe(topic)

def publishPositions(client):
    while True:
        positions = getAllPositions()
        for i, position in enumerate(positions):
            msg = {"x": position[0], "y": position[1], "z": position[2]}
            result = client.publish(chariotPositionTopics[i], json.dumps(msg))
            if result[0] == 0:
                pass
            else:
                print(f"Failed to send message to topic {chariotPositionTopics[i]}", file=sys.stderr)
        time.sleep(2)

mqtt_client = connect_mqtt()
subscribeToTopics(mqtt_client)
publish_thread = threading.Thread(target=publishPositions, args=(mqtt_client,))
publish_thread.start()

while supervisor.step(timestep) != -1:
    pass
