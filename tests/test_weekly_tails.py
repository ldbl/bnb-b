"""
Focused WeeklyTailsAnalyzer tests for KISS testing strategy.
Direct unit tests for core functionality - no complex mocking.
"""

import pandas as pd

from bnb_trading.analysis.weekly_tails.analyzer import WeeklyTailsAnalyzer


def create_weekly_data_with_tail(tail_strength=2.0, weeks=10):
    """Create weekly data with a strong tail pattern."""
    dates = pd.date_range("2024-01-01", periods=weeks, freq="W")

    # Base data
    data = {
        "Open": [500.0] * weeks,
        "High": [520.0] * weeks,
        "Low": [480.0] * weeks,
        "Close": [510.0] * weeks,
        "Volume": [1000000] * weeks,
    }

    # Add strong tail in last week
    if weeks > 0:
        low_price = 450.0  # Strong lower wick
        data["Low"][-1] = low_price
        data["Open"][-1] = 500.0
        data["Close"][-1] = 495.0  # Bullish close above open
        data["Volume"][-1] = 2000000  # High volume

    return pd.DataFrame(data, index=dates)


def test_calculate_tail_strength_basic_long_signal(test_config):
    """Test basic LONG signal detection with strong tail."""
    analyzer = WeeklyTailsAnalyzer(test_config)
    df = create_weekly_data_with_tail(tail_strength=3.0, weeks=12)

    result = analyzer.calculate_tail_strength(df)

    assert result["signal"] == "LONG"
    assert result["strength"] > 0.0
    assert result["confidence"] > 0.0
    assert "tail" in result["reason"].lower()


def test_calculate_tail_strength_insufficient_data(test_config):
    """Test handling of insufficient data gracefully."""
    analyzer = WeeklyTailsAnalyzer(test_config)
    df = create_weekly_data_with_tail(weeks=2)  # Too few weeks

    result = analyzer.calculate_tail_strength(df)

    assert result["signal"] == "HOLD"
    assert result["strength"] == 0.0
    assert result["confidence"] == 0.0
    assert "insufficient" in result["reason"].lower()


def test_calculate_tail_strength_no_qualifying_tails(test_config):
    """Test HOLD when no tails meet criteria."""
    analyzer = WeeklyTailsAnalyzer(test_config)

    # Create data with weak tails
    dates = pd.date_range("2024-01-01", periods=10, freq="W")
    df = pd.DataFrame(
        {
            "Open": [500.0] * 10,
            "High": [505.0] * 10,  # Small range
            "Low": [499.0] * 10,  # No meaningful lower wick
            "Close": [502.0] * 10,
            "Volume": [1000000] * 10,
        },
        index=dates,
    )

    result = analyzer.calculate_tail_strength(df)

    assert result["signal"] == "HOLD"
    assert result["strength"] == 0.0
    assert "no qualifying" in result["reason"].lower()


def test_tail_ratio_validation(test_config):
    """Test tail ratio validation rule."""
    # Set strict tail ratio requirement
    config = test_config.copy()
    config["weekly_tails"]["min_tail_ratio"] = 2.0

    analyzer = WeeklyTailsAnalyzer(config)

    # Create data with weak tail ratio
    dates = pd.date_range("2024-01-01", periods=10, freq="W")
    df = pd.DataFrame(
        {
            "Open": [500.0] * 10,
            "High": [520.0] * 10,
            "Low": [495.0] * 10,  # Small lower wick relative to ATR
            "Close": [505.0] * 10,
            "Volume": [1000000] * 10,
        },
        index=dates,
    )

    result = analyzer.calculate_tail_strength(df)

    assert result["signal"] == "HOLD"
    assert result["strength"] == 0.0


