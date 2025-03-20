import dlt
from dlt.sources.sql_database import sql_database
import os
from dlt.destinations import postgres

def load_tables():
    TARGET_USER = os.getenv('TARGET_USER')
    TARGET_PASS = os.getenv('TARGET_PASS')
    TARGET_DB = os.getenv('TARGET_DB')
    TARGET_ADDRESS = os.getenv('TARGET_ADDRESS')

    ORIGIN_USER = os.getenv('ORIGIN_USER')
    ORIGIN_ADDRESS = os.getenv('ORIGIN_ADDRESS')
    ORIGIN_PASS = os.getenv('ORIGIN_PASS')
    ORIGIN_DB = os.getenv('ORIGIN_DB')

    credentials_target = f'postgresql://{TARGET_USER}:{TARGET_PASS}@{TARGET_ADDRESS}/{TARGET_DB}'

    credentials_origin = f'postgresql://{ORIGIN_USER}:{ORIGIN_PASS}@{ORIGIN_ADDRESS}/{ORIGIN_DB}'

    source = sql_database(credentials_origin, table_names=["os_open_uprn"], schema="public")

    # Create a dlt pipeline object
    pipeline = dlt.pipeline(
        pipeline_name="etl_test", # Custom name for the pipeline
        destination=postgres(credentials=credentials_target),
        dataset_name="os_open_uprn" # Custom name for the dataset created in the destination
    )

    # Run the pipeline
    load_info = pipeline.run(source)

    # Pretty print load information
    print(load_info)

if __name__ == '__main__':
    load_tables()