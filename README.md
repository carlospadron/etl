# ETL

Comparison of techs to perform ETL

# Data

OS Open UPRN
https://osdatahub.os.uk/downloads/open/OpenUPRN

count: 41,011,955

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

# get secrets
Do once a day: 
```
export VAULT_ADDR=VAULT_URL
vault login
```
then run
```
source get_secrets.sh
```