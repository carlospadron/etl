# ETL

Comparison of techs to perform ETL. The idea is simple, read a dataset from postgres, replicate it on another postres database and evaluate time and memory consupmtion. The detailed statistics can be found in [results.ipynb](results.ipynb).

# Data

OS Open UPRN
https://osdatahub.os.uk/downloads/open/OpenUPRN

full count: 41,011,955
test count: 2,000,000

# Highligts

## pg_dump/pg_restore
- For postgresql to postgresql is the most efficient tool.
- It is not possible to transform the data.

## Sling
- Great for replications as it includes many inbuild features (retries, streaming etc)
- it has a very low memory impact
- it is not as fast as other solutions

## DuckDB 
- is a winner (in terms of execution time) for both small and large datasets
- it is not distributed so it might struggle with very large datasets
- it is mostly sql based. Familiar for many but might have limitations.

## Spark
- handles well memory for both small and large datasets
- not as fast as duckdb for these tests
- it is distributed so it can handle very large datasets (Terabytes and more)
- allows SQL, python and scala
- It also has machine learning and graph theory capabilities

## Polars
- Very efficient compared to Pandas and for small datasets competes well against spark.
- Very similar to pandas.


# Setup

This project provides multiple ways to set up the databases:

## Option 1: Local Development with Docker Compose (Recommended)

The easiest way to get started is using Docker Compose for local development:

### Quick Start

```bash
# Install dependencies (includes invoke)
uv sync

# Complete setup: start databases, seed data, and generate .env
uv run invoke setup-local

# Or run the script directly
python setup_local.py
```

This will:
- Start two PostgreSQL databases (source on port 5434, target on port 5433)
- Create the required table schemas
- Seed data from CSV if available in `data/osopenuprn_*.csv`
- Generate a centralised `.env` file with all connection variables

## Option 2: AWS Deployment with Terraform

For production or cloud-based testing, use Terraform to deploy Aurora PostgreSQL Serverless:

```bash
uv run invoke terraform-init

# Configure variables (copy and edit the example file)
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform.tfvars with your AWS VPC and subnet IDs

uv run invoke terraform-apply
```

## Option 3: Manual Local Setup

If you have an existing PostgreSQL installation:

```bash
createdb postgres   # source database
createdb target     # target database
psql -d postgres -f data/table_definitions.sql
psql -d target -f data/table_definitions.sql
python data/initial_upload.py
```

## Prerequisites

- **Python** >= 3.12 with [uv](https://docs.astral.sh/uv/) (manages dependencies — includes `psycopg2-binary`, no system Postgres client needed)
- **For Docker Setup**: Docker and Docker Compose
- **For Terraform**: Terraform >= 1.0, AWS CLI
- **For Manual Setup**: PostgreSQL >= 12 server (client tools not required)

Check dependencies:
```bash
uv run invoke check-deps
```

# Running Benchmarks

All benchmarks are managed centrally. Each subfolder contains an ETL implementation with its own Dockerfile. The centralised runner builds images, runs containers, monitors memory, validates source/target row counts, and generates a text report.

## Run All Benchmarks

```bash
# Full dataset (default)
uv run invoke test-all

# 2 million row subset
uv run invoke test-all --dataset 2m
```

## Run a Specific Benchmark

```bash
uv run invoke test-etl --etl duckdb_copy
uv run invoke test-etl --etl duckdb_copy --dataset 2m
```

## Build All Docker Images (without running)

```bash
uv run invoke build-all
```

## Stop and Clean Local Databases

```bash
# Stop databases (preserves data)
uv run invoke stop-local

# Stop and remove databases and all data volumes
uv run invoke clean-local
```

## List All Available Tasks

```bash
uv run invoke --list
```

## Available ETL Methods

| Method | Description |
|--------|-------------|
| `duckdb_copy` | DuckDB with CSV intermediate |
| `duckdb_copy_parquet` | DuckDB with Parquet intermediate |
| `pandas_copy` | Pandas read_sql + COPY bulk load |
| `pandas_to_sql` | Pandas read_sql + to_sql() |
| `pg_dump_restore` | Native pg_dump/pg_restore |
| `polars_adbc_copy` | Polars ADBC + COPY bulk load |
| `polars_connectorx_copy` | Polars ConnectorX + COPY bulk load |
| `polars_connectorx_write` | Polars ConnectorX + write_database |
| `pyspark_copy` | PySpark JDBC read + CSV + COPY |
| `pyspark_write` | PySpark JDBC read + JDBC write |
| `sling` | Sling full-refresh replication |
| `spark` | Scala Spark JDBC read + JDBC write |
| `meltano` | Meltano EL with tap-postgres + target-postgres |
| `dlt` | dlt sql_database source + postgres destination |

## Benchmark Report

After running benchmarks, a `benchmark_report.txt` file is generated with:
- Duration for each test
- Peak memory usage
- Source and target row counts
- Pass/fail validation (source count must equal target count)

# Database Reference

## Local Connection Details

| | Source | Target |
|---|---|---|
| Host | `localhost` | `localhost` |
| Port | `5434` | `5433` |
| Database | `postgres` | `target` |
| User | `postgres` | `postgres` |
| Password | `postgres` | `postgres` |

Verify connectivity:
```bash
PGPASSWORD=postgres psql -h localhost -p 5434 -U postgres -d postgres -c "SELECT version();"
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d target -c "SELECT version();"
```

## Table Schema

```sql
CREATE TABLE os_open_uprn (
    uprn BIGINT NOT NULL,
    x_coordinate FLOAT8 NOT NULL,
    y_coordinate FLOAT8 NOT NULL,
    latitude FLOAT8 NOT NULL,
    longitude FLOAT8 NOT NULL
);
```

`os_open_uprn_2m` is pre-built at setup time as a 2,000,000-row subset of `os_open_uprn`.

## AWS Seeding

After `uv run invoke terraform-apply`, seed the remote database:

```bash
DB_ENDPOINT=$(cd terraform && terraform output -raw cluster_endpoint)
DB_USER=$(cd terraform && terraform output -raw master_username)
DB_PASSWORD=$(cd terraform && terraform output -raw master_password)

cd terraform && uv run python seed-database.py
```

Then set your `.env` to point at the AWS cluster:
```bash
ORIGIN_ADDRESS=<cluster_endpoint>
ORIGIN_DB=source
ORIGIN_USER=<master_username>
ORIGIN_PASS=<master_password>
TARGET_ADDRESS=<cluster_endpoint>
TARGET_DB=target
TARGET_USER=<master_username>
TARGET_PASS=<master_password>
```