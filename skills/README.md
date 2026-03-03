# Skills（技能）目錄說明 / Skills Directory

本目錄用於存放 OpenClaw Agent 的自訂技能（Skills）。
This directory is for custom OpenClaw Agent skills.

## 什麼是 Skill？/ What is a Skill?

Skill 是一個可被 Agent 調用的功能模塊，可以是：
A Skill is a callable module that can:

- 調用外部 API（如天氣、新聞、鏈上數據）
- 執行計算（如技術指標計算）
- 觸發自動化流程（如發送通知）
- 查詢數據庫或文件

## 如何新增 Skill / How to Add a Skill

1. 在本目錄下創建一個新的 `.md` 或 `.yaml` 文件
2. 遵循 OpenClaw 官方的 Skill 格式定義
3. 重啟 OpenClaw 容器使技能生效：
   ```bash
   docker compose restart openclaw
   ```

## 範例 Skill 結構 / Example Skill Structure

```yaml
name: get_market_data
description: Fetch real-time market data for a given trading pair
parameters:
  symbol:
    type: string
    description: Trading pair, e.g. BTC/USDT
  timeframe:
    type: string
    description: Candlestick timeframe, e.g. 1h, 4h, 1d
    default: "1h"
endpoint: https://api.exchange.com/v1/klines
method: GET
```

## 參考資源 / References

- [OpenClaw 官方文檔](https://docs.openclaw.ai/skills)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
