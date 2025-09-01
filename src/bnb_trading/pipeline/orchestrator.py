"""Main pipeline orchestration for BNB Trading System."""

import logging
import os
import sys
from typing import Any

import pandas as pd
import toml

# For direct script execution - add src to path
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(os.path.dirname(current_dir))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# Use absolute imports for package structure
from bnb_trading.core.exceptions import AnalysisError
from bnb_trading.data.fetcher import BNBDataFetcher
from bnb_trading.signals.generator import SignalGenerator

logger = logging.getLogger(__name__)


class TradingPipeline:
    """Thin orchestration layer that ties everything together"""

    def __init__(self, config_path: str = "config.toml"):
        """Initialize trading pipeline with configuration."""
        self.config_path = config_path

        # Try to find config.toml in project root
        if not os.path.exists(config_path):
            # Look for config in project root (2 levels up from src/bnb_trading/pipeline)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(current_dir))
            )
            root_config_path = project_root + "/config.toml"
            if os.path.exists(root_config_path):
                config_path = root_config_path
                self.config_path = root_config_path

        self.config = toml.load(config_path)

        # Initialize core components
        self.data_fetcher = BNBDataFetcher(self.config["data"]["symbol"])
        self.signal_generator = SignalGenerator(self.config)

        logger.info("🚀 Trading Pipeline initialized")

    def run_analysis(self) -> dict[str, Any]:
        """
        Execute complete trading analysis pipeline.

        Returns:
            Complete analysis results with signal and metadata
        """
        try:
            # Step 1: Fetch data
            logger.info("📊 Fetching market data...")
            lookback_days = self.config["data"]["lookback_days"]
            data = self.data_fetcher.fetch_bnb_data(lookback_days)

            daily_df = data["daily"]
            weekly_df = data["weekly"]

            # Debug breakpoint as per REc.md plan
            logger.debug(
                f"[DATA] Candles: daily={len(daily_df)}, weekly={len(weekly_df)}"
            )

            # Step 2: Run analyses
            logger.info("🔍 Running technical analysis...")
            analyses = self._execute_analyses(daily_df, weekly_df)

            # Debug breakpoint for analysis results
            non_hold_count = sum(
                1
                for a in analyses.values()
                if isinstance(a, dict) and a.get("signal") != "HOLD"
            )
            logger.debug(
                f"[ANALYSIS] Modules: {list(analyses.keys())}, Non-HOLD: {non_hold_count}"
            )

            # Step 3: Generate signals
            logger.info("⚡ Generating trading signals...")
            signal = self.signal_generator.generate_signal(
                daily_df, weekly_df, analyses
            )

            # Debug breakpoint for signal generation
            if isinstance(signal, dict):
                long_score = signal.get("long_score", 0)
                short_score = signal.get("short_score", 0)
                confidence = signal.get("confidence", 0)
                logger.debug(
                    f"[SIGNALS] Confluence: long_score={long_score:.3f}, short_score={short_score:.3f}, confidence={confidence:.3f}"
                )

            # Debug final decision
            final_signal = (
                signal.get("signal", "UNKNOWN")
                if isinstance(signal, dict)
                else str(signal)
            )
            final_confidence = (
                signal.get("confidence", 0) if isinstance(signal, dict) else 0
            )
            reasons_count = (
                len(signal.get("reasons", [])) if isinstance(signal, dict) else 0
            )
            logger.debug(
                f"[DECISION] Final: signal={final_signal}, confidence={final_confidence:.3f}, reasons={reasons_count}"
            )

            # Step 4: Validate
            logger.info("✅ Validating results...")
            validated_signal = self._validate_results(signal, daily_df)

            # Step 5: Export results to CSV
            self._export_results_to_csv(validated_signal, daily_df, weekly_df, analyses)

            # Step 6: Return results
            return {
                "signal": validated_signal,
                "data": {"daily": daily_df, "weekly": weekly_df},
                "analyses": analyses,
                "metadata": {
                    "pipeline_version": "2.0.0",
                    "data_points": len(daily_df),
                    "analysis_modules": len(analyses),
                },
            }

        except Exception as e:
            logger.exception(f"Pipeline execution failed: {e}")
            raise AnalysisError(f"Trading pipeline failed: {e}") from e

    def _execute_analyses(
        self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame
    ) -> dict[str, Any]:
        """Execute all analysis modules."""
        analyses = {}

        try:
            logger.info("🔍 Running comprehensive technical analysis...")

            # Import and run FULL suite of analysis modules
            from bnb_trading.elliott_wave_analyzer import ElliottWaveAnalyzer
            from bnb_trading.fibonacci import FibonacciAnalyzer
            from bnb_trading.ichimoku_module import IchimokuAnalyzer
            from bnb_trading.indicators import TechnicalIndicators
            from bnb_trading.moving_averages import MovingAveragesAnalyzer
            from bnb_trading.optimal_levels import OptimalLevelsAnalyzer
            from bnb_trading.trend_analyzer import TrendAnalyzer
            from bnb_trading.weekly_tails import WeeklyTailsAnalyzer
            from bnb_trading.whale_tracker import WhaleTracker

            # 1. 📐 Fibonacci Analysis (35% weight - PRIMARY)
            try:
                fib_analyzer = FibonacciAnalyzer(self.config)
                fib_result = fib_analyzer.analyze_fibonacci_trend(daily_df)
                # Extract the signal part for combiner compatibility
                fib_signal = fib_result.get("fibonacci_signal", {})
                analyses["fibonacci"] = {
                    "signal": fib_signal.get("signal", "HOLD"),
                    "strength": fib_signal.get("strength", 0.0),
                }
                logger.info("✅ Fibonacci analysis completed")
            except Exception as e:
                logger.warning(f"Fibonacci analysis failed: {e}")
                analyses["fibonacci"] = {"signal": "HOLD", "error": str(e)}

            # 2. 🔍 Weekly Tails Analysis (40% weight - DOMINANT)
            try:
                tails_analyzer = WeeklyTailsAnalyzer(self.config)
                tails_result = tails_analyzer.analyze_weekly_tails_trend(weekly_df)
                # Extract the signal part for combiner compatibility
                analyses["weekly_tails"] = tails_result.get(
                    "tails_signal", {"signal": "HOLD", "strength": 0.0}
                )
                logger.info("✅ Weekly tails analysis completed")
            except Exception as e:
                logger.warning(f"Weekly tails analysis failed: {e}")
                analyses["weekly_tails"] = {"signal": "HOLD", "error": str(e)}

            # 3. 📊 Technical Indicators (RSI, MACD, BB)
            try:
                tech_indicators = TechnicalIndicators(self.config)
                tech_indicators.calculate_indicators(daily_df)
                rsi_signals = tech_indicators.get_rsi_signals(daily_df)
                macd_signals = tech_indicators.get_macd_signals(daily_df)
                bb_signals = tech_indicators.get_bollinger_signals(daily_df)
                volume_signals = tech_indicators.get_volume_signal(daily_df)

                analyses["indicators"] = {
                    "rsi": rsi_signals,
                    "macd": macd_signals,
                    "bollinger_bands": bb_signals,
                    "volume": volume_signals,
                }
                logger.info("✅ Technical indicators completed")
            except Exception as e:
                logger.warning(f"Technical indicators failed: {e}")
                analyses["indicators"] = {"signal": "HOLD", "error": str(e)}

            # 4. 🎯 Optimal Levels Analysis (Entry/Exit zones)
            try:
                levels_analyzer = OptimalLevelsAnalyzer(self.config)
                levels_result = levels_analyzer.analyze_optimal_levels(
                    daily_df, weekly_df
                )
                analyses["optimal_levels"] = levels_result
                logger.info("✅ Optimal levels analysis completed")
            except Exception as e:
                logger.warning(f"Optimal levels analysis failed: {e}")
                analyses["optimal_levels"] = {"error": str(e)}

            # 5. 🌊 Elliott Wave Analysis
            try:
                elliott_analyzer = ElliottWaveAnalyzer(self.config)
                elliott_result = elliott_analyzer.analyze_elliott_wave(
                    daily_df, weekly_df
                )
                analyses["elliott_wave"] = elliott_result
                logger.info("✅ Elliott Wave analysis completed")
            except Exception as e:
                logger.warning(f"Elliott Wave analysis failed: {e}")
                analyses["elliott_wave"] = {"error": str(e)}

            # 6. 🐋 Whale Activity Tracking
            try:
                whale_tracker = WhaleTracker(self.config)
                whale_result = whale_tracker.get_whale_activity_summary(
                    7
                )  # Last 7 days
                analyses["whale_activity"] = whale_result
                logger.info("✅ Whale activity analysis completed")
            except Exception as e:
                logger.warning(f"Whale tracking failed: {e}")
                analyses["whale_activity"] = {"error": str(e)}

            # 7. 🏮 Ichimoku Cloud Analysis
            try:
                ichimoku_analyzer = IchimokuAnalyzer(self.config)
                ichimoku_data = ichimoku_analyzer.calculate_all_ichimoku_lines(daily_df)
                ichimoku_signals = ichimoku_analyzer.analyze_ichimoku_signals(
                    ichimoku_data
                )
                analyses["ichimoku"] = ichimoku_signals
                logger.info("✅ Ichimoku analysis completed")
            except Exception as e:
                logger.warning(f"Ichimoku analysis failed: {e}")
                analyses["ichimoku"] = {"error": str(e)}

            # 8. 📈 Trend Analysis
            try:
                trend_analyzer = TrendAnalyzer(self.config)
                trend_result = trend_analyzer.analyze_trend(daily_df, weekly_df)
                analyses["trend"] = trend_result
                logger.info("✅ Trend analysis completed")
            except Exception as e:
                logger.warning(f"Trend analysis failed: {e}")
                analyses["trend"] = {"error": str(e)}

            # 9. 📊 Moving Averages Analysis
            try:
                ma_analyzer = MovingAveragesAnalyzer(self.config)
                ma_result = ma_analyzer.analyze_moving_averages(daily_df)
                analyses["moving_averages"] = ma_result
                logger.info("✅ Moving averages analysis completed")
            except Exception as e:
                logger.warning(f"Moving averages analysis failed: {e}")
                analyses["moving_averages"] = {"error": str(e)}

            # 10. 🧠 Sentiment Analysis
            try:
                from bnb_trading.sentiment_module import SentimentAnalyzer

                sentiment_analyzer = SentimentAnalyzer(self.config)
                # Get dummy sentiment data for now
                fear_greed = 50.0  # Neutral
                social = {"sentiment": "NEUTRAL", "confidence": 0.5}
                news = {"sentiment": "NEUTRAL", "score": 0.0}
                momentum = {"trend": "SIDEWAYS", "strength": 0.5}
                sentiment_result = sentiment_analyzer.calculate_composite_sentiment(
                    fear_greed, social, news, momentum
                )
                analyses["sentiment"] = sentiment_result
                logger.info("✅ Sentiment analysis completed")
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
                analyses["sentiment"] = {"error": str(e)}

            successful_analyses = [k for k, v in analyses.items() if "error" not in v]
            logger.info(
                f"✅ Completed {len(successful_analyses)}/{len(analyses)} analysis modules"
            )

            return analyses

        except Exception as e:
            logger.exception(f"Error executing analyses: {e}")
            return {}

    def _validate_results(
        self, signal: dict[str, Any], daily_df: pd.DataFrame
    ) -> dict[str, Any]:
        """Validate pipeline results."""
        try:
            # Basic validation
            if not signal:
                return {
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reason": "No signal generated",
                }

            # Ensure required fields
            validated_signal = signal.copy()
            validated_signal.setdefault("signal", "HOLD")
            validated_signal.setdefault("confidence", 0.0)
            validated_signal.setdefault(
                "price", daily_df["Close"].iloc[-1] if not daily_df.empty else 0.0
            )

            return validated_signal

        except Exception as e:
            logger.exception(f"Error validating results: {e}")
            return {
                "signal": "HOLD",
                "confidence": 0.0,
                "reason": f"Validation error: {e}",
            }

    def _export_results_to_csv(
        self,
        signal: dict[str, Any],
        daily_df: pd.DataFrame,
        weekly_df: pd.DataFrame,
        analyses: dict[str, Any],
    ) -> None:
        """
        Export analysis results to CSV file for tracking and analysis.

        Args:
            signal: Validated trading signal
            daily_df: Daily OHLCV DataFrame
            weekly_df: Weekly OHLCV DataFrame
            analyses: Analysis results from all modules
        """
        try:
            from datetime import datetime
            from pathlib import Path

            # Ensure data directory exists
            data_dir = Path("data")
            data_dir.mkdir(parents=True, exist_ok=True)

            # Create CSV record
            timestamp = datetime.now()
            current_price = daily_df["Close"].iloc[-1] if not daily_df.empty else 0.0

            # Build analysis summary
            analysis_summary = {}
            for module, result in analyses.items():
                if isinstance(result, dict):
                    analysis_summary[f"{module}_signal"] = result.get(
                        "signal", "UNKNOWN"
                    )
                    analysis_summary[f"{module}_confidence"] = result.get(
                        "confidence", 0.0
                    )
                    analysis_summary[f"{module}_strength"] = result.get("strength", 0.0)

            # Create record
            record = {
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "run_id": timestamp.strftime("%Y%m%d_%H%M%S"),
                "signal": signal.get("signal", "UNKNOWN"),
                "confidence": signal.get("confidence", 0.0),
                "current_price": current_price,
                "reason": signal.get("reason", ""),
                "daily_candles": len(daily_df),
                "weekly_candles": len(weekly_df),
                **analysis_summary,
            }

            # Convert to DataFrame
            results_df = pd.DataFrame([record])

            # Configurable filename with timestamp
            filename = (
                data_dir / f"pipeline_results_{timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
            )

            # Export with proper encoding and no index
            results_df.to_csv(filename, index=False, encoding="utf-8")
            logger.info(f"📄 Results exported to: {filename}")

        except Exception as e:
            logger.exception(f"Failed to export results to CSV: {e}")
            # Don't re-raise - CSV export failure shouldn't break the pipeline
