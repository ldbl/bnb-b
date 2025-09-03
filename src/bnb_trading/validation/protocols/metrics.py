"""Performance metrics calculation for validation."""

import logging
from typing import Any

from bnb_trading.core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


def calculate_performance_metrics(results: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate comprehensive performance metrics from test results.

    Args:
        results: Test results data

    Returns:
        Dict with calculated performance metrics
    """
    try:
        if not results:
            return _get_empty_metrics()

        # Basic metrics
        total_signals = results.get("total_signals", 0)
        long_signals = results.get("long_signals", 0)
        short_signals = results.get("short_signals", 0)

        # Accuracy calculations
        long_wins = results.get("long_wins", 0)
        short_wins = results.get("short_wins", 0)
        total_wins = long_wins + short_wins

        long_accuracy = (long_wins / long_signals * 100) if long_signals > 0 else 0.0
        short_accuracy = (
            (short_wins / short_signals * 100) if short_signals > 0 else 0.0
        )
        overall_accuracy = (
            (total_wins / total_signals * 100) if total_signals > 0 else 0.0
        )

        # P&L calculations
        total_pnl = results.get("total_pnl", 0.0)
        avg_pnl_per_trade = total_pnl / total_signals if total_signals > 0 else 0.0

        # Risk metrics
        max_drawdown = results.get("max_drawdown", 0.0)
        sharpe_ratio = results.get("sharpe_ratio", 0.0)

        return {
            "total_signals": total_signals,
            "long_signals": long_signals,
            "short_signals": short_signals,
            "long_accuracy": long_accuracy,
            "short_accuracy": short_accuracy,
            "overall_accuracy": overall_accuracy,
            "total_pnl": total_pnl,
            "avg_pnl_per_trade": avg_pnl_per_trade,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "profit_factor": _calculate_profit_factor(results),
            "win_rate": overall_accuracy / 100.0,
        }

    except Exception as e:
        logger.exception(f"Error calculating performance metrics: {e}")
        raise AnalysisError(f"Performance metrics calculation failed: {e}") from e


def compare_metrics(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    """
    Compare current metrics against baseline.

    Args:
        baseline: Baseline performance metrics
        current: Current performance metrics

    Returns:
        Comparison results with differences and percentages
    """
    try:
        comparison = {}

        for metric_name in [
            "long_accuracy",
            "short_accuracy",
            "overall_accuracy",
            "total_pnl",
            "max_drawdown",
        ]:
            baseline_value = baseline.get(metric_name, 0.0)
            current_value = current.get(metric_name, 0.0)

            # Calculate absolute and percentage difference
            abs_diff = current_value - baseline_value
            pct_diff = (abs_diff / baseline_value * 100) if baseline_value != 0 else 0.0

            comparison[metric_name] = {
                "baseline": baseline_value,
                "current": current_value,
                "abs_difference": abs_diff,
                "pct_difference": pct_diff,
                "improved": abs_diff > 0
                if metric_name != "max_drawdown"
                else abs_diff < 0,
            }

        return comparison

    except Exception as e:
        logger.exception(f"Error comparing metrics: {e}")
        raise AnalysisError(f"Metrics comparison failed: {e}") from e


def _calculate_profit_factor(results: dict[str, Any]) -> float:
    """Calculate profit factor (gross profit / gross loss)."""
    try:
        gross_profit = float(results.get("gross_profit", 0.0))
        gross_loss = float(results.get("gross_loss", 0.0))

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return gross_profit / abs(gross_loss)

    except Exception as e:
        logger.exception(f"Error calculating profit factor: {e}")
        return 0.0


def _get_empty_metrics() -> dict[str, Any]:
    """Return empty metrics structure."""
    return {
        "total_signals": 0,
        "long_signals": 0,
        "short_signals": 0,
        "long_accuracy": 0.0,
        "short_accuracy": 0.0,
        "overall_accuracy": 0.0,
        "total_pnl": 0.0,
        "avg_pnl_per_trade": 0.0,
        "max_drawdown": 0.0,
        "sharpe_ratio": 0.0,
        "profit_factor": 0.0,
        "win_rate": 0.0,
    }
