"""
Minimal test fixtures for KISS testing strategy.
Simple, predictable test data without complex abstractions.
"""

import pandas as pd
import pytest


@pytest.fixture
def test_config():
    """Minimal test configuration with essential parameters."""
    return {
        "signals": {
            "weights": {
                "weekly_tails": 0.60,
                "fibonacci": 0.20,
                "trend": 0.10,
                "moving_avg": 0.10,
            },
            "thresholds": {"confidence_min": 0.85},
        },
        "fibonacci": {
            "swing_lookback": 100,
            "key_levels": [0.382, 0.618],
            "proximity_threshold": 0.03,
            "min_swing_size": 0.15,
        },
        "weekly_tails": {
            "lookback_weeks": 8,
            "min_tail_strength": 0.35,
            "min_tail_ratio": 0.3,
            "max_body_atr": 2.0,
        },
        "analysis": {
            "trend": {
                "lookback_periods": 20,
                "strength_threshold": 0.6,
            }
        },
        "moving_averages": {
            "short_window": 50,
            "long_window": 200,
            "signal_threshold": 0.02,
        },
    }


@pytest.fixture
def sample_daily_data():
    """Simple daily price data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    return pd.DataFrame(
        {
            "Open": [500.0] * 100,
            "High": [510.0] * 100,
            "Low": [490.0] * 100,
            "Close": [505.0] * 100,
            "Volume": [1000000] * 100,
        },
        index=dates,
    )


@pytest.fixture
def sample_weekly_data():
    """Simple weekly price data for testing."""
    weekly_dates = pd.date_range("2024-01-01", periods=15, freq="W")
    return pd.DataFrame(
        {
            "Open": [500.0] * 15,
            "High": [520.0] * 15,
            "Low": [480.0] * 15,
            "Close": [505.0] * 15,
            "Volume": [5000000] * 15,
        },
        index=weekly_dates,
    )
