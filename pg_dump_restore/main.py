import os
import subprocess
import sys
from pathlib import Path

import psycopg2

SCRIPT_DIR = Path(__file__).parent

ORIGIN_ADDRESS = os.environ['ORIGIN_ADDRESS']
ORIGIN_PORT = os.getenv('ORIGIN_PORT', '5432')
ORIGIN_DB = os.environ['ORIGIN_DB']
ORIGIN_USER = os.environ['ORIGIN_USER']
ORIGIN_PASS = os.environ['ORIGIN_PASS']

TARGET_ADDRESS = os.environ['TARGET_ADDRESS']
TARGET_PORT = os.getenv('TARGET_PORT', '5432')
TARGET_DB = os.environ['TARGET_DB']
TARGET_USER = os.environ['TARGET_USER']
TARGET_PASS = os.environ['TARGET_PASS']

SRC_TABLE = os.getenv('SOURCE_TABLE', 'os_open_uprn')
ROLE = 'postgres'
DUMP_FILE = f'{SRC_TABLE}.dump'


def run(cmd: list, env: dict) -> None:
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        sys.exit(result.returncode)


# Dump from source
print(f'Dumping {SRC_TABLE} from source...')
run(
    ['pg_dump', '-h', ORIGIN_ADDRESS, '-p', ORIGIN_PORT,
     '-U', ORIGIN_USER, '-d', ORIGIN_DB,
     '-t', SRC_TABLE, '-Fc', '-Oxa', '-f', DUMP_FILE],
    env={**os.environ, 'PGPASSWORD': ORIGIN_PASS},
)

# Apply table definitions and create staging table on target
print('Preparing target schema...')
table_sql = (SCRIPT_DIR / 'table_definitions.sql').read_text()
conn = psycopg2.connect(
    host=TARGET_ADDRESS, port=int(TARGET_PORT),
    user=TARGET_USER, password=TARGET_PASS, dbname=TARGET_DB,
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute(table_sql)
    if SRC_TABLE != 'os_open_uprn':
        cur.execute(f'DROP TABLE IF EXISTS {SRC_TABLE}; CREATE TABLE {SRC_TABLE} (LIKE os_open_uprn)')
conn.close()

# Restore to target
print('Restoring to target...')
run(
    ['pg_restore', '-h', TARGET_ADDRESS, '-p', TARGET_PORT,
     '-U', TARGET_USER, '-d', TARGET_DB, f'--role={ROLE}', DUMP_FILE],
    env={**os.environ, 'PGPASSWORD': TARGET_PASS},
)

# Rename if the source table is not already os_open_uprn
if SRC_TABLE != 'os_open_uprn':
    print(f'Renaming {SRC_TABLE} -> os_open_uprn...')
    conn = psycopg2.connect(
        host=TARGET_ADDRESS, port=int(TARGET_PORT),
        user=TARGET_USER, password=TARGET_PASS, dbname=TARGET_DB,
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f'DROP TABLE os_open_uprn; ALTER TABLE {SRC_TABLE} RENAME TO os_open_uprn')
    conn.close()

print('Done.')
