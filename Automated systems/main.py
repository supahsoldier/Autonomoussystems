import socket
import network
import time
import random
import math
from machine import Pin, PWM, ADC, I2C
import ujson as json  # Correctly import ujson for JSON parsing
#from vl53l0x import VL53L0X
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
built_in_led = machine.Pin("LED", machine.Pin.OUT)
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
target_position = None

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
    return client

# Callback for MQTT messages
def mqtt_callback(topic, msg):
    global current_position, target_position
    try:
        msg = msg.decode('utf-8')
        print(f'Received message on topic {topic}: {msg}')
        data = json.loads(msg)
        
        # Ensure data is a list containing a dictionary
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            data = data[0]  # Extract the dictionary from the list
        
        if isinstance(data, dict):
            if topic == b'chariot/6/position':
                current_position = (data.get('x', 0), data.get('y', 0))
                print(f'Successfully got position: {current_position}')
            elif topic == b'chariot/6/target':
                target_position = (data.get('x', 0), data.get('y', 0))
                print(f'Target position has been delivered: {target_position}')
        else:
            print(f'Unexpected JSON structure: {data}')
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
    global current_position, target_position
    if target_position:
        dx = target_position[0] - current_position[0]
        dy = target_position[1] - current_position[1]
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 1:
            print("Reached target position")
            target_position = None
            return
        
        angle = math.atan2(dy, dx)
        speed = 50  # Adjust as necessary
        LeftMotor.duty_u16(int(5000 + 2000 * math.sin(angle)))
        RightMotor.duty_u16(int(5000 - 2000 * math.sin(angle)))
        time.sleep(0.1)
        LeftMotor.duty_u16(5000)
        RightMotor.duty_u16(5000)

# Connect to Wi-Fi
connect_to_wifi()

# Connect to MQTT
mqtt_client = connect_to_mqtt()
mqtt_client.set_callback(mqtt_callback)

# Subscribe to topics
result_position = mqtt_client.subscribe(b'chariot/6/position')
result_target = mqtt_client.subscribe(b'chariot/6/target')

if result_position == 1 and result_target == 1:
    print('Successfully subscribed to topics')
else:
    print('Failed to subscribe to topics')

# Main loop for handling MQTT messages and driving
while True:
    mqtt_client.check_msg()
    drive_to_target()
    time.sleep(0.1)
    print(f'waiting')

