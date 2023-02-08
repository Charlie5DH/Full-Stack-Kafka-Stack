import paho.mqtt.client as mqtt

'''
Taken and adapted from https://python.plainenglish.io/mqtt-beginners-guide-in-python-38590c8328ae
When a client subscribes to a topic, it is basically telling the broker to send messages to it that are sent to the broker on that topic. —paho-mqtt
Most of the examples just give some codes that can only handle messages from one topic, which is not so good. 
Because most time, we want to handle different messages from different topics separately, e.g., use different functions.

loop_forever() will make our program run forever, but it will block the program. This means that the other codes below client.
loop_forever will never be executed. So what if we need to display the data on a screen which requires a while loop. 
This means we have to process data from the mqtt server and display it on screen at the same time. 
And now we need loop_start() function.
'''


def on_message_temperature(client, userdata, msg):
    # a callback function
    # Message is an object and the payload property contains the message data which is binary data.
    # The actual message payload is a binary buffer.
    # In order to decode this payload you need to know what type of data was sent.
    # If it is JSON formatted data then you decode it as a string and then decode the JSON string as follows:
    # decoded_message=str(message.payload.decode("utf-8")))
    # msg=json.loads(decoded_message)
    print('Received a new temperature data ', str(msg.payload.decode('utf-8')))
    print('message topic=', msg.topic)
    print('message qos=', msg.qos)


def on_message_humidity(client, userdata, msg):
    print('Received a new humidity data ', str(msg.payload.decode('utf-8')))


# Give a name to this MQTT client
client = mqtt.Client('greenhouse_server')
client.message_callback_add('greenhouse/temperature', on_message_temperature)
client.message_callback_add('greenhouse/humidity', on_message_humidity)

# IP address of your MQTT broker, using ipconfig to look up it
client.connect('localhost', 1883)
# 'greenhouse/#' means subscribe all topic under greenhouse
client.subscribe('greenhouse/#')

client.loop_forever()
# stop the loop
# client.loop_stop()

# while True:
# time.sleep(6)
# do something you like
