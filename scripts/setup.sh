#!/usr/bin/env bash
# setup.sh — OpenClaw 量化交易 Agent 一鍵安裝腳本
# One-click setup script for the OpenClaw Quant Trading Agent
#
# Usage: ./scripts/setup.sh

set -euo pipefail

# ──────────────────────────────────────────────
# Colors
# ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ──────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   OpenClaw 量化交易 Agent 安裝程序         ║${NC}"
echo -e "${BLUE}║   OpenClaw Quant Trading Agent Setup      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ──────────────────────────────────────────────
# 1. Check dependencies / 檢查依賴
# ──────────────────────────────────────────────
log_info "檢查系統依賴 / Checking system dependencies..."

if ! command -v docker &>/dev/null; then
    log_error "Docker 未安裝。請先安裝 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
log_success "Docker $(docker --version | awk '{print $3}' | tr -d ',')"

# Check Docker Compose (v2 plugin or standalone v1)
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    log_success "Docker Compose $(docker compose version --short)"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
    log_success "docker-compose $(docker-compose --version | awk '{print $3}' | tr -d ',')"
else
    log_error "Docker Compose 未安裝。請先安裝: https://docs.docker.com/compose/install/"
    exit 1
fi

# ──────────────────────────────────────────────
# 2. Create .env from .env.example / 建立 .env
# ──────────────────────────────────────────────
cd "$REPO_ROOT"

if [[ -f ".env" ]]; then
    log_warn ".env 文件已存在，跳過複製 / .env already exists, skipping copy"
else
    cp .env.example .env
    log_success ".env 文件已從 .env.example 建立 / .env created from .env.example"
fi

# ──────────────────────────────────────────────
# 3. Prompt user to fill in API keys / 提示填入 API Keys
# ──────────────────────────────────────────────
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}  請填入您的 API Keys / Please fill in your API Keys${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""
echo "  編輯 .env 文件並填入以下密鑰 / Edit .env and fill in:"
echo "    • OPENCLAW_API_KEY  — OpenAI / Anthropic API Key"
echo "    • EXCHANGE_API_KEY  — 交易所 API Key"
echo "    • EXCHANGE_API_SECRET — 交易所 API Secret"
echo ""

read -r -p "  是否現在開啟 .env 進行編輯？(y/N) / Open .env for editing now? (y/N): " EDIT_NOW
if [[ "${EDIT_NOW,,}" == "y" ]]; then
    "${EDITOR:-nano}" .env
fi

# ──────────────────────────────────────────────
# 4. Create required directories / 建立必要目錄
# ──────────────────────────────────────────────
log_info "建立必要目錄 / Creating required directories..."
mkdir -p logs backups
log_success "logs/ 和 backups/ 目錄已建立"

# ──────────────────────────────────────────────
# 5. Pull Docker image / 拉取映像
# ──────────────────────────────────────────────
log_info "拉取 OpenClaw Docker 映像 / Pulling OpenClaw Docker image..."
docker pull openclaw/openclaw:latest || {
    log_warn "無法拉取映像，請確認網絡連接 / Could not pull image, check network"
}

# ──────────────────────────────────────────────
# 6. Start services / 啟動服務
# ──────────────────────────────────────────────
echo ""
read -r -p "  是否現在啟動服務？(Y/n) / Start services now? (Y/n): " START_NOW
if [[ "${START_NOW,,}" != "n" ]]; then
    log_info "啟動 OpenClaw 服務 / Starting OpenClaw service..."
    $COMPOSE_CMD up -d
    log_success "服務已啟動 / Service started"
    echo ""
    log_info "服務地址 / Service URL: http://localhost:18789"
    log_info "查看日誌 / View logs: docker compose logs -f openclaw"
    log_info "健康檢查 / Health check: ./scripts/healthcheck.sh"
else
    echo ""
    log_info "稍後可執行以下命令啟動 / Start later with:"
    echo "  $COMPOSE_CMD up -d"
fi

echo ""
log_success "安裝完成！/ Setup complete!"
echo ""
