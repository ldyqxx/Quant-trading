#!/usr/bin/env bash
# healthcheck.sh — OpenClaw 健康檢查腳本 / Health Check Script
#
# Usage: ./scripts/healthcheck.sh

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONTAINER_NAME="${OPENCLAW_CONTAINER:-openclaw-quant}"
API_URL="${OPENCLAW_API_URL:-http://localhost:18789}"
HEALTH_ENDPOINT="${API_URL}/health"

log_ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
log_fail() { echo -e "${RED}[✗]${NC} $*"; }
log_info() { echo -e "${BLUE}[i]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $*"; }

FAILED=0

echo ""
echo -e "${BLUE}OpenClaw 健康檢查 / Health Check — $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ──────────────────────────────────────────────
# 1. Check Docker daemon / 檢查 Docker
# ──────────────────────────────────────────────
if docker info &>/dev/null 2>&1; then
    log_ok "Docker daemon is running"
else
    log_fail "Docker daemon is NOT running"
    FAILED=$((FAILED + 1))
fi

# ──────────────────────────────────────────────
# 2. Check container status / 檢查容器狀態
# ──────────────────────────────────────────────
if docker ps --filter "name=${CONTAINER_NAME}" --filter "status=running" --format "{{.Names}}" \
    | grep -q "${CONTAINER_NAME}"; then
    UPTIME=$(docker inspect --format '{{.State.StartedAt}}' "${CONTAINER_NAME}" 2>/dev/null || echo "unknown")
    log_ok "Container '${CONTAINER_NAME}' is running (started: ${UPTIME})"
else
    log_fail "Container '${CONTAINER_NAME}' is NOT running"
    FAILED=$((FAILED + 1))

    # Show last logs if container exists but stopped
    if docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" \
        | grep -q "${CONTAINER_NAME}"; then
        log_info "Last 10 log lines:"
        docker logs --tail 10 "${CONTAINER_NAME}" 2>&1 | sed 's/^/  /'
    fi
fi

# ──────────────────────────────────────────────
# 3. Check API availability / 檢查 API 可用性
# ──────────────────────────────────────────────
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${HEALTH_ENDPOINT}" 2>/dev/null || echo "000")

if [[ "${HTTP_CODE}" == "200" ]]; then
    log_ok "API endpoint ${HEALTH_ENDPOINT} returned HTTP ${HTTP_CODE}"
elif [[ "${HTTP_CODE}" == "000" ]]; then
    log_fail "API endpoint ${HEALTH_ENDPOINT} is unreachable (connection refused)"
    FAILED=$((FAILED + 1))
else
    log_warn "API endpoint ${HEALTH_ENDPOINT} returned HTTP ${HTTP_CODE}"
fi

# ──────────────────────────────────────────────
# 4. Check Docker healthcheck status / 容器健康檢查狀態
# ──────────────────────────────────────────────
HEALTH_STATUS=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' \
    "${CONTAINER_NAME}" 2>/dev/null || echo "container-not-found")

case "${HEALTH_STATUS}" in
    healthy)          log_ok "Docker healthcheck: ${HEALTH_STATUS}" ;;
    no-healthcheck)   log_info "Docker healthcheck: not configured" ;;
    starting)         log_warn "Docker healthcheck: ${HEALTH_STATUS} (still initializing)" ;;
    *)                log_fail "Docker healthcheck: ${HEALTH_STATUS}"; FAILED=$((FAILED + 1)) ;;
esac

# ──────────────────────────────────────────────
# 5. Summary / 摘要
# ──────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ "${FAILED}" -eq 0 ]]; then
    echo -e "${GREEN}✅ 所有檢查通過 / All checks passed${NC}"
    exit 0
else
    echo -e "${RED}❌ ${FAILED} 項檢查失敗 / ${FAILED} check(s) failed${NC}"
    exit 1
fi
