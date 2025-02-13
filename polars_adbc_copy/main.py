import polars as pl
import os
from io import StringIO

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

table_origin = 'source.table'
table_target = 'source.table'
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
data.write_csv(output, index=False, header=False, sep='|')
output.seek(0)

#copy data to destination
print('Copying data to destination')
connection = engine_target.raw_connection()
cursor = connection.cursor()
cursor.copy_expert(f"COPY {table_target} FROM STDIN DELIMITER '|' CSV", output)
connection.commit()
cursor.close()