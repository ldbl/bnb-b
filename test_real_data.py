#!/usr/bin/env python3
"""
Тест на weekly_tails.py с реални данни от Binance
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
from data_fetcher import BNBDataFetcher
from weekly_tails import WeeklyTailsAnalyzer
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def test_real_data():
    """Тества weekly_tails.py с реални данни"""

    print("🔧 ТЕСТ С РЕАЛНИ ДАННИ ОТ BINANCE")
    print("=" * 50)

    try:
        # Извличаме реални данни
        data_fetcher = BNBDataFetcher()
        print("📊 Извличаме данни...")
        data = data_fetcher.fetch_bnb_data(90)  # 90 дни

        if not data or 'weekly' not in data:
            print("❌ Грешка при извличане на данни")
            return

        weekly_df = data['weekly']
        print(f"✅ Извлечени {len(weekly_df)} седмични записа")
        print(f"📊 Колонки: {list(weekly_df.columns)}")

        # Показваме последните 3 седмици
        print("\n📈 Последните 3 седмици:")
        for i, (date, row) in enumerate(weekly_df.tail(3).iterrows()):
            open_price = row['Open']
            high_price = row['High']
            low_price = row['Low']
            close_price = row['Close']
            is_bullish = close_price > open_price
            upper_wick = high_price - max(open_price, close_price)
            lower_wick = min(open_price, close_price) - low_price
            total_range = high_price - low_price

            upper_wick_pct = (upper_wick / total_range * 100) if total_range > 0 else 0

            print(".2f"
                  ".2f")

        # Инициализираме анализатора
        config = {
            'weekly_tails': {
                'lookback_weeks': 8,
                'min_tail_size': 0.03,
                'strong_tail_size': 0.05,
                'confluence_bonus': 1.5
            }
        }

        analyzer = WeeklyTailsAnalyzer(config)
        print("\n✅ Анализатор инициализиран успешно")

        # Тестваме анализ
        print("\n🎯 Анализираме седмични опашки...")
        tails_analysis = analyzer.analyze_weekly_tails(weekly_df)
        print(f"📈 Анализирани опашки: {len(tails_analysis)}")

        for i, tail in enumerate(tails_analysis[-3:]):  # Последните 3
            print(f"  {i+1}. {tail['date'].date()}: {tail['dominant_tail']} опашка ({tail['tail_strength']:.1%}) - {tail['signal']}")

        # Тестваме генериране на сигнал
        if tails_analysis:
            print("\n🎯 Генерираме сигнал...")
            signal = analyzer.get_weekly_tails_signal(tails_analysis)
            print(f"🎯 ГЕНЕРИРАН СИГНАЛ: {signal.get('signal', 'ERROR')} (сила: {signal.get('strength', 0):.2f})")
            print(f"📝 Причина: {signal.get('reason', 'ERROR')}")
        else:
            print("❌ Няма анализирани опашки")

    except Exception as e:
        print(f"❌ ГРЕШКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_data()
