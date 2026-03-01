# PySpark Copy

Reads from source via JDBC into a Spark DataFrame, writes to CSV, then bulk copies to target via `COPY FROM STDIN`.

Run with: `make test-etl ETL=pyspark_copy`