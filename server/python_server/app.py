import random
import time
import sys
from paho.mqtt import client as mqtt_client

broker = 'host.docker.internal'
port = 1883
topic = "python/mqtt"
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
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`", file=sys.stderr)
        else:
            print(f"Failed to send message to topic {topic}", file=sys.stderr)
        msg_count += 1
        if msg_count > 50:
            break


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    run()



# Example camera:
# url = "http://192.168.2.18:1973/shot.jpg"
# file_path = "downloaded_image.jpg"
# download_jpg(url, file_path)
