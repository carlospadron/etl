```
cd pg_dump_restore
sudo docker build -t pg_dump_restore .
sudo docker images
cd ..
sudo docker rm -f pg_dump_restore || true
sudo docker run --rm --env-file .env --name pg_dump_restore --network host pg_dump_restore
```
in other terminal
```
./log_memory.sh pg_dump_restore 5
```

Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```