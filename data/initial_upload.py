#!/usr/bin/env python3
"""Cross-platform replacement for initial_upload.sh"""

import os
import subprocess
import sys
from pathlib import Path

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

    host = env_vars.get("ORIGIN_ADDRESS", os.environ.get("PGHOST", "localhost"))
    port = env_vars.get("ORIGIN_PORT", os.environ.get("PGPORT", "5434"))
    user = env_vars.get("ORIGIN_USER", os.environ.get("PGUSER", "postgres"))
    password = env_vars.get("ORIGIN_PASS", os.environ.get("PGPASSWORD", "postgres"))
    db = env_vars.get("ORIGIN_DB", os.environ.get("PGDATABASE", "postgres"))

    csv_files = sorted(SCRIPT_DIR.glob("osopenuprn_*.csv"))
    if not csv_files:
        print("Error: No CSV file found matching osopenuprn_*.csv", file=sys.stderr)
        sys.exit(1)

    csv_file = csv_files[0]
    print(f"Using CSV file: {csv_file}")

    psql_env = {**os.environ, "PGPASSWORD": password}
    base = ["-h", host, "-p", port, "-U", user, "-d", db]

    subprocess.run(
        ["psql", *base, "-f", str(SCRIPT_DIR / "table_definitions.sql")],
        check=True,
        env=psql_env,
    )
    subprocess.run(
        ["psql", *base, "-c", f"\\copy os_open_uprn_full FROM '{csv_file}' WITH CSV HEADER"],
        check=True,
        env=psql_env,
    )
    subprocess.run(
        ["psql", *base, "-c", "DROP TABLE IF EXISTS os_open_uprn"],
        check=True,
        env=psql_env,
    )
    subprocess.run(
        ["psql", *base, "-c", "SELECT * INTO os_open_uprn FROM os_open_uprn_full"],
        check=True,
        env=psql_env,
    )
    # Uncomment to load only 2 million rows for testing:
    # subprocess.run(
    #     ["psql", *base, "-c", "SELECT * INTO os_open_uprn FROM os_open_uprn_full LIMIT 2000000"],
    #     check=True, env=psql_env,
    # )


if __name__ == "__main__":
    main()
