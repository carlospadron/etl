# Infrastructure Setup Guide

This document provides comprehensive instructions for setting up the ETL project infrastructure.

## Overview

The project supports three deployment options:

1. **Local Development (Docker Compose)** - Recommended for development and testing
2. **AWS Deployment (Terraform)** - For production or cloud-based testing
3. **Manual Setup** - For custom or existing PostgreSQL installations

## Prerequisites

### For Local Development
- Docker Engine 20.10 or later
- Docker Compose v2 or later (or docker-compose v1.29+)
- PostgreSQL client tools (psql)

### For AWS Deployment
- Terraform >= 1.0
- AWS CLI configured with credentials
- PostgreSQL client tools (psql)
- An existing AWS VPC with at least 2 subnets in different AZs

### Check Prerequisites
```bash
make check-deps
```

## Local Development Setup

### Quick Start

The fastest way to get started:

```bash
make setup-local
```

This single command will:
1. Start two PostgreSQL 17 databases using Docker Compose
2. Create the required table schemas automatically
3. Seed data if a CSV file is available at `data/osopenuprn_202502.csv`
4. Display connection information

### Step-by-Step Setup

1. **Start the databases:**
   ```bash
   make start-local
   ```

2. **Verify databases are running:**
   ```bash
   docker ps | grep etl-postgres
   ```

3. **Connect to source database:**
   ```bash
   psql postgresql://postgres:postgres@localhost:5432/postgres
   ```

4. **Connect to target database:**
   ```bash
   psql postgresql://postgres:postgres@localhost:5433/target
   ```

5. **Seed data (optional):**
   
   Download the OS Open UPRN dataset from:
   https://osdatahub.os.uk/downloads/open/OpenUPRN
   
   Place the CSV file at `data/osopenuprn_202502.csv`, then run:
   ```bash
   ./setup-local.sh
   ```

### Database Connection Details

**Source Database:**
- Host: `localhost`
- Port: `5432`
- Database: `postgres`
- Username: `postgres`
- Password: `postgres`
- Connection String: `postgresql://postgres:postgres@localhost:5432/postgres`

**Target Database:**
- Host: `localhost`
- Port: `5433`
- Database: `target`
- Username: `postgres`
- Password: `postgres`
- Connection String: `postgresql://postgres:postgres@localhost:5433/target`

### Managing Local Databases

```bash
# View logs
make logs-local

# Stop databases (keeps data)
make stop-local

# Restart databases
make start-local

# Remove databases and all data
make clean-local
```

### Environment Variables for ETL Scripts

When running ETL scripts locally, use these environment variables:

```bash
export ORIGIN_ADDRESS=localhost
export ORIGIN_DB=postgres
export ORIGIN_USER=postgres
export ORIGIN_PASS=postgres

export TARGET_ADDRESS=localhost
export TARGET_DB=target
export TARGET_USER=postgres
export TARGET_PASS=postgres
```

Or for target on port 5433:
```bash
export TARGET_ADDRESS=localhost:5433
```

## AWS Deployment with Terraform

### Prerequisites

1. AWS account with appropriate permissions
2. VPC with at least 2 subnets in different availability zones
3. Terraform and PostgreSQL client installed locally

### Setup Steps

1. **Navigate to terraform directory:**
   ```bash
   cd terraform
   ```

2. **Configure variables:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```
   
   Edit `terraform.tfvars` and provide:
   - Your VPC ID
   - At least 2 subnet IDs
   - A strong master password (change the default!)

3. **Initialize Terraform:**
   ```bash
   terraform init
   # Or from project root:
   make terraform-init
   ```

4. **Review the plan:**
   ```bash
   terraform plan
   # Or from project root:
   make terraform-plan
   ```

5. **Apply configuration:**
   ```bash
   terraform apply
   # Or from project root:
   make terraform-apply
   ```

6. **Get connection details:**
   ```bash
   terraform output
   # Or from project root:
   make terraform-output
   ```

### Seeding Data on AWS

After infrastructure is created:

```bash
cd terraform

# Get connection details from Terraform
DB_ENDPOINT=$(terraform output -raw cluster_endpoint)
DB_USER=$(terraform output -raw master_username)
DB_PASSWORD=$(terraform output -raw master_password)

# Seed the database
DB_ENDPOINT="$DB_ENDPOINT" \
DB_USER="$DB_USER" \
DB_PASSWORD="$DB_PASSWORD" \
SOURCE_DB="source" \
CSV_FILE="/path/to/osopenuprn_202502.csv" \
./seed-database.sh
```

### Environment Variables for AWS

```bash
export ORIGIN_ADDRESS=$(cd terraform && terraform output -raw cluster_endpoint)
export ORIGIN_DB=source
export ORIGIN_USER=$(cd terraform && terraform output -raw master_username)
export ORIGIN_PASS=$(cd terraform && terraform output -raw master_password)

