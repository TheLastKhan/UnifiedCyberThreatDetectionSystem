#!/bin/bash
# ============================================
# Production Startup Script
# Unified Cyber Threat Detection System
# ============================================

set -e

echo "============================================"
echo "Starting Unified Threat Detection System"
echo "============================================"

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Wait for database
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up!"

# Run database migrations (if any)
echo "Running database migrations..."
# python manage.py db upgrade

# Load ML models
echo "Checking ML models..."
if [ ! -f "models/email_detector_stacking.pkl" ]; then
    echo "WARNING: Trained models not found!"
    echo "Please train models first: python train_models.py"
fi

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers ${WORKERS:-4} \
    --threads ${THREADS:-2} \
    --worker-class ${WORKER_CLASS:-sync} \
    --timeout ${TIMEOUT:-120} \
    --keepalive ${KEEPALIVE:-5} \
    --max-requests ${MAX_REQUESTS:-1000} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \
    --access-logfile ${ACCESS_LOG:-"-"} \
    --error-logfile ${ERROR_LOG:-"-"} \
    --log-level ${LOG_LEVEL:-info} \
    --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s' \
    web_dashboard.app:app
