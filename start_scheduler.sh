#!/bin/sh
export REDIS_URL=redis://$OPAC_PROC_REDIS_HOST:$OPAC_PROC_REDIS_PORT/0
export WORKER_PATH="/app/"

# limpamos as filas de scheduler e instalamos de novo todos os schedulers
python $WORKER_PATH/opac_proc/manage.py clear_and_setup_all_schedulers

rqscheduler \
    --url=$REDIS_URL \
    --path=$WORKER_PATH \
    --interval=2 \
    --verbose
