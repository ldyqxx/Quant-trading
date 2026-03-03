#!/usr/bin/env bash
# backup.sh — OpenClaw 備份腳本 / Backup Script
#
# 備份 config、strategies、logs 到 backups/ 目錄，附帶時間戳。
# Backs up config, strategies, and logs to the backups/ directory with a timestamp.
#
# Usage: ./scripts/backup.sh [--no-logs]

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
BACKUP_DIR="${REPO_ROOT}/backups/backup_${TIMESTAMP}"
INCLUDE_LOGS=true

# Parse arguments / 解析參數
for arg in "$@"; do
    case "$arg" in
        --no-logs) INCLUDE_LOGS=false ;;
        *) echo "Unknown argument: $arg" >&2; exit 1 ;;
    esac
done

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }

echo ""
echo -e "${BLUE}OpenClaw 備份 / Backup — ${TIMESTAMP}${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p "${BACKUP_DIR}"
cd "${REPO_ROOT}"

# ──────────────────────────────────────────────
# Backup config/ / 備份配置
# ──────────────────────────────────────────────
if [[ -d "config" ]]; then
    cp -r config "${BACKUP_DIR}/"
    log_success "config/ backed up"
else
    log_warn "config/ directory not found, skipping"
fi

# ──────────────────────────────────────────────
# Backup strategies/ / 備份策略
# ──────────────────────────────────────────────
if [[ -d "strategies" ]]; then
    cp -r strategies "${BACKUP_DIR}/"
    log_success "strategies/ backed up"
else
    log_warn "strategies/ directory not found, skipping"
fi

# ──────────────────────────────────────────────
# Backup skills/ / 備份技能
# ──────────────────────────────────────────────
if [[ -d "skills" ]]; then
    cp -r skills "${BACKUP_DIR}/"
    log_success "skills/ backed up"
else
    log_warn "skills/ directory not found, skipping"
fi

# ──────────────────────────────────────────────
# Backup logs/ (optional) / 備份日誌（可選）
# ──────────────────────────────────────────────
if [[ "${INCLUDE_LOGS}" == "true" ]]; then
    if [[ -d "logs" ]]; then
        cp -r logs "${BACKUP_DIR}/"
        log_success "logs/ backed up"
    else
        log_warn "logs/ directory not found, skipping"
    fi
else
    log_info "Skipping logs/ (--no-logs)"
fi

# ──────────────────────────────────────────────
# Create compressed archive / 建立壓縮包
# ──────────────────────────────────────────────
ARCHIVE="${REPO_ROOT}/backups/backup_${TIMESTAMP}.tar.gz"
tar -czf "${ARCHIVE}" -C "${REPO_ROOT}/backups" "backup_${TIMESTAMP}"
rm -rf "${BACKUP_DIR}"

ARCHIVE_SIZE=$(du -sh "${ARCHIVE}" | awk '{print $1}')
log_success "備份完成 / Backup complete: ${ARCHIVE} (${ARCHIVE_SIZE})"

# ──────────────────────────────────────────────
# Cleanup old backups (keep last 7) / 清理舊備份
# ──────────────────────────────────────────────
KEEP=7
BACKUP_COUNT=$(find "${REPO_ROOT}/backups" -maxdepth 1 -name "backup_*.tar.gz" | wc -l)
if [[ "${BACKUP_COUNT}" -gt "${KEEP}" ]]; then
    log_info "清理舊備份，保留最新 ${KEEP} 份 / Cleaning old backups, keeping last ${KEEP}..."
    find "${REPO_ROOT}/backups" -maxdepth 1 -name "backup_*.tar.gz" \
        | sort | head -n "-${KEEP}" | xargs rm -f
    log_success "舊備份已清理 / Old backups cleaned"
fi

echo ""
