#!/usr/bin/env python3
"""
Тест на signal_generator.py с ултра-стриктни SHORT настройки
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
from data_fetcher import BNBDataFetcher
from signal_generator import SignalGenerator
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def test_signal_generator():
    """Тества signal_generator с ултра-стриктни SHORT настройки"""

    print("🔧 ТЕСТ НА SIGNAL GENERATOR С УЛТРА-СТРИКТНИ SHORT НАСТРОЙКИ")
    print("=" * 70)

    try:
        # Зареждаме конфигурацията
        import toml
        with open('config.toml', 'r', encoding='utf-8') as f:
            config = toml.load(f)

        print(f"📊 min_short_score = {config['signal_scoring']['min_short_score']}")

        # Извличаме данни
        data_fetcher = BNBDataFetcher()
        print("📊 Извличаме данни...")
        data = data_fetcher.fetch_bnb_data(90)

        if not data or 'daily' not in data or 'weekly' not in data:
            print("❌ Грешка при извличане на данни")
            return

        daily_df = data['daily']
        weekly_df = data['weekly']

        print(f"✅ Извлечени {len(daily_df)} дневни и {len(weekly_df)} седмични записа")

        # Инициализираме signal generator
        signal_generator = SignalGenerator(config)
        print("✅ Signal Generator инициализиран")

        # Броим SHORT сигнали
        short_signals_count = 0
        total_signals = 0

        # Тестваме за всяка седмица
        for i in range(10, len(weekly_df)):  # Започваме от 10-та седмица за достатъчно история
            try:
                current_date = weekly_df.index[i]
                current_weekly = weekly_df.iloc[:i+1]
                current_daily = daily_df[daily_df.index <= current_date]

                if len(current_daily) < 50 or len(current_weekly) < 8:
                    continue

                signal = signal_generator.generate_signal(current_daily, current_weekly)
                total_signals += 1

                if signal and signal.get('signal') == 'SHORT':
                    short_signals_count += 1
                    print(f"🔴 SHORT #{short_signals_count} на {current_date.date()}: сила {signal.get('strength', 0):.3f}")

            except Exception as e:
                continue

        print("\n📊 РЕЗУЛТАТИ:")
        print(f"   🔴 SHORT сигнали: {short_signals_count}")
        print(f"   📈 Общо сигнали: {total_signals}")
        print(f"   📊 SHORT процент: {short_signals_count/total_signals*100:.1f}%" if total_signals > 0 else "   📊 SHORT процент: 0%")
        print(f"   🎯 SHORT accuracy потенциал: {short_signals_count}/{total_signals} = {short_signals_count/total_signals*100:.1f}%" if total_signals > 0 else "   🎯 SHORT accuracy потенциал: 0/0 = 0%")

        if short_signals_count > 0:
            print("   ⚠️  SHORT сигналите все още са много! Трябват още по-строги настройки.")
        else:
            print("   ✅ НУЛА SHORT сигнали! Успех! 🎉")

    except Exception as e:
        print(f"❌ ГРЕШКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_signal_generator()
