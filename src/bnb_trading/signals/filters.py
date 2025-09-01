"""Signal filtering logic for BNB Trading System."""

import logging
from typing import Any

from bnb_trading.core.constants import SIGNAL_HOLD, SIGNAL_LONG, SIGNAL_SHORT
from bnb_trading.core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


def apply_signal_filters(
    signal: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """
    Apply comprehensive filters to trading signal.

    Args:
        signal: Signal to filter
        config: System configuration

    Returns:
        Filtered signal
    """
    try:
        filtered_signal = signal.copy()

        # Confidence threshold filter
        confidence = signal.get("strength", 0.0)
        confidence_threshold = config.get("signals", {}).get(
            "confidence_threshold", 0.8
        )

        if confidence < confidence_threshold:
            filtered_signal["signal"] = SIGNAL_HOLD
            filtered_signal["filter_reason"] = (
                f"Confidence {confidence:.2f} below threshold {confidence_threshold}"
            )
            return filtered_signal

        # Minimum confirmations filter
        confirmations = _count_signal_confirmations(signal)
        min_confirmations = config.get("signals", {}).get("min_confirmations", 1)

        if confirmations < min_confirmations:
            filtered_signal["signal"] = SIGNAL_HOLD
            filtered_signal["filter_reason"] = (
                f"Only {confirmations} confirmations, need {min_confirmations}"
            )
            return filtered_signal

        # Market regime filter for SHORT signals
        if signal.get("signal") == SIGNAL_SHORT:
            filtered_signal = _apply_short_market_filters(filtered_signal, config)

        # LONG signal enhancement filters
        elif signal.get("signal") == SIGNAL_LONG:
            filtered_signal = _apply_long_enhancement_filters(filtered_signal, config)

        return filtered_signal

    except Exception as e:
        logger.exception(f"Грешка при signal filtering: {e}")
        raise AnalysisError(f"Signal filtering failed: {e}") from e


def _count_signal_confirmations(signal: dict[str, Any]) -> int:
    """Count number of confirmations for a signal."""
    score_breakdown = signal.get("score_breakdown", {})
    target_signal = signal.get("signal", SIGNAL_HOLD)

    confirmations = 0
    for analysis in score_breakdown.values():
        if isinstance(analysis, dict) and analysis.get("signal") == target_signal:
            confirmations += 1

    return confirmations


def _apply_short_market_filters(
    signal: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """Apply market regime filters for SHORT signals."""

    # Check if SHORT signals are enabled in current market regime
    smart_short_config = config.get("smart_short", {})

    if smart_short_config.get("bull_market_block", True):
        # This would need market regime detection
        # For now, keep signal as is
        pass

    return signal


def _apply_long_enhancement_filters(
    signal: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """Apply enhancement filters for LONG signals."""

    # LONG signal quality filters
    long_config = config.get("long_signals", {})

    # EMA confirmation filter
    if long_config.get("ema_confirmation", True):
        # Would check EMA alignment here
        pass

    # Volume confirmation filter
    if long_config.get("volume_confirmation_enabled", True):
        # Would check volume confirmation here
        pass

    return signal
