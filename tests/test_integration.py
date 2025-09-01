"""
Fixed integration tests for the working decision.py from commit 50d5636.
Tests the complete pipeline flow with simple, direct assertions.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from bnb_trading.core.models import DecisionContext
from bnb_trading.signals.decision import decide_long


@pytest.fixture
def integration_context(
    test_config, sample_daily_data, sample_weekly_data
) -> DecisionContext:
    """Create integration test context."""
    return DecisionContext(
        closed_daily_df=sample_daily_data,
        closed_weekly_df=sample_weekly_data,
        config=test_config,
        timestamp=sample_daily_data.index[-1],
    )


def test_pipeline_full_success_flow(integration_context):
    """Test complete successful pipeline flow from context to LONG signal."""

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision._get_fibonacci_confidence") as mock_fib,
        patch("bnb_trading.signals.decision._get_trend_confidence") as mock_trend,
        patch("bnb_trading.signals.decision._get_volume_confidence") as mock_vol,
    ):
        # Configure successful pipeline flow
        mock_tails.return_value.calculate_tail_strength.return_value = {
            "signal": "LONG",
            "strength": 0.90,
            "confidence": 0.95,
            "price_level": 500.0,
        }

        # Mock helper functions for strong confidence
        mock_fib.return_value = 0.80
        mock_trend.return_value = 0.85
        mock_vol.return_value = 0.70

        result = decide_long(integration_context)

        # Pipeline should produce LONG signal
        assert result.signal == "LONG"
        assert result.confidence >= 0.85
        assert "Strong weekly tail" in result.reasons[0]
        assert result.metrics["tail_strength"] >= 0.85


def test_pipeline_weekly_tails_gate_blocks_signal(integration_context):
    """Test pipeline blocks signal when weekly tails gate fails."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails fails gate check
        mock_tails.return_value.calculate_tail_strength.return_value = {
            "signal": "HOLD",
            "strength": 0.20,
            "confidence": 0.10,
            "price_level": 500.0,
        }

        result = decide_long(integration_context)

        # Pipeline should stop at gate
        assert result.signal == "HOLD"
        assert result.confidence < 0.85
        assert "Basic filters failed" in result.reasons[0]


def test_pipeline_health_gate_protection(integration_context):
    """Test pipeline health gate protects against unhealthy modules."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Critical module has ERROR status
        mock_tails.return_value.calculate_tail_strength.side_effect = Exception(
            "Analysis failed"
        )

        result = decide_long(integration_context)

        # Health gate should block
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Error:" in result.reasons[0]


def test_pipeline_confidence_threshold_enforcement(integration_context):
    """Test pipeline enforces confidence threshold correctly."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Configure low confidence scenario
        mock_tails.return_value.calculate_tail_strength.return_value = {
            "signal": "LONG",
            "strength": 0.50,
            "confidence": 0.60,  # Below threshold
            "price_level": 500.0,
        }

        result = decide_long(integration_context)

        # Pipeline should enforce threshold
        assert result.signal == "HOLD"
        assert result.confidence < 0.88
        assert "Below threshold" in result.reasons[0]


def test_pipeline_partial_module_failures(integration_context):
    """Test pipeline handles partial module failures correctly."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails works but with weak signal
        mock_tails.return_value.calculate_tail_strength.return_value = {
            "signal": "LONG",
            "strength": 0.35,  # Above minimum but weak
            "confidence": 0.40,  # Low confidence
            "price_level": 500.0,
        }

        result = decide_long(integration_context)

        # Should handle gracefully
        assert result.signal == "HOLD"
        assert result.confidence < 0.88
        assert "Below threshold" in result.reasons[0]


def test_pipeline_exception_safety(integration_context):
    """Test pipeline handles exceptions safely."""

    with patch("bnb_trading.signals.decision._validate_no_lookahead") as mock_validate:
        # Simulate validation exception
        mock_validate.side_effect = Exception("Validation failed")

        result = decide_long(integration_context)

        # Should return safe result
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "Error:" in result.reasons[0]


def test_data_context_validation(integration_context):
    """Test pipeline validates data context properly."""

    # Test with empty dataframes
    empty_context = DecisionContext(
        closed_daily_df=pd.DataFrame(),
        closed_weekly_df=pd.DataFrame(),
        config=integration_context.config,
        timestamp=integration_context.timestamp,
    )

    result = decide_long(empty_context)

    # Should handle empty data safely
    assert result.signal == "HOLD"
    assert result.confidence == 0.0
    # Could be validation failure or basic filters failure
    assert any(
        keyword in result.reasons[0]
        for keyword in ["validation", "Basic filters", "Error"]
    )
