# Kafka Connect Example and Workflow

Kafka Connect is a framework for connecting Kafka with external systems such as databases, key-value stores, search indexes, and file systems.

To use Kafka Connect, you create a configuration file that defines the external data source and destination, and then start Kafka Connect with this configuration file. Kafka Connect runs as a standalone process or in a cluster. You can also run Kafka Connect as a plugin on top of Kafka brokers.

We will use Kafka Connect to read data from a MySQL database and write the data to a Kafka topic. We will then use Kafka Connect to read data from the Kafka topic and write the data to another database.

## Connectors

To check the available connectors, run the following command:

```
    curl http://localhost:8083/connector-plugins
```

The output of this should be:

```json
[
  { "class": "com.mongodb.kafka.connect.MongoSinkConnector", "type": "sink", "version": "1.5.0" },
  { "class": "com.mongodb.kafka.connect.MongoSourceConnector", "type": "source", "version": "1.5.0" },
  { "class": "io.debezium.connector.mysql.MySqlConnector", "type": "source", "version": "1.2.2.Final" }
  { "class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector", "type": "sink", "version": "10.0.1" },
]
```

The MySQL sevice starts from the folder `mysql` in the root of the project which contains a set of .sql files that will be executed when the container starts. The files are executed in alphabetical order (`00`,`01`,`02`). The first file creates the database and the second file creates the table and inserts some data.
This is the container configuration:

```yaml
mysql:
  image: mysql:latest
  container_name: mysql
  ports:
    - 3306:3306
  environment:
    - MYSQL_ROOT_PASSWORD=debezium
    - MYSQL_USER=mysqluser
    - MYSQL_PASSWORD=mysqlpw
  volumes:
    - ./data/mysql:/docker-entrypoint-initdb.d
    - ./data:/data
```

## Connect to the MySQL table

```
docker exec -it mysql bash -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD demo'
```

## See an order

```sql
SELECT * FROM ORDERS ORDER BY CREATE_TS DESC LIMIT 1\G
```

Trigger the MySQL data generator:

```bash
docker exec mysql /data/02_populate_more_orders.sh
```

## Create the connector

When we start the container we install the plugins. To configure the connectors we can make a `PUT` request to the REST API.

```bash
curl -i -X PUT -H  "Content-Type:application/json" \
    http://localhost:8083/connectors/source-debezium-orders-00/config \
    -d '{
  "connector.class": "io.debezium.connector.mysql.MySqlConnector",
  "database.hostname": "mysql",
  "database.port": "3306",
  "database.user": "debezium",
  "database.password": "dbz",
  "database.server.id": "42",
  "database.server.name": "asgard",
  "table.whitelist": "demo.orders",
  "database.history.kafka.bootstrap.servers": "kafka:9092",
  "database.history.kafka.topic": "dbhistory.demo" ,
  "decimal.handling.mode": "double",
  "include.schema.changes": "true",
  "transforms": "unwrap,addTopicPrefix",
  "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
  "transforms.addTopicPrefix.type":"org.apache.kafka.connect.transforms.RegexRouter",
  "transforms.addTopicPrefix.regex":"(.*)",
  "transforms.addTopicPrefix.replacement":"mysql-debezium-$1"
}'

```

Then to check the status of the connector we can simply make a request to the REST API:

```bash
http://localhost:8083/connectors?expand=info&expand=status
```

And look for the following fields to seee if the connector is running:

```json
"status": {
      "name": "source-debezium-orders-00",
      "connector": {
        "state": "RUNNING",
        "worker_id": "kafka-connect:8083"
      },
      "tasks": [
        {
          "id": 0,
          "state": "RUNNING",
          "worker_id": "kafka-connect:8083"
        }
      ],
      "type": "source"
    }
```

## View the topic in the CLI:

```bash
 docker exec kafkacat kafkacat -b kafka:9092 -t mysql-debezium-asgard.demo.ORDERS -C -o -10 -q
```

## Stream data from Kafka to Elasticsearch

```bash
curl -i -X PUT -H  "Content-Type:application/json" \
    http://localhost:8083/connectors/sink-elastic-orders-00/config \
    -d '{
        "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
        "topics": "mysql-debezium-asgard.demo.ORDERS",
        "connection.url": "http://elasticsearch:9200",
        "type.name": "kafkaconnect",
        "key.ignore": "true",
        "schema.ignore": "true"
    }'
```

If you want to set the Elasticsearch document id to match the key of the source database record use the following:

```bash
"key.ignore": "true",
…
"transforms": "extractKey",
"transforms.extractKey.type":"org.apache.kafka.connect.transforms.ExtractField$Key",
"transforms.extractKey.field":"id"
```

## View the streming using Kafkat

First execute the script simulating the data generator:

```bash
docker exec mysql /data/02_populate_more_orders.sh
```

Then open the Kafka UI or the Confluent Console and select the topic `mysql-debezium-asgard.demo.ORDERS` or use the CLI ad Kafkacat:

```bash
docker exec kafkacat kafkacat -b kafka:9092 -t mysql-debezium-asgard.demo.ORDERS -C -o -10 -q -r http://schema-registry:8085 -s avro
```

or use the Kafka CLI to create a consumer:

```bash
docker exec -it kafka bash -c 'kafka-console-consumer --bootstrap-server kafka:9092 --topic mysql-debezium-asgard.demo.ORDERS --from-beginning --property schema.registry.url=http://schema-registry:8085 --property print.key=true --property key.separator=" : " --property print.value=true --property value.separator=" : " --property print.timestamp=true --property print.headers=true --property print.schema.ids=true --property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer --property value.deserializer=io.confluent.kafka.serializers.KafkaAvroDeserializer'
```

## Configure Neo4JS

```bash
curl -i -X PUT -H  "Content-Type:application/json" \
    http://localhost:8083/connectors/sink-neo4j-orders-00/config \
    -d '{
        "connector.class": "streams.kafka.connect.sink.Neo4jSinkConnector",
        "topics": "mysql-debezium-asgard.demo.ORDERS",
        "neo4j.server.uri": "bolt://neo4j:7687",
        "neo4j.authentication.basic.username": "neo4j",
        "neo4j.authentication.basic.password": "connect",
        "neo4j.topic.cypher.mysql-debezium-asgard.demo.ORDERS": "MERGE (city:city{city: event.delivery_city}) MERGE (customer:customer{id: event.customer_id, delivery_address: event.delivery_address, delivery_city: event.delivery_city, delivery_company: event.delivery_company}) MERGE (vehicle:vehicle{make: event.make, model:event.model}) MERGE (city)<-[:LIVES_IN]-(customer)-[:BOUGHT{order_total_usd:event.order_total_usd,order_id:event.id}]->(vehicle)"
      }'
```

## Until this point

To this point we have configured `Kafka` as a broker and `Zookeper` as our broker manager. We also configured a Schema Registry service in port `8085`, a `KsqlDB server`, a `Ksql CLI` and a `Kafka Connect Service`. This are the services working together with Kafka.

**Main Services:**

- Kafka
- Zookeper

**Services working with Kafka:**

- KsqlDB server
- Schema Registry
- Kafka Connect
- KsqlDB CLI

**Services for Monitoring Kafka:**

- Control Center
- Kafka UI
- Kafdrop

**Services Working as consumers (Sink Connectors)**

- Elasticsearch Connector
- Neo4J Conector
- MongoDB Connector (In Development)

**Services Working as Producers (Source Connectors)**

- MySQL Debezium Connector

**Databases**

- MySQL DB
- Elasticsearch
- Neo4J
- MongoDB (In Development)

**Others**

- Kibana monitoring Elasticsearch
