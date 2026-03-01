# PySpark Write

Reads from source via JDBC into a Spark DataFrame, then writes directly to target via JDBC with repartitioning.

Run with: `make test-etl ETL=pyspark_write`