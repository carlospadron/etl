# Pandas Copy

Reads from source using `pd.read_sql`, creates CSV in memory, then bulk copies to target via `COPY FROM STDIN`.

Run with: `make test-etl ETL=pandas_copy`