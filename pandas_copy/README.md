```
cd pandas_copy
sudo docker build -t pandas_copy .
sudo docker images
cd ..
sudo docker rm -f pandas_copy || true
sudo docker run --rm --env-file .env --name pandas_copy pandas_copy
```
in other terminal
```
./log_memory.sh pandas_copy 5
```