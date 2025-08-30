"""
Base test classes and common utilities for BNB Trading System tests.

This module provides base classes and utilities that are shared across
different test types to ensure consistency and reduce code duplication.
"""

from typing import Any

import numpy as np
import pandas as pd
import pytest

from bnb_trading.core.models import DecisionContext, ModuleResult


class AnalyzerTestBase:
    """
    Base class for analyzer unit tests.

    Provides common setup, teardown, and assertion methods for all
    analyzer tests. All analyzer test classes should inherit from this.
    """

    @pytest.fixture(autouse=True)
    def setup_analyzer(self, test_config, sample_daily_data, sample_weekly_data):
        """Automatic setup for each analyzer test."""
        self.config = test_config
        self.sample_daily_data = sample_daily_data
        self.sample_weekly_data = sample_weekly_data

        # Common test data variations
        self.minimal_data = sample_daily_data.head(10)  # Insufficient data
        self.sufficient_data = sample_daily_data.head(100)  # Adequate data
        self.full_data = sample_daily_data  # Full dataset

    def assert_valid_module_result(self, result: ModuleResult) -> None:
        """
        Common assertions for ModuleResult validation.

        Validates that a ModuleResult has the correct structure and
        follows the semantic rules established in the core models.
        """
        # Type validation
        assert isinstance(result, ModuleResult), (
            f"Expected ModuleResult, got {type(result)}"
        )

        # Status validation
        assert result.status in ["OK", "DISABLED", "ERROR", "DEGRADED"], (
            f"Invalid status: {result.status}"
        )

        # State validation
        assert result.state in ["LONG", "SHORT", "HOLD", "UP", "DOWN", "NEUTRAL"], (
            f"Invalid state: {result.state}"
        )

        # Score validation
        assert isinstance(result.score, (int, float)), (
            f"Score must be numeric, got {type(result.score)}"
        )
        assert 0.0 <= result.score <= 1.0, (
            f"Score must be between 0.0 and 1.0, got {result.score}"
        )

        # Contribution validation
        assert isinstance(result.contrib, (int, float)), (
            f"Contrib must be numeric, got {type(result.contrib)}"
        )
        assert 0.0 <= result.contrib <= 1.0, (
            f"Contrib must be between 0.0 and 1.0, got {result.contrib}"
        )

        # Semantic rule validation: if status != "OK" → contrib = 0.0, state = "NEUTRAL"
        if result.status != "OK":
            assert result.contrib == 0.0, (
                f"Non-OK status must have contrib=0.0, got {result.contrib}"
            )
            assert result.state == "NEUTRAL", (
                f"Non-OK status must have state=NEUTRAL, got {result.state}"
            )

        # Reason validation
        assert result.reason is not None, "Reason cannot be None"
        assert isinstance(result.reason, str), (
            f"Reason must be string, got {type(result.reason)}"
        )
        assert len(result.reason.strip()) > 0, "Reason cannot be empty"

        # Meta validation
        assert result.meta is not None, "Meta cannot be None"
        assert isinstance(result.meta, dict), (
            f"Meta must be dict, got {type(result.meta)}"
        )

    def assert_analyzer_healthy(self, result: ModuleResult) -> None:
        """Assert that analyzer is in healthy state."""
        assert result.status == "OK", f"Analyzer not healthy: {result.reason}"
        assert result.score > 0.0, "Healthy analyzer should have positive score"
        assert result.contrib > 0.0, (
            "Healthy analyzer should have positive contribution"
        )

    def assert_analyzer_disabled(
        self, result: ModuleResult, expected_reason_keywords: list[str] = None
    ) -> None:
        """Assert that analyzer is properly disabled."""
        assert result.status == "DISABLED", (
            f"Expected DISABLED status, got {result.status}"
        )
        assert result.state == "NEUTRAL", "Disabled analyzer must have NEUTRAL state"
        assert result.score == 0.0, "Disabled analyzer must have zero score"
        assert result.contrib == 0.0, "Disabled analyzer must have zero contribution"

        if expected_reason_keywords:
            for keyword in expected_reason_keywords:
                assert keyword.lower() in result.reason.lower(), (
                    f"Expected '{keyword}' in reason: {result.reason}"
                )


class IntegrationTestBase:
    """
    Base class for integration tests.

    Provides setup and utilities for testing interactions between
    multiple components of the trading system.
    """

    @pytest.fixture(autouse=True)
    def setup_integration(self, test_config):
        """Automatic setup for each integration test."""
        self.config = test_config

        # Store original imports for cleanup
        self._original_modules = {}

    def create_test_decision_context(
        self,
        daily_data: pd.DataFrame = None,
        weekly_data: pd.DataFrame = None,
        config: dict[str, Any] = None,
        timestamp: pd.Timestamp = None,
    ) -> DecisionContext:
        """Create a DecisionContext for integration testing."""
        return DecisionContext(
            closed_daily_df=daily_data or self.sample_daily_data,
            closed_weekly_df=weekly_data or self.sample_weekly_data,
            config=config or self.config,
            timestamp=timestamp or pd.Timestamp.now(),
        )

    def mock_analyzer_result(
        self,
        status: str = "OK",
        state: str = "HOLD",
        score: float = 0.5,
        contrib: float = 0.1,
        reason: str = "Test result",
        meta: dict[str, Any] = None,
    ) -> ModuleResult:
        """Create a mock ModuleResult for testing."""
        return ModuleResult(
            status=status,
            state=state,
            score=score,
            contrib=contrib,
            reason=reason,
            meta=meta or {},
        )


