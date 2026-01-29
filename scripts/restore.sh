#!/bin/bash
# =============================================================================
# CIS Database Restore Script
# =============================================================================
# Usage: ./restore.sh /path/to/db_backup.dump
# =============================================================================

set -euo pipefail

COMPOSE_DIR="/opt/cis"

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <backup_file.dump>"
    echo ""
    echo "Available backups:"
    ls -lht /opt/cis/backups/db_*.dump 2>/dev/null || echo "  No backups found in /opt/cis/backups/"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=== CIS Database Restore ==="
echo "Backup file: $BACKUP_FILE"
echo "File size:   $(du -h "$BACKUP_FILE" | cut -f1)"
echo "File date:   $(stat -c %y "$BACKUP_FILE" 2>/dev/null || stat -f %Sm "$BACKUP_FILE" 2>/dev/null)"
echo ""

# Verify checksum if available
BACKUP_DIR=$(dirname "$BACKUP_FILE")
BACKUP_NAME=$(basename "$BACKUP_FILE")
DATE_PART=$(echo "$BACKUP_NAME" | sed 's/db_\(.*\)\.dump/\1/')
CHECKSUM_FILE="$BACKUP_DIR/checksums_${DATE_PART}.txt"

if [ -f "$CHECKSUM_FILE" ]; then
    echo "Verifying checksum..."
    cd "$BACKUP_DIR"
    if sha256sum -c "$CHECKSUM_FILE" --ignore-missing 2>/dev/null; then
        echo "Checksum verified OK."
    else
        echo "WARNING: Checksum verification failed!"
        read -p "Continue anyway? (yes/no): " checksum_confirm
        if [ "$checksum_confirm" != "yes" ]; then
            echo "Aborted."
            exit 1
        fi
    fi
    echo ""
fi

echo "WARNING: This will replace the current database with the backup."
echo "All current data will be lost."
echo ""
read -p "Are you sure? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "[$(date)] Restoring database from $BACKUP_FILE..."

docker-compose -f "$COMPOSE_DIR/docker-compose.yml" -f "$COMPOSE_DIR/docker-compose.prod.yml" \
    exec -T db pg_restore -U cis -d cis --clean --if-exists < "$BACKUP_FILE"

echo "[$(date)] Database restored successfully."
echo ""
echo "You may want to restart the backend service:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart backend"
