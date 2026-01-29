#!/bin/bash
# =============================================================================
# CIS Database and Files Backup Script
# =============================================================================
# Run via cron: 0 2 * * * /opt/cis/scripts/backup.sh >> /var/log/cis-backup.log 2>&1
# =============================================================================

set -euo pipefail

BACKUP_DIR="/opt/cis/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
COMPOSE_DIR="/opt/cis"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. PostgreSQL backup
echo "[$(date)] Starting PostgreSQL backup..."
docker-compose -f "$COMPOSE_DIR/docker-compose.yml" -f "$COMPOSE_DIR/docker-compose.prod.yml" \
    exec -T db pg_dump -U cis -Fc cis > "$BACKUP_DIR/db_${DATE}.dump"

if [ ! -s "$BACKUP_DIR/db_${DATE}.dump" ]; then
    echo "[$(date)] ERROR: PostgreSQL backup file is empty!"
    exit 1
fi

echo "[$(date)] PostgreSQL backup completed: db_${DATE}.dump ($(du -h "$BACKUP_DIR/db_${DATE}.dump" | cut -f1))"

# 2. MinIO backup (copy data directory)
echo "[$(date)] Starting MinIO backup..."
tar -czf "$BACKUP_DIR/minio_${DATE}.tar.gz" -C /opt/cis/data minio 2>/dev/null || true
echo "[$(date)] MinIO backup completed."

# 3. Compress and checksum
echo "[$(date)] Creating checksums..."
cd "$BACKUP_DIR"
sha256sum "db_${DATE}.dump" "minio_${DATE}.tar.gz" > "checksums_${DATE}.txt"

# 4. Cleanup old backups
echo "[$(date)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -type f -mtime +${RETENTION_DAYS} -delete

echo "[$(date)] Backup completed successfully."
echo "Files:"
ls -lh "$BACKUP_DIR/db_${DATE}.dump" "$BACKUP_DIR/minio_${DATE}.tar.gz" "$BACKUP_DIR/checksums_${DATE}.txt"
