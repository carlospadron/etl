# poors_man_etl

Simple etl built in python to replicate relatively small tables

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