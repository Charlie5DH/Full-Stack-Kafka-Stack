FROM confluentinc/cp-kafka-connect-base:latest

#If you want to run a local build of the connector, uncomment the COPY command and make sure the JAR file is in the directory path
#COPY mongo-kafka-connect-<<INSERT BUILD HERE>>3-all.jar /usr/share/confluent-hub-components

ENV CONNECT_PLUGIN_PATH="/usr/share/java,/usr/share/confluent-hub-components"

RUN echo "Installing Plugins"
RUN confluent-hub install --no-prompt debezium/debezium-connector-mysql:1.2.2
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-elasticsearch:11.1.3
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-mqtt:latest
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-influxdb:latest

RUN echo "Launching Kafka Connect worker"
RUN /etc/confluent/docker/run &
RUN echo "Waiting for Kafka Connect to start"

#ENV CONNECT_PLUGIN_PATH="/usr/share/java,/usr/share/confluent-hub-components"