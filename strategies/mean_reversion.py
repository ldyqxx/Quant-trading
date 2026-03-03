"""
mean_reversion.py — 均值回歸策略 / Mean Reversion Strategy

基於布林帶（Bollinger Bands）的均值回歸策略。
Mean reversion strategy using Bollinger Bands.

Usage:
    strategy = MeanReversionStrategy(symbol="ETH/USDT")
    signal = strategy.generate_signal(ohlcv_data)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .base import BaseStrategy, BacktestResult, Signal


@dataclass
class MeanReversionConfig:
    """均值回歸策略配置 / Mean Reversion strategy configuration."""

    symbol: str = "BTC/USDT"
    timeframe: str = "4h"

    # 布林帶設定 / Bollinger Bands settings
    bb_period: int = 20          # 移動平均週期 / MA period
    bb_std_dev: float = 2.0      # 標準差倍數 / Std deviation multiplier

    # 進出場確認 / Entry/exit confirmation
    min_band_width_pct: float = 1.0   # 最小帶寬百分比，避免橫盤假信號
    close_at_middle: bool = True      # 在中軌平倉 / Close at middle band

    # 風控設定 / Risk settings
    stop_loss_pct: float = 1.5
    take_profit_pct: float = 3.0


class MeanReversionStrategy(BaseStrategy):
    """
    均值回歸策略 — 使用布林帶識別超買超賣後逆勢交易。
    Mean Reversion Strategy — trades against extremes using Bollinger Bands.

    Entry conditions:
        BUY  : Price closes below lower band (oversold)
        SELL : Price closes above upper band (overbought)
        HOLD : Price within bands or band width too narrow
    """

    def __init__(self, config: MeanReversionConfig | None = None) -> None:
        self.config = config or MeanReversionConfig()
        self.name = "MeanReversionStrategy"

    # ──────────────────────────────────────────────
    # Public Interface
    # ──────────────────────────────────────────────

    def generate_signal(self, data: list[dict[str, Any]]) -> Signal:
        """
        根據最新 OHLCV 數據生成交易信號。
        Generate a trading signal from the latest OHLCV data.
        """
        period = self.config.bb_period
        if len(data) < period:
            return Signal(action="HOLD", reason="Insufficient data for Bollinger Bands")

        closes = [float(c["close"]) for c in data]
        upper, middle, lower = self._calc_bollinger_bands(
            closes, period, self.config.bb_std_dev
        )

        latest_close = closes[-1]
        u, m, l = upper[-1], middle[-1], lower[-1]
        band_width_pct = (u - l) / m * 100 if m != 0 else 0.0

        # 帶寬過窄時跳過信號（橫盤整理）
        if band_width_pct < self.config.min_band_width_pct:
            return Signal(
                action="HOLD",
                symbol=self.config.symbol,
                reason=f"Band width {band_width_pct:.2f}% too narrow — sideways market",
                metadata={"upper": u, "middle": m, "lower": l, "close": latest_close},
            )

        # BUY: 收盤價跌破下軌
        if latest_close < l:
            return Signal(
                action="BUY",
                symbol=self.config.symbol,
                reason=f"Close {latest_close:.2f} < lower band {l:.2f} (oversold)",
                stop_loss_pct=self.config.stop_loss_pct,
                take_profit_pct=self.config.take_profit_pct,
                metadata={"upper": u, "middle": m, "lower": l, "band_width_pct": band_width_pct},
            )

        # SELL: 收盤價突破上軌
        if latest_close > u:
            return Signal(
                action="SELL",
                symbol=self.config.symbol,
                reason=f"Close {latest_close:.2f} > upper band {u:.2f} (overbought)",
                stop_loss_pct=self.config.stop_loss_pct,
                take_profit_pct=self.config.take_profit_pct,
                metadata={"upper": u, "middle": m, "lower": l, "band_width_pct": band_width_pct},
            )

        return Signal(
            action="HOLD",
            symbol=self.config.symbol,
            reason=f"Close {latest_close:.2f} within bands [{l:.2f}, {u:.2f}]",
            metadata={"upper": u, "middle": m, "lower": l},
        )

    def execute(self, signal: Signal, market: dict[str, Any]) -> dict[str, Any]:
        """
        執行交易訂單。
        Execute a trade order.
        """
        if signal.action == "HOLD":
            return {"status": "skipped", "reason": "HOLD signal"}

        price = float(market.get("price", 0))
        balance = float(market.get("available_balance", 0))
        risk_amount = balance * (signal.stop_loss_pct / 100)
        # Risk-based sizing: lose at most risk_amount if stop is hit
        size = round(risk_amount / (price * (signal.stop_loss_pct / 100)), 6)

        return {
            "status": "submitted",
            "strategy": self.name,
            "action": signal.action,
            "symbol": self.config.symbol,
            "size": size,
            "price": price,
            "stop_loss": price * (1 - signal.stop_loss_pct / 100) if signal.action == "BUY"
                         else price * (1 + signal.stop_loss_pct / 100),
            "take_profit": price * (1 + signal.take_profit_pct / 100) if signal.action == "BUY"
                           else price * (1 - signal.take_profit_pct / 100),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def backtest(self, historical_data: list[dict[str, Any]]) -> BacktestResult:
        """
        對歷史數據執行回測。
        Run backtest on historical data.
        """
        trades: list[dict[str, Any]] = []
        position: dict[str, Any] | None = None
        equity = 10_000.0

        period = self.config.bb_period

        for i in range(period, len(historical_data)):
            window = historical_data[: i + 1]
            signal = self.generate_signal(window)
            price = float(historical_data[i]["close"])

            if signal.action == "BUY" and position is None:
                size = equity * 0.95 / price
                position = {"entry_price": price, "size": size, "side": "BUY"}

            elif position is not None:
                closes = [float(c["close"]) for c in window]
                _, middle, _ = self._calc_bollinger_bands(
                    closes, period, self.config.bb_std_dev
                )
                at_middle = price >= middle[-1] if position["side"] == "BUY" else price <= middle[-1]

                should_exit = (
                    (self.config.close_at_middle and at_middle)
                    or signal.action == "SELL"
                )
                if should_exit:
                    pnl = (price - position["entry_price"]) * position["size"]
                    equity += pnl
                    trades.append({
                        "entry": position["entry_price"],
                        "exit": price,
                        "pnl": round(pnl, 2),
                        "pnl_pct": round((price / position["entry_price"] - 1) * 100, 2),
                    })
                    position = None

        total_pnl = sum(t["pnl"] for t in trades)
        winning = [t for t in trades if t["pnl"] > 0]
        return BacktestResult(
            strategy=self.name,
            total_trades=len(trades),
            winning_trades=len(winning),
            total_pnl=round(total_pnl, 2),
            total_return_pct=round((equity / 10_000.0 - 1) * 100, 2),
            win_rate=round(len(winning) / len(trades) * 100, 2) if trades else 0.0,
            final_equity=round(equity, 2),
        )

    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def _calc_bollinger_bands(
        closes: list[float],
        period: int,
        std_multiplier: float,
    ) -> tuple[list[float], list[float], list[float]]:
        """Calculate Bollinger Bands (upper, middle, lower)."""
        upper_band: list[float] = []
        middle_band: list[float] = []
        lower_band: list[float] = []

        for i in range(len(closes)):
            if i < period - 1:
                upper_band.append(float("nan"))
                middle_band.append(float("nan"))
                lower_band.append(float("nan"))
                continue

            window = closes[i - period + 1 : i + 1]
            mean = sum(window) / period
            variance = sum((x - mean) ** 2 for x in window) / period
            std = math.sqrt(variance)

            upper_band.append(mean + std_multiplier * std)
            middle_band.append(mean)
            lower_band.append(mean - std_multiplier * std)

        return upper_band, middle_band, lower_band
