#!/usr/bin/env python3
"""
Comprehensive Fibonacci Retracement & Extension Visualization for BNB/USDT

Creates a detailed "card-style" visualization with:
- Current Fibonacci levels (retracements & extensions)
- Historical touch analysis (±0.6% tolerance)
- Optimal entry/resistance zones
- Visual price ladder

Requirements:
- Weekly swing detection (closed candles only, k=2 fractals)
- Daily data for touch counting (500 days)
- No look-ahead bias
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from bnb_trading.data.fetcher import BNBDataFetcher

logger = logging.getLogger(__name__)


def find_last_weekly_swing(
    weekly_df: pd.DataFrame, k: int = 2
) -> tuple[float, float, str, str]:
    """
    Find last confirmed weekly swing Low→High using recent significant swing

    Args:
        weekly_df: Weekly OHLCV data (closed candles only)
        k: Fractal period (default 2)

    Returns:
        (low_price, high_price, low_date, high_date)
    """
    if len(weekly_df) < k * 2 + 1:
        raise ValueError(
            f"Need at least {k * 2 + 1} weekly candles for fractal analysis"
        )

    # Use closed candles only (exclude current incomplete week)
    closed_df = weekly_df[:-1].copy()  # Remove last (potentially incomplete) candle

    # Get OHLC columns with validation
    required_columns = {
        "high": ["high", "High"],
        "low": ["low", "Low"],
        "close": ["close", "Close"],
    }
    column_mapping = {}

    for col_type, possible_names in required_columns.items():
        found = None
        for name in possible_names:
            if name in closed_df.columns:
                found = name
                break
        if found is None:
            raise ValueError(
                f"Missing OHLC column: {col_type}. Expected one of {possible_names}. "
                f"Available columns: {list(closed_df.columns)}"
            )
        column_mapping[col_type] = found

    high_col = column_mapping["high"]
    low_col = column_mapping["low"]

    # For relevance, focus on last 20 weeks maximum
    recent_df = closed_df.tail(20).copy()

    # Find significant swing in recent data
    highs = recent_df[high_col].values
    lows = recent_df[low_col].values
    dates = recent_df.index.values

    # Find the major swing: lowest low to highest high in recent period
    min_idx = np.argmin(lows)
    max_idx = np.argmax(highs)

    # Ensure we have a Low→High progression
    if min_idx < max_idx:
        # Perfect Low→High swing
        swing_low = lows[min_idx]
        swing_high = highs[max_idx]
        low_date = str(dates[min_idx])[:10]
        high_date = str(dates[max_idx])[:10]
    else:
        # Find alternative: recent significant correction + recovery
        # Look for lowest point in recent 10 weeks
        very_recent = recent_df.tail(10)

        if len(very_recent) >= 3:
            min_price = very_recent[low_col].min()
            max_price = very_recent[high_col].max()

            min_date_idx = very_recent[low_col].idxmin()
            max_date_idx = very_recent[high_col].idxmax()

            swing_low = min_price
            swing_high = max_price
            low_date = str(min_date_idx)[:10]
            high_date = str(max_date_idx)[:10]
        else:
            # Final fallback - use overall range
            swing_low = recent_df[low_col].min()
            swing_high = recent_df[high_col].max()
            low_date = str(recent_df[low_col].idxmin())[:10]
            high_date = str(recent_df[high_col].idxmax())[:10]

    # Ensure meaningful swing size (at least 5% range)
    swing_size = (swing_high - swing_low) / swing_low
    if swing_size < 0.05:
        # Use broader range for small swings
        extended_df = closed_df.tail(30) if len(closed_df) >= 30 else closed_df
        swing_low = extended_df[low_col].min()
        swing_high = extended_df[high_col].max()
        low_date = str(extended_df[low_col].idxmin())[:10]
        high_date = str(extended_df[high_col].idxmax())[:10]

    return swing_low, swing_high, low_date, high_date


def calculate_fibonacci_levels(
    low: float, high: float, current_price: float
) -> dict[str, Any]:
    """
    Calculate Fibonacci retracement and extension levels

    Args:
        low: Swing low price
        high: Swing high price
        current_price: Current market price

    Returns:
        Dictionary with retracement and extension levels
    """
    range_value = high - low

    # Retracement levels (below current price)
    retracement_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
    retracements = []

    for ratio in retracement_ratios:
        level_price = low + ratio * range_value
        if level_price < current_price:  # Only levels below current price
            delta_pct = ((level_price - current_price) / current_price) * 100
            retracements.append(
                {
                    "ratio": ratio,
                    "price": level_price,
                    "delta_pct": delta_pct,
                    "is_golden": ratio == 0.618,
                }
            )

    # Extension levels (above current price)
    extension_ratios = [1.272, 1.414, 1.618, 2.0, 2.618]
    extensions = []

    for ratio in extension_ratios:
        level_price = high + (ratio - 1.0) * range_value
        if level_price > current_price:  # Only levels above current price
            delta_pct = ((level_price - current_price) / current_price) * 100
            extensions.append(
                {
                    "ratio": ratio,
                    "price": level_price,
                    "delta_pct": delta_pct,
                    "is_golden": ratio == 1.618,
                }
            )

    return {
        "retracements": retracements,
        "extensions": extensions,
        "swing_low": low,
        "swing_high": high,
        "range": range_value,
    }


def count_touches(
    daily_df: pd.DataFrame, level_price: float, tolerance: float = 0.006
) -> int:
    """
    Count historical touches at Fibonacci level with ±tolerance

    Args:
        daily_df: Daily OHLCV data
        level_price: Fibonacci level price
        tolerance: Touch tolerance (default 0.6%)

    Returns:
        Number of touches
    """
    if len(daily_df) == 0:
        return 0

    # Get OHLC columns with validation
    high_col = None
    low_col = None

    for col in ["high", "High"]:
        if col in daily_df.columns:
            high_col = col
            break
    for col in ["low", "Low"]:
        if col in daily_df.columns:
            low_col = col
            break

    if high_col is None:
        raise ValueError(
            "Missing high column. Expected 'high' or 'High'. "
            f"Available columns: {list(daily_df.columns)}"
        )
    if low_col is None:
        raise ValueError(
            "Missing low column. Expected 'low' or 'Low'. "
            f"Available columns: {list(daily_df.columns)}"
        )

    highs = daily_df[high_col].values
    lows = daily_df[low_col].values

    upper_bound = level_price * (1 + tolerance)
    lower_bound = level_price * (1 - tolerance)

    touches = 0

    for i in range(len(highs)):
        # Check if the candle touched this level
        candle_high = highs[i]
        candle_low = lows[i]

        if candle_low <= upper_bound and candle_high >= lower_bound:
            touches += 1

    return touches


def get_touch_rank(touches: int, all_touches: list[int]) -> str:
    """Determine touch rank based on percentile"""
    if not all_touches:
        return "LOW"

    percentile = (sum(1 for t in all_touches if t <= touches) / len(all_touches)) * 100

    if percentile >= 75:
        return "HIGH"
    if percentile >= 40:
        return "MED"
    return "LOW"


def create_fibonacci_map() -> str:
    """
    Create comprehensive Fibonacci visualization map

    Returns:
        Formatted string with complete Fibonacci analysis
    """
    try:
        logger.info("🔄 Fetching BNB/USDT data...")

        # Initialize data fetcher
        fetcher = BNBDataFetcher()

        # Fetch data
        data = fetcher.fetch_bnb_data(lookback_days=500)
        daily_df = data["daily"]
        weekly_df = data["weekly"]

        if daily_df.empty or weekly_df.empty:
            return "❌ Error: No data available"

        logger.info(
            f"📊 Data loaded: {len(daily_df)} daily, {len(weekly_df)} weekly candles"
        )

        # Get current price with validation
        close_col = None
        for col in ["close", "Close"]:
            if col in daily_df.columns:
                close_col = col
                break
        if close_col is None:
            raise ValueError(
                "Missing close column. Expected 'close' or 'Close'. "
                f"Available columns: {list(daily_df.columns)}"
            )

        current_price = float(daily_df[close_col].iloc[-1])
        current_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"💰 Current price: ${current_price:.2f}")

        # Find last weekly swing
        logger.info("🔍 Detecting last weekly swing...")
        swing_low, swing_high, low_date, high_date = find_last_weekly_swing(weekly_df)

        logger.info(
            f"📈 Last swing: ${swing_low:.2f} ({low_date}) → ${swing_high:.2f} ({high_date})"
        )

        # Calculate Fibonacci levels
        fib_data = calculate_fibonacci_levels(swing_low, swing_high, current_price)

        # Count touches for each level
        logger.info("🔢 Counting historical touches...")

        all_touches = []

        # Process retracements
        for ret in fib_data["retracements"]:
            touches = count_touches(daily_df, ret["price"])
            ret["touches"] = touches
            all_touches.append(touches)

        # Process extensions
        for ext in fib_data["extensions"]:
            touches = count_touches(daily_df, ext["price"])
            ext["touches"] = touches
            all_touches.append(touches)

        # Sort retracements by proximity to current price (closest first)
        fib_data["retracements"].sort(key=lambda x: abs(x["delta_pct"]))

        # Sort extensions by price (ascending)
        fib_data["extensions"].sort(key=lambda x: x["price"])

        # Find recommended entry (retracement with max touches, then closest)
        if fib_data["retracements"]:
            max_touches = max(ret["touches"] for ret in fib_data["retracements"])
            best_retracements = [
                ret for ret in fib_data["retracements"] if ret["touches"] == max_touches
            ]
            recommended = min(best_retracements, key=lambda x: abs(x["delta_pct"]))
        else:
            recommended = None

        # Create visualization
        output = []
        output.append(f"💹 BNB/USDT — Fibonacci Map (as of {current_date})")
        output.append(f"Price: ${current_price:.2f}")
        output.append(
            f"Last Swing: ${swing_low:.2f} ({low_date}) → ${swing_high:.2f} ({high_date})"
        )
        output.append("")

        # Extensions (above price)
        if fib_data["extensions"]:
            output.append("⬆️ EXTENSIONS (above price):")
            for i, ext in enumerate(fib_data["extensions"], 1):
                golden_marker = " (GOLDEN EXTENSION)" if ext["is_golden"] else ""
                star = "⭐ " if ext["is_golden"] else ""
                output.append(
                    f"  {i}) {star}{ext['ratio']:.3f}{golden_marker}  ${ext['price']:.2f}  (+{ext['delta_pct']:.1f}%)  • touches: {ext['touches']}"
                )
        else:
            output.append("⬆️ EXTENSIONS: None above current price")

        output.append("")

        # Retracements (below price)
        if fib_data["retracements"]:
            output.append("⬇️ RETRACEMENTS (below price):")
            for i, ret in enumerate(fib_data["retracements"], 1):
                golden_marker = " (GOLDEN RATIO)" if ret["is_golden"] else ""
                star = "⭐ " if ret["is_golden"] else ""
                rank = get_touch_rank(ret["touches"], all_touches)
                output.append(
                    f"  {i}) {star}{ret['ratio']:.3f}{golden_marker}  ${ret['price']:.2f}  ({ret['delta_pct']:.1f}%)  • touches: {ret['touches']} ({rank})"
                )
        else:
            output.append("⬇️ RETRACEMENTS: None below current price")

        output.append("")

        # Recommended entry
        if recommended:
            rank = get_touch_rank(recommended["touches"], all_touches)
            output.append(
                f"⭐ RECOMMENDED ENTRY: ${recommended['price']:.2f}  ({rank}, {recommended['delta_pct']:.1f}%)"
            )
        else:
            output.append(
                "⭐ RECOMMENDED ENTRY: No suitable retracement levels below current price"
            )

        output.append("")

        # Optimal entry zones (top 3 retracements by touches + proximity)
        if len(fib_data["retracements"]) >= 1:
            # Score by touches + proximity weight
            for ret in fib_data["retracements"]:
                proximity_score = 100 / (
                    abs(ret["delta_pct"]) + 1
                )  # Higher for closer levels
                ret["combined_score"] = ret["touches"] * 10 + proximity_score

            top_entries = sorted(
                fib_data["retracements"],
                key=lambda x: x["combined_score"],
                reverse=True,
            )[:3]

            output.append(
                "🟢 OPTIMAL LONG ENTRY ZONES (by confluence of touches & proximity):"
            )
            for i, zone in enumerate(top_entries, 1):
                rank = get_touch_rank(zone["touches"], all_touches)
                output.append(
                    f"  {i}) ${zone['price']:.2f}  (touches: {zone['touches']} {rank}, {zone['delta_pct']:.1f}%)"
                )

        output.append("")

        # Key resistance zones (top 3 extensions by touches)
        if len(fib_data["extensions"]) >= 1:
            top_resistances = sorted(
                fib_data["extensions"], key=lambda x: x["touches"], reverse=True
            )[:3]

            output.append(
                "🔴 KEY RESISTANCE ZONES (extensions with highest historic reactions):"
            )
            for i, zone in enumerate(top_resistances, 1):
                rank = get_touch_rank(zone["touches"], all_touches)
                output.append(
                    f"  {i}) ${zone['price']:.2f}  (touches: {zone['touches']} {rank}, +{zone['delta_pct']:.1f}%)"
                )

        output.append("")

        # Visual price ladder
        output.append("📊 VISUAL FIBONACCI LADDER:")
        output.append("")

        # Collect all levels for ladder
        all_levels = []

        for ext in fib_data["extensions"]:
            all_levels.append(("EXT", ext["ratio"], ext["price"]))

        all_levels.append(("PRICE", 1.0, current_price))

        for ret in reversed(
            fib_data["retracements"]
        ):  # Reverse to show higher levels first
            all_levels.append(("RET", ret["ratio"], ret["price"]))

        # Sort by price (descending)
        all_levels.sort(key=lambda x: x[2], reverse=True)

        for level_type, ratio, price in all_levels:
            if level_type == "PRICE":
                output.append(f"PRICE  ${price:.2f}  ──●──┤")
            else:
                bar_length = min(int(ratio * 8), 15)  # Scale bar length
                bar = "─" * bar_length
                output.append(f"{level_type} {ratio:6.3f}  {bar}┤")

        output.append("                     ─┘")
        output.append("")
        output.append("🎯 Analysis complete! Fibonacci map generated successfully.")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Error creating Fibonacci map: {e}"


if __name__ == "__main__":
    # Create and display Fibonacci map
    map_output = create_fibonacci_map()
    print(map_output)

    # Save to file
    with open("/Users/stan/bnb-b/fibonacci_map_output.txt", "w") as f:
        f.write(map_output)

    print("\n💾 Fibonacci map saved to: fibonacci_map_output.txt")