class RegressionTestBase:
    """
    Base class for regression tests.

    Provides utilities for testing that changes don't break existing
    functionality, especially the critical 21/21 LONG signal accuracy.
    """

    def assert_long_signal_preserved(
        self, context: DecisionContext, expected_confidence: float = None
    ) -> None:
        """Assert that a historical LONG signal is preserved."""
        from bnb_trading.signals.decision import decide_long

        result = decide_long(context)

        assert result.signal == "LONG", (
            f"LONG signal lost! Got {result.signal} with confidence {result.confidence:.3f}"
        )

        assert result.confidence >= 0.85, (
            f"LONG confidence below threshold: {result.confidence:.3f} < 0.85"
        )

        if expected_confidence is not None:
            assert abs(result.confidence - expected_confidence) < 0.01, (
                f"LONG confidence changed: expected {expected_confidence:.3f}, got {result.confidence:.3f}"
            )

    def assert_signals_identical(
        self,
        context1: DecisionContext,
        context2: DecisionContext,
        tolerance: float = 0.001,
    ) -> None:
        """Assert that two contexts produce identical signals."""
        from bnb_trading.signals.decision import decide_long

        result1 = decide_long(context1)
        result2 = decide_long(context2)

        assert result1.signal == result2.signal, (
            f"Signal mismatch: {result1.signal} != {result2.signal}"
        )

        assert abs(result1.confidence - result2.confidence) < tolerance, (
            f"Confidence mismatch: {result1.confidence:.6f} != {result2.confidence:.6f}"
        )

    def load_historical_long_signals(self) -> list[dict[str, Any]]:
        """Load historical LONG signal data for regression testing."""
        # Placeholder for loading actual historical data
        # This would load the 21 confirmed LONG signals from a data file
        return [
            {"date": "2024-04-09", "expected_confidence": 0.87},
            {"date": "2024-05-15", "expected_confidence": 0.91},
            # ... would contain all 21 historical LONG signals
        ]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def generate_synthetic_ohlcv(
    start_date: str = "2024-01-01",
    periods: int = 100,
    base_price: float = 500.0,
    volatility: float = 0.02,
    trend_direction: str = "sideways",  # "up", "down", "sideways"
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data for testing.

    Args:
        start_date: Start date for the data
        periods: Number of periods to generate
        base_price: Starting price
        volatility: Daily volatility (standard deviation)
        trend_direction: Overall trend direction
        seed: Random seed for reproducibility

    Returns:
        DataFrame with OHLCV columns and datetime index
    """
    np.random.seed(seed)
    dates = pd.date_range(start_date, periods=periods, freq="D")

    prices = []
    current_price = base_price

    # Trend parameters
    trend_factors = {
        "up": 1.001,  # 0.1% daily growth
        "down": 0.999,  # 0.1% daily decline
        "sideways": 1.0,  # No trend
    }
    trend_factor = trend_factors.get(trend_direction, 1.0)

    for i in range(periods):
        # Apply trend
        current_price *= trend_factor

        # Add random volatility
        daily_change = np.random.normal(0, volatility)
        current_price *= 1 + daily_change

        # Ensure positive prices
        current_price = max(current_price, 1.0)
        prices.append(current_price)

    # Generate OHLC from close prices
    opens = [prices[0], *prices[:-1]]  # Previous close as next open
    highs = [p * np.random.uniform(1.001, 1.01) for p in prices]
    lows = [p * np.random.uniform(0.99, 0.999) for p in prices]

    # Generate realistic volume
    base_volume = 1000000
    volumes = [base_volume * np.random.uniform(0.5, 2.0) for _ in range(periods)]

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


def create_test_config(overrides: dict[str, Any] = None) -> dict[str, Any]:
    """
    Create test configuration with optional overrides.

    Args:
        overrides: Dictionary of config values to override

    Returns:
        Complete test configuration dictionary
    """
    base_config = {
        "signals": {
            "weights": {
                "weekly_tails": 0.60,
                "fibonacci": 0.20,
                "trend": 0.10,
                "moving_avg": 0.10,
            },
            "thresholds": {"confidence_min": 0.85},
            "critical_modules": ["weekly_tails"],
        },
        "weekly_tails": {
            "lookback_weeks": 8,
            "min_tail_strength": 0.35,
        },
        "fibonacci": {
            "swing_lookback": 100,
            "key_levels": [0.382, 0.618],
        },
        "trend_analysis": {
            "lookback_days": 20,
            "weight": 0.10,
        },
        "moving_averages": {
            "fast_period": 10,
            "slow_period": 50,
        },
    }

    if overrides:
        # Deep merge overrides into base config
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if (
                    key in base_dict
                    and isinstance(base_dict[key], dict)
                    and isinstance(value, dict)
                ):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value

        deep_update(base_config, overrides)

    return base_config
