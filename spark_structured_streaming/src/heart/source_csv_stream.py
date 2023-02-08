import os
from pyspark.ml import Pipeline
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, LongType, DoubleType

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "heart_measures"

# get the path to the current file
path = os.path.dirname(os.path.abspath(__file__))
# get the path to the parent directory
parent_path = os.path.dirname(path)
upper_parent_path = os.path.dirname(parent_path)
# get the path to the data directory
data_path = os.path.join(upper_parent_path, "data")
# list the files in the data directory and filter for csv files
csv_files = [f for f in os.listdir(data_path) if f.endswith(".csv")]
csv_file = csv_files[1]  # get the first csv file
# get the full path to the csv file
csv_file_path = os.path.join(data_path, csv_file)

SCHEMA = StructType(
    [StructField("age", LongType(), True),
     StructField("sex", LongType(), True),
     StructField("cp", LongType(), True),
     StructField('trtbps', LongType(), True),
     StructField("chol", LongType(), True),
     StructField("fbs", LongType(), True),
     StructField("restecg", LongType(), True),
     StructField("thalachh", LongType(), True),
     StructField("exng", LongType(), True),
     StructField("oldpeak", DoubleType(), True),
     StructField("slp", LongType(), True),
     StructField("caa", LongType(), True),
     StructField("thall", LongType(), True),
     StructField("output", LongType(), True),
     ])

spark = SparkSession.builder.appName("write_heart_data_topic").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

dataframe = spark.read.csv(
    path=csv_file_path, header=True, schema=SCHEMA, sep=",")

print("df schema: ", dataframe.printSchema())
dataframe.show(10)

print("Writing to dataframe to Kafka")

# Write the stream to the topic
dataframe.write \
    .format("kafka")\
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)\
    .option("topic", KAFKA_TOPIC)\
    .save()

print("Dataframe written to kafka topic")
