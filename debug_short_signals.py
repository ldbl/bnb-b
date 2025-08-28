#!/usr/bin/env python3
"""
Debug SHORT сигнали - директен тест на weekly_tails модула
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
import toml
from data_fetcher import BNBDataFetcher
from weekly_tails import WeeklyTailsAnalyzer
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def debug_short_signals():
    """Debug SHORT сигнали"""

    print("🐛 DEBUG SHORT СИГНАЛИ")
    print("=" * 50)

    try:
        # Зареждаме конфигурацията
        config_data = toml.load('config.toml')

        # Извличаме данни
        data_fetcher = BNBDataFetcher()
        print("📊 Извличаме данни...")
        data = data_fetcher.fetch_bnb_data(200)  # 200 дни история

        if not data or 'weekly' not in data:
            print("❌ Грешка при извличане на данни")
            return

        weekly_df = data['weekly']
        print(f"✅ Извлечени {len(weekly_df)} седмични записа")

        # Инициализираме WeeklyTailsAnalyzer
        weekly_tails_analyzer = WeeklyTailsAnalyzer(config_data)

        print("\n🔍 АНАЛИЗ НА СЕДМИЧНИ ОПАШКИ...")
        print("   Търсим големи горни опашки (SHORT потенциал)")

        short_candidates = []

        # Анализираме всяка седмица
        for i in range(5, len(weekly_df)):  # Започваме от 5-та седмица
            current_weekly = weekly_df.iloc[:i+1]

            try:
                # Първо анализираме опашките (връща List[Dict])
                tails_analysis = weekly_tails_analyzer.analyze_weekly_tails(current_weekly)

                # После генерираме сигнал от анализа
                signal = weekly_tails_analyzer.get_weekly_tails_signal(tails_analysis)

                if signal and signal.get('signal') == 'SHORT':
                    signal_date = weekly_df.index[i]

                    # Взимаме допълнителна информация за дебъг
                    last_candle = current_weekly.iloc[-1]
                    upper_wick_pct = (last_candle['High'] - max(last_candle['Open'], last_candle['Close'])) / (last_candle['High'] - last_candle['Low']) * 100
                    lower_wick_pct = (min(last_candle['Open'], last_candle['Close']) - last_candle['Low']) / (last_candle['High'] - last_candle['Low']) * 100

                    short_candidates.append({
                        'date': signal_date.date(),
                        'confidence': signal['confidence'],
                        'price': last_candle['Close'],
                        'upper_wick_pct': upper_wick_pct,
                        'lower_wick_pct': lower_wick_pct,
                        'signal_strength': signal.get('strength', 'N/A'),
                        'tail_strength': signal.get('tail_strength', 'N/A')
                    })

            except Exception as e:
                continue

        print(f"\n📊 РЕЗУЛТАТИ ОТ WEEKLY TAILS АНАЛИЗА:")
        print(f"   🔴 SHORT кандидати: {len(short_candidates)}")

        if short_candidates:
            print("\n🔴 ПОДРОБНА ИНФОРМАЦИЯ ЗА SHORT КАНДИДАТИ:")
            print("   Дата       | Цена     | Горна опашка | Долна опашка | Сила")
            print("   -----------|----------|--------------|--------------|-----")

            for candidate in short_candidates[:10]:  # Показваме първите 10
                print("12")

            if len(short_candidates) > 10:
                print(f"   ... и още {len(short_candidates) - 10} SHORT кандидати")

            # Анализ по месеци
            print("\n📅 SHORT КАНДИДАТИ ПО МЕСЕЦИ:")
            monthly_candidates = {}
            for candidate in short_candidates:
                month_key = f"{candidate['date'].year}-{candidate['date'].month:02d}"
                monthly_candidates[month_key] = monthly_candidates.get(month_key, 0) + 1

            for month, count in sorted(monthly_candidates.items()):
                print(f"   {month}: {count} SHORT кандидати")

        else:
            print("\n❌ НЯМА SHORT КАНДИДАТИ В ТОЗИ ПЕРИОД!")
            print("   💡 Това може да означава:")
            print("      - BNB няма SHORT възможности в този период")
            print("      - Параметрите за SHORT сигнали са твърде строги")
            print("      - Има проблем в логиката на weekly_tails модула")

            # Нека проверим някои свещи ръчно
            print("\n🔍 РЪЧЕН АНАЛИЗ НА НЯКОИ СВЕЩИ:")
            for i in [10, 20, 30, 40, 50]:
                if i < len(weekly_df):
                    candle = weekly_df.iloc[i]
                    upper_wick = candle['High'] - max(candle['Open'], candle['Close'])
                    lower_wick = min(candle['Open'], candle['Close']) - candle['Low']
                    total_range = candle['High'] - candle['Low']

                    if total_range > 0:
                        upper_wick_pct = upper_wick / total_range * 100
                        lower_wick_pct = lower_wick / total_range * 100

                        print(".1f")

    except Exception as e:
        print(f"❌ ГРЕШКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_short_signals()
