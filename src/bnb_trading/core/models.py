"""Core data models for BNB Trading System."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd

# Module health status types
Status = Literal["OK", "DEGRADED", "DISABLED", "ERROR"]
# Signal state types
SignalState = Literal["LONG", "SHORT", "HOLD", "UP", "DOWN", "NEUTRAL"]


@dataclass
class ModuleResult:
    """Unified result structure for all analysis modules."""

    status: Status  # Module health status
    state: SignalState  # Semantic signal state
    score: float  # 0.0-1.0 raw module strength
    contrib: float  # 0.0-1.0 normalized contribution to final decision
    reason: str  # Human readable explanation
    meta: dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def __post_init__(self) -> None:
        """Enforce business rule: if status != OK, then contrib=0.0 and state=NEUTRAL."""
        if self.status != "OK":
            self.contrib = 0.0
            self.state = "NEUTRAL"


@dataclass
class DecisionContext:
    """Context for unified decision making - no look-ahead"""

    closed_daily_df: pd.DataFrame  # Last 500 closed daily candles
    closed_weekly_df: pd.DataFrame  # Last 100 closed weekly candles
    config: dict[str, Any]  # Configuration from config.toml
    timestamp: pd.Timestamp  # Decision timestamp for MTF sync validation


@dataclass
class DecisionResult:
    """Result from unified decision function"""

    signal: str  # LONG, SHORT, HOLD
    confidence: float  # 0.0 to 1.0
    reasons: list[str]  # List of reasons for decision
    metrics: dict[str, Any]  # Detailed metrics for telemetry
    price_level: float  # Signal price level
    analysis_timestamp: pd.Timestamp  # When analysis was performed


@dataclass
class TestResult:
    """Структура за резултати от тестване"""

    period_name: str
    start_date: str
    end_date: str
    total_signals: int
    long_signals: int
    short_signals: int
    long_accuracy: float
    short_accuracy: float
    overall_accuracy: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    avg_trade_duration: float
    baseline_comparison: dict[str, float] = field(default_factory=dict)


@dataclass
class BaselineMetrics:
    """Базови метрики за сравнение"""

    long_accuracy: float
    short_accuracy: float


@dataclass
class ValidationPoint:
    """Структура за един validation point"""

    name: str
    description: str
    critical: bool  # Ако е True, failure блокира deployment
    validator_func: Callable[..., Any]
    expected_result: Any
    failure_message: str


@dataclass
class ValidationResult:
    """Резултат от цялата validation"""

    feature_name: str
    total_points: int
    passed_points: int
    failed_points: int
    critical_failures: int
    results: dict[str, dict[str, Any]]
    deployment_ready: bool
    summary: str


@dataclass
class ShortSignalCandidate:
    """Кандидат за SHORT сигнал с всички анализи"""

    timestamp: pd.Timestamp
    price: float
    confidence: float
    reasons: list[str]
    confluence_score: int
    risk_reward_ratio: float
    stop_loss_price: float
    take_profit_price: float
    market_regime: str
    ath_distance_pct: float


@dataclass
class Signal:
    """Standard trading signal structure"""

    signal_type: str  # "LONG", "SHORT", "HOLD"
    confidence: float
    price: float
    timestamp: pd.Timestamp
    stop_loss: float = 0.0
    take_profit: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass
class MarketRegime:
    """Market regime classification"""

    regime_type: str  # "STRONG_BULL", "MODERATE_BULL", "NEUTRAL", "BEAR"
    confidence: float
    trend_strength: float
    duration_days: int
    characteristics: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Generic analysis result structure"""

    module_name: str
    signal: str
    confidence: float
    strength: float
    supporting_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
