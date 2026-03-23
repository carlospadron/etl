import dlt
import os

from dlt.sources.sql_database import sql_database

ORIGIN_USER = os.environ['ORIGIN_USER']
ORIGIN_PASS = os.environ['ORIGIN_PASS']
ORIGIN_DB = os.environ['ORIGIN_DB']
ORIGIN_ADDRESS = os.environ['ORIGIN_ADDRESS']
ORIGIN_PORT = os.getenv('ORIGIN_PORT', '5432')

TARGET_USER = os.environ['TARGET_USER']
TARGET_PASS = os.environ['TARGET_PASS']
TARGET_DB = os.environ['TARGET_DB']
TARGET_ADDRESS = os.environ['TARGET_ADDRESS']
TARGET_PORT = os.getenv('TARGET_PORT', '5432')

SOURCE_TABLE = os.getenv('SOURCE_TABLE', 'os_open_uprn')

# postgresql+psycopg2:// for SQLAlchemy (sql_database source)
source_url = f"postgresql+psycopg2://{ORIGIN_USER}:{ORIGIN_PASS}@{ORIGIN_ADDRESS}:{ORIGIN_PORT}/{ORIGIN_DB}"
target_url = f"postgresql://{TARGET_USER}:{TARGET_PASS}@{TARGET_ADDRESS}:{TARGET_PORT}/{TARGET_DB}"

print(f"Reading from {ORIGIN_ADDRESS}/{ORIGIN_DB} table {SOURCE_TABLE}", flush=True)

source = sql_database(source_url, schema="public", table_names=[SOURCE_TABLE])

# Always write to 'os_open_uprn' — handles the 2m variant rename transparently
source.resources[SOURCE_TABLE].apply_hints(table_name="os_open_uprn")

pipeline = dlt.pipeline(
    pipeline_name="etl_benchmark",
    destination=dlt.destinations.postgres(target_url),
    dataset_name="public",
)

print("Running dlt pipeline...", flush=True)
info = pipeline.run(source, write_disposition="replace")
print(info, flush=True)

if info.has_failed_jobs:
    import sys
    sys.exit(1)
