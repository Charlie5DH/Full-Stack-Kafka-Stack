#!/usr/bin/env bash

# Init kafkacat consumer
echo "Init kafkacat consumer..."
docker exec kafkacat kafkacat -b kafka:9092 -t mysql-debezium-asgard.demo.ORDERS -C -o -10 -q -r http://schema-registry:8085 -s avro
#docker exec -it kafka bash -c kafka-console-consumer --bootstrap-server kafka:9092 --topic mysql-debezium-asgard.demo.ORDERS --broker-list localhost:9092