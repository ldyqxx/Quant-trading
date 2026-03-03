"""
base.py — 策略基類與共用數據結構 / Base Strategy Class and Shared Data Structures

所有策略均需繼承 BaseStrategy 並實現其抽象方法。
All strategies must inherit BaseStrategy and implement its abstract methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Signal:
    """交易信號 / Trading Signal."""

    action: str  # "BUY" | "SELL" | "HOLD"
    symbol: str = ""
    reason: str = ""
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.action not in ("BUY", "SELL", "HOLD"):
            raise ValueError(f"Invalid action: {self.action}. Must be BUY, SELL, or HOLD.")


@dataclass
class BacktestResult:
    """回測結果 / Backtest Result."""

    strategy: str
    total_trades: int
    winning_trades: int
    total_pnl: float
    total_return_pct: float
    win_rate: float
    final_equity: float

    def summary(self) -> str:
        return (
            f"Strategy    : {self.strategy}\n"
            f"Total Trades: {self.total_trades}\n"
            f"Win Rate    : {self.win_rate:.1f}%\n"
            f"Total PnL   : {self.total_pnl:.2f} USDT\n"
            f"Total Return: {self.total_return_pct:.2f}%\n"
            f"Final Equity: {self.final_equity:.2f} USDT\n"
        )


class BaseStrategy(ABC):
    """
    所有量化策略的基類。
    Abstract base class for all quantitative trading strategies.
    """

    name: str = "BaseStrategy"

    @abstractmethod
    def generate_signal(self, data: list[dict[str, Any]]) -> Signal:
        """
        根據市場數據生成交易信號。
        Generate a trading signal from market data.

        Args:
            data: List of OHLCV dicts with keys: time, open, high, low, close, volume

        Returns:
            Signal object with action BUY / SELL / HOLD
        """

    @abstractmethod
    def execute(self, signal: Signal, market: dict[str, Any]) -> dict[str, Any]:
        """
        執行交易訂單。
        Execute a trade order.

        Args:
            signal: Signal from generate_signal()
            market: Current market state (price, balance, etc.)

        Returns:
            Order result dict
        """

    @abstractmethod
    def backtest(self, historical_data: list[dict[str, Any]]) -> BacktestResult:
        """
        對歷史數據執行回測。
        Run a backtest on historical data.

        Args:
            historical_data: List of OHLCV dicts in chronological order

        Returns:
            BacktestResult with performance metrics
        """
