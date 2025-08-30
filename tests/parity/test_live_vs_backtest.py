"""Parity tests to ensure live and backtest generate identical decisions."""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from bnb_trading.signals.decision import (
    DecisionContext,
    run_backtest_decision,
    run_live_decision,
)


def load_fixture_context(date: str = "2024-08-05") -> DecisionContext:
    """Load fixture context for the specified date."""
    from bnb_trading.data.fetcher import BNBDataFetcher
    from bnb_trading.pipeline.orchestrator import TradingPipeline

    # Initialize components
    fetcher = BNBDataFetcher("BNB/USDT")
    pipeline = TradingPipeline()

    # Fetch data up to target date
    import pandas as pd

    target_date = pd.to_datetime(date)

    data = fetcher.fetch_bnb_data(500)
    daily_df = data["daily"][data["daily"].index <= target_date]
    weekly_df = data["weekly"][data["weekly"].index <= target_date]

    # Execute analyses
    analyses = pipeline._execute_analyses(daily_df, weekly_df)

    return DecisionContext(
        daily_df=daily_df,
        weekly_df=weekly_df,
        analyses=analyses,
        config=pipeline.config,
    )


def test_identical_decisions():
    """Test that live and backtest decisions are identical for the same context."""
    print("🧪 Testing parity between live and backtest decisions...")

    try:
        # Load test context
        print("📊 Loading fixture context for 2024-08-05...")
        context = load_fixture_context("2024-08-05")

        # Run both decision methods
        print("🔍 Running live decision logic...")
        live_result = run_live_decision(context)

        print("🔍 Running backtest decision logic...")
        backtest_result = run_backtest_decision(context)

        # Compare results
        print("\n📊 Comparison Results:")
        print(
            f"Live:      {live_result.signal} (confidence: {live_result.confidence:.3f})"
        )
        print(
            f"Backtest:  {backtest_result.signal} (confidence: {backtest_result.confidence:.3f})"
        )

        # Assertions
        signal_match = live_result.signal == backtest_result.signal
        confidence_diff = abs(live_result.confidence - backtest_result.confidence)
        confidence_match = confidence_diff < 0.001  # 0.1% tolerance

        print(f"\n✅ Signal Match: {signal_match}")
        print(f"✅ Confidence Match: {confidence_match} (diff: {confidence_diff:.6f})")

        if signal_match and confidence_match:
            print("🎉 PARITY TEST PASSED - Live and backtest are identical!")
            return True
        print("❌ PARITY TEST FAILED - Live and backtest differ!")
        print(
            f"   Signal difference: {live_result.signal} vs {backtest_result.signal}"
        )
        print(f"   Confidence difference: {confidence_diff:.6f}")
        return False

    except Exception as e:
        print(f"❌ Parity test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_multiple_dates():
    """Test parity across multiple dates to ensure consistency."""
    test_dates = ["2024-08-05", "2024-07-01", "2024-06-15"]
    results = []

    print("🧪 Testing parity across multiple dates...")

    for date in test_dates:
        print(f"\n📅 Testing date: {date}")
        try:
            context = load_fixture_context(date)
            live_result = run_live_decision(context)
            backtest_result = run_backtest_decision(context)

            signal_match = live_result.signal == backtest_result.signal
            confidence_diff = abs(live_result.confidence - backtest_result.confidence)
            confidence_match = confidence_diff < 0.001

            results.append(
                {
                    "date": date,
                    "signal_match": signal_match,
                    "confidence_match": confidence_match,
                    "confidence_diff": confidence_diff,
                    "live_signal": live_result.signal,
                    "backtest_signal": backtest_result.signal,
                }
            )

            status = "✅" if signal_match and confidence_match else "❌"
            print(
                f"{status} {date}: {live_result.signal} (diff: {confidence_diff:.6f})"
            )

        except Exception as e:
            print(f"❌ {date}: Error - {e}")
            results.append({"date": date, "error": str(e)})

    # Summary
    successful_tests = [
        r
        for r in results
        if "error" not in r and r["signal_match"] and r["confidence_match"]
    ]
    print(f"\n📊 Summary: {len(successful_tests)}/{len(test_dates)} tests passed")

    return len(successful_tests) == len(test_dates)


if __name__ == "__main__":
    # Ensure test directories exist
    Path("tests/parity").mkdir(parents=True, exist_ok=True)

    # Run tests
    print("=" * 60)
    print("🧪 BNB Trading System - Parity Test Suite")
    print("=" * 60)

    # Test 1: Single date parity
    test1_result = test_identical_decisions()

    # Test 2: Multiple dates parity
    test2_result = test_multiple_dates()

    # Final result
    all_passed = test1_result and test2_result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL PARITY TESTS PASSED!")
    else:
        print("❌ SOME PARITY TESTS FAILED!")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)
