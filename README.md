# ETL

Comparison of techs to perform ETL

# Data

OS Open UPRN
https://osdatahub.os.uk/downloads/open/OpenUPRN

full count: 41,011,955
test count: 2,000,000

run upload:
```
cd data
sh initial_upload.sh
```

# Databases

origin: postgres
target: target

create target:
```
createdb target
```

## check image sizes
```
sudo docker images
```
# check memory
chmod +x log_memory.sh


# Conclusions

## Sling
- Great for replications as it includes many inbuild features (retries, streaming etc)
- it has a very low memory impact
- it is not as fast as other solutions

## DuckDB 
- is a winner (in terms of execution time) for both small and large datasets
- it is not distributed so it might struggle with very large datasets
- it is mostly sql based. Familiar for many but might have limitations.

## Spark
- handles well memory for both small and large datasets
- not as fast as duckdb
- it is distributed so it can handle very large datasets (Terabytes)
- allows SQL, python and scala
- It also has machine learning and graph theory capabilities

## Polars
- Very efficient compared to Pandas and for small datasets competes well against spark.
- Very similar to pandas.