"""Market regime detection for smart SHORT signals."""

import logging
from typing import Any

import numpy as np
import pandas as pd

from bnb_trading.core.constants import (
    REGIME_BEAR,
    REGIME_MODERATE_BULL,
    REGIME_NEUTRAL,
    REGIME_STRONG_BULL,
)
from bnb_trading.core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    """
    Детектор за пазарни режими - основата за SHORT решения
    """

    def __init__(self) -> None:
        self.regime_thresholds = {
            "STRONG_BULL": {"trend_strength": 2.0, "volume_trend": "increasing"},
            "MODERATE_BULL": {"trend_strength": 1.0, "volume_trend": "stable"},
            "NEUTRAL": {"trend_strength": 0.2, "volume_trend": "any"},
            "MODERATE_BEAR": {"trend_strength": -1.0, "volume_trend": "decreasing"},
            "STRONG_BEAR": {"trend_strength": -2.0, "volume_trend": "decreasing"},
        }

    def detect_market_regime(
        self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame
    ) -> dict[str, Any]:
        """
        Детектира текущия пазарен режим базирано на:
        - Trend strength (daily & weekly)
        - Volume trends
        - ATH proximity
        - RSI levels
        """

        try:
            # Daily trend analysis
            daily_trend = self._calculate_trend_strength(daily_df, "Close", 20)
            daily_volume_trend = self._analyze_volume_trend(daily_df, 20)

            # Weekly trend analysis
            weekly_trend = (
                self._calculate_trend_strength(weekly_df, "Close", 4)
                if weekly_df is not None
                else 0
            )
            weekly_volume_trend = (
                self._analyze_volume_trend(weekly_df, 4)
                if weekly_df is not None
                else "unknown"
            )

            # ATH proximity
            current_price = daily_df["Close"].iloc[-1]
            ath_col = (
                "ATH"
                if "ATH" in daily_df.columns
                else ("High" if "High" in daily_df.columns else "Close")
            )
            ath_price = daily_df[ath_col].max()
            ath_distance_pct = ((ath_price - current_price) / ath_price) * 100

            # RSI levels
            rsi_current = daily_df["RSI"].iloc[-1] if "RSI" in daily_df.columns else 50

            # Determine regime
            regime = self._classify_regime(
                daily_trend,
                weekly_trend,
                daily_volume_trend,
                weekly_volume_trend,
                ath_distance_pct,
                rsi_current,
            )

            return {
                "regime": regime,
                "daily_trend": daily_trend,
                "weekly_trend": weekly_trend,
                "daily_volume_trend": daily_volume_trend,
                "weekly_volume_trend": weekly_volume_trend,
                "ath_distance_pct": ath_distance_pct,
                "rsi_current": rsi_current,
                "short_signals_allowed": self._are_short_signals_allowed(
                    regime, ath_distance_pct
                ),
                "confidence": self._calculate_regime_confidence(
                    daily_trend, weekly_trend
                ),
            }

        except Exception as e:
            logger.exception(f"Грешка при market regime detection: {e}")
            raise AnalysisError(f"Market regime detection failed: {e}") from e

    def _calculate_trend_strength(
        self, df: pd.DataFrame, column: str, lookback: int
    ) -> float:
        """Изчислява сила на тренда (от -3 до +3)"""
        try:
            # Check if column exists with different case
            if column not in df.columns:
                # Try with capitalized first letter
                column = column.capitalize()
                if column not in df.columns:
                    logger.exception(f"Колона {column} не е намерена в DataFrame")
                    return 0.0

            prices = df[column].tail(lookback)
            if len(prices) < lookback:
                return 0.0

            # Linear regression slope normalized
            x = np.arange(len(prices))
            slope = float(np.polyfit(x, prices, 1)[0])

            # Normalize by price volatility
            price_std = float(prices.std())
            if price_std == 0:
                return 0.0

            normalized_slope = slope / price_std

            # Clamp between -3 and +3
            return max(-3.0, min(3.0, normalized_slope))

        except Exception as e:
            logger.exception(f"Грешка при trend strength calculation: {e}")
            return 0.0

    def _analyze_volume_trend(self, df: pd.DataFrame, lookback: int) -> str:
        """Анализира тренда на обема"""
        try:
            if "Volume" not in df.columns and "volume" not in df.columns:
                return "unknown"

            volume_col = "Volume" if "Volume" in df.columns else "volume"
            volumes = df[volume_col].tail(lookback)
            if len(volumes) < lookback:
                return "unknown"

            # Simple trend analysis
            first_half = volumes[: lookback // 2].mean()
            second_half = volumes[lookback // 2 :].mean()

            ratio = second_half / first_half if first_half > 0 else 1.0

            if ratio > 1.2:
                return "increasing"
            if ratio < 0.8:
                return "decreasing"
            return "stable"

        except Exception as e:
            logger.exception(f"Грешка при volume trend analysis: {e}")
            return "unknown"

    def _classify_regime(
        self,
        daily_trend: float,
        weekly_trend: float,
        daily_volume_trend: str,
        weekly_volume_trend: str,
        ath_distance_pct: float,
        rsi_current: float,
    ) -> str:
        """Класифицира пазарния режим"""

        # Weighted trend score (weekly has more weight)
        combined_trend = (daily_trend * 0.4) + (weekly_trend * 0.6)

        # Strong bull market conditions
        if (
            combined_trend > 1.5
            and ath_distance_pct < 15
            and daily_volume_trend in ["increasing", "stable"]
        ):
            return REGIME_STRONG_BULL

        # Moderate bull market
        if combined_trend > 0.5 and ath_distance_pct < 30:
            return REGIME_MODERATE_BULL

        # Bear market
        if combined_trend < -0.5:
            return REGIME_BEAR

        # Default to neutral
        return REGIME_NEUTRAL

    def _are_short_signals_allowed(self, regime: str, ath_distance_pct: float) -> bool:
        """Определя дали SHORT сигналите са позволени"""

        # Block SHORT in strong bull markets
        if regime == REGIME_STRONG_BULL:
            return False

        # Strict filtering in moderate bull
        if regime == REGIME_MODERATE_BULL and ath_distance_pct < 10:
            return False

        return True

    def _calculate_regime_confidence(
        self, daily_trend: float, weekly_trend: float
    ) -> float:
        """Изчислява confidence на regime detection"""

        # Higher confidence when both timeframes agree
        trend_agreement = abs(daily_trend - weekly_trend)
        max_confidence = 1.0 - (trend_agreement / 6.0)  # Max diff is 6 (-3 to +3)

        return max(0.0, min(1.0, max_confidence))
