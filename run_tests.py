#!/usr/bin/env python3
"""
Cross-platform replacement for run_tests.sh

Builds Docker images, runs containers, monitors memory, validates row counts,
and generates a text report.

Usage:
  python run_tests.py                          # run all methods
  python run_tests.py duckdb_copy pandas_copy  # run specific methods
  python run_tests.py --env /path/to/.env ...  # override .env path
  python run_tests.py --help
"""

import argparse
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

import psycopg2

SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_ENV_FILE = SCRIPT_DIR / ".env"
REPORT_FILE = SCRIPT_DIR / "benchmark_report.txt"
MEMORY_INTERVAL = 2  # seconds between docker stats polls

ALL_METHODS = [
    "duckdb_copy",
    "duckdb_copy_parquet",
    "pandas_copy",
    "pandas_to_sql",
    "pg_dump_restore",
    "polars_adbc_copy",
    "polars_connectorx_copy",
    "polars_connectorx_write",
    "pyspark_copy",
    "pyspark_write",
    "sling",
    "spark",
]


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def error(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)


def load_env(env_file: Path) -> dict:
    if not env_file.exists():
        error(f".env file not found at {env_file}")
        info("Run 'invoke setup-local' to generate it.")
        sys.exit(1)
    env = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    info(f"Loaded environment from {env_file}")
    return env


def get_row_count(host: str, port: str, user: str, password: str, db: str, table: str) -> str:
    try:
        conn = psycopg2.connect(host=host, port=int(port), user=user, password=password, dbname=db)
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
        conn.close()
        return str(count)
    except Exception:
        return "ERROR"


def truncate_target_table(table: str, env: dict) -> None:
    try:
        conn = psycopg2.connect(
            host=env["TARGET_ADDRESS"], port=int(env["TARGET_PORT"]),
            user=env["TARGET_USER"], password=env["TARGET_PASS"], dbname=env["TARGET_DB"],
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {table}")
        conn.close()
    except Exception:
        pass


def _parse_memory_mib(value: str) -> float:
    """Convert docker stats memory string (e.g. '1.5GiB', '300MiB') to MiB."""
    value = value.strip()
    if value.endswith("GiB"):
        return float(value[:-3]) * 1024
    if value.endswith("MiB"):
        return float(value[:-3])
    if value.endswith("KiB"):
        return float(value[:-3]) / 1024
    if value.endswith("B"):
        return float(value[:-1]) / 1_048_576
    return 0.0


def monitor_memory(container_name: str, log_path: Path, stop_event: threading.Event) -> None:
    with log_path.open("w") as f:
        f.write("Timestamp,MemoryUsage\n")
    while not stop_event.is_set():
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{.MemUsage}}", container_name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            mem = result.stdout.strip().split()[0]
            if mem:
                with log_path.open("a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{mem}\n")
        stop_event.wait(MEMORY_INTERVAL)


def get_peak_memory(log_path: Path) -> str:
    if not log_path.exists():
        return "N/A"
    peak = 0.0
    try:
        lines = log_path.read_text().splitlines()[1:]  # skip header
        for line in lines:
            _, _, mem_str = line.partition(",")
            if mem_str:
                peak = max(peak, _parse_memory_mib(mem_str))
    except Exception:
        return "N/A"
    return f"{peak:.1f}MiB" if peak > 0 else "N/A"


def build_image(method: str) -> bool:
    method_dir = SCRIPT_DIR / method
    if not (method_dir / "Dockerfile").exists():
        error(f"No Dockerfile found for {method}")
        return False
    info(f"Building image for {method}...")
    result = subprocess.run(
        ["docker", "build", "-t", f"etl-{method}", str(method_dir)],
        capture_output=True,
    )
    return result.returncode == 0


