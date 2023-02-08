# copy jobs to spark container
docker cp apache_spark_examples/ ${SPARK_CONTAINER}:/home/

# establish an interactive session with the spark container
docker exec -it ${SPARK_CONTAINER} bash

# set environment variables used by jobs
export BOOTSTRAP_SERVERS="kafka:29092"
export TOPIC_PURCHASES="demo.purchases"
export BOOTSTRAP_SERVERS="kafka:29092"
export TOPIC_PURCHASES="demo.purchases"

# optional: SASL/SCRAM vs. PLAINTEXT
AUTH_METHOD="sasl_scram"
export SASL_USERNAME="foo"
export SASL_PASSWORD="bar"

# run batch processing job
cd /home/apache_spark_examples/
spark-submit spark_batch_kafka.py

# run stream processing job
spark-submit spark_streaming_kafka.py

