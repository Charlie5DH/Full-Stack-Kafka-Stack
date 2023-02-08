import os
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, LongType, DoubleType

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "engine_measures_streamed"

# get the path to the current file
path = os.path.dirname(os.path.abspath(__file__))
# get the path to the parent directory
parent_path = os.path.dirname(path)
upper_parent_path = os.path.dirname(parent_path)
# get the path to the data directory
data_path = os.path.join(upper_parent_path, "data")
# list the files in the data directory and filter for csv files
csv_files = [f for f in os.listdir(data_path) if f.endswith(".csv")]
csv_file = csv_files[0]  # get the first csv file
# get the full path to the csv file
csv_file_path = os.path.join(data_path, csv_file)

SCHEMA = StructType([
    StructField("UDI", LongType()),
    StructField("Product ID", StringType()),
    StructField("Type", StringType()),
    StructField("Air temperature [K]", DoubleType()),
    StructField("Process temperature [K]", DoubleType()),
    StructField("Rotational speed [rpm]", DoubleType()),
    StructField("Torque [Nm]", DoubleType()),
    StructField("Tool wear [min]", IntegerType()),
    StructField("Target", IntegerType()),
    StructField("Failure Type", StringType())
])

spark = SparkSession.builder.appName("write_sensor_data_topic").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Reduce logging verbosity
# Read the parquet file write it to the topic
# We need to specify the schema in the stream
# and also convert the entries to the format key, value
dataframe = spark.read.csv(
    path=csv_file_path, header=True, schema=SCHEMA, sep=",") \
    .withColumn("value", F.to_json(F.struct(F.col("*")))) \
    .withColumn("key", F.col("UDI").cast("string")) \

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
