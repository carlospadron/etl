# DuckDB Copy (CSV)

Reads from source PostgreSQL via `postgres_scan`, exports to CSV, then copies to target using `COPY FROM`.

Run with: `make test-etl ETL=duckdb_copy`