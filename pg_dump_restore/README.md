```
cd pg_dump_restore
docker build -t pg_dump_restore .
docker images
cd ..
docker rm -f pg_dump_restore || true
docker run --rm --env-file .env --name pg_dump_restore --network host pg_dump_restore
```
in other terminal
```
./log_memory.sh pg_dump_restore 5
```

Evaluate:
```
psql -h localhost -p 5433 -U postgres -d target -c "SELECT count(*) FROM os_open_uprn"
psql -h localhost -p 5433 -U postgres -d target -c "TRUNCATE TABLE os_open_uprn"
```