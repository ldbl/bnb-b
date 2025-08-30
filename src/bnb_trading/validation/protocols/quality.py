"""Quality scoring for validation results."""

import logging
from typing import Any

from bnb_trading.core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


def calculate_quality_score(validation_results: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate overall quality score based on validation results.

    Args:
        validation_results: Results from validation protocol

    Returns:
        Quality score and breakdown
    """
    try:
        if not validation_results:
            return _get_empty_quality_score()

        total_points = validation_results.get("total_points", 0)
        passed_points = validation_results.get("passed_points", 0)
        critical_failures = validation_results.get("critical_failures", 0)

        # Base quality score
        base_score = (passed_points / total_points) if total_points > 0 else 0.0

        # Critical failure penalty
        critical_penalty = critical_failures * 0.3

        # Final quality score
        quality_score = max(0.0, base_score - critical_penalty)

        # Quality grade
        quality_grade = _calculate_quality_grade(quality_score)

        # Deployment readiness
        deployment_ready = critical_failures == 0 and quality_score >= 0.8

        return {
            "quality_score": quality_score,
            "quality_grade": quality_grade,
            "base_score": base_score,
            "critical_penalty": critical_penalty,
            "deployment_ready": deployment_ready,
            "total_points": total_points,
            "passed_points": passed_points,
            "critical_failures": critical_failures,
            "recommendations": _generate_recommendations(validation_results),
        }

    except Exception as e:
        logger.exception(f"Error calculating quality score: {e}")
        raise AnalysisError(f"Quality score calculation failed: {e}") from e


def _calculate_quality_grade(score: float) -> str:
    """Calculate quality grade based on score."""
    if score >= 0.9:
        return "A+"
    if score >= 0.8:
        return "A"
    if score >= 0.7:
        return "B"
    if score >= 0.6:
        return "C"
    if score >= 0.5:
        return "D"
    return "F"


def _generate_recommendations(validation_results: dict[str, Any]) -> list[str]:
    """Generate improvement recommendations based on validation results."""
    recommendations = []

    try:
        results = validation_results.get("results", {})

        for point_name, point_result in results.items():
            if not point_result.get("passed", True):
                if "accuracy" in point_name:
                    recommendations.append(
                        "Review signal generation logic for accuracy improvements"
                    )
                elif "pnl" in point_name:
                    recommendations.append(
                        "Analyze P&L regression and optimize signal quality"
                    )
                elif "drawdown" in point_name:
                    recommendations.append("Implement better risk management controls")
                elif "performance" in point_name:
                    recommendations.append(
                        "Optimize algorithm performance and reduce computational overhead"
                    )

    except Exception as e:
        logger.exception(f"Error generating recommendations: {e}")

    return recommendations


def _get_empty_quality_score() -> dict[str, Any]:
    """Return empty quality score structure."""
    return {
        "quality_score": 0.0,
        "quality_grade": "F",
        "base_score": 0.0,
        "critical_penalty": 0.0,
        "deployment_ready": False,
        "total_points": 0,
        "passed_points": 0,
        "critical_failures": 0,
        "recommendations": ["No validation data available"],
    }
