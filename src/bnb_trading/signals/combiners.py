"""Signal combination logic for BNB Trading System."""

import logging
from typing import Any

from bnb_trading.core.constants import SIGNAL_HOLD, SIGNAL_LONG, SIGNAL_SHORT
from bnb_trading.core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


def combine_signals(
    analyses: dict[str, Any],
    weights: dict[str, float],
    confidence_threshold: float = 0.3,
) -> dict[str, Any]:
    """
    Combine multiple analysis results into a single signal using weighted scoring.

    Args:
        analyses: Dictionary of analysis results from various modules
        weights: Weight configuration for each analysis type

    Returns:
        Combined signal with overall direction and strength
    """
    try:
        if not analyses:
            return {
                "signal": SIGNAL_HOLD,
                "strength": 0.0,
                "reasons": ["No analysis results available"],
                "score_breakdown": {},
            }

        long_score = 0.0
        short_score = 0.0
        total_weight = 0.0
        reasons = []
        score_breakdown = {}

        # Process each analysis result
        for analysis_name, analysis_result in analyses.items():
            if analysis_result is None or not isinstance(analysis_result, dict):
                continue

            weight = weights.get(analysis_name, 0.0)
            if weight == 0.0:
                continue

            signal = analysis_result.get("signal", SIGNAL_HOLD)
            strength = analysis_result.get("strength", 0.0)

            # Apply weighted scoring
            weighted_strength = strength * weight

            if signal == SIGNAL_LONG:
                long_score += weighted_strength
                reasons.append(f"{analysis_name}: LONG ({strength:.2f})")
            elif signal == SIGNAL_SHORT:
                short_score += weighted_strength
                reasons.append(f"{analysis_name}: SHORT ({strength:.2f})")
            else:
                reasons.append(f"{analysis_name}: HOLD ({strength:.2f})")

            score_breakdown[analysis_name] = {
                "signal": signal,
                "strength": strength,
                "weight": weight,
                "weighted_score": weighted_strength,
            }

            total_weight += weight

        # Determine final signal
        final_signal = _determine_final_signal(
            long_score, short_score, total_weight, confidence_threshold
        )

        # Debug logging
        logger.info(
            f"Signal combination: LONG={long_score:.3f}, SHORT={short_score:.3f}, Total_weight={total_weight:.3f}"
        )
        logger.info(
            f"Normalized: LONG={long_score / total_weight if total_weight > 0 else 0:.3f}, threshold={confidence_threshold}"
        )
        logger.info(
            f"Final signal: {final_signal['signal']} (strength: {final_signal['strength']:.3f})"
        )

        return {
            "signal": final_signal["signal"],
            "strength": final_signal["strength"],
            "reasons": reasons,
            "score_breakdown": score_breakdown,
            "long_score": long_score,
            "short_score": short_score,
            "total_weight": total_weight,
        }

    except Exception as e:
        logger.exception(f"Грешка при combining signals: {e}")
        raise AnalysisError(f"Signal combination failed: {e}") from e


def _determine_final_signal(
    long_score: float,
    short_score: float,
    total_weight: float,
    confidence_threshold: float = 0.3,
) -> dict[str, Any]:
    """Determine final signal based on long/short scores."""

    if total_weight == 0:
        return {"signal": SIGNAL_HOLD, "strength": 0.0}

    # Normalize scores
    normalized_long = long_score / total_weight
    normalized_short = short_score / total_weight

    # Determine signal with configurable threshold
    min_threshold = confidence_threshold

    if normalized_long > normalized_short and normalized_long > min_threshold:
        return {"signal": SIGNAL_LONG, "strength": normalized_long}
    if normalized_short > normalized_long and normalized_short > min_threshold:
        return {"signal": SIGNAL_SHORT, "strength": normalized_short}
    return {
        "signal": SIGNAL_HOLD,
        "strength": max(normalized_long, normalized_short),
    }
