# Kafka Commands

Once the Kafka server is up and running, you can use the following commands to interact with it. Log into the Kafka broker usingthe following command:

```bash
docker exec -it kafka bash
```

## Create a topic

```bash
kafka-topics --create --topic testing_topic --partitions 3 --replication-factor 1 --if-not-exists --bootstrap-server localhost:29092
```

## List Topics

To list all the topics in the Kafka cluster, use the following command:

```bash
    kafka-topics --list --bootstrap-server localhost:2181
```

## Kafka Console Producer and Consumers

```
kafka-console-producer --broker-list localhost:29092 --topic testing_topic
```

```
kafka-console-consumer --bootstrap-server localhost:29092 --topic testing_topic --from-beginning
```

## Describe Topics

To describe a topic, use the following command:

```bash
kafka-topics --describe --topic testing_topic --bootstrap-server localhost:29092
```
