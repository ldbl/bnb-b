"""
Integration tests for KISS testing strategy.
Tests the complete pipeline flow with simple, direct assertions.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from bnb_trading.core.models import DecisionContext, ModuleResult
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
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Configure successful pipeline flow
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=0.9,
            contrib=0.54,
            reason="Strong weekly tail",
        )
        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK", state="UP", score=0.8, contrib=0.08, reason="Strong uptrend"
        )
        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK", state="HOLD", score=0.7, contrib=0.14, reason="At key level"
        )
        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK", state="UP", score=0.9, contrib=0.09, reason="Above MA"
        )

        result = decide_long(integration_context)

        # Verify complete pipeline success
        assert result.signal == "LONG"
        assert result.confidence >= 0.85
        assert len(result.reasons) >= 3  # Multiple reasons provided
        assert result.metrics["total_confidence"] >= 0.85
        assert len(result.metrics["ok_modules"]) == 4


def test_pipeline_weekly_tails_gate_blocks_signal(integration_context):
    """Test pipeline blocks signal when weekly tails gate fails."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Weekly tails fails gate check
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK", state="HOLD", score=0.3, contrib=0.18, reason="Weak tail"
        )

        result = decide_long(integration_context)

        # Pipeline should stop at gate
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "gate failed" in result.reasons[0].lower()


def test_pipeline_health_gate_protection(integration_context):
    """Test pipeline health gate protects against unhealthy modules."""

    with patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails:
        # Critical module has ERROR status
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="ERROR",
            state="NEUTRAL",
            score=0.0,
            contrib=0.0,
            reason="Analysis failed",
        )

        result = decide_long(integration_context)

        # Health gate should block
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "critical module" in result.reasons[0].lower()
        assert result.metrics["failed_health_gate"] == "weekly_tails"


def test_pipeline_confidence_threshold_enforcement(integration_context):
    """Test pipeline enforces confidence threshold correctly."""

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Configure low confidence scenario
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK", state="LONG", score=0.5, contrib=0.30, reason="Moderate tail"
        )
        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK", state="NEUTRAL", score=0.4, contrib=0.04, reason="Weak trend"
        )
        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK", state="HOLD", score=0.3, contrib=0.06, reason="Neutral fib"
        )
        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK", state="DOWN", score=0.3, contrib=0.03, reason="Below MA"
        )

        result = decide_long(integration_context)

        # Should enforce confidence threshold
        assert result.signal == "HOLD"
        assert result.confidence < 0.85
        assert "below threshold" in result.reasons[0].lower()


def test_pipeline_partial_module_failures(integration_context):
    """Test pipeline handles partial module failures correctly."""

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Mix of success and failures
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK",
            state="LONG",
            score=1.0,
            contrib=0.60,
            reason="Very strong tail",
        )
        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="ERROR",
            state="NEUTRAL",
            score=0.0,
            contrib=0.0,
            reason="Trend error",
        )
        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK", state="HOLD", score=0.8, contrib=0.16, reason="Good fib level"
        )
        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="DISABLED", state="NEUTRAL", score=0.0, contrib=0.0, reason="No data"
        )

        result = decide_long(integration_context)

        # Should handle partial failures
        assert result.signal in ["LONG", "HOLD"]  # Depends on total confidence
        assert len(result.metrics["module_results"]) == 4  # All modules tracked

        # Count OK modules from module_results
        ok_modules = [
            m
            for m, data in result.metrics["module_results"].items()
            if data["status"] == "OK"
        ]
        assert len(ok_modules) == 2  # weekly_tails and fibonacci are OK


def test_pipeline_exception_safety(integration_context):
    """Test pipeline handles exceptions safely."""

    # Mock analyzer to raise exception
    with patch(
        "bnb_trading.signals.decision.WeeklyTailsAnalyzer",
        side_effect=Exception("Module initialization failed"),
    ):
        result = decide_long(integration_context)

        # Should fail safely
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "error" in result.reasons[0].lower()


def test_pipeline_configurable_thresholds(integration_context):
    """Test pipeline respects configurable thresholds."""

    # Lower confidence threshold
    integration_context.config["signals"]["thresholds"]["confidence_min"] = 0.50

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.PatternTrendAnalyzer") as mock_trend,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
        patch("bnb_trading.signals.decision.MovingAveragesAnalyzer") as mock_ma,
    ):
        # Medium confidence that meets lowered threshold
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK", state="LONG", score=0.6, contrib=0.36, reason="Medium tail"
        )
        mock_trend.return_value.analyze.return_value = ModuleResult(
            status="OK", state="UP", score=0.5, contrib=0.05, reason="Weak trend"
        )
        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="OK", state="HOLD", score=0.4, contrib=0.08, reason="Neutral fib"
        )
        mock_ma.return_value.analyze_with_module_result.return_value = ModuleResult(
            status="OK", state="UP", score=0.3, contrib=0.03, reason="Slightly above"
        )

        result = decide_long(integration_context)

        # Should pass with lowered threshold
        assert result.signal == "LONG"
        assert result.confidence >= 0.50
        assert result.metrics["threshold"] == 0.50


def test_pipeline_critical_modules_configuration(integration_context):
    """Test pipeline respects critical modules configuration."""

    # Add fibonacci as critical module
    integration_context.config["signals"]["critical_modules"] = [
        "weekly_tails",
        "fibonacci",
    ]

    with (
        patch("bnb_trading.signals.decision.WeeklyTailsAnalyzer") as mock_tails,
        patch("bnb_trading.signals.decision.FibonacciAnalyzer") as mock_fib,
    ):
        # Weekly tails OK, but fibonacci not healthy
        mock_tails.return_value.analyze.return_value = ModuleResult(
            status="OK", state="LONG", score=1.0, contrib=0.60, reason="Strong tail"
        )
        mock_fib.return_value.analyze.return_value = ModuleResult(
            status="ERROR", state="NEUTRAL", score=0.0, contrib=0.0, reason="Fib error"
        )

        result = decide_long(integration_context)

        # Should fail due to fibonacci being critical but unhealthy
        assert result.signal == "HOLD"
        assert result.confidence == 0.0
        assert "critical module fibonacci" in result.reasons[0].lower()
        assert result.metrics["failed_health_gate"] == "fibonacci"


def test_data_context_validation(test_config):
    """Test decision context validation works correctly."""

    # Create context with missing data
    empty_daily = pd.DataFrame()
    empty_weekly = pd.DataFrame()

    context = DecisionContext(
        closed_daily_df=empty_daily,
        closed_weekly_df=empty_weekly,
        config=test_config,
        timestamp=pd.Timestamp.now(),
    )

    # Should handle empty data gracefully
    result = decide_long(context)
    assert isinstance(result.signal, str)
    assert isinstance(result.confidence, (int, float))
    assert isinstance(result.reasons, list)
