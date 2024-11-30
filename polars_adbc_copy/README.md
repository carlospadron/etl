```
cd polars_adbc_copy
sudo docker build -t polars_adbc_copy .
sudo docker images
cd ..
sudo docker rm -f polars_adbc_copy || true
sudo docker run --rm --env-file .env --name polars_adbc_copy polars_adbc_copy
```
in other terminal
```
./log_memory.sh polars_adbc_copy 5
```