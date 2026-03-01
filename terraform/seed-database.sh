#!/usr/bin/env bash

set -euo pipefail

# This script seeds the Aurora PostgreSQL database with data
# It expects the following environment variables to be set:
# - DB_ENDPOINT: The database endpoint
# - DB_USER: The master username
# - DB_PASSWORD: The master password
# - SOURCE_DB: The source database name
# - CSV_FILE: Path to the CSV file to import (optional)

echo "Database Seeding Script"
echo "======================="

# Check required environment variables
: "${DB_ENDPOINT:?DB_ENDPOINT environment variable is required}"
: "${DB_USER:?DB_USER environment variable is required}"
: "${DB_PASSWORD:?DB_PASSWORD environment variable is required}"
: "${SOURCE_DB:?SOURCE_DB environment variable is required}"

export PGPASSWORD="${DB_PASSWORD}"

echo "Checking database connectivity..."
if ! pg_isready -h "${DB_ENDPOINT}" -p 5432 -U "${DB_USER}" -d "${SOURCE_DB}" >/dev/null 2>&1; then
    echo "Error: Cannot connect to database at ${DB_ENDPOINT}"
    exit 1
fi

echo "Database is accessible"

# Check if CSV file is provided and exists
if [ -n "${CSV_FILE:-}" ] && [ -f "${CSV_FILE}" ]; then
    echo "CSV file found at ${CSV_FILE}"
    echo "Importing data into source database..."
    
    # Import data into temporary table
    psql -h "${DB_ENDPOINT}" -U "${DB_USER}" -p 5432 -d "${SOURCE_DB}" \
        -c "\copy os_open_uprn_full FROM '${CSV_FILE}' WITH CSV HEADER"
    
    # Create the main table from the full dataset
    psql -h "${DB_ENDPOINT}" -U "${DB_USER}" -p 5432 -d "${SOURCE_DB}" \
        -c "DROP TABLE IF EXISTS os_open_uprn"
    
    psql -h "${DB_ENDPOINT}" -U "${DB_USER}" -p 5432 -d "${SOURCE_DB}" \
        -c "SELECT * INTO os_open_uprn FROM os_open_uprn_full"
    
    # Get row count
    ROW_COUNT=$(psql -h "${DB_ENDPOINT}" -U "${DB_USER}" -p 5432 -d "${SOURCE_DB}" \
        -t -c "SELECT COUNT(*) FROM os_open_uprn" | xargs)
    
    echo "Successfully seeded ${ROW_COUNT} rows into source database"
else
    echo "No CSV file provided or file does not exist. Skipping data import."
    echo "To import data later, run this script with CSV_FILE environment variable set."
    echo "Example: CSV_FILE=/path/to/data.csv ./seed-database.sh"
fi

echo "Seeding complete!"
