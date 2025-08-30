"""
Mock object factories for BNB Trading System tests.

This module provides factory functions for creating mock objects
that are commonly used across different test types.
"""

from typing import Any

import numpy as np
import pandas as pd

from bnb_trading.core.models import DecisionContext, DecisionResult, ModuleResult


class MockAnalyzer:
    """Mock analyzer that can be configured to return specific ModuleResults."""

    def __init__(self, name: str = "mock_analyzer"):
        self.name = name
        self.analyze_return_value = None
        self.analyze_side_effect = None
        self.call_count = 0
        self.call_history = []

    def configure_result(
        self,
        status: str = "OK",
        state: str = "NEUTRAL",
        score: float = 0.5,
        contrib: float = 0.1,
        reason: str = "Mock result",
        meta: dict[str, Any] | None = None,
    ) -> "MockAnalyzer":
        """Configure the result that analyze() will return."""
        self.analyze_return_value = ModuleResult(
            status=status,
            state=state,
            score=score,
            contrib=contrib,
            reason=reason,
            meta=meta or {},
        )
        return self

    def configure_side_effect(self, side_effect) -> "MockAnalyzer":
        """Configure a side effect (like raising an exception)."""
        self.analyze_side_effect = side_effect
        return self

    def analyze(self, *args, **kwargs) -> ModuleResult:
        """Mock analyze method that tracks calls and returns configured result."""
        self.call_count += 1
        self.call_history.append({"args": args, "kwargs": kwargs})

        if self.analyze_side_effect is not None:
            if callable(self.analyze_side_effect):
                return self.analyze_side_effect(*args, **kwargs)
            raise self.analyze_side_effect

        return self.analyze_return_value or ModuleResult(
            status="OK",
            state="NEUTRAL",
            score=0.5,
            contrib=0.1,
            reason=f"Default mock result from {self.name}",
            meta={},
        )


class MockBinanceAPI:
    """Mock Binance API responses for data fetcher tests."""

    @staticmethod
    def create_ohlcv_response(
        symbol: str = "BNB/USDT",
        timeframe: str = "1d",
        periods: int = 100,
        base_price: float = 500.0,
    ) -> dict[str, Any]:
        """Create realistic OHLCV API response."""
        np.random.seed(42)  # Deterministic

        ohlcv_data = []
        current_time = pd.Timestamp.now().timestamp() * 1000  # Milliseconds

        for i in range(periods):
            # Generate timestamp (going backwards in time)
            timestamp = current_time - (periods - i) * 24 * 60 * 60 * 1000

            # Generate OHLCV
            price = base_price * (1 + np.random.normal(0, 0.01))
            open_price = price * np.random.uniform(0.999, 1.001)
            high_price = max(price, open_price) * np.random.uniform(1.001, 1.01)
            low_price = min(price, open_price) * np.random.uniform(0.99, 0.999)
            volume = np.random.uniform(800000, 1200000)

            ohlcv_data.append(
                [timestamp, open_price, high_price, low_price, price, volume]
            )

        return {
            "symbol": symbol,
            "data": ohlcv_data,
            "timeframe": timeframe,
            "response_time": pd.Timestamp.now().isoformat(),
        }

    @staticmethod
    def create_error_response(
        error_code: int = 500, error_msg: str = "API Error"
    ) -> dict[str, Any]:
        """Create error API response for testing error handling."""
        return {
            "error": True,
            "code": error_code,
            "message": error_msg,
            "timestamp": pd.Timestamp.now().isoformat(),
        }


def create_mock_module_result(
    status: str = "OK",
    state: str = "NEUTRAL",
    score: float = 0.5,
    contrib: float = 0.1,
    reason: str = "Mock result",
    meta: dict[str, Any] | None = None,
) -> ModuleResult:
    """Factory function to create ModuleResult objects for testing."""
    return ModuleResult(
        status=status,
        state=state,
        score=score,
        contrib=contrib,
        reason=reason,
        meta=meta or {},
    )


def create_mock_decision_result(
    signal: str = "HOLD",
    confidence: float = 0.5,
    reasons: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
    price_level: float = 500.0,
    analysis_timestamp: pd.Timestamp | None = None,
) -> DecisionResult:
    """Factory function to create DecisionResult objects for testing."""
    return DecisionResult(
        signal=signal,
        confidence=confidence,
        reasons=reasons or ["Mock decision reason"],
        metrics=metrics or {"mock": True},
        price_level=price_level,
        analysis_timestamp=analysis_timestamp or pd.Timestamp.now(),
    )