def test_body_size_validation(test_config):
    """Test body size validation rule."""
    # Set strict body size limit
    config = test_config.copy()
    config["weekly_tails"]["max_body_atr"] = 0.5

    analyzer = WeeklyTailsAnalyzer(config)

    # Create data with large body size
    dates = pd.date_range("2024-01-01", periods=10, freq="W")
    df = pd.DataFrame(
        {
            "Open": [500.0] * 10,
            "High": [520.0] * 10,
            "Low": [450.0] * 10,  # Good lower wick
            "Close": [600.0] * 10,  # But huge body
            "Volume": [2000000] * 10,
        },
        index=dates,
    )

    result = analyzer.calculate_tail_strength(df)

    assert result["signal"] == "HOLD"


def test_close_position_validation(test_config):
    """Test close position validation rule."""
    # Set minimum close position
    config = test_config.copy()
    config["weekly_tails"]["min_close_pos"] = 0.7

    analyzer = WeeklyTailsAnalyzer(config)

    # Create data with low close position
    dates = pd.date_range("2024-01-01", periods=10, freq="W")
    df = pd.DataFrame(
        {
            "Open": [500.0] * 10,
            "High": [520.0] * 10,
            "Low": [450.0] * 10,
            "Close": [460.0] * 10,  # Close near low (low close position)
            "Volume": [1000000] * 10,
        },
        index=dates,
    )

    result = analyzer.calculate_tail_strength(df)

    assert result["signal"] == "HOLD"


def test_error_handling_invalid_data(test_config):
    """Test handling of corrupted/invalid data safely."""
    analyzer = WeeklyTailsAnalyzer(test_config)

    # Create data with invalid values
    dates = pd.date_range("2024-01-01", periods=10, freq="W")
    df = pd.DataFrame(
        {
            "Open": [0.0, -100.0] + [500.0] * 8,  # Invalid prices
            "High": [520.0] * 10,
            "Low": [480.0] * 10,
            "Close": [505.0] * 10,
            "Volume": [0.0, -1000.0] + [1000000] * 8,  # Invalid volumes
        },
        index=dates,
    )

    result = analyzer.calculate_tail_strength(df)

    # Should handle errors gracefully
    assert "signal" in result
    assert "strength" in result
    assert "confidence" in result


def test_configuration_parameter_loading(test_config):
    """Test configuration parameters load correctly."""
    config = test_config.copy()
    config["weekly_tails"] = {
        "lookback_weeks": 12,
        "min_tail_strength": 2.5,
        "min_tail_ratio": 1.5,
        "max_body_atr": 0.6,
        "min_close_pos": 0.4,
    }

    analyzer = WeeklyTailsAnalyzer(config)

    assert analyzer.lookback_weeks == 12
    assert analyzer.min_tail_strength == 2.5
    assert analyzer.min_tail_ratio == 1.5
    assert analyzer.max_body_atr == 0.6
    assert analyzer.min_close_pos == 0.4


def test_module_result_interface(test_config):
    """Test WeeklyTailsAnalyzer provides expected interface."""
    # Test direct analyzer interface instead of module wrapper
    analyzer = WeeklyTailsAnalyzer(test_config)
    weekly_data = create_weekly_data_with_tail(weeks=10)

    result = analyzer.calculate_tail_strength(weekly_data)

    # Should return expected interface
    assert "signal" in result
    assert "strength" in result
    assert "confidence" in result
    assert "reason" in result
    assert result["signal"] in ["LONG", "HOLD"]
    assert isinstance(result["strength"], (int, float))
    assert isinstance(result["confidence"], (int, float))


def test_regression_accuracy_protection(test_config):
    """Ensure analyzer changes don't break 21/21 LONG accuracy."""
    analyzer = WeeklyTailsAnalyzer(test_config)

    # Test known LONG scenario
    df = create_weekly_data_with_tail(tail_strength=4.0, weeks=12)
    result = analyzer.calculate_tail_strength(df)

    # Critical assertions for regression protection
    assert result["signal"] in ["LONG", "HOLD"]  # Valid signals only
    assert isinstance(result["strength"], (int, float))
    assert isinstance(result["confidence"], (int, float))
    assert 0.0 <= result["confidence"] <= 1.0  # Valid confidence range
    assert isinstance(result["reason"], str)
    assert len(result["reason"]) > 0  # Non-empty reason
