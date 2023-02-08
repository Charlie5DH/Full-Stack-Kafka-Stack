'''
Streaming queries to console
Read another CSV file and stream it to the same concurrent topic.

'''

import os
import time

import pyspark.sql.functions as F

from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, FloatType

path = "../data/csv/csvFile_2021_01_27.csv"
time_between_messages = 0.5  # 1800 messages * .5 seconds = ~15 minutes


def main():

    spark = SparkSession \
        .builder \
        .appName("kafka-incremental-tem") \
        .getOrCreate()

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

    df_TH = read_from_csv(spark,  schema)
    df_TH.cache()

    write_to_kafka(spark, df_TH)


def read_from_csv(spark, schema):
    df_T = spark.read.csv(path=path,
                          schema=schema, header=True, sep=",")
    return df_T


def write_to_kafka(spark, df_T):

    T_count = df_T.count()

    for r in range(0, T_count):
        row = df_T.collect()[r]
        df_message = spark.createDataFrame([row], df_T.schema)

        df_message = df_message \
            .drop("Unnamed: 0") \
            .selectExpr("CAST(id AS STRING) AS key",
                        "to_json(struct(*)) AS value") \
            .write \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:29092") \
            .option("topic", "spark_streaming_topic") \
            .save()

        df_message.show(1)

        time.sleep(time_between_messages)


if __name__ == "__main__":
    main()
