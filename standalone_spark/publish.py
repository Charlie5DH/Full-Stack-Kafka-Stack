import os
from uuid import uuid4
import io
from kafka import KafkaProducer
from avro.schema import Parse
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
import json

from _prod_utils import delivery_report

# Added confluent native avro serialization and python client
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

import configparser
config = configparser.ConfigParser()
config.read("configurations/configurations.ini")


# serialize object to json and publish message to kafka topic
def publish_to_kafka(topic, message):
    #configs = get_configs()

    bootstrap_servers = config["KAFKA"]["bootstrap_servers"]
    auth_method = config["KAFKA"]["auth_method"]
    sasl_username = config["KAFKA"]["sasl_username"]
    sasl_password = config["KAFKA"]["sasl_password"]

    configs = {"bootstrap_servers": bootstrap_servers}

    if auth_method == "sasl_scram":
        configs["security_protocol"] = "SASL_SSL"
        configs["sasl_mechanism"] = "SCRAM-SHA-512"
        configs["sasl_plain_username"] = sasl_username
        configs["sasl_plain_password"] = sasl_password

    producer = KafkaProducer(
        value_serializer=lambda v: json.dumps(vars(v)).encode("utf-8"),
        **configs,
    )
    producer.send(topic, value=message)
    print("Topic: {0}, Value: {1}".format(topic, message))

# serialize object to json and publish message to kafka topic


def publish_avro(topic, message):
    bootstrap_servers = config["KAFKA"]["bootstrap_servers"]
    auth_method = config["KAFKA"]["auth_method"]
    sasl_username = config["KAFKA"]["sasl_username"]
    sasl_password = config["KAFKA"]["sasl_password"]

    configs = {"bootstrap.servers": bootstrap_servers}
    schema_registry_url = config["KAFKA"]["schema_registry_url"]

    # Create a Kafka client ready to produce messages
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    # Get the schema to use to serialize the message
    schema = Parse(open(message.schema_path(), "rb").read())

    # serialize the message data using the schema
    buf = io.BytesIO()
    encoder = BinaryEncoder(buf)
    writer = DatumWriter(writer_schema=schema)
    writer.write(message.to_dict(), encoder)
    buf.seek(0)
    message_data = (buf.read())

    # message key if needed
    key = None

    # headers if needed
    headers = []

    # Send the serialized message to the Kafka topic
    producer.send(topic,
                  message_data,
                  key,
                  headers)
    print("Topic: {0}, Value: {1}".format(topic, message))
    producer.flush()


def publish_to_kafka_avro(topic, message):

    path = os.path.realpath(os.path.dirname(
        __file__)) + "/schema/" + message.schema_name() + ".avsc"
    with open(f"{path}") as f:
        schema = f.read()

    schema_registry_conf = {'url': config["KAFKA"]["schema_registry_url"]}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema)

    string_serializer = StringSerializer('utf_8')

    producer_conf = {'bootstrap.servers': config["KAFKA"]["bootstrap_servers"]}

    producer = Producer(producer_conf)
    producer.poll(0.0)

    try:
        message = message.to_dict()

        producer.produce(topic=topic,
                         key=(str(uuid4())),
                         value=avro_serializer(
                             message, SerializationContext(topic, MessageField.VALUE)),
                         # on_delivery=delivery_report
                         )
        print("Topic: {0}, Value: {1}".format(topic, message))

    except BufferError as e:
        print("Local producer queue is full ({0} messages awaiting delivery): try again".format(
            len(producer)))
    except Exception as e:
        print(e)
        pass
    except KeyboardInterrupt:
        pass
    except ValueError:
        print("Invalid input, discarding record...")
    producer.flush()
