#!/bin/bash

curl -X PUT -H  "Content-Type:application/json" http://localhost:8083/connectors/source-debezium-orders-00/config \
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

curl -X PUT -H  "Content-Type:application/json" http://localhost:8083/connectors/sink-elastic-orders-00/config \
    -d '{
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "topics": "mysql-debezium-asgard.demo.ORDERS",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",
    "key.ignore": "true",
    "schema.ignore": "true"
}'

curl -X PUT -H  "Content-Type:application/json" http://localhost:8083/connectors/source-mqtt-measures/config \
    -d '{
         "connector.class": "io.confluent.connect.mqtt.MqttSourceConnector",
         "tasks.max": "1",
         "mqtt.server.uri": "tcp://mosquitto:1883",
         "mqtt.topics":"sensor",
         "kafka.topic":"room_env_measures",
         "mqtt.qos": "2",
         "confluent.topic.bootstrap.servers": "kafka:9092",
         "confluent.topic.replication.factor": "1",
         "key.converter": "org.apache.kafka.connect.storage.StringConverter",
         "value.converter":"org.apache.kafka.connect.converters.ByteArrayConverter",
         "value.converter.schemas.enable": "true",
         "value.converter.schema.registry.url": "http://schema-registry:8085"
 }'

 curl -X PUT -H  "Content-Type:application/json" http://localhost:8083/connectors/source-mqtt-measures-2/config \
    -d '{
         "connector.class": "io.confluent.connect.mqtt.MqttSourceConnector",
         "tasks.max": "1",
         "mqtt.server.uri": "tcp://mosquitto:1883",
         "mqtt.topics":"engine_measures",
         "kafka.topic":"engine.vibration",
         "mqtt.qos": "2",
         "confluent.topic.bootstrap.servers": "kafka:9092",
         "confluent.topic.replication.factor": "1",
         "key.converter": "org.apache.kafka.connect.storage.StringConverter",
         "value.converter":"org.apache.kafka.connect.converters.ByteArrayConverter",
         "value.converter.schemas.enable": "true",
         "value.converter.schema.registry.url": "http://schema-registry:8085"
 }'

 curl -X PUT -H  "Content-Type:application/json" http://localhost:8083/connectors/influxdb-sink-connector/config \
    -d '{
         "connector.class":"io.confluent.influxdb.InfluxDBSinkConnector",
         "tasks.max":"1",
         "topics":"engine.vibration",
         "influxdb.url":"http://influxdb:8086",
         "influxdb.db":"streamed_data",
         "influxdb.username":"admin",
         "influxdb.password":"thepasswordis",
         "measurement.name.format":"${topic}",
         "key.converter": "org.apache.kafka.connect.storage.StringConverter",
         "value.converter":"org.apache.kafka.connect.json.JsonConverter",
         "value.converter.schema.registry.url":"http://schema-registry:8085"
  }
 }'
