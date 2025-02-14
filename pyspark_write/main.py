from pyspark.sql import SparkSession
import os

#credentials
TARGET_USER = os.getenv('TARGET_USER')
TARGET_PASS = os.getenv('TARGET_PASS')
TARGET_DB = os.getenv('TARGET_DB')
TARGET_ADDRESS = os.getenv('TARGET_ADDRESS')

ORIGIN_USER = os.getenv('ORIGIN_USER')
ORIGIN_ADDRESS = os.getenv('ORIGIN_ADDRESS')
ORIGIN_PASS = os.getenv('ORIGIN_PASS')
ORIGIN_DB = os.getenv('ORIGIN_DB')

url_target = f"jdbc:postgresql://{TARGET_ADDRESS}/{TARGET_DB}"
url_origin = f"jdbc:postgresql://{ORIGIN_ADDRESS}/{ORIGIN_DB}"

table_origin = 'public.os_open_uprn'
table_target = 'os_open_uprn'
query = f"SELECT * FROM {table_origin}"

spark = (SparkSession.builder
    .appName("Scals/spark ETL")
    .config("spark.master", "local[*]")
    .config('spark.jars.packages', 'org.postgresql:postgresql:42.2.18')
    .getOrCreate()
    )

# Read data from PostgreSQL into a DataFrame
print("Reading data from PostgreSQL into a DataFrame")
df = (spark.read
    .format("jdbc")
    .option("url", url_origin)
    .option("query", query)
    .option("user", ORIGIN_USER)
    .option("password", ORIGIN_PASS)
    .option("fetchsize", "100000")
    .option("driver", "org.postgresql.Driver")
    .load()
)

# Write the DataFrame to another PostgreSQL table
print("Writing the DataFrame to another PostgreSQL table")

# insert mode that is very slow but database agnostic
(df
    .repartition(20)
    .write
    .mode("overwrite") # append/overwrite
    .format("jdbc")
    .option("url", url_target)
    .option("dbtable", table_target)
    .option("user", TARGET_USER)
    .option("password", TARGET_PASS)
    .option("batchsize", "10000")
    .option("truncate", "true")
    .option("driver", "org.postgresql.Driver")
    .save() 
)

# Stop the Spark session
spark.stop()

print("ETL job completed")