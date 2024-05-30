import random
import json
import time
import sys
import threading
from paho.mqtt import client as mqtt_client
from controller import Supervisor

broker = '145.137.22.244'
port = 1883
receiveTopic = "python/melle/serversend"

chariot1PositionTopic = "chariot/1/position"
chariot2PositionTopic = "chariot/2/position"
chariot3PositionTopic = "chariot/3/position"
chariot4PositionTopic = "chariot/4/position"
chariot5PositionTopic = "chariot/5/position"
chariot6PositionTopic = "chariot/6/position"
chariotPositionTopics = [chariot1PositionTopic, chariot2PositionTopic, chariot3PositionTopic, chariot4PositionTopic, chariot5PositionTopic, chariot6PositionTopic]

chariot1TargetTopic = "chariot/1/target"
chariot2TargetTopic = "chariot/2/target"
chariot3TargetTopic = "chariot/3/target"
chariot4TargetTopic = "chariot/4/target"
chariot5TargetTopic = "chariot/5/target"
chariot6TargetTopic = "chariot/6/target"
chariotTargetTopics = [chariot1TargetTopic, chariot2TargetTopic, chariot3TargetTopic, chariot4TargetTopic, chariot5TargetTopic, chariot6TargetTopic]

client_id = "MelleSimulatie"
#client_id = f'client-{random.randint(0, 1000)}'

# Create supervisor instance
supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

# Retrieve the node references of the cubes
Chariot1_node = supervisor.getFromDef('Kubes1')
Chariot2_node = supervisor.getFromDef('Kubes2')
Chariot3_node = supervisor.getFromDef('Kubes3')
Chariot4_node = supervisor.getFromDef('Kubes4')
Chariot5_node = supervisor.getFromDef('Kubes5')
Chariot6_node = supervisor.getFromDef('Kubes6')

def getAllPositions():
    # Get the original positions of all cubes
    return [
        Chariot1_node.getPosition(),
        Chariot2_node.getPosition(),
        Chariot3_node.getPosition(),
        Chariot4_node.getPosition(),
        Chariot5_node.getPosition(),
        Chariot6_node.getPosition()
    ]

def calculateNewPositions(original_positions):
    # Calculate new positions for each cube based on the square pattern with a step of 1
    new_positions = []
    for position in original_positions:
        x, y, z = position
        # Move the cube in a square pattern with a step of 1 from its original position
        new_position = [[round(x + 1, 1), round(y + 1, 1), z], [round(x + 1, 1), round(y - 1, 1), z], [round(x - 1, 1), round(y - 1, 1), z], [round(x - 1, 1), round(y + 1, 1), z]]
        new_positions.append(new_position)
    return new_positions

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", file=sys.stderr)
        else:
            print(f"Failed to connect, return code {rc}\n", file=sys.stderr)
    
    def on_log(client, userdata, level, buf):
        print(f"LOG: {buf}", file=sys.stderr)

    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic", file=sys.stderr)
        msgConverted = json.loads(msg.payload.decode())
        if msg.topic == chariot1TargetTopic:
            Chariot1_node.getField('translation').setSFVec3f([msgConverted['x'], msgConverted['y'], msgConverted['z']])
        elif msg.topic == chariot2TargetTopic:
            Chariot2_node.getField('translation').setSFVec3f([msgConverted['x'], msgConverted['y'], msgConverted['z']])
        elif msg.topic == chariot3TargetTopic:
            Chariot3_node.getField('translation').setSFVec3f([msgConverted['x'], msgConverted['y'], msgConverted['z']])
        elif msg.topic == chariot4TargetTopic:
            Chariot4_node.getField('translation').setSFVec3f([msgConverted['x'], msgConverted['y'], msgConverted['z']])
        elif msg.topic == chariot5TargetTopic:
            Chariot5_node.getField('translation').setSFVec3f([msgConverted['x'], msgConverted['y'], msgConverted['z']])
        elif msg.topic == chariot6TargetTopic:
            Chariot6_node.getField('translation').setSFVec3f([msgConverted['x'], msgConverted['y'], msgConverted['z']])        
        
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_log = on_log
    client.connect(broker, port)
    client.loop_start()  # Start the loop
    return client
    
def subscribeToTopics(client):
    for topic in chariotTargetTopics:
        client.subscribe(topic)

# Sends the positions of all cubes to the server every second
def publishPositions(client):
    while True:
        #List of lists with x, y, z positions of all cubes
        positions = getAllPositions()
        msg = {}
        
        for i, position in enumerate(positions):
            msg = {
                "x": position[0],
                "y": position[1],
                "z": position[2]
            }

            result = client.publish(chariotPositionTopics[i], str(msg))
            status = result[0]

            if status == 0:
                print(f"Sent `{msg}` to topic `{chariotPositionTopics[i]}`", file=sys.stderr)
            else:
                print(f"Failed to send message to topic {chariotPositionTopics[i]}", file=sys.stderr)
        time.sleep(2)


# Subscribe to the topic and start MQTT client loop
mqtt_client = connect_mqtt()
subscribeToTopics(mqtt_client)
x = threading.Thread(target=publishPositions, args=(mqtt_client,))
x.start()

while supervisor.step(timestep) != -1:
    pass
