# Integrate Kafka with PySpark

PySpark is an interface for Apache Spark in Python. It not only allows you to write Spark applications using Python APIs, but also provides the PySpark shell for interactively analyzing your data in a distributed environment. PySpark supports most of Spark’s features such as Spark SQL, DataFrame, Streaming, MLlib (Machine Learning) and Spark Core.

- Spark SQL and DataFrame: Spark SQL is a Spark module for structured data processing. It provides a programming abstraction called DataFrame and can also act as distributed SQL query engine.

- pandas API on Spark: pandas API on Spark allows you to scale your pandas workload out. With this package, you can:

  - Be **immediately productive with Spark**, with no learning curve, if you are already **familiar with pandas**.
  - Have a single codebase that works both with pandas (tests, smaller datasets) and with Spark (distributed datasets).
  - Switch to pandas API and PySpark API contexts easily without any overhead.

- Streaming: Running on top of Spark, the streaming feature in Apache Spark enables powerful interactive and analytical applications across both streaming and historical data, while inheriting Spark’s ease of use and fault tolerance characteristics.

- MLlib: Built on top of Spark, MLlib is a scalable machine learning library that provides a uniform set of high-level APIs that help users create and tune practical machine learning pipelines.

- Spark Core: Spark Core is the underlying general execution engine for the Spark platform that all other functionality is built on top of. It provides an RDD (Resilient Distributed Dataset) and in-memory computing capabilities.

Spark is great for processing large amounts of data, including real-time and near-real-time streams of events. It is a great tool for data scientists and analysts to use for data exploration and analysis. It is also a great tool for data engineers to use for data processing and transformation.

## Kafka Consumer

We first create a spark session, SparkSession provides a single point of entry to interact with underlying Spark functionality and allows programming Spark with DataFrame and Dataset APIs.

To read from Kafka for streaming queries, we can use the function `spark.readStream`. We use the spark session we had created to **read stream** by giving the Kafka configurations like the bootstrap servers and the Kafka topic on which it should listen.

```python
# Subscribe to 1 topic
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("subscribe", "topic1") \
  .option("includeHeaders", "true") \ # Include headers
  .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "headers") #if headers
```

We can also subscribe to all topics that match with the regular expression ‘topic-name.\*’ by using the option subscribePattern instead of subscribe. It reads all events in all partitions.

```python
# Subscribe to multiple topics
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("subscribe", "topic1,topic2") \
  .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# Subscribe to a pattern
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("subscribePattern", "topic.*") \
  .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
```

## Creating a Kafka Source for Batch Queries

The start point when a query is started, either use `“earliest”` which is from the earliest offsets (same as `'auto.offset.reset': "earliest"`), or `“latest”` which is just from the latest offsets, or a JSON string specifying a starting offset for each topic partition. In the JSON, -2 as an offset can be used to refer to earliest, -1 to latest.

```python
# Subscribe to 1 topic defaults to the earliest and latest offsets
df = spark \
  .read \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("subscribe", "topic1") \
  .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# Subscribe to multiple topics, specifying explicit Kafka offsets
df = spark \
  .read \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("subscribe", "topic1,topic2") \
  .option("startingOffsets", """{"topic1":{"0":23,"1":-2},"topic2":{"0":-2}}""") \
  .option("endingOffsets", """{"topic1":{"0":50,"1":-1},"topic2":{"0":-1}}""") \
  .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# Subscribe to a pattern, at the earliest and latest offsets
df = spark \
  .read \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("subscribePattern", "topic.*") \
  .option("startingOffsets", "earliest") \
  .option("endingOffsets", "latest") \
  .load()
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
```

## Kafka Read Streaming

For rate-limiting, you can use the Spark configuration variable `spark.streaming.kafka.maxRatePerPartition` to set the maximum number of messages per partition per batch.

We can use the `kafka_df` to read the data from the stream but any new data coming from the stream can’t be read, so to constantly keep listening we need to use the below code:

```python
def func_call(df, batch_id):
    df.selectExpr("CAST(value AS STRING) as json")
    requests = df.rdd.map(lambda x: x.value).collect()
    logging.info(requests)

query = kafka_df.writeStream \
    .format(HiveWarehouseSession.STREAM_TO_STREAM) \
    .foreachBatch(func_call) \
    .option("checkpointLocation","file://F:/tmp/kafka/checkpoint") \
    .trigger(processingTime="5 minutes") \
    .start().awaitTermination()
```

In the above piece of code, the `func_call` is a python function that is being called from the writeStream which checks for new messages on the Kafka stream every 5 minutes as mentioned in `processingTime`, **the processing time can be changed based on how frequently you need to read the Kafka Stream**. The `func_call` will receive a dataframe and a `batch_id` as we are reading messages in batches. In the `func_call` we are just reading the dataframe and printing the data.

