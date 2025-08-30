"""
Volume and ATR Guards for LONG Signal Filtering
Simple but effective filters to improve LONG precision ≥85%
"""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def volume_liquidity_filter(
    ctx_data: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """
    Volume liquidity filter for LONG signals

    Args:
        ctx_data: Context data with OHLCV DataFrames
        config: Configuration dictionary

    Returns:
        Dict with filter results and confidence adjustments
    """
    try:
        daily_df = ctx_data.get("closed_daily_df")
        if daily_df is None or len(daily_df) < 20:
            return {
                "passed": False,
                "reason": "Insufficient daily data for volume filter",
                "confidence_multiplier": 0.0,
            }

        # Get volume data
        volume_col = "volume" if "volume" in daily_df.columns else "Volume"
        if volume_col not in daily_df.columns:
            return {
                "passed": False,
                "reason": "No volume data available",
                "confidence_multiplier": 0.0,
            }

        volume = daily_df[volume_col]
        current_volume = float(volume.iloc[-1])

        # Calculate volume MA20
        volume_ma20 = float(volume.rolling(window=20).mean().iloc[-1])

        if volume_ma20 <= 0:
            return {
                "passed": False,
                "reason": "Invalid volume MA20",
                "confidence_multiplier": 0.0,
            }

        # Volume ratio threshold from config
        config.get("signals", {}).get("volume_weight", 0.10)
        required_ratio = 1.3  # 30% above average

        volume_ratio = current_volume / volume_ma20

        # Filter logic
        if volume_ratio >= required_ratio:
            confidence_boost = min((volume_ratio - 1.0) * 0.5, 0.3)  # Max 30% boost
            return {
                "passed": True,
                "reason": f"Volume {volume_ratio:.2f}x MA20 (≥{required_ratio:.1f}x)",
                "confidence_multiplier": 1.0 + confidence_boost,
                "volume_ratio": volume_ratio,
            }
        return {
            "passed": False,
            "reason": f"Volume {volume_ratio:.2f}x MA20 (<{required_ratio:.1f}x)",
            "confidence_multiplier": 0.7,  # Penalty but not complete block
            "volume_ratio": volume_ratio,
        }

    except Exception as e:
        logger.exception(f"Error in volume liquidity filter: {e}")
        return {
            "passed": False,
            "reason": f"Volume filter error: {e}",
            "confidence_multiplier": 0.0,
        }


def atr_chop_guard(ctx_data: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """
    ATR chop filter to avoid signals in low volatility periods

    Args:
        ctx_data: Context data with OHLCV DataFrames
        config: Configuration dictionary

    Returns:
        Dict with filter results and confidence adjustments
    """
    try:
        daily_df = ctx_data.get("closed_daily_df")
        if daily_df is None or len(daily_df) < 14:
            return {
                "passed": False,
                "reason": "Insufficient daily data for ATR filter",
                "confidence_multiplier": 0.0,
            }

        # Calculate ATR(14)
        atr = _calculate_atr(daily_df, 14)
        if atr <= 0:
            return {
                "passed": False,
                "reason": "Invalid ATR calculation",
                "confidence_multiplier": 0.0,
            }

        # Get current price for percentage calculation
        close_col = "close" if "close" in daily_df.columns else "Close"
        current_price = float(daily_df[close_col].iloc[-1])

        # ATR as percentage of price
        atr_pct = atr / current_price

        # Minimum volatility threshold (configurable)
        min_atr_pct = (
            config.get("weekly_tails", {}).get("atr_period", 14) * 0.001
        )  # Default: 1.4%
        min_atr_pct = 0.02  # Fixed 2% minimum volatility

        # Filter logic
        if atr_pct >= min_atr_pct:
            volatility_boost = min((atr_pct - min_atr_pct) * 2.0, 0.2)  # Max 20% boost
            return {
                "passed": True,
                "reason": f"ATR {atr_pct:.2%} ≥ {min_atr_pct:.2%} (good volatility)",
                "confidence_multiplier": 1.0 + volatility_boost,
                "atr_pct": atr_pct,
            }
        return {
            "passed": False,
            "reason": f"ATR {atr_pct:.2%} < {min_atr_pct:.2%} (low volatility)",
            "confidence_multiplier": 0.8,  # Penalty for choppy markets
            "atr_pct": atr_pct,
        }

    except Exception as e:
        logger.exception(f"Error in ATR chop guard: {e}")
        return {
            "passed": False,
            "reason": f"ATR filter error: {e}",
            "confidence_multiplier": 0.0,
        }


def apply_all_guards(
    ctx_data: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """
    Apply all signal guards and return combined result

    Args:
        ctx_data: Context data with OHLCV DataFrames
        config: Configuration dictionary

    Returns:
        Dict with combined filter results
    """
    try:
        # Apply individual filters
        volume_result = volume_liquidity_filter(ctx_data, config)
        atr_result = atr_chop_guard(ctx_data, config)

        # Combine results
        all_passed = volume_result.get("passed", False) and atr_result.get(
            "passed", False
        )

        # Calculate combined confidence multiplier
        volume_mult = volume_result.get("confidence_multiplier", 1.0)
        atr_mult = atr_result.get("confidence_multiplier", 1.0)
        combined_mult = volume_mult * atr_mult

        # Build reasons list
        reasons = []
        if volume_result.get("reason"):
            reasons.append(f"Volume: {volume_result['reason']}")
        if atr_result.get("reason"):
            reasons.append(f"ATR: {atr_result['reason']}")

        return {
            "passed": all_passed,
            "confidence_multiplier": combined_mult,
            "reasons": reasons,
            "filters": {"volume": volume_result, "atr": atr_result},
        }

    except Exception as e:
        logger.exception(f"Error applying signal guards: {e}")
        return {
            "passed": False,
            "confidence_multiplier": 0.0,
            "reasons": [f"Guards error: {e}"],
            "filters": {},
        }


def _calculate_atr(df: pd.DataFrame, period: int) -> float:
    """Calculate Average True Range"""
    try:
        if len(df) < period:
            return 0.0

        # Get OHLC columns (handle different naming conventions)
        high_col = "high" if "high" in df.columns else "High"
        low_col = "low" if "low" in df.columns else "Low"
        close_col = "close" if "close" in df.columns else "Close"

        high = df[high_col]
        low = df[low_col]
        close = df[close_col]

        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]

        return float(atr) if not pd.isna(atr) else 0.0

    except Exception as e:
        logger.exception(f"Error calculating ATR: {e}")
        return 0.0
