#!/bin/bash
# =============================================================================
# CIS - Manual Deployment Script
# =============================================================================
# Usage: ./deploy.sh [--no-migrate] [--no-build]
# =============================================================================

set -euo pipefail

COMPOSE_DIR="/opt/cis"
COMPOSE_CMD="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"
NO_MIGRATE=false
NO_BUILD=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --no-migrate) NO_MIGRATE=true ;;
        --no-build)   NO_BUILD=true ;;
        --help)
            echo "Usage: $0 [--no-migrate] [--no-build]"
            echo "  --no-migrate  Skip database migrations"
            echo "  --no-build    Skip building images (use existing)"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

cd "$COMPOSE_DIR"

echo "=== CIS Deployment Script ==="
echo "[$(date)] Starting deployment..."

# Pull latest code
echo "[$(date)] Pulling latest code from main..."
git pull origin main

# Build and restart services
if [ "$NO_BUILD" = true ]; then
    echo "[$(date)] Starting services (no build)..."
    $COMPOSE_CMD up -d
else
    echo "[$(date)] Building and starting services..."
    $COMPOSE_CMD up -d --build
fi

# Wait for services to be ready
echo "[$(date)] Waiting for services to start..."
sleep 10

# Run migrations
if [ "$NO_MIGRATE" = true ]; then
    echo "[$(date)] Skipping database migrations (--no-migrate)."
else
    echo "[$(date)] Running database migrations..."
    $COMPOSE_CMD exec -T backend alembic upgrade head
fi

# Health check
echo "[$(date)] Running health check..."
sleep 5
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "[$(date)] Health check passed."
else
    echo "[$(date)] WARNING: Health check failed! Check service logs:"
    echo "  $COMPOSE_CMD logs --tail=50 backend"
    echo "  $COMPOSE_CMD logs --tail=50 nginx"
fi

# Show service status
echo ""
echo "[$(date)] Service status:"
$COMPOSE_CMD ps

echo ""
echo "[$(date)] Deployment completed."