def run_single_test(method: str, env: dict, env_file: Path) -> dict:
    table = "os_open_uprn"
    container_name = f"etl-{method}"

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        mem_log = Path(tmp.name)

    info(f"--- Running: {method} ---")

    if not build_image(method):
        return {
            "method": method, "exit_code": -1, "duration": 0,
            "peak_mem": "N/A", "source_count": "N/A", "target_count": "N/A",
            "status": "FAIL (build failed)",
        }

    truncate_target_table(table, env)

    source_count = get_row_count(
        env["ORIGIN_ADDRESS"], env["ORIGIN_PORT"],
        env["ORIGIN_USER"], env["ORIGIN_PASS"], env["ORIGIN_DB"], table,
    )

    # Remove any previous container with the same name
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

    start_time = time.monotonic()
    subprocess.run(
        [
            "docker", "run", "-d",
            "--name", container_name,
            "--network", "host",
            "--env-file", str(env_file),
            f"etl-{method}",
        ],
        check=True,
        capture_output=True,
    )

    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=monitor_memory, args=(container_name, mem_log, stop_event), daemon=True
    )
    monitor_thread.start()

    result = subprocess.run(["docker", "wait", container_name], capture_output=True, text=True)
    duration = int(time.monotonic() - start_time)
    exit_code = int(result.stdout.strip()) if result.returncode == 0 else 1

    stop_event.set()
    monitor_thread.join(timeout=MEMORY_INTERVAL + 1)

    peak_mem = get_peak_memory(mem_log)
    mem_log.unlink(missing_ok=True)

    target_count = get_row_count(
        env["TARGET_ADDRESS"], env["TARGET_PORT"],
        env["TARGET_USER"], env["TARGET_PASS"], env["TARGET_DB"], table,
    )

    if exit_code != 0:
        status = f"FAIL (exit code {exit_code})"
    elif "ERROR" in (source_count, target_count):
        status = "FAIL (count error)"
    elif source_count != target_count:
        status = "FAIL (count mismatch)"
    else:
        status = "PASS"

    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

    if status == "PASS":
        info(f"{method}: PASS ({duration}s, peak {peak_mem})")
    else:
        error(f"{method}: {status} ({duration}s)")

    return {
        "method": method, "exit_code": exit_code, "duration": duration,
        "peak_mem": peak_mem, "source_count": source_count,
        "target_count": target_count, "status": status,
    }


def generate_report(results: list[dict], env: dict) -> None:
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed

    lines = [
        "============================================",
        "  ETL Benchmark Report",
        "============================================",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Source: {env['ORIGIN_ADDRESS']}:{env['ORIGIN_PORT']}/{env['ORIGIN_DB']}",
        f"Target: {env['TARGET_ADDRESS']}:{env['TARGET_PORT']}/{env['TARGET_DB']}",
        "Table:  os_open_uprn",
        "",
        "--------------------------------------------",
        "Results",
        "--------------------------------------------",
        "",
    ]
    for r in results:
        lines += [
            f"Test: {r['method']}",
            f"  Duration:     {r['duration']}s",
            f"  Peak Memory:  {r['peak_mem']}",
            f"  Source Count: {r['source_count']}",
            f"  Target Count: {r['target_count']}",
            f"  Validation:   {r['status']}",
            "",
        ]
    lines += [
        "--------------------------------------------",
        "Summary",
        "--------------------------------------------",
        f"Total tests: {len(results)}",
        f"Passed:      {passed}",
        f"Failed:      {failed}",
        "============================================",
    ]

    REPORT_FILE.write_text("\n".join(lines) + "\n")
    info(f"Report written to {REPORT_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ETL benchmarks.")
    parser.add_argument("methods", nargs="*", help="Methods to run (default: all)")
    parser.add_argument("--env", default=str(DEFAULT_ENV_FILE), help="Path to .env file")
    args = parser.parse_args()

    methods = args.methods or ALL_METHODS
    env_file = Path(args.env)

    invalid = [m for m in methods if m not in ALL_METHODS]
    if invalid:
        for m in invalid:
            error(f"Unknown method: {m}")
        parser.print_help()
        sys.exit(1)

    env = load_env(env_file)
    info(f"Running {len(methods)} ETL benchmark(s)...")
    print()

    results = []
    for method in methods:
        results.append(run_single_test(method, env, env_file))
        print()

    generate_report(results, env)
    print()
    print(REPORT_FILE.read_text())


if __name__ == "__main__":
    main()
