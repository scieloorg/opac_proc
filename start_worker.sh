#!/bin/sh
export REDIS_URL=redis://$OPAC_PROC_REDIS_HOST:$OPAC_PROC_REDIS_PORT/0
export WORKER_NAME=$HOSTNAME-$(cat /proc/sys/kernel/random/uuid)
export WORKER_PATH="/app/"

rq worker \
    --url=$REDIS_URL \
    --sentry-dsn=$OPAC_PROC_SENTRY_DSN \
    --path=$WORKER_PATH \
    --name=$WORKER_NAME \
    qex_collections qex_journals qex_issues qex_articles qex_press_releases qex_news \
    qtr_collections qtr_journals qtr_issues qtr_articles qtr_press_releases qtr_news \
    qlo_collections qlo_journals qlo_issues qlo_articles qlo_press_releases qlo_news \
    qpdf_catalog qxml_catalog
