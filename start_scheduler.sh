#!/bin/sh
export REDIS_URL=redis://$OPAC_PROC_REDIS_HOST:$OPAC_PROC_REDIS_PORT/0
export WORKER_PATH="/app/"

python $WORKER_PATH/opac_proc/manage.py setup_static_catalog_scheduler --all

rqscheduler \
    --url=$REDIS_URL \
    --path=$WORKER_PATH \
    --interval=2 \
    --verbose
