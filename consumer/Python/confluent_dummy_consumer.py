from confluent_kafka import Consumer

################
c = Consumer({'bootstrap.servers': 'localhost:29092',
             'group.id': 'python-consumer', 'auto.offset.reset': 'earliest'})
print('Kafka Consumer has been initiated...')
################

# The consumer is subscribed to the topic user-tracker
print('Available topics to consume: ', c.list_topics().topics)

# If the topic does not exist, the consumer will not be able to consume any data.
if 'user-tracker' in c.list_topics().topics:
    c.subscribe(['user-tracker'])
    print('Subscribed to topic: user-tracker')
else:
    print('Topic user-tracker does not exist. Please create it first.')


def main():
    while True:
        msg = c.poll(1.0)  # timeout
        if msg is None:
            continue
        if msg.error():
            print('Error: {}'.format(msg.error()))
            continue
        data = msg.value().decode('utf-8')
        print(data)
    c.close()


if __name__ == '__main__':
    main()
