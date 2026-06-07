#!/usr/bin/env bash
# Agentic Marketplace — Production Deployment Script
# Usage: ./scripts/deploy.sh [environment]

set -euo pipefail

# ── Colors ─────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── Configuration ─────────────────────────────────────────
ENV="${1:-production}"
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE="backend/.env.production"
BACKUP_DIR="/backups/agentic-marketplace"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEPLOY_LOG="/tmp/deploy_${TIMESTAMP}.log"

# ── Functions ─────────────────────────────────────────────
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$DEPLOY_LOG"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$DEPLOY_LOG"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$DEPLOY_LOG"
}

error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$DEPLOY_LOG"
    exit 1
}

# ── Pre-flight Checks ─────────────────────────────────────
preflight() {
    log "Running pre-flight checks..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        error "Docker Compose is not available"
    fi

    # Check env file
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file not found: $ENV_FILE"
    fi

    # Check required env variables
    required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "MINIO_ROOT_PASSWORD" "JWT_SECRET_KEY" "OPENROUTER_API_KEY")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$ENV_FILE"; then
            warn "Missing env variable: $var"
        fi
    done

    success "Pre-flight checks passed"
}

# ── Backup ────────────────────────────────────────────────
backup() {
    log "Creating backup before deployment..."

    mkdir -p "$BACKUP_DIR"

    # Backup PostgreSQL
    docker compose -f "$COMPOSE_FILE" exec -T postgres \
        pg_dump -U agentic agentic_marketplace | \
        gzip > "$BACKUP_DIR/db_backup_${TIMESTAMP}.sql.gz" 2>/dev/null || \
        warn "Database backup failed (may be first deploy)"

    # Cleanup old backups (keep 7 days)
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete 2>/dev/null || true

    success "Backup completed"
}

# ── Deploy ────────────────────────────────────────────────
deploy() {
    log "Starting deployment to ${ENV}..."

    log "Pulling latest images..."
    docker compose -f "$COMPOSE_FILE" pull 2>&1 | tee -a "$DEPLOY_LOG"

    log "Building application images..."
    docker compose -f "$COMPOSE_FILE" build --no-cache 2>&1 | tee -a "$DEPLOY_LOG"

    log "Starting infrastructure services..."
    docker compose -f "$COMPOSE_FILE" up -d postgres redis qdrant minio 2>&1 | tee -a "$DEPLOY_LOG"

    log "Waiting for infrastructure to be healthy..."
    sleep 10

    # Check PostgreSQL
    for i in {1..30}; do
        if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U agentic &>/dev/null; then
            success "PostgreSQL is ready"
            break
        fi
        if [ "$i" -eq 30 ]; then
            error "PostgreSQL failed to start"
        fi
        sleep 2
    done

    log "Running database migrations..."
    docker compose -f "$COMPOSE_FILE" run --rm backend \
        python -c "import asyncio; from app.db.base import Base, engine; asyncio.run(Base.metadata.create_all(engine))" \
        2>&1 | tee -a "$DEPLOY_LOG" || warn "Migration step skipped"

    log "Starting application services..."
    docker compose -f "$COMPOSE_FILE" up -d backend frontend celery-worker celery-beat 2>&1 | tee -a "$DEPLOY_LOG"

    log "Starting nginx..."
    docker compose -f "$COMPOSE_FILE" up -d nginx 2>&1 | tee -a "$DEPLOY_LOG"

    success "Deployment complete"
}

# ── Health Checks ─────────────────────────────────────────
health_check() {
    log "Running health checks..."

    local failed=0

    # Backend health
    for i in {1..12}; do
        if curl -sf http://localhost:8000/health &>/dev/null; then
            success "Backend is healthy"
            break
        fi
        if [ "$i" -eq 12 ]; then
            error "Backend health check failed"
            failed=1
        fi
        sleep 5
    done

    # Frontend health
    if curl -sf http://localhost:3000 &>/dev/null; then
        success "Frontend is healthy"
    else
        warn "Frontend health check failed (may still be starting)"
    fi

    # Nginx health
    if curl -sf http://localhost/health &>/dev/null; then
        success "Nginx is healthy"
    else
        warn "Nginx health check failed"
    fi

    return $failed
}

# ── Rollback ──────────────────────────────────────────────
rollback() {
    warn "Deployment failed! Rolling back..."

    docker compose -f "$COMPOSE_FILE" down 2>&1 | tee -a "$DEPLOY_LOG"

    if [ -f "$BACKUP_DIR/db_backup_${TIMESTAMP}.sql.gz" ]; then
        log "Restoring database from backup..."
        gunzip -c "$BACKUP_DIR/db_backup_${TIMESTAMP}.sql.gz" | \
            docker compose -f "$COMPOSE_FILE" exec -T postgres \
            psql -U agentic agentic_marketplace 2>&1 | tee -a "$DEPLOY_LOG" || \
            warn "Database restore failed"
    fi

    log "Rollback complete. Check logs at $DEPLOY_LOG"
    exit 1
}

# ── Status Report ─────────────────────────────────────────
status() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Agentic Marketplace — Deployment Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""

    docker compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true

    echo ""
    echo -e "${BLUE}  URLs:${NC}"
    echo "  Frontend:    http://localhost:3000"
    echo "  API:         http://localhost:8000/api/v1"
    echo "  API Docs:    http://localhost:8000/api/docs"
    echo "  MinIO:       http://localhost:9001"
    echo "  Nginx:       http://localhost"
    echo ""
    echo -e "${BLUE}  Log file: $DEPLOY_LOG${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

# ── Main ──────────────────────────────────────────────────
main() {
    echo -e "${BLUE}"
    echo "  ╔══════════════════════════════════════════════╗"
    echo "  ║   Agentic Marketplace — Deployment Script    ║"
    echo "  ║   Environment: ${ENV}                        "
    echo "  ╚══════════════════════════════════════════════╝"
    echo -e "${NC}"

    preflight
    backup
    deploy

    if health_check; then
        success "🎉 Deployment successful!"
        status
    else
        rollback
    fi
}

main "$@"
