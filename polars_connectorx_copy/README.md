```
cd polars_connectorx_copy
sudo docker build -t polars_connectorx_copy .
sudo docker images
cd ..
sudo docker rm -f polars_connectorx_copy || true
sudo docker run --rm --env-file .env --name polars_connectorx_copy polars_connectorx_copy
```
in other terminal
```
./log_memory.sh polars_connectorx_copy 5
```