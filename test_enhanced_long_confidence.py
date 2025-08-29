import sys
import pandas as pd
from datetime import datetime, timedelta
from signal_generator import SignalGenerator
from data_fetcher import BNBDataFetcher
import toml
import logging
logging.basicConfig(level=logging.WARNING, format='%(name)s:%(levelname)s:%(message)s')

print("🧪 Enhanced LONG Confidence Scoring - 18-month backtest")
print("📅 Period: 2024-03-07 to 2025-08-29 (540 days, 77 weeks)")
print()

# Initialize components
fetcher = BNBDataFetcher()
config = toml.load('config.toml')
generator = SignalGenerator(config)

# Load data for 18-month period
data_dict = fetcher.fetch_bnb_data(lookback_days=540)
daily_df = data_dict['daily']
weekly_df = data_dict['weekly']
if daily_df is None or daily_df.empty:
    print("❌ Failed to load data")
    sys.exit(1)

# Filter to exact period
start_date = pd.Timestamp("2024-03-07").tz_localize("UTC")
end_date = pd.Timestamp("2025-08-29").tz_localize("UTC")

if daily_df.index.tz is None:
    daily_df.index = daily_df.index.tz_localize("UTC")
if weekly_df.index.tz is None:
    weekly_df.index = weekly_df.index.tz_localize("UTC")

# Filter data
daily_filtered = daily_df[(daily_df.index >= start_date) & (daily_df.index <= end_date)]
weekly_filtered = weekly_df[(weekly_df.index >= start_date) & (weekly_df.index <= end_date)]

print(f"📊 Data loaded: Daily={len(daily_filtered)} days, Weekly={len(weekly_filtered)} weeks")

# Generate signals
signals = []
total_days = len(daily_filtered)

for i in range(21, total_days):  # Start after sufficient data
    current_date = daily_filtered.index[i]
    
    # Get data up to current point
    daily_slice = daily_filtered.iloc[:i+1]
    weekly_slice = weekly_filtered[weekly_filtered.index <= current_date]
    
    if len(weekly_slice) < 8:  # Need minimum weekly data
        continue
    
    # Generate signal
    try:
        signal_result = generator.generate_signal(daily_slice, weekly_slice)
        
        if signal_result["signal"] in ["LONG", "SHORT"]:
            # Calculate P&L after 7 days
            entry_price = daily_slice.iloc[-1]["Close"]
            
            # Find exit date (7 days later)
            exit_idx = min(i + 7, total_days - 1)
            exit_price = daily_filtered.iloc[exit_idx]["Close"]
            
            if signal_result["signal"] == "LONG":
                pnl = ((exit_price - entry_price) / entry_price) * 100
            else:  # SHORT
                pnl = ((entry_price - exit_price) / entry_price) * 100
            
            # Determine win/loss
            result = "WIN" if pnl > 0 else "LOSS"
            
            signals.append({
                "date": current_date,
                "signal": signal_result["signal"],
                "confidence": signal_result["confidence"],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "result": result,
                "reason": signal_result["reason"][:100] if len(signal_result["reason"]) > 100 else signal_result["reason"]
            })
    except Exception as e:
        if i % 50 == 0:  # Only print every 50th error to avoid spam
            print(f"Error at {current_date}: {str(e)[:50]}...")
        continue

print(f"\n📈 Signal generation completed: {len(signals)} signals found")

