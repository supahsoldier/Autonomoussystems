import socket
import network
import time
import random
import math
from machine import Pin, PWM, ADC, I2C
import ujson as json 
from simple import MQTTClient

BUILT_IN_LED = 25
FLED = 20
BLED = 21
PWM_LM = 6
PWM_RM = 7
PWM_SC = 10
SDA = 4
SCL = 5
MISO = 16
MOSI = 19
SCK = 18
CS = 17

# Insert your network parameters
ssid = b'tesla iot'
pwd = b'fsL6HgjN'

# MQTT server parameters
mqtt_server = '145.24.238.180'
mqtt_port = 1883
client_id = f'pico-{random.randint(0,1000)}'

# Initial state definition
built_in_led = Pin("LED", Pin.OUT)
fled = Pin(FLED, Pin.OUT)
bled = Pin(BLED, Pin.OUT)
fled.value(True)
bled.value(False)
built_in_led.value(True)
time.sleep(1)
built_in_led.value(False)
time.sleep(1)
fled.value(True)

# Initialize state
current_position = (0, 0, 0)  # (x, y, rotation)
target_path = []  # List of target positions
target_received = False  # Flag to see if the target path has been received

# Set up servos
LeftMotor = PWM(Pin(PWM_LM))
LeftMotor.freq(50)
RightMotor = PWM(Pin(PWM_RM))
RightMotor.freq(50)
PanMotor = PWM(Pin(PWM_SC))
PanMotor.freq(50)

# Load the local page content
page = open("main.html", "r")
html = page.read()
page.close()

# Function to control servos
def MoveForward():
    LeftMotor.duty_u16(5150)  
    RightMotor.duty_u16(4500)  
    time.sleep(0.5)
    StopMotors()

def MoveBackward():
    LeftMotor.duty_u16(4500) 
    RightMotor.duty_u16(5210)  
    time.sleep(0.5)
    StopMotors()

def StopMotors():
    LeftMotor.duty_u16(5000)
    RightMotor.duty_u16(5000)

def RotateLeft():
    LeftMotor.duty_u16(4500) 
    RightMotor.duty_u16(4500) 
    time.sleep(0.1)
    StopMotors()
    
def RotateRight():
    LeftMotor.duty_u16(5200)  
    RightMotor.duty_u16(5200)  
    time.sleep(0.1)
    StopMotors()

# Function to connect to Wi-Fi
def connect_to_wifi():
    network.hostname("mypicow")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Hostname set to: " + str(network.hostname()))

    time0 = time.time()
    wlan.connect(ssid, pwd)
    while 1:
        if wlan.isconnected():
            print("\nConnected!\n")
            built_in_led.value(True)
            break
        else:
            print(".")
            time.sleep(1)
            if time.time() - time0 > 10:
                print("Connection could not be established")
                break

    sta_if = network.WLAN(network.STA_IF)
    print(sta_if.ifconfig()[0])

# Function to connect to MQTT
def connect_to_mqtt():
    client = MQTTClient(client_id, mqtt_server, port=mqtt_port, user=None, password=None, ssl=False, keepalive=720)
    try:
        client.connect()
        print(f'Connected to {mqtt_server} MQTT broker')
    except Exception as e:
        print(f'Failed to connect to MQTT broker: {e}')
        return None
    return client

# Callback function to handle MQTT messages
def mqtt_callback(topic, msg):
    global current_position, target_path, target_received
    try:
        msg = msg.decode('utf-8')
        print(f'Received message on topic {topic}: {msg}')
        data = json.loads(msg)
        
        if topic == b'chariot/2/position':
            current_position = (data.get('x', 0), data.get('y', 0), data.get('rotation', 0))
            print(f'Successfully got position: {current_position}')
        elif topic == b'chariot/2/target':
            if isinstance(data, list) and len(data) > 1:
                # the first coordinate is the current position, so will be skipped
                target_path = [(point['x'], point['y'], (point.get('rotation', 0) + 180) % 360) for point in data[1:]]
                target_received = True
                print(f'Target path has been delivered: {target_path}')
            elif isinstance(data, list) and len(data) == 1:
                print('Only one coordinate received, skipping as it is the current position.')
            else:
                print(f'Unexpected JSON structure for target path: {data}')
    except ValueError as e:
        print(f'Error parsing JSON: {e}')
    except TypeError as e:
        print(f'Error with JSON data: {e}')


# Fuction to publish messages to MQTT
def publish(client, topic, message):
    try:
        client.publish(topic, message)
        print('Published:', message)
    except Exception as e:
        print(f'Failed to publish message: {e}')

def normalize_rotation(rotation):
    return rotation % 360

def is_within_tolerance(value, target, tolerance=15):
    return abs(value - target) % 360 <= tolerance or abs(value - target) % 360 >= (360 - tolerance)

# Function to drive towards target position following the target_path
def drive_to_target():
    global current_position, target_path
    if target_path:
        target = target_path[0]
        target_x, target_y, end_rotation = target
        
        # Calculate the required rotation to move towards the target
        dx = target_x - current_position[0]
        dy = target_y - current_position[1]
        
        if dx == 1:
            required_rotation = 0  # Moving right
        elif dx == -1:
            required_rotation = 180  # Moving left
        elif dy == -1:
            required_rotation = 90  # Moving up
        elif dy == 1:
            required_rotation = 270  # Moving down
        else:
            required_rotation = current_position[2]  # Stay in the same direction
        
        current_rotation = normalize_rotation(current_position[2])
        
        # check if the car is in the tolerance range to move forward or backward
        if is_within_tolerance(current_rotation, required_rotation, tolerance=15):
            print("Moving Forward")
            MoveForward()
        elif is_within_tolerance((current_rotation + 180) % 360, required_rotation, tolerance=15):
            print("Moving Backward")
            MoveBackward()
        else:
            # Rotate the car to the required rotation
            if (required_rotation - current_rotation + 360) % 360 > 180:
                print("Rotating Left")
                RotateLeft()
            else:
                print("Rotating Right")
        
        # Check if the car has reached the target position
        if (current_position[0], current_position[1]) == (target_x, target_y):
            target_path.pop(0)
            current_position = (target_x, target_y, current_rotation)  # Keep current rotation
            
            if not target_path:
                # Chariot reached the final target, adjust rotation to match the end rotation with a tolerance
                while not is_within_tolerance(current_rotation, end_rotation, tolerance=15):
                    if (end_rotation - current_rotation + 360) % 360 > 180:
                        RotateLeft()
                    else:
                        RotateRight()
                    time.sleep(0.1)
                    mqtt_client.check_msg()
                    current_rotation = normalize_rotation(current_position[2])  # Update current rotation
                StopMotors()
                publish(mqtt_client, b'chariot/2/status', 'stop')
                return
            
        mqtt_client.check_msg()  # Check for update on position messages
        time.sleep(0.1)
    
# Connect to Wi-Fi
connect_to_wifi()

# Connect to MQTT
mqtt_client = connect_to_mqtt()
if mqtt_client:
    mqtt_client.set_callback(mqtt_callback)

    # Subscribe to the mqtt topics
    result_position = mqtt_client.subscribe(b'chariot/2/position')
    result_target = mqtt_client.subscribe(b'chariot/2/target')

    # Main loop that handles MQTT messages and driving
    while True:
        mqtt_client.check_msg()
        if target_received:
            publish(mqtt_client, b'chariot/2/status', 'start')
            target_received = False 
        drive_to_target()
        time.sleep(0.1)
else:
    print('MQTT client not connected')