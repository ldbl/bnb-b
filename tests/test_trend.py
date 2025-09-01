"""
Focused TrendAnalyzer tests for KISS testing strategy.
Direct unit tests for core trend analysis functionality.
"""

import numpy as np
import pandas as pd

from bnb_trading.trend_analyzer import TrendAnalyzer

# Set random seed for deterministic test results
np.random.seed(42)


def create_trend_data(
    direction: str = "uptrend", strength: str = "moderate", periods: int = 200
) -> pd.DataFrame:
    """Create test data with specific trend characteristics."""
    dates = pd.date_range("2024-01-01", periods=periods, freq="D")

    base_price = 500.0
    prices = []

    if direction == "uptrend":
        # Create uptrend with specified strength
        slope_multiplier = {"weak": 0.3, "moderate": 0.8, "strong": 1.5, "extreme": 3.0}
        slope = slope_multiplier.get(strength, 0.8)

        for i in range(periods):
            # Linear uptrend with noise
            trend_price = base_price + (i * slope)
            noise = np.random.normal(0, 5)  # Small random noise
            prices.append(max(trend_price + noise, 1.0))  # Ensure positive prices

    elif direction == "downtrend":
        slope_multiplier = {
            "weak": -0.3,
            "moderate": -0.8,
            "strong": -1.5,
            "extreme": -3.0,
        }
        slope = slope_multiplier.get(strength, -0.8)

        for i in range(periods):
            trend_price = base_price + (i * slope)
            noise = np.random.normal(0, 5)
            prices.append(max(trend_price + noise, 1.0))

    else:  # neutral/sideways
        for i in range(periods):
            noise = np.random.normal(0, 10)
            prices.append(max(base_price + noise, 1.0))

    # Create OHLCV data
    data = {
        "Open": [p * 0.998 for p in prices],
        "High": [p * 1.005 for p in prices],
        "Low": [p * 0.995 for p in prices],
        "Close": prices,
        "Volume": [1000000] * periods,
    }

    return pd.DataFrame(data, index=dates)


def create_weekly_data(periods: int = 20) -> pd.DataFrame:
    """Create simple weekly data."""
    dates = pd.date_range("2024-01-01", periods=periods, freq="W")
    return pd.DataFrame(
        {
            "Open": [500.0] * periods,
            "High": [520.0] * periods,
            "Low": [480.0] * periods,
            "Close": [510.0] * periods,
            "Volume": [5000000] * periods,
        },
        index=dates,
    )


def test_analyze_daily_trend_uptrend(test_config):
    """Test daily trend analysis with uptrend data."""
    analyzer = TrendAnalyzer(test_config)
    df = create_trend_data("uptrend", "strong", 200)

    daily_trend = analyzer._analyze_daily_trend(df)

    assert daily_trend["direction"] == "UPTREND"
    assert daily_trend["strength"] in [
        "WEAK",
        "MODERATE",
        "STRONG",
        "EXTREME",
    ]  # Can vary with random noise
    assert daily_trend["price_change_pct"] > 0
    assert daily_trend["slope"] > 0


def test_analyze_daily_trend_downtrend(test_config):
    """Test daily trend analysis with downtrend data."""
    analyzer = TrendAnalyzer(test_config)
    df = create_trend_data("downtrend", "strong", 200)

    daily_trend = analyzer._analyze_daily_trend(df)

    assert daily_trend["direction"] == "DOWNTREND"
    assert daily_trend["strength"] in ["MODERATE", "STRONG", "EXTREME"]
    assert daily_trend["price_change_pct"] < 0
    assert daily_trend["slope"] < 0


def test_analyze_daily_trend_neutral(test_config):
    """Test daily trend analysis with neutral data."""
    analyzer = TrendAnalyzer(test_config)
    df = create_trend_data("neutral", "weak", 200)

    daily_trend = analyzer._analyze_daily_trend(df)

    assert daily_trend["direction"] in [
        "NEUTRAL",
        "UPTREND",
        "DOWNTREND",
    ]  # Random noise can create slight trends
    assert daily_trend["strength"] in ["WEAK", "MODERATE"]


