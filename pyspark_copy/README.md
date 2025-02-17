```
cd pyspark_copy
sudo docker build -t pyspark_copy .
sudo docker images
cd ..
sudo docker rm -f pyspark_copy || true
sudo docker run --rm --env-file .env --name pyspark_copy --network host pyspark_copy
```
in other terminal
```
./log_memory.sh pyspark_copy 1
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```