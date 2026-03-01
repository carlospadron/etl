# DuckDB Copy (Parquet)

Reads from source PostgreSQL via `postgres_scan`, exports to Parquet, then copies to target using `COPY FROM`.

Run with: `make test-etl ETL=duckdb_copy_parquet`