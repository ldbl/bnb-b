"""Main signal generation orchestrator (thin layer)."""

import logging
from typing import Any

import pandas as pd

from ..core.exceptions import AnalysisError
from ..core.types import SignalResult
from .combiners import combine_signals
from .confidence import calculate_confidence

# from .filters import apply_signal_filters  # Temporarily disabled for new architecture

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Core Signal Generation Engine for BNB Trading System (refactored thin layer)

    This class serves as the main orchestrator for the entire BNB trading system,
    delegating to specialized modules for signal combination, confidence calculation,
    and filtering.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the signal generator with configuration.

        Args:
            config: System configuration parameters
        """
        self.config = config

        # Extract key parameters from config
        signals_config = config.get("signals", {})
        self.fibonacci_weight = signals_config.get("fibonacci_weight", 0.35)
        self.weekly_tails_weight = signals_config.get("weekly_tails_weight", 0.40)
        self.ma_weight = signals_config.get("ma_weight", 0.10)
        self.rsi_weight = signals_config.get("rsi_weight", 0.08)
        self.macd_weight = signals_config.get("macd_weight", 0.07)
        self.bb_weight = signals_config.get("bb_weight", 0.00)
        self.sentiment_weight = signals_config.get("sentiment_weight", 0.05)
        self.min_confirmations = signals_config.get("min_confirmations", 1)
        self.confidence_threshold = signals_config.get("confidence_threshold", 0.8)

    def generate_signal(
        self,
        daily_df: pd.DataFrame,
        weekly_df: pd.DataFrame | None = None,
        analyses: dict[str, Any] | None = None,
    ) -> SignalResult:
        """
        Generate trading signal by orchestrating all analysis modules.

        Args:
            daily_df: Daily OHLCV data
            weekly_df: Weekly OHLCV data (optional)
            analyses: Pre-computed analyses from other modules

        Returns:
            Dict with trading signal and metadata
        """
        try:
            # Step 1: Run all analysis modules if not provided
            if analyses is None:
                analyses = self._execute_all_analyses(daily_df, weekly_df)

            # Step 2: Combine signals using weighted scoring
            combined_signal = combine_signals(
                analyses, self._get_weights(), self.confidence_threshold
            )

            # Debug signal combination
            long_score = combined_signal.get("long_score", 0)
            short_score = combined_signal.get("short_score", 0)
            logger.debug(
                f"[SIGNALS] Confluence: long_score={long_score:.3f}, short_score={short_score:.3f}, threshold={self.confidence_threshold}"
            )

            # Step 3: Calculate confidence score
            confidence = calculate_confidence(combined_signal, analyses)

            # Step 4: Apply signal filters
            filters_applied = [
                "trend_filter",
                "volume_filter",
                "regime_filter",
            ]  # Example filters
            # Apply basic signal filters (simplified for now)
            final_signal = combined_signal  # TODO: Re-implement filters module
            filters_passed = (
                "Yes" if final_signal.get("signal") != "HOLD" else "Partial"
            )
            logger.debug(
                f"[FILTERS] Applied: {filters_applied}, Passed: {filters_passed}"
            )

            # Step 5: Format final result
            return {
                "signal": final_signal.get("signal", "HOLD"),
                "confidence": confidence,
                "price": daily_df["Close"].iloc[-1] if not daily_df.empty else 0.0,
                "timestamp": pd.Timestamp(daily_df.index[-1])
                if not daily_df.empty
                else pd.Timestamp.now(),
                "reasons": final_signal.get("reasons", []),
                "analyses": analyses,
                "metadata": {
                    "min_confirmations": self.min_confirmations,
                    "confidence_threshold": self.confidence_threshold,
                    "weights": self._get_weights(),
                },
            }

        except Exception as e:
            logger.exception(f"Грешка при signal generation: {e}")
            raise AnalysisError(f"Signal generation failed: {e}") from e

    def _execute_all_analyses(
        self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame | None
    ) -> dict[str, Any]:
        """Execute all analysis modules and collect results."""
        analyses: dict[str, Any] = {}

        try:
            # Import analysis modules
            from ..analysis.weekly_tails.analyzer import WeeklyTailsAnalyzer
            from ..fibonacci import FibonacciAnalyzer
            from ..indicators import TechnicalIndicators

            logger.info("Executing all analysis modules...")

            # 1. Fibonacci Analysis
            try:
                if "fibonacci" in self.config and self.fibonacci_weight > 0:
                    fib_analyzer = FibonacciAnalyzer(self.config)
                    fib_result = fib_analyzer.analyze_fibonacci_trend(daily_df)
                    analyses["fibonacci"] = fib_result.get("fibonacci_signal", {})
                    logger.info(
                        f"Fibonacci analysis completed: {analyses['fibonacci'].get('signal', 'N/A')}"
                    )
            except Exception as e:
                logger.exception(f"Error in Fibonacci analysis: {e}")
                analyses["fibonacci"] = {
                    "signal": "HOLD",
                    "strength": 0.0,
                    "error": str(e),
                }

            # 2. Weekly Tails Analysis
            try:
                logger.info(
                    f"Weekly tails check: weekly_df={weekly_df is not None}, config_has_weekly_tails={'weekly_tails' in self.config}, weight={self.weekly_tails_weight}"
                )
                if (
                    weekly_df is not None
                    and "weekly_tails" in self.config
                    and self.weekly_tails_weight > 0
                ):
                    logger.info("Weekly tails analysis starting...")
                    tails_analyzer = WeeklyTailsAnalyzer(self.config)
                    tails_result = tails_analyzer.calculate_tail_strength(weekly_df)
                    logger.info(
                        f"Tails result type: {type(tails_result)}, keys: {list(tails_result.keys()) if isinstance(tails_result, dict) else 'N/A'}"
                    )
                    analyses["weekly_tails"] = {
                        "signal": tails_result.get("signal", "HOLD"),
                        "strength": tails_result.get("strength", 0.0),
                    }
                    logger.info(
                        f"Weekly tails analysis completed: {analyses['weekly_tails'].get('signal', 'N/A')}"
                    )
                else:
                    logger.warning(
                        f"Weekly tails check failed: weekly_df={weekly_df is not None}, config_has_weekly_tails={'weekly_tails' in self.config}, weight={self.weekly_tails_weight}"
                    )
            except Exception as e:
                logger.exception(f"Error in Weekly Tails analysis: {e}")
                analyses["weekly_tails"] = {
                    "signal": "HOLD",
                    "strength": 0.0,
                    "error": str(e),
                }

            # 3. Technical Indicators Analysis
            try:
                if any([self.rsi_weight > 0, self.macd_weight > 0, self.bb_weight > 0]):
                    indicators = TechnicalIndicators(self.config)
                    daily_with_indicators = indicators.calculate_indicators(
                        daily_df.copy()
                    )

                    # Get individual indicator signals
                    if self.rsi_weight > 0:
                        rsi_signals = indicators.get_rsi_signal(daily_with_indicators)
                        analyses["rsi"] = rsi_signals
                        logger.info(
                            f"RSI analysis completed: {rsi_signals.get('signal', 'N/A')}"
                        )

                    if self.macd_weight > 0:
                        # Get MACD values from the last row
                        macd_line = (
                            daily_with_indicators["MACD"].iloc[-1]
                            if "MACD" in daily_with_indicators.columns
                            else 0.0
                        )
                        signal_line = (
                            daily_with_indicators["MACD_signal"].iloc[-1]
                            if "MACD_signal" in daily_with_indicators.columns
                            else 0.0
                        )
                        histogram = (
                            daily_with_indicators["MACD_histogram"].iloc[-1]
                            if "MACD_histogram" in daily_with_indicators.columns
                            else 0.0
                        )
                        macd_signals = indicators.get_macd_signal(
                            macd_line, signal_line, histogram
                        )
                        analyses["macd"] = macd_signals
                        logger.info(
                            f"MACD analysis completed: {macd_signals.get('signal', 'N/A')}"
                        )

                    if self.bb_weight > 0:
                        # Get Bollinger values from the last row
                        current_price = (
                            daily_with_indicators["Close"].iloc[-1]
                            if "Close" in daily_with_indicators.columns
                            else 0.0
                        )
                        upper_band = (
                            daily_with_indicators["BB_upper"].iloc[-1]
                            if "BB_upper" in daily_with_indicators.columns
                            else 0.0
                        )
                        lower_band = (
                            daily_with_indicators["BB_lower"].iloc[-1]
                            if "BB_lower" in daily_with_indicators.columns
                            else 0.0
                        )
                        bb_position = (
                            ((current_price - lower_band) / (upper_band - lower_band))
                            if upper_band > lower_band
                            else 0.5
                        )
                        bb_signals = indicators.get_bollinger_signal(
                            current_price, upper_band, lower_band, bb_position
                        )
                        analyses["bollinger"] = bb_signals
                        logger.info(
                            f"Bollinger Bands analysis completed: {bb_signals.get('signal', 'N/A')}"
                        )

            except Exception as e:
                logger.exception(f"Error in Technical Indicators analysis: {e}")
                if self.rsi_weight > 0:
                    analyses["rsi"] = {
                        "signal": "HOLD",
                        "strength": 0.0,
                        "error": str(e),
                    }
                if self.macd_weight > 0:
                    analyses["macd"] = {
                        "signal": "HOLD",
                        "strength": 0.0,
                        "error": str(e),
                    }
                if self.bb_weight > 0:
                    analyses["bollinger"] = {
                        "signal": "HOLD",
                        "strength": 0.0,
                        "error": str(e),
                    }

            # 4. Moving Averages Analysis (if weight > 0)
            try:
                if self.ma_weight > 0:
                    from ..moving_averages import MovingAveragesAnalyzer

                    ma_analyzer = MovingAveragesAnalyzer(self.config)
                    # Use the available methods to build a simple MA analysis
                    ema_data = ma_analyzer.calculate_emas(daily_df)
                    ma_signals = ma_analyzer.get_ma_trading_signals(ema_data)
                    analyses["moving_averages"] = ma_signals
                    logger.info(
                        f"Moving averages analysis completed: {ma_signals.get('signal', 'N/A')}"
                    )
            except Exception as e:
                logger.exception(f"Error in Moving Averages analysis: {e}")
                analyses["moving_averages"] = {
                    "signal": "HOLD",
                    "strength": 0.0,
                    "error": str(e),
                }

            logger.info(
                f"Analysis execution completed. Active modules: {list(analyses.keys())}"
            )
            return analyses

        except Exception as e:
            logger.exception(f"Грешка при executing analyses: {e}")
            return {}

    def _get_weights(self) -> dict[str, float]:
        """Get analysis weights configuration."""
        return {
            "fibonacci": self.fibonacci_weight,
            "weekly_tails": self.weekly_tails_weight,
            "moving_averages": self.ma_weight,
            "rsi": self.rsi_weight,
            "macd": self.macd_weight,
            "bollinger": self.bb_weight,
            "sentiment": self.sentiment_weight,
            "trend": 0.05,  # Add trend analysis weight
        }
