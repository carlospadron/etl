```
cd modin_copy
sudo docker build -t modin_copy .
sudo docker images
cd ..
sudo docker rm -f modin_copy || true
sudo docker run --rm --env-file .env --name modin_copy --network host modin_copy
```
in other terminal
```
./log_memory.sh modin_copy 5
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```