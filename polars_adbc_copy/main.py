import polars as pl
import os
from io import StringIO
import psycopg2

#credentials
TARGET_USER = os.getenv('TARGET_USER')
TARGET_PASS = os.getenv('TARGET_PASS')
TARGET_DB = os.getenv('TARGET_DB')
TARGET_ADDRESS = os.getenv('TARGET_ADDRESS')

ORIGIN_USER = os.getenv('ORIGIN_USER')
ORIGIN_ADDRESS = os.getenv('ORIGIN_ADDRESS')
ORIGIN_PASS = os.getenv('ORIGIN_PASS')
ORIGIN_DB = os.getenv('ORIGIN_DB')

conn_target = psycopg2.connect(
    dbname=TARGET_DB,
    user=TARGET_USER,
    password=TARGET_PASS,
    host=TARGET_ADDRESS
)

engine_target = f'postgresql://{TARGET_USER}:{TARGET_PASS}@{TARGET_ADDRESS}/{TARGET_DB}'

engine_origin = f'postgresql://{ORIGIN_USER}:{ORIGIN_PASS}@{ORIGIN_ADDRESS}/{ORIGIN_DB}'

table_origin = 'public.os_open_uprn'
table_target = 'os_open_uprn'
query = f"SELECT row_number() over () as fid, * FROM {table_origin}"

#read data from source
print('Reading data from source')
data = pl.read_database_uri(
    query, 
    engine_origin,
    partition_on='fid',
    partition_num=10, # partition seems not to be having an effect for adbc
    engine='adbc'
    ).drop('fid')

#create csv in memory
print('Creating csv in memory')
output = StringIO()
data.write_csv(output, include_header=False, separator='|')
output.seek(0)

#copy data to destination
print('Copying data to destination')
cursor = conn_target.cursor()
cursor.copy_expert(f"COPY {table_target} FROM STDIN DELIMITER '|' CSV", output)
conn_target.commit()
cursor.close()