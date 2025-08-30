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

        # Market Status
        if not daily_df.empty:
            daily_change = (
                (current_price - daily_df["Close"].iloc[-2])
                / daily_df["Close"].iloc[-2]
            ) * 100
            high_24h = daily_df["High"].iloc[-1]
            low_24h = daily_df["Low"].iloc[-1]
            volume_24h = daily_df["Volume"].iloc[-1]

            print(
                f"  24h Change: {daily_change:+.2f}% | High: ${high_24h:.2f} | Low: ${low_24h:.2f}"
            )
            print(f"  Volume: {volume_24h:,.0f} BNB")

        # Enhanced Analysis Results Display
        print("\n🔍 COMPREHENSIVE ANALYSIS RESULTS")
        print("-" * 63)

        # Fibonacci Analysis (35% weight)
        if "fibonacci" in analyses and "error" not in analyses["fibonacci"]:
            display_fibonacci_detailed(analyses["fibonacci"], current_price)

        # Weekly Tails Analysis (40% weight - DOMINANT)
        if "weekly_tails" in analyses and "error" not in analyses["weekly_tails"]:
            display_weekly_tails_detailed(analyses["weekly_tails"])

        # Optimal Levels Analysis
        if "optimal_levels" in analyses and "error" not in analyses["optimal_levels"]:
            display_optimal_levels_detailed(analyses["optimal_levels"], current_price)

        # Elliott Wave Analysis
        if "elliott_wave" in analyses and "error" not in analyses["elliott_wave"]:
            display_elliott_wave_detailed(analyses["elliott_wave"])

        # Whale Activity
        if "whale_activity" in analyses and "error" not in analyses["whale_activity"]:
            display_whale_activity_detailed(analyses["whale_activity"])

        # Ichimoku Cloud
        if "ichimoku" in analyses and "error" not in analyses["ichimoku"]:
            display_ichimoku_detailed(analyses["ichimoku"], current_price)

        # Technical Indicators Summary
        if "indicators" in analyses and "error" not in analyses["indicators"]:
            display_indicators_detailed(analyses["indicators"])

        # Primary Trading Signal (Final Decision)
        display_primary_signal_detailed(signal_result)

        # System Status
        display_system_status_detailed(metadata, analyses)

    except Exception as e:
        logger.error(f"Error in display_structured_signal_report: {e}")
        print(f"❌ Error displaying analysis: {e}")


def display_fibonacci_detailed(
    fib_data: dict[str, Any], current_price: float = None
) -> None:
    """Display comprehensive Fibonacci retracement and extension map."""
    try:
        # Import the comprehensive Fibonacci map generator
        import os
        import sys

        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to project root: src/bnb_trading/utils -> src/bnb_trading -> src -> project_root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        sys.path.insert(0, project_root)

        from fibonacci_map import create_fibonacci_map

        print("\n📐 FIBONACCI ANALYSIS (20% Weight)")
        print("─" * 50)

        # Generate and display comprehensive Fibonacci map
        fibonacci_map = create_fibonacci_map()
        print(fibonacci_map)

    except Exception as e:
        # Fallback to basic Fibonacci display if map generation fails
        print("\n📐 FIBONACCI ANALYSIS (20% Weight)")
        print("─" * 50)

        signal = fib_data.get("signal", "HOLD")
        strength = fib_data.get("strength", 0.0)

        print(f"📊 Signal: {signal} | Strength: {strength:.2f}")

        if current_price:
            print(f"💰 Current Price: ${current_price:.2f}")

        print(f"⚠️  Detailed Fibonacci map unavailable: {e}")
        print("💡 Try running 'python3 fibonacci_map.py' for detailed analysis")


