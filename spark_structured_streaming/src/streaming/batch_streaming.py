# spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 --packages org.apache.spark:spark-avro_2.12:3.3.1 /src/streaming/batches.py

import os

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructField,
    StructType,
    IntegerType,
    StringType,
    FloatType,
    TimestampType,
    BooleanType,
)
from pyspark.sql.window import Window
from pyspark.sql.avro.functions import from_avro, to_avro

options = {
    "kafka.bootstrap.servers": "kafka:9092",
    "subscribe": "demo.purchases.json",
    "startingOffsets": "earliest",
    "endingOffsets": "latest",
}

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "demo.purchases.json"


def main():
    spark = SparkSession.builder.appName("kafka-batch-query").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    df_sales = spark.read.format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    summarize_sales(df_sales)


def summarize_sales(df_sales):
    '''
    Aggregates the number of items sold and the total sales for each product, based on existing messages consumed from the demo.purchases topic.
    We use the PySpark DataFrame class’s read() and write() methods in the first example, reading from Kafka and writing to the console.
    The batch processing job sorts the results and outputs the top 25 items by total sales to the console.
    '''

    schema = StructType(
        [
            StructField("transaction_time", TimestampType(), False),
            StructField("transaction_id", IntegerType(), False),
            StructField("product_id", StringType(), False),
            StructField("price", FloatType(), False),
            StructField("quantity", IntegerType(), False),
            StructField("is_member", BooleanType(), True),
            StructField("member_discount", FloatType(), True),
            StructField("add_supplements", BooleanType(), True),
            StructField("supplement_price", FloatType(), True),
            StructField("total_purchase", FloatType(), False),
        ]
    )

    window = Window.partitionBy("product_id").orderBy("total_purchase")
    window_agg = Window.partitionBy("product_id")

    df_sales = df_sales.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .select(F.from_json("value", schema=schema).alias("data")) \
        .select("data.*") \
        .withColumn("row", F.row_number().over(window)) \
        .withColumn("quantity", F.count(F.col("quantity")).over(window_agg)) \
        .withColumn("sales", F.sum(F.col("total_purchase")).over(window_agg)) \
        .filter(F.col("row") == 1) \
        .drop("row") \
        .select(
        "product_id",
        F.format_number("sales", 2).alias("sales"),
        F.format_number("quantity", 0).alias("quantity"),
    ) \
        .coalesce(1) \
        .orderBy(F.regexp_replace("sales", ",", "").cast("float"), ascending=False) \
        .write.format("console") \
        .option("numRows", 25) \
        .option("truncate", False) \
        .save()


if __name__ == "__main__":
    main()
