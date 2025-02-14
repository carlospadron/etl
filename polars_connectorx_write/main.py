import polars as pl
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
    partition_num=10,
    protocol= 'binary',
    engine='connectorx'
    ).drop('fid')

#copy data to destination
data.write_database(
    table_name=table_target,  
    if_table_exists = 'append',
    connection=engine_target
)