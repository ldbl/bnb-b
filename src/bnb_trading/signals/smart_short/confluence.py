"""Confluence validation logic for smart SHORT signals."""

import logging
from typing import Any

import pandas as pd

from ...core.exceptions import AnalysisError
from ...core.models import ShortSignalCandidate

logger = logging.getLogger(__name__)


def validate_short_confluence(
    setup: dict[str, Any],
    daily_df: pd.DataFrame,
    weekly_df: pd.DataFrame | None,
    market_regime: dict[str, Any],
) -> ShortSignalCandidate | None:
    """
    SIMPLIFIED 3-Layer Validation за SHORT setup:

    1. ATH Proximity Check (basic safety)
    2. Basic Technical Check (RSI overbought)
    3. Risk/Reward Assessment (minimum protection)
    """

    try:
        reasons = []
        confluence_score = 0

        # Layer 1: ATH Proximity Check (basic safety)
        current_price = setup["price"]
        ath_price = daily_df["ATH"].max()
        ath_distance_pct = ((ath_price - current_price) / ath_price) * 100

        if ath_distance_pct > 40.0:  # Simple check - don't SHORT too far from ATH
            return None

        reasons.append(f"ATH distance: {ath_distance_pct:.1f}%")
        confluence_score += 1

        # Layer 2: Basic Technical Check (RSI overbought only)
        if "RSI" in daily_df.columns and daily_df["RSI"].iloc[setup["index"]] > 70:
            reasons.append("RSI overbought")
            confluence_score += 1

        # Layer 3: Risk/Reward Assessment (minimum 1:1.5)
        risk_reward = _calculate_risk_reward(setup["price"], daily_df, setup["index"])
        if risk_reward < 1.5:  # Minimum risk/reward
            return None

        reasons.append(f"Risk/Reward: 1:{risk_reward:.1f}")
        confluence_score += 1

        # Simple confidence calculation (much more permissive)
        confidence = min(0.85, confluence_score / 3.0 * market_regime["confidence"])

        # Calculate stop loss and take profit
        stop_loss_price = setup["price"] * 1.05  # Simple 5% stop loss
        take_profit_price = setup["price"] * (1 - (risk_reward * 0.05))

        return ShortSignalCandidate(
            timestamp=setup["timestamp"],
            price=setup["price"],
            confidence=confidence,
            reasons=reasons,
            confluence_score=confluence_score,
            risk_reward_ratio=risk_reward,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            market_regime=market_regime["regime"],
            ath_distance_pct=ath_distance_pct,
        )

    except Exception as e:
        logger.exception(f"Грешка при SHORT setup validation: {e}")
        raise AnalysisError(f"Short confluence validation failed: {e}") from e


def check_volume_divergence(df: pd.DataFrame, index: int) -> bool:
    """Проверява за bearish volume divergence"""
    try:
        lookback = 10

        if index < lookback:
            return False

        # Check if volume column exists
        if "Volume" not in df.columns and "volume" not in df.columns:
            return False

        volume_col = "Volume" if "Volume" in df.columns else "volume"
        price_window = df["Close"].iloc[index - lookback : index + 1]
        volume_window = df[volume_col].iloc[index - lookback : index + 1]

        if len(price_window) < lookback or len(volume_window) < lookback:
            return False

        # Look for price making higher highs while volume makes lower highs
        price_trend = price_window.tail(5).mean() > price_window.head(5).mean()
        volume_trend = volume_window.tail(5).mean() < volume_window.head(5).mean()

        return price_trend and volume_trend

    except Exception as e:
        logger.exception(f"Грешка при volume divergence check: {e}")
        return False


def _calculate_risk_reward(price: float, df: pd.DataFrame, index: int) -> float:
    """Изчислява risk/reward ratio за SHORT позиция"""
    try:
        # Simple support/resistance calculation
        lookback = 20

        if index < lookback:
            return 1.0

        # Find recent support level
        support_window = df["Low"].iloc[index - lookback : index + 1]
        support_level = float(support_window.min())

        # Potential profit to support
        potential_profit = (price - support_level) / price

        # Risk (5% stop loss)
        risk = 0.05

        # Risk/reward ratio
        if risk == 0:
            return 1.0

        return potential_profit / risk

    except Exception as e:
        logger.exception(f"Грешка при risk/reward calculation: {e}")
        return 1.0
