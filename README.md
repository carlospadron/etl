# ETL

Comparison of techs to perform ETL

# Data

OS Open UPRN
https://osdatahub.os.uk/downloads/open/OpenUPRN

full count: 41,011,955
test count: 5,000,000

run upload:
```
cd data
sh initial_upload.sh
```

# Databases

origin: postgres
target: target

create target:
```
createdb target
```

## check image sizes
```
sudo docker images
```
# check memory
chmod +x log_memory.sh