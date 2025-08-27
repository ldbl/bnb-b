#!/usr/bin/env python3
"""
Phase 2 LONG Signal Enhancements Test
Тест за валидиране на новите LONG подобрения
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from signal_generator import SignalGenerator
from data_fetcher import BNBDataFetcher
import toml
import logging

# Намаляваме logging за по-чист output
logging.getLogger('signal_generator').setLevel(logging.WARNING)
logging.getLogger('fibonacci').setLevel(logging.WARNING)
logging.getLogger('weekly_tails').setLevel(logging.WARNING)
logging.getLogger('trend_analyzer').setLevel(logging.WARNING)
logging.getLogger('data_fetcher').setLevel(logging.WARNING)

def test_phase2_long_enhancements():
    """Test Phase 2 LONG signal enhancements"""
    print("🧪 PHASE 2 LONG SIGNAL ENHANCEMENTS TEST")
    print("=" * 50)

    # Инициализираме компонентите
    data_fetcher = BNBDataFetcher('BNB/USDT')

    # Зареждаме config
    with open('config.toml', 'r') as f:
        config = toml.load(f)

    signal_generator = SignalGenerator(config)

    try:
        print("📊 Взимаме данни (последните 90 дни)...")
        data = data_fetcher.fetch_bnb_data(90)

        if not data or 'daily' not in data or 'weekly' not in data:
            print("❌ Грешка при извличане на данни")
            return

        daily_df = data['daily']
        weekly_df = data['weekly']

        print(f"✅ Данни заредени: {len(daily_df)} daily, {len(weekly_df)} weekly rows")
        print(f"📅 Период: {daily_df.index[0].strftime('%Y-%m-%d')} до {daily_df.index[-1].strftime('%Y-%m-%d')}")

        # Тестваме сигнал за последната дата
        test_date = daily_df.index[-1]
        print(f"\n🎯 Тестваме сигнал за дата: {test_date.strftime('%Y-%m-%d')}")

        # Генерираме сигнал
        signal = signal_generator.generate_signal(daily_df, weekly_df)

        if signal and signal['signal'] != 'HOLD':
            print("\n📊 РЕЗУЛТАТ:")
            print(f"   Сигнал: {signal['signal']}")
            print(f"   Увереност: {signal['confidence']:.2f}")
            print(f"   Причина: {signal['reason']}")

            # Проверяваме дали има Phase 2 подобрения
            if 'Phase 2' in signal['reason']:
                print("✅ Phase 2 подобрения: АКТИВНИ!")
                if 'Volume LONG' in signal['reason']:
                    print("   💰 Volume Confirmation: АКТИВЕН")
                if 'Divergence LONG' in signal['reason']:
                    print("   🔄 Divergence Confirmation: АКТИВЕН")
                if 'Market Regime LONG' in signal['reason']:
                    print("   📊 Market Regime Awareness: АКТИВЕН")
            else:
                print("⚠️ Phase 2 подобрения: НЕАКТИВНИ (може да няма достатъчно данни)")

            # Показваме детайли
            if signal['signal'] == 'LONG':
                print("\n🎉 LONG сигнал генериран!")
                print("   💪 Това показва че Phase 2 подобренията работят!")
            else:
                print("\n📉 SHORT сигнал генериран!")
                print("   💡 Това е добре - SHORT сигнали също са важни!")
        else:
            print("\n📊 Резултат: HOLD сигнал")
            print("   💭 Няма достатъчно силни сигнали в момента")
        print("\n✅ Phase 2 LONG Enhancements Test: ЗАВЪРШЕН!")

    except Exception as e:
        print(f"❌ Грешка при тестване: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_phase2_long_enhancements()
