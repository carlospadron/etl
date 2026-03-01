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
# Complete setup: start databases, seed data, and generate .env
make setup-local

# Or use the script directly
./setup-local.sh
```

This will:
- Start two PostgreSQL databases (source on port 5434, target on port 5433)
- Create the required table schemas
- Seed data from CSV if available in `data/osopenuprn_*.csv`
- Generate a centralised `.env` file with all connection variables

## Option 2: AWS Deployment with Terraform

For production or cloud-based testing, use Terraform to deploy Aurora PostgreSQL Serverless:

```bash
# Initialize Terraform
cd terraform
terraform init

# Configure variables (copy and edit the example file)
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS VPC and subnet IDs

# Deploy infrastructure
terraform apply
```

See [SETUP.md](SETUP.md) for detailed instructions.

## Option 3: Manual Local Setup

If you prefer to use your own PostgreSQL installation, copy `.env.example` to `.env` and adjust the values, then create the databases and seed data manually.

## Prerequisites

- **For Docker Setup**: Docker and Docker Compose
- **For Terraform**: Terraform >= 1.0, AWS CLI, PostgreSQL client
- **For Manual Setup**: PostgreSQL >= 12

Check dependencies:
```bash
make check-deps
```

# Running Benchmarks

All benchmarks are managed centrally. Each subfolder contains an ETL implementation with its own Dockerfile. The centralised runner builds images, runs containers, monitors memory, validates source/target row counts, and generates a text report.

## Run All Benchmarks

```bash
make test-all
```

## Run a Specific Benchmark

```bash
make test-etl ETL=duckdb_copy
```

## Build All Docker Images (without running)

```bash
make build-all
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

## Benchmark Report

After running benchmarks, a `benchmark_report.txt` file is generated with:
- Duration for each test
- Peak memory usage
- Source and target row counts
- Pass/fail validation (source count must equal target count)