# Apache Kafka with IoT: A Practical Guide.

In this project, we are deploying an application with Kafka as the core, and multiple technologies around it using Docker. In this case,we are producing data to a local MQTT broker (Mosquitto), through Python producers and consuming the data from the Broker using Kafka Connect MQTT connectors. In this case, we are not doing anything else with the data, but we can easily add more consumers to the pipeline, for example, a Spark Streaming application, a Kafka Streams application or source connector to stream the data to a database.

The data from the MQTT broker is also consumed by Telegraf and sent to InfluxDB for visualization in Grafana. The Grafana container is also configured to use the InfluxDB data source.

There is a MySQL databaset that is populated using a SQL script. The data is then consumed by Kafka Connect JDBC connector and sent to a Kafka topic. The data is then consumed by a KsqlDB Database to perform aggregations and create Tables and Streams. Once the tables are created they can be consumed using the REST API of KSQlDB.

There is a Spark Cluster that streams data from a CSV file to Kafka and consumes it to create aggregations.

<img src="./assets/structure.png" />

## Requirements

- Docker
- Docker Compose
- Python 3.6 or higher
- Python libraries: paho-mqtt, influxdb, requests, json, time, random, confluent_kafka

## Technologies

- Apache Kafka
- Zookeeper
- Kafka Connect (JDBC, MQTT, Debezium)
- KsqlDB
- Ksqldb CLI
- Spark
- Mosquitto
- InfluxDB
- Grafana
- MySQL
- Telegraf
- Python
- Docker
- Confluent Control Center
- Kafka UI
- Elasticsearch
- Kibana

## Installation

### 1. Clone the repository

```bash
git clone
```

### 2. Start the application

```bash
docker-compose up -d --build
```

### Create the connectors

```bash
connectors/configure_connectors.sh
```

### Start MySQL producer

```bash
docker exec mysql data/Scripts/02_populate_more_orders.sh
```

### Create consumers

```bash
docker-compose exec kafkacat kafkacat -b kafka:9092 -t mysql-debezium-asgard.demo.ORDERS -C -o -1 -q -r http://schema-registry:8085 -s avro
```

### Start python producers

```bash
python producers/avro_producer.py
python producers/measures_producer.py
python mqtt/producer.py
python mqtt/producer2.py
cd streaming_example/
python producer_avro.py
python producer_json.py
```

### Start Spark Streaming

```bash
docker exec spark-master spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /src/streaming/stream_dataset_to_kafka.py

docker exec spark-master spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /src/streaming/stream_dataset_to_kafka_slow.py

docker exec spark-master spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /src/streaming/stream_group_by.py

docker exec spark-master spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 /src/streaming/stream_tumbling_wind_5min_group.py
```

## Kafka REST Proxy

The Kafka REST Proxy provides a RESTful interface to a Kafka cluster. It makes it easy to produce and consume messages, view the state of the cluster, and perform administrative actions without using the native Kafka protocol or clients. Examples of use cases include reporting data to Kafka from any frontend app built in any language, ingesting messages into a stream processing framework that doesn't yet support Kafka, and scripting administrative actions.

## Adding automatic topic creation

To create topics automatically add the following configuration to the Kafka Connect configuration file:

````yml
  kafka-init-topics:
    image: confluentinc/cp-kafka:5.3.1
    volumes:
      - ./message.json:/data/message.json
    depends_on:
      - kafka1
    command: "bash -c 'echo Waiting for Kafka to be ready... && \
      cub kafka-ready -b kafka1:29092 1 30 && \
      kafka-topics --create --topic second.users --partitions 3 --replication-factor 1 --if-not-exists --zookeeper zookeeper1:2181 && \
      kafka-topics --create --topic second.messages --partitions 2 --replication-factor 1 --if-not-exists --zookeeper zookeeper1:2181 && \
      kafka-topics --create --topic first.messages --partitions 2 --replication-factor 1 --if-not-exists --zookeeper zookeeper0:2181 && \
      kafka-console-producer --broker-list kafka1:29092 -topic second.users < /data/message.json'"
      ```
````

or use the following command:

```bash
docker compose exec broker \
  kafka-topics --create \
    --topic purchases \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1
```

## References

- [Conduktor Full Kafka Stack Repo](https://github.com/conduktor/kafka-stack-docker-compose/blob/master/full-stack.yml)
- [Kafka UI docker compose example](https://github.com/provectus/kafka-ui/blob/master/documentation/compose/kafka-ui.yaml)
- [Kafka UI Repo](https://github.com/provectus/kafka-ui)
- [KsqlDB Installation Guide](https://docs.ksqldb.io/en/0.8.x-ksqldb/operate-and-deploy/installation/installing/)
- [Python Producer and Consumer](https://github.com/confluentinc/confluent-kafka-python)
