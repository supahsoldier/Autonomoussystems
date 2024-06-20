import random, json, time, sys
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from paho.mqtt import client as mqtt_client
from bfs import getPaths, generate_graph
from letter import getLetters, getRotation

# initial chariot coordinates
chariots = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]

# topics for receiving input
topics = ["application/front/in", "chariot/1/position", "chariot/2/position", "chariot/3/position", "chariot/4/position", "chariot/5/position", "chariot/6/position", "chariot/1/status","chariot/2/status", "chariot/3/status", "chariot/4/status", "chariot/5/status", "chariot/6/status"]

# topics for outputting data
target_topics = ["chariot/1/target", "chariot/2/target", "chariot/3/target", "chariot/4/target", "chariot/5/target", "chariot/6/target"]

# arrays containing positions and rotations for individual letters
letters = getLetters()
rotations = getRotation()

incomming_buffer = []
moving = [False, False, False, False, False, False]

# broker information
broker = 'host.docker.internal'
port = 1883
topic = "python/mqtt"
client_id = f'publish-{random.randint(0, 1000)}' # Generates a Client ID with the publish prefix.

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", file=sys.stderr)
        else:
            print("Failed to connect, return code %d\n", rc, file=sys.stderr)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, msg, topic):

    # msg = f"messages: {msg_count}"
    result = client.publish(topic, msg)

    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`", file=sys.stderr)
    else:
        print(f"Failed to send message to topic {topic}", file=sys.stderr)

def on_message(client, userdata, msg):
    global chariots
    # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    if "front/in" in msg.topic:
        for char in msg.payload.decode():
            if ('a' <= char <= 'z') or char == ' ':
                incomming_buffer.append(char)
        return
    
    if "status" in msg.topic:
        if '1' in msg.topic:
            moving[0] = True if "start" in msg.payload.decode() else False
        elif '2' in msg.topic:
            moving[1] = True if "start" in msg.payload.decode() else False
        elif '3' in msg.topic:
            moving[2] = True if "start" in msg.payload.decode() else False
        elif '4' in msg.topic:
            moving[3] = True if "start" in msg.payload.decode() else False
        elif '5' in msg.topic:
            moving[4] = True if "start" in msg.payload.decode() else False
        elif '6' in msg.topic:
            moving[5] = True if "start" in msg.payload.decode() else False
        return

    try:
        jObject = json.loads(msg.payload.decode())

        if '1' in msg.topic:
            chariots[0] = (jObject["x"], jObject["y"])
        elif '2' in msg.topic:
            chariots[1] = (jObject["x"], jObject["y"])
        elif '3' in msg.topic:
            chariots[2] = (jObject["x"], jObject["y"])
        elif '4' in msg.topic:
            chariots[3] = (jObject["x"], jObject["y"])
        elif '5' in msg.topic:
            chariots[4] = (jObject["x"], jObject["y"])
        elif '6' in msg.topic:
            chariots[5] = (jObject["x"], jObject["y"])
    except json.JSONDecodeError:
        print("provided input was expected to be json, but was: ", msg.payload.decode())


    
client = connect_mqtt()
client.loop_start()

for topic in topics:
    client.subscribe(topic)

client.on_message = on_message

def send_paths(target_vertices, rotations): 

    # Randomly select 6 different starting vertices
    all_vertices = list(generate_graph(20).keys())
    starting_vertices = chariots

    # Print the starting and target vertices
    print("Starting vertices:", starting_vertices)
    print("Target vertices:", target_vertices)

    # Define empty array
    efficient_target_vertices = []

    # Calculate distance matrix
    distance_matrix = cdist(starting_vertices, target_vertices)

    # Apply Hungarian algorithm to find optimal assignment
    row_ind, col_ind = linear_sum_assignment(distance_matrix)

    # Print the assignments
    for i, j in zip(row_ind, col_ind):
        efficient_target_vertices.append(target_vertices[j])

    # Create a mapping between the original indices and the indices obtained from Hungarian algorithm
    index_mapping = {original_index: assigned_index for original_index, assigned_index in zip(range(len(target_vertices)), col_ind)}

    # Reorder the rotations list according to the mapping
    efficient_rotations = [rotations[index_mapping[i]] for i in range(len(target_vertices))]

    # Find the paths from each starting vertex to each target vertex
    paths = getPaths(starting_vertices, efficient_target_vertices)

    # If no paths are possible then return to start positions and try again
    if paths is None:
        print("No Paths found")
        if set(target_vertices) != letters[' ']:
            incomming_buffer.insert(0, ' ')
        return
    
    incomming_buffer.pop(0)

    for path in paths:
        print(path)

    # Collect paths into JSON objects
    json_objects = []
    i = 0
    for path in paths:
        json_path = [{"x": vertex[0], "y": vertex[1], "z": 0, "rotation": efficient_rotations[i]} for vertex in path]
        # json_path = [{"x": vertex[0], "y": vertex[1], "z": 0, "rotation": 0} for vertex in path]
        json_objects.append(json_path)
        i += 1

    # Send json paths to respective Chariots
    for i in range(6):
        # print(json.dumps(json_objects[i], indent=4))
        publish(client, json.dumps(json_objects[i]), target_topics[i])

while True:
    # Check for characters in the buffer and if present process these one by one
    if(len(incomming_buffer) > 0):
        incommingChar = incomming_buffer[0]
        targets = letters[incommingChar]
        rotationTargets = rotations[incommingChar]
        send_paths(targets, rotationTargets)

        time.sleep(2)
        while any(moving):
            print("incomming_buffer: ")
            print(incomming_buffer)
            time.sleep(1)
        # time.sleep(2)
    time.sleep(1)

