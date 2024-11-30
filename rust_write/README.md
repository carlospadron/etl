IN DEVELOPMENT

TODO
- numeric type
- date
- polars dataframe
- copy

```
cd rust_write
sudo docker build -t rust_write .
sudo docker images
cd ..
sudo docker rm -f rust_write || true
sudo docker run --rm --env-file .env --name rust_write rust_write
```
in other terminal
```
./log_memory.sh rust_write 5
```
