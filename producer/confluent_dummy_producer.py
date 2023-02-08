#!/usr/bin/env python

from confluent_kafka import Producer
from faker import Faker
import json
import time
import logging
import random

fake = Faker()

####################################
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='producer.log',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

###################################
p = Producer({'bootstrap.servers': 'localhost:29092',
             'client.id': 'python-producer'})
print('Kafka Producer has been initiated...')
###################################


def receipt(err, msg):
    if err is not None:
        print('Error: {}'.format(err))
    else:
        message = 'Produced message on topic {} with value of {}\n'.format(
            msg.topic(), msg.value().decode('utf-8'))
        logger.info(message)
        print(message)
####################################

# Before shipping data to Kafka, the main() function is calling poll()
# to request any previous events to the producer. If found, events are sent to the callback function (receipt).
# In this case, p.poll(1) means that a timeout of 1 second is allowed.

# Eventually, the producer is also flushed ( p.flush()), that means blocking it until previous messaged have been delivered effectively,
# to make it synchronous.


def main():
    while True:
        data = {
            'user_id': fake.random_int(min=20000, max=100000),
            'user_name': fake.name(),
            'user_address': fake.street_address() + ' | ' + fake.city() + ' | ' + fake.country_code(),
            'platform': random.choice(['Mobile', 'Laptop', 'Tablet']),
            'signup_at': str(fake.date_time_this_month())
        }
        m = json.dumps(data)
        p.poll(1)
        p.produce('user-tracker', m.encode('utf-8'), callback=receipt)
        p.flush()
        time.sleep(5)


if __name__ == '__main__':
    main()
