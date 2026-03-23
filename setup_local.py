#!/usr/bin/env python3
"""Cross-platform replacement for setup-local.sh"""

import glob
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "data"

_DEFAULTS = {
    "SOURCE_HOST": "localhost",
    "SOURCE_PORT": "5434",
    "SOURCE_DB": "postgres",
    "SOURCE_USER": "postgres",
    "SOURCE_PASS": "postgres",
    "TARGET_HOST": "localhost",
    "TARGET_PORT": "5433",
    "TARGET_DB": "target",
    "TARGET_USER": "postgres",
    "TARGET_PASS": "postgres",
}


def _load_config() -> dict:
    """Read config from .env if present, then env vars, then defaults."""
    cfg = dict(_DEFAULTS)
    env_file = SCRIPT_DIR / ".env"
    if env_file.exists():
        mapping = {
            "ORIGIN_ADDRESS": "SOURCE_HOST",
            "ORIGIN_PORT": "SOURCE_PORT",
            "ORIGIN_DB": "SOURCE_DB",
            "ORIGIN_USER": "SOURCE_USER",
            "ORIGIN_PASS": "SOURCE_PASS",
            "TARGET_ADDRESS": "TARGET_HOST",
            "TARGET_PORT": "TARGET_PORT",
            "TARGET_DB": "TARGET_DB",
            "TARGET_USER": "TARGET_USER",
            "TARGET_PASS": "TARGET_PASS",
        }
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                if key in mapping:
                    cfg[mapping[key]] = value.strip()
    # Plain env vars take highest precedence
    for key in _DEFAULTS:
        if key in os.environ:
            cfg[key] = os.environ[key]
    return cfg


_cfg = _load_config()
SOURCE_HOST = _cfg["SOURCE_HOST"]
SOURCE_PORT = _cfg["SOURCE_PORT"]
SOURCE_DB = _cfg["SOURCE_DB"]
SOURCE_USER = _cfg["SOURCE_USER"]
SOURCE_PASS = _cfg["SOURCE_PASS"]
TARGET_HOST = _cfg["TARGET_HOST"]
TARGET_PORT = _cfg["TARGET_PORT"]
TARGET_DB = _cfg["TARGET_DB"]
TARGET_USER = _cfg["TARGET_USER"]
TARGET_PASS = _cfg["TARGET_PASS"]


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def warn(msg: str) -> None:
    print(f"[WARNING] {msg}")


def error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


def check_dependencies() -> None:
    info("Checking dependencies...")
    missing = []
    for dep in ("docker",):
        if shutil.which(dep) is None:
            missing.append(dep)
    if missing:
        error(f"Missing dependencies: {', '.join(missing)}")
        info("Please install the missing dependencies and try again.")
        sys.exit(1)

    result = subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True,
    )
    if result.returncode != 0:
        error("docker compose is required but not available.")
        sys.exit(1)

    info("All dependencies found.")


