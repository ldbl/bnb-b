"""
Focused FibonacciAnalyzer tests for KISS testing strategy.
Direct unit tests for core Fibonacci functionality - simple and effective.
"""

import pandas as pd

from bnb_trading.fibonacci import FibonacciAnalyzer


def create_swing_data(
    high_price=600.0, low_price=400.0, current_price=500.0, periods=120
):
    """Create test data with defined swing high/low pattern."""
    dates = pd.date_range("2024-01-01", periods=periods, freq="D")

    # Create base data
    data = {
        "Open": [500.0] * periods,
        "High": [520.0] * periods,
        "Low": [480.0] * periods,
        "Close": [current_price] * periods,
        "Volume": [1000000] * periods,
    }

    # Create swing high at 25% of the data
    high_idx = periods // 4
    data["High"][high_idx] = high_price

    # Create swing low at 75% of the data
    low_idx = periods * 3 // 4
    data["Low"][low_idx] = low_price

    return pd.DataFrame(data, index=dates)


def test_find_swing_points_basic(test_config):
    """Test basic swing point detection."""
    analyzer = FibonacciAnalyzer(test_config)
    df = create_swing_data(high_price=600.0, low_price=400.0)

    high, low, high_idx, low_idx = analyzer.find_swing_points(df)

    assert high == 600.0
    assert low == 400.0
    assert high_idx is not None
    assert low_idx is not None


def test_find_swing_points_insufficient_size(test_config):
    """Test swing detection with insufficient swing size."""
    # Set high minimum swing size
    config = test_config.copy()
    config["fibonacci"]["min_swing_size"] = 0.5  # 50% minimum

    analyzer = FibonacciAnalyzer(config)
    df = create_swing_data(high_price=510.0, low_price=490.0)  # Only 4% swing

    high, low, high_idx, low_idx = analyzer.find_swing_points(df)

    # Should return None for all values due to insufficient swing size
    assert high is None
    assert low is None
    assert high_idx is None
    assert low_idx is None


def test_calculate_fibonacci_levels(test_config):
    """Test Fibonacci level calculations."""
    analyzer = FibonacciAnalyzer(test_config)

    fib_levels = analyzer.calculate_fibonacci_levels(600.0, 400.0)

    # Expected levels for 200-point swing (600-400)
    expected_levels = {
        0.0: 400.0,  # 0% = swing low
        0.236: 447.2,  # 23.6%
        0.382: 476.4,  # 38.2%
        0.5: 500.0,  # 50%
        0.618: 523.6,  # 61.8%
        0.786: 557.2,  # 78.6%
        1.0: 600.0,  # 100% = swing high
    }

    for level, expected_price in expected_levels.items():
        assert abs(fib_levels[level] - expected_price) < 0.1


def test_calculate_fibonacci_levels_invalid_swings(test_config):
    """Test Fibonacci calculations with invalid swing points."""
    analyzer = FibonacciAnalyzer(test_config)

    # Test with None values
    fib_levels = analyzer.calculate_fibonacci_levels(None, 400.0)
    assert fib_levels == {}

    fib_levels = analyzer.calculate_fibonacci_levels(600.0, None)
    assert fib_levels == {}


def test_check_fib_proximity_at_key_level(test_config):
    """Test proximity detection at key Fibonacci level."""
    analyzer = FibonacciAnalyzer(test_config)

    # Fib levels for 600-400 swing
    fib_levels = {
        0.0: 400.0,
        0.382: 476.4,
        0.618: 523.6,
        1.0: 600.0,
    }

    # Current price near 61.8% level
    proximity_info = analyzer.check_fib_proximity(525.0, fib_levels)

    assert proximity_info["nearest_level"] == 0.618
    assert len(proximity_info["active_levels"]) > 0
    assert 0.618 in proximity_info["key_level_proximity"]
    assert proximity_info["key_level_proximity"][0.618]["is_active"] is True


def test_check_fib_proximity_no_active_levels(test_config):
    """Test proximity detection away from any levels."""
    analyzer = FibonacciAnalyzer(test_config)

    fib_levels = {
        0.0: 400.0,
        0.382: 476.4,
        0.618: 523.6,
        1.0: 600.0,
    }

    # Current price far from any level
    proximity_info = analyzer.check_fib_proximity(450.0, fib_levels)

    assert len(proximity_info["active_levels"]) == 0
    assert proximity_info["nearest_level"] is not None


def test_get_fibonacci_signal_long_at_support(test_config):
    """Test LONG signal generation at Fibonacci support."""
    analyzer = FibonacciAnalyzer(test_config)

    fib_levels = {
        0.0: 400.0,
        0.236: 447.2,
        0.382: 476.4,  # Key support level
        0.5: 500.0,
        0.618: 523.6,
        0.786: 557.2,
        1.0: 600.0,
    }

    # Price at 38.2% support level
    signal_info = analyzer.get_fibonacci_signal(476.0, fib_levels)

    assert signal_info["signal"] == "LONG"
    assert signal_info["strength"] == 0.8
    assert "LONG" in signal_info["reason"]
    assert "support" in signal_info["reason"].lower()


def test_analyze_complete_workflow(test_config):
    """Test complete analyze method workflow."""
    analyzer = FibonacciAnalyzer(test_config)
    df = create_swing_data(high_price=600.0, low_price=400.0, current_price=476.0)

    result = analyzer.analyze_fibonacci_trend(df)

    assert "swing_high" in result
    assert "swing_low" in result
    assert "fibonacci_levels" in result
    assert "current_price" in result
    assert "fibonacci_signal" in result
    assert result["swing_high"] == 600.0
    assert result["swing_low"] == 400.0


def test_analyze_module_result_interface(test_config):
    """Test ModuleResult interface for decision engine integration."""
    analyzer = FibonacciAnalyzer(test_config)
    daily_df = create_swing_data()
    weekly_df = pd.DataFrame()  # Not used by Fibonacci

    result = analyzer.analyze(daily_df, weekly_df)

    # Check ModuleResult interface
    assert hasattr(result, "status")
    assert hasattr(result, "state")
    assert hasattr(result, "score")
    assert hasattr(result, "contrib")
    assert hasattr(result, "reason")

    # Fibonacci always returns HOLD state
    assert result.state == "HOLD"
    assert result.status in ["OK", "DISABLED", "ERROR"]
    assert 0.0 <= result.score <= 1.0


def test_error_handling_invalid_data(test_config):
    """Test error handling with invalid data."""
    analyzer = FibonacciAnalyzer(test_config)

    # Create DataFrame with insufficient data
    df = pd.DataFrame(
        {
            "Open": [500.0],
            "High": [510.0],
            "Low": [490.0],
            "Close": [505.0],
        },
        index=pd.date_range("2024-01-01", periods=1, freq="D"),
    )

    result = analyzer.analyze_fibonacci_trend(df)

    # Should handle gracefully
    assert "error" in result
    assert isinstance(result["error"], str)
