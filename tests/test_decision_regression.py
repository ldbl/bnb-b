"""
Critical regression tests for 21/21 LONG accuracy protection.
Simple, direct tests focused on preserving perfect LONG signal accuracy.
"""

from unittest.mock import patch

import pytest

from bnb_trading.core.models import DecisionContext, ModuleResult
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

    # Mock all analyzers to return strong LONG signal
    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Configure strong LONG signal scenario
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=1.0,
            contrib=0.60,
            reason="Very strong weekly tail detected",
        )

        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="UP",
            score=0.8,
            contrib=0.08,
            reason="Strong upward trend confirmed",
        )

        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="HOLD",
            score=0.7,
            contrib=0.14,
            reason="Near golden ratio support",
        )

        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK",
            state="UP",
            score=0.9,
            contrib=0.09,
            reason="Price well above moving averages",
        )

        # Total confidence = 0.60 + 0.08 + 0.14 + 0.09 = 0.91 >= 0.85

        result = decide_long(decision_context)

        # Critical assertions for 21/21 LONG accuracy
        assert result.signal == "LONG"
        assert result.confidence >= 0.85
        assert "weekly" in result.reasons[0].lower()
        assert result.metrics["total_confidence"] >= 0.85


def test_weekly_tails_gate_enforcement(decision_context):
    """Ensure weekly tails gate prevents false LONG signals."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails returns HOLD - should block LONG
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="HOLD",
            score=0.3,
            contrib=0.18,
            reason="Weak weekly pattern",
        )

        result = decide_long(decision_context)

        # Gate should block LONG signal
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "weekly tails gate failed" in result.reasons[0].lower()


def test_health_gate_protection(decision_context):
    """Ensure critical module health gate prevents risky signals."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails has ERROR status
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="ERROR",
            state="NEUTRAL",
            score=0.0,
            contrib=0.0,
            reason="Weekly tails analysis failed",
        )

        result = decide_long(decision_context)

        # Health gate should prevent LONG
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "critical module" in result.reasons[0].lower()


def test_confidence_threshold_enforcement(decision_context):
    """Ensure confidence threshold prevents weak LONG signals."""

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Weak signals that don't meet threshold
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=0.4,
            contrib=0.24,
            reason="Weak weekly tail",
        )

        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK", state="UP", score=0.3, contrib=0.03, reason="Weak trend"
        )

        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK", state="HOLD", score=0.2, contrib=0.04, reason="Neutral fib"
        )

        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK", state="DOWN", score=0.2, contrib=0.02, reason="Below MA"
        )

        # Total confidence = 0.24 + 0.03 + 0.04 + 0.02 = 0.33 < 0.85

        result = decide_long(decision_context)

        # Should reject due to low confidence
        assert result.signal == "HOLD"
        assert result.confidence < 0.85
        assert "below threshold" in result.reasons[0].lower()


def test_exception_handling_safety(decision_context):
    """Ensure system fails safely when modules have exceptions."""

    # Mock analyzer to raise exception
    with patch(
        "bnb_trading.signals.decision.WeeklyTailsAnalyzer",
        side_effect=Exception("Analyzer initialization failed"),
    ):
        result = decide_long(decision_context)

        # Should fail safely to HOLD
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "error" in result.reasons[0].lower()
