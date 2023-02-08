import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, DoubleType, IntegerType

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "engine_measures_streamed_slow"
KAFKA_TOPIC_TO_WRITE = "engine_measures_grouped"

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

spark = SparkSession.builder.appName('5_min_tumbing').getOrCreate()

# Reduce logging verbosity
spark.sparkContext.setLogLevel("WARN")


df_traffic_stream = spark\
    .readStream.format("kafka")\
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)\
    .option("subscribe", KAFKA_TOPIC)\
    .option("startingOffsets", "earliest")\
    .load()\
    .select(
        F.from_json(
            F.decode(F.col("value"), "iso-8859-1"),
            SCHEMA
        ).alias("value")
    )\
    .select("value.*")


# Count the total number of records in the 5min tumbling window
df_traffic_stream\
    .groupBy(
        F.window("Timestamp", "5 minutes"),
        F.col("Type")
    )\
    .count()\
    .writeStream\
    .option("truncate", "false")\
    .outputMode("update")\
    .format("console")\
    .start()\
    .awaitTermination()
