import argparse
import os

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer


class User(object):
    def __init__(self, user_id, user_name, user_address, platform, signup_at):
        self.user_id = user_id
        self.user_name = user_name
        self.user_address = user_address
        self.platform = platform
        self.signup_at = signup_at


def dict_to_user(obj, ctx):
    """
    Converts object literal(dict) to a User instance.
    Args:
        obj (dict): Object literal(dict)
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
    """

    if obj is None:
        return None

    # User._address must not be serialized; omit from dict
    return User(
        user_id=obj.get('user_id'),
        user_name=obj.get('user_name'),
        user_address=obj.get('user_address'),
        platform=obj.get('platform'),
        signup_at=obj.get('signup_at')
    )


def main(args):
    topic = args.topic
    is_specific = args.specific == "true"

    if is_specific:
        schema = "user_tracker.avsc"
    else:
        schema = "user_tracker.avsc"

    path = os.path.realpath(os.path.dirname(
        __file__).replace("consumer", "schemas").replace("Python", ""))
    with open(f"{path}/{schema}") as f:
        schema_str = f.read()

    sr_conf = {'url': args.schema_registry}
    schema_registry_client = SchemaRegistryClient(sr_conf)

    avro_deserializer = AvroDeserializer(schema_registry_client,
                                         schema_str,
                                         dict_to_user)

    consumer_conf = {'bootstrap.servers': args.bootstrap_servers,
                     'group.id': args.group,
                     'auto.offset.reset': "earliest"}

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            user = avro_deserializer(msg.value(), SerializationContext(
                msg.topic(), MessageField.VALUE))
            if user is not None:
                print("record: {}\n"
                      "\tid: {}\n"
                      "\tname: {}\n"
                      "\taddress: {}\n"
                      "\tplatform: {}\n"
                      "\tsignup_at: {}\n"
                      .format(msg.key(), user.user_id,
                              user.user_name,
                              user.user_address,
                              user.platform,
                              user.signup_at))
        except KeyboardInterrupt:
            break

    consumer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AvroDeserializer example")
    parser.add_argument('-b', dest="bootstrap_servers", default="localhost:29092",
                        help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry", default="http://localhost:8085",
                        help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="example_avro",
                        help="Topic name")
    parser.add_argument('-g', dest="group", default="example_avro",
                        help="Consumer group")
    parser.add_argument('-p', dest="specific", default="true",
                        help="Avro specific record")

    main(parser.parse_args())
