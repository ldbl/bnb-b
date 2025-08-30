#!/usr/bin/env python3
"""
Debug Signal Generation Script

This script tests signal generation for a specific historical date to debug
why the backtester is generating only HOLD signals instead of LONG/SHORT signals.
"""

import logging
import sys

# Add the src directory to Python path
sys.path.append("src")

from bnb_trading.data.fetcher import BNBDataFetcher
from bnb_trading.fibonacci import FibonacciAnalyzer
from bnb_trading.indicators import TechnicalIndicators
from bnb_trading.signals.generator import SignalGenerator
from bnb_trading.weekly_tails import WeeklyTailsAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration - simplified for testing"""
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
            "confidence_threshold": 0.25,  # Lowered for testing
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
        },
        "moving_averages": {"fast_period": 10, "slow_period": 50, "trend_period": 200},
    }


def test_individual_modules(daily_df, weekly_df, config):
    """Test individual analysis modules"""
    print("\n=== TESTING INDIVIDUAL MODULES ===")

    # Test Fibonacci Analysis
    print("\n1. Testing Fibonacci Analysis...")
    try:
        fib_analyzer = FibonacciAnalyzer(config)
        fib_result = fib_analyzer.analyze_fibonacci_trend(daily_df)
        print(f"   Fibonacci Analysis Result: {type(fib_result)}")
        print(f"   Keys: {list(fib_result.keys())}")

        if "fibonacci_signal" in fib_result:
            fib_signal = fib_result["fibonacci_signal"]
            print(f"   Fib Signal: {fib_signal.get('signal', 'N/A')}")
            print(f"   Fib Strength: {fib_signal.get('strength', 'N/A')}")
            print(f"   Fib Reason: {fib_signal.get('reason', 'N/A')}")

    except Exception as e:
        print(f"   ERROR in Fibonacci: {e}")

    # Test Weekly Tails Analysis
    print("\n2. Testing Weekly Tails Analysis...")
    try:
        tails_analyzer = WeeklyTailsAnalyzer(config)
        tails_result = tails_analyzer.analyze_weekly_tails_trend(weekly_df)
        print(f"   Weekly Tails Result: {type(tails_result)}")
        print(f"   Keys: {list(tails_result.keys())}")

        if "tails_signal" in tails_result:
            tails_signal = tails_result["tails_signal"]
            print(f"   Tails Signal: {tails_signal.get('signal', 'N/A')}")
            print(f"   Tails Strength: {tails_signal.get('strength', 'N/A')}")
            print(f"   Tails Reason: {tails_signal.get('reason', 'N/A')}")

    except Exception as e:
        print(f"   ERROR in Weekly Tails: {e}")

    # Test Technical Indicators
    print("\n3. Testing Technical Indicators...")
    try:
        indicators = TechnicalIndicators(config)
        daily_with_indicators = indicators.calculate_indicators(daily_df.copy())

        # Get latest values
        latest = daily_with_indicators.iloc[-1]
        print(f"   RSI: {latest.get('RSI', 'N/A')}")
        print(f"   MACD: {latest.get('MACD', 'N/A')}")
        print(f"   BB_position: {latest.get('bb_position', 'N/A')}")

        # Test signal generation
        rsi_signals = indicators.get_rsi_signals(daily_with_indicators)
        macd_signals = indicators.get_macd_signals(daily_with_indicators)

        print(f"   RSI Signals: {rsi_signals}")
        print(f"   MACD Signals: {macd_signals}")

    except Exception as e:
        print(f"   ERROR in Technical Indicators: {e}")


def test_signal_generator_current_implementation(daily_df, weekly_df, config):
    """Test the current broken implementation"""
    print("\n=== TESTING CURRENT SIGNAL GENERATOR ===")

    generator = SignalGenerator(config)

    # Test the current implementation
    try:
        result = generator.generate_signal(daily_df, weekly_df)
        print(f"Signal Generator Result: {result}")
        print(f"Signal: {result.get('signal', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print(f"Reasons: {result.get('reasons', [])}")
        print(f"Analyses keys: {list(result.get('analyses', {}).keys())}")

        # Check if analyses is empty (this is the bug)
        analyses = result.get("analyses", {})
        if not analyses:
            print("❌ BUG FOUND: analyses dictionary is EMPTY!")
            print("   This is why we're getting only HOLD signals")

    except Exception as e:
        print(f"ERROR in Signal Generator: {e}")


def test_manual_signal_combination(daily_df, weekly_df, config):
    """Test manual signal combination to demonstrate what should work"""
    print("\n=== TESTING MANUAL SIGNAL COMBINATION ===")

    try:
        # Run individual analyses
        fib_analyzer = FibonacciAnalyzer(config)
        fib_result = fib_analyzer.analyze_fibonacci_trend(daily_df)

        tails_analyzer = WeeklyTailsAnalyzer(config)
        tails_result = tails_analyzer.analyze_weekly_tails_trend(weekly_df)

        indicators = TechnicalIndicators(config)
        daily_with_indicators = indicators.calculate_indicators(daily_df.copy())
        rsi_signals = indicators.get_rsi_signals(daily_with_indicators)
        macd_signals = indicators.get_macd_signals(daily_with_indicators)

        # Manually create analyses dict
        analyses = {
            "fibonacci": fib_result.get("fibonacci_signal", {}),
            "weekly_tails": tails_result.get("tails_signal", {}),
            "rsi": rsi_signals,
            "macd": macd_signals,
        }

        print("Manual analyses dictionary:")
        for key, value in analyses.items():
            signal = value.get("signal", "N/A") if isinstance(value, dict) else "N/A"
            strength = (
                value.get("strength", "N/A") if isinstance(value, dict) else "N/A"
            )
            print(f"   {key}: signal={signal}, strength={strength}")

        # Test the combine_signals function
        from bnb_trading.signals.combiners import combine_signals

        weights = {"fibonacci": 0.35, "weekly_tails": 0.40, "rsi": 0.08, "macd": 0.07}

        combined = combine_signals(analyses, weights)
        print("\nCombined Signal Result:")
        print(f"   Signal: {combined.get('signal', 'N/A')}")
        print(f"   Strength: {combined.get('strength', 'N/A')}")
        print(f"   Long Score: {combined.get('long_score', 'N/A')}")
        print(f"   Short Score: {combined.get('short_score', 'N/A')}")
        print(f"   Reasons: {combined.get('reasons', [])}")

    except Exception as e:
        print(f"ERROR in Manual Combination: {e}")


def main():
    """Main test function"""
    print("🔍 DEBUG: BNB Signal Generation Issue")
    print("=" * 50)

    # Load configuration
    config = load_config()

    # Fetch data
    print("Fetching data...")
    try:
        fetcher = BNBDataFetcher()
        data = fetcher.fetch_bnb_data(500)  # 500 days lookback
        daily_df = data["daily"]
        weekly_df = data["weekly"]

        print("✅ Data loaded successfully")
        print(f"   Daily data: {len(daily_df)} rows")
        print(f"   Weekly data: {len(weekly_df)} rows")
        print(f"   Current price: ${daily_df['Close'].iloc[-1]:.2f}")
        print(f"   Date range: {daily_df.index[0]} to {daily_df.index[-1]}")

    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return

    # Test individual modules
    test_individual_modules(daily_df, weekly_df, config)

    # Test current signal generator
    test_signal_generator_current_implementation(daily_df, weekly_df, config)

    # Test manual signal combination
    test_manual_signal_combination(daily_df, weekly_df, config)

    print("\n🎯 CONCLUSION:")
    print(
        "The issue is that SignalGenerator._execute_all_analyses() returns an empty dict"
    )
    print("This needs to be implemented to actually run the analysis modules")


if __name__ == "__main__":
    main()
