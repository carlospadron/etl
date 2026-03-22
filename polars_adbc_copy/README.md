# Polars ADBC Copy

Reads from source using Polars with the ADBC engine, creates CSV in memory, then bulk copies to target via `COPY FROM STDIN`.

Run with: `make test-etl ETL=polars_adbc_copy`