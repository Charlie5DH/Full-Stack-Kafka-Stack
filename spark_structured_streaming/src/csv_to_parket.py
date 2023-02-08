from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, TimestampType, IntegerType, DoubleType

import os

# get the path to the current file
path = os.path.dirname(os.path.abspath(__file__))
# get the path to the parent directory
parent_path = os.path.dirname(path)
# get the path to the data directory
data_path = os.path.join(parent_path, "data")
# list the files in the data directory and filter for csv files
csv_files = [f for f in os.listdir(data_path) if f.endswith(".csv")]
# get the first csv file
csv_file = csv_files[0]
# get the full path to the csv file
csv_file_path = os.path.join(data_path, csv_file)
#path = "../data/predictive_maintenance.csv"

spark = SparkSession.builder\
    .appName('transformCSVParquet')\
    .getOrCreate()

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

df = spark.read.csv(path=csv_file_path, header=True, schema=SCHEMA, sep=",")
df.show(5)

# remove csv from file name
parquet_file = csv_file.replace(".csv", ".parquet")
# get the full path to the parquet file
parquet_file_path = os.path.join(data_path, parquet_file)
# write the dataframe to parquet
df.write.parquet(parquet_file_path)

# Command to run the script
# spark-submit --deploy-mode client --master spark://spark:7077 --driver-memory 2G --executor-memory 2G transform_json_to_parquet.py

# Unprotect the folder
# sudo chmod -R 777 data/
