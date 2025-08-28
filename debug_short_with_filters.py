#!/usr/bin/env python3
"""
Debug SHORT сигнали с включени филтри - да видим къде се блокират
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
import toml
from data_fetcher import BNBDataFetcher
from signal_generator import SignalGenerator
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def debug_short_with_filters():
    """Debug SHORT сигнали с включени филтри"""

    print("🐛 DEBUG SHORT СИГНАЛИ С ФИЛТРИ")
    print("=" * 60)

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
        daily_df = data['daily']
        print(f"✅ Извлечени {len(daily_df)} дневни и {len(weekly_df)} седмични записа")

        # Инициализираме SignalGenerator
        signal_generator = SignalGenerator(config_data)

        print("\n🔍 АНАЛИЗ НА SHORT СИГНАЛИ С ФИЛТРИ...")
        print("   Ще следим къде се блокират SHORT сигналите")

        short_attempts = []
        short_blocked_by_trend = 0
        short_blocked_by_fib = 0
        short_blocked_by_other = 0

        # Анализираме последните 20 седмици
        for i in range(max(10, len(weekly_df) - 20), len(weekly_df)):
            current_date = weekly_df.index[i]
            current_weekly = weekly_df.iloc[:i+1]
            current_daily = daily_df[daily_df.index <= current_date]

            if len(current_daily) < 50 or len(current_weekly) < 4:
                continue

            try:
                # Генерираме сигнал
                signal = signal_generator.generate_signal(current_daily, current_weekly)

                if signal and signal.get('signal') != 'HOLD':
                    signal_type = signal.get('signal')

                    # Ако е SHORT, проследяваме какво се е случило
                    if signal_type == 'SHORT':
                        short_info = {
                            'date': current_date.date(),
                            'signal': signal_type,
                            'confidence': signal.get('confidence', 0),
                            'price': current_daily['Close'].iloc[-1] if not current_daily.empty else 0,
                            'fibonacci_analysis': signal.get('fibonacci_analysis', {}),
                            'weekly_tails_analysis': signal.get('weekly_tails_analysis', {}),
                            'trend_analysis': signal.get('trend_analysis', {}),
                            'indicators_signals': signal.get('indicators_signals', {}),
                            'reasons': signal.get('reasons', [])
                        }
                        short_attempts.append(short_info)
                        print(f"🔴 SHORT сигнал на {current_date.date()}: увереност {signal.get('confidence', 0):.2f}")

                    elif signal_type == 'LONG':
                        print(f"🟢 LONG сигнал на {current_date.date()}: увереност {signal.get('confidence', 0):.2f}")

            except Exception as e:
                continue

        print(f"\n📊 РЕЗУЛТАТИ:")
        print(f"   🔴 SHORT опити: {len(short_attempts)}")
        print(f"   🟢 LONG сигнали: бяха генерирани (не броим)")
        print(f"   ❌ SHORT блокирани от тренд: {short_blocked_by_trend}")
        print(f"   ❌ SHORT блокирани от Fibonacci: {short_blocked_by_fib}")
        print(f"   ❌ SHORT блокирани от други: {short_blocked_by_other}")

        if short_attempts:
            print("\n🔴 SHORT СИГНАЛИ - ДЕТАЙЛИ:")
            for i, short in enumerate(short_attempts[:5], 1):
                print(f"\n{i}. Дата: {short['date']}")
                print(f"   Увереност: {short['confidence']:.2f}")
                print(f"   Цена: ${short['price']:.2f}")
                print(f"   Причини: {', '.join(short['reasons'][:3])}")  # Първите 3 причини

                # Анализираме тренд информацията
                trend_analysis = short['trend_analysis']
                if trend_analysis:
                    combined_trend = trend_analysis.get('combined_trend', {})
                    daily_trend = trend_analysis.get('daily_trend', {})
                    trend_direction = combined_trend.get('direction', 'UNKNOWN')
                    daily_direction = daily_trend.get('direction', 'UNKNOWN')
                    daily_strength = daily_trend.get('strength', 'UNKNOWN')

                    print(f"   📈 Тренд: Combined={trend_direction}, Daily={daily_direction} ({daily_strength})")

                # Анализираме weekly tails информацията
                tails_analysis = short['weekly_tails_analysis']
                if tails_analysis and tails_analysis.get('tails_signal'):
                    tails_signal = tails_analysis['tails_signal']
                    print(f"   🕯️ Weekly Tails: {tails_signal.get('signal', 'UNKNOWN')} (сила: {tails_signal.get('strength', 0):.2f})")

        else:
            print("\n❌ НЯМА SHORT СИГНАЛИ В ТОЗИ ПЕРИОД!")
            print("\n💡 ВЪЗМОЖНИ ПРИЧИНИ:")
            print("   1. 🎯 ТРЕНД ФИЛТЪР: BNB е в силен bull run - SHORT се блокира при силни uptrends")
            print("   2. 🔍 WEEKLY TAILS: Няма достатъчно силни горни опашки за SHORT")
            print("   3. 🎛️ ФИБОНАЧИ ФИЛТЪР: SHORT се позволява само на resistance нива")
            print("   4. ⚙️ КОНФИГУРАЦИЯ: SHORT изискванията са твърде строги")

            # Нека проверим какво показва тренд анализаторът за последната дата
            print("\n🔍 АНАЛИЗ НА ТРЕНДА ЗА ПОСЛЕДНАТА ДАТА:")
            last_date = weekly_df.index[-1]
            last_daily = daily_df[daily_df.index <= last_date]
            last_weekly = weekly_df

            if len(last_daily) >= 50 and len(last_weekly) >= 4:
                try:
                    signal = signal_generator.generate_signal(last_daily, last_weekly)
                    trend_analysis = signal.get('trend_analysis', {})

                    if trend_analysis:
                        combined_trend = trend_analysis.get('combined_trend', {})
                        daily_trend = trend_analysis.get('daily_trend', {})
                        weekly_trend = trend_analysis.get('weekly_trend', {})

                        print(f"   📊 Combined trend: {combined_trend.get('direction', 'UNKNOWN')} (сила: {combined_trend.get('strength', 'UNKNOWN')})")
                        print(f"   📊 Daily trend: {daily_trend.get('direction', 'UNKNOWN')} (сила: {daily_trend.get('strength', 'UNKNOWN')})")
                        print(f"   📊 Weekly trend: {weekly_trend.get('direction', 'UNKNOWN')} (сила: {weekly_trend.get('strength', 'UNKNOWN')})")

                        trend_direction = combined_trend.get('direction', 'UNKNOWN')
                        daily_direction = daily_trend.get('direction', 'UNKNOWN')

                        if trend_direction in ['UPTREND', 'STRONG_UPTREND'] or daily_direction == 'UPTREND':
                            print(f"   🚫 SHORT е блокиран! Трендът е твърде силен възходящ")

                except Exception as e:
                    print(f"   ❌ Грешка при анализ на тренда: {e}")

    except Exception as e:
        print(f"❌ ГРЕШКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_short_with_filters()
