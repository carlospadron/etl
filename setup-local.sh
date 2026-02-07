#!/usr/bin/env bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/data"
CSV_FILE="${DATA_DIR}/osopenuprn_202502.csv"

# Database connection details for docker-compose setup
SOURCE_HOST="localhost"
SOURCE_PORT="5432"
SOURCE_DB="postgres"
SOURCE_USER="postgres"
SOURCE_PASS="postgres"

TARGET_HOST="localhost"
TARGET_PORT="5433"
TARGET_DB="target"
TARGET_USER="postgres"
TARGET_PASS="postgres"

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command -v psql &> /dev/null; then
        missing_deps+=("postgresql-client (psql)")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_info "All dependencies found."
}

start_databases() {
    print_info "Starting PostgreSQL databases with Docker Compose..."
    
    # Use docker compose (new) or docker-compose (old)
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    
    print_info "Waiting for databases to be ready..."
    sleep 5
    
    # Wait for source database
    for i in {1..30}; do
        if PGPASSWORD="${SOURCE_PASS}" psql -h "${SOURCE_HOST}" -p "${SOURCE_PORT}" -U "${SOURCE_USER}" -d "${SOURCE_DB}" -c "SELECT 1" &> /dev/null; then
            print_info "Source database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Source database did not become ready in time"
            exit 1
        fi
        sleep 2
    done
    
    # Wait for target database
    for i in {1..30}; do
        if PGPASSWORD="${TARGET_PASS}" psql -h "${TARGET_HOST}" -p "${TARGET_PORT}" -U "${TARGET_USER}" -d "${TARGET_DB}" -c "SELECT 1" &> /dev/null; then
            print_info "Target database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Target database did not become ready in time"
            exit 1
        fi
        sleep 2
    done
}

seed_data() {
    print_info "Checking for CSV data file..."
    
    if [ ! -f "${CSV_FILE}" ]; then
        print_warning "CSV file not found at ${CSV_FILE}"
        print_info "You can download the OS Open UPRN dataset from:"
        print_info "https://osdatahub.os.uk/downloads/open/OpenUPRN"
        print_info "Place the CSV file at: ${CSV_FILE}"
        print_warning "Skipping data seeding. You can run this script again after downloading the data."
        return 0
    fi
    
    print_info "Seeding data into source database..."
    print_info "This may take a while depending on the size of your CSV file..."
    
    export PGPASSWORD="${SOURCE_PASS}"
    
    # Import data into temporary table
    psql -h "${SOURCE_HOST}" -p "${SOURCE_PORT}" -U "${SOURCE_USER}" -d "${SOURCE_DB}" \
        -c "\copy os_open_uprn_full FROM '${CSV_FILE}' WITH CSV HEADER"
    
    # Create the main table from the full dataset
    # You can limit the rows by uncommenting the LIMIT clause
    psql -h "${SOURCE_HOST}" -p "${SOURCE_PORT}" -U "${SOURCE_USER}" -d "${SOURCE_DB}" \
        -c "DROP TABLE IF EXISTS os_open_uprn"
    
    # For testing with smaller dataset, use LIMIT 2000000
    # psql -h "${SOURCE_HOST}" -p "${SOURCE_PORT}" -U "${SOURCE_USER}" -d "${SOURCE_DB}" \
    #     -c "SELECT * INTO os_open_uprn FROM os_open_uprn_full LIMIT 2000000"
    
    # For full dataset
    psql -h "${SOURCE_HOST}" -p "${SOURCE_PORT}" -U "${SOURCE_USER}" -d "${SOURCE_DB}" \
        -c "SELECT * INTO os_open_uprn FROM os_open_uprn_full"
    
    # Get row count
    ROW_COUNT=$(psql -h "${SOURCE_HOST}" -p "${SOURCE_PORT}" -U "${SOURCE_USER}" -d "${SOURCE_DB}" \
        -t -c "SELECT COUNT(*) FROM os_open_uprn")
    
    print_info "Successfully seeded ${ROW_COUNT} rows into source database"
    
    unset PGPASSWORD
}

print_connection_info() {
    print_info "================================================"
    print_info "Database Setup Complete!"
    print_info "================================================"
    echo ""
    print_info "Source Database Connection:"
    echo "  Host: ${SOURCE_HOST}"
    echo "  Port: ${SOURCE_PORT}"
    echo "  Database: ${SOURCE_DB}"
    echo "  Username: ${SOURCE_USER}"
    echo "  Password: ${SOURCE_PASS}"
    echo ""
    print_info "Target Database Connection:"
    echo "  Host: ${TARGET_HOST}"
    echo "  Port: ${TARGET_PORT}"
    echo "  Database: ${TARGET_DB}"
    echo "  Username: ${TARGET_USER}"
    echo "  Password: ${TARGET_PASS}"
    echo ""
    print_info "Connection strings:"
    echo "  Source: postgresql://${SOURCE_USER}:${SOURCE_PASS}@${SOURCE_HOST}:${SOURCE_PORT}/${SOURCE_DB}"
    echo "  Target: postgresql://${TARGET_USER}:${TARGET_PASS}@${TARGET_HOST}:${TARGET_PORT}/${TARGET_DB}"
    echo ""
    print_info "To stop the databases, run: docker-compose down"
    print_info "To remove all data, run: docker-compose down -v"
}

# Main execution
main() {
    print_info "ETL Project - Database Setup Script"
    echo ""
    
    check_dependencies
    start_databases
    seed_data
    print_connection_info
}

# Run main function
main
