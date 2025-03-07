```
cd sling
sudo docker build -t sling .
sudo docker images
cd ..
sudo docker rm -f sling || true
sudo docker run --rm --env-file .env --name sling --network host sling
```
in other terminal
```
./log_memory.sh sling 5
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```