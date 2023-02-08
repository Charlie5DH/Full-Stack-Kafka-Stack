#!/bin/bash

SPARK_CONTAINER=$(docker container ls --filter  name=spark-master --format "{{.Names}}")
echo "Entering Spark container: $SPARK_CONTAINER"

docker exec -it spark-master bash -c "spark-submit ./Jobs/batches.py"