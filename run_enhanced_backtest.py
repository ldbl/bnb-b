#!/usr/bin/env python3
"""
Enhanced Backtest with Detailed Signal Analysis
Записва подробна информация за всеки сигнал за анализ
"""

import logging
import sys
from datetime import datetime

# Add src to path
from pathlib import Path
from typing import Any

import pandas as pd

current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    import toml

    from bnb_trading.core.models import DecisionContext
    from bnb_trading.data.fetcher import BNBDataFetcher  # Updated path
    from bnb_trading.signals.decision import decide_long
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all modules are properly installed and configured.")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedBacktester:
    """Enhanced backtester with detailed signal analysis"""

    def __init__(self, config_path: str = "config.toml"):
        """Initialize enhanced backtester"""
        with open(config_path) as f:
            self.config = toml.load(f)

        self.data_fetcher = BNBDataFetcher()
        self.signals_log = []

    def run_backtest(self, months: int = 18) -> dict[str, Any]:
        """Run enhanced backtest with detailed logging"""
        logger.info(f"🚀 Starting Enhanced Backtest - {months} months")

        # Fetch data
        logger.info("📊 Fetching BNB/USDT data...")
        try:
            data = self.data_fetcher.fetch_bnb_data(lookback_days=600)
            daily_df = data["daily"]
            weekly_df = data["weekly"]
        except Exception as e:
            logger.error(f"Data fetch error: {e}")
            return {"error": str(e)}

        # Setup backtest period
        end_date = daily_df.index[-1]
        start_date = end_date - pd.Timedelta(days=months * 30)

        backtest_daily = daily_df[start_date:end_date]
        backtest_weekly = weekly_df[start_date:end_date]

        logger.info(f"📅 Backtest period: {start_date.date()} to {end_date.date()}")
        logger.info(
            f"📊 Data: {len(backtest_daily)} daily, {len(backtest_weekly)} weekly candles"
        )

        # Process signals weekly
        results = []
        total_weeks = len(backtest_weekly) - 4  # Leave buffer for future validation

        print(f"\n🔄 Processing {total_weeks} weeks...")

        long_signals = 0
        successful_signals = 0

        for i in range(
            2, total_weeks
        ):  # REDUCED: Start from week 2 to capture more signals like original system
            current_date = backtest_weekly.index[i]

            # Get historical data up to current point
            hist_daily = backtest_daily.loc[:current_date]
            hist_weekly = backtest_weekly.iloc[: i + 1]

            if len(hist_daily) < 50 or len(hist_weekly) < 8:
                continue

            # Generate signal using unified decision logic
            try:
                ctx = DecisionContext(
                    closed_daily_df=hist_daily,
                    closed_weekly_df=hist_weekly,
                    config=self.config,
                    timestamp=current_date,
                )

                decision = decide_long(ctx)

                if decision.signal == "LONG":
                    long_signals += 1

                    # Validate signal after 14 days
                    validation_result = self._validate_signal_after_14_days(
                        decision, current_date, backtest_daily
                    )

                    signal_record = {
                        "signal_date": current_date,
                        "signal": decision.signal,
                        "confidence": decision.confidence,
                        "entry_price": decision.price_level
                        or hist_daily["close"].iloc[-1],
                        "reasons": decision.reasons,
                        "tail_strength": decision.metrics.get("tail_strength", 0),
                        "volume_confidence": decision.metrics.get(
                            "volume_confidence", 0
                        ),
                        "fibonacci_confidence": decision.metrics.get(
                            "fibonacci_confidence", 0
                        ),
                        "trend_confidence": decision.metrics.get("trend_confidence", 0),
                        "validation_result": validation_result,
                        "success": validation_result["success"],
                        "pnl_pct": validation_result["pnl_pct"],
                    }

                    self.signals_log.append(signal_record)

                    if validation_result["success"]:
                        successful_signals += 1

                    # Log signal details
                    status = "✅" if validation_result["success"] else "❌"
                    print(
                        f"{status} {current_date.date()}: LONG @ ${signal_record['entry_price']:.2f}, "
                        f"confidence={decision.confidence:.3f}, "
                        f"tail={decision.metrics.get('tail_strength', 0):.2f}, "
                        f"PnL={validation_result['pnl_pct']:.1f}%"
                    )

            except Exception as e:
                logger.warning(f"Signal generation failed for {current_date}: {e}")
                continue

            # Progress indicator
            if i % 10 == 0:
                current_accuracy = (successful_signals / max(long_signals, 1)) * 100
                print(
                    f"📈 Progress: {i}/{total_weeks} weeks, "
                    f"LONG signals: {long_signals}, accuracy: {current_accuracy:.1f}%"
                )

        # Calculate final results
        overall_accuracy = (successful_signals / max(long_signals, 1)) * 100

        results = {
            "total_weeks_analyzed": total_weeks,
            "long_signals_generated": long_signals,
            "successful_signals": successful_signals,
            "accuracy_pct": overall_accuracy,
            "signals_log": self.signals_log,
        }

        # Save detailed results
        self._save_detailed_results(results)

        print("\n🎯 FINAL RESULTS:")
        print(f"📊 LONG Signals: {long_signals}")
        print(f"✅ Successful: {successful_signals}")
        print(f"🎯 Accuracy: {overall_accuracy:.1f}%")
        print(
            f"💾 Detailed log saved to: data/enhanced_backtest_{datetime.now().strftime('%Y-%m-%d')}.csv"
        )

        return results

    def _validate_signal_after_14_days(
        self, decision, signal_date, daily_df
    ) -> dict[str, Any]:
        """Validate LONG signal after 14 days"""
        try:
            # Fix column name access - handle both 'close' and 'Close'
            close_col = "close" if "close" in daily_df.columns else "Close"

            if signal_date not in daily_df.index:
                return {
                    "success": False,
                    "pnl_pct": 0,
                    "reason": "Signal date not in daily data",
                }

            entry_price = decision.price_level or daily_df.loc[signal_date, close_col]

            # Find price 14 days later
            future_date = signal_date + pd.Timedelta(days=14)

            # Get future data after signal date
            future_prices = daily_df[daily_df.index > signal_date]
            if len(future_prices) == 0:
                return {"success": False, "pnl_pct": 0, "reason": "No future data"}

            # Find exit price - prefer exact 14-day match, else closest within range
            if future_date in future_prices.index:
                exit_price = future_prices.loc[future_date, close_col]
            else:
                # Get data within 14-20 days range for more flexible matching
                days_ahead = future_prices.head(20)  # Look up to 20 days ahead
                if len(days_ahead) >= 10:  # At least 10 days of data
                    # Use price around day 14 (take day 10-14 range)
                    target_slice = (
                        days_ahead.iloc[9:15]
                        if len(days_ahead) >= 15
                        else days_ahead.iloc[-5:]
                    )
                    exit_price = target_slice.iloc[-1][close_col]
                else:
                    return {
                        "success": False,
                        "pnl_pct": 0,
                        "reason": "Insufficient future data",
                    }

            # Calculate P&L
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100
            success = pnl_pct > 0  # Simple success criteria: positive return

            return {
                "success": success,
                "pnl_pct": pnl_pct,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "reason": f"{'Profitable' if success else 'Loss'}: {pnl_pct:.2f}% after ~14 days",
            }

        except Exception as e:
            logger.warning(f"Validation error for {signal_date}: {e}")
            return {"success": False, "pnl_pct": 0, "reason": f"Error: {e!s}"}

    def _save_detailed_results(self, results: dict[str, Any]) -> None:
        """Save detailed results to CSV for analysis"""
        if not results["signals_log"]:
            logger.warning("No signals to save")
            return

        # Convert to DataFrame
        df = pd.DataFrame(results["signals_log"])

        # Add summary statistics
        summary_stats = {
            "total_signals": len(df),
            "successful_signals": df["success"].sum(),
            "accuracy_pct": (df["success"].sum() / len(df)) * 100,
            "avg_pnl_pct": df["pnl_pct"].mean(),
            "avg_confidence": df["confidence"].mean(),
            "avg_tail_strength": df["tail_strength"].mean(),
        }

        # Save to CSV
        filename = f"data/enhanced_backtest_{datetime.now().strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename, index=False)

        # Save summary
        summary_filename = (
            f"data/enhanced_backtest_summary_{datetime.now().strftime('%Y-%m-%d')}.txt"
        )
        with open(summary_filename, "w") as f:
            f.write(
                "🚀 Enhanced Backtest Results - Weekly Tails Dominant (60% weight)\n"
            )
            f.write(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            f.write("📊 SUMMARY STATISTICS:\n")
            for key, value in summary_stats.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")

            f.write("🔍 TOP 5 SUCCESSFUL SIGNALS:\n")
            top_signals = df[df["success"]].nlargest(5, "pnl_pct")
            for _, signal in top_signals.iterrows():
                f.write(
                    f"  {signal['signal_date'].date()}: {signal['pnl_pct']:.1f}% PnL, "
                    f"conf={signal['confidence']:.3f}, tail={signal['tail_strength']:.2f}\n"
                )

            f.write("\n🔍 WORST 5 FAILED SIGNALS:\n")
            worst_signals = df[~df["success"]].nsmallest(5, "pnl_pct")
            for _, signal in worst_signals.iterrows():
                f.write(
                    f"  {signal['signal_date'].date()}: {signal['pnl_pct']:.1f}% PnL, "
                    f"conf={signal['confidence']:.3f}, tail={signal['tail_strength']:.2f}\n"
                )


if __name__ == "__main__":
    backtester = EnhancedBacktester("config.toml")
    results = backtester.run_backtest(months=18)

    if "error" not in results:
        print("\n✅ Enhanced backtest completed successfully!")
        print("📊 Check detailed CSV and summary files in data/ directory")
    else:
        print(f"❌ Backtest failed: {results['error']}")
