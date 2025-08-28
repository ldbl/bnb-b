#!/usr/bin/env python3
"""
Детайлно дебъгване на SHORT сигнали - проследяване на всяка стъпка
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
import toml
from data_fetcher import BNBDataFetcher
from signal_generator import SignalGenerator
from weekly_tails import WeeklyTailsAnalyzer
from fibonacci import FibonacciAnalyzer
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def debug_short_detailed():
    """Детайлно дебъгване на SHORT сигнали"""

    print("🔍 ДЕТАЙЛНО ДЕБЪГВАНЕ НА SHORT СИГНАЛИ")
    print("=" * 60)

    try:
        # Зареждаме конфигурацията
        config_data = toml.load('config.toml')

        # Извличаме данни
        data_fetcher = BNBDataFetcher()
        print("📊 Извличане на данни...")
        data = data_fetcher.fetch_bnb_data(300)  # 300 дни за по-дълъг период

        if not data or 'weekly' not in data:
            print("❌ Грешка при извличане на данни")
            return

        weekly_df = data['weekly']
        daily_df = data['daily']
        print(f"✅ Извлечени {len(daily_df)} дневни и {len(weekly_df)} седмични записа")

        # Инициализираме анализаторите
        weekly_tails_analyzer = WeeklyTailsAnalyzer(config_data)
        fib_analyzer = FibonacciAnalyzer(config_data)
        signal_generator = SignalGenerator(config_data)

        print("\n🔍 АНАЛИЗ НА SHORT СИГНАЛИ ПО СТЪПКИ...")
        print("   Ще проследим всяка стъпка от анализа до крайния сигнал")

        # Статистика
        total_weeks = 0
        weeks_with_short_candidates = 0
        weeks_with_short_signals = 0
        blocked_by_trend = 0
        blocked_by_fib = 0
        blocked_by_other = 0

        # Анализираме последните 30 седмици
        for i in range(max(10, len(weekly_df) - 30), len(weekly_df)):
            current_date = weekly_df.index[i]
            current_weekly = weekly_df.iloc[:i+1]
            current_daily = daily_df[daily_df.index <= current_date]

            if len(current_daily) < 50 or len(current_weekly) < 4:
                continue

            total_weeks += 1

            try:
                # СТЪПКА 1: Анализираме weekly tails
                tails_analysis = weekly_tails_analyzer.analyze_weekly_tails(current_weekly)

                # Търсим SHORT кандидати от weekly tails
                short_candidates = [t for t in tails_analysis if t.get('signal') == 'SHORT']

                if short_candidates:
                    weeks_with_short_candidates += 1
                    print(f"\n🟢 СЕДМИЦА {current_date.date()}:")
                    print(f"   📊 Намерени {len(short_candidates)} SHORT кандидати от weekly_tails")

                    for candidate in short_candidates:
                        print(f"   🕯️ SHORT кандидат: сила={candidate.get('tail_strength', 0):.2f}, цена=${candidate.get('close', 0):.2f}")

                    # СТЪПКА 2: Проверяваме Fibonacci анализ
                    fib_analysis = fib_analyzer.analyze_fibonacci_trend(current_daily)

                    # СТЪПКА 3: Генерираме сигнал през signal_generator
                    signal = signal_generator.generate_signal(current_daily, current_weekly)

                    if signal and signal.get('signal') == 'SHORT':
                        weeks_with_short_signals += 1
                        print(f"   ✅ КРАЕН РЕЗУЛТАТ: SHORT сигнал генериран!")
                        print(f"   📊 Увереност: {signal.get('confidence', 0):.2f}")

                        # Показваме детайли за сигнала
                        if 'weekly_tails_analysis' in signal:
                            tails_signal = signal['weekly_tails_analysis'].get('tails_signal', {})
                            print(f"   🕯️ Weekly Tails: {tails_signal.get('signal', 'UNKNOWN')} (сила: {tails_signal.get('strength', 0):.2f})")

                        if 'fibonacci_analysis' in signal:
                            fib_signal = signal['fibonacci_analysis'].get('fibonacci_signal', 'UNKNOWN')
                            print(f"   🎯 Fibonacci: {fib_signal}")

                        # Показваме ATH proximity бонус ако има такъв
                        if 'reasons' in signal:
                            ath_reasons = [r for r in signal['reasons'] if 'ATH Proximity' in r]
                            if ath_reasons:
                                for reason in ath_reasons:
                                    print(f"   🔥 {reason}")

                    else:
                        print(f"   ❌ КРАЕН РЕЗУЛТАТ: {signal.get('signal', 'HOLD') if signal else 'Няма сигнал'}")
                        print("   🔍 Причина за блокиране:")
                        # Анализираме защо е блокиран
                        if signal and 'reasons' in signal:
                            for reason in signal['reasons']:
                                print(f"      - {reason}")

                        # Проверяваме тренд анализ
                        trend_analysis = signal.get('trend_analysis', {}) if signal else {}
                        if trend_analysis:
                            combined_trend = trend_analysis.get('combined_trend', {})
                            daily_trend = trend_analysis.get('daily_trend', {})
                            trend_direction = combined_trend.get('direction', 'UNKNOWN')
                            daily_direction = daily_trend.get('direction', 'UNKNOWN')
                            daily_strength = daily_trend.get('strength', 'UNKNOWN')

                            print(f"   📈 Тренд: Combined={trend_direction}, Daily={daily_direction} ({daily_strength})")

                            if trend_direction in ['UPTREND', 'STRONG_UPTREND'] or daily_direction == 'UPTREND':
                                if daily_strength in ['MODERATE', 'STRONG']:
                                    blocked_by_trend += 1
                                    print("   🚫 SHORT блокиран от тренд филтър!")

                else:
                    # Няма SHORT кандидати от weekly tails
                    print(f"\n⚪ СЕДМИЦА {current_date.date()}: Няма SHORT кандидати от weekly_tails")

            except Exception as e:
                print(f"   ❌ Грешка при анализ на седмица {current_date.date()}: {e}")

        # Финална статистика
        print(f"\n📊 ФИНАЛНА СТАТИСТИКА:")
        print(f"   📅 Общо анализирани седмици: {total_weeks}")
        print(f"   🕯️ Седмици с SHORT кандидати: {weeks_with_short_candidates}")
        print(f"   ✅ Седмици с SHORT сигнали: {weeks_with_short_signals}")
        print(f"   🚫 SHORT блокирани от тренд: {blocked_by_trend}")
        print(f"   🚫 SHORT блокирани от Fibonacci: {blocked_by_fib}")
        print(f"   🚫 SHORT блокирани от други: {blocked_by_other}")

        # Анализ на резултатите
        if weeks_with_short_candidates == 0:
            print("\n❌ ПРОБЛЕМ: Няма SHORT кандидати от weekly_tails анализатора!")
            print("   💡 Възможни причини:")
            print("      - BNB няма горни опашки в този период")
            print("      - Параметрите за SHORT са твърде строги")
            print("      - Технически проблем в weekly_tails модула")

        elif weeks_with_short_signals == 0:
            print("\n❌ ПРОБЛЕМ: Има SHORT кандидати, но всички се блокират!")
            print("   💡 Най-вероятна причина:")
            print("      - Тренд филтрите блокират всички SHORT сигнали")
            print("      - BNB е в силен bull run период")

        else:
            print("\n✅ УСПЕХ: Има работещи SHORT сигнали!")

    except Exception as e:
        print(f"❌ ГРЕШКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_short_detailed()
