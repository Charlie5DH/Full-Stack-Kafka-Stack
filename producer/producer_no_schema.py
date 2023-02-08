#!/usr/bin/env python

import os
import json
from kafka import KafkaProducer
from random import randint
from time import sleep
from faker import Faker

CLIENT_ID = "producer_1"


def produce(fake_obj, producer):
    i = 0

    while True:
        # fake_obj user data
        user = fake_obj.simple_profile()

        producer.send(
            topic="test",
            key="measures",
            value={
                "id": i,
                "username": user["mail"].split("@")[0],
                "email": user["mail"],
                "password": user["username"],
                "sex": user["sex"],
                "address": user["address"],
                "birthdate": user["birthdate"].strftime("%Y-%m-%d"),
            },
            headers=[("key", "value")],
        )
        print(f">>>> Message {i} sent to Kafka topic 'test'")
        i += 1
        producer.flush()
        sleep(1)


if __name__ == "__main__":

    topic = "test_topic_2"
    fake_obj = Faker()
    i = 0

    try:
        producer = KafkaProducer(
            bootstrap_servers="localhost:29092",
            client_id=CLIENT_ID,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        print(f"Error: {e}")

    print(">>> Producer started <<<")

    while True:
        # fake_obj user data
        user = fake_obj.simple_profile()

        producer.send(
            topic=topic,
            key=bytes("measures", encoding="utf-8"),
            value={
                "id": i,
                "username": user["mail"].split("@")[0],
                "email": user["mail"],
                "password": user["username"],
                "sex": user["sex"],
                "address": user["address"],
                "birthdate": user["birthdate"].strftime("%Y-%m-%d"),
            },
        )
        print(f">>>> Message {i} sent to Kafka topic '{topic}'")
        i += 1
        producer.flush()
        sleep(2)
