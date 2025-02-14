```
cd pyspark_write
sudo docker build -t pyspark_write .
sudo docker images
cd ..
sudo docker rm -f pyspark_write || true
sudo docker run --rm --env-file .env --name pyspark_write --network host pyspark_write
```
in other terminal
```
./log_memory.sh pyspark_write 1
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```