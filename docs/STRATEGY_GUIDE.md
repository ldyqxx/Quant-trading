# 策略開發指南 / Strategy Development Guide

> 本指南說明如何為 OpenClaw 量化交易 Agent 開發自訂交易策略。
> This guide explains how to develop custom trading strategies for the OpenClaw Quant Trading Agent.

---

## 目錄 / Table of Contents

1. [策略架構](#策略架構)
2. [BaseStrategy 介面](#basestrategy-介面)
3. [開發新策略](#開發新策略)
4. [接入 OpenClaw Agent](#接入-openclaw-agent)
5. [回測您的策略](#回測您的策略)
6. [最佳實踐](#最佳實踐)

---

## 策略架構 / Strategy Architecture

所有策略遵循統一的三層架構：
All strategies follow a unified three-layer architecture:

```
OHLCV Data
    │
    ▼
generate_signal()  ──►  Signal (BUY/SELL/HOLD)
                                │
                                ▼
                         execute()  ──►  Order Result
                         
Historical Data
    │
    ▼
backtest()  ──►  BacktestResult
```

---

## BaseStrategy 介面 / BaseStrategy Interface

```python
from strategies.base import BaseStrategy, Signal, BacktestResult

class BaseStrategy(ABC):
    name: str  # 策略名稱

    @abstractmethod
    def generate_signal(self, data: list[dict]) -> Signal:
        """根據 OHLCV 數據生成交易信號"""

    @abstractmethod
    def execute(self, signal: Signal, market: dict) -> dict:
        """執行交易訂單"""

    @abstractmethod
    def backtest(self, historical_data: list[dict]) -> BacktestResult:
        """對歷史數據執行回測"""
```

### Signal 物件 / Signal Object

```python
@dataclass
class Signal:
    action: str          # "BUY" | "SELL" | "HOLD"
    symbol: str = ""     # 交易品種，例如 "BTC/USDT"
    reason: str = ""     # 信號原因說明
    stop_loss_pct: float = 2.0   # 止損百分比
    take_profit_pct: float = 4.0 # 止盈百分比
    metadata: dict = {}  # 額外信息（指標值等）
```

### BacktestResult 物件 / BacktestResult Object

```python
@dataclass
class BacktestResult:
    strategy: str
    total_trades: int       # 總交易次數
    winning_trades: int     # 獲利交易次數
    total_pnl: float        # 總盈虧（USDT）
    total_return_pct: float # 總收益率（%）
    win_rate: float         # 勝率（%）
    final_equity: float     # 最終資金（USDT）
```

---

## 開發新策略 / Developing a New Strategy

### 步驟 1：創建策略文件

在 `strategies/` 目錄下創建新的 Python 文件：

```python
# strategies/my_strategy.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .base import BaseStrategy, Signal, BacktestResult


@dataclass
class MyStrategyConfig:
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    # 添加您的策略參數...
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0


class MyStrategy(BaseStrategy):
    """我的自訂策略 / My Custom Strategy."""

    def __init__(self, config: MyStrategyConfig | None = None) -> None:
        self.config = config or MyStrategyConfig()
        self.name = "MyStrategy"

    def generate_signal(self, data: list[dict[str, Any]]) -> Signal:
        """實現您的信號生成邏輯 / Implement your signal generation logic."""
        if len(data) < 2:
            return Signal(action="HOLD", reason="Insufficient data")

        # 您的指標計算...
        latest_close = float(data[-1]["close"])
        prev_close = float(data[-2]["close"])

        if latest_close > prev_close * 1.02:  # 上漲超過 2%
            return Signal(
                action="BUY",
                symbol=self.config.symbol,
                reason=f"Price increased {(latest_close/prev_close-1)*100:.2f}%",
                stop_loss_pct=self.config.stop_loss_pct,
                take_profit_pct=self.config.take_profit_pct,
            )

        if latest_close < prev_close * 0.98:  # 下跌超過 2%
            return Signal(
                action="SELL",
                symbol=self.config.symbol,
                reason=f"Price decreased {(1-latest_close/prev_close)*100:.2f}%",
                stop_loss_pct=self.config.stop_loss_pct,
                take_profit_pct=self.config.take_profit_pct,
            )

        return Signal(action="HOLD", symbol=self.config.symbol, reason="No signal")

    def execute(self, signal: Signal, market: dict[str, Any]) -> dict[str, Any]:
        """執行訂單 / Execute order."""
        if signal.action == "HOLD":
            return {"status": "skipped"}

        price = float(market.get("price", 0))
        balance = float(market.get("available_balance", 0))
        size = round(balance * 0.1 / price, 6)

        return {
            "status": "submitted",
            "strategy": self.name,
            "action": signal.action,
            "symbol": self.config.symbol,
            "size": size,
            "price": price,
        }

    def backtest(self, historical_data: list[dict[str, Any]]) -> BacktestResult:
        """回測 / Backtest."""
        # 實現您的回測邏輯...
        return BacktestResult(
            strategy=self.name,
            total_trades=0, winning_trades=0,
            total_pnl=0.0, total_return_pct=0.0,
            win_rate=0.0, final_equity=10000.0,
        )
```

### 步驟 2：在 `__init__.py` 中導出

```python
# strategies/__init__.py
from .my_strategy import MyStrategy, MyStrategyConfig
```

### 步驟 3：重啟 OpenClaw 容器

```bash
docker compose restart openclaw
```

---

## 接入 OpenClaw Agent / Integrating with OpenClaw Agent

在 `config/soul.md` 中告知 Agent 您的新策略：

```markdown
## 自訂策略 / Custom Strategies

除了內建策略，您還可以使用以下自訂策略：

- **MyStrategy**: 當價格變動超過 2% 時發出信號。適用於高波動市場。
  使用方式：`策略名稱: MyStrategy, 交易對: BTC/USDT`
```

---

## 回測您的策略 / Backtesting Your Strategy

```python
import json
from strategies.my_strategy import MyStrategy

# 載入歷史數據（格式：OHLCV 列表）
with open("data/btcusdt_1h.json") as f:
    historical_data = json.load(f)

strategy = MyStrategy()
result = strategy.backtest(historical_data)
print(result.summary())
```

**輸出範例：**
```
Strategy    : MyStrategy
Total Trades: 45
Win Rate    : 60.0%
Total PnL   : 1250.50 USDT
Total Return: 12.51%
Final Equity: 11250.50 USDT
```

---

## 最佳實踐 / Best Practices

### ✅ 應該做 / Do

- 在 paper 模式下充分回測後再上線
- 設定合理的止損（`stop_loss_pct`）
- 限制每筆倉位大小
- 記錄所有交易決策的原因（`reason` 字段）
- 添加單元測試驗證信號邏輯

### ❌ 不應該做 / Don't

- 不要過度擬合歷史數據（overfitting）
- 不要在沒有止損的情況下開倉
- 不要在未充分測試前切換到 live 模式
- 不要在單個策略中承擔過高的資金比例
- 不要忽略交易手續費對回測結果的影響

### 風控清單 / Risk Management Checklist

- [ ] 設定每筆交易的最大風險金額
- [ ] 設定總持倉的最大比例
- [ ] 設定每日最大虧損限制
- [ ] 在不同市場環境（牛市/熊市/橫盤）中測試策略
- [ ] 考慮滑點和手續費的影響
