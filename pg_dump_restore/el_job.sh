#!/bin/bash

touch ~/.pgpass
chmod 600 ~/.pgpass

echo "$sf_db_address:5432:$sf_db_name:$sf_user:$sf_pass" >> ~/.pgpass
echo "$db_address_stag:5432:$db_name:$data_uploads_user:$data_uploads_pass_staging" >> ~/.pgpass

export SRC_DB_TABLE="source.table"
export ROLE="gis_admin"

# Dump the table from the source database ONLY DATA, table needs to exist already
pg_dump -h $sf_db_address -U $sf_user -d $sf_db_name -t $SRC_DB_TABLE -Fc -Oxa -f $SRC_DB_TABLE.dump

#EVALUATE EXECUTION
#pg_restore --role=$ROLE -f execution.sql $SRC_DB_TABLE.dump #

# Restore the table to the destination database
pg_restore -h $db_address_stag -U $data_uploads_user -d $db_name --role=$ROLE $SRC_DB_TABLE.dump