#!/usr/bin/env python3
"""
Тест на weekly_tails.py с конкретни данни
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
from weekly_tails import WeeklyTailsAnalyzer
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def test_weekly_tails():
    """Тества weekly_tails.py с конкретни данни"""

    print("🔧 ТЕСТ НА WEEKLY TAILS ANALYZER")
    print("=" * 50)

    # Създаваме тестови данни - конкретно BEARISH свещ с голяма горна опашка
    test_data = pd.DataFrame({
        'Open': [600.0, 590.0],  # BEARISH свещ (отворя 600, затваря 590)
        'High': [650.0, 640.0],  # Големи горни опашки
        'Low': [585.0, 580.0],
        'Close': [590.0, 585.0],
        'Volume': [1000000, 1100000]
    }, index=pd.date_range('2024-01-01', periods=2, freq='W'))

    print("📊 Тестови данни:")
    print(test_data)

    # Инициализираме анализатора
    config = {
        'weekly_tails': {
            'lookback_weeks': 8,
            'min_tail_size': 0.03,
            'strong_tail_size': 0.05,
            'confluence_bonus': 1.5
        }
    }

    try:
        analyzer = WeeklyTailsAnalyzer(config)
        print("✅ Анализатор инициализиран успешно")

        # Тестваме анализ на опашките
        tails_analysis = analyzer.analyze_weekly_tails(test_data)
        print(f"📈 Анализирани опашки: {len(tails_analysis)}")

        for i, tail in enumerate(tails_analysis):
            print(f"  {i+1}. {tail['date'].date()}: {tail['dominant_tail']} опашка ({tail['tail_strength']:.1%}) - {tail['signal']}")

        # Тестваме генериране на сигнал
        if tails_analysis:
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
    test_weekly_tails()
