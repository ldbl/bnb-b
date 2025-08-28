#!/usr/bin/env python3
"""
🧪 Тест на SmartShortSignalGenerator с реални данни
===================================================

Този файл тества новия SmartShortSignalGenerator модул
преди интеграцията му в основната система.
"""

import sys
import pandas as pd
from smart_short_generator import SmartShortSignalGenerator, MarketRegimeDetector
from data_fetcher import BNBDataFetcher
import toml

print('🧪 ТЕСТИРАНЕ НА SmartShortSignalGenerator')
print('=' * 50)

try:
    # Зареждаме конфигурация
    with open('config.toml', 'r', encoding='utf-8') as f:
        config = toml.load(f)

    # Създаваме data fetcher
    fetcher = BNBDataFetcher(config['data']['symbol'])

    # Взимаме 100 дни данни за тест
    print('📊 Зареждаме исторически данни...')
    data = fetcher.fetch_bnb_data(100)

    if data and 'daily' in data:
        daily_df = data['daily']
        weekly_df = data.get('weekly', pd.DataFrame())

        print(f'✅ Заредени данни: {len(daily_df)} daily, {len(weekly_df)} weekly')

        # Тест 1: Market Regime Detection
        print('\n🔍 ТЕСТ 1: Market Regime Detection')
        regime_detector = MarketRegimeDetector()
        regime = regime_detector.detect_market_regime(daily_df, weekly_df)

        print(f'📊 Текущ режим: {regime["regime"]}')
        print(f'🎯 SHORT позволени: {regime["short_signals_allowed"]}')
        print(f'📈 Daily тренд: {regime["daily_trend"]:.2f}')
        print(f'📊 Weekly тренд: {regime["weekly_trend"]:.2f}')
        print(f'📍 ATH дистанция: {regime["ath_distance_pct"]:.1f}%')

        # Тест 2: Smart SHORT Generator
        print('\n🎯 ТЕСТ 2: Smart SHORT Signal Generation')
        short_generator = SmartShortSignalGenerator(config)

        signals = short_generator.generate_short_signals(daily_df, weekly_df)

        print(f'📊 Генерирани SHORT сигнали: {len(signals)}')

        if signals:
            print('\n🏆 ТОП SHORT СИГНАЛ:')
            top_signal = signals[0]
            print(f'   📅 Дата: {top_signal.timestamp}')
            print(f'   💰 Цена: ${top_signal.price:.2f}')
            print(f'   🎯 Увереност: {top_signal.confidence:.1f}')
            print(f'   🔢 Confluence Score: {top_signal.confluence_score}/7')
            print(f'   ⚖️ Risk/Reward: 1:{top_signal.risk_reward_ratio:.1f}')
            print(f'   🛑 Stop Loss: ${top_signal.stop_loss_price:.2f}')
            print(f'   🎯 Take Profit: ${top_signal.take_profit_price:.2f}')
            print(f'   📍 ATH Distance: {top_signal.ath_distance_pct:.1f}%')
            print(f'   📊 Market Regime: {top_signal.market_regime}')
            print(f'   📋 Причини: {len(top_signal.reasons)} фактора')
            for i, reason in enumerate(top_signal.reasons[:3], 1):
                print(f'      {i}. {reason}')
        else:
            print('   ✅ НЯМА SHORT сигнали - правилно поведение в текущия пазар!')

        print('\n🎉 ТЕСТ ЗАВЪРШЕН УСПЕШНО!')

    else:
        print('❌ Неуспешно зареждане на данни')

except Exception as e:
    print(f'❌ Грешка при тест: {e}')
    import traceback
    traceback.print_exc()
