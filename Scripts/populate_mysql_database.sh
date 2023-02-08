#!/usr/bin/env bash

echo "Populating MySQL database..."

# Run 02_populate_more_orders script from inside the container
docker exec mysql data/Scripts/02_populate_more_orders.sh



