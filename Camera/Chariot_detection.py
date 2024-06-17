import cv2
from ultralytics import YOLO
import random
import sys
from paho.mqtt import client as mqtt_client
import json 

broker = '145.24.238.180'
port = 1883

# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", file=sys.stderr)
        else:
            print("Failed to connect, return code %d\n", rc, file=sys .stderr)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, x, y):
    data = {
        "x": cell_x,
        "y": cell_y,
        "z": 0,
        "rotation": 0.0,    
    }
    msg = json.dumps(data)
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`", file=sys.stderr)
    else:
        print(f"Failed to send message to topic {topic}", file=sys.stderr)

def publishabsolute(client, topic):
    data = {
        "posx": cx,
        "posy": cy,    
    }
    msg = json.dumps(data)
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`", file=sys.stderr)
    else:
        print(f"Failed to send message to topic {topic}", file=sys.stderr)

def publishcenter(client, topic):
    data = {
        "x": str(cell_centers.get(cell_x)),
        "y": str(cell_centers.get(cell_y)) 
    }
    msg = json.dumps(data)
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`", file=sys.stderr)
    else:
        print(f"Failed to send message to topic {topic}", file=sys.stderr)

client = connect_mqtt()

cap = cv2.VideoCapture(1)
model = YOLO("chariotv2.pt")

# Get the width and height of the video frame
ret, frame = cap.read()
frame_height, frame_width = frame.shape[:2]

# Define the number of grid cells
grid_size = 20

# Calculate the size of each grid cell
cell_width = frame_width // grid_size
cell_height = frame_height // grid_size

# Calculate the range for grid coordinates
coordinate_range = grid_size // 2

# Create a dictionary to store the center coordinates of each cell
cell_centers = {}

# Calculate and store the center coordinates for each cell
for i in range(-coordinate_range, coordinate_range):
    for j in range(-coordinate_range, coordinate_range):
        cell_center_x = ((i + coordinate_range) * cell_width) + (cell_width // 2)
        cell_center_y = ((j + coordinate_range) * cell_height) + (cell_height // 2)
        cell_centers[(i, j)] = (cell_center_x, cell_center_y)

while True:
    success, chariotv2 = cap.read()
    if not success:
        break
    
    results = model(chariotv2)
    classNames = model.names    

    for r in results:
        boxes = r.boxes

        for box in boxes:
            confidence = box.conf[0]
            if confidence >= 0.6:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Calculate the center coordinates (midpoint of the bounding box)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # Calculate the grid cell index
                cell_x = (cx // cell_width) - coordinate_range
                cell_y = (cy // cell_height) - coordinate_range

                # Get the center of the cell from the dictionary
                cell_center = cell_centers.get((cell_x, cell_y))

                # Print the center coordinates and the cell index for each detected object
                print(f"Object detected at: x={cx}, y={cy}, Cell=({cell_x}, {cell_y}), Cell Center={cell_center}")

                # Publish the cell center coordinates to MQTT based on the detected class
                cls = int(box.cls[0])
                if classNames[cls] == 'chariot':
                    publish(client, "chariot/5/position", cell_center[0], cell_center[1])
                    publishabsolute(client, "chariot/5/absolute")
                    publishcenter(client, "chariot/5/center")
                elif classNames[cls] == 'chariot2':
                    publish(client, "chariot/6/position", cell_center[0], cell_center[1])

                cv2.rectangle(chariotv2, (x1, y1), (x2, y2), (255, 0, 255), 3)

                print("Confidence:", round(confidence.item(), 2))
                cls = int(box.cls[0])
                print("Detection:", classNames[cls])

                # Define the text properties
                text = f"{classNames[cls]}: {round(confidence.item(), 2)}"
                org = (x1, y1 - 10 if y1 - 10 > 10 else y1 + 10)  # To position the text above the bounding box
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 0.5
                color = (255, 0, 0)
                thickness = 2

                # Draw the class name above the bounding box
                cv2.putText(chariotv2, text, org, font, fontScale, color, thickness, cv2.LINE_AA)

                # Optionally, draw the center point for visualization
                cv2.circle(chariotv2, (cx, cy), 5, (0, 255, 0), -1)

                # Display the cell index
                cell_text = f"Cell: ({cell_x}, {cell_y})"
                cell_org = (cx, cy - 10 if cy - 10 > 10 else cy + 10)
                cv2.putText(chariotv2, cell_text, cell_org, font, fontScale, color, thickness, cv2.LINE_AA)

    # Draw the grid lines for visualization
    for i in range(grid_size):
        x = i * cell_width
        cv2.line(chariotv2, (x, 0), (x, frame_height), (255, 255, 255), 1)
    for j in range(grid_size):
        y = j * cell_height
        cv2.line(chariotv2, (0, y), (frame_width, y), (255, 255, 255), 1)

    cv2.imshow('chariotv2Detect', chariotv2)
    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
