"""
Global pytest configuration and fixtures for BNB Trading System tests.

This file contains shared fixtures and configuration that are used across
all test modules in the testing infrastructure.
"""

import sys

# Add src to Python path for imports
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bnb_trading.core.models import DecisionContext

# ============================================================================
# GLOBAL PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "regression: mark test as a regression test")
    config.addinivalue_line(
        "markers", "benchmark: mark test as a performance benchmark"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add markers based on test path
        if "unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "regression/" in str(item.fspath):
            item.add_marker(pytest.mark.regression)


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================


@pytest.fixture
def test_config():
    """Standard test configuration that matches production config structure."""
    return {
        "signals": {
            "weights": {
                "weekly_tails": 0.60,
                "fibonacci": 0.20,
                "trend": 0.10,
                "moving_avg": 0.10,
                "sentiment": 0.00,
            },
            "thresholds": {"confidence_min": 0.85},
            "critical_modules": ["weekly_tails"],
        },
        "weekly_tails": {
            "lookback_weeks": 8,
            "atr_period": 14,
            "vol_sma_period": 20,
            "min_tail_size": 0.02,
            "strong_tail_size": 0.05,
            "confluence_bonus": 1.5,
            "min_tail_ratio": 0.3,
            "min_tail_strength": 0.35,
            "min_close_pos": 0.2,
            "max_body_atr": 2.0,
        },
        "fibonacci": {
            "swing_lookback": 100,
            "key_levels": [0.382, 0.618],
            "proximity_threshold": 0.03,
            "min_swing_size": 0.15,
        },
        "trend_analysis": {
            "lookback_days": 20,
            "min_consecutive_patterns": 2,
            "weight": 0.10,
            "window_size": 3,
            "score_base": 0.5,
            "score_increment": 0.1,
            "score_max": 0.8,
        },
        "moving_averages": {
            "fast_period": 10,
            "slow_period": 50,
            "volume_confirmation": True,
            "volume_multiplier": 1.5,
            "volume_lookback": 14,
        },
    }


# ============================================================================
# DATA GENERATION FIXTURES
# ============================================================================


@pytest.fixture
def sample_daily_data():
    """Generate deterministic daily OHLCV data for reproducible tests."""
    dates = pd.date_range("2024-01-01", periods=200, freq="D")
    np.random.seed(42)  # Deterministic for reproducibility

    base_price = 500.0
    prices = []

    for i in range(200):
        # Create sideways market with minor fluctuations
        daily_change = np.random.normal(0, 0.01)  # 1% daily volatility
        if i == 0:
            price = base_price
        else:
            price = prices[-1] * (1 + daily_change)
        prices.append(max(price, 1.0))  # Ensure positive prices

    return pd.DataFrame(
        {
            "Open": [p * 0.999 for p in prices],
            "High": [p * 1.005 for p in prices],
            "Low": [p * 0.995 for p in prices],
            "Close": prices,
            "Volume": np.random.uniform(800000, 1200000, 200),
        },
        index=dates,
    )


@pytest.fixture
def sample_weekly_data():
    """Generate deterministic weekly OHLCV data for reproducible tests."""
    dates = pd.date_range("2024-01-01", periods=30, freq="W")
    np.random.seed(42)  # Deterministic for reproducibility

    base_price = 500.0
    prices = []

    for i in range(30):
        # Create weekly patterns with some volatility
        weekly_change = np.random.normal(0, 0.05)  # 5% weekly volatility
        if i == 0:
            price = base_price
        else:
            price = prices[-1] * (1 + weekly_change)
        prices.append(max(price, 1.0))  # Ensure positive prices

    return pd.DataFrame(
        {
            "Open": [p * 0.995 for p in prices],
            "High": [p * 1.02 for p in prices],  # Higher weekly ranges
            "Low": [p * 0.98 for p in prices],
            "Close": prices,
            "Volume": np.random.uniform(4000000, 6000000, 30),
        },
        index=dates,
    )


@pytest.fixture
def bullish_trend_data():
    """Generate bullish trending market data."""
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    np.random.seed(123)  # Different seed for different pattern

    base_price = 400.0
    prices = []

    for i in range(150):
        # Create consistent uptrend with some noise
        trend_component = base_price * (1.001**i)  # 0.1% daily growth
        noise = np.random.normal(0, 0.008)  # 0.8% daily noise
        price = trend_component * (1 + noise)
        prices.append(max(price, 1.0))

    return pd.DataFrame(
        {
            "Open": [p * 0.998 for p in prices],
            "High": [p * 1.008 for p in prices],
            "Low": [p * 0.992 for p in prices],
            "Close": prices,
            "Volume": np.random.uniform(900000, 1300000, 150),
        },
        index=dates,
    )


@pytest.fixture
def bearish_trend_data():
    """Generate bearish trending market data."""
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    np.random.seed(456)  # Different seed for different pattern

    base_price = 600.0
    prices = []

    for i in range(150):
        # Create consistent downtrend with some noise
        trend_component = base_price * (0.9995**i)  # -0.05% daily decline
        noise = np.random.normal(0, 0.012)  # 1.2% daily noise
        price = trend_component * (1 + noise)
        prices.append(max(price, 1.0))

    return pd.DataFrame(
        {
            "Open": [p * 1.002 for p in prices],
            "High": [p * 1.005 for p in prices],
            "Low": [p * 0.985 for p in prices],
            "Close": prices,
            "Volume": np.random.uniform(1100000, 1500000, 150),
        },
        index=dates,
    )


# ============================================================================
# DECISION CONTEXT FIXTURES
# ============================================================================


@pytest.fixture
def sample_decision_context(test_config, sample_daily_data, sample_weekly_data):
    """Create a complete DecisionContext for testing."""
    return DecisionContext(
        closed_daily_df=sample_daily_data,
        closed_weekly_df=sample_weekly_data,
        config=test_config,
        timestamp=sample_daily_data.index[-1],
    )


@pytest.fixture
def bullish_decision_context(test_config, bullish_trend_data, sample_weekly_data):
    """Create DecisionContext with bullish market conditions."""
    return DecisionContext(
        closed_daily_df=bullish_trend_data,
        closed_weekly_df=sample_weekly_data,
        config=test_config,
        timestamp=bullish_trend_data.index[-1],
    )


@pytest.fixture
def bearish_decision_context(test_config, bearish_trend_data, sample_weekly_data):
    """Create DecisionContext with bearish market conditions."""
    return DecisionContext(
        closed_daily_df=bearish_trend_data,
        closed_weekly_df=sample_weekly_data,
        config=test_config,
        timestamp=bearish_trend_data.index[-1],
    )


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary directory for test data files."""
    return tmp_path / "test_data"


@pytest.fixture
def mock_timestamp():
    """Fixed timestamp for deterministic tests."""
    return pd.Timestamp("2024-04-09 12:00:00")


# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================


@pytest.fixture
def performance_threshold():
    """Performance thresholds for benchmark tests."""
    return {
        "decision_time_max": 2.0,  # seconds
        "analysis_time_max": 1.0,  # seconds
        "memory_usage_max": 100,  # MB
    }
