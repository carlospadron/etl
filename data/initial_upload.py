#!/usr/bin/env python3
"""Cross-platform replacement for initial_upload.sh"""

import sys
from pathlib import Path

import psycopg2

SCRIPT_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SCRIPT_DIR.parent


def load_env() -> dict:
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        return {}
    env = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def main() -> None:
    env_vars = load_env()

    host = env_vars.get("ORIGIN_ADDRESS", "localhost")
    port = int(env_vars.get("ORIGIN_PORT", "5434"))
    user = env_vars.get("ORIGIN_USER", "postgres")
    password = env_vars.get("ORIGIN_PASS", "postgres")
    db = env_vars.get("ORIGIN_DB", "postgres")

    csv_files = sorted(SCRIPT_DIR.glob("osopenuprn_*.csv"))
    if not csv_files:
        print("Error: No CSV file found matching osopenuprn_*.csv", file=sys.stderr)
        sys.exit(1)

    csv_file = csv_files[0]
    print(f"Using CSV file: {csv_file}")

    table_sql = (SCRIPT_DIR / "table_definitions.sql").read_text()

    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(table_sql)
            print("Table definitions applied.")
            with open(csv_file, newline="", encoding="utf-8") as f:
                cur.copy_expert("COPY os_open_uprn_full FROM STDIN WITH CSV HEADER", f)
            print("CSV loaded into os_open_uprn_full.")
            cur.execute("DROP TABLE IF EXISTS os_open_uprn")
            cur.execute("SELECT * INTO os_open_uprn FROM os_open_uprn_full")
            # To load only 2 million rows for testing, replace the line above with:
            # cur.execute("SELECT * INTO os_open_uprn FROM os_open_uprn_full LIMIT 2000000")
            print("os_open_uprn created.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
