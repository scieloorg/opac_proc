docker run -v /tmp/opac_proc_logs/:/app/logs/ \
    -e OPAC_PROC_COLLECTION="sss" \
    -e OPAC_PROC_MONGODB_HOST="192.168.169.196" \
    -e OPAC_PROC_MONGODB_NAME="opac" \
    -e OPAC_PROC_LOG_LEVEL="DEBUG" \
    scieloorg/opac_proc
