# 詳細安裝指南 / Detailed Setup Guide

> 本指南適用於在 Linux/macOS 伺服器或 VPS 上部署 OpenClaw 量化交易 Agent。
> This guide covers deploying the OpenClaw Quant Trading Agent on Linux/macOS servers or VPS.

---

## 目錄 / Table of Contents

1. [系統需求](#系統需求)
2. [快速安裝](#快速安裝)
3. [手動安裝](#手動安裝)
4. [VPS 部署建議](#vps-部署建議)
5. [Docker 配置說明](#docker-配置說明)
6. [環境變數說明](#環境變數說明)
7. [常見問題](#常見問題)

---

## 系統需求 / System Requirements

| 項目 | 最低需求 | 建議配置 |
|---|---|---|
| 操作系統 | Ubuntu 20.04 / macOS 12+ | Ubuntu 22.04 LTS |
| CPU | 1 核心 | 2+ 核心 |
| 記憶體 | 1 GB RAM | 2+ GB RAM |
| 儲存空間 | 10 GB | 20+ GB SSD |
| Docker | 20.10+ | 最新版 |
| Docker Compose | 2.0+ | 最新版 |
| 網絡 | 穩定互聯網連接 | 低延遲 VPS |

---

## 快速安裝 / Quick Installation

```bash
# 克隆倉庫
git clone https://github.com/ldyqxx/Quant-trading.git
cd Quant-trading

# 執行一鍵安裝腳本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

---

## 手動安裝 / Manual Installation

### 步驟 1：安裝 Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
下載並安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 步驟 2：建立環境變數文件

```bash
cp .env.example .env
nano .env  # 填入您的 API Keys
```

必填項目：
- `OPENCLAW_API_KEY` — OpenAI 或 Anthropic API Key
- `EXCHANGE_API_KEY` — 交易所 API Key
- `EXCHANGE_API_SECRET` — 交易所 API Secret

### 步驟 3：建立必要目錄

```bash
mkdir -p logs backups
```

### 步驟 4：啟動服務

```bash
docker compose up -d
```

### 步驟 5：確認服務正常

```bash
./scripts/healthcheck.sh
# 或
docker compose ps
docker compose logs openclaw
```

---

## VPS 部署建議 / VPS Deployment Recommendations

### 推薦 VPS 提供商

| 提供商 | 入門規格 | 月費（約）| 適用 |
|---|---|---|---|
| DigitalOcean | 1 vCPU / 1 GB / 25 GB SSD | $6 USD | 測試環境 |
| Vultr | 1 vCPU / 1 GB / 25 GB SSD | $6 USD | 測試環境 |
| Hetzner | 2 vCPU / 2 GB / 40 GB SSD | €4 EUR | 生產環境 |
| AWS EC2 | t3.small | ~$15 USD | 生產環境 |

### 安全強化建議

```bash
# 1. 創建非 root 用戶
adduser quantbot
usermod -aG docker quantbot
su - quantbot

# 2. 設定防火牆，僅允許必要端口
ufw allow 22/tcp    # SSH
ufw allow 443/tcp   # HTTPS（如有反向代理）
ufw deny 18789      # 不對外暴露 OpenClaw 端口
ufw enable

# 3. 設定 SSH Key 認證，禁用密碼登入
# 編輯 /etc/ssh/sshd_config:
# PasswordAuthentication no
# PubkeyAuthentication yes
```

### 使用 systemd 管理服務（可選）

```bash
# /etc/systemd/system/openclaw.service
[Unit]
Description=OpenClaw Quant Trading Agent
After=docker.service
Requires=docker.service

[Service]
User=quantbot
WorkingDirectory=/home/quantbot/Quant-trading
ExecStart=/usr/bin/docker compose up
ExecStop=/usr/bin/docker compose down
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

---

## Docker 配置說明 / Docker Configuration

### 查看服務狀態

```bash
docker compose ps
docker compose logs -f openclaw
docker stats openclaw-quant
```

### 重啟服務

```bash
docker compose restart openclaw
```

### 更新至最新版本

```bash
docker compose pull
docker compose up -d
```

### 停止服務

```bash
docker compose down
```

---

## 環境變數說明 / Environment Variables

| 變數 | 必填 | 說明 | 預設值 |
|---|---|---|---|
| `OPENCLAW_API_KEY` | ✅ | AI 模型 API Key | — |
| `OPENCLAW_MODEL` | ❌ | 使用的模型 | `gpt-4o` |
| `EXCHANGE_API_KEY` | ✅ | 交易所 API Key | — |
| `EXCHANGE_API_SECRET` | ✅ | 交易所 API Secret | — |
| `EXCHANGE_NAME` | ❌ | 交易所名稱 | `binance` |
| `TRADING_MODE` | ❌ | `paper` 或 `live` | `paper` |
| `RISK_LIMIT_PCT` | ❌ | 單筆最大風險 % | `2.0` |
| `MAX_POSITION_SIZE` | ❌ | 最大持倉（USDT）| `1000` |
| `HEARTBEAT_INTERVAL` | ❌ | 心跳間隔（秒）| `60` |
| `LOG_LEVEL` | ❌ | 日誌級別 | `INFO` |

---

## 常見問題 / FAQ

**Q: 服務啟動後無法訪問 http://localhost:18789**
A: 確認容器正在運行：`docker compose ps`。如在 VPS 上，確認已設定 SSH 隧道或反向代理。

**Q: 如何查看實時日誌？**
A: `docker compose logs -f openclaw`

**Q: paper 模式和 live 模式的區別？**
A: `paper` 模式僅模擬交易，不會實際下單。`live` 模式會真實調用交易所 API 進行交易。**強烈建議先在 paper 模式下測試。**

**Q: 如何備份我的配置？**
A: `./scripts/backup.sh`

**Q: 如何更新 OpenClaw 版本？**
A: `docker compose pull && docker compose up -d`
