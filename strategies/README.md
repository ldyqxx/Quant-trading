# 交易策略目錄 / Trading Strategies

本目錄包含用於 OpenClaw 量化交易 Agent 的策略範例。
This directory contains strategy examples for the OpenClaw Quant Trading Agent.

## 策略列表 / Strategy List

| 文件 / File | 策略 / Strategy | 適用市場 / Market |
|---|---|---|
| `momentum.py` | 動量策略（RSI + MACD）| 趨勢市場 |
| `mean_reversion.py` | 均值回歸（布林帶）| 震盪市場 |
| `grid_trading.py` | 網格交易 | 橫盤震盪 |

## 統一接口 / Unified Interface

所有策略繼承自 `BaseStrategy`，實現以下方法：
All strategies inherit from `BaseStrategy` and implement:

- `generate_signal(data)` — 生成交易信號（BUY / SELL / HOLD）
- `execute(signal, market)` — 執行交易訂單
- `backtest(historical_data)` — 回測策略表現

## 開發新策略 / Developing New Strategies

詳見 [策略開發指南](../docs/STRATEGY_GUIDE.md)。
See [Strategy Development Guide](../docs/STRATEGY_GUIDE.md).

## 免責聲明 / Disclaimer

> ⚠️ 策略範例僅供參考，不構成投資建議。請在模擬環境充分測試後再用於實盤。
> ⚠️ Strategy examples are for reference only and do not constitute investment advice. Test thoroughly in paper trading before going live.
