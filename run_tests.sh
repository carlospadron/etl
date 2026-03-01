#!/usr/bin/env bash

set -euo pipefail

# Centralised ETL benchmark runner
# Builds Docker images, runs containers, monitors memory, validates counts,
# and generates a text report.

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
REPORT_FILE="${SCRIPT_DIR}/benchmark_report.txt"
MEMORY_INTERVAL=2

# All ETL methods with Dockerfiles
ALL_METHODS=(
    duckdb_copy
    duckdb_copy_parquet
    pandas_copy
    pandas_to_sql
    pg_dump_restore
    polars_adbc_copy
    polars_connectorx_copy
    polars_connectorx_write
    pyspark_copy
    pyspark_write
    sling
    spark
)

print_info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    echo "Usage: $0 [options] [method ...]"
    echo ""
    echo "Run ETL benchmarks for one or more methods."
    echo "If no methods are specified, all methods are run."
    echo ""
    echo "Options:"
    echo "  -e, --env FILE    Path to .env file (default: .env)"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Available methods:"
    for m in "${ALL_METHODS[@]}"; do
        echo "  $m"
    done
}

load_env() {
    if [ ! -f "${ENV_FILE}" ]; then
        print_error ".env file not found at ${ENV_FILE}"
        print_info "Run 'make setup-local' to generate it."
        exit 1
    fi
    set -a
    # shellcheck source=/dev/null
    source "${ENV_FILE}"
    set +a
    print_info "Loaded environment from ${ENV_FILE}"
}

get_row_count() {
    local host="$1" port="$2" user="$3" pass="$4" db="$5" table="$6"
    PGPASSWORD="${pass}" psql -h "${host}" -p "${port}" -U "${user}" -d "${db}" \
        -t -A -c "SELECT COUNT(*) FROM ${table}" 2>/dev/null || echo "ERROR"
}

truncate_target_table() {
    local table="$1"
    PGPASSWORD="${TARGET_PASS}" psql \
        -h "${TARGET_ADDRESS}" -p "${TARGET_PORT}" \
        -U "${TARGET_USER}" -d "${TARGET_DB}" \
        -c "TRUNCATE TABLE ${table}" > /dev/null 2>&1 || true
}

monitor_memory() {
    local container_name="$1" log_file="$2"
    echo "Timestamp,MemoryUsage" > "${log_file}"
    while docker inspect "${container_name}" > /dev/null 2>&1; do
        local mem
        mem=$(docker stats --no-stream --format "{{.MemUsage}}" "${container_name}" 2>/dev/null | awk '{print $1}') || true
        if [ -n "${mem}" ]; then
            echo "$(date +"%Y-%m-%d %H:%M:%S"),${mem}" >> "${log_file}"
        fi
        sleep "${MEMORY_INTERVAL}"
    done
}

get_peak_memory() {
    local log_file="$1"
    if [ ! -f "${log_file}" ]; then
        echo "N/A"
        return
    fi
    # Parse memory values, convert to MiB, find max
    tail -n +2 "${log_file}" | awk -F',' '{
        val = $2
        if (val ~ /GiB/) { gsub(/GiB/, "", val); mb = val * 1024 }
        else if (val ~ /MiB/) { gsub(/MiB/, "", val); mb = val }
        else if (val ~ /KiB/) { gsub(/KiB/, "", val); mb = val / 1024 }
        else if (val ~ /B/)   { gsub(/B/, "", val); mb = val / 1048576 }
        else { mb = 0 }
        if (mb > max) max = mb
    } END { if (max > 0) printf "%.1fMiB\n", max; else print "N/A" }'
}

build_image() {
    local method="$1"
    local dir="${SCRIPT_DIR}/${method}"
    if [ ! -f "${dir}/Dockerfile" ]; then
        print_error "No Dockerfile found for ${method}"
        return 1
    fi
    print_info "Building image for ${method}..."
    docker build -t "etl-${method}" "${dir}" > /dev/null 2>&1
}