## Kafka Write Streaming

Consequently, when writing—either **Streaming Queries** or Batch **Queries—to** Kafka, some records may be duplicated; this can happen, for example, if Kafka needs to retry a message that was not acknowledged by a Broker, even though that Broker received and wrote the message record. Structured Streaming cannot prevent such duplicates from occurring due to these Kafka write semantics. However, if writing the query is successful, then you can assume that the query output was written at least once. A possible solution to **remove duplicates when reading** the written data could be to introduce a primary (unique) key that can be used to perform de-duplication when reading.

The Dataframe being written to Kafka should have the following columns in schema:

For streaming sourced dataframe, we can directly use `DataFrame.writeStream` function to write into a Kafka topic.

```python
# Write key-value data from a DataFrame to a specific Kafka topic specified in an option
ds = df \
  .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
  .writeStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("topic", "topic1") \
  .start()

# Write key-value data from a DataFrame to Kafka using a topic specified in the data
ds = df \
  .selectExpr("topic", "CAST(key AS STRING)", "CAST(value AS STRING)") \
  .writeStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .start()
```

## Kafka Write Batches

```python
# Write key-value data from a DataFrame to a specific Kafka topic specified in an option
df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
  .write \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("topic", "topic1") \
  .save()

# Write key-value data from a DataFrame to Kafka using a topic specified in the data
df.selectExpr("topic", "CAST(key AS STRING)", "CAST(value AS STRING)") \
  .write \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .save()
```

## Kafka Specific Configurations

Kafka’s own configurations can be set via DataStreamReader.option with kafka. prefix, e.g, stream.option("kafka.bootstrap.servers", "host:port"). For possible kafka parameters, see Kafka consumer config docs for parameters related to reading data, and Kafka producer config docs for parameters related to writing data.

Note that the following Kafka params cannot be set and the Kafka source or sink will throw an exception:

- `group.id`: Kafka source will create a unique group id for each query automatically. The user can set the prefix of the automatically generated group.id’s via the optional source option `groupIdPrefix`, default value is `“spark-kafka-source”`. You can also set `“kafka.group.id”` to force Spark to use a special group id, however, please read warnings for this option and use it with caution.

- `auto.offset.reset`: Set the source option `startingOffsets` to specify where to start instead. Structured Streaming manages which offsets are consumed internally, rather than rely on the kafka Consumer to do it. This will ensure that no data is missed when new topics/partitions are dynamically subscribed. Note that `startingOffsets` only applies when a new streaming query is started, and that resuming will always pick up from where the query left off. Note that when the offsets consumed by a streaming application no longer exist in Kafka (e.g., topics are deleted, offsets are out of range, or offsets are removed after retention period), the offsets will not be reset and the streaming application will see data loss. In extreme cases, for example the throughput of the streaming application cannot catch up the retention speed of Kafka, the input rows of a batch might be gradually reduced until zero when the offset ranges of the batch are completely not in Kafka. Enabling `failOnDataLoss` option can ask Structured Streaming to fail the query for such cases.

- `key.deserializer`: Keys are always deserialized as byte arrays with `ByteArrayDeserializer`. Use DataFrame operations to explicitly deserialize the keys.
  value.deserializer: Values are always deserialized as byte arrays with `ByteArrayDeserializer`. Use DataFrame operations to explicitly deserialize the values.

- `key.serializer`: Keys are always serialized with ByteArraySerializer or `StringSerializer`. Use DataFrame operations to explicitly serialize the keys into either strings or byte arrays.

- `value.serializer`: values are always serialized with ByteArraySerializer or `StringSerializer`. Use DataFrame operations to explicitly serialize the values into either strings or byte arrays.

- `enable.auto.commit`: Kafka source doesn’t commit any offset.

- `interceptor.classes`: Kafka source always read keys and values as byte arrays. It’s not safe to use ConsumerInterceptor as it may break the query.

## Kafka Concepts

Apache Kafka is an open-source distributed event (real-time) streaming platform used by thousands of companies for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications. It has the following attributes:

- **Producer application**: This reads data from DB, REST API, file systems, and so on

- **Cluster**: Group of compute nodes to distribute the workload on Kafka server. Kafka cluster typically consists of multiple brokers to maintain load balance.

- **Topic**: Arbitrary name given to dataset (stream) from the producer(s). The table is to database as the topic is to Kafka. When an event stream enters Kafka, it is persisted as a topic. In Kafka’s universe, a topic is a materialized event stream. In other words, a topic is a stream at rest. Topics are the central concept in Kafka that decouples producers and consumers. A consumer pulls messages off of a Kafka topic while producers push messages into a Kafka topic. A topic can have many producers and many consumers.

