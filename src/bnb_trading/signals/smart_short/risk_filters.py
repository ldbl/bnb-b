"""Risk management filters for smart SHORT signals."""

import logging
from typing import Any

from bnb_trading.core.constants import (
    ATH_PROXIMITY_MAX,
    ATH_PROXIMITY_MIN,
    DEFAULT_STOP_LOSS_PCT,
    MIN_RISK_REWARD_RATIO,
)
from bnb_trading.core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


def apply_risk_filters(
    signal: dict[str, Any], market_data: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """
    Apply comprehensive risk filters to SHORT signal.

    Args:
        signal: SHORT signal candidate
        market_data: Market data context
        config: Risk management configuration

    Returns:
        Updated signal with risk filters applied
    """
    try:
        # ATH proximity filter
        ath_distance_pct = signal.get("ath_distance_pct", 0)

        if not _is_ath_distance_acceptable(ath_distance_pct, config):
            signal["blocked"] = True
            signal["block_reason"] = (
                f"ATH distance {ath_distance_pct:.1f}% outside acceptable range"
            )
            return signal

        # Risk/reward filter
        risk_reward = signal.get("risk_reward_ratio", 0)
        min_rr = config.get("min_risk_reward_ratio", MIN_RISK_REWARD_RATIO)

        if risk_reward < min_rr:
            signal["blocked"] = True
            signal["block_reason"] = (
                f"Risk/reward {risk_reward:.1f} below minimum {min_rr}"
            )
            return signal

        # Market regime filter
        market_regime = market_data.get("market_regime", {})
        if not market_regime.get("short_signals_allowed", False):
            signal["blocked"] = True
            signal["block_reason"] = (
                f"SHORT signals blocked in {market_regime.get('regime', 'unknown')} market"
            )
            return signal

        # Volume filter
        if not _has_sufficient_volume(market_data, config):
            signal["blocked"] = True
            signal["block_reason"] = "Insufficient volume for SHORT entry"
            return signal

        signal["blocked"] = False
        return signal

    except Exception as e:
        logger.exception(f"Грешка при risk filter application: {e}")
        raise AnalysisError(f"Risk filter application failed: {e}") from e


def calculate_stop_loss_take_profit(
    entry_price: float,
    risk_reward_ratio: float,
    max_stop_loss_pct: float = DEFAULT_STOP_LOSS_PCT,
) -> dict[str, float]:
    """
    Calculate stop loss and take profit levels for SHORT position.

    Args:
        entry_price: Entry price for SHORT
        risk_reward_ratio: Target risk/reward ratio
        max_stop_loss_pct: Maximum stop loss percentage

    Returns:
        Dict with stop_loss_price and take_profit_price
    """
    try:
        # Calculate stop loss (above entry for SHORT)
        stop_loss_pct = min(max_stop_loss_pct, 0.05)  # Max 5% stop loss
        stop_loss_price = entry_price * (1 + stop_loss_pct)

        # Calculate take profit (below entry for SHORT)
        take_profit_pct = stop_loss_pct * risk_reward_ratio
        take_profit_price = entry_price * (1 - take_profit_pct)

        return {
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct,
        }

    except Exception as e:
        logger.exception(f"Грешка при SL/TP calculation: {e}")
        return {
            "stop_loss_price": entry_price * 1.05,
            "take_profit_price": entry_price * 0.95,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.05,
        }


def _is_ath_distance_acceptable(
    ath_distance_pct: float, config: dict[str, Any]
) -> bool:
    """Check if ATH distance is within acceptable range for SHORT."""
    min_distance = float(config.get("min_ath_distance_pct", ATH_PROXIMITY_MIN * 100))
    max_distance = float(config.get("max_ath_distance_pct", ATH_PROXIMITY_MAX * 100))

    return min_distance <= ath_distance_pct <= max_distance


def _has_sufficient_volume(market_data: dict[str, Any], config: dict[str, Any]) -> bool:
    """Check if volume is sufficient for SHORT entry."""
    try:
        current_volume = float(market_data.get("current_volume", 0))
        avg_volume = float(market_data.get("avg_volume_20d", 0))

        min_volume_ratio = float(config.get("min_volume_ratio", 0.8))

        if avg_volume == 0:
            return True  # Can't validate, allow through

        volume_ratio = current_volume / avg_volume
        return volume_ratio >= min_volume_ratio

    except Exception as e:
        logger.exception(f"Грешка при volume check: {e}")
        return True  # Default to allow