run_single_test() {
    local method="$1"
    local table="os_open_uprn"
    local container_name="etl-${method}"
    local mem_log="/tmp/etl_mem_${method}.csv"

    print_info "--- Running: ${method} ---"

    # Build image
    if ! build_image "${method}"; then
        echo "${method}|BUILD_FAILED|0|N/A|N/A|N/A|FAIL"
        return
    fi

    # Truncate target table
    truncate_target_table "${table}"

    # Get source count
    local source_count
    source_count=$(get_row_count "${ORIGIN_ADDRESS}" "${ORIGIN_PORT}" \
        "${ORIGIN_USER}" "${ORIGIN_PASS}" "${ORIGIN_DB}" "${table}")

    # Remove any previous container with the same name
    docker rm -f "${container_name}" > /dev/null 2>&1 || true

    # Start container detached
    local start_time
    start_time=$(date +%s)

    docker run -d --name "${container_name}" \
        --network host \
        --env-file "${ENV_FILE}" \
        "etl-${method}" > /dev/null 2>&1

    # Start memory monitor in background
    monitor_memory "${container_name}" "${mem_log}" &
    local monitor_pid=$!

    # Wait for container to finish
    local exit_code
    exit_code=$(docker wait "${container_name}" 2>/dev/null) || exit_code=1

    local end_time
    end_time=$(date +%s)
    local duration=$(( end_time - start_time ))

    # Stop memory monitor
    kill "${monitor_pid}" 2>/dev/null || true
    wait "${monitor_pid}" 2>/dev/null || true

    # Get peak memory
    local peak_mem
    peak_mem=$(get_peak_memory "${mem_log}")

    # Get target count
    local target_count
    target_count=$(get_row_count "${TARGET_ADDRESS}" "${TARGET_PORT}" \
        "${TARGET_USER}" "${TARGET_PASS}" "${TARGET_DB}" "${table}")

    # Validate
    local status="PASS"
    if [ "${exit_code}" != "0" ]; then
        status="FAIL (exit code ${exit_code})"
    elif [ "${source_count}" = "ERROR" ] || [ "${target_count}" = "ERROR" ]; then
        status="FAIL (count error)"
    elif [ "${source_count}" != "${target_count}" ]; then
        status="FAIL (count mismatch)"
    fi

    # Clean up container
    docker rm -f "${container_name}" > /dev/null 2>&1 || true
    rm -f "${mem_log}"

    if [[ "${status}" == "PASS" ]]; then
        print_info "${method}: PASS (${duration}s, peak ${peak_mem})"
    else
        print_error "${method}: ${status} (${duration}s)"
    fi

    # Return result as pipe-separated line
    echo "${method}|${exit_code}|${duration}|${peak_mem}|${source_count}|${target_count}|${status}"
}

generate_report() {
    local results_file="$1"

    {
        echo "============================================"
        echo "  ETL Benchmark Report"
        echo "============================================"
        echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "Source: ${ORIGIN_ADDRESS}:${ORIGIN_PORT}/${ORIGIN_DB}"
        echo "Target: ${TARGET_ADDRESS}:${TARGET_PORT}/${TARGET_DB}"
        echo "Table:  os_open_uprn"
        echo ""
        echo "--------------------------------------------"
        echo "Results"
        echo "--------------------------------------------"
        echo ""

        local total=0 passed=0 failed=0

        while IFS='|' read -r method exit_code duration peak_mem source_count target_count status; do
            total=$((total + 1))
            echo "Test: ${method}"
            echo "  Duration:     ${duration}s"
            echo "  Peak Memory:  ${peak_mem}"
            echo "  Source Count: ${source_count}"
            echo "  Target Count: ${target_count}"
            echo "  Validation:   ${status}"
            echo ""
            if [ "${status}" = "PASS" ]; then
                passed=$((passed + 1))
            else
                failed=$((failed + 1))
            fi
        done < "${results_file}"

        echo "--------------------------------------------"
        echo "Summary"
        echo "--------------------------------------------"
        echo "Total tests: ${total}"
        echo "Passed:      ${passed}"
        echo "Failed:      ${failed}"
        echo "============================================"
    } > "${REPORT_FILE}"

    print_info "Report written to ${REPORT_FILE}"
}

main() {
    local methods=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -e|--env)
                ENV_FILE="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                methods+=("$1")
                shift
                ;;
        esac
    done

    # Default to all methods
    if [ ${#methods[@]} -eq 0 ]; then
        methods=("${ALL_METHODS[@]}")
    fi

    # Validate methods
    for method in "${methods[@]}"; do
        local valid=false
        for m in "${ALL_METHODS[@]}"; do
            if [ "${method}" = "${m}" ]; then
                valid=true
                break
            fi
        done
        if [ "${valid}" = false ]; then
            print_error "Unknown method: ${method}"
            usage
            exit 1
        fi
    done

    load_env

    print_info "Running ${#methods[@]} ETL benchmark(s)..."
    echo ""

    local results_tmp="/tmp/etl_results_$$.txt"
    > "${results_tmp}"

    for method in "${methods[@]}"; do
        result=$(run_single_test "${method}")
        echo "${result}" >> "${results_tmp}"
        echo ""
    done

    generate_report "${results_tmp}"
    rm -f "${results_tmp}"

    echo ""
    cat "${REPORT_FILE}"
}

main "$@"
