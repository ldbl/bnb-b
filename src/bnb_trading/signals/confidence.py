"""Confidence calculation for trading signals."""

import logging
from typing import Any

from ..core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


def calculate_confidence(signal: dict[str, Any], analyses: dict[str, Any]) -> float:
    """
    Calculate overall confidence score for a trading signal.

    Args:
        signal: Combined signal result
        analyses: Individual analysis results

    Returns:
        Confidence score between 0.0 and 1.0
    """
    try:
        if not signal or signal.get("signal") == "HOLD":
            return 0.0

        base_strength = float(signal.get("strength", 0.0))

        # Count confirmations
        target_signal = signal.get("signal", "HOLD")
        confirmations = _count_confirmations(analyses, target_signal)

        # Calculate confluence bonus
        confluence_bonus = _calculate_confluence_bonus(analyses, target_signal)

        # Calculate volume confirmation bonus
        volume_bonus = _calculate_volume_bonus(analyses)

        # Calculate timeframe alignment bonus
        timeframe_bonus = _calculate_timeframe_bonus(analyses)

        # Combine all factors
        total_confidence = (
            base_strength + confluence_bonus + volume_bonus + timeframe_bonus
        )

        # Apply confirmation penalty if insufficient
        min_confirmations = 2
        if confirmations < min_confirmations:
            confirmation_penalty = (min_confirmations - confirmations) * 0.1
            total_confidence -= confirmation_penalty

        # Clamp between 0 and 1
        return max(0.0, min(1.0, total_confidence))

    except Exception as e:
        logger.exception(f"Грешка при confidence calculation: {e}")
        raise AnalysisError(f"Confidence calculation failed: {e}") from e


def _count_confirmations(analyses: dict[str, Any], target_signal: str) -> int:
    """Count number of analyses confirming the target signal."""
    confirmations = 0

    for analysis in analyses.values():
        if isinstance(analysis, dict) and analysis.get("signal") == target_signal:
            confirmations += 1

    return confirmations


def _calculate_confluence_bonus(analyses: dict[str, Any], target_signal: str) -> float:
    """Calculate bonus for multiple analyses agreeing."""

    # Key confluence combinations
    fibonacci_agrees = analyses.get("fibonacci", {}).get("signal") == target_signal
    weekly_tails_agrees = (
        analyses.get("weekly_tails", {}).get("signal") == target_signal
    )
    trend_agrees = analyses.get("trend", {}).get("signal") == target_signal

    bonus = 0.0

    # Fibonacci + Weekly Tails = strong confluence
    if fibonacci_agrees and weekly_tails_agrees:
        bonus += 0.15

    # Trend + any other = trend confirmation
    if trend_agrees and (fibonacci_agrees or weekly_tails_agrees):
        bonus += 0.10

    return bonus


def _calculate_volume_bonus(analyses: dict[str, Any]) -> float:
    """Calculate volume confirmation bonus."""

    volume_analysis = analyses.get("indicators", {})
    if not isinstance(volume_analysis, dict):
        return 0.0

    volume_signal = volume_analysis.get("volume_signal")
    if volume_signal == "STRONG":
        return 0.05
    if volume_signal == "MODERATE":
        return 0.03

    return 0.0


def _calculate_timeframe_bonus(analyses: dict[str, Any]) -> float:
    """Calculate multi-timeframe alignment bonus."""

    multi_tf_analysis = analyses.get("multi_timeframe", {})
    if not isinstance(multi_tf_analysis, dict):
        return 0.0

    alignment_score = float(multi_tf_analysis.get("alignment_score", 0.0))

    # Bonus based on alignment quality
    if alignment_score > 0.8:
        return 0.10
    if alignment_score > 0.6:
        return 0.05

    return 0.0
