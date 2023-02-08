import os

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, FloatType, TimestampType, DoubleType
from pyspark.sql.window import Window
from pyspark.sql.functions import col


def main():

    spark = SparkSession \
        .builder \
        .appName("SparkAverageStreaming") \
        .getOrCreate()

    dataframe = read_from_kafka(spark)
    stream_average(dataframe)


def read_from_kafka(spark):
    '''This read the stream with readStream and finally later prints to the console
    '''

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "mysql-debezium-asgard.demo.ORDERS") \
        .load()
    return df


def stream_average(df_orders):
    ''' This function reads the data from the topic still no average calculated,
    But calculates the strem read data (i.e. spark streaming) Tavg. 
    '''

    schema = StructType([StructField("id", IntegerType(), False),
                         StructField("customer_id", IntegerType(), False),
                         StructField("order_total_usd", DoubleType(), False),
                         StructField("make", StringType(), False),
                         StructField("model",
                                     StringType(), False),
                         StructField("delivery_city", StringType(), False),
                         StructField("delivery_company", StringType(), False),
                         StructField("delivery_address", StringType(), False),
                         StructField("CREATE_TS", TimestampType(), False),
                         StructField("UPDATE_TS",  TimestampType(), False)])

    orders = [col('order_total_usd')]

    averageFunc = sum(x for x in orders)/len(orders)

    df_orders = df_orders \
        .selectExpr("CAST(value AS STRING)") \
        .select(F.from_json("value", schema=schema).alias("data")) \
        .select("data.*") \
        .withColumn('orders(Avg)', averageFunc) \
        .coalesce(1) \
        .writeStream \
        .queryName("streaming_to_console") \
        .trigger(processingTime="1 minute") \
        .outputMode("append") \
        .format("console") \
        .option("numRows", 25) \
        .option("truncate", False) \
        .start().awaitTermination()


if __name__ == "__main__":
    main()
