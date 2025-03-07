import duckdb
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

# Install and load the PostgreSQL extension
duckdb.sql("INSTALL postgres;")
duckdb.sql("LOAD postgres;")

schema_origin = 'public'
table_origin = 'os_open_uprn'
table_target = 'os_open_uprn'
query = f"SELECT * FROM {table_origin}"

#read data from source
print('Reading data from source')
duckdb.sql(
    f"""
    CREATE TABLE {table_origin} AS
    FROM postgres_scan(
        'host={ORIGIN_ADDRESS}
        port=5432
        dbname={ORIGIN_DB}
        user={ORIGIN_USER}
        password={ORIGIN_PASS}',
        '{schema_origin}', 
        '{table_origin}');
    """
)

# Save data to csv
duckdb.sql(
    f"""
    COPY {table_origin} TO 'data.parquet' (FORMAT PARQUET);
"""
)

#copy data to destination
print('Copying data to destination')
duckdb.sql(
    f"""
    ATTACH 
        'host={TARGET_ADDRESS}
        port=5432
        dbname={TARGET_DB}
        user={TARGET_USER}
        password={TARGET_PASS}' AS target (TYPE POSTGRES);
    COPY target.{table_target} FROM 'data.parquet' (FORMAT PARQUET);       
"""
)