- **Partition**: The data can be huge for the broker node (single) node to handle, the ideal solution is to break it and distribute it to multiple broker nodes. So Kafka broker breaks the topic into partitions and distributes it among different brokers. For example, 1 data — 1/2 partition + 1/2 partition, finally store the first partition in one node (broker) and store the second partition of data in another node (broker). If we are to put all partitions of a topic in a single broker, the scalability of that topic will be constrained by the broker’s IO throughput. A topic will never get bigger than the biggest machine in the cluster. By spreading partitions across multiple brokers, a single topic can be scaled horizontally to provide performance far beyond a single broker’s ability.

- **Kafka Broker**: is a Kafka server, in abstraction. Producer and consumer don't interact directly, only via a broker. Kafka distributes the partitions of a particular topic across multiple brokers. A better theoretical understanding of brokers is uniquely narrated by
  Dunith Dhanushka

- **Offset**: sequenced number (id) of the messages as per arrival in the partition. FIFO, the first message in the partition gets the first id, offsets are immutable. To locate a message you need to know three things: Topic Name, partition number, and offset number

- **Consumer group**: hundreds of producers can send data to Kafka topic which is distributed across nodes. So Kafka cluster can handle the scalability. but for example, suppose you have a retail chain and each retail shop has a billing counter. You want to push each billing info from each billing counter (Producer 1,2,3…) to the data center (on-prem), for this you create a unique producer at each billing location, these producers send messages (bills) to the Kafka topic. Next thing is to create one single consumer application to pull from Kafka topic to a single data center. Now think of the scale, you have hundreds of producers (pushing data in a single topic) but one single consumer, how will you handle the volume and velocity? Now large Kafka cluster with partitioned topics solves the scalability on the producer side, but what about the consumer side? this means several brokers are sharing the workload to receive and store data, source-side sounds good, but what about destination side — only a single consumer application. A solution is a consumer group, which has multiple consumer applications which divide the work among themselves. how to divide the work? suppose we have 600 partitions, and we are having 100 consumers let's say 600/100 — 6 partitions for each consumer. If not, we will add more consumers. Max consumer is 600 so each consumer has one single partition. So partitioning in a consumer group is a tool for scalability. Max number of consumers in a group is the total number of partitions a topic has.

## PySpark Schema

PySpark StructType & StructField classes are used to programmatically specify the schema to the DataFrame and create complex columns like nested struct, array, and map columns. StructType is a collection of StructField’s that defines column name, column data type, boolean to specify if the field can be nullable or not and metadata.

```python
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField, StringType, IntegerType

spark = SparkSession.builder.master("local[1]") \
                    .appName('SparkByExamples.com') \
                    .getOrCreate()

data = [("James","","Smith","36636","M",3000),
    ("Michael","Rose","","40288","M",4000),
    ("Robert","","Williams","42114","M",4000),
    ("Maria","Anne","Jones","39192","F",4000),
    ("Jen","Mary","Brown","","F",-1)
  ]

schema = StructType([ \
    StructField("firstname",StringType(),True), \
    StructField("middlename",StringType(),True), \
    StructField("lastname",StringType(),True), \
    StructField("id", StringType(), True), \
    StructField("gender", StringType(), True), \
    StructField("salary", IntegerType(), True) \
  ])
```

```bash
root
 |-- firstname: string (nullable = true)
 |-- middlename: string (nullable = true)
 |-- lastname: string (nullable = true)
 |-- id: string (nullable = true)
 |-- gender: string (nullable = true)
 |-- salary: integer (nullable = true)

+---------+----------+--------+-----+------+------+
|firstname|middlename|lastname|id   |gender|salary|
+---------+----------+--------+-----+------+------+
|James    |          |Smith   |36636|M     |3000  |
|Michael  |Rose      |        |40288|M     |4000  |
|Robert   |          |Williams|42114|M     |4000  |
|Maria    |Anne      |Jones   |39192|F     |4000  |
|Jen      |Mary      |Brown   |     |F     |-1    |
+---------+----------+--------+-----+------+------+
```

# Submitt Application to Kafka Cluster

`spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.2.0 --master spark://spark-master:7077 --driver-memory 1G --executor-memory 1G spark-apps/average_stream_processor.py`

# References

- [Integrate Kafka with PySpark](https://medium.com/geekculture/integrate-kafka-with-pyspark-f77a49491087)
- [Apache Kafka](https://kafka.apache.org/)
- [PySpark](https://spark.apache.org/docs/latest/api/python/index.html)
- [Structured Streaming + Kafka Integration Guide](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html)
- [Spark Schemas](https://sparkbyexamples.com/pyspark/pyspark-structtype-and-structfield/)
- [Spark documentation](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
