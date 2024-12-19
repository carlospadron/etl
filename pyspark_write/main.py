from pyspark.sql import SparkSession
import os

#credentials
db_user_terra = os.getenv('data_uploads_user')
db_password_terra = os.getenv('data_uploads_pass_staging')
db_name_terra = os.getenv('db_name')
db_address_terra = os.getenv('db_address_stag')

sf_user = os.getenv('sf_user')
sf_db_address = os.getenv('sf_db_address')
sf_pass = os.getenv('sf_pass')
sf_db_name = os.getenv('sf_db_name')

url_terra = f"jdbc:postgresql://{db_address_terra}/{db_name_terra}"
url_sf = f"jdbc:postgresql://{sf_db_address}/{sf_db_name}"

table_sf = 'source.table'
table_terra = 'source.table'
query = f"SELECT * FROM {table_sf}"

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
    .option("url", url_sf)
    .option("query", query)
    .option("user", sf_user)
    .option("password", sf_pass)
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
    .option("url", url_terra)
    .option("dbtable", table_terra)
    .option("user", db_user_terra)
    .option("password", db_password_terra)
    .option("batchsize", "10000")
    .option("truncate", "true")
    .option("driver", "org.postgresql.Driver")
    .save() 
)

# Stop the Spark session
spark.stop()

print("ETL job completed")