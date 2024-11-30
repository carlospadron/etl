```
cd polars_connectorx_write
sudo docker build -t polars_connectorx_write .
sudo docker images
cd ..
sudo docker rm -f polars_connectorx_write || true
sudo docker run --rm --env-file .env --name polars_connectorx_write polars_connectorx_write
```
in other terminal
```
./log_memory.sh polars_connectorx_write 5
```