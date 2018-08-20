#!/bin/sh
export REDIS_URL=redis://$OPAC_PROC_REDIS_HOST:$OPAC_PROC_REDIS_PORT/0
export WORKER_PATH="/app/"

python $WORKER_PATH/opac_proc/manage.py setup_static_catalog_scheduler --all

# iniciamos todos os schedulers para ATUALIZAR identifiers de todos os modelos:
python $WORKER_PATH/opac_proc/manage.py setup_idsync_scheduler

# iniciamos todos os schedulers para PRODUCIR diffs de todos os modelos de todas as fases de todas as ações:
python $WORKER_PATH/opac_proc/manage.py setup_produce_differ_scheduler

# iniciamos todos os schedulers para CONSUMIR diffs de todos os modelos de todas as fases de todas as ações:
python $WORKER_PATH/opac_proc/manage.py setup_consume_differ_scheduler

rqscheduler \
    --url=$REDIS_URL \
    --path=$WORKER_PATH \
    --interval=2 \
    --verbose
