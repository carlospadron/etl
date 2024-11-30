import polars as pl
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

engine_terra = f'postgresql://{db_user_terra}:{db_password_terra}@{db_address_terra}/{db_name_terra}'

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

#copy data to destination
data.write_database(
    table_name=table_terra,  
    if_table_exists = 'append',
    connection=engine_terra
)