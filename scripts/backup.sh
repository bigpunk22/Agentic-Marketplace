#!/usr/bin/env bash
# Agentic Marketplace — Backup Script
# Usage: ./scripts/backup.sh
# Recommended: Run daily via cron

set -euo pipefail

# ── Configuration ─────────────────────────────────────────
BACKUP_DIR="/backups/agentic-marketplace"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7
LOG_FILE="/var/log/agentic-backup.log"

# ── Colors ─────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# ── Backup Directory ──────────────────────────────────────
mkdir -p "$BACKUP_DIR"

# ── PostgreSQL Backup ─────────────────────────────────────
backup_postgres() {
    log "Starting PostgreSQL backup..."
    
    local backup_file="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql.gz"
    
    docker exec am_postgres pg_dump -U agentic agentic_marketplace | gzip > "$backup_file"
    
    if [ -f "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "${GREEN}[✓]${NC} PostgreSQL backup complete: $backup_file ($size)"
    else
        log "${RED}[✗]${NC} PostgreSQL backup failed"
    fi
}

# ── Redis Backup ──────────────────────────────────────────
backup_redis() {
    log "Starting Redis backup..."
    
    local backup_file="$BACKUP_DIR/redis_backup_${TIMESTAMP}.rdb"
    
    # Trigger BGSAVE
    docker exec am_redis redis-cli -a "${REDIS_PASSWORD:-}" BGSAVE
    
    # Wait for save to complete
    sleep 5
    
    # Copy RDB file
    docker cp am_redis:/data/dump.rdb "$backup_file" 2>/dev/null || true
    
    if [ -f "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "${GREEN}[✓]${NC} Redis backup complete: $backup_file ($size)"
    else
        log "${YELLOW}[!]${NC} Redis backup skipped (may not be ready)"
    fi
}

# ── MinIO Backup ─────────────────────────────────────────
backup_minio() {
    log "Starting MinIO data backup..."
    
    local backup_dir="$BACKUP_DIR/minio_backup_${TIMESTAMP}"
    mkdir -p "$backup_dir"
    
    # Copy data volume
    docker cp am_minio:/data/. "$backup_dir/" 2>/dev/null || true
    
    # Compress
    tar -czf "${backup_dir}.tar.gz" -C "$backup_dir" . 2>/dev/null || true
    rm -rf "$backup_dir"
    
    if [ -f "${backup_dir}.tar.gz" ]; then
        local size=$(du -h "${backup_dir}.tar.gz" | cut -f1)
        log "${GREEN}[✓]${NC} MinIO backup complete: ${backup_dir}.tar.gz ($size)"
    else
        log "${YELLOW}[!]${NC} MinIO backup skipped"
    fi
}

# ── Configuration Backup ─────────────────────────────────
backup_config() {
    log "Backing up configuration files..."
    
    local config_backup="$BACKUP_DIR/config_backup_${TIMESTAMP}.tar.gz"
    
    tar -czf "$config_backup" \
        backend/.env.production \
        frontend/.env.production \
        docker-compose.production.yml \
        nginx/nginx.conf \
        scripts/ \
        2>/dev/null || true
    
    log "${GREEN}[✓]${NC} Configuration backup complete"
}

# ── Cleanup Old Backups ───────────────────────────────────
cleanup() {
    log "Cleaning up backups older than ${RETENTION_DAYS} days..."
    
    local deleted=0
    
    for pattern in "db_backup_*.sql.gz" "redis_backup_*.rdb" "minio_backup_*.tar.gz" "config_backup_*.tar.gz"; do
        while IFS= read -r file; do
            rm -f "$file"
            ((deleted++))
        done < <(find "$BACKUP_DIR" -name "$pattern" -mtime "+${RETENTION_DAYS}")
    done
    
    log "${GREEN}[✓]${NC} Cleaned up $deleted old backup files"
}

# ── Summary ───────────────────────────────────────────────
summary() {
    echo ""
    log "═══════════════════════════════════════════"
    log "  Backup Summary"
    log "═══════════════════════════════════════════"
    echo ""
    
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    local file_count=$(find "$BACKUP_DIR" -type f | wc -l)
    
    log "  Backup directory: $BACKUP_DIR"
    log "  Total size: $total_size"
    log "  Total files: $file_count"
    echo ""
    log "  Recent backups:"
    ls -lt "$BACKUP_DIR" | head -10
    echo ""
    log "═══════════════════════════════════════════"
}

# ── Main ──────────────────────────────────────────────────
main() {
    log "Starting backup at $TIMESTAMP"
    
    backup_postgres
    backup_redis
    backup_minio
    backup_config
    cleanup
    summary
    
    log "Backup complete!"
}

main "$@"
