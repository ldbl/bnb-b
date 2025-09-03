"""Historical test result analysis."""

import logging
from typing import Any

from bnb_trading.core.exceptions import AnalysisError
from bnb_trading.core.models import BaselineMetrics, TestResult

logger = logging.getLogger(__name__)


def analyze_test_results(
    results: list[TestResult], baseline: BaselineMetrics
) -> dict[str, Any]:
    """
    Analyze historical test results against baseline.

    Args:
        results: List of test results from different periods
        baseline: Baseline metrics for comparison

    Returns:
        Comprehensive analysis of test performance
    """
    try:
        if not results:
            return _get_empty_analysis()

        # Aggregate metrics
        total_signals = sum(r.total_signals for r in results)
        total_long = sum(r.long_signals for r in results)
        total_short = sum(r.short_signals for r in results)

        # Weighted averages
        overall_accuracy = _calculate_weighted_accuracy(results)
        long_accuracy = _calculate_weighted_long_accuracy(results)
        short_accuracy = _calculate_weighted_short_accuracy(results)

        # Performance analysis
        total_pnl = sum(r.total_pnl for r in results)
        avg_sharpe = sum(r.sharpe_ratio for r in results) / len(results)
        max_drawdown = max(r.max_drawdown for r in results)

        # Comparison with baseline
        long_vs_baseline = long_accuracy - baseline.long_accuracy
        short_vs_baseline = short_accuracy - baseline.short_accuracy

        # Period-by-period analysis
        period_analysis = _analyze_by_period(results)

        return {
            "summary": {
                "total_signals": total_signals,
                "total_long": total_long,
                "total_short": total_short,
                "overall_accuracy": overall_accuracy,
                "long_accuracy": long_accuracy,
                "short_accuracy": short_accuracy,
                "total_pnl": total_pnl,
                "avg_sharpe": avg_sharpe,
                "max_drawdown": max_drawdown,
            },
            "baseline_comparison": {
                "long_vs_baseline": long_vs_baseline,
                "short_vs_baseline": short_vs_baseline,
                "long_improved": long_vs_baseline > 0,
                "short_improved": short_vs_baseline > 0,
            },
            "period_analysis": period_analysis,
            "quality_assessment": _assess_quality(results, baseline),
        }

    except Exception as e:
        logger.exception(f"Error analyzing test results: {e}")
        raise AnalysisError(f"Test result analysis failed: {e}") from e


def _calculate_weighted_accuracy(results: list[TestResult]) -> float:
    """Calculate overall weighted accuracy."""
    total_signals = sum(r.total_signals for r in results)
    if total_signals == 0:
        return 0.0

    weighted_sum = sum(r.overall_accuracy * r.total_signals for r in results)
    return weighted_sum / total_signals


def _calculate_weighted_long_accuracy(results: list[TestResult]) -> float:
    """Calculate LONG weighted accuracy."""
    total_long = sum(r.long_signals for r in results)
    if total_long == 0:
        return 0.0

    weighted_sum = sum(r.long_accuracy * r.long_signals for r in results)
    return weighted_sum / total_long


def _calculate_weighted_short_accuracy(results: list[TestResult]) -> float:
    """Calculate SHORT weighted accuracy."""
    total_short = sum(r.short_signals for r in results)
    if total_short == 0:
        return 0.0

    weighted_sum = sum(r.short_accuracy * r.short_signals for r in results)
    return weighted_sum / total_short


def _analyze_by_period(results: list[TestResult]) -> dict[str, dict[str, Any]]:
    """Analyze results by individual periods."""
    period_analysis = {}

    for result in results:
        period_analysis[result.period_name] = {
            "accuracy": result.overall_accuracy,
            "long_accuracy": result.long_accuracy,
            "short_accuracy": result.short_accuracy,
            "pnl": result.total_pnl,
            "signals": result.total_signals,
            "assessment": _assess_period_performance(result),
        }

    return period_analysis


def _assess_period_performance(result: TestResult) -> str:
    """Assess performance for a single period."""
    if result.overall_accuracy >= 80:
        return "EXCELLENT"
    if result.overall_accuracy >= 70:
        return "GOOD"
    if result.overall_accuracy >= 60:
        return "ACCEPTABLE"
    if result.overall_accuracy >= 50:
        return "POOR"
    return "CRITICAL"


def _assess_quality(
    results: list[TestResult], baseline: BaselineMetrics
) -> dict[str, Any]:
    """Assess overall quality of test results."""
    avg_long_acc = _calculate_weighted_long_accuracy(results)
    avg_short_acc = _calculate_weighted_short_accuracy(results)

    quality_issues = []

    # Check for regressions
    if avg_long_acc < baseline.long_accuracy:
        quality_issues.append(
            f"LONG accuracy regression: {avg_long_acc:.1f}% vs {baseline.long_accuracy:.1f}%"
        )

    if avg_short_acc < baseline.short_accuracy:
        quality_issues.append(
            f"SHORT accuracy regression: {avg_short_acc:.1f}% vs {baseline.short_accuracy:.1f}%"
        )

    # Overall assessment
    has_critical_issues = any("regression" in issue for issue in quality_issues)

    return {
        "overall_grade": "PASS" if not has_critical_issues else "FAIL",
        "quality_issues": quality_issues,
        "recommendations": _generate_recommendations(quality_issues),
        "deployment_ready": not has_critical_issues,
    }


def _generate_recommendations(quality_issues: list[str]) -> list[str]:
    """Generate recommendations based on quality issues."""
    recommendations = []

    for issue in quality_issues:
        if "LONG" in issue:
            recommendations.append("Review LONG signal generation logic")
        elif "SHORT" in issue:
            recommendations.append("Enhance SHORT signal filtering")

    return recommendations


def _get_empty_analysis() -> dict[str, Any]:
    """Return empty analysis structure."""
    return {
        "summary": {
            "total_signals": 0,
            "overall_accuracy": 0.0,
            "long_accuracy": 0.0,
            "short_accuracy": 0.0,
        },
        "baseline_comparison": {},
        "period_analysis": {},
        "quality_assessment": {"overall_grade": "NO_DATA"},
    }
