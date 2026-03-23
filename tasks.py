"""
ETL project task runner  —  cross-platform replacement for Makefile / Taskfile.
Requires: pip install invoke

Usage:
  invoke --list                  # show all tasks
  invoke setup-local             # start DBs and seed data
  invoke test-etl --etl duckdb_copy
  invoke terraform-destroy       # prompts for confirmation
"""

import shutil
import sys
from pathlib import Path

from invoke import Collection, task

SCRIPT_DIR = Path(__file__).parent.resolve()
TERRAFORM_DIR = SCRIPT_DIR / "terraform"

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


# ---------------------------------------------------------------------------
# Local Development
# ---------------------------------------------------------------------------


@task
def setup_local(c):
    """Complete setup: start databases and seed data."""
    c.run(f"uv run python {SCRIPT_DIR / 'setup_local.py'}")


@task
def start_local(c):
    """Start local PostgreSQL databases with Docker Compose."""
    c.run("docker compose up -d")


@task
def stop_local(c):
    """Stop local databases."""
    c.run("docker compose stop")


@task
def clean_local(c):
    """Stop and remove local databases and volumes."""
    c.run("docker compose down -v")


@task
def logs_local(c):
    """Show logs from local databases."""
    c.run("docker compose logs -f")


@task
def seed_data(c):
    """Seed data into local source database (requires CSV file in data/)."""
    c.run(f"uv run python {SCRIPT_DIR / 'data' / 'initial_upload.py'}")


# ---------------------------------------------------------------------------
# AWS / Terraform
# ---------------------------------------------------------------------------


@task
def terraform_init(c):
    """Initialize Terraform."""
    with c.cd(str(TERRAFORM_DIR)):
        c.run("terraform init")


@task
def terraform_validate(c):
    """Validate Terraform configuration."""
    with c.cd(str(TERRAFORM_DIR)):
        c.run("terraform validate")


@task
def terraform_plan(c):
    """Show Terraform execution plan."""
    with c.cd(str(TERRAFORM_DIR)):
        c.run("terraform plan")


@task
def terraform_apply(c):
    """Apply Terraform configuration to create AWS infrastructure."""
    with c.cd(str(TERRAFORM_DIR)):
        c.run("terraform apply")


@task
def terraform_destroy(c):
    """Destroy AWS infrastructure created by Terraform."""
    answer = input("This will destroy all AWS infrastructure. Are you sure? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        sys.exit(0)
    with c.cd(str(TERRAFORM_DIR)):
        c.run("terraform destroy")


@task
def terraform_output(c):
    """Show Terraform outputs."""
    with c.cd(str(TERRAFORM_DIR)):
        c.run("terraform output")


# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------


@task(
    help={"dataset": "Dataset size: '2m' for 2 million rows or 'full' for complete dataset (default: full)"},
)
def test_all(c, dataset="full"):
    """Run all ETL benchmarks (build, run, monitor, validate, report)."""
    c.run(f"uv run python {SCRIPT_DIR / 'run_tests.py'} --dataset {dataset}")


@task(
    help={
        "etl": f"ETL method to run. One of: {', '.join(ALL_METHODS)}",
        "dataset": "Dataset size: '2m' for 2 million rows or 'full' for complete dataset (default: full)",
    },
)
def test_etl(c, etl, dataset="full"):
    """Run a single ETL benchmark. Use --etl to specify the method."""
    if etl not in ALL_METHODS:
        print(f"Unknown method: {etl}")
        print(f"Available: {', '.join(ALL_METHODS)}")
        sys.exit(1)
    c.run(f"uv run python {SCRIPT_DIR / 'run_tests.py'} {etl} --dataset {dataset}")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


@task
def build_all(c):
    """Build all ETL Docker images."""
    for method in ALL_METHODS:
        method_dir = SCRIPT_DIR / method
        if (method_dir / "Dockerfile").exists():
            print(f"Building etl-{method}...")
            c.run(f"docker build -t etl-{method} {method_dir}")


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


@task
def check_deps(c):
    """Check that required CLI tools are installed."""
    missing = []
    for dep in ("docker", "terraform"):
        if shutil.which(dep) is None:
            missing.append(dep)
    if missing:
        print(f"[ERROR] Missing: {', '.join(missing)}")
        sys.exit(1)
    c.run("docker --version")
    c.run("docker compose version")
    c.run("terraform --version")
    print("All dependencies found.")


# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------

ns = Collection(
    setup_local,
    start_local,
    stop_local,
    clean_local,
    logs_local,
    seed_data,
    terraform_init,
    terraform_validate,
    terraform_plan,
    terraform_apply,
    terraform_destroy,
    terraform_output,
    test_all,
    test_etl,
    build_all,
    check_deps,
)
