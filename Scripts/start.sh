#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

# Configure connectors
echo "Configuring connectors..."
connectors/configure_connectors.sh

echo "Populating MySQL database..."
# Run 02_populate_more_orders script from inside the container
docker exec mysql data/Scripts/02_populate_more_orders.sh

echo "Create orders consumer"
docker-compose exec kafkacat kafkacat -b kafka:9092 -t mysql-debezium-asgard.demo.ORDERS -C -o -1 -q -r http://schema-registry:8085 -s avro


