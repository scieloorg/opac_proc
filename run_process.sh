docker run -v /tmp/opac_proc_logs/:/app/logs/ \
    -e OPAC_PROC_COLLECTION="sss" \
    -e OPAC_PROC_MONGODB_HOST="172.17.0.2" \
    -e OPAC_PROC_MONGODB_NAME="opac_test" \
    -e OPAC_PROC_LOG_LEVEL="DEBUG" \
    opac_proc
