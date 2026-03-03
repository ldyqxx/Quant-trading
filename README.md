# OpenClaw 量化交易 Agent / OpenClaw Quant Trading Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> 基於 [OpenClaw](https://github.com/openclaw/openclaw) 框架的自主量化交易 AI Agent 部署配置。
>
> A production-ready deployment configuration for an autonomous quantitative trading AI Agent built on the [OpenClaw](https://github.com/openclaw/openclaw) framework.

---

## 功能特色 / Features

- 🤖 **自主交易決策** — AI Agent 自動分析市場並執行交易策略
- 📊 **多策略支持** — 內建動量策略、均值回歸、網格交易範例
- 🐳 **Docker 一鍵部署** — 完整的 Docker Compose 配置，分鐘級上線
- 🔒 **風險管控** — 可配置倉位限制、風控規則、止損機制
- 📈 **多交易所支持** — 支持 Binance、OKX、Bybit 等主流交易所
- 📝 **完整日誌** — 持倉、PnL、風險指標定期報告

---

## 快速開始 / Quick Start

### 系統需求 / Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- Git

### 安裝步驟 / Installation

```bash
# 1. 克隆倉庫 / Clone the repository
git clone https://github.com/ldyqxx/Quant-trading.git
cd Quant-trading

# 2. 執行一鍵安裝腳本 / Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. 填入您的 API Keys（腳本會引導您）/ Fill in your API Keys (the script will guide you)
# 編輯 .env 文件 / Edit .env file
nano .env

# 4. 啟動服務 / Start the service
docker compose up -d

# 5. 確認服務正常 / Verify the service is running
./scripts/healthcheck.sh
```

服務啟動後，OpenClaw Agent 將在 `http://localhost:18789` 提供服務。

After startup, the OpenClaw Agent will be available at `http://localhost:18789`.

---

## 目錄結構 / Directory Structure

```
Quant-trading/
├── README.md                  # 本文件 / This file
├── docker-compose.yml         # Docker Compose 配置
├── .env.example               # 環境變數範例
├── .gitignore                 # Git 忽略規則
├── config/
│   └── soul.md                # Agent 人格與行為定義
├── skills/
│   └── README.md              # 自訂技能說明
├── strategies/
│   ├── README.md              # 策略說明
│   ├── momentum.py            # 動量策略
│   ├── mean_reversion.py      # 均值回歸策略
│   └── grid_trading.py        # 網格交易策略
├── scripts/
│   ├── setup.sh               # 一鍵安裝腳本
│   ├── healthcheck.sh         # 健康檢查腳本
│   └── backup.sh              # 備份腳本
└── docs/
    ├── SETUP_GUIDE.md         # 詳細安裝指南
    ├── STRATEGY_GUIDE.md      # 策略開發指南
    └── SECURITY.md            # 安全注意事項
```

---

## 技術架構 / Architecture

```
┌─────────────────────────────────────────────────────┐
│                   OpenClaw Agent                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Soul / 人格 │  │  Skills / 技能│  │ Strategies │  │
│  │  (soul.md)  │  │  (skills/)   │  │ (strategies│  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘  │
│         └────────────────┴────────────────┘         │
│                          │                           │
│              ┌───────────▼───────────┐               │
│              │    AI Model (LLM)     │               │
│              │  GPT-4o / Claude etc  │               │
│              └───────────┬───────────┘               │
└──────────────────────────┼──────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   Exchange API          │
              │  Binance / OKX / Bybit  │
              └─────────────────────────┘
```

---

## 策略說明 / Strategy Overview

| 策略 / Strategy | 文件 / File | 說明 / Description |
|---|---|---|
| 動量策略 | `strategies/momentum.py` | 基於 RSI + MACD 的趨勢跟蹤 |
| 均值回歸 | `strategies/mean_reversion.py` | 基於布林帶的震盪交易 |
| 網格交易 | `strategies/grid_trading.py` | 區間震盪的網格套利 |

詳見 [策略開發指南](docs/STRATEGY_GUIDE.md)。

---

## 詳細文檔 / Documentation

- 📖 [詳細安裝指南](docs/SETUP_GUIDE.md)
- 📊 [策略開發指南](docs/STRATEGY_GUIDE.md)
- 🔒 [安全注意事項](docs/SECURITY.md)

---

## 貢獻指南 / Contributing

歡迎提交 Pull Request 或開 Issue 討論新功能。
Contributions, issues and feature requests are welcome!

1. Fork 本倉庫
2. 創建功能分支 (`git checkout -b feature/my-strategy`)
3. 提交更改 (`git commit -m 'Add my strategy'`)
4. 推送到分支 (`git push origin feature/my-strategy`)
5. 開啟 Pull Request

---

## 授權聲明 / License

本項目採用 [MIT License](https://opensource.org/licenses/MIT) 授權。

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## 免責聲明 / Disclaimer

> ⚠️ **重要**：本項目僅供教育和研究目的。量化交易涉及重大財務風險。在實盤交易前，請充分測試您的策略並了解相關風險。作者不對任何交易損失承擔責任。
>
> ⚠️ **Important**: This project is for educational and research purposes only. Quantitative trading involves significant financial risk. Always thoroughly test your strategies before live trading. The authors are not responsible for any trading losses.