def create_mock_decision_context(
    daily_data: pd.DataFrame | None = None,
    weekly_data: pd.DataFrame | None = None,
    config: dict[str, Any] | None = None,
    timestamp: pd.Timestamp | None = None,
) -> DecisionContext:
    """Factory function to create DecisionContext objects for testing."""
    if daily_data is None:
        # Create minimal daily data
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        daily_data = pd.DataFrame(
            {
                "Open": np.random.uniform(490, 510, 100),
                "High": np.random.uniform(505, 520, 100),
                "Low": np.random.uniform(480, 495, 100),
                "Close": np.random.uniform(495, 515, 100),
                "Volume": np.random.uniform(800000, 1200000, 100),
            },
            index=dates,
        )

    if weekly_data is None:
        # Create minimal weekly data
        dates = pd.date_range("2024-01-01", periods=20, freq="W")
        weekly_data = pd.DataFrame(
            {
                "Open": np.random.uniform(490, 510, 20),
                "High": np.random.uniform(510, 530, 20),
                "Low": np.random.uniform(470, 490, 20),
                "Close": np.random.uniform(495, 515, 20),
                "Volume": np.random.uniform(4000000, 6000000, 20),
            },
            index=dates,
        )

    if config is None:
        config = {
            "signals": {
                "weights": {
                    "weekly_tails": 0.6,
                    "fibonacci": 0.2,
                    "trend": 0.1,
                    "moving_avg": 0.1,
                },
                "thresholds": {"confidence_min": 0.85},
                "critical_modules": ["weekly_tails"],
            }
        }

    return DecisionContext(
        closed_daily_df=daily_data,
        closed_weekly_df=weekly_data,
        config=config,
        timestamp=timestamp or daily_data.index[-1],
    )


class MockAnalyzerPatch:
    """Context manager for patching analyzers in tests."""

    def __init__(self, analyzer_path: str, mock_analyzer: MockAnalyzer):
        self.analyzer_path = analyzer_path
        self.mock_analyzer = mock_analyzer
        self.patcher = None

    def __enter__(self):
        from unittest.mock import patch

        self.patcher = patch(self.analyzer_path, return_value=self.mock_analyzer)
        return self.patcher.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.patcher:
            return self.patcher.__exit__(exc_type, exc_val, exc_tb)
        return None


def patch_analyzer(
    analyzer_path: str,
    status: str = "OK",
    state: str = "NEUTRAL",
    score: float = 0.5,
    contrib: float = 0.1,
    reason: str = "Mock result",
) -> MockAnalyzerPatch:
    """
    Convenience function to patch an analyzer with a mock.

    Usage:
        with patch_analyzer("bnb_trading.fibonacci.FibonacciAnalyzer",
                          state="HOLD", score=0.7, contrib=0.14):
            # Test code here
            pass
    """
    mock_analyzer = MockAnalyzer().configure_result(
        status=status, state=state, score=score, contrib=contrib, reason=reason
    )
    return MockAnalyzerPatch(analyzer_path, mock_analyzer)


def create_realistic_market_data(
    periods: int = 200,
    market_condition: str = "sideways",  # "bullish", "bearish", "sideways", "volatile"
    base_price: float = 500.0,
    seed: int = 42,
) -> pd.DataFrame:
    """Create realistic market data for different market conditions."""
    np.random.seed(seed)
    dates = pd.date_range("2024-01-01", periods=periods, freq="D")

    prices = []
    current_price = base_price

    # Market condition parameters
    conditions = {
        "bullish": {"trend": 1.001, "volatility": 0.015},
        "bearish": {"trend": 0.999, "volatility": 0.018},
        "sideways": {"trend": 1.0, "volatility": 0.012},
        "volatile": {"trend": 1.0, "volatility": 0.035},
    }

    params = conditions.get(market_condition, conditions["sideways"])
    trend_factor = params["trend"]
    volatility = params["volatility"]

    for i in range(periods):
        # Apply trend
        current_price *= trend_factor

        # Add volatility
        daily_change = np.random.normal(0, volatility)
        current_price *= 1 + daily_change

        # Add some mean reversion to keep prices reasonable
        if current_price > base_price * 2:
            current_price *= 0.98
        elif current_price < base_price * 0.5:
            current_price *= 1.02

        prices.append(max(current_price, 1.0))

    # Generate realistic OHLC
    opens = [prices[0], *prices[:-1]]
    highs = []
    lows = []

    for i, close in enumerate(prices):
        open_price = opens[i]

        # Realistic intraday range
        daily_range = abs(close - open_price) * np.random.uniform(1.5, 3.0)
        mid_price = (close + open_price) / 2

        high = mid_price + daily_range / 2
        low = mid_price - daily_range / 2

        # Ensure OHLC relationships are valid
        high = max(high, open_price, close)
        low = min(low, open_price, close)

        highs.append(high)
        lows.append(low)

    # Generate volume with some correlation to price movement
    volumes = []
    for i in range(periods):
        base_vol = 1000000

        if i > 0:
            price_change = abs(prices[i] - prices[i - 1]) / prices[i - 1]
            volume_multiplier = 1 + price_change * 5  # Higher volume on big moves
        else:
            volume_multiplier = 1

        volume = base_vol * volume_multiplier * np.random.uniform(0.5, 2.0)
        volumes.append(volume)

    return pd.DataFrame(
        {
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": prices,
            "Volume": volumes,
        },
        index=dates,
    )
