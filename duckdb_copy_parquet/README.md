```
cd duckdb_copy_parquet
sudo docker build -t duckdb_copy_parquet .
sudo docker images
cd ..
sudo docker rm -f duckdb_copy_parquet || true
sudo docker run --rm --env-file .env --name duckdb_copy_parquet --network host duckdb_copy_parquet
```
in other terminal
```
./log_memory.sh duckdb_copy_parquet 5
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```