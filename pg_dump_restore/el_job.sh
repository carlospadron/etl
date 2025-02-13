#!/bin/bash

touch ~/.pgpass
chmod 600 ~/.pgpass

echo "$ORIGIN_ADDRESS:5432:$ORIGIN_DB:$ORIGIN_USER:$ORIGIN_PASS" >> ~/.pgpass
echo "$TARGET_ADDRESS:5432:$TARGET_DB:$TARGET_USER:$TARGET_PASS" >> ~/.pgpass

export SRC_DB_TABLE="os_open_uprn"

# Dump the table from the source database ONLY DATA, table needs to exist already
pg_dump -h $ORIGIN_ADDRESS -U $ORIGIN_USER -d $ORIGIN_DB -t $SRC_DB_TABLE -Fc -Oxa -f $SRC_DB_TABLE.dump

#EVALUATE EXECUTION
#pg_restore --role=$ROLE -f execution.sql $SRC_DB_TABLE.dump #

# Restore the table to the destination database
pg_restore -h $TARGET_ADDRESS -U $TARGET_USER -d $TARGET_DB --role=$ROLE $SRC_DB_TABLE.dump