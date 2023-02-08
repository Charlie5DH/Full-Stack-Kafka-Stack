'''
A batch query implies that the data will be queried in batches of the data.
For that, the data has to be aggregated in the batches using spark function such as window_agg = Window.partitionBy('someUniqueNameSpace') .
someUniqueNameSpace can be any column that can partition and aggregate the whole data into groups, for example, retail_office_sales or country, etc.
It can be timestamp-ed in 5 minute of a window or anything like that.
However, in this article, I will batch query whole data from the topic print it in the console and finally it will keep printing the other batches, 
which are none of course. 
but it will show that number of rows queried are zero in the susbsequent batches.   
'''

import os
import pyspark.sql.functions as F

from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, \
    StringType, FloatType, TimestampType
from pyspark.sql.functions import col


def main():

    spark = SparkSession \
        .builder \
        .appName("kafka-streaming-sales-console") \
        .master("local[*]") \
        .getOrCreate()

    df_TH = read_from_kafka(spark)

    calculate_average_tem(df_TH)


def read_from_kafka(spark):
    '''This read the stream with readStream and finally later prints to the console
    '''

    df_T = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:29092") \
        .option("subscribe", "spark_batch_csv_tem") \
        .option("startingOffsets", "earliest") \
        .load()
    return df_T


def calculate_average_tem(df_T):
    ''' This function reads the data from the topic still no average calculated,
    But calculates the strem read data (i.e. spark streaming) Tavg. 
    '''

    schema = StructType([StructField("Unnamed: 0", IntegerType(), False),
                         StructField("id", IntegerType(), False),
                         StructField("dateTime", StringType(), False),
                         StructField("Tamb", FloatType(), False),
                         StructField("TtopTestTankHPCir", FloatType(), False),
                         StructField("TbottomTestTankHpCir",
                                     StringType(), False),
                         StructField("TtopSourceTank", FloatType(), False),
                         StructField("TloadTankMix", FloatType(), False),
                         StructField("TTopTestTankLoadCir",
                                     FloatType(), False),
                         StructField("TloadMix", FloatType(), False),
                         StructField("TbottomSourceTank",  FloatType(), False),
                         StructField("TbottomTestTankLoadCir",
                                     FloatType(), False),
                         StructField("T0",  FloatType(), False),
                         StructField("T1",  FloatType(), False),
                         StructField("T2",  FloatType(), False),
                         StructField("T3",  FloatType(), False),
                         StructField("T4",  FloatType(), False),
                         StructField("T5",  FloatType(), False),
                         StructField("T6",  FloatType(), False),
                         StructField("T7",  FloatType(), False),
                         StructField("T8",  FloatType(), False),
                         StructField("T9",  FloatType(), False),
                         StructField("flowHP",  FloatType(), False),
                         StructField("flowLoad",  FloatType(), False),
                         StructField("Load_kW",  FloatType(), False),
                         StructField("Heat_Capacity_kW",  FloatType(), False)])

    T = [col('T0'), col('T1'), col('T2'), col('T3'), col('T4'),
         col('T5'), col('T6'), col('T7'), col('T8'), col('T9')]

    averageFunc = sum(x for x in T)/len(T)

    df_T = df_T \
        .selectExpr("CAST(value AS STRING)") \
        .select(F.from_json("value", schema=schema).alias("data")) \
        .select("data.*") \
        .withColumn('Tem(Avg)', averageFunc) \
        .coalesce(1) \
        .writeStream \
        .queryName("streaming_to_console") \
        .trigger(processingTime="1 minute") \
        .outputMode("append") \
        .format("console") \
        .option("numRows", 25) \
        .option("truncate", False) \
        .start()

    df_T.awaitTermination()


if __name__ == "__main__":
    main()
