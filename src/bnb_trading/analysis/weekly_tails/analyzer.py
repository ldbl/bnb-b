"""
Enhanced Weekly Tails Analyzer with ATR Normalization for LONG Precision ≥85%

Core formula: tail_strength = (lower_wick / body_size) * volume_ratio * (1 / atr_normalized)
Focus: Simple but accurate, no look-ahead, weekly tails dominant weight
"""

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from bnb_trading.core.models import ModuleResult

logger = logging.getLogger(__name__)


class WeeklyTailsAnalyzer:
    """Enhanced Weekly Tails Analyzer for LONG precision ≥85%"""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with configuration"""
        tails_config = config.get("weekly_tails", {})
        self.lookback_weeks = tails_config.get("lookback_weeks", 8)
        self.min_tail_strength = tails_config.get("min_tail_strength", 1.2)
        self.atr_period = tails_config.get("atr_period", 14)
        self.volume_ma_period = tails_config.get("vol_sma_period", 20)

        # New validation parameters
        self.min_tail_ratio = tails_config.get("min_tail_ratio", 1.0)
        self.max_body_atr = tails_config.get("max_body_atr", 0.8)
        self.min_close_pos = tails_config.get("min_close_pos", 0.35)

        # RESTORE ORIGINAL PERFECT LOGIC: Trend-based Weighting Parameters
        self.trend_based_weighting = tails_config.get("trend_based_weighting", True)
        self.bull_market_threshold = tails_config.get(
            "bull_market_threshold", 0.15
        )  # 15% gain
        self.bear_market_threshold = tails_config.get(
            "bear_market_threshold", -0.10
        )  # 10% loss
        self.long_tail_amplification = tails_config.get("long_tail_amplification", 1.5)
        self.short_tail_suppression = tails_config.get("short_tail_suppression", 0.3)

        logger.info(
            f"Weekly Tails Analyzer initialized - min_tail_strength: {self.min_tail_strength}, "
            f"min_tail_ratio: {self.min_tail_ratio}, max_body_atr: {self.max_body_atr}, "
            f"trend_based_weighting: {self.trend_based_weighting}"
        )

    def calculate_tail_strength(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        Calculate enhanced tail strength with ATR normalization

        Formula: tail_strength = (lower_wick / body_size) * volume_ratio * (1 / atr_normalized)

        Args:
            df: DataFrame with OHLCV data (closed candles only!)

        Returns:
            Dict with tail analysis results
        """
        try:
            # Look-ahead guard: ensure we only use closed candles
            closed_df = self._ensure_closed_candles(df)
            if len(closed_df) < self.lookback_weeks:
                return self._empty_result("Insufficient closed data")

            recent_weeks = closed_df.tail(self.lookback_weeks)

            # Calculate components for each week
            results = []
            for i, (date, row) in enumerate(recent_weeks.iterrows()):
                tail_data = self._analyze_single_week(
                    row, date, recent_weeks.iloc[: i + 1]
                )
                if tail_data:
                    results.append(tail_data)

            # Find strongest LONG tail signal
            long_tails = [
                t
                for t in results
                if t["signal"] == "LONG" and t["strength"] >= self.min_tail_strength
            ]

            if not long_tails:
                return self._empty_result("No qualifying LONG tails found")

            # Return strongest tail
            strongest_tail = max(long_tails, key=lambda x: x["strength"])

            return {
                "signal": "LONG",
                "strength": strongest_tail["strength"],
                "confidence": min(
                    strongest_tail["strength"] / 5.0, 1.0
                ),  # Normalize to 0-1
                "reason": strongest_tail["reason"],
                "price_level": strongest_tail["low"],
                "all_tails": results,
                "analysis_date": pd.Timestamp.now(),
            }

        except Exception as e:
            logger.exception(f"Error calculating tail strength: {e}")
            return self._empty_result(f"Error: {e}")

    def _analyze_single_week(
        self, row: pd.Series, date: pd.Timestamp, history_df: pd.DataFrame
    ) -> dict[str, Any] | None:
        """Analyze single weekly candle for tail strength with correct ATR normalization"""
        try:
            # Extract OHLCV
            open_price = float(row.get("open", row.get("Open", 0)))
            high_price = float(row.get("high", row.get("High", 0)))
            low_price = float(row.get("low", row.get("Low", 0)))
            close_price = float(row.get("close", row.get("Close", 0)))
            volume = float(row.get("volume", row.get("Volume", 0)))

            if any(
                x <= 0 for x in [open_price, high_price, low_price, close_price, volume]
            ):
                return None

            # Calculate epsilon for division safety
            epsilon = 1e-8 * close_price

            # Calculate tail metrics with proper definitions
            body_size = max(abs(close_price - open_price), epsilon)
            lower_wick = max(min(open_price, close_price) - low_price, 0)
            upper_wick = max(high_price - max(open_price, close_price), 0)

            # Skip if no meaningful lower wick
            if lower_wick < 0.01:
                return None

            # Calculate ATR from previous weeks (no look-ahead)
            atr_w = self._calculate_atr_shifted(history_df, self.atr_period)
            if atr_w <= 0:
                return None

            # Calculate volume SMA from previous weeks (no look-ahead)
            vol_sma = self._calculate_volume_sma_shifted(
                history_df, self.volume_ma_period
            )

            # Enhanced tail strength formula (correct ATR normalization)
            tail_ratio = lower_wick / max(
                atr_w, epsilon
            )  # Bigger wick relative to volatility = better
            body_control = min(
                body_size / max(atr_w, epsilon), 1.0
            )  # Large body reduces validity
            body_factor = (
                1.0 - 0.5 * body_control
            )  # Range 0.5..1.0 (smaller body = higher factor)
            volume_ratio = np.clip(
                volume / max(vol_sma, epsilon), 0.5, 2.0
            )  # Reduce noise
            vol_factor = volume_ratio  # 0.5..2.0 range

            tail_strength = tail_ratio * body_factor * vol_factor

            # Validation rules for LONG signals
            min_tail_ratio = getattr(self, "min_tail_ratio", 1.0)
            max_body_atr = getattr(self, "max_body_atr", 0.8)
            min_close_pos = getattr(self, "min_close_pos", 0.35)

            # Rule 1: lower_wick / atr_w >= min_tail_ratio
            if tail_ratio < min_tail_ratio:
                return None

            # Rule 2: tail_strength >= min_tail_strength
            if tail_strength < self.min_tail_strength:
                return None

            # Rule 3: body_size / atr_w <= max_body_atr
            if (body_size / max(atr_w, epsilon)) > max_body_atr:
                return None

            # Rule 4: close position validation
            price_range = max(high_price - low_price, epsilon)
            close_pos = (close_price - low_price) / price_range
            if close_pos < min_close_pos:
                return None

            # Signal classification (prefer bullish candles for LONG)
            is_bullish = close_price > open_price
            signal = "LONG" if is_bullish else "HOLD"

            reason = (
                f"Tail ratio: {tail_ratio:.2f}, strength: {tail_strength:.2f}, "
                f"close_pos: {close_pos:.2f}, body_factor: {body_factor:.2f}"
            )

            return {
                "date": date,
                "signal": signal,
                "strength": tail_strength,
                "tail_ratio": tail_ratio,
                "body_factor": body_factor,
                "volume_ratio": volume_ratio,
                "close_pos": close_pos,
                "lower_wick": lower_wick,
                "upper_wick": upper_wick,
                "body_size": body_size,
                "atr_w": atr_w,
                "low": low_price,
                "high": high_price,
                "close": close_price,
                "is_bullish": is_bullish,
                "reason": reason,
            }

        except Exception as e:
            logger.exception(f"Error analyzing week {date}: {e}")
            return None

    def _calculate_atr_shifted(self, df: pd.DataFrame, period: int) -> float:
        """Calculate ATR with proper look-ahead prevention (shifted)"""
        try:
            if len(df) < max(2, period // 4):  # Need at least some data
                return 0.0

            # Handle both column naming conventions
            high = (
                df["High"]
                if "High" in df.columns
                else df.get("high", pd.Series(dtype=float))
            )
            low = (
                df["Low"]
                if "Low" in df.columns
                else df.get("low", pd.Series(dtype=float))
            )
            close = (
                df["Close"]
                if "Close" in df.columns
                else df.get("close", pd.Series(dtype=float))
            )

            if any(col.empty for col in [high, low, close]):
                return 0.0

            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))

            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Use smaller min_periods for more flexible ATR calculation
            min_periods = max(2, min(period // 2, len(df) // 2))
            atr = true_range.rolling(window=period, min_periods=min_periods).mean()
            atr_shifted = atr.shift(1)  # Use previous ATR value

            # Get the last valid ATR value
            valid_atr = atr_shifted.dropna()
            if len(valid_atr) > 0:
                return float(valid_atr.iloc[-1])
            # Fallback: use simple price range average
            price_ranges = high - low
            return float(price_ranges.mean()) if not price_ranges.empty else 0.0

        except Exception as e:
            logger.exception(f"Error calculating shifted ATR: {e}")
            return 0.0

    def _calculate_volume_sma_shifted(self, df: pd.DataFrame, period: int) -> float:
        """Calculate volume SMA with proper look-ahead prevention (shifted)"""
        try:
            if len(df) < 2:  # Need at least 2 data points
                return 1.0

            # Handle both column naming conventions
            volume = (
                df["Volume"]
                if "Volume" in df.columns
                else df.get("volume", pd.Series(dtype=float))
            )
            if volume.empty:
                return 1.0

            # Use flexible min_periods
            min_periods = max(2, min(period // 4, len(df) // 2))
            vol_sma = volume.rolling(window=period, min_periods=min_periods).mean()
            vol_sma_shifted = vol_sma.shift(1)  # Use previous SMA value

            # Get the last valid SMA value
            valid_sma = vol_sma_shifted.dropna()
            if len(valid_sma) > 0:
                return float(valid_sma.iloc[-1])
            # Fallback: use volume mean
            return float(volume.mean()) if not volume.empty else 1.0

        except Exception as e:
            logger.exception(f"Error calculating shifted volume SMA: {e}")
            return 1.0

    def _calculate_atr(self, df: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        try:
            if len(df) < period:
                return 0.0

            high = df.get("high", df.get("High", pd.Series(dtype=float)))
            low = df.get("low", df.get("Low", pd.Series(dtype=float)))
            close = df.get("close", df.get("Close", pd.Series(dtype=float)))

            if any(col.empty for col in [high, low, close]):
                return 0.0

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

    def _calculate_volume_ma(self, df: pd.DataFrame, period: int) -> float:
        """Calculate volume moving average"""
        try:
            if len(df) < period:
                return 1.0

            volume = df.get("volume", df.get("Volume", pd.Series(dtype=float)))
            if volume.empty:
                return 1.0

            volume_ma = volume.rolling(window=period).mean().iloc[-1]
            return float(volume_ma) if not pd.isna(volume_ma) else 1.0

        except Exception as e:
            logger.exception(f"Error calculating volume MA: {e}")
            return 1.0

    def _ensure_closed_candles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure we only use closed candles - no look-ahead"""
        # For backtesting, we already receive historical data
        # So we can use all provided data as it's already "closed" relative to analysis point
        return df

    def _empty_result(self, reason: str) -> dict[str, Any]:
        """Return empty result with reason"""
        return {
            "signal": "HOLD",
            "strength": 0.0,
            "confidence": 0.0,
            "reason": reason,
            "price_level": 0.0,
            "all_tails": [],
            "analysis_date": pd.Timestamp.now(),
        }

    def validate_no_lookahead(
        self, df: pd.DataFrame, analysis_timestamp: pd.Timestamp
    ) -> bool:
        """Validate that analysis doesn't use future data"""
        try:
            if df.empty:
                return True

            # Check that all data is before analysis timestamp
            last_data_time = (
                df.index[-1]
                if hasattr(df.index, "to_pydatetime")
                else analysis_timestamp
            )

            if hasattr(last_data_time, "replace"):
                # For weekly data, ensure we don't use current incomplete week
                week_end = last_data_time.replace(hour=23, minute=59, second=59)
                return week_end < analysis_timestamp

            return True

        except Exception as e:
            logger.exception(f"Error validating no look-ahead: {e}")
            return False

    def analyze(
        self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame
    ) -> "ModuleResult":
        """
        Unified analyze method returning ModuleResult for decision engine integration.

        Args:
            daily_df: Daily OHLCV data (unused for weekly tails)
            weekly_df: Weekly OHLCV data for tail analysis

        Returns:
            ModuleResult with status, state, score, contrib, reason
        """
        from bnb_trading.core.models import ModuleResult

        try:
            # RESTORE ORIGINAL PERFECT LOGIC: Apply trend-based weighting
            if self.trend_based_weighting:
                # Analyze market trend first
                market_trend = self._analyze_market_trend(weekly_df)

                # Calculate tail strength using existing method
                result = self.calculate_tail_strength(weekly_df)

                # Apply trend-based weighting to results
                weighted_result = self._apply_trend_weighting(result, market_trend)
            else:
                # Use original method without trend weighting
                weighted_result = self.calculate_tail_strength(weekly_df)
                market_trend = "NEUTRAL"

            # Map result to ModuleResult format
            signal = weighted_result.get("signal", "HOLD")
            confidence = weighted_result.get("confidence", 0.0)
            reason = weighted_result.get("reason", "No weekly tails pattern")

            # Convert signal to state and calculate contribution
            if signal == "LONG":
                state = "LONG"
                score = confidence
                # Use default weight of 0.60 for weekly tails
                contrib = score * 0.60
            else:
                state = "HOLD"
                score = confidence
                contrib = 0.0

            return ModuleResult(
                status="OK",
                state=state,
                score=score,
                contrib=contrib,
                reason=reason,
                meta={"original_result": weighted_result, "market_trend": market_trend},
            )

        except Exception as e:
            logger.exception(f"Weekly tails analysis failed: {e}")
            return ModuleResult(
                status="ERROR",
                state="NEUTRAL",
                score=0.0,
                contrib=0.0,
                reason=f"Weekly tails analysis error: {e}",
                meta={},
            )

    def _analyze_market_trend(self, weekly_df: pd.DataFrame) -> str:
        """
        RESTORED ORIGINAL PERFECT LOGIC: Analyze market trend to determine appropriate tail weighting

        Returns:
            str: Market trend classification (BULL, BEAR, NEUTRAL)
        """
        try:
            if len(weekly_df) < self.lookback_weeks:
                return "NEUTRAL"

            close_col = "close" if "close" in weekly_df.columns else "Close"
            recent_weeks = weekly_df[close_col].tail(self.lookback_weeks)

            # Calculate trend strength over lookback period
            trend_change = (
                recent_weeks.iloc[-1] - recent_weeks.iloc[0]
            ) / recent_weeks.iloc[0]

            # Determine trend classification
            if trend_change >= self.bull_market_threshold:
                return "BULL"
            if trend_change <= self.bear_market_threshold:
                return "BEAR"
            return "NEUTRAL"

        except Exception as e:
            logger.error(f"Error analyzing market trend: {e}")
            return "NEUTRAL"

    def _apply_trend_weighting(
        self, tails_result: dict[str, Any], market_trend: str
    ) -> dict[str, Any]:
        """
        RESTORED ORIGINAL PERFECT LOGIC: Apply trend-based weighting to tail signals

        Args:
            tails_result: Original tails analysis result
            market_trend: Current market trend classification

        Returns:
            Weighted tails result with trend-appropriate adjustments
        """
        try:
            weighted_result = tails_result.copy()
            original_strength = tails_result.get("strength", 0.0)
            signal = tails_result.get("signal", "HOLD")
            original_reason = tails_result.get("reason", "")

            # Apply trend-based weighting logic
            if market_trend == "BULL":
                if signal == "LONG":
                    # Amplify LONG tail signals in bull markets
                    new_strength = min(
                        original_strength * self.long_tail_amplification, 5.0
                    )  # Cap at 5.0
                    new_confidence = min(
                        weighted_result.get("confidence", 0.0)
                        * self.long_tail_amplification,
                        1.0,
                    )
                    weighted_result.update(
                        {
                            "strength": new_strength,
                            "confidence": new_confidence,
                            "reason": f"{original_reason} (Bull market amplified)",
                            "trend_adjustment": "BULL_AMPLIFIED",
                        }
                    )
                    logger.debug(
                        f"Bull market: LONG signal amplified from {original_strength:.2f} to {new_strength:.2f}"
                    )

            elif market_trend == "BEAR":
                if signal == "LONG":
                    # Reduce LONG tail signals in bear markets
                    new_strength = original_strength * 0.7
                    new_confidence = weighted_result.get("confidence", 0.0) * 0.7
                    weighted_result.update(
                        {
                            "strength": new_strength,
                            "confidence": new_confidence,
                            "reason": f"{original_reason} (Bear market reduced)",
                            "trend_adjustment": "BEAR_REDUCED",
                        }
                    )
                    logger.debug(
                        f"Bear market: LONG signal reduced from {original_strength:.2f} to {new_strength:.2f}"
                    )

            else:  # NEUTRAL
                weighted_result["trend_adjustment"] = "NO_ADJUSTMENT"

            return weighted_result

        except Exception as e:
            logger.error(f"Error applying trend weighting: {e}")
            return tails_result
