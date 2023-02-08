# MQTT Brokers configuration

There are different MQTT brokers available. Two of the most popular are Mosquitto and HiveMQ. Both are open source and free to use. We will be using 3 configurations.

- Mosquitto local broker with docker
- HiveMQ local broker with docker
- HiveMQ cloud broker (HiveMQ Cloud now is also available for free up to 100 devices)

Each broker has its own configuration and we will be using the same configuration for all of them. The configuration is the following:

- Port: 1883
- Username: admin
- Password: admin
- Topic: {device_id}/data

## Mosquitto local broker with docker

### Installation

```bash
docker run -it -p 1883:1883 -p 9001:9001 -e MQTT_USERNAME=admin -e MQTT_PASSWORD=admin -e MQTT_ALLOW_ANONYMOUS=false eclipse-mosquitto
```

OR

```yaml
version: "3.7"
services:
  mosquitto:
    image: eclipse-mosquitto
    container_name: mosquitto
    restart: always
    ports:
      - 1883:1883
      - 9001:9001
    environment:
      - MQTT_USERNAME=admin
      - MQTT_PASSWORD=admin
      - MQTT_ALLOW_ANONYMOUS=false
```

### Configuration

Mosquitto broker is configured with environment variables. The configuration is the following:

```conf
persistence true
listener 1883
allow_anonymous true
connection_messages true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
```

## HiveMQ local broker with docker

### Installation

```bash
docker run -it -p 1883:1883 -p 8080:8080 -e HIVE_MQ_USERNAME=admin -e HIVE_MQ_PASSWORD=admin -e HIVE_MQ_ALLOW_ANONYMOUS=false hivemq/hivemq4
```
