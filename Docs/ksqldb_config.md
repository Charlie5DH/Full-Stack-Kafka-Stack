## Configure ksqlDB with Docker

You can deploy ksqlDB by using Docker containers. Confluent maintains images at Docker Hub for [ksqlDB Server](https://hub.docker.com/r/confluentinc/ksqldb-server) and the [ksqlDB command-line interface (CLI)](https://hub.docker.com/r/confluentinc/ksqldb-cli).

Use the following settings to start containers that run ksqlDB in various configurations.

## Assign configuration settings in the Docker run command

You can pass configuration settings dynamically into containers by using environment variables. When you start a container, set up the configuration with the `-e` or `--env` flags in the `docker run` command.

In most cases, to assign a ksqlDB configuration parameter in a container, you prepend the parameter name with KSQL\_ and substitute the underscore character for periods. For example, to assign the `ksql.queries.file` setting in your docker run command, specify:

```bash
-e KSQL_KSQL_QUERIES_FILE=<path-in-container-to-sql-file>
```

## ksqlDB Server configurations

### ksqlDB Interactive Server Settings

```bash
docker run -d \
  -p 127.0.0.1:8088:8088 \
  -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
  -e KSQL_LISTENERS=http://0.0.0.0:8088/ \
  -e KSQL_KSQL_SERVICE_ID=ksql_service_2_ \
  confluentinc/ksqldb-server:0.28.2
```

`KSQL_BOOTSTRAP_SERVERS` is the address of the Kafka broker that ksqlDB Server uses to read and write data. The default is `localhost:9092`.

`KSQL_LISTENERS` A list of URIs, including the protocol, that the broker listens on. If you are using IPv6, set it to `http://[::]:8088`.

`KSQL_KSQL_SERVICE_ID` The service ID of the ksqlDB Server, which is used as the prefix for the internal topics created by ksqlDB.

### ksqlDB Headless Server Settings (Production)

You can deploy ksqlDB Server in a non-interactive, or headless, mode. In headless mode, interactive use of the `ksqlDB` cluster is disabled, and you configure ksqlDB Server with a predefined .sql file and the `KSQL_KSQL_QUERIES_FILE` setting.

```bash
docker run -d \
  -v /path/on/host:/path/in/container/ \
  -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
  -e KSQL_KSQL_SERVICE_ID=ksql_standalone_1_ \
  -e KSQL_KSQL_QUERIES_FILE=/path/in/container/queries.sql \
  confluentinc/ksqldb-server:0.28.2
```

### Enable the ksqlDB Processing Log

ksqlDB emits a log of record processing events, called the processing log, to help you debug SQL queries. For more information, see ksqlDB Processing Log.

```bash
# — Processing log config —
KSQL_LOG4J_PROCESSING_LOG_BROKERLIST: kafka:29092
KSQL_LOG4J_PROCESSING_LOG_TOPIC: demo_processing_log
KSQL_KSQL_LOGGING_PROCESSING_TOPIC_NAME: demo_processing_log
KSQL_KSQL_LOGGING_PROCESSING_TOPIC_AUTO_CREATE: "true"
KSQL_KSQL_LOGGING_PROCESSING_STREAM_AUTO_CREATE: "true"
```

## Using docker compose

```yaml
ksqldb-server:
  image: confluentinc/ksqldb-server:0.28.2
  hostname: ksqldb-server
  container_name: ksqldb-server
  depends_on:
    - broker
    - schema-registry
  ports:
    - "8088:8088"
  volumes:
    - "./extensions/:/opt/ksqldb-udfs"
  environment:
    KSQL_LISTENERS: "http://0.0.0.0:8088"
    KSQL_BOOTSTRAP_SERVERS: "broker:9092"
    KSQL_KSQL_SCHEMA_REGISTRY_URL: "http://schema-registry:8081"
    KSQL_KSQL_LOGGING_PROCESSING_STREAM_AUTO_CREATE: "true"
    KSQL_KSQL_LOGGING_PROCESSING_TOPIC_AUTO_CREATE: "true"
    # Configuration for UDFs
    KSQL_KSQL_EXTENSION_DIR: "/opt/ksqldb-udfs"
```

## Create a stack file to define your ksqlDB application

For a local installation, include one or more Kafka brokers in the stack and one or more ksqlDB Server instances.

- ZooKeeper: one instance, for cluster metadata
- Kafka: one or more instances
- Schema Registry: optional, but required for Avro, Protobuf, and JSON_SR
- ksqlDB Server: one or more instances
- ksqlDB CLI: optional
- Other services: like Elasticsearch, optional

A stack that runs Schema Registry can handle `Avro`, `Protobuf`, and `JSON_SR` formats. Without Schema Registry, ksqlDB handles only `JSON` or delimited schemas for events.

## Start the ksqlDB CLI

When all of the services in the stack are Up, run the following command to start the ksqlDB CLI and connect to a ksqlDB Server.

Run the following command to start the ksqlDB CLI in the running ksqldb-cli container.

```bash
docker exec -it ksqldb-cli ksql http://primary-ksqldb-server:8088
```

## KSQLDB HTTP API

The ksqlDB HTTP API uses content types for requests and responses to indicate the serialization format of the data and the API version.

Your request should specify this serialization format and version in the Accept header, for example:
Here's an example request that returns the results from the LIST STREAMS command:

```bash
curl -X "POST" "http://localhost:8088/ksql" \
     -H "Accept: application/vnd.ksql.v1+json" \
     -d $'{
  "ksql": "LIST STREAMS;",
  "streamsProperties": {}
}'
```

Here's an example request that retrieves streaming data from TEST_STREAM:

```bash
curl -X "POST" "http://localhost:8088/query" \
     -H "Accept: application/vnd.ksql.v1+json" \
     -d $'{
  "ksql": "SELECT * FROM TEST_STREAM EMIT CHANGES;",
  "streamsProperties": {}
}'
```

A PROTOBUF content type where the rows are serialized in the PROTOBUF format is also supported for querying the /query and /query-stream endpoints. You can specify this serialization format in the Accept header:

    ```bash
    Accept: application/vnd.ksql.v1+protobuf
    ```

## Python Client

See more at [Python client](https://github.com/bryanyang0528/ksql-python)

```python
import logging
from ksql import KSQLAPI

logging.basicConfig(level=logging.DEBUG)
client = KSQLAPI('http://ksql-server:8088')

client.ksql('show tables')

client.query('select * from table1')
```

## KSQLDB

`docker exec -it ksqldb ksql http://localhost:8088`

## KSQLDB Commands

Create connectors using ksqldb

```bash
SHOW TOPICS;
```

```bash
SHOW CONNECTORS;
```

```sql
CREATE SINK CONNECTOR SINK_ES_AGG WITH (
    'connector.class' = 'io.confluent.connect.elasticsearch.ElasticsearchSinkConnector',
    'topics'          = 'ORDERS_BY_HOUR',
    'connection.url'  = 'http://elasticsearch:9200',
    'type.name'       = 'type.name=kafkaconnect',
    'key.ignore'      = 'false',
    'schema.ignore'   = 'true'
);
```
