#!/bin/bash
# Entrypoint script for ILNET collector container

set -e

echo "[$(date)] Starting ILNET Collector..."

# Create log directory
mkdir -p /var/log/ilnet

# Load environment variables
if [ -f /app/.env ]; then
    echo "[$(date)] Loading .env configuration"
    set -a
    source /app/.env
    set +a
fi

# Wait for Prometheus to be ready
echo "[$(date)] Waiting for Prometheus..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://prometheus:9090/-/healthy > /dev/null 2>&1; then
        echo "[$(date)] Prometheus is ready!"
        break
    fi
    echo "[$(date)] Waiting for Prometheus... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "[$(date)] Warning: Prometheus did not become ready in time"
fi

# Wait for Redis to be ready
echo "[$(date)] Waiting for Redis..."
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if redis-cli -h redis -p 6379 ping > /dev/null 2>&1; then
        echo "[$(date)] Redis is ready!"
        break
    fi
    echo "[$(date)] Waiting for Redis... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "[$(date)] Warning: Redis did not become ready in time"
fi

echo "[$(date)] All services ready. Starting application..."

# Execute the main command
exec "$@"
