#!/usr/bin/env python

import argparse
import os
from uuid import uuid4
from faker import Faker
import random
from time import sleep

from six.moves import input

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.
    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def main(args):
    topic = args.topic
    is_specific = args.specific == "true"

    if is_specific:
        schema = "user_tracker.avsc"
    else:
        schema = "user_tracker.avsc"

    path = os.path.realpath(os.path.dirname(
        __file__).replace("producer", "schemas"))
    with open(f"{path}/{schema}") as f:
        schema_str = f.read()

    schema_registry_conf = {'url': args.schema_registry}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema_str)

    string_serializer = StringSerializer('utf_8')

    producer_conf = {'bootstrap.servers': args.bootstrap_servers}

    producer = Producer(producer_conf)

    print("Producing user records to topic {}. ^C to exit.".format(topic))

    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)
        try:
            user = {
                'user_id': fake.random_int(min=20000, max=100000),
                'user_name': fake.name(),
                'user_address': fake.street_address() + ' | ' + fake.city() + ' | ' + fake.country_code(),
                'platform': random.choice(['Mobile', 'Laptop', 'Tablet']),
                'signup_at': str(fake.date_time_this_month())
            }

            producer.produce(topic=topic,
                             key=(str(uuid4())),
                             value=avro_serializer(
                                 user, SerializationContext(topic, MessageField.VALUE)),
                             on_delivery=delivery_report)
        except KeyboardInterrupt:
            break
        except ValueError:
            print("Invalid input, discarding record...")
            continue

        sleep(args.sleep_time)

    print("\nFlushing records...")
    producer.flush()


if __name__ == '__main__':
    fake = Faker()

    parser = argparse.ArgumentParser(description="AvroSerializer example")
    parser.add_argument('-b', dest="bootstrap_servers",
                        help="Bootstrap broker(s) (host[:port])", default="localhost:29092")
    parser.add_argument('-s', dest="schema_registry",
                        help="Schema Registry (http(s)://host[:port]", default="http://localhost:8085")
    parser.add_argument('-t', dest="topic", default="example_avro",
                        help="Topic name")
    parser.add_argument('-p', dest="specific", default="true",
                        help="Avro specific record")
    parser.add_argument('-st', dest="sleep_time", default=2,
                        type=int, help="sleep_time")

    main(parser.parse_args())
