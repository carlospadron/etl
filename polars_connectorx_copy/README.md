# Polars ConnectorX Copy

Reads from source using Polars with ConnectorX engine (partitioned), creates CSV in memory, then bulk copies to target via `COPY FROM STDIN`.

Run with: `make test-etl ETL=polars_connectorx_copy`