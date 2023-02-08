'''
MQTT is a binary based protocol where the control elements are binary bytes and not text strings. 
Topic names, Client ID, User names and Passwords are encoded as stream of bytes using UTF-8.
'''

import time
import json
import numpy as np
import datetime as dt
import paho.mqtt.client as mqtt


def on_publish(client, userdata, mid):
    print("sent a message")


mqttClient = mqtt.Client("engine_data")
mqttClient.on_publish = on_publish
mqttClient.connect('localhost', 1883)
# start a new thread
mqttClient.loop_start()

# Why use msg.encode('utf-8') here
# MQTT is a binary based protocol where the control elements are binary bytes and not text strings.
# Topic names, Client ID, Usernames and Passwords are encoded as stream of bytes using UTF-8.
while True:
    msg = {
        "sensor_id": "sensor_1",
        "vibration": np.random.randint(0, 100),
        "acceleration_x": np.random.randint(0, 100),
        "acceleration_y": np.random.randint(0, 100),
        "acceleration_z": np.random.randint(0, 100),
        "timestamp": dt.datetime.now().isoformat()
    }
    info = mqttClient.publish(
        topic='engine_measures',
        payload=json.dumps(msg).encode('utf-8'),
        qos=0,
    )
    # Because published() is not synchronous,
    # it returns false while he is not aware of delivery that's why calling wait_for_publish() is mandatory.
    info.wait_for_publish()
    print("Message published: ", info.is_published())
    time.sleep(3)