export TARGET_ADDRESS=$ORIGIN_ADDRESS
export TARGET_DB=target
export TARGET_USER=$ORIGIN_USER
export TARGET_PASS=$ORIGIN_PASS
```

### Destroying Infrastructure

When you're done:

```bash
terraform destroy
# Or from project root:
make terraform-destroy
```

**Warning:** This permanently deletes all data and resources.

## Manual Setup

If you have an existing PostgreSQL installation:

1. **Create databases:**
   ```bash
   createdb postgres  # Source database
   createdb target    # Target database
   ```

2. **Create table schemas:**
   ```bash
   psql -d postgres -f data/table_definitions.sql
   psql -d target -f data/table_definitions.sql
   ```

3. **Seed data:**
   ```bash
   cd data
   # Edit initial_upload.sh if needed to match your setup
   ./initial_upload.sh
   ```

## Data Information

### OS Open UPRN Dataset

- **Source:** https://osdatahub.os.uk/downloads/open/OpenUPRN
- **Full Dataset:** 41,011,955 rows
- **Test Dataset:** 2,000,000 rows (configurable)
- **File Location:** `data/osopenuprn_202502.csv`

### Table Schema

```sql
DROP TABLE IF EXISTS os_open_uprn_full;
CREATE TABLE os_open_uprn_full (
    uprn BIGINT NOT NULL,
    x_coordinate FLOAT8 NOT NULL,
    y_coordinate FLOAT8 NOT NULL,
    latitude FLOAT8 NOT NULL,
    longitude FLOAT8 NOT NULL
);
```

The `os_open_uprn` table is created from `os_open_uprn_full` and can be limited for testing:

```sql
-- Full dataset
SELECT * INTO os_open_uprn FROM os_open_uprn_full;

-- Test dataset (2M rows)
SELECT * INTO os_open_uprn FROM os_open_uprn_full LIMIT 2000000;
```

## Testing Your Setup

### Verify Database Connectivity

```bash
# Test source database
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT version();"

# Test target database
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d target -c "SELECT version();"
```

### Run a Simple ETL Test

```bash
# Insert sample data into source
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d postgres << EOF
INSERT INTO os_open_uprn_full (uprn, x_coordinate, y_coordinate, latitude, longitude)
VALUES (100000001, 530000.0, 180000.0, 51.5074, -0.1278);
EOF

# Test pg_dump/restore ETL method
make test-pg-dump
```

## Troubleshooting

### Docker Compose Issues

**Problem:** Port already in use
```
Error: bind: address already in use
```

**Solution:** Change the port mapping in `docker-compose.yml` or stop the conflicting service.

**Problem:** Cannot connect to database
```
psql: error: connection to server at "localhost" (::1), port 5432 failed
```

**Solution:** Wait for the database to be fully ready (health checks take a few seconds) or check if containers are running:
```bash
docker ps | grep etl-postgres
```

### Terraform Issues

**Problem:** Cannot connect to database after apply
```
Error: connection refused
```

**Solution:** 
- Check security group rules allow your IP
- Verify the cluster is in "available" state
- Wait for auto-pause to wake the serverless cluster

**Problem:** State locking
```
Error: Error acquiring the state lock
```

**Solution:**
```bash
cd terraform
terraform force-unlock <LOCK_ID>
```

### Data Seeding Issues

**Problem:** CSV file not found
```
ERROR:  could not open file for reading: No such file or directory
```

**Solution:** Download the dataset and place it at the correct path:
```bash
# Should be at:
data/osopenuprn_202502.csv
```

**Problem:** Out of memory during import
```
ERROR:  out of memory
```

**Solution:** Use a smaller dataset for testing:
```sql
SELECT * INTO os_open_uprn FROM os_open_uprn_full LIMIT 2000000;
```

## Architecture Diagrams

### Local Development Architecture

```
┌─────────────────────────────────────────┐
│          Docker Compose Network         │
│                                         │
│  ┌──────────────────┐  ┌─────────────┐ │
│  │ postgres-source  │  │   postgres- │ │
│  │  (PostgreSQL 17) │  │   target    │ │
│  │                  │  │ (PostgreSQL │ │
│  │  Database: postgres │  Database:  │ │
│  │  Port: 5432      │  │   target   │ │
│  │                  │  │  Port: 5433 │ │
│  └──────────────────┘  └─────────────┘ │
│                                         │
└─────────────────────────────────────────┘
            │                │
            └────────┬───────┘
                     │
            ┌────────▼─────────┐
            │   ETL Scripts    │
            │  (pg_dump, etc)  │
            └──────────────────┘
```

### AWS Architecture

```
┌─────────────────────────────────────────────────────┐
│                      AWS VPC                        │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         Aurora PostgreSQL Serverless         │  │
│  │                                              │  │
│  │  ┌──────────────┐      ┌──────────────┐    │  │
│  │  │   Database:  │      │   Database:  │    │  │
│  │  │    source    │      │    target    │    │  │
│  │  └──────────────┘      └──────────────┘    │  │
│  │                                              │  │
│  │  Auto-scaling: 2-8 ACUs                      │  │
│  │  Auto-pause: enabled                         │  │
│  └──────────────────────────────────────────────┘  │
│                       │                             │
│            ┌──────────▼──────────┐                  │
│            │   Security Group    │                  │
│            │  (Port 5432 open)   │                  │
│            └─────────────────────┘                  │
└─────────────────────────────────────────────────────┘
                       │
              ┌────────▼─────────┐
              │  Your Machine /  │
              │   ETL Scripts    │
              └──────────────────┘
```

## Next Steps

After setting up your infrastructure:

1. Download the OS Open UPRN dataset
2. Seed the data using the appropriate method
3. Run the ETL benchmarks from the project root
4. Review results in `results.ipynb`

## Support

For issues or questions:
- Check the [main README.md](../README.md)
- Review the [terraform/README.md](terraform/README.md) for AWS-specific questions
- Check Docker Compose logs: `make logs-local`
