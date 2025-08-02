```
cd meltano
sudo docker build -t meltano .
sudo docker images
cd ..
sudo docker rm -f meltano || true
sudo docker run --rm --env-file .env --name meltano --network host meltano
```
in other terminal
```
./log_memory.sh meltano 5
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```