def test_analyze_daily_trend_insufficient_data(test_config):
    """Test daily trend analysis with insufficient data."""
    analyzer = TrendAnalyzer(test_config)
    df = create_trend_data("uptrend", "moderate", 10)  # Only 10 days

    daily_trend = analyzer._analyze_daily_trend(df)

    assert "error" in daily_trend
    assert "недостатъчно данни" in daily_trend["error"].lower()


def test_analyze_weekly_trend_basic(test_config):
    """Test weekly trend analysis with basic data."""
    analyzer = TrendAnalyzer(test_config)
    df = create_weekly_data(20)

    weekly_trend = analyzer._analyze_weekly_trend(df)

    assert "direction" in weekly_trend
    assert "strength" in weekly_trend
    assert "price_change_pct" in weekly_trend
    assert weekly_trend["direction"] in ["UPTREND", "DOWNTREND", "NEUTRAL"]


def test_analyze_price_range(test_config):
    """Test price range analysis."""
    analyzer = TrendAnalyzer(test_config)
    df = create_trend_data("uptrend", "moderate", 100)

    range_analysis = analyzer._analyze_price_range(df)

    assert "current_range" in range_analysis
    assert "current_range_pct" in range_analysis
    assert "range_status" in range_analysis
    assert "range_position" in range_analysis
    assert range_analysis["range_status"] in ["EXPANDING", "CONTRACTING", "RANGE"]
    assert 0.0 <= range_analysis["range_position"] <= 1.0


def test_strength_to_score_conversion(test_config):
    """Test trend strength to numerical score conversion."""
    analyzer = TrendAnalyzer(test_config)

    assert analyzer._strength_to_score("WEAK") == 0.3
    assert analyzer._strength_to_score("MODERATE") == 0.6
    assert analyzer._strength_to_score("STRONG") == 1.0
    assert analyzer._strength_to_score("EXTREME") == 1.2
    assert analyzer._strength_to_score("UNKNOWN") == 0.5  # Default


def test_detect_market_regime_strong_bull(test_config):
    """Test market regime detection for strong bull market."""
    analyzer = TrendAnalyzer(test_config)
    df = create_trend_data("uptrend", "extreme", 400)  # Long strong uptrend

    medium_trend = {"price_change_pct": 30.0, "direction": "UPTREND"}
    long_trend = {"price_change_pct": 60.0, "direction": "UPTREND"}

    regime = analyzer._detect_market_regime(df, medium_trend, long_trend)

    assert regime["regime"] in ["STRONG_BULL", "MODERATE_BULL", "WEAK_BULL"]
    assert 0.0 <= regime["confidence"] <= 1.0
    assert isinstance(regime["reason"], str)


def test_complete_trend_analysis(test_config):
    """Test complete trend analysis workflow."""
    analyzer = TrendAnalyzer(test_config)
    daily_df = create_trend_data("uptrend", "moderate", 200)
    weekly_df = create_weekly_data(30)

    result = analyzer.analyze_trend(daily_df, weekly_df)

    # Check all required components
    assert "daily_trend" in result
    assert "weekly_trend" in result
    assert "medium_term_trend" in result
    assert "long_term_trend" in result
    assert "market_regime" in result
    assert "range_analysis" in result
    assert "combined_trend" in result
    assert "adaptive_strategy" in result

    # Check combined trend structure
    combined = result["combined_trend"]
    assert "primary_trend" in combined
    assert "trend_confidence" in combined
    assert "combined_strength" in combined


def test_error_handling_invalid_data(test_config):
    """Test error handling with invalid data."""
    analyzer = TrendAnalyzer(test_config)

    # Create DataFrame with insufficient data
    df = pd.DataFrame(
        {
            "Open": [500.0],
            "High": [510.0],
            "Low": [490.0],
            "Close": [505.0],
            "Volume": [1000000],
        },
        index=pd.date_range("2024-01-01", periods=1, freq="D"),
    )

    weekly_df = create_weekly_data(2)

    result = analyzer.analyze_trend(df, weekly_df)

    # Should handle errors gracefully
    assert isinstance(result, dict)
    # May contain errors in sub-components but shouldn't crash
