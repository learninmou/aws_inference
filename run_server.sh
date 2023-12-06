CURDIR=$(cd "$(dirname "$0")"; pwd)
cd $CURDIR

export ENV_LOG_DIR="${CURDIR}/logs"
export ENV_AWS_ENDPOINTS_FILE="${CURDIR}/endpoints.ini"
export ENV_AWS_AK=""
export ENV_AWS_SK=""

mkdir -p $ENV_LOG_DIR
gunicorn launcher:app \
    --bind 0.0.0.0:8080 \
    --workers 8 \
    --threads 1 \
    --timeout 90 \
    --worker-class "uvicorn.workers.UvicornWorker" \
    --access-logfile "${ENV_LOG_DIR}/access.log"
