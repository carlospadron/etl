#!/usr/bin/env python3
"""
Seed the Aurora PostgreSQL database with OS Open UPRN data.

Required environment variables:
  DB_ENDPOINT  - Database hostname/endpoint
  DB_USER      - Master username
  DB_PASSWORD  - Master password
  SOURCE_DB    - Source database name

Optional:
  CSV_FILE     - Path to the CSV file to import
"""
import os
import sys
from pathlib import Path

import psycopg2

SCRIPT_DIR = Path(__file__).parent

DB_ENDPOINT = os.environ.get('DB_ENDPOINT') or sys.exit('DB_ENDPOINT is required')
DB_USER = os.environ.get('DB_USER') or sys.exit('DB_USER is required')
DB_PASSWORD = os.environ.get('DB_PASSWORD') or sys.exit('DB_PASSWORD is required')
SOURCE_DB = os.environ.get('SOURCE_DB') or sys.exit('SOURCE_DB is required')
CSV_FILE = os.getenv('CSV_FILE', '')

print("Database Seeding Script")
print("=======================")
print("Checking database connectivity...")

try:
    conn = psycopg2.connect(host=DB_ENDPOINT, port=5432, user=DB_USER, password=DB_PASSWORD, dbname=SOURCE_DB)
    conn.close()
except Exception as e:
    print(f"Error: Cannot connect to database at {DB_ENDPOINT}: {e}", file=sys.stderr)
    sys.exit(1)

print("Database is accessible")

if CSV_FILE and Path(CSV_FILE).is_file():
    print(f"CSV file found at {CSV_FILE}")
    print("Importing data into source database...")

    conn = psycopg2.connect(host=DB_ENDPOINT, port=5432, user=DB_USER, password=DB_PASSWORD, dbname=SOURCE_DB)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            table_sql = (SCRIPT_DIR.parent / 'data' / 'table_definitions.sql').read_text()
            cur.execute(table_sql)
            with open(CSV_FILE, newline='', encoding='utf-8') as f:
                cur.copy_expert("COPY os_open_uprn FROM STDIN WITH CSV HEADER", f)
            cur.execute("DROP TABLE IF EXISTS os_open_uprn_2m")
            cur.execute("SELECT * INTO os_open_uprn_2m FROM os_open_uprn LIMIT 2000000")
            cur.execute("SELECT COUNT(*) FROM os_open_uprn")
            row_count = cur.fetchone()[0]
    finally:
        conn.close()

    print(f"Successfully seeded {row_count:,} rows into source database")
    print("Created os_open_uprn_2m (2,000,000 rows)")
else:
    print("No CSV file provided or file does not exist. Skipping data import.")
    print("To import data, set the CSV_FILE environment variable:")
    print("  CSV_FILE=/path/to/data.csv uv run python terraform/seed-database.py")

print("Seeding complete!")
