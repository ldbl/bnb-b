"""Minimal reproducible test case for 2024-08-05 LONG signal fixture."""

import os
import sys

import pandas as pd

# Add src to path for imports
sys.path.append("src")

FIXTURE_DATE = "2024-08-05"
EXPECTED_SIGNAL = "LONG"
EXPECTED_CONFIDENCE = 0.375
FIXTURE_DATA = "tests/fixtures/bnb_2024_08_05.csv"


def create_fixture_context(date: str = FIXTURE_DATE):
    """Create a minimal reproducible test context for the specified date."""
    from bnb_trading.data.fetcher import BNBDataFetcher

    # Initialize data fetcher
    fetcher = BNBDataFetcher("BNB/USDT")

    # Fetch data up to the fixture date
    target_date = pd.to_datetime(date)

    try:
        # Fetch 500 days of data (enough for analysis)
        data = fetcher.fetch_bnb_data(500)

        # Filter data to end at target date
        daily_df = data["daily"]
        weekly_df = data["weekly"]

        # Find the closest date to our target
        daily_filtered = daily_df[daily_df.index <= target_date]
        weekly_filtered = weekly_df[weekly_df.index <= target_date]

        if daily_filtered.empty:
            print(f"❌ No data found for date {date}")
            return None

        print(
            f"✅ Context created for {date}: daily={len(daily_filtered)}, weekly={len(weekly_filtered)}"
        )
        print(f"📊 Last price: ${daily_filtered['Close'].iloc[-1]:.2f}")
        print(f"📅 Last date: {daily_filtered.index[-1].strftime('%Y-%m-%d')}")

        return {
            "daily_df": daily_filtered,
            "weekly_df": weekly_filtered,
            "target_date": target_date,
            "expected_signal": EXPECTED_SIGNAL,
            "expected_confidence": EXPECTED_CONFIDENCE,
        }

    except Exception as e:
        print(f"❌ Error creating fixture context: {e}")
        return None


def run_fixture_test():
    """Run the minimal reproducible test case."""
    from bnb_trading.pipeline.orchestrator import TradingPipeline

    print("🧪 Running minimal reproducible test case for 2024-08-05")
    print("=" * 60)

    # Create fixture context
    context = create_fixture_context()
    if not context:
        return False

    # Initialize pipeline
    pipeline = TradingPipeline()

    try:
        # Override data with fixture data
        daily_df = context["daily_df"]
        weekly_df = context["weekly_df"]

        # Run analyses
        analyses = pipeline._execute_analyses(daily_df, weekly_df)
        print(f"🔍 Analyses completed: {list(analyses.keys())}")

        # Generate signal
        signal_result = pipeline.signal_generator.generate_signal(
            daily_df, weekly_df, analyses
        )

        # Compare with expected results
        actual_signal = signal_result.get("signal", "UNKNOWN")
        actual_confidence = signal_result.get("confidence", 0.0)

        print("\n📊 Results:")
        print(f"Expected: {EXPECTED_SIGNAL} ({EXPECTED_CONFIDENCE:.3f})")
        print(f"Actual:   {actual_signal} ({actual_confidence:.3f})")

        signal_match = actual_signal == EXPECTED_SIGNAL
        confidence_close = (
            abs(actual_confidence - EXPECTED_CONFIDENCE) < 0.1
        )  # 10% tolerance

        print(f"\n✅ Signal Match: {signal_match}")
        print(f"✅ Confidence Close: {confidence_close} (tolerance: ±0.1)")

        if signal_match and confidence_close:
            print("🎉 FIXTURE TEST PASSED!")
            return True
        print("❌ FIXTURE TEST FAILED - System behavior changed")
        return False

    except Exception as e:
        print(f"❌ Fixture test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Create test fixtures directory
    from pathlib import Path
    Path("tests/fixtures").mkdir(parents=True, exist_ok=True)

    # Run the test
    success = run_fixture_test()
    sys.exit(0 if success else 1)
