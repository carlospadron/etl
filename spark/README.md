## sbt project compiled with Scala 3

### Usage

This is a normal sbt project. You can compile code with `sbt compile`, run it with `sbt run`, and `sbt console` will start a Scala 3 REPL.

For more information on the sbt-dotty plugin, see the
[scala3-example-project](https://github.com/scala/scala3-example-project/blob/main/README.md).

#### Carlos' notes

# install Coursier
```
curl -fL https://github.com/coursier/coursier/releases/latest/download/cs-x86_64-pc-linux.gz | gzip -d > cs && chmod +x cs && ./cs setup
```
Get jvm 11 for spark (although last stable is 21)
```
cs java --jvm 11 -version
```

# create project
```
sbt new scala/scala3.g8
```

# run
get java home
```
eval "$(cs java --jvm 11 --env)"
```

```
cd spark
sudo docker build -t spark .
sudo docker images
cd ..
sudo docker rm -f spark || true
sudo docker run --rm --env-file .env --name spark --network host spark
```
in other terminal
```
./log_memory.sh spark 1
```
Evaluate:
```
psql -d target -c "SELECT count(*) FROM os_open_uprn"
psql -d target -c "TRUNCATE TABLE os_open_uprn"
```