if signals:
    # Analysis
    total = len(signals)
    successful = sum(1 for s in signals if s["result"] == "WIN")
    overall_accuracy = (successful / total) * 100
    
    long_signals = [s for s in signals if s["signal"] == "LONG"]
    short_signals = [s for s in signals if s["signal"] == "SHORT"]
    
    long_wins = sum(1 for s in long_signals if s["result"] == "WIN")
    short_wins = sum(1 for s in short_signals if s["result"] == "WIN")
    
    long_acc = (long_wins / len(long_signals)) * 100 if long_signals else 0
    short_acc = (short_wins / len(short_signals)) * 100 if short_signals else 0
    
    print("\n=== ENHANCED LONG CONFIDENCE SCORING RESULTS ===")
    print(f"📊 Total Signals: {total}")
    print(f"✅ Successful Signals: {successful}")
    print(f"🎯 Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"📈 LONG Signals: {len(long_signals)} ({long_acc:.1f}% accuracy - {long_wins} wins)")
    print(f"📉 SHORT Signals: {len(short_signals)} ({short_acc:.1f}% accuracy - {short_wins} wins)")
    
    # Confidence analysis for LONG signals
    if long_signals:
        long_confidences = [s["confidence"] for s in long_signals]
        avg_conf = sum(long_confidences) / len(long_confidences)
        max_conf = max(long_confidences)
        min_conf = min(long_confidences)
        print(f"📊 LONG Confidence: Avg={avg_conf:.3f}, Max={max_conf:.3f}, Min={min_conf:.3f}")
    
    # P&L analysis
    total_pnl = sum(s["pnl"] for s in signals)
    avg_pnl = total_pnl / len(signals)
    
    winning_pnls = [s["pnl"] for s in signals if s["result"] == "WIN"]
    losing_pnls = [s["pnl"] for s in signals if s["result"] == "LOSS"]
    
    print(f"💰 Average P&L: {avg_pnl:+.2f}%")
    
    if winning_pnls:
        avg_win = sum(winning_pnls) / len(winning_pnls)
        print(f"🏆 Winning Signal Average: {avg_win:+.2f}%")
    
    if losing_pnls:
        avg_loss = sum(losing_pnls) / len(losing_pnls)
        print(f"📉 Losing Signal Average: {avg_loss:+.2f}%")
    
    print("\n=== COMPARISON WITH PREVIOUS RESULTS ===")
    print("Previous Overall Accuracy: 55.3% → Current: {:.1f}%".format(overall_accuracy))
    print("Previous LONG Accuracy: 60.0% → Current: {:.1f}%".format(long_acc))
    print("Previous SHORT Accuracy: 46.2% → Current: {:.1f}%".format(short_acc))
    
    improvement = long_acc - 60.0 if long_signals else 0
    if improvement > 5:
        print(f"🚀 SIGNIFICANT LONG Accuracy Improvement: +{improvement:.1f}%")
    elif improvement > 0:
        print(f"📈 LONG Accuracy Improvement: +{improvement:.1f}%")
    elif improvement < -5:
        print(f"📉 SIGNIFICANT LONG Accuracy Decline: {improvement:.1f}%")
    elif improvement < 0:
        print(f"📉 LONG Accuracy Decline: {improvement:.1f}%")
    else:
        print("📊 LONG Accuracy Unchanged")
        
    # High confidence LONG analysis
    high_conf_longs = [s for s in long_signals if s["confidence"] > 0.5]
    if high_conf_longs:
        high_conf_wins = sum(1 for s in high_conf_longs if s["result"] == "WIN")
        high_conf_acc = (high_conf_wins / len(high_conf_longs)) * 100
        print(f"🎯 High Confidence LONG (>0.5): {len(high_conf_longs)} signals, {high_conf_acc:.1f}% accuracy")

    # Save results to file
    import json
    results = {
        "date": "2025-08-29",
        "enhancement": "Enhanced LONG Confidence Scoring",
        "period": "2024-03-07 to 2025-08-29",
        "total_signals": total,
        "overall_accuracy": overall_accuracy,
        "long_accuracy": long_acc,
        "short_accuracy": short_acc,
        "long_confidence_avg": avg_conf if long_signals else 0,
        "avg_pnl": avg_pnl,
        "improvement_vs_baseline": improvement
    }
    
    with open("data/backtest_enhanced_long_confidence_2025-08-29.txt", "w") as f:
        f.write("🚀 BNB Trading System - Backtest Results\n")
        f.write(f"📅 Date: 2025-08-29\n")
        f.write(f"🔧 Enhancement: Enhanced LONG Confidence Scoring\n")
        f.write("\n=== ENHANCEMENT DESCRIPTION ===\n")
        f.write("✅ Replaced ultra-strict LONG blocking filters with smart confidence scoring\n")
        f.write("✅ Implemented 7-factor confidence enhancement algorithm\n")
        f.write("✅ Added quality multipliers for RSI, Bollinger, MACD, Divergence, Fibonacci, Weekly Tails, Trend\n")
        f.write("✅ Reduced minimum confidence threshold from 0.3 to 0.15 (more permissive)\n")
        f.write("\n=== BACKTEST RESULTS ===\n")
        f.write(f"📅 Period: 2024-03-07 to 2025-08-29 (540 days, 77 weeks)\n")
        f.write(f"📊 Total Signals: {total}\n")
        f.write(f"✅ Successful Signals: {successful}\n")
        f.write(f"🎯 Overall Accuracy: {overall_accuracy:.1f}%\n")
        f.write(f"📈 LONG Signals: {len(long_signals)} ({long_acc:.1f}% accuracy - {long_wins} wins)\n")
        f.write(f"📉 SHORT Signals: {len(short_signals)} ({short_acc:.1f}% accuracy - {short_wins} wins)\n")
        if long_signals:
            f.write(f"📊 LONG Confidence: Avg={avg_conf:.3f}, Max={max_conf:.3f}, Min={min_conf:.3f}\n")
        f.write(f"💰 Average P&L: {avg_pnl:+.2f}%\n")
        if winning_pnls:
            f.write(f"🏆 Winning Signal Average: {sum(winning_pnls)/len(winning_pnls):+.2f}%\n")
        if losing_pnls:
            f.write(f"📉 Losing Signal Average: {sum(losing_pnls)/len(losing_pnls):+.2f}%\n")
        f.write("\n=== COMPARISON WITH PREVIOUS RESULTS ===\n")
        f.write(f"Overall Accuracy: 55.3% → {overall_accuracy:.1f}%\n")
        f.write(f"LONG Accuracy: 60.0% → {long_acc:.1f}%\n")
        f.write(f"SHORT Accuracy: 46.2% → {short_acc:.1f}%\n")
        if improvement > 0:
            f.write(f"🚀 LONG Accuracy Improvement: +{improvement:.1f}%\n")
        elif improvement < 0:
            f.write(f"📉 LONG Accuracy Decline: {improvement:.1f}%\n")
        else:
            f.write(f"📊 LONG Accuracy Unchanged\n")
        if high_conf_longs:
            f.write(f"🎯 High Confidence LONG (>0.5): {len(high_conf_longs)} signals, {high_conf_acc:.1f}% accuracy\n")

else:
    print("❌ No signals generated during backtest period")