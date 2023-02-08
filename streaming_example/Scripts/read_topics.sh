# establish an interactive session with the spark container
KAFKA_CONTAINER=$(docker container ls --filter name=kafka --format "{{.ID}}")
docker exec -it ${KAFKA_CONTAINER} bash

# set environment variables used by jobs
export BOOTSTRAP_SERVERS="localhost:29092"
export TOPIC_PRODUCTS="demo.products"
export TOPIC_PURCHASES="demo.purchases"
export TOPIC_INVENTORIES="demo.inventories"

# list topics
kafka-topics.sh --list --bootstrap-server $BOOTSTRAP_SERVERS

# read topics from beginning
kafka-console-consumer.sh \
    --topic $TOPIC_PRODUCTS --from-beginning \
    --bootstrap-server $BOOTSTRAP_SERVERS

kafka-console-consumer.sh \
    --topic $TOPIC_PURCHASES --from-beginning \
    --bootstrap-server $BOOTSTRAP_SERVERS

kafka-console-consumer.sh \
    --topic $TOPIC_INVENTORIES --from-beginning \
    --bootstrap-server $BOOTSTRAP_SERVERS