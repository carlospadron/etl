# dlt (data load tool)

PostgreSQL-to-PostgreSQL EL using [dlt](https://dlthub.com/).

## How it works

1. `dlt.sources.sql_database` reads the source table via SQLAlchemy + psycopg2
2. `dlt.destinations.postgres` writes to the target database
3. `write_disposition="replace"` performs a full reload on every run
4. `apply_hints(table_name="os_open_uprn")` renames the `os_open_uprn_2m` source stream to `os_open_uprn` in the target, so both the `2m` and `full` dataset modes write to the same table

## Notes

- dlt adds internal bookkeeping columns (`_dlt_load_id`, `_dlt_id`) and tables (`_dlt_loads`, `_dlt_pipeline_state`) to the target schema — these are harmless for the benchmark
- Row-by-row inserts (10 000 rows/batch) make this significantly slower than bulk-copy methods
