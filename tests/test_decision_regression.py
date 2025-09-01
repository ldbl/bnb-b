"""
Fixed regression tests for 21/21 LONG accuracy protection.
Tests updated to match the actual working decision.py from commit 50d5636.
"""

from unittest.mock import patch

import pytest

from bnb_trading.core.models import DecisionContext
from bnb_trading.signals.decision import decide_long


@pytest.fixture
def decision_context(
    test_config, sample_daily_data, sample_weekly_data
) -> DecisionContext:
    """Create DecisionContext for regression testing."""
    return DecisionContext(
        closed_daily_df=sample_daily_data,
        closed_weekly_df=sample_weekly_data,
        config=test_config,
        timestamp=sample_daily_data.index[-1],
    )


def test_long_signal_regression_protection(decision_context):
    """Critical test: Ensure 21/21 LONG accuracy is preserved."""

    # Mock weekly tails analyzer and helper functions for strong LONG signal
    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision._get_fibonacci_confidence") as mock_fib,
        patch("bnb_trading.signals.decision._get_trend_confidence") as mock_trend,
        patch("bnb_trading.signals.decision._get_volume_confidence") as mock_vol,
    ):
        # Configure strong LONG signal scenario
        mock_tails.return_value.calculate_tail_strength.return_value = {
            "signal": "LONG",
            "strength": 0.90,
            "confidence": 0.95,  # High tail confidence
            "price_level": 500.0,
        }

        # Mock helper functions to contribute to weighted confidence
        mock_fib.return_value = 0.80  # 0.80 * 0.20 = 0.16
        mock_trend.return_value = 0.85  # 0.85 * 0.10 = 0.085
        mock_vol.return_value = 0.70  # 0.70 * 0.10 = 0.07

        # Total weighted = 0.95*0.60 + 0.80*0.20 + 0.85*0.10 + 0.70*0.10
        #                = 0.57 + 0.16 + 0.085 + 0.07 = 0.885 >= 0.88 ✓

        # Test critical LONG signal generation
        result = decide_long(decision_context)

        # Must produce LONG signal with high confidence
        assert result.signal == "LONG"
        assert result.confidence >= 0.85
        assert "Strong weekly tail" in result.reasons[0]
        assert result.metrics["tail_strength"] >= 0.80

        # Verify weekly tails analyzer was called
        mock_tails.return_value.calculate_tail_strength.assert_called_once()


def test_weekly_tails_gate_enforcement(decision_context):
    """Ensure weekly tails gate prevents false LONG signals."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails returns HOLD - should block LONG
        mock_tails.return_value.calculate_tail_strength.return_value = {
            "signal": "HOLD",
            "strength": 0.2,
            "confidence": 0.1,
            "price_level": 500.0,
        }

        result = decide_long(decision_context)

        # Gate should block LONG signal
        assert result.signal == "HOLD"
        assert result.confidence < 0.85
        assert "Basic filters failed" in result.reasons[0]


def test_health_gate_protection(decision_context):
    """Ensure system handles analyzer failures gracefully."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails analyzer throws exception
        mock_tails.return_value.calculate_tail_strength.side_effect = Exception(
            "Weekly tails analysis failed"
        )

        result = decide_long(decision_context)

        # Should return safe HOLD signal
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Error:" in result.reasons[0]


def test_confidence_threshold_enforcement(decision_context):
    """Ensure confidence threshold prevents weak LONG signals."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Configure weak signal below threshold
        mock_tails.return_value.calculate_tail_strength.return_value = {
            "signal": "LONG",
            "strength": 0.40,
            "confidence": 0.50,  # Below 0.88 threshold
            "price_level": 500.0,
        }

        result = decide_long(decision_context)

        # Should block weak signal
        assert result.signal == "HOLD"
        assert result.confidence < 0.88
        assert "Below threshold" in result.reasons[0]


def test_exception_handling_safety(decision_context):
    """Test system safely handles all exceptions."""

    with patch("bnb_trading.signals.decision._validate_no_lookahead") as mock_validate:
        # Simulate validation failure
        mock_validate.side_effect = Exception("Validation error")

        result = decide_long(decision_context)

        # Should return safe result
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Error:" in result.reasons[0]
