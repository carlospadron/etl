```
cd duckdb_copy
sudo docker build -t duckdb_copy .
sudo docker images
cd ..
sudo docker rm -f duckdb_copy || true
sudo docker run --rm --env-file .env --name duckdb_copy --network host duckdb_copy
```
in other terminal
```
./log_memory.sh duckdb_copy 5
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```