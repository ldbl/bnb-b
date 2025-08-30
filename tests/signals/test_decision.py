"""
Unit tests for PR #5: Unified Decision Engine
"""

from unittest.mock import patch

import pandas as pd
import pytest

from bnb_trading.core.models import DecisionContext, ModuleResult
from bnb_trading.signals.decision import _load_critical_modules, decide_long


@pytest.fixture
def sample_context():
    """Sample DecisionContext for testing"""
    # Create sample data
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    daily_df = pd.DataFrame(
        {
            "Open": [500] * 100,
            "High": [510] * 100,
            "Low": [490] * 100,
            "Close": [505] * 100,
            "Volume": [1000000] * 100,
        },
        index=dates,
    )

    weekly_dates = pd.date_range("2024-01-01", periods=15, freq="W")
    weekly_df = pd.DataFrame(
        {
            "Open": [500] * 15,
            "High": [520] * 15,
            "Low": [480] * 15,
            "Close": [505] * 15,
            "Volume": [5000000] * 15,
        },
        index=weekly_dates,
    )

    config = {
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

    return DecisionContext(
        closed_daily_df=daily_df,
        closed_weekly_df=weekly_df,
        config=config,
        timestamp=dates[-1],
    )


def test_decide_long_successful_signal(sample_context):
    """Test successful LONG signal generation"""

    # Mock all analyzers to return OK results with sufficient confidence
    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Configure mocks to return successful ModuleResults
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=0.8,
            contrib=0.48,  # 0.8 * 0.60
            reason="Strong weekly tail detected",
        )

        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="UP",
            score=0.7,
            contrib=0.07,  # 0.7 * 0.10
            reason="Upward trend confirmed",
        )

        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="HOLD",
            score=0.6,
            contrib=0.12,  # 0.6 * 0.20
            reason="Near key Fibonacci level",
        )

        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK",
            state="UP",
            score=0.8,
            contrib=0.08,  # 0.8 * 0.10
            reason="Price above moving averages",
        )

        # Total confidence = 0.48 + 0.07 + 0.12 + 0.08 = 0.75
        # But we need >= 0.85, so let's increase tails contrib
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=1.0,
            contrib=0.60,  # Higher contrib to reach threshold
            reason="Very strong weekly tail detected",
        )
        # New total = 0.60 + 0.07 + 0.12 + 0.08 = 0.87 >= 0.85

        result = decide_long(sample_context)

        # Verify LONG signal
        assert result.signal == "LONG"
        assert result.confidence >= 0.85
        assert "Weekly tails LONG signal" in result.reasons[0]
        assert "OK modules" in result.reasons[2]

        # Verify metrics
        assert result.metrics["total_confidence"] >= 0.85
        assert "module_results" in result.metrics
        assert len(result.metrics["ok_modules"]) == 4


def test_decide_long_weekly_tails_gate_failure(sample_context):
    """Test failure when weekly tails doesn't return LONG"""

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Weekly tails returns HOLD instead of LONG
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="HOLD",
            score=0.3,
            contrib=0.18,
            reason="Weak weekly pattern",
        )

        # Other modules are OK
        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK", state="UP", score=0.8, contrib=0.08, reason="Upward trend"
        )

        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="HOLD",
            score=0.6,
            contrib=0.12,
            reason="Neutral Fibonacci",
        )

        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK", state="UP", score=0.7, contrib=0.07, reason="Above MA"
        )

        result = decide_long(sample_context)

        # Should return HOLD due to tails gate failure
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Weekly tails gate failed" in result.reasons[0]
        assert result.metrics["failed_tails_gate"] is True


def test_decide_long_health_gate_failure(sample_context):
    """Test failure when critical module (weekly_tails) has non-OK status"""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails has ERROR status
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="ERROR",
            state="NEUTRAL",
            score=0.0,
            contrib=0.0,
            reason="Weekly tails analysis failed",
        )

        result = decide_long(sample_context)

        # Should fail health gate
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Critical module weekly_tails not healthy" in result.reasons[0]
        assert result.metrics["failed_health_gate"] == "weekly_tails"


def test_decide_long_insufficient_confidence(sample_context):
    """Test HOLD when total confidence < threshold"""

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Weekly tails OK but low confidence overall
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=0.4,
            contrib=0.24,  # 0.4 * 0.60
            reason="Weak weekly tail",
        )

        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="NEUTRAL",
            score=0.3,
            contrib=0.03,  # 0.3 * 0.10
            reason="Sideways trend",
        )

        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="HOLD",
            score=0.2,
            contrib=0.04,  # 0.2 * 0.20
            reason="Far from key levels",
        )

        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK",
            state="DOWN",
            score=0.2,
            contrib=0.02,  # 0.2 * 0.10
            reason="Below moving averages",
        )

        # Total confidence = 0.24 + 0.03 + 0.04 + 0.02 = 0.33 < 0.85

        result = decide_long(sample_context)

        # Should return HOLD due to insufficient confidence
        assert result.signal == "HOLD"
        assert result.confidence == 0.33
        assert "Below threshold" in result.reasons[0]
        assert result.metrics["total_confidence"] < 0.85


