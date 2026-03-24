import os
from io import BytesIO

import psycopg2

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

src = psycopg2.connect(host=ORIGIN_ADDRESS, port=ORIGIN_PORT, user=ORIGIN_USER,
                       password=ORIGIN_PASS, dbname=ORIGIN_DB)
tgt = psycopg2.connect(host=TARGET_ADDRESS, port=TARGET_PORT, user=TARGET_USER,
                       password=TARGET_PASS, dbname=TARGET_DB)

buf = BytesIO()

print(f'Copying {SOURCE_TABLE} -> os_open_uprn via binary COPY...', flush=True)

# Fetch column names from source so the COPY FROM targets only those columns,
# regardless of any extra columns on the target (e.g. metadata added by other tools)
with src.cursor() as cur:
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = %s "
        "ORDER BY ordinal_position",
        (SOURCE_TABLE,),
    )
    columns = [row[0] for row in cur.fetchall()]
    col_list = ", ".join(columns)

    cur.copy_expert(
        f"COPY (SELECT * FROM public.{SOURCE_TABLE}) TO STDOUT (FORMAT BINARY)",
        buf,
    )

buf.seek(0)

with tgt.cursor() as cur:
    cur.copy_expert(f"COPY os_open_uprn ({col_list}) FROM STDIN (FORMAT BINARY)", buf)

tgt.commit()
src.close()
tgt.close()

print('Done.', flush=True)
