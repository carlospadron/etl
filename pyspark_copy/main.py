from pyspark.sql import SparkSession
import os
import psycopg2
from glob import glob

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

# Write the DataFrame to a CSV file
print("Writing the DataFrame to a CSV file")
csv_path = "data"
df.write.csv(csv_path, header=True, mode="overwrite")

# Write the DataFrame to another PostgreSQL table
print("Writing the DataFrame to another PostgreSQL table")

# Use psycopg2 to copy the CSV data into the PostgreSQL table
print("Copying the CSV data into the PostgreSQL table")
conn = psycopg2.connect(
    dbname=TARGET_DB,
    user=TARGET_USER,
    password=TARGET_PASS,
    host=TARGET_ADDRESS
)
cur = conn.cursor()

files = glob(f"{csv_path}/*.csv")
with open(files[0], 'r') as f:
    cur.copy_expert(f"COPY {table_target} FROM STDIN WITH CSV HEADER", f)

conn.commit()
cur.close()
conn.close()

# Stop the Spark session
spark.stop()

print("ETL job completed")