def test_decide_long_partial_module_failures(sample_context):
    """Test when some modules fail but weekly_tails is OK"""

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Weekly tails OK with high contribution
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=1.0,
            contrib=0.60,
            reason="Very strong weekly tail",
        )

        # Trend fails
        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="ERROR",
            state="NEUTRAL",
            score=0.0,
            contrib=0.0,
            reason="Trend analysis error",
        )

        # Fibonacci OK with high contribution
        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK", state="HOLD", score=1.0, contrib=0.20, reason="At golden ratio"
        )

        # Moving averages disabled
        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="DISABLED",
            state="NEUTRAL",
            score=0.0,
            contrib=0.0,
            reason="Insufficient data",
        )

        # Total confidence = 0.60 + 0.00 + 0.20 + 0.00 = 0.80 < 0.85

        result = decide_long(sample_context)

        # Should return HOLD due to partial failures lowering confidence
        assert result.signal == "HOLD"
        assert result.confidence == 0.80
        assert len(result.metrics["module_results"]) == 4  # All modules tracked


def test_decide_long_exception_handling(sample_context):
    """Test exception handling in decide_long"""

    # Mock analyzer to raise exception during initialization
    with patch(
        "bnb_trading.signals.decision.WeeklyTailsAnalyzer",
        side_effect=Exception("Initialization failed"),
    ):
        result = decide_long(sample_context)

        # Should return empty decision with error
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Error:" in result.reasons[0]


def test_decide_long_critical_modules_config(sample_context):
    """Test that critical modules can be configured"""

    # Add additional critical module to config
    sample_context.config["signals"]["critical_modules"] = ["weekly_tails", "fibonacci"]

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
    ):
        # Weekly tails OK but Fibonacci not OK
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=1.0,
            contrib=0.60,
            reason="Strong weekly tail",
        )

        # Fibonacci has ERROR status (should fail health gate)
        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="ERROR",
            state="NEUTRAL",
            score=0.0,
            contrib=0.0,
            reason="Fibonacci analysis failed",
        )

        result = decide_long(sample_context)

        # Should fail health gate due to Fibonacci being critical and not healthy
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Critical module fibonacci not healthy" in result.reasons[0]
        assert result.metrics["failed_health_gate"] == "fibonacci"


def test_decide_long_config_threshold_override(sample_context):
    """Test that confidence threshold can be configured"""

    # Lower threshold to 0.50
    sample_context.config["signals"]["thresholds"]["confidence_min"] = 0.50

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Medium confidence that would fail default threshold but pass lowered one
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=0.8,
            contrib=0.48,
            reason="Medium weekly tail",
        )

        # Other modules contribute small amounts
        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="NEUTRAL",
            score=0.1,
            contrib=0.01,
            reason="Neutral trend",
        )

        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="HOLD",
            score=0.1,
            contrib=0.02,
            reason="Neutral Fibonacci",
        )

        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK", state="NEUTRAL", score=0.1, contrib=0.01, reason="Neutral MA"
        )

        # Total confidence = 0.48 + 0.01 + 0.02 + 0.01 = 0.52 >= 0.50

        result = decide_long(sample_context)

        # Should return LONG due to lowered threshold
        assert result.signal == "LONG"
        assert result.confidence >= 0.50
        assert result.metrics["threshold"] == 0.50


def test_load_critical_modules_validation():
    """Test _load_critical_modules validation and fallback behavior"""

    # Test with valid config
    valid_config = {"signals": {"critical_modules": ["weekly_tails", "fibonacci"]}}
    result = _load_critical_modules(valid_config)
    assert result == ["weekly_tails", "fibonacci"]

    # Test with invalid type (not a list)
    invalid_config = {"signals": {"critical_modules": "weekly_tails"}}
    result = _load_critical_modules(invalid_config)
    assert result == ["weekly_tails"]  # Should fall back to default

    # Test with invalid list items (not strings)
    invalid_config = {"signals": {"critical_modules": ["weekly_tails", 123]}}
    result = _load_critical_modules(invalid_config)
    assert result == ["weekly_tails"]  # Should fall back to default

    # Test with missing config section
    empty_config = {}
    result = _load_critical_modules(empty_config)
    assert result == ["weekly_tails"]  # Should fall back to default

    # Test with None config (should load from file)
    result = _load_critical_modules(None)
    assert isinstance(result, list)  # Should return a list
    assert "weekly_tails" in result  # Should contain default or config value
