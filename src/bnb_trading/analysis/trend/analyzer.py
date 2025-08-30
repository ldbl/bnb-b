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


class TrendAnalyzer:
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
            f"TrendAnalyzer initialized: lookback={self.lookback_days}, weight={self.weight}"
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
                    "ema_state": ema_result["state"],
                    "ema_score": ema_result["score"],
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
        """Analyze Higher Highs/Higher Lows patterns in recent data."""
        recent_data = df.tail(self.lookback_days).copy()

        # Find local highs and lows (simplified)
        highs = recent_data["High"].values
        lows = recent_data["Low"].values

        # Simple approach: compare 5-day windows
        window_size = 5
        higher_highs = 0
        lower_highs = 0
        higher_lows = 0
        lower_lows = 0

        for i in range(window_size, len(highs) - window_size):
            current_high = highs[i]
            previous_high = highs[i - window_size]
            current_low = lows[i]
            previous_low = lows[i - window_size]

            if current_high > previous_high:
                higher_highs += 1
            elif current_high < previous_high:
                lower_highs += 1

            if current_low > previous_low:
                higher_lows += 1
            elif current_low < previous_low:
                lower_lows += 1

        # Determine trend direction
        if higher_highs >= self.min_consecutive and higher_lows >= self.min_consecutive:
            state: SignalState = "UP"
            score = min(0.8, 0.4 + (higher_highs + higher_lows) * 0.05)
        elif lower_highs >= self.min_consecutive and lower_lows >= self.min_consecutive:
            state = "DOWN"
            score = min(0.8, 0.4 + (lower_highs + lower_lows) * 0.05)
        else:
            state = "NEUTRAL"
            score = 0.3

        return {
            "state": state,
            "score": score,
            "higher_highs": higher_highs,
            "lower_highs": lower_highs,
            "higher_lows": higher_lows,
            "lower_lows": lower_lows,
        }

    def _analyze_ema_slope(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze EMA50 vs EMA200 slope for trend confirmation."""
        try:
            # Calculate EMAs
            closes = df["Close"].values
            ema50 = talib.EMA(closes, timeperiod=50)
            ema200 = talib.EMA(closes, timeperiod=200)

            # Get recent values (non-NaN)
            recent_ema50 = ema50[-10:]  # Last 10 days
            recent_ema200 = ema200[-10:]

            # Remove NaN values
            valid_ema50 = recent_ema50[~np.isnan(recent_ema50)]
            valid_ema200 = recent_ema200[~np.isnan(recent_ema200)]

            if len(valid_ema50) < 5 or len(valid_ema200) < 5:
                return {
                    "state": "NEUTRAL",
                    "score": 0.3,
                    "reason": "Insufficient EMA data",
                }

            # Calculate slopes (recent trend in EMAs)
            ema50_slope = (valid_ema50[-1] - valid_ema50[0]) / len(valid_ema50)
            ema200_slope = (valid_ema200[-1] - valid_ema200[0]) / len(valid_ema200)
            current_price = df["Close"].iloc[-1]

            # Trend determination
            if (
                valid_ema50[-1] > valid_ema200[-1]
                and current_price > valid_ema50[-1]
                and ema50_slope > 0
            ):
                state: SignalState = "UP"
                score = 0.7
            elif valid_ema50[-1] > valid_ema200[-1] and ema50_slope > 0:
                state = "UP"
                score = 0.5
            elif (
                valid_ema50[-1] < valid_ema200[-1]
                and current_price < valid_ema50[-1]
                and ema50_slope < 0
            ):
                state = "DOWN"
                score = 0.7
            elif valid_ema50[-1] < valid_ema200[-1] and ema50_slope < 0:
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
                "ema50_current": valid_ema50[-1],
                "ema200_current": valid_ema200[-1],
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
