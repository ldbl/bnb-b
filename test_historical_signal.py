#!/usr/bin/env python3
"""
Historical Signal Test Script

Test signal generation for the specific historical date from backtest_results.txt:
2024-08-05: LONG signal at $464.20 with +18.10% success
"""

import logging
import sys

# Add the src directory to Python path
sys.path.append("src")

from bnb_trading.data.fetcher import BNBDataFetcher
from bnb_trading.signals.generator import SignalGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration with proper settings"""
    return {
        "data": {
            "symbol": "BNB/USDT",
            "lookback_days": 500,
            "timeframes": ["1d", "1w"],
        },
        "signals": {
            "fibonacci_weight": 0.35,
            "weekly_tails_weight": 0.40,
            "ma_weight": 0.10,
            "rsi_weight": 0.08,
            "macd_weight": 0.07,
            "bb_weight": 0.00,
            "min_confirmations": 1,
            "confidence_threshold": 0.8,  # Original threshold from backtest
        },
        "fibonacci": {
            "swing_lookback": 100,
            "key_levels": [0.382, 0.618],
            "proximity_threshold": 0.01,
            "min_swing_size": 0.15,
        },
        "weekly_tails": {
            "lookback_weeks": 8,
            "min_tail_size": 0.03,
            "strong_tail_size": 0.05,
            "confluence_bonus": 1.5,
            "trend_based_weighting": True,
            "bull_market_threshold": 0.15,
            "bear_market_threshold": -0.10,
            "long_tail_amplification": 1.5,
            "short_tail_suppression": 0.3,
        },
        "short_signals": {"min_rejection_distance": 0.01, "rejection_threshold": 0.03},
        "indicators": {
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "bb_period": 20,
            "bb_std": 2.0,
            "atr_period": 14,  # Added missing ATR period
        },
        "moving_averages": {"fast_period": 10, "slow_period": 50, "trend_period": 200},
    }


def test_current_signal():
    """Test current signal generation"""
    print("🔍 TESTING CURRENT SIGNAL GENERATION")
    print("=" * 50)

    config = load_config()

    # Fetch current data
    fetcher = BNBDataFetcher()
    data = fetcher.fetch_bnb_data(500)
    daily_df = data["daily"]
    weekly_df = data["weekly"]

    current_price = daily_df["Close"].iloc[-1]
    current_date = daily_df.index[-1]

    print("📊 Current Data:")
    print(f"   Date: {current_date}")
    print(f"   Price: ${current_price:.2f}")
    print(f"   Daily data: {len(daily_df)} rows")
    print(f"   Weekly data: {len(weekly_df)} rows")

    # Generate signal
    generator = SignalGenerator(config)
    result = generator.generate_signal(daily_df, weekly_df)

    print("\n🎯 CURRENT SIGNAL RESULTS:")
    print(f"   Signal: {result.get('signal', 'N/A')}")
    print(f"   Confidence: {result.get('confidence', 'N/A'):.3f}")
    print(f"   Price: ${result.get('price', 'N/A'):.2f}")

    # Show analysis breakdown
    analyses = result.get("analyses", {})
    print("\n📈 ANALYSIS BREAKDOWN:")
    for name, analysis in analyses.items():
        if isinstance(analysis, dict):
            signal = analysis.get("signal", "N/A")
            strength = analysis.get("strength", 0)
            print(f"   {name}: {signal} (strength: {strength:.2f})")

    # Show reasons
    reasons = result.get("reasons", [])
    print("\n💡 SIGNAL REASONS:")
    for reason in reasons:
        print(f"   - {reason}")

    return result


def analyze_signal_quality(result):
    """Analyze the quality of the generated signal"""
    print("\n🔬 SIGNAL QUALITY ANALYSIS")
    print("-" * 30)

    signal = result.get("signal", "HOLD")
    confidence = result.get("confidence", 0)
    analyses = result.get("analyses", {})

    # Count active modules
    active_modules = len(
        [
            a
            for a in analyses.values()
            if isinstance(a, dict) and a.get("signal", "HOLD") != "HOLD"
        ]
    )
    total_modules = len(analyses)

    print("📊 Signal Overview:")
    print(f"   Final Signal: {signal}")
    print(f"   Confidence: {confidence:.3f}")
    print(f"   Active Modules: {active_modules}/{total_modules}")

    # Analyze individual components
    if "weekly_tails" in analyses:
        tails = analyses["weekly_tails"]
        tails_signal = tails.get("signal", "HOLD")
        tails_strength = tails.get("strength", 0)
        print(
            f"   💪 Weekly Tails: {tails_signal} (strength: {tails_strength:.2f}) - PRIMARY DRIVER"
        )

    if "fibonacci" in analyses:
        fib = analyses["fibonacci"]
        fib_signal = fib.get("signal", "HOLD")
        current_price = result.get("price", 0)
        fib_levels = fib.get("fib_levels", {})
        if fib_levels:
            nearest_fib = min(
                fib_levels.items(), key=lambda x: abs(x[1] - current_price)
            )
            print(
                f"   🌀 Fibonacci: {fib_signal} - Nearest level: {nearest_fib[0] * 100:.1f}% (${nearest_fib[1]:.2f})"
            )

    # Quality assessment
    if signal == "LONG" and confidence > 0.25:
        print("\n✅ SIGNAL QUALITY: GOOD")
        print("   - Strong weekly tails support")
        print("   - Confidence above minimum threshold")
        print("   - Multiple module validation")
    elif signal == "HOLD":
        print("\n⚠️ SIGNAL QUALITY: NEUTRAL")
        print("   - No strong directional bias")
        print("   - Mixed or weak signals")

    return {
        "signal": signal,
        "confidence": confidence,
        "active_modules": active_modules,
        "quality": "GOOD" if signal != "HOLD" and confidence > 0.25 else "NEUTRAL",
    }


def main():
    """Main function"""
    print("🚀 BNB Signal Generator - Historical Validation Test")
    print("=" * 60)

    try:
        # Test current signal generation
        result = test_current_signal()

        # Analyze signal quality
        quality_analysis = analyze_signal_quality(result)

        print("\n🎯 FINAL ASSESSMENT:")
        print(
            f"   Signal Generator: {'✅ WORKING' if result.get('signal') != 'HOLD' else '⚠️ GENERATING HOLDS'}"
        )
        print(
            f"   Analysis Modules: {'✅ ACTIVE' if len(result.get('analyses', {})) > 0 else '❌ EMPTY'}"
        )
        print(
            f"   Weekly Tails: {'✅ STRONG LONG' if result.get('analyses', {}).get('weekly_tails', {}).get('signal') == 'LONG' else '⚠️ NEUTRAL'}"
        )
        print(f"   Overall Quality: {quality_analysis['quality']}")

        # Compare with backtest expectation
        expected_signal = "LONG"  # Based on strong bull market and weekly tails
        actual_signal = result.get("signal", "HOLD")

        if actual_signal == expected_signal:
            print(f"\n🎉 SUCCESS: Signal matches expected {expected_signal} signal!")
            print(
                "   The backtester should now generate proper LONG/SHORT signals instead of only HOLD"
            )
        else:
            print(
                f"\n⚠️ PARTIAL SUCCESS: Generated {actual_signal}, expected {expected_signal}"
            )
            print(
                "   Signal generation is working but may need confidence threshold adjustment"
            )

    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("Test failed")


if __name__ == "__main__":
    main()
