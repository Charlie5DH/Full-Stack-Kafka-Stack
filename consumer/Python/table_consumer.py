import argparse
import os

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer


class Orders(object):
    def __init__(self, order_count, total_value_usd, window_start_ts, make):
        self.window_start_ts = window_start_ts
        self.order_count = order_count
        self.total_value_usd = total_value_usd
        self.make = make


def dict_to_orders(obj, ctx):
    """
    Converts object literal(dict) to a Orders instance.
    Args:
        obj (dict): Object literal(dict)
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
    """

    if obj is None:
        return None

    # User._address must not be serialized; omit from dict
    return Orders(
        window_start_ts=obj.get(str('window_start_ts').upper()),
        order_count=obj.get(str('order_count').upper()),
        total_value_usd=obj.get(str('total_value_usd').upper()),
        make=obj.get(str("make").upper())
    )


def main(args):
    topic = args.topic

    path = os.path.realpath(os.path.dirname(
        __file__).replace("consumer", "schemas").replace("Python", ""))

    with open(f"{path}/orders_table.avsc") as f:
        schema_str = f.read()

    sr_conf = {'url': args.schema_registry}
    schema_registry_client = SchemaRegistryClient(sr_conf)

    avro_deserializer = AvroDeserializer(schema_registry_client,
                                         schema_str,
                                         dict_to_orders)

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

            orders = avro_deserializer(msg.value(), SerializationContext(
                msg.topic(), MessageField.VALUE))
            if orders is not None:
                print("\tMAKE: {}\n"
                      "\tWINDOW_START_TS: {}\n"
                      "\tORDER_COUNT: {}\n"
                      "\tTOTAL_VALUE_USD: {}\n"
                      .format(orders.make,
                              orders.window_start_ts,
                              orders.order_count,
                              orders.total_value_usd))
        except KeyboardInterrupt:
            break

    consumer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AvroDeserializer example")
    parser.add_argument('-b', dest="bootstrap_servers", default="localhost:29092",
                        help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry", default="http://localhost:8085",
                        help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="ORDERS_BY_MINUTE",
                        help="Topic name")
    parser.add_argument('-g', dest="group", default="ORDERS_BY_MINUTE",
                        help="Consumer group")
    parser.add_argument('-p', dest="specific", default="true",
                        help="Avro specific record")

    main(parser.parse_args())