def start_databases() -> None:
    info("Starting PostgreSQL databases with Docker Compose...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True, cwd=SCRIPT_DIR)

    info("Waiting for databases to be ready...")
    time.sleep(5)

    for label, host, port, user, password, db in (
        ("Source", SOURCE_HOST, SOURCE_PORT, SOURCE_USER, SOURCE_PASS, SOURCE_DB),
        ("Target", TARGET_HOST, TARGET_PORT, TARGET_USER, TARGET_PASS, TARGET_DB),
    ):
        for attempt in range(1, 31):
            try:
                conn = psycopg2.connect(host=host, port=int(port), user=user, password=password, dbname=db)
                conn.close()
                info(f"{label} database is ready")
                break
            except psycopg2.OperationalError:
                if attempt == 30:
                    error(f"{label} database did not become ready in time")
                    sys.exit(1)
                time.sleep(2)


def seed_data() -> None:
    info("Checking for CSV data file...")
    matches = sorted(glob.glob(str(DATA_DIR / "osopenuprn_*.csv")))
    if not matches:
        warn(f"No CSV file found matching {DATA_DIR}/osopenuprn_*.csv")
        info("You can download the OS Open UPRN dataset from:")
        info("https://osdatahub.os.uk/downloads/open/OpenUPRN")
        info(f"Place the CSV file at: {DATA_DIR}/osopenuprn_<date>.csv")
        warn("Skipping data seeding. Re-run after downloading the data.")
        return

    # Skip seeding if data already exists
    try:
        conn = psycopg2.connect(
            host=SOURCE_HOST, port=int(SOURCE_PORT),
            user=SOURCE_USER, password=SOURCE_PASS, dbname=SOURCE_DB,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM os_open_uprn_full")
            existing = cur.fetchone()[0]
        conn.close()
        if existing > 0:
            info(f"Source table already contains {existing} rows — skipping seed.")
            return
    except Exception:
        pass

    csv_file = matches[0]
    info(f"Seeding data into source database from {csv_file}...")
    info("This may take a while depending on the size of your CSV file...")

    conn = psycopg2.connect(
        host=SOURCE_HOST, port=int(SOURCE_PORT),
        user=SOURCE_USER, password=SOURCE_PASS, dbname=SOURCE_DB,
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            with open(csv_file, newline="", encoding="utf-8") as f:
                cur.copy_expert("COPY os_open_uprn_full FROM STDIN WITH CSV HEADER", f)
            cur.execute("DROP TABLE IF EXISTS os_open_uprn")
            cur.execute("SELECT * INTO os_open_uprn FROM os_open_uprn_full")
            cur.execute("SELECT COUNT(*) FROM os_open_uprn")
            row_count = cur.fetchone()[0]
    finally:
        conn.close()
    info(f"Successfully seeded {row_count} rows into source database")


def generate_env_file() -> None:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    env_path = SCRIPT_DIR / ".env"
    info(f"Generating local .env file at {env_path}...")
    env_path.write_text(
        f"""\
# Local development environment variables (host machine)
# Generated by setup_local.py on {timestamp}

# Source database
ORIGIN_ADDRESS={SOURCE_HOST}
ORIGIN_PORT={SOURCE_PORT}
ORIGIN_DB={SOURCE_DB}
ORIGIN_USER={SOURCE_USER}
ORIGIN_PASS={SOURCE_PASS}

# Target database
TARGET_ADDRESS={TARGET_HOST}
TARGET_PORT={TARGET_PORT}
TARGET_DB={TARGET_DB}
TARGET_USER={TARGET_USER}
TARGET_PASS={TARGET_PASS}

# Sling connection strings
SOURCEDB=postgresql://{SOURCE_USER}:{SOURCE_PASS}@{SOURCE_HOST}:{SOURCE_PORT}/{SOURCE_DB}
TARGETDB=postgresql://{TARGET_USER}:{TARGET_PASS}@{TARGET_HOST}:{TARGET_PORT}/{TARGET_DB}
"""
    )
    info("Generated .env")

    docker_env_path = SCRIPT_DIR / ".env.docker"
    info(f"Generating Docker .env.docker file at {docker_env_path}...")
    docker_env_path.write_text(
        f"""\
# Docker container environment variables (uses container names on etl_etl-network)
# Generated by setup_local.py on {timestamp}

# Source database
ORIGIN_ADDRESS=etl-postgres-source
ORIGIN_PORT=5432
ORIGIN_DB={SOURCE_DB}
ORIGIN_USER={SOURCE_USER}
ORIGIN_PASS={SOURCE_PASS}

# Target database
TARGET_ADDRESS=etl-postgres-target
TARGET_PORT=5432
TARGET_DB={TARGET_DB}
TARGET_USER={TARGET_USER}
TARGET_PASS={TARGET_PASS}

# Sling connection strings
SOURCEDB=postgresql://{SOURCE_USER}:{SOURCE_PASS}@etl-postgres-source:5432/{SOURCE_DB}
TARGETDB=postgresql://{TARGET_USER}:{TARGET_PASS}@etl-postgres-target:5432/{TARGET_DB}
"""
    )
    info("Generated .env.docker")


def print_connection_info() -> None:
    info("================================================")
    info("Database Setup Complete!")
    info("================================================")
    print()
    info("Source Database Connection:")
    print(f"  Host:     {SOURCE_HOST}")
    print(f"  Port:     {SOURCE_PORT}")
    print(f"  Database: {SOURCE_DB}")
    print(f"  Username: {SOURCE_USER}")
    print(f"  Password: {SOURCE_PASS}")
    print()
    info("Target Database Connection:")
    print(f"  Host:     {TARGET_HOST}")
    print(f"  Port:     {TARGET_PORT}")
    print(f"  Database: {TARGET_DB}")
    print(f"  Username: {TARGET_USER}")
    print(f"  Password: {TARGET_PASS}")
    print()
    info("Connection strings:")
    print(f"  Source: postgresql://{SOURCE_USER}:{SOURCE_PASS}@{SOURCE_HOST}:{SOURCE_PORT}/{SOURCE_DB}")
    print(f"  Target: postgresql://{TARGET_USER}:{TARGET_PASS}@{TARGET_HOST}:{TARGET_PORT}/{TARGET_DB}")
    print()
    info("Centralised .env file has been generated.")
    info("Run ETL benchmarks with: invoke test-all")
    info("Or run a specific test with: invoke test-etl --etl <name>")
    print()
    info("To stop the databases, run: docker compose down")
    info("To remove all data, run: docker compose down -v")


def main() -> None:
    info("ETL Project - Database Setup Script")
    print()
    check_dependencies()
    start_databases()
    seed_data()
    generate_env_file()
    print_connection_info()


if __name__ == "__main__":
    main()
