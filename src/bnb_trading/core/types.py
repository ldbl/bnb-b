"""Type definitions for BNB Trading System."""

from typing import Any, Literal, Protocol, TypedDict

import pandas as pd

# Signal Types
SignalType = Literal["LONG", "SHORT", "HOLD"]
MarketRegimeType = Literal["STRONG_BULL", "MODERATE_BULL", "NEUTRAL", "BEAR"]


class SignalResult(TypedDict):
    """Standard trading signal result structure."""

    signal: SignalType
    confidence: float
    price: float
    timestamp: pd.Timestamp
    reasons: list[str]
    analyses: dict[str, Any]
    metadata: dict[str, Any]


class SimpleSignal(TypedDict):
    """Simple signal for basic use cases."""

    signal: SignalType
    confidence: float
    price: float
    timestamp: pd.Timestamp
    reason: str
    stop_loss: float
    take_profit: float


class AnalysisData(TypedDict):
    """Analysis result from individual modules."""

    signal: SignalType
    strength: float
    confidence: float
    data: dict[str, Any]
    metadata: dict[str, Any]


class FibonacciAnalysis(TypedDict):
    """Fibonacci analysis result."""

    current_price: float
    fibonacci_levels: dict[str, float]
    proximity_analysis: dict[str, Any]
    signal: SignalType
    strength: float
    confluence_zones: list[dict[str, Any]]


class WeeklyTailsAnalysis(TypedDict):
    """Weekly tails analysis result."""

    signal: SignalType
    strength: float
    tail_type: str
    tail_length_pct: float
    volume_confirmation: bool
    confluence_bonus: float


class TechnicalIndicators(TypedDict):
    """Technical indicators analysis."""

    rsi: dict[str, Any]
    macd: dict[str, Any]
    bollinger: dict[str, Any]
    volume: dict[str, Any]
    combined_signal: SignalType


class MarketData(TypedDict):
    """Market data structure."""

    daily: pd.DataFrame
    weekly: pd.DataFrame
    symbol: str
    last_update: pd.Timestamp


class BacktestResult(TypedDict):
    """Backtest execution result."""

    total_signals: int
    successful_signals: int
    overall_accuracy: float
    long_accuracy: float
    short_accuracy: float
    avg_profit_loss_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float


class ValidationMetrics(TypedDict):
    """Validation metrics structure."""

    passed: int
    failed: int
    critical_failures: int
    deployment_ready: bool
    details: dict[str, Any]


# Protocol interfaces
class DataProvider(Protocol):
    """Protocol for data providers."""

    def fetch_data(self, lookback_days: int) -> MarketData:
        """Fetch market data."""
        ...


class AnalysisModule(Protocol):
    """Protocol for analysis modules."""

    def analyze(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> AnalysisData:
        """Perform analysis and return results."""
        ...


class SignalGenerator(Protocol):
    """Protocol for signal generators."""

    def generate_signal(
        self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame
    ) -> SignalResult:
        """Generate trading signal."""
        ...


# Configuration types
class DataConfig(TypedDict):
    """Data configuration section."""

    symbol: str
    lookback_days: int
    timeframes: list[str]


class SignalsConfig(TypedDict):
    """Signals configuration section."""

    fibonacci_weight: float
    weekly_tails_weight: float
    ma_weight: float
    rsi_weight: float
    macd_weight: float
    bb_weight: float
    confidence_threshold: float


class SystemConfig(TypedDict):
    """Complete system configuration."""

    data: DataConfig
    signals: SignalsConfig
    # Other config sections can be added as needed
