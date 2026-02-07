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
# Complete setup: start databases and seed data (if CSV is available)
make setup-local

# Or use the script directly
./setup-local.sh
```

This will:
- Start two PostgreSQL databases (source on port 5432, target on port 5433)
- Create the required table schemas
- Seed data from CSV if available in `data/osopenuprn_202502.csv`

### Manual Control

```bash
# Start databases only
make start-local

# Stop databases
make stop-local

# Remove databases and volumes
make clean-local

# View logs
make logs-local
```

### Connection Details

After setup, databases are accessible at:

**Source Database:**
- Host: localhost
- Port: 5432
- Database: postgres
- User: postgres
- Password: postgres
- Connection string: `postgresql://postgres:postgres@localhost:5432/postgres`

**Target Database:**
- Host: localhost
- Port: 5433
- Database: target
- User: postgres
- Password: postgres
- Connection string: `postgresql://postgres:postgres@localhost:5433/target`

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

# Seed data (optional)
DB_ENDPOINT=$(terraform output -raw cluster_endpoint)
DB_USER=$(terraform output -raw master_username)
DB_PASSWORD=$(terraform output -raw master_password)
SOURCE_DB="source" CSV_FILE="/path/to/data.csv" ./seed-database.sh
```

See [terraform/README.md](terraform/README.md) for detailed instructions.

## Option 3: Manual Local Setup

If you prefer to use your own PostgreSQL installation:

```bash
# Create databases
createdb postgres  # Source database
createdb target    # Target database

# Create tables
psql -d postgres -f data/table_definitions.sql
psql -d target -f data/table_definitions.sql

# Seed data (if you have the CSV file)
cd data
./initial_upload.sh
```

## Data

Download the OS Open UPRN dataset:
- URL: https://osdatahub.os.uk/downloads/open/OpenUPRN
- Place the CSV file at: `data/osopenuprn_202502.csv`
- Full dataset: 41,011,955 rows
- Test dataset: 2,000,000 rows (can be configured in seeding scripts)

## Prerequisites

- **For Docker Setup**: Docker and Docker Compose
- **For Terraform**: Terraform >= 1.0, AWS CLI, PostgreSQL client
- **For Manual Setup**: PostgreSQL >= 12

Check dependencies:
```bash
make check-deps
```