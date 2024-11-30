import polars as pl
import os
from io import StringIO
import psycopg2

#credentials
db_user_terra = os.getenv('data_uploads_user')
db_password_terra = os.getenv('data_uploads_pass_staging')
db_name_terra = os.getenv('db_name')
db_address_terra = os.getenv('db_address_stag')

sf_user = os.getenv('sf_user')
sf_db_address = os.getenv('sf_db_address')
sf_pass = os.getenv('sf_pass')
sf_db_name = os.getenv('sf_db_name')

conn_terra = psycopg2.connect(
    dbname=db_name_terra,
    user=db_user_terra,
    password=db_password_terra,
    host=db_address_terra
)

engine_sf = f'postgresql://{sf_user}:{sf_pass}@{sf_db_address}/{sf_db_name}'

table_sf = 'source.table'
table_terra = 'source.table'
query = f"SELECT row_number() over () as fid, * FROM {table_sf}"

#read data from source
print('Reading data from source')
data = pl.read_database_uri(
    query, 
    engine_sf,
    partition_on='fid',
    partition_num=10,
    protocol= 'binary',
    engine='connectorx'
    ).drop('fid')

#create csv in memory
print('Creating csv in memory')
output = StringIO()
data.write_csv(output, include_header=False, separator='|')
output.seek(0)

#copy data to destination
print('Copying data to destination')
cursor = conn_terra.cursor()
cursor.copy_expert(f"COPY {table_terra} FROM STDIN DELIMITER '|' CSV", output)
conn_terra.commit()
cursor.close()