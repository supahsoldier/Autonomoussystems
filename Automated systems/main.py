import socket
import network
import time
import random
from machine import Pin, PWM, ADC, I2C
import ujson as json  # Correctly import ujson for JSON parsing
#from vl53l0x import VL53L0X
from simple import MQTTClient

BUILT_IN_LED=25
FLED=20
BLED=21
PWM_LM=6
PWM_RM=7
PWM_SC=10
SDA=4
SCL=5
MISO=16
MOSI=19
SCK=18
CS=17

# Insert your network parameters
ssid = b'Gast4'
pwd = b'G*st4l@@r'

# MQTT server parameters
mqtt_server = '145.137.20.240'
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

# Set up I2C for VL53L0X
#i2c = I2C(0, scl=Pin(SCL), sda=Pin(SDA), freq=400000)
#sensor = VL53L0X(i2c)
#sensor.start()

# Load the local page content
page = open("main.html", "r")
html = page.read()
page.close()

# Function to control servos
def MoveForward(power, Stime):
    #if not obstacle_detected():
        LeftMotor.duty_u16(7000)
        RightMotor.duty_u16(3000)
        time.sleep(Stime)
        LeftMotor.duty_u16(5000)
        RightMotor.duty_u16(5000)
    #else:
     #   print("Obstacle detected! Stopping.")

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
    print(f'looking for data')
    global current_position, target_position
    msg = msg.decode('utf-8')
    data = json.loads(msg)
    if topic == b'chariot/1/position':
        current_position = (data['x'], data['y'])
        print(f'Succesfully got position')
        print(current_position)
    elif topic == b'chariot/1/target':
        target_position = (data['x'], data['y'])
        print(f'target position has been deliverd') 

# Function to publish messages
def publish(client, topic, message):
    try:
        client.publish(topic, message)
        print('Published:', message)
    except Exception as e:
        print(f'Failed to publish message: {e}')

# Function to detect obstacles
#def obstacle_detected():
 #   distance = sensor.read()
  #  print(f"Distance: {distance} mm")
   # return distance < 200
   
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
result_position = mqtt_client.subscribe(b'chariot/1/position')
result_target = mqtt_client.subscribe(b'chariot/1/target')


# Listen on port 80
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
print("Listening to port 80\n")
s.listen(1)

while True:
    mqtt_client.check_msg()
    drive_to_target()
    time.sleep(0.1)
    print(f'waiting')

#     cl, addr = s.accept()
#     print("Incoming connection request from: " + str(addr) + "\n")
#     cl_file = cl.makefile('rwb', 0)
#     found = False
#     while True:
#         line = cl_file.readline()
#         if not line or line == b'\r\n':
#             break
#         if not found:
#             if str(line).find("/?PRESS=FRONT_LED_ON") != -1:
#                 fled.value(True)
#                 #publish(mqtt_client, 'pico/actions', 'FRONT_LED_ON')
#                 found = True
#             if str(line).find("/?PRESS_1=FRONT_LED_OFF") != -1:
#                 fled.value(False)
#                # publish(mqtt_client, 'pico/actions', 'FRONT_LED_OFF')
#                 found = True
#             if str(line).find("/?PRESS_2=BACK_LED_ON") != -1:
#                 bled.value(True)
#               #  publish(mqtt_client, 'pico/actions', 'BACK_LED_ON')
#                 found = True
#             if str(line).find("/?PRESS_3=BACK_LED_OFF") != -1:
#                 bled.value(False)
#          #       publish(mqtt_client, 'pico/actions', 'BACK_LED_OFF')
#                 found = True
#             if str(line).find("/?PRESS_4=MOVE") != -1:
#                 MoveForward(50, 1)
#           #      publish(mqtt_client, 'pico/actions', 'MOVE')
#                 found = True
#             if str(line).find("/?PRESS_5=LEFT") != -1:
#                 MoveLeft(50, 1)
#            #     publish(mqtt_client, 'pico/actions', 'LEFT')
#                 found = True
#             if str(line).find("/?PRESS_6=RIGHT") != -1:
#                 MoveRight(50, 1)
#             #    publish(mqtt_client, 'pico/actions', 'RIGHT')
#                 found = True
#             if str(line).find("/?PRESS_7=BACK") != -1:
#                 MoveBackward(50, 1)
#              #   publish(mqtt_client, 'pico/actions', 'BACK')
#                 found = True
# 
#     response = html
#     cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
#     cl.send(response)
#     cl.close()

