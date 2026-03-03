"""
grid_trading.py — 網格交易策略 / Grid Trading Strategy

在設定的價格區間內均勻布置多個買賣訂單，震盪行情中低買高賣累積利潤。
Places evenly-spaced buy and sell orders within a price range to profit from oscillations.

Usage:
    strategy = GridTradingStrategy(symbol="BTC/USDT", lower=25000, upper=35000, grids=10)
    signal = strategy.generate_signal(ohlcv_data)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .base import BaseStrategy, BacktestResult, Signal


@dataclass
class GridConfig:
    """網格策略配置 / Grid strategy configuration."""

    symbol: str = "BTC/USDT"
    timeframe: str = "15m"

    # 網格設定 / Grid settings
    lower_price: float = 0.0     # 網格下界 / Lower price boundary
    upper_price: float = 0.0     # 網格上界 / Upper price boundary
    grid_count: int = 10         # 網格數量 / Number of grids
    investment_usdt: float = 1000.0  # 總投入資金 / Total investment in USDT

    # 止損保護 / Stop-loss protection
    stop_loss_pct: float = 5.0   # 跌破下界 X% 時強制止損
    auto_reset: bool = False     # 超出邊界時是否自動重設網格
    slippage_tolerance_pct: float = 0.1  # 網格觸發時的滑點容忍百分比

    def __post_init__(self) -> None:
        if self.lower_price > 0 and self.upper_price > 0:
            if self.lower_price >= self.upper_price:
                raise ValueError("lower_price must be less than upper_price")
            if self.grid_count < 2:
                raise ValueError("grid_count must be at least 2")


@dataclass
class GridLevel:
    """單一網格層級 / A single grid level."""

    price: float
    order_size: float        # 每格訂單量（以交易品種計）
    has_buy_order: bool = False
    has_sell_order: bool = False
    filled_buy: bool = False   # 是否已成交買單


class GridTradingStrategy(BaseStrategy):
    """
    網格交易策略 — 在價格區間內等間距布置買賣網格。
    Grid Trading Strategy — places equally spaced buy/sell orders in a price range.

    How it works:
        1. 在 lower_price ~ upper_price 之間，均勻設定 grid_count 個價格節點
        2. 每個節點均掛一個限價買單
        3. 當買單成交後，在上方一格掛賣單
        4. 如此往復，每完成一個來回即鎖定一格利潤
    """

    def __init__(self, config: GridConfig | None = None) -> None:
        self.config = config or GridConfig()
        self.name = "GridTradingStrategy"
        self._grid_levels: list[GridLevel] = []
        self._initialized = False

    # ──────────────────────────────────────────────
    # Public Interface
    # ──────────────────────────────────────────────

    def initialize_grid(self, current_price: float) -> list[GridLevel]:
        """
        初始化網格，根據當前價格設定網格邊界（若未手動指定）。
        Initialize the grid, auto-setting boundaries based on current price if not set.

        Args:
            current_price: Current market price

        Returns:
            List of GridLevel objects
        """
        cfg = self.config

        # 若未設定邊界，以當前價格上下各 10% 作為邊界
        if cfg.lower_price <= 0 or cfg.upper_price <= 0:
            cfg.lower_price = round(current_price * 0.90, 2)
            cfg.upper_price = round(current_price * 1.10, 2)

        step = (cfg.upper_price - cfg.lower_price) / cfg.grid_count
        order_size = round(
            cfg.investment_usdt / cfg.grid_count / current_price, 6
        )

        self._grid_levels = [
            GridLevel(
                price=round(cfg.lower_price + i * step, 2),
                order_size=order_size,
            )
            for i in range(cfg.grid_count + 1)
        ]
        self._initialized = True
        return self._grid_levels

    def generate_signal(self, data: list[dict[str, Any]]) -> Signal:
        """
        根據當前價格判斷網格觸發情況，生成交易信號。
        Check grid triggers against the current price.

        Args:
            data: List of OHLCV dicts (only the latest close price is used)

        Returns:
            Signal: BUY, SELL, or HOLD
        """
        if not data:
            return Signal(action="HOLD", reason="No market data")

        current_price = float(data[-1]["close"])

        if not self._initialized:
            self.initialize_grid(current_price)

        cfg = self.config

        # 超出網格邊界 — 止損或等待
        if current_price < cfg.lower_price * (1 - cfg.stop_loss_pct / 100):
            return Signal(
                action="SELL",
                symbol=cfg.symbol,
                reason=f"Price {current_price:.2f} breached stop-loss "
                       f"({cfg.lower_price * (1 - cfg.stop_loss_pct / 100):.2f})",
                stop_loss_pct=cfg.stop_loss_pct,
                metadata={"grid_lower": cfg.lower_price, "grid_upper": cfg.upper_price},
            )

        if current_price > cfg.upper_price:
            return Signal(
                action="HOLD",
                symbol=cfg.symbol,
                reason=f"Price {current_price:.2f} above grid upper {cfg.upper_price:.2f} — waiting",
                metadata={"grid_lower": cfg.lower_price, "grid_upper": cfg.upper_price},
            )

        # 找到當前價格對應的網格層
        triggered_level = self._find_triggered_level(current_price)
        if triggered_level is None:
            return Signal(action="HOLD", symbol=cfg.symbol, reason="No grid level triggered")

        # 已填充買單的網格層 → 尋找是否需要掛賣單
        if triggered_level.filled_buy:
            sell_level_idx = self._grid_levels.index(triggered_level) + 1
            if sell_level_idx < len(self._grid_levels):
                sell_price = self._grid_levels[sell_level_idx].price
                if current_price >= sell_price:
                    triggered_level.filled_buy = False
                    return Signal(
                        action="SELL",
                        symbol=cfg.symbol,
                        reason=f"Grid SELL at {sell_price:.2f} triggered (price={current_price:.2f})",
                        metadata={"grid_level": sell_price, "order_size": triggered_level.order_size},
                    )

        # 未填充買單的網格層 → 掛買單
        if not triggered_level.filled_buy and current_price <= triggered_level.price:
            triggered_level.filled_buy = True
            return Signal(
                action="BUY",
                symbol=cfg.symbol,
                reason=f"Grid BUY at {triggered_level.price:.2f} triggered (price={current_price:.2f})",
                metadata={"grid_level": triggered_level.price, "order_size": triggered_level.order_size},
            )

        return Signal(action="HOLD", symbol=cfg.symbol, reason="No grid action needed")

    def execute(self, signal: Signal, market: dict[str, Any]) -> dict[str, Any]:
        """
        執行網格訂單。
        Execute a grid order.
        """
        if signal.action == "HOLD":
            return {"status": "skipped", "reason": "HOLD signal"}

        price = float(market.get("price", signal.metadata.get("grid_level", 0)))
        order_size = float(signal.metadata.get("order_size", 0))

        return {
            "status": "submitted",
            "strategy": self.name,
            "action": signal.action,
            "symbol": self.config.symbol,
            "size": order_size,
            "price": price,
            "order_type": "limit",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def backtest(self, historical_data: list[dict[str, Any]]) -> BacktestResult:
        """
        對歷史數據執行網格回測。
        Run grid backtest on historical data.
        """
        if not historical_data:
            return BacktestResult(
                strategy=self.name,
                total_trades=0, winning_trades=0,
                total_pnl=0.0, total_return_pct=0.0,
                win_rate=0.0, final_equity=self.config.investment_usdt,
            )

        # 重置網格狀態
        self._initialized = False
        self._grid_levels = []

        first_price = float(historical_data[0]["close"])
        self.initialize_grid(first_price)

        trades: list[dict[str, Any]] = []
        equity = self.config.investment_usdt
        open_buys: list[tuple[float, float]] = []  # FIFO list of (grid_price, entry_price)

        for bar in historical_data:
            price = float(bar["close"])
            signal = self.generate_signal([bar])

            if signal.action == "BUY":
                grid_price = signal.metadata.get("grid_level", price)
                order_size = signal.metadata.get("order_size", 0)
                cost = price * order_size
                if equity >= cost:
                    equity -= cost
                    open_buys.append((grid_price, price))  # FIFO append

            elif signal.action == "SELL":
                order_size = signal.metadata.get("order_size", 0)
                # Match against the oldest (first-in) buy — FIFO
                if open_buys:
                    _grid_price, entry_price = open_buys.pop(0)
                    pnl = (price - entry_price) * order_size
                    equity += price * order_size
                    trades.append({
                        "entry": entry_price,
                        "exit": price,
                        "size": order_size,
                        "pnl": round(pnl, 2),
                    })

        total_pnl = sum(t["pnl"] for t in trades)
        winning = [t for t in trades if t["pnl"] > 0]

        return BacktestResult(
            strategy=self.name,
            total_trades=len(trades),
            winning_trades=len(winning),
            total_pnl=round(total_pnl, 2),
            total_return_pct=round(total_pnl / self.config.investment_usdt * 100, 2),
            win_rate=round(len(winning) / len(trades) * 100, 2) if trades else 0.0,
            final_equity=round(equity, 2),
        )

    def get_grid_summary(self) -> dict[str, Any]:
        """返回網格概況 / Return grid summary."""
        if not self._initialized:
            return {"status": "not_initialized"}
        return {
            "symbol": self.config.symbol,
            "lower": self.config.lower_price,
            "upper": self.config.upper_price,
            "grid_count": self.config.grid_count,
            "investment_usdt": self.config.investment_usdt,
            "levels": [
                {"price": lvl.price, "filled": lvl.filled_buy}
                for lvl in self._grid_levels
            ],
        }

    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────

    def _find_triggered_level(self, current_price: float) -> GridLevel | None:
        """Find the nearest grid level at or above current price."""
        tolerance = 1 - self.config.slippage_tolerance_pct / 100
        candidates = [
            lvl for lvl in self._grid_levels
            if lvl.price >= current_price * tolerance
        ]
        return min(candidates, key=lambda lvl: lvl.price) if candidates else None
