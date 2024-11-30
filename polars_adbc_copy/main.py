import polars as pl
import os
from io import StringIO

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
connection = engine_terra.raw_connection()
cursor = connection.cursor()
cursor.copy_expert(f"COPY {table_terra} FROM STDIN DELIMITER '|' CSV", output)
connection.commit()
cursor.close()