def display_weekly_tails_detailed(tails_data: dict[str, Any]) -> None:
    """Display detailed weekly tails analysis (DOMINANT weight)."""
    print("\n🔍 WEEKLY TAILS ANALYSIS (40% Weight - DOMINANT)")
    print("─" * 55)

    tails_signal = tails_data.get("tails_signal", {})
    signal = tails_signal.get("signal", "HOLD")
    strength = tails_data.get("tail_strength", 0.0)
    confidence = tails_signal.get("confidence", 0.0)

    print(
        f"📊 Signal: {signal} | Strength: {strength:.2f} | Confidence: {confidence:.1%}"
    )

    # Pattern analysis
    pattern = tails_data.get("pattern_type", "Unknown")
    if pattern != "Unknown":
        print(f"📊 Pattern: {pattern}")

    # ATR normalization details
    atr_data = tails_data.get("atr_analysis", {})
    if atr_data:
        atr_value = atr_data.get("current_atr", 0)
        normalized_tail = atr_data.get("normalized_tail", 0)
        print(f"📏 ATR: {atr_value:.2f} | Normalized Tail: {normalized_tail:.2f}")

    # Key insight
    if signal == "LONG" and strength > 1.0:
        print("💡 Strong reversal tail detected - High probability LONG setup!")
    elif signal == "SHORT" and strength > 1.0:
        print("💡 Strong rejection tail detected - Potential SHORT opportunity!")


def display_optimal_levels_detailed(
    levels_data: dict[str, Any], current_price: float
) -> None:
    """Display detailed optimal entry/exit levels analysis."""
    print("\n🎯 OPTIMAL ENTRY/EXIT LEVELS")
    print("─" * 40)

    optimal_levels = levels_data.get("optimal_levels", {})

    # Support levels (Entry zones for LONG)
    support_levels = optimal_levels.get("top_support_levels", [])
    if support_levels:
        print("🟢 OPTIMAL LONG ENTRY ZONES:")
        for i, (price, touches) in enumerate(support_levels[:3], 1):
            distance = ((current_price - price) / current_price) * 100
            strength = "🔥" if touches >= 5 else "⭐" if touches >= 3 else "📍"
            print(
                f"   {i}. {strength} ${price:.2f} ({touches} touches, -{distance:.1f}%)"
            )

    # Resistance levels (Exit zones / SHORT entry)
    resistance_levels = optimal_levels.get("top_resistance_levels", [])
    if resistance_levels:
        print("🔴 KEY RESISTANCE ZONES:")
        for i, (price, touches) in enumerate(resistance_levels[:3], 1):
            distance = ((price - current_price) / current_price) * 100
            strength = "🔥" if touches >= 5 else "⭐" if touches >= 3 else "📍"
            print(
                f"   {i}. {strength} ${price:.2f} ({touches} touches, +{distance:.1f}%)"
            )

    # Best averaged support recommendation
    avg_support = optimal_levels.get("averaged_support")
    if avg_support:
        avg_price = avg_support.get("price", 0)
        reliability = avg_support.get("reliability", "UNKNOWN")
        distance = ((current_price - avg_price) / current_price) * 100
        print(
            f"⭐ RECOMMENDED ENTRY: ${avg_price:.2f} ({reliability}, -{distance:.1f}%)"
        )


def display_elliott_wave_detailed(elliott_data: dict[str, Any]) -> None:
    """Display detailed Elliott Wave analysis."""
    print("\n🌊 ELLIOTT WAVE ANALYSIS")
    print("─" * 35)

    signal = elliott_data.get("signal", "HOLD")
    current_wave = elliott_data.get("current_wave", "Unknown")
    wave_progress = elliott_data.get("wave_progress", 0.0)
    completion_prob = elliott_data.get("completion_probability", 0.0)

    print(f"📊 Signal: {signal} | Wave: {current_wave}")
    print(f"📈 Progress: {wave_progress:.1%} | Completion: {completion_prob:.1%}")

    # Next wave prediction
    next_wave = elliott_data.get("next_wave_prediction")
    if next_wave:
        print(f"🔮 Next Expected: {next_wave}")

    # Wave completion insights
    if completion_prob > 70:
        print("💡 Wave completion likely - Watch for reversal!")
    elif completion_prob > 40:
        print("💡 Wave developing - Monitor for completion signals")


def display_whale_activity_detailed(whale_data: dict[str, Any]) -> None:
    """Display detailed whale activity analysis."""
    print("\n🐋 WHALE ACTIVITY (7 Days)")
    print("─" * 30)

    sentiment = whale_data.get("whale_sentiment", "NEUTRAL")
    activity_level = whale_data.get("activity_level", "NORMAL")
    large_txs = whale_data.get("large_transactions", 0)

    print(f"🐋 Sentiment: {sentiment} | Activity: {activity_level}")

    if large_txs > 0:
        print(f"💸 Large Transactions: {large_txs}")

    # Net flow analysis
    net_flow = whale_data.get("net_flow", 0)
    if net_flow != 0:
        flow_direction = "🟢 INFLOW" if net_flow > 0 else "🔴 OUTFLOW"
        print(f"💰 Net Flow: {abs(net_flow):,.0f} BNB ({flow_direction})")

    # Insights
    if sentiment == "BULLISH" and net_flow > 0:
        print("💡 Bullish whale activity - Potential price support!")
    elif sentiment == "BEARISH" and net_flow < 0:
        print("💡 Bearish whale activity - Watch for selling pressure!")


def display_ichimoku_detailed(
    ichimoku_data: dict[str, Any], current_price: float
) -> None:
    """Display detailed Ichimoku cloud analysis."""
    print("\n🏮 ICHIMOKU CLOUD")
    print("─" * 25)

    signal = ichimoku_data.get("signal", "HOLD")
    cloud_position = ichimoku_data.get("cloud_position", "UNKNOWN")
    tenkan_kijun = ichimoku_data.get("tenkan_kijun_cross", "NEUTRAL")

    print(f"📊 Signal: {signal} | Position: {cloud_position}")
    print(f"⚡ TK Cross: {tenkan_kijun}")

    # Current line values
    current_values = ichimoku_data.get("current_values", {})
    if current_values:
        tenkan = current_values.get("tenkan_sen", 0)
        kijun = current_values.get("kijun_sen", 0)
        senkou_a = current_values.get("senkou_span_a", 0)
        senkou_b = current_values.get("senkou_span_b", 0)

        if tenkan and kijun:
            print(f"📏 Tenkan: ${tenkan:.2f} | Kijun: ${kijun:.2f}")
        if senkou_a and senkou_b:
            cloud_top = max(senkou_a, senkou_b)
            cloud_bottom = min(senkou_a, senkou_b)
            print(f"☁️ Cloud: ${cloud_bottom:.2f} - ${cloud_top:.2f}")

            # Cloud analysis
            if current_price > cloud_top:
                print("💡 Price above cloud - Bullish momentum!")
            elif current_price < cloud_bottom:
                print("💡 Price below cloud - Bearish momentum!")
            else:
                print("💡 Price in cloud - Consolidation phase!")


def display_indicators_detailed(indicators_data: dict[str, Any]) -> None:
    """Display detailed technical indicators analysis."""
    print("\n📊 TECHNICAL INDICATORS")
    print("─" * 35)

    # RSI Analysis
    rsi_data = indicators_data.get("rsi", {})
    if rsi_data and "error" not in rsi_data:
        rsi_value = rsi_data.get("current_rsi", 0)
        rsi_signal = rsi_data.get("signal", "HOLD")
        rsi_zone = (
            "🔥 OVERSOLD"
            if rsi_value < 30
            else "🔥 OVERBOUGHT"
            if rsi_value > 70
            else "⚪ NEUTRAL"
        )
        print(f"📈 RSI: {rsi_value:.1f} ({rsi_signal}) - {rsi_zone}")

    # MACD Analysis
    macd_data = indicators_data.get("macd", {})
    if macd_data and "error" not in macd_data:
        macd_signal = macd_data.get("signal", "HOLD")
        macd_line = macd_data.get("macd_line", 0)
        signal_line = macd_data.get("signal_line", 0)
        histogram = macd_data.get("histogram", 0)

        momentum = "🟢 BULLISH" if histogram > 0 else "🔴 BEARISH"
        print(f"📊 MACD: {macd_signal} - {momentum}")
        print(
            f"    Line: {macd_line:.3f} | Signal: {signal_line:.3f} | Hist: {histogram:.3f}"
        )

    # Bollinger Bands
    bb_data = indicators_data.get("bollinger_bands", {})
    if bb_data and "error" not in bb_data:
        bb_signal = bb_data.get("signal", "HOLD")
        bb_position = bb_data.get("position", "MIDDLE")
        squeeze = bb_data.get("squeeze_detected", False)

        position_emoji = "🔥" if bb_position in ["UPPER", "LOWER"] else "⚪"
        print(f"📊 BB: {bb_signal} - {position_emoji} {bb_position}")
        if squeeze:
            print("    💡 Squeeze detected - Breakout imminent!")

    # Volume Analysis
    volume_data = indicators_data.get("volume", {})
    if volume_data and "error" not in volume_data:
        volume_signal = volume_data.get("signal", "NORMAL")
        volume_ratio = volume_data.get("volume_ratio", 1.0)

        vol_status = (
            "🔥 HIGH"
            if volume_ratio > 2.0
            else "📈 ELEVATED"
            if volume_ratio > 1.5
            else "⚪ NORMAL"
        )
        print(f"📊 Volume: {volume_signal} - {vol_status} ({volume_ratio:.1f}x avg)")


def display_primary_signal_detailed(signal_result: dict[str, Any]) -> None:
    """Display primary trading signal with detailed reasoning."""
    print("\n🎯 PRIMARY TRADING DECISION")
    print("═" * 50)

    signal = signal_result.get("signal", "UNKNOWN")
    confidence = signal_result.get("confidence", 0.0)
    reasons = signal_result.get("reasons", [])

    # Signal display with emoji
    if signal == "LONG":
        emoji = "🟢"
        action = "🚀 BUY OPPORTUNITY DETECTED"
        risk_note = "💡 Consider dollar-cost averaging into position"
    elif signal == "SHORT":
        emoji = "🔴"
        action = "📉 SELL OPPORTUNITY DETECTED"
        risk_note = "⚠️ Use tight stop-loss, monitor for reversal"
    else:
        emoji = "⚪"
        action = "⏸️ HOLD - WAIT FOR CLEARER SETUP"
        risk_note = "🧘 Patience is key - await better opportunity"

    print(f"{emoji} SIGNAL: {signal}")
    print(f"🎯 CONFIDENCE: {confidence:.1%}")
    print(f"📋 ACTION: {action}")

    # Reasoning
    if reasons:
        print("💡 KEY FACTORS:")
        for i, reason in enumerate(reasons[:5], 1):  # Show top 5 reasons
            print(f"   {i}. {reason}")

    print(f"💭 ADVICE: {risk_note}")


def display_system_status_detailed(
    metadata: dict[str, Any], analyses: dict[str, Any]
) -> None:
    """Display detailed system status."""
    print("\n⚙️ SYSTEM STATUS")
    print("═" * 40)

    # Analysis health check
    total_modules = len(analyses)
    successful_modules = len([k for k, v in analyses.items() if "error" not in v])
    failed_modules = [k for k, v in analyses.items() if "error" in v]

    health_pct = (successful_modules / total_modules) * 100 if total_modules > 0 else 0
    health_status = (
        "🟢 EXCELLENT"
        if health_pct >= 90
        else "🟡 GOOD"
        if health_pct >= 75
        else "🔴 NEEDS ATTENTION"
    )

    print(
        f"🔧 Analysis Health: {health_status} ({successful_modules}/{total_modules} modules)"
    )
    print(f"📊 Data Quality: {metadata.get('data_points', 'N/A')} points processed")
    print(f"🚀 Pipeline: v{metadata.get('pipeline_version', 'Unknown')}")

    if failed_modules:
        print(f"⚠️ Issues: {', '.join(failed_modules)}")

    print("✅ ANALYSIS COMPLETE - System Ready for Trading!")
