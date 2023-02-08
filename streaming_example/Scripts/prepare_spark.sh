#!/bin/bash
# establish an interactive session with the spark container
#SPARK_CONTAINER=$(docker container ls --filter  name=spark-master --format "{{.Names}}")

echo "Entering Spark container: $SPARK_CONTAINER"
apt-get update && apt-get install wget vim -y
wget https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar
wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.1/kafka-clients-2.8.1.jar
wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.3.0/spark-sql-kafka-0-10_2.12-3.3.0.jar
wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.3.0/spark-token-provider-kafka-0-10_2.12-3.3.0.jar
mv *.jar ./jars/

# mv *.jar /opt/bitnami/spark/jars/

exit