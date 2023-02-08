"""
reading from the topic and doing some calculation on the data and writing to the csv file
read_from_kafka() function reads the Kafka topic. 
In calculate_average_tem(df_T) function, we again define the schema by which the Kafka topic’s data would be rendered.
This rendering/unpacking/deserializing is facilitated via .select(F.from_json(“value”,schema=schema).alias(“data”)).select(“data.*”)
.averageFunc would calculate the average of the 10 columns defined in the list T. 
Data is printed on the console for debugging purposes via. 
.format(“console”) and finally written in CSV file via. .write.format(“csv”)
Please change the path to the csv to cwd.
"""
import os

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, FloatType, TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import col


def main():
    spark = SparkSession \
        .builder \
        .appName("kafka-batch-tem") \
        .master("local[*]") \
        .getOrCreate()
    df_TH = read_from_kafka(spark)
    calculate_average_tem(df_TH)


def read_from_kafka(spark):
    # Batch read from Kafka
    df_T = spark.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:29092") \
        .option("subscribe", "spark_batch_csv_tem") \
        .load()

    return df_T


def calculate_average_tem(df_T):
    #path = os.getcwd()
    path = "/home/yogender/Desktop/kafka/kafkaTemfiles"

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
    df_output = df_T \
        .selectExpr("CAST(value AS STRING)") \
        .select(F.from_json("value", schema=schema).alias("data")) \
        .select("data.*") \
        .withColumn('Tem(Avg)', averageFunc) \

    df_output \
        .write \
        .format("console") \
        .option("numRows", 50) \
        .option("truncate", False) \
        .save()

    df_output.coalesce(1) \
        .write.format("csv") \
        .option("header", "false") \
        .save(os.path.join(path, "file2.txt"))
    # df_output \
    #    .write \
    #    .csv(path=path,
    #         header=True, sep="|") \
    #    .mode('append')


if __name__ == "__main__":
    main()
