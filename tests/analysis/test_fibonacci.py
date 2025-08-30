"""
Unit tests for Fibonacci ModuleResult implementation (PR #4)
"""

import pandas as pd
import pytest

from bnb_trading.core.models import ModuleResult
from bnb_trading.fibonacci import FibonacciAnalyzer


@pytest.fixture
def fibonacci_config():
    """Standard Fibonacci config for testing"""
    return {
        "fibonacci": {
            "swing_lookback": 100,
            "key_levels": [0.382, 0.618],
            "proximity_threshold": 0.03,
            "min_swing_size": 0.15,
        },
        "signals": {"weights": {"fibonacci": 0.20}},
    }


@pytest.fixture
def sample_data():
    """Sample OHLCV data for testing with sufficient swing size"""
    dates = pd.date_range("2024-01-01", periods=200, freq="D")
    # Create data with clear swing pattern - LARGER swings (>15%)
    prices = []
    base_price = 400.0

    for i in range(200):
        # Create wave pattern with big swing high at middle
        if i < 50:
            price = base_price + (i * 3)  # Rising to ~550
        elif i < 100:
            price = (
                base_price + 150 - ((i - 50) * 2.5)
            )  # Falling to ~425 (swing high at ~550)
        elif i < 150:
            price = base_price + 25 + ((i - 100) * 1.5)  # Rising again to ~500
        else:
            price = base_price + 100 - ((i - 150) * 1)  # Decline to ~450

        prices.append(price)

    df = pd.DataFrame(
        {
            "Open": [p - 2 for p in prices],
            "High": [p + 5 for p in prices],
            "Low": [p - 8 for p in prices],
            "Close": prices,
            "Volume": [1000000] * 200,
        },
        index=dates,
    )

    return df


def test_fibonacci_analyze_basic(fibonacci_config, sample_data):
    """Test basic Fibonacci analyze method functionality"""
    analyzer = FibonacciAnalyzer(fibonacci_config)
    result = analyzer.analyze(sample_data, sample_data)  # weekly_df not used

    # Should return ModuleResult
    assert isinstance(result, ModuleResult)

    # Should always return HOLD state
    assert result.state == "HOLD"

    # Should have OK status with valid swing points
    assert result.status == "OK"

    # Score should be between 0.0 and 1.0
    assert 0.0 <= result.score <= 1.0

    # Contrib should be score * weight
    expected_contrib = result.score * 0.20
    assert abs(result.contrib - expected_contrib) < 0.001

    # Should have reason
    assert result.reason
    assert "Fibonacci analysis" in result.reason

    # Should have metadata
    assert result.meta
    assert "fib_levels" in result.meta
    assert "current_price" in result.meta


def test_fibonacci_analyze_insufficient_data(fibonacci_config):
    """Test behavior with insufficient data"""
    analyzer = FibonacciAnalyzer(fibonacci_config)

    # Create very small dataset (insufficient for swing detection)
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    small_df = pd.DataFrame(
        {
            "Open": [500] * 10,
            "High": [505] * 10,
            "Low": [495] * 10,
            "Close": [500] * 10,
            "Volume": [1000000] * 10,
        },
        index=dates,
    )

    result = analyzer.analyze(small_df, small_df)

    # Should be disabled due to insufficient data
    assert result.status == "DISABLED"
    assert result.state == "NEUTRAL"
    assert result.score == 0.0
    assert result.contrib == 0.0
    assert "Insufficient data" in result.reason


def test_fibonacci_analyze_small_swing(fibonacci_config):
    """Test behavior when swing size is too small"""
    # Modify config to have higher min_swing_size
    config = fibonacci_config.copy()
    config["fibonacci"]["min_swing_size"] = 0.50  # Very high threshold

    analyzer = FibonacciAnalyzer(config)

    # Create data with small swing
    dates = pd.date_range("2024-01-01", periods=150, freq="D")
    prices = [500 + (i % 10) for i in range(150)]  # Very small price movements

    df = pd.DataFrame(
        {
            "Open": prices,
            "High": [p + 2 for p in prices],
            "Low": [p - 2 for p in prices],
            "Close": prices,
            "Volume": [1000000] * 150,
        },
        index=dates,
    )

    result = analyzer.analyze(df, df)

    # Should be disabled due to small swing
    assert result.status == "DISABLED"
    assert result.state == "NEUTRAL"
    assert result.contrib == 0.0


def test_fibonacci_score_calculation():
    """Test _calculate_fib_score method logic"""
    config = {
        "fibonacci": {
            "swing_lookback": 100,
            "key_levels": [0.382, 0.618],
            "proximity_threshold": 0.03,
            "min_swing_size": 0.15,
        },
        "signals": {"weights": {"fibonacci": 0.20}},
    }

    analyzer = FibonacciAnalyzer(config)

    # Test case 1: No active levels (neutral)
    proximity_info = {"active_levels": []}
    score = analyzer._calculate_fib_score(proximity_info)
    assert score == 0.3

    # Test case 2: Golden ratio (61.8%)
    proximity_info = {"active_levels": [{"level": 0.618, "distance_percentage": 0.005}]}
    score = analyzer._calculate_fib_score(proximity_info)
    assert score == 0.7

    # Test case 3: Key level very close
    proximity_info = {
        "active_levels": [
            {
                "level": 0.382,
                "distance_percentage": 0.005,  # Very close (0.5%)
            }
        ]
    }
    score = analyzer._calculate_fib_score(proximity_info)
    assert score == 0.8

    # Test case 4: 50% level (neutral)
    proximity_info = {"active_levels": [{"level": 0.5, "distance_percentage": 0.01}]}
    score = analyzer._calculate_fib_score(proximity_info)
    assert score == 0.3


def test_fibonacci_analyze_error_handling(fibonacci_config):
    """Test error handling in analyze method"""
    analyzer = FibonacciAnalyzer(fibonacci_config)

    # Pass invalid DataFrame (empty DataFrame causes swing detection to fail)
    invalid_df = pd.DataFrame()  # Empty dataframe

    result = analyzer.analyze(invalid_df, invalid_df)

    # Should return DISABLED status (handled gracefully by swing detection)
    assert result.status == "DISABLED"
    assert result.state == "NEUTRAL"
    assert result.score == 0.0
    assert result.contrib == 0.0
    assert "data" in result.reason.lower()  # "Insufficient data" message


def test_fibonacci_config_weight_extraction(sample_data):
    """Test that weight is correctly extracted from config"""
    config = {
        "fibonacci": {
            "swing_lookback": 100,
            "key_levels": [0.382, 0.618],
            "proximity_threshold": 0.03,
            "min_swing_size": 0.15,
        },
        "signals": {
            "weights": {
                "fibonacci": 0.35  # Different weight
            }
        },
    }

    analyzer = FibonacciAnalyzer(config)
    result = analyzer.analyze(sample_data, sample_data)

    # Contrib should use the configured weight
    expected_contrib = result.score * 0.35
    assert abs(result.contrib - expected_contrib) < 0.001
