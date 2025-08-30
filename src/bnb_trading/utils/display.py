"""Enhanced display utilities for BNB Trading System console output."""

import logging
from datetime import datetime
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def display_structured_signal_report(
    signal_result: dict[str, Any],
    data: dict[str, pd.DataFrame],
    analyses: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    """
    Display structured console report as specified in REc.md plan.

    Creates a beautiful, informative console output with:
    - Data health summary
    - Analysis snapshot
    - Confluence matrix
    - Validation results
    - Final decision with reasoning
    - Performance metrics
    """
    try:
        # Extract key data
        daily_df = data.get("daily", pd.DataFrame())
        weekly_df = data.get("weekly", pd.DataFrame())
        current_price = daily_df["Close"].iloc[-1] if not daily_df.empty else 0.0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Header
        print("═" * 63)
        print(f"🚀 BNB TRADING SIGNAL | {timestamp} | BNB/USDT")
        print("═" * 63)

        # Data Health Section
        print("📊 DATA HEALTH")
        daily_gap = 0  # Placeholder for gap calculation
        weekly_gap = 0
        print(
            f"  Daily:   {len(daily_df)} candles | Last: ${current_price:.2f} | Gap: {daily_gap}"
        )
        print(
            f"  Weekly:  {len(weekly_df)} candles  | Last: ${current_price:.2f} | Gap: {weekly_gap}"
        )
        print()

        # Analysis Snapshot Section
        print("🔬 ANALYSIS SNAPSHOT")

        # Extract key indicator values
        rsi_value = _extract_indicator_value(analyses, "rsi", "RSI")
        macd_value = _extract_indicator_value(analyses, "macd", "MACD")
        bb_position = _extract_indicator_value(analyses, "bb", "BB_Position")

        # Fibonacci analysis
        fib_info = analyses.get("fibonacci", {})
        fib_level = fib_info.get("current_level", "N/A")

        # Weekly tails
        tails_info = analyses.get("weekly_tails", {})
        tails_signal = tails_info.get("signal", "N/A")

        # Moving averages
        ma_info = analyses.get("ma", {})
        ma_trend = ma_info.get("trend", "N/A")

        print(
            f"  RSI:        {rsi_value:<8} | MACD: {macd_value:<8} | BB: {bb_position}"
        )
        print(
            f"  Fibonacci:  {fib_level:<8} | Tails: {tails_signal:<8} | MA: {ma_trend}"
        )
        print()

        # Confluence Matrix Section
        print("📈 CONFLUENCE MATRIX")
        print("  ┌─────────────┬────────┬──────┬────────┐")
        print("  │ Module      │ Signal │ Str  │ Weight │")
        print("  ├─────────────┼────────┼──────┼────────┤")

        # Display each analysis module
        for module_name, analysis in analyses.items():
            if isinstance(analysis, dict):
                signal = analysis.get("signal", "HOLD")
                strength = analysis.get("strength", 0.0)
                weight = _get_module_weight(module_name) * 100
                print(
                    f"  │ {module_name:<11} │ {signal:<6} │ {strength:.2f} │ {weight:5.0f}% │"
                )

        print("  └─────────────┴────────┴──────┴────────┘")
        print()

        # Validation Section
        print("✅ VALIDATION")

        # Risk filters status
        ath_check = (
            "✓ ATH Check"
            if _check_ath_distance(current_price, daily_df)
            else "✗ ATH Check"
        )
        volume_check = "✓ Volume" if _check_volume_conditions(daily_df) else "✗ Volume"
        regime_check = "✗ Regime"  # Placeholder

        print(f"  Risk Filters:    {ath_check}  {volume_check}  {regime_check}")

        # Confluence summary
        total_modules = len([a for a in analyses.values() if isinstance(a, dict)])
        aligned_modules = len(
            [
                a
                for a in analyses.values()
                if isinstance(a, dict) and a.get("signal") != "HOLD"
            ]
        )

        print(f"  Confluence:      {aligned_modules}/{total_modules} modules aligned")
        print()

        # Decision Section
        final_signal = signal_result.get("signal", "HOLD")
        confidence = signal_result.get("confidence", 0.0)
        reasons = signal_result.get("reasons", [])
        main_reason = reasons[0] if reasons else "No specific reason provided"

        print(f"🎯 DECISION: {final_signal} | Confidence: {confidence:.3f}")
        print(f"   Reason: {main_reason}")
        print()

        # Performance metrics
        pipeline_time = metadata.get("pipeline_time", 0)
        analysis_time = metadata.get("analysis_time", 0)
        decision_time = metadata.get("decision_time", 0.02)

        print(
            f"⏱️  Pipeline: {pipeline_time:.2f}s | Analysis: {analysis_time:.2f}s | Decision: {decision_time:.2f}s"
        )
        print("═" * 63)

    except Exception as e:
        logger.exception(f"Error displaying structured report: {e}")
        # Fallback to simple display
        print(
            f"🚀 BNB TRADING SIGNAL: {signal_result.get('signal', 'ERROR')} ({signal_result.get('confidence', 0):.3f})"
        )
        print(f"   Error in display: {e}")


def _extract_indicator_value(
    analyses: dict[str, Any], module: str, indicator: str
) -> str:
    """Extract indicator value with proper formatting."""
    try:
        module_data = analyses.get(module, {})
        if isinstance(module_data, dict):
            value = module_data.get(indicator.lower(), module_data.get("value", 0))
            if isinstance(value, (int, float)):
                if indicator == "RSI":
                    trend_arrow = "↑" if value > 50 else "↓" if value < 50 else "→"
                    return f"{value:.1f} {trend_arrow}"
                if indicator == "MACD":
                    trend_arrow = "↑" if value > 0 else "↓"
                    return f"{value:.1f} {trend_arrow}"
                return f"{value:.2f}"
        return "N/A"
    except Exception:
        return "N/A"


def _get_module_weight(module_name: str) -> float:
    """Get module weight for display."""
    weight_map = {
        "fibonacci": 0.35,
        "weekly_tails": 0.40,
        "ma": 0.10,
        "rsi": 0.08,
        "macd": 0.07,
        "bb": 0.00,
        "indicators": 0.15,  # Combined technical indicators
    }
    return weight_map.get(module_name, 0.0)


def _check_ath_distance(current_price: float, daily_df: pd.DataFrame) -> bool:
    """Check if current price is at safe distance from ATH."""
    try:
        if daily_df.empty:
            return False

        recent_high = daily_df["Close"].tail(180).max()
        distance_from_ath = (recent_high - current_price) / recent_high
        return distance_from_ath > 0.05  # More than 5% from ATH
    except Exception:
        return False


def _check_volume_conditions(daily_df: pd.DataFrame) -> bool:
    """Check volume conditions."""
    try:
        if daily_df.empty or "Volume" not in daily_df.columns:
            return False

        recent_volume = daily_df["Volume"].tail(1).iloc[0]
        avg_volume = daily_df["Volume"].tail(20).mean()
        return recent_volume > avg_volume * 1.1  # 10% above average
    except Exception:
        return False


def display_simple_signal(signal: str, confidence: float, price: float) -> None:
    """Simple signal display for quick output."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] 🚀 {signal} | {confidence:.3f} | ${price:.2f}")


def display_error(error_message: str) -> None:
    """Display error message with consistent formatting."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] ❌ ERROR: {error_message}")


def display_debug_info(debug_data: dict[str, Any]) -> None:
    """Display debug information when verbose mode is enabled."""
    print("\n🔍 DEBUG INFO:")
    for key, value in debug_data.items():
        print(f"  {key}: {value}")
    print()
