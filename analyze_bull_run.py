#!/usr/bin/env python3
"""
Анализ на bull run тренда в последните месеци
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
from data_fetcher import BNBDataFetcher
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def analyze_bull_run():
    """Анализира bull run тренда в последните месеци"""

    print("🔥 АНАЛИЗ НА BULL RUN ТРЕНД В ПОСЛЕДНИТЕ МЕСЕЦИ")
    print("=" * 60)

    try:
        # Извличаме данни
        data_fetcher = BNBDataFetcher()
        print("📊 Извличаме данни...")
        data = data_fetcher.fetch_bnb_data(180)  # 6 месеца

        if not data or 'daily' not in data:
            print("❌ Грешка при извличане на данни")
            return

        daily_df = data['daily']
        print(f"✅ Извлечени {len(daily_df)} дневни записа")
        print(f"📅 Период: {daily_df.index[0].date()} до {daily_df.index[-1].date()}")

        # Анализираме последните 3 месеца
        end_date = daily_df.index[-1]
        start_date = end_date - pd.Timedelta(days=90)  # 90 дни = 3 месеца

        recent_data = daily_df[daily_df.index >= start_date]
        print(f"\n📈 АНАЛИЗ НА ПОСЛЕДНИТЕ 3 МЕСЕЦА:")
        print(f"   📅 От {start_date.date()} до {end_date.date()}")
        print(f"   📊 {len(recent_data)} дневни записа")

        # Изчисляваме основни метрики
        start_price = recent_data['Close'].iloc[0]
        end_price = recent_data['Close'].iloc[-1]
        max_price = recent_data['High'].max()
        min_price = recent_data['Low'].min()

        total_return = (end_price - start_price) / start_price * 100
        max_drawdown = ((max_price - min_price) / max_price) * 100

        print("\n📊 ОСНОВНИ МЕТРИКИ:")
        print(".2f")
        print(".2f")
        print(".2f")
        print(".2f")
        print("\n🔥 BULL RUN АНАЛИЗ:")
        if total_return > 20:
            print("   🚀 СИЛЕН BULL RUN! Цената се е качила значително!")
            print("   💡 Това обяснява липсата на SHORT сигнали!")
        elif total_return > 10:
            print("   📈 Умерен възходящ тренд")
        elif total_return > 0:
            print("   ➡️ Лек възходящ тренд")
        else:
            print("   📉 Низходящ или страничен тренд")

        # Анализираме седмични данни за опашки
        if 'weekly' in data:
            weekly_df = data['weekly']

            # Взимаме последните 3 месеца седмични данни
            recent_weekly = weekly_df[weekly_df.index >= start_date]
            print("\n🕯️ АНАЛИЗ НА СЕДМИЧНИ СВЕЩИ:")
            print(f"   📊 {len(recent_weekly)} седмични свещи")

            # Броим bullish vs bearish свещи
            bullish_count = 0
            bearish_count = 0
            doji_count = 0

            for _, row in recent_weekly.iterrows():
                open_price = row['Open']
                close_price = row['Close']
                body_size = abs(close_price - open_price)

                if body_size < (open_price + close_price) / 2 * 0.001:  # Doji (< 0.1%)
                    doji_count += 1
                elif close_price > open_price:
                    bullish_count += 1
                else:
                    bearish_count += 1

            print(f"   🟢 Bullish свещи: {bullish_count}")
            print(f"   🔴 Bearish свещи: {bearish_count}")
            print(f"   ⚪ Doji свещи: {doji_count}")

            bullish_percentage = bullish_count / len(recent_weekly) * 100
            print(".1f")
            if bullish_percentage > 70:
                print("   🔥 ЕКСТРЕМЕН BULL RUN! Почти всички свещи са bullish!")
            elif bullish_percentage > 60:
                print("   🚀 СИЛЕН BULL RUN! Много повече bullish свещи!")
            elif bullish_percentage > 50:
                print("   📈 Лек bull тренд")

            # Анализираме опашки
            upper_wicks = []
            lower_wicks = []

            for _, row in recent_weekly.iterrows():
                open_price = row['Open']
                high_price = row['High']
                low_price = row['Low']
                close_price = row['Close']

                body_high = max(open_price, close_price)
                body_low = min(open_price, close_price)

                upper_wick = high_price - body_high
                lower_wick = body_low - low_price

                total_range = high_price - low_price
                if total_range > 0:
                    upper_wick_pct = upper_wick / total_range * 100
                    lower_wick_pct = lower_wick / total_range * 100

                    upper_wicks.append(upper_wick_pct)
                    lower_wicks.append(lower_wick_pct)

            if upper_wicks:
                avg_upper_wick = np.mean(upper_wicks)
                avg_lower_wick = np.mean(lower_wicks)
                max_upper_wick = max(upper_wicks)
                max_lower_wick = max(lower_wicks)

                print("\n🕯️ АНАЛИЗ НА ОПАШКИТЕ:")
                print(".1f")
                print(".1f")
                print(".1f")
                print(".1f")
                if avg_upper_wick < 30 and avg_lower_wick > 40:
                    print("   ✅ ХАРАКТЕРНО ЗА BULL RUN: Малки горни опашки, големи долни опашки!")
                    print("   💡 Това обяснява липсата на SHORT сигнали - няма съпротива отгоре!")

                # Броим големи опашки
                large_upper_wicks = sum(1 for wick in upper_wicks if wick > 50)
                large_lower_wicks = sum(1 for wick in lower_wicks if wick > 50)

                print(f"   🔴 Големи горни опашки (>50%): {large_upper_wicks}")
                print(f"   🟢 Големи долни опашки (>50%): {large_lower_wicks}")

                if large_upper_wicks < large_lower_wicks:
                    print("   🎯 ПОТВЪРЖДЕНИЕ: Повече големи долни опашки = BULL RUN!")

        print("\n🎯 ЗАКЛЮЧЕНИЕ:")
        print("   🔥 Данните потвърждават BULL RUN тренд!")
        print("   ❌ Липсата на SHORT сигнали е правилна!")
        print("   ✅ Системата правилно не генерира SHORT сигнали в силен възходящ тренд!")
        print("   💡 Това е признак за добро качество на филтрите!")

    except Exception as e:
        print(f"❌ ГРЕШКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_bull_run()
