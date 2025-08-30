"""
Simple Trend Analyzer - HH/HL Logic with EMA Slope Confirmation

Implements clean, straightforward trend detection using:
1. Higher Highs / Higher Lows pattern analysis (20-day lookback)
2. EMA50 vs EMA200 slope confirmation
3. Returns ModuleResult with UP/DOWN/NEUTRAL states
"""

import logging
from typing import Any

import numpy as np
import pandas as pd
import talib

from bnb_trading.core.models import ModuleResult, SignalState

logger = logging.getLogger(__name__)


class PatternTrendAnalyzer:
    """
    Simple trend analyzer using HH/HL logic and moving average confirmation.

    Methodology:
    - Analyzes last 20 days for Higher Highs/Higher Lows patterns
    - UP: ≥2 consecutive Higher Highs AND Higher Lows
    - DOWN: ≥2 consecutive Lower Highs AND Lower Lows
    - NEUTRAL: otherwise
    - Confirms with EMA50 vs EMA200 slope
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize trend analyzer with configuration."""
        trend_config = config.get("trend_analysis", {})

        self.lookback_days = int(trend_config.get("lookback_days", 20))
        self.min_consecutive = int(trend_config.get("min_consecutive_patterns", 2))
        self.weight = float(trend_config.get("weight", 0.10))

        logger.info(
            f"PatternTrendAnalyzer initialized: lookback={self.lookback_days}, weight={self.weight}"
        )

    def analyze(self, daily_df: pd.DataFrame) -> ModuleResult:
        """
        Analyze trend using HH/HL logic with EMA confirmation.

        Args:
            daily_df: Daily OHLCV data

        Returns:
            ModuleResult with UP/DOWN/NEUTRAL state and contribution
        """
        try:
            if len(daily_df) < self.lookback_days + 50:  # Need extra for EMAs
                return ModuleResult(
                    status="DISABLED",
                    state="NEUTRAL",
                    score=0.0,
                    contrib=0.0,
                    reason="Insufficient data for trend analysis",
                    meta={
                        "required_days": self.lookback_days + 50,
                        "available": len(daily_df),
                    },
                )

            # 1. HH/HL Pattern Analysis
            hh_hl_result = self._analyze_hh_hl_patterns(daily_df)

            # 2. EMA Slope Analysis
            ema_result = self._analyze_ema_slope(daily_df)

            # 3. Combine results
            final_state, final_score, reason = self._combine_signals(
                hh_hl_result, ema_result
            )

            return ModuleResult(
                status="OK",
                state=final_state,
                score=final_score,
                contrib=final_score * self.weight,
                reason=reason,
                meta={
                    "hh_hl_state": hh_hl_result["state"],
                    "hh_hl_score": hh_hl_result["score"],
                    "max_hh_streak": hh_hl_result.get("max_hh_streak", 0),
                    "max_hl_streak": hh_hl_result.get("max_hl_streak", 0),
                    "max_lh_streak": hh_hl_result.get("max_lh_streak", 0),
                    "max_ll_streak": hh_hl_result.get("max_ll_streak", 0),
                    "ema_state": ema_result["state"],
                    "ema_score": ema_result["score"],
                    "ema_valid_points": ema_result.get("valid_data_points", 0),
                    "lookback_days": self.lookback_days,
                },
            )

        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return ModuleResult(
                status="ERROR",
                state="NEUTRAL",
                score=0.0,
                contrib=0.0,
                reason=f"Analysis failed: {e!s}",
                meta={"error": str(e)},
            )

    def _analyze_hh_hl_patterns(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze Higher Highs/Higher Lows patterns with proper consecutive tracking."""
        recent_data = df.tail(self.lookback_days).copy()

        # Robust NaN handling per project guidelines
        highs = np.nan_to_num(recent_data["High"].values, nan=0.0)
        lows = np.nan_to_num(recent_data["Low"].values, nan=0.0)

        # Filter out zero values (converted NaNs)
        valid_indices = (highs > 0) & (lows > 0)
        if not np.any(valid_indices):
            return {"state": "NEUTRAL", "score": 0.3, "reason": "No valid price data"}

        highs = highs[valid_indices]
        lows = lows[valid_indices]

        if len(highs) < 6:  # Need minimum data for pattern detection
            return {
                "state": "NEUTRAL",
                "score": 0.3,
                "reason": "Insufficient data for patterns",
            }

        # Track consecutive streaks properly
        max_hh_streak = 0
        max_hl_streak = 0
        max_lh_streak = 0
        max_ll_streak = 0

        current_hh_streak = 0
        current_hl_streak = 0
        current_lh_streak = 0
        current_ll_streak = 0

        # Compare consecutive 3-day windows for more robust detection
        window_size = 3
        for i in range(window_size, len(highs)):
            current_high = highs[i]
            previous_high = highs[i - window_size]
            current_low = lows[i]
            previous_low = lows[i - window_size]

            # Track Higher Highs streak
            if current_high > previous_high:
                current_hh_streak += 1
                max_hh_streak = max(max_hh_streak, current_hh_streak)
            else:
                current_hh_streak = 0

            # Track Higher Lows streak
            if current_low > previous_low:
                current_hl_streak += 1
                max_hl_streak = max(max_hl_streak, current_hl_streak)
            else:
                current_hl_streak = 0

            # Track Lower Highs streak
            if current_high < previous_high:
                current_lh_streak += 1
                max_lh_streak = max(max_lh_streak, current_lh_streak)
            else:
                current_lh_streak = 0

            # Track Lower Lows streak
            if current_low < previous_low:
                current_ll_streak += 1
                max_ll_streak = max(max_ll_streak, current_ll_streak)
            else:
                current_ll_streak = 0

        # Determine trend based on CONSECUTIVE patterns (architectural requirement)
        if (
            max_hh_streak >= self.min_consecutive
            and max_hl_streak >= self.min_consecutive
        ):
            state: SignalState = "UP"
            # Score based on streak strength and alignment
            streak_strength = min(max_hh_streak, max_hl_streak)
            score = min(0.8, 0.5 + streak_strength * 0.1)
        elif (
            max_lh_streak >= self.min_consecutive
            and max_ll_streak >= self.min_consecutive
        ):
            state = "DOWN"
            streak_strength = min(max_lh_streak, max_ll_streak)
            score = min(0.8, 0.5 + streak_strength * 0.1)
        else:
            state = "NEUTRAL"
            score = 0.3

        return {
            "state": state,
            "score": score,
            "max_hh_streak": max_hh_streak,
            "max_hl_streak": max_hl_streak,
            "max_lh_streak": max_lh_streak,
            "max_ll_streak": max_ll_streak,
            "data_points": len(highs),
        }

    def _analyze_ema_slope(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze EMA50 vs EMA200 slope with robust NaN handling."""
        try:
            # Robust NaN handling for close prices per project guidelines
            closes = np.nan_to_num(df["Close"].values, nan=0.0)

            # Filter out zero values (converted NaNs)
            valid_closes = closes[closes > 0]
            if len(valid_closes) < 200:  # Need minimum data for EMA200
                return {
                    "state": "NEUTRAL",
                    "score": 0.3,
                    "reason": "Insufficient price data for EMA calculation",
                }

            # Calculate EMAs with cleaned data
            ema50 = talib.EMA(valid_closes, timeperiod=50)
            ema200 = talib.EMA(valid_closes, timeperiod=200)

            # Apply project guideline NaN handling to EMA results
            ema50 = np.nan_to_num(ema50, nan=0.0)
            ema200 = np.nan_to_num(ema200, nan=0.0)

            # Get recent non-zero values
            recent_ema50 = ema50[-10:]
            recent_ema200 = ema200[-10:]

            valid_ema50 = recent_ema50[recent_ema50 > 0]
            valid_ema200 = recent_ema200[recent_ema200 > 0]

            if len(valid_ema50) < 5 or len(valid_ema200) < 5:
                return {
                    "state": "NEUTRAL",
                    "score": 0.3,
                    "reason": "Insufficient valid EMA data",
                }

            # Calculate slopes (recent trend in EMAs)
            ema50_slope = (valid_ema50[-1] - valid_ema50[0]) / len(valid_ema50)
            ema200_slope = (valid_ema200[-1] - valid_ema200[0]) / len(valid_ema200)

            # Robust current price extraction with NaN handling
            current_price = np.nan_to_num(df["Close"].iloc[-1], nan=0.0)
            if current_price == 0:
                return {
                    "state": "NEUTRAL",
                    "score": 0.3,
                    "reason": "Invalid current price",
                }

            # Enhanced trend determination with architectural precision
            ema50_current = valid_ema50[-1]
            ema200_current = valid_ema200[-1]

            if (
                ema50_current > ema200_current
                and current_price > ema50_current
                and ema50_slope > 0
            ):
                state: SignalState = "UP"
                score = 0.7
            elif ema50_current > ema200_current and ema50_slope > 0:
                state = "UP"
                score = 0.5
            elif (
                ema50_current < ema200_current
                and current_price < ema50_current
                and ema50_slope < 0
            ):
                state = "DOWN"
                score = 0.7
            elif ema50_current < ema200_current and ema50_slope < 0:
                state = "DOWN"
                score = 0.5
            else:
                state = "NEUTRAL"
                score = 0.3

            return {
                "state": state,
                "score": score,
                "ema50_slope": ema50_slope,
                "ema200_slope": ema200_slope,
                "ema50_current": ema50_current,
                "ema200_current": ema200_current,
                "valid_data_points": len(valid_closes),
            }

        except Exception as e:
            logger.warning(f"EMA analysis failed: {e}")
            return {"state": "NEUTRAL", "score": 0.3, "reason": f"EMA error: {e!s}"}

    def _combine_signals(
        self, hh_hl: dict[str, Any], ema: dict[str, Any]
    ) -> tuple[SignalState, float, str]:
        """Combine HH/HL and EMA signals into final result."""
        hh_state = hh_hl["state"]
        ema_state = ema["state"]

        # Agreement between signals
        if hh_state == ema_state:
            if hh_state == "UP":
                final_state: SignalState = "UP"
                final_score = min(
                    0.8, (hh_hl["score"] + ema["score"]) / 2 + 0.1
                )  # Bonus for agreement
                reason = "Strong uptrend: HH/HL and EMA confirm UP"
            elif hh_state == "DOWN":
                final_state = "DOWN"
                final_score = min(0.8, (hh_hl["score"] + ema["score"]) / 2 + 0.1)
                reason = "Strong downtrend: HH/HL and EMA confirm DOWN"
            else:  # Both NEUTRAL
                final_state = "NEUTRAL"
                final_score = 0.4
                reason = "Neutral trend: no clear direction"
        else:
            # Disagreement - take average but lower confidence
            avg_score = (hh_hl["score"] + ema["score"]) / 2

            # Priority logic: if one is strong UP/DOWN and other is NEUTRAL, lean towards the strong signal
            if hh_state in ["UP", "DOWN"] and ema_state == "NEUTRAL":
                final_state = hh_state
                final_score = max(0.4, avg_score * 0.8)  # Reduced confidence
                reason = f"Weak {hh_state.lower()} trend: HH/HL shows {hh_state}, EMA neutral"
            elif ema_state in ["UP", "DOWN"] and hh_state == "NEUTRAL":
                final_state = ema_state
                final_score = max(0.4, avg_score * 0.8)
                reason = f"Weak {ema_state.lower()} trend: EMA shows {ema_state}, HH/HL neutral"
            else:
                # Opposing signals - stay neutral
                final_state = "NEUTRAL"
                final_score = 0.3
                reason = f"Conflicting signals: HH/HL={hh_state}, EMA={ema_state}"

        return final_state, final_score, reason
