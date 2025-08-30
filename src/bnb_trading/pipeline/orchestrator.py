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

try:
    from bnb_trading.core.exceptions import AnalysisError
    from bnb_trading.data.fetcher import BNBDataFetcher
    from bnb_trading.signals.generator import SignalGenerator
except ImportError:
    # Fallback for direct execution
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

            # Step 5: Return results
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
            # Import and run actual analysis modules
            from bnb_trading.fibonacci import FibonacciAnalyzer
            from bnb_trading.indicators import TechnicalIndicators
            from bnb_trading.weekly_tails import WeeklyTailsAnalyzer

            # Initialize analyzers
            fib_analyzer = FibonacciAnalyzer(self.config)
            tails_analyzer = WeeklyTailsAnalyzer(self.config)
            tech_indicators = TechnicalIndicators(self.config)

            # Run analyses with proper method calls
            fib_result = fib_analyzer.analyze_fibonacci_trend(daily_df)
            analyses["fibonacci"] = fib_result.get("fibonacci_signal", {})

            tails_result = tails_analyzer.analyze_weekly_tails_trend(weekly_df)
            analyses["weekly_tails"] = tails_result.get("tails_signal", {})

            # For indicators, we need to add individual signal extraction
            tech_indicators.calculate_indicators(daily_df)
            analyses["indicators"] = {"signal": "HOLD", "strength": 0.0}  # Placeholder

            logger.info(f"✅ Executed {len(analyses)} analysis modules")
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
