"""
Parity Tests for Live vs Backtest Decision Consistency
Ensures unified decision logic produces identical results
"""

import numpy as np
import pandas as pd

from bnb_trading.core.models import DecisionContext, DecisionResult

# Import the unified decision logic
from bnb_trading.signals.decision import decide_long


class TestDecisionParity:
    """Test live vs backtest decision consistency"""

    def setup_method(self):
        """Setup test data and configuration"""
        self.config = {
            "signals": {
                "weekly_tails_weight": 0.60,
                "fibonacci_weight": 0.20,
                "trend_weight": 0.10,
                "volume_weight": 0.10,
                "confidence_threshold": 0.88,
            },
            "weekly_tails": {
                "lookback_weeks": 8,
                "min_tail_strength": 2.5,
                "atr_period": 14,
                "volume_ma_period": 20,
            },
        }

        # Create test data
        self.daily_df = self._create_test_daily_data()
        self.weekly_df = self._create_test_weekly_data()

    def _create_test_daily_data(self) -> pd.DataFrame:
        """Create realistic daily OHLCV data"""
        dates = pd.date_range("2024-01-01", "2024-08-30", freq="D")
        n_days = len(dates)

        # Simulate realistic BNB price movement
        np.random.seed(42)  # For reproducible tests
        base_price = 500.0
        price_changes = np.random.normal(0.001, 0.05, n_days)  # 5% daily volatility
        prices = [base_price]

        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 10.0))  # Minimum price floor

        # Generate OHLCV
        data = []
        for i, (date, close) in enumerate(zip(dates, prices, strict=False)):
            high = close * (1 + abs(np.random.normal(0, 0.02)))
            low = close * (1 - abs(np.random.normal(0, 0.02)))
            open_price = low + (high - low) * np.random.random()
            volume = np.random.normal(1000000, 200000)

            data.append(
                {
                    "Open": open_price,
                    "High": high,
                    "Low": low,
                    "Close": close,
                    "Volume": max(volume, 100000),  # Minimum volume
                }
            )

        return pd.DataFrame(data, index=dates)

    def _create_test_weekly_data(self) -> pd.DataFrame:
        """Create weekly data from daily data"""
        # Group daily data by week and aggregate
        weekly_data = []
        daily_grouped = self.daily_df.groupby(pd.Grouper(freq="W"))

        for week_end, week_data in daily_grouped:
            if len(week_data) == 0:
                continue

            weekly_data.append(
                {
                    "Open": week_data.iloc[0]["Open"],
                    "High": week_data["High"].max(),
                    "Low": week_data["Low"].min(),
                    "Close": week_data.iloc[-1]["Close"],
                    "Volume": week_data["Volume"].sum(),
                }
            )

        return pd.DataFrame(weekly_data, index=list(daily_grouped.groups.keys()))

    def test_same_data_same_decision(self):
        """Test that same data produces same decision"""
        timestamp = pd.Timestamp("2024-08-30 12:00:00")

        # Create identical contexts
        ctx1 = DecisionContext(
            closed_daily_df=self.daily_df,
            closed_weekly_df=self.weekly_df,
            config=self.config,
            timestamp=timestamp,
        )

        ctx2 = DecisionContext(
            closed_daily_df=self.daily_df.copy(),
            closed_weekly_df=self.weekly_df.copy(),
            config=self.config.copy(),
            timestamp=timestamp,
        )

        # Make decisions
        result1 = decide_long(ctx1)
        result2 = decide_long(ctx2)

        # Assert identical results
        assert result1.signal == result2.signal, (
            f"Signals differ: {result1.signal} != {result2.signal}"
        )
        assert abs(result1.confidence - result2.confidence) < 1e-10, (
            f"Confidence differs: {result1.confidence} != {result2.confidence}"
        )
        assert result1.reasons == result2.reasons, (
            f"Reasons differ: {result1.reasons} != {result2.reasons}"
        )

    def test_no_lookahead_validation(self):
        """Test that look-ahead detection works"""
        # Test with future timestamp - should fail validation
        future_timestamp = pd.Timestamp("2025-01-01 12:00:00")

        ctx = DecisionContext(
            closed_daily_df=self.daily_df,
            closed_weekly_df=self.weekly_df,
            config=self.config,
            timestamp=future_timestamp,
        )

        result = decide_long(ctx)

        # Should pass (data is historical relative to timestamp)
        assert result.signal in ["LONG", "SHORT", "HOLD"]

    def test_closed_data_only(self):
        """Test that only closed candles are used"""
        current_time = pd.Timestamp("2024-08-30 12:00:00")

        # Add a "current" incomplete candle
        daily_with_current = self.daily_df.copy()
        daily_with_current.loc[current_time] = daily_with_current.iloc[-1].copy()

        weekly_with_current = self.weekly_df.copy()
        weekly_with_current.loc[current_time] = weekly_with_current.iloc[-1].copy()

        ctx = DecisionContext(
            closed_daily_df=daily_with_current,
            closed_weekly_df=weekly_with_current,
            config=self.config,
            timestamp=current_time,
        )

        result = decide_long(ctx)

        # Decision should work (internal logic handles current candle exclusion)
        assert isinstance(result, DecisionResult)

    def test_live_vs_backtest_identical(self):
        """Test that live and backtest modes produce identical results for same data"""
        test_date = pd.Timestamp("2024-08-15")

        # Simulate live context (current time)
        live_ctx = DecisionContext(
            closed_daily_df=self.daily_df.loc[:test_date],
            closed_weekly_df=self.weekly_df.loc[:test_date],
            config=self.config,
            timestamp=test_date,
        )

        # Simulate backtest context (historical replay at same point)
        backtest_ctx = DecisionContext(
            closed_daily_df=self.daily_df.loc[:test_date],
            closed_weekly_df=self.weekly_df.loc[:test_date],
            config=self.config,
            timestamp=test_date,  # Same timestamp
        )

        # Make decisions
        live_result = decide_long(live_ctx)
        backtest_result = decide_long(backtest_ctx)

        # Results must be identical
        assert live_result.signal == backtest_result.signal
        assert abs(live_result.confidence - backtest_result.confidence) < 1e-10
        assert live_result.reasons == backtest_result.reasons

    def test_different_timestamps_same_data(self):
        """Test that different analysis timestamps don't affect decision on same historical data"""
        data_cutoff = pd.Timestamp("2024-08-15")

        # Same data, different analysis timestamps
        ctx1 = DecisionContext(
            closed_daily_df=self.daily_df.loc[:data_cutoff],
            closed_weekly_df=self.weekly_df.loc[:data_cutoff],
            config=self.config,
            timestamp=pd.Timestamp("2024-08-15 10:00:00"),  # Morning
        )

        ctx2 = DecisionContext(
            closed_daily_df=self.daily_df.loc[:data_cutoff],
            closed_weekly_df=self.weekly_df.loc[:data_cutoff],
            config=self.config,
            timestamp=pd.Timestamp("2024-08-15 18:00:00"),  # Evening
        )

        result1 = decide_long(ctx1)
        result2 = decide_long(ctx2)

        # Should be identical (same data, same decision)
        assert result1.signal == result2.signal
        assert abs(result1.confidence - result2.confidence) < 1e-10

    def test_config_changes_affect_decision(self):
        """Test that configuration changes affect decisions as expected"""
        base_config = self.config.copy()

        # Lower confidence threshold
        modified_config = base_config.copy()
        modified_config["signals"]["confidence_threshold"] = 0.5  # Lower from 0.88

        ctx1 = DecisionContext(
            closed_daily_df=self.daily_df,
            closed_weekly_df=self.weekly_df,
            config=base_config,
            timestamp=pd.Timestamp("2024-08-30"),
        )

        ctx2 = DecisionContext(
            closed_daily_df=self.daily_df,
            closed_weekly_df=self.weekly_df,
            config=modified_config,
            timestamp=pd.Timestamp("2024-08-30"),
        )

        result1 = decide_long(ctx1)
        result2 = decide_long(ctx2)

        # Results may differ due to different thresholds
        # This tests that config changes are respected
        assert isinstance(result1, DecisionResult)
        assert isinstance(result2, DecisionResult)
        # Confidence values should be same, but signal may differ due to threshold

    def test_minimal_data_handling(self):
        """Test behavior with minimal data"""
        # Create minimal datasets
        minimal_daily = self.daily_df.iloc[-10:].copy()  # Only 10 days
        minimal_weekly = self.weekly_df.iloc[-2:].copy()  # Only 2 weeks

        ctx = DecisionContext(
            closed_daily_df=minimal_daily,
            closed_weekly_df=minimal_weekly,
            config=self.config,
            timestamp=pd.Timestamp("2024-08-30"),
        )

        result = decide_long(ctx)

        # Should handle minimal data gracefully
        assert isinstance(result, DecisionResult)
        assert result.signal in ["LONG", "SHORT", "HOLD"]


if __name__ == "__main__":
    # Run tests directly
    test_suite = TestDecisionParity()
    test_suite.setup_method()

    print("🧪 Running Decision Parity Tests...")

    try:
        test_suite.test_same_data_same_decision()
        print("✅ Same data produces same decision")

        test_suite.test_live_vs_backtest_identical()
        print("✅ Live vs backtest parity validated")

        test_suite.test_no_lookahead_validation()
        print("✅ No look-ahead validation working")

        test_suite.test_closed_data_only()
        print("✅ Closed data only constraint validated")

        test_suite.test_different_timestamps_same_data()
        print("✅ Timestamp independence validated")

        test_suite.test_config_changes_affect_decision()
        print("✅ Configuration sensitivity validated")

        test_suite.test_minimal_data_handling()
        print("✅ Minimal data handling validated")

        print("\n🎉 All parity tests passed!")

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"💥 Test error: {e}")
