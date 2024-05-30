import cv2
from roboflow import Roboflow
import sys
import random
import time
import sys
from paho.mqtt import client as mqtt_client

broker = '145.137.22.244'
port = 1883
topic = "chariot/1/position"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

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


def publish(client):
    msg = str(class_counts)
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`", file=sys.stderr)
    else:
        print(f"Failed to send message to topic {topic}", file=sys.stderr)


# Replace with your actual Roboflow API key
api_key = "nBZ6SNqSQr7WktcP0BUK"  # Insert your API key here
project_id = "chariot-yvuqc"
model_version = "1"

try:
    # Initialize the Roboflow API
    rf = Roboflow(api_key=api_key)
    project = rf.workspace().project(project_id)
    model = project.version(model_version).model
    print("Roboflow model loaded successfully.")
except Exception as e:
    print(f"Failed to load Roboflow model: {e}")
    sys.exit(1)

client = connect_mqtt()

# Open the webcam feed
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit(1)

# Dictionary to store the count of detected classes
class_counts = {}

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert the frame to RGB (Roboflow expects RGB images)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    try:
        # Predict the frame using the Roboflow model
        predictions = model.predict(rgb_frame, confidence=40, overlap=30).json()
        print(predictions)  # Debug: Print predictions
    except Exception as e:
        print(f"Prediction error: {e}")
        continue

    # Clear the class counts dictionary for the new frame
    class_counts.clear()

    # Draw bounding boxes on the frame and count the classes
    for prediction in predictions.get('predictions', []):
        x0, y0, x1, y1 = (int(prediction['x'] - prediction['width'] // 2),
                          int(prediction['y'] - prediction['height'] // 2),
                          int(prediction['x'] + prediction['width'] // 2),
                          int(prediction['y'] + prediction['height'] // 2))
        label = prediction['class']
        confidence = prediction['confidence']

        # Update the class count
        if label in class_counts:
            class_counts[label] += 1
        else:
            class_counts[label] = 1

        # Draw the bounding box and label
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} ({confidence:.2f})", (x0, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    publish(client)

    # Print the class counts (or send them to a server)
    print(class_counts)  # You can replace this with your server code

    # Press Q on keyboard to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
