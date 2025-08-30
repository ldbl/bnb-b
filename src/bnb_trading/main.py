"""
BNB Trading System - Main Entry Point (Refactored)

MODULAR BNB SWING TRADING SYSTEM WITH PIPELINE ARCHITECTURE

This is the PRIMARY ENTRY POINT for the BNB Trading System, using the new
modular pipeline architecture for clean separation of concerns.

ARCHITECTURE:
    - Pipeline orchestration layer (TradingPipeline)
    - Multiple execution modes (PipelineRunner)
    - Modular analysis components
    - Configuration-driven parameters (config.toml)
    - Real-time data from Binance API via CCXT

CORE COMPONENTS:
    1. Pipeline Orchestration (pipeline/orchestrator.py)
    2. Execution Runners (pipeline/runners.py)
    3. Data Layer (data/fetcher.py)
    4. Signal Generation (signals/generator.py)
    5. Analysis Modules (analysis/* packages)
    6. Validation System (validation/*)
    7. Testing Framework (testing/*)

USAGE MODES:
    - Real-time analysis: python3 -m bnb_trading.main_new
    - Live signal generation: PipelineRunner().run_live_analysis()
    - Historical backtesting: PipelineRunner().run_backtest_mode(18)
    - Fast signals only: PipelineRunner().run_signal_only_mode()

OUTPUT FILES:
    - analysis_results.txt: Complete analysis report
    - results_summary.txt: Executive summary
    - backtest_results.txt: Backtesting performance
    - results.csv: Signal history database
    - bnb_trading.log: System logs

PERFORMANCE TARGETS:
    - Overall accuracy: 75%+
    - LONG signals: 85%+ accuracy (1:4 risk/reward)
    - SHORT signals: 75%+ accuracy (1:3 risk/reward)
    - Max drawdown: <10%
    - Sharpe ratio: >1.5

EXAMPLE USAGE:
    >>> from .pipeline.runners import PipelineRunner
    >>> runner = PipelineRunner()
    >>> results = runner.run_live_analysis()
    >>> print(f"Signal: {results['signal']['signal']}")

AUTHOR: BNB Trading System Team
VERSION: 3.0.0 - Modular Architecture
DATE: 2025-08-30
"""

import logging
import os
import sys
from typing import Any

# Handle imports for both direct execution and module import
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def _import_pipeline_runner():
    """Import PipelineRunner after path setup to avoid E402"""
    try:
        # Try relative import first (when run as module)
        from .pipeline.runners import PipelineRunner

        return PipelineRunner
    except ImportError:
        # Fall back to absolute import (when run directly)
        from bnb_trading.pipeline.runners import PipelineRunner

        return PipelineRunner


def setup_logging() -> None:
    """Setup logging configuration for the trading system."""
    logging.basicConfig(
        level=logging.ERROR,  # Show only errors by default
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bnb_trading.log"),
            logging.StreamHandler(),
        ],
    )
    # Set all module loggers to ERROR level to suppress INFO messages
    logging.getLogger("bnb_trading").setLevel(logging.ERROR)
    logging.getLogger("src.bnb_trading").setLevel(logging.ERROR)


def display_signal_summary(results: dict[str, Any], structured: bool = False) -> None:
    """Display signal summary with enhanced telemetry for unified decision logic."""

    # Check if this is a unified decision result
    if results.get("unified_decision") and "decision_result" in results:
        from .utils.telemetry import display_decision_telemetry

        decision_result = results["decision_result"]
        display_decision_telemetry(decision_result)
        return

    if structured:
        # Use enhanced structured display from REc.md plan
        try:
            try:
                from .utils.display import display_structured_signal_report
            except ImportError:
                from bnb_trading.utils.display import display_structured_signal_report

            signal_data = results.get("signal", {})
            data = results.get("data", {})
            analyses = results.get("analyses", {})
            metadata = results.get("metadata", {})

            display_structured_signal_report(signal_data, data, analyses, metadata)
            return
        except Exception as e:
            # Show the error and fall back to simple display
            print(f"⚠️  Structured display error: {e}")

    # Simple signal summary (original format)
    signal_data = results.get("signal", {})

    # Handle both fast mode (signal is string) and full mode (signal is dict)
    if isinstance(signal_data, dict):
        signal = signal_data.get("signal", "UNKNOWN")
        confidence = signal_data.get("confidence", results.get("confidence", 0.0))
        price = signal_data.get("price", results.get("price", 0.0))
    else:
        # Fast mode - signal_data is the signal string itself
        signal = signal_data if isinstance(signal_data, str) else "UNKNOWN"
        confidence = results.get("confidence", 0.0)
        price = results.get("price", 0.0)

    print("\n" + "=" * 60)
    print("🚀 BNB TRADING SYSTEM - SIGNAL SUMMARY")
    print("=" * 60)
    print(f"📊 Current Signal: {signal}")
    print(f"🎯 Confidence: {confidence:.1%}")
    print(f"💰 Current Price: ${price:.2f}")
    print("⏰ Analysis Complete")
    print("=" * 60)

    if signal == "LONG":
        print("✅ LONG signal detected - Consider buying opportunity")
    elif signal == "SHORT":
        print("🔴 SHORT signal detected - Consider selling opportunity")
    else:
        print("⏸️  HOLD signal - Wait for better opportunity")

    print("=" * 60 + "\n")


def run_live_analysis() -> dict[str, Any]:
    """Run live trading analysis using pipeline architecture."""
    try:
        print("🔴 LIVE: Starting real-time BNB analysis...")

        # Initialize pipeline runner
        pipeline_runner_class = _import_pipeline_runner()
        runner = pipeline_runner_class()

        # Execute live analysis
        results = runner.run_live_analysis()

        # Display results with structured format
        display_signal_summary(results, structured=True)

        return results

    except Exception as e:
        logging.error(f"Live analysis failed: {e}")
        print(f"❌ Error: {e}")
        return {"error": str(e)}


def main() -> None:
    """Main entry point for BNB Trading System."""
    setup_logging()

    print("\n🚀 BNB Trading System v3.0 - Modular Architecture")
    print("=" * 60)

    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        pipeline_runner_class = _import_pipeline_runner()
        runner = pipeline_runner_class()

        if mode == "backtest":
            months = int(sys.argv[2]) if len(sys.argv) > 2 else 18
            print(f"📈 Running {months}-month backtest...")
            results = runner.run_backtest_mode(months)
            print(f"✅ Backtest completed: {results}")

        elif mode == "fast":
            print("⚡ Fast signal generation mode...")
            results = runner.run_signal_only_mode()
            display_signal_summary(results)

        elif mode == "validate":
            feature = sys.argv[2] if len(sys.argv) > 2 else "system"
            print(f"🧪 Validation mode for: {feature}")
            results = runner.run_validation_mode(feature)
            print(f"✅ Validation completed: {results}")

        else:
            print("❌ Unknown mode. Available: backtest, fast, validate")
            return
    else:
        # Default: live analysis
        run_live_analysis()


if __name__ == "__main__":
    main()
