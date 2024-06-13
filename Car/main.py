import socket
import network
import time
import random
import math
from machine import Pin, PWM, ADC, I2C
import ujson as json  # Correctly import ujson for JSON parsing
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
bled.value(True)
built_in_led.value(True)
time.sleep(1)
built_in_led.value(False)
time.sleep(1)
fled.value(False)

# Initialize state
current_position = (0, 0)
target_path = []  # List to hold multiple target coordinates

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
def MoveForward(power, Stime):
    LeftMotor.duty_u16(7000)
    RightMotor.duty_u16(3000)
    time.sleep(Stime)
    LeftMotor.duty_u16(5000)
    RightMotor.duty_u16(5000)

def MoveBackward(power, Stime):
    LeftMotor.duty_u16(3000)
    RightMotor.duty_u16(7000)
    time.sleep(Stime)
    LeftMotor.duty_u16(5000)
    RightMotor.duty_u16(5000)

def MoveLeft(power, Stime):
    LeftMotor.duty_u16(5000)
    RightMotor.duty_u16(3000)
    time.sleep(Stime)
    LeftMotor.duty_u16(5000)
    RightMotor.duty_u16(5000)

def MoveRight(power, Stime):
    LeftMotor.duty_u16(7000)
    RightMotor.duty_u16(5000)
    time.sleep(Stime)
    LeftMotor.duty_u16(5000)
    RightMotor.duty_u16(5000)

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

# Callback for MQTT messages
def mqtt_callback(topic, msg):
    global current_position, target_path
    try:
        msg = msg.decode('utf-8')
        print(f'Received message on topic {topic}: {msg}')
        data = json.loads(msg)
        
        if topic == b'chariot/5/position':
            current_position = (data.get('x', 0), data.get('y', 0))
            print(f'Successfully got position: {current_position}')
        elif topic == b'chariot/5/target':
            if isinstance(data, list):
                target_path = [(point['x'], point['y']) for point in data]
                print(f'Target path has been delivered: {target_path}')
            else:
                print(f'Unexpected JSON structure for target path: {data}')
    except ValueError as e:
        print(f'Error parsing JSON: {e}')
    except TypeError as e:
        print(f'Error with JSON data: {e}')

# Function to publish messages
def publish(client, topic, message):
    try:
        client.publish(topic, message)
        print('Published:', message)
    except Exception as e:
        print(f'Failed to publish message: {e}')

# Function to drive towards target position
def drive_to_target():
    global current_position, target_path
    if target_path:
        next_target = target_path[0]
        dx = next_target[0] - current_position[0]
        dy = next_target[1] - current_position[1]
        distance = math.sqrt(dx**2 + dy**2)
        print(f"Current position: {current_position}, Next target: {next_target}, Distance: {distance}")
        
        # Start driving towards the target
        if distance > 0.9:
            angle = math.atan2(dy, dx)
            LeftMotor.duty_u16(int(5000 + 2000 * math.sin(angle)))
            RightMotor.duty_u16(int(5000 - 2000 * math.sin(angle)))
            print(f"Driving towards target: {next_target}")
        else:
            print(f"Reached target position: {next_target}")
            target_path.pop(0)  # Remove the reached target from the list
            LeftMotor.duty_u16(5000)  # Stop the motors
            RightMotor.duty_u16(5000)
            current_position = next_target  # Update current position

# Connect to Wi-Fi
connect_to_wifi()

# Connect to MQTT
mqtt_client = connect_to_mqtt()
if mqtt_client:
    mqtt_client.set_callback(mqtt_callback)

    # Subscribe to topics
    result_position = mqtt_client.subscribe(b'chariot/5/position')
    result_target = mqtt_client.subscribe(b'chariot/5/target')

    # Main loop for handling MQTT messages and driving
    while True:
        mqtt_client.check_msg()
        drive_to_target()
        time.sleep(0.1)
else:
    print('MQTT client not connected')
