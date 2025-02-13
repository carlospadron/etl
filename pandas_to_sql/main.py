import pandas as pd
from sqlalchemy import create_engine
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

engine_target = create_engine(
    f'postgresql://{TARGET_USER}:{TARGET_PASS}@{TARGET_ADDRESS}/{TARGET_DB}')

engine_origin = create_engine(
    f'postgresql://{ORIGIN_USER}:{ORIGIN_PASS}@{ORIGIN_ADDRESS}/{ORIGIN_DB}')

table_origin = 'source.table'
table_target = 'asset_legacy'
schema_target = 'public_origin_legacy'
query = f"SELECT * FROM {table_origin}"

#read data from source
print('Reading data from source')
data = pd.read_sql(query, engine_origin)

#copy data to destination
print('Copying data to destination')
data.to_sql(
    table_target,
    engine_target,
    schema=schema_target,
    if_exists='append',
    index=False,
    method='multi'
)