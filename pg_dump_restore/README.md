# pg_dump / pg_restore

Uses native PostgreSQL `pg_dump` and `pg_restore` to transfer data. Most efficient for postgres-to-postgres with no data transformation needed.

Run with: `make test-etl ETL=pg_dump_restore`