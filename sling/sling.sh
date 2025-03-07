#!/bin/bash

echo $SOURCEDB
echo $TARGETDB

export SLING_THREADS=3
sling run \
    --src-conn SOURCEDB \
    --src-stream 'public.os_open_uprn' \
    --tgt-conn TARGETDB \
    --tgt-object 'public.{stream_table}' \
    --mode full-refresh  