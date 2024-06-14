import random
import json
import time
import sys
import math
import threading
from paho.mqtt import client as mqttClient
from controller import Supervisor


# MQTT server information
broker = '145.24.238.180'
port = 1883

# Needed MQTT topics
chariotPositionTopics = ["chariot/1/position", "chariot/2/position", "chariot/3/position", "chariot/4/position", "chariot/5/position", "chariot/6/position"]
chariotTargetTopics = ["chariot/1/target", "chariot/2/target", "chariot/3/target", "chariot/4/target", "chariot/5/target", "chariot/6/target"]
chariotStatusTopics = ["chariot/1/status", "chariot/2/status", "chariot/3/status", "chariot/4/status", "chariot/5/status", "chariot/6/status"]

# Generate a random client ID
clientId = f'supervisor-{random.randint(0, 1000)}'

# Get the supervisor and the time step
supervisor = Supervisor()
timeStep = int(supervisor.getBasicTimeStep())

# Get the nodes of the chariots
chariotNodes = [supervisor.getFromDef(f'Kubes{i+1}') for i in range(6)]

# Returns the position of all chariots
# Change range to 4 when working WITH the phisical chariots
# Change range to 6 when working WITHOUT the phisical chariots
def getAllPositions():

    nodes = []
    for i in range(4):
        node = chariotNodes[i].getField('translation').getSFVec3f()
        nodes.append(node)

    return nodes

# Function to move a chariot to a specific position
def moveToPosition(node, statusTopic, pathData, delay=0.5):

    publishStatus(mqttClient, statusTopic, "start")

    # Goes through the path and moves the chariot to the desired position
    for pos in pathData:
        currentPos = node.getField('translation').getSFVec3f()
        wantedPos = [round(pos['x']), round(pos['y']), round(pos['z'])]

        # Calculate the desired angle for the movement and set the rotation
        angle = calculateDesiredAngle(currentPos, wantedPos)
        rotationField = node.getField('rotation')
        rotation = [0, 0, 1, angle]  
        rotationField.setSFRotation(rotation)

        # Set the position
        node.getField('translation').setSFVec3f(wantedPos)

        # Wait for the specified delay
        time.sleep(delay)

    publishStatus(mqttClient, statusTopic, "stop")

    #Set the final orientation
    rotationField = node.getField('rotation')
    rotation = [0, 0, 1, pathData[0]['rotation'] * math.pi / 180]
    rotationField.setSFRotation(rotation)

# Moves the physical simulated robots to their real world position
def movePhysicalChariot(node, statusTopic, positionData, delay=0.5):

    wantedPos = [round(positionData['x']), round(positionData['y']), round(positionData['z'])]
    wantedRotation = positionData['rotation'] * math.pi / 180

    # Calculate the desired angle for the movement and set the rotation
    rotationField = node.getField('rotation')
    rotation = [0, 0, 1, wantedRotation]  
    rotationField.setSFRotation(rotation)

    # Set the position
    node.getField('translation').setSFVec3f(wantedPos)

    # Wait for the specified delay
    time.sleep(delay)
    
# Function to get the current rotation of a node in degrees
# Change range to 4 when working WITH the phisical chariots
# Change range to 5 when working WITHOUT the phisical chariots
def getAllCurrentRotationDegrees():
    nodes = []

    for i in range(4):
        node = chariotNodes[i].getField('rotation').getSFRotation()[3] * 180 / math.pi
        nodes.append(node)

    return nodes

# Function to calculate the desired angle for a chariot to move to a specific position
def calculateDesiredAngle(currentPos, desiredPos):
    x = desiredPos[0] - currentPos[0]
    y = desiredPos[1] - currentPos[1]
    return math.atan2(y, x)

# Function to connect to the MQTT broker
def connectMqtt():
    def onConnect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", file=sys.stderr)
        else:
            print(f"Failed to connect, return code {rc}\n", file=sys.stderr)

    # Function to handle incoming messages
    def onMessage(client, userdata, msg):
        msgConverted = json.loads(msg.payload.decode())

        if msg.topic == chariotPositionTopics[4] or msg.topic == chariotPositionTopics[5]:
            topicIndex = chariotPositionTopics.index(msg.topic)
            threading.Thread(target=movePhysicalChariot, args=(chariotNodes[topicIndex], chariotStatusTopics[topicIndex], msgConverted)).start()
        elif msg.topic != chariotTargetTopics[4] and msg.topic != chariotTargetTopics[5]:
            topicIndex = chariotTargetTopics.index(msg.topic)
            threading.Thread(target=moveToPosition, args=(chariotNodes[topicIndex], chariotStatusTopics[topicIndex] , msgConverted)).start()
    
    client = mqttClient.Client(mqttClient.CallbackAPIVersion.VERSION1, clientId)
    client.on_connect = onConnect
    client.on_message = onMessage
    client.connect(broker, port)
    client.loop_start()
    return client

# Function to subscribe to the needed topics
def subscribeToTopics(client):
    client.subscribe(chariotPositionTopics[4])
    client.subscribe(chariotPositionTopics[5])

    for topic in chariotTargetTopics:
        client.subscribe(topic)

# Function to publish the status of the chariots
def publishStatus(client, topic, status):
    result = client.publish(topic, status)
    if result[0] != 0:
        print(f"Failed to send message to topic {topic}\n")

# Function to publish the positions of the chariots every 2 seconds
def publishPositions(client):
    while True:
        positions = getAllPositions()
        rotations = getAllCurrentRotationDegrees()

        for i, position in enumerate(positions):
            msg = {
                "x": round(position[0]),
                "y": round(position[1]),
                "z": round(position[2]),
                "rotation": rotations[i]
            }
            result = client.publish(chariotPositionTopics[i], json.dumps(msg))
            if result[0] != 0:
                print(f"Failed to send message to topic {chariotPositionTopics[i]}", file=sys.stderr)
        time.sleep(2)

mqttClient = connectMqtt()
subscribeToTopics(mqttClient)
publishThread = threading.Thread(target=publishPositions, args=(mqttClient,))
publishThread.start()

while supervisor.step(timeStep) != -1:
    pass
