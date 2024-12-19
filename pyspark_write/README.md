```
cd pyspark_write
sudo docker build -t pyspark_write .
sudo docker images
cd ..
sudo docker rm -f pyspark_write || true
sudo docker run --rm --env-file .env --name pyspark_write pyspark_write
```
in other terminal
```
./log_memory.sh pyspark_write 5
```