```
cd pandas_to_sql
sudo docker build -t pandas_to_sql .
sudo docker images
cd ..
sudo docker rm -f pandas_to_sql || true
sudo docker run --rm --env-file .env --name pandas_to_sql --network host pandas_to_sql
```
in other terminal
```
./log_memory.sh pandas_to_sql 5
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```