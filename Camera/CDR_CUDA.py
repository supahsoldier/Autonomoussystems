import cv2
from ultralytics import YOLO
import random
import sys
from paho.mqtt import client as mqtt_client
import json
import math
# pip install torch torchvision torchaudio
import torch

broker = '145.24.238.180'
port = 1883

# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!", file=sys.stderr)
        else:
            print(f"Failed to connect, return code {rc}", file=sys.stderr)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topic, cell_x, cell_y, rotation, posx, posy):
    data = {
        "x": cell_x,
        "y": cell_y,
        "posx": posx,
        "posy": posy,
        "rotation": rotation,
    }
    msg = json.dumps(data)
    result, _ = client.publish(topic, msg)
    if result == mqtt_client.MQTT_ERR_SUCCESS:
        print(f"Send `{msg}` to topic `{topic}`", file=sys.stderr)
    else:
        print(f"Failed to send message to topic {topic}", file=sys.stderr)

client = connect_mqtt()

cap = cv2.VideoCapture(1)

# Check if CUDA is available and move model to GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = YOLO("ChariotV3.pt").to(device)

# Get the width and height of the video frame
ret, frame = cap.read()
frame_height, frame_width = frame.shape[:2]

# Define the number of grid cells
grid_size = 20

# Calculate the size of each grid cell
cell_width = frame_width // grid_size
cell_height = frame_height // grid_size

# Create a dictionary to store the center coordinates of each cell
cell_centers = {}

# Calculate and store the center coordinates for each cell
for i in range(grid_size):
    for j in range(grid_size):
        cell_center_x = (i * cell_width) + (cell_width // 2)
        cell_center_y = (j * cell_height) + (cell_height // 2)
        adjusted_x = i - 10
        adjusted_y = j - 10
        cell_centers[(adjusted_x, adjusted_y)] = (cell_center_x, cell_center_y)

while True:
    success, chariotv2 = cap.read()
    if not success:
        break
    
    # Move image to GPU if necessary
    chariotv2_tensor = torch.from_numpy(chariotv2).unsqueeze(0).permute(0, 3, 1, 2).float().to(device)

    # Perform inference on GPU
    with torch.no_grad():
        results = model(chariotv2_tensor)

    classNames = model.names    

    for r in results:
        boxes = r.boxes
        keypoints = r.keypoints  # Assuming keypoints are stored in r.keypoints

        for i, box in enumerate(boxes):
            confidence = box.conf[0]
            if confidence >= 0.8:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Calculate the center coordinates (midpoint of the bounding box)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # Calculate the grid cell index
                cell_x = cx // cell_width
                cell_y = cy // cell_height

                # Adjust the cell coordinates to range from -10 to 10
                adjusted_cell_x = cell_x - 10
                adjusted_cell_y = cell_y - 10

                # Get the center of the cell from the dictionary
                cell_center = cell_centers.get((adjusted_cell_x, adjusted_cell_y))

                # Extract keypoints for the front and back of the object
                kp = keypoints[i].xy[0]  # Extract the first set of keypoints

                # Debugging: Print the keypoints to check if they are detected correctly
                print(f"Detected keypoints for object {i}: {kp}")

                if kp.shape[0] < 2:
                    print("Not enough keypoints detected for this object, skipping.")
                    continue  # Skip this object if it doesn't have the expected keypoints

                front_x, front_y = kp[0]
                back_x, back_y = kp[1]

                # Calculate the rotation angle in radians
                dx = front_x - back_x
                dy = front_y - back_y
                rotation_rad = math.atan2(dy, dx)

                # Convert radians to degrees
                rotation_deg = math.degrees(rotation_rad)

                # Adjust rotation angle to be within 0° to 360° range, starting from left
                rotation = 270 - rotation_deg  # Adjust to start from the left side
                rotation = rotation if rotation >= 0 else 360 + rotation

                # Print the center coordinates and the cell index for each detected object
                print(f"Object detected at: x={cx}, y={cy}, Cell=({adjusted_cell_x}, {adjusted_cell_y}), "
                      f"Cell Center X={cell_center[0]}, Cell Center Y={cell_center[1]}, Rotation={rotation:.2f}")

                # Publish the cell center coordinates and rotation to MQTT based on the detected class
                cls = int(box.cls[0])
                if classNames[cls] == 'ChariotY':
                    publish(client, "chariot/5/position", adjusted_cell_x, adjusted_cell_y, rotation, cx, cy)
                elif classNames[cls] == 'ChariotB':
                    publish(client, "chariot/6/position", adjusted_cell_x, adjusted_cell_y, rotation, cx, cy)

                cv2.rectangle(chariotv2, (x1, y1), (x2, y2), (255, 0, 255), 3)

                print("Confidence:", round(confidence.item(), 2))
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
                cell_text = f"Cell: ({adjusted_cell_x}, {adjusted_cell_y})"
                cell_org = (cx, cy - 10 if cy - 10 > 10 else cy + 10)
                cv2.putText(chariotv2, cell_text, cell_org, font, fontScale, color, thickness, cv2.LINE_AA)

    # Draw the grid lines for visualization
    for i in range(0, frame_width, cell_width):
        cv2.line(chariotv2, (i, 0), (i, frame_height), (255, 255, 255), 1)
    for j in range(0, frame_height, cell_height):
        cv2.line(chariotv2, (0, j), (frame_width, j), (255, 255, 255), 1)

    cv2.imshow('chariotv2Detect', chariotv2)
    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()