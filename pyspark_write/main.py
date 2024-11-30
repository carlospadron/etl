import pandas as pd
from sqlalchemy import create_engine
import os
import pyspark.pandas as ps

#credentials
db_user_terra = os.getenv('data_uploads_user')
db_password_terra = os.getenv('data_uploads_pass_staging')
db_name_terra = os.getenv('db_name')
db_address_terra = os.getenv('db_address_stag')

sf_user = os.getenv('sf_user')
sf_db_address = os.getenv('sf_db_address')
sf_pass = os.getenv('sf_pass')
sf_db_name = os.getenv('sf_db_name')

engine_terra = create_engine(
    f'postgresql://{db_user_terra}:{db_password_terra}@{db_address_terra}/{db_name_terra}')

engine_sf = f"jdbc:postgresql://{sf_db_address}/{sf_db_name}"

table_sf = 'source.table'
table_terra = 'asset_legacy'
schema_terra = 'public_sf_legacy'
query = f"SELECT * FROM {table_sf} limit 100"

#read data from source
print('Reading data from source')
data = ps.read_sql_query(
    query, 
    engine_sf,
    options={'user': sf_user, 'password': sf_pass})
# data = pd.read_sql(query, engine_sf)

# #copy data to destination
# print('Copying data to destination')
# data.to_sql(
#     table_terra, 
#     engine_terra, 
#     schema=schema_terra, 
#     if_exists='append', 
#     index=False,
#     method='multi'
# )