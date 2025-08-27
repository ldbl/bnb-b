#!/usr/bin/env python3
"""
Short Accuracy Validation Test
Тест за валидиране на SHORT accuracy след всички Phase 1 подобрения
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtester import Backtester
import logging

# Намаляваме logging за по-чист output
logging.getLogger('signal_generator').setLevel(logging.WARNING)
logging.getLogger('fibonacci').setLevel(logging.WARNING)
logging.getLogger('weekly_tails').setLevel(logging.WARNING)
logging.getLogger('trend_analyzer').setLevel(logging.WARNING)
logging.getLogger('data_fetcher').setLevel(logging.WARNING)

def test_short_accuracy():
    """Test SHORT accuracy after all Phase 1 improvements"""
    print('🧪 ФАЗА 7: SHORT ACCURACY ВАЛИДАЦИЯ')
    print('=' * 40)
    print('🎯 ЦЕЛ: SHORT accuracy > 60%')
    print('🔥 Тестваме всички 9 SHORT филтри в исторически контекст')
    print()

    backtester = Backtester()

    try:
        print('📊 Стартираме FULL BACKTEST (18 месеца)...')
        print('⏳ Това може да отнеме няколко минути...')

        # Стартираме full backtest
        results = backtester.run_backtest(18)

        if 'error' in results:
            print(f'❌ Backtest failed: {results["error"]}')
            return

        analysis = results['analysis']

        print('\n📊 BACKTEST РЕЗУЛТАТИ:')
        print('=' * 50)
        print(f'📈 Общо сигнали: {analysis["total_signals"]}')
        print(f'🏆 Успешни сигнали: {analysis["successful_signals"]}')
        print('.1f')
        print()

        print('📊 ПО ТИП СИГНАЛ:')
        print('.1f')
        print('.1f')
        print()

        # Проверяваме SHORT accuracy
        short_accuracy = analysis['short_signals']['accuracy']
        short_total = analysis['short_signals']['total']

        print('🎯 SHORT SIGNALS VALIDATION:')
        print('=' * 30)

        if short_total == 0:
            print('⚠️  НЯМА SHORT сигнали генерирани')
            print('   Това може да означава че филтрите работят твърде агресивно')
            print('   или че няма подходящи SHORT възможности в тествания период')
        else:
            print(f'📊 SHORT сигнали: {short_total}')
            print('.1f')

            if short_accuracy >= 60:
                print('🎉 УСПЕХ! SHORT accuracy >= 60%')
                print('✅ Phase 1 SHORT сигнали подобрения - ВАЛИДИРАНИ!')
            elif short_accuracy >= 40:
                print('⚠️  SHORT accuracy е добра (>= 40%) но под целта 60%')
                print('   Може да се нуждае от допълнително фина настройка')
            else:
                print('❌ SHORT accuracy е под очакванията (< 40%)')
                print('   Нужно е допълнително тестване и оптимизация')

        print('\n📋 ДОТАЙЛНИ РЕЗУЛТАТИ:')
        print('.2f')
        if analysis['best_signals']:
            print('.2f')
        if analysis['worst_signals']:
            print('.2f')

        print('\n📁 Резултатите са експортирани в data/backtest_results.txt')

        # Експортираме резултатите
        backtester.export_backtest_results(results)

        print('\n✅ ФАЗА 7: SHORT Accuracy валидация - ЗАВЪРШЕНА')

        if short_total > 0 and short_accuracy >= 60:
            print('\n🎊 ПОЗДРАВЛЕНИЯ! PHASE 1 SHORT IMPROVEMENTS - УСПЕШНИ!')
            print('🎯 SHORT accuracy target (60%+) - ПОСТИГНАТ!')
            print('🔥 9 SHORT quality filters - ВАЛИДИРАНИ!')
            print('🏆 Phase 1 - ЗАВЪРШЕН!')
        elif short_total == 0:
            print('\n⚠️  PHASE 1 SHORT IMPROVEMENTS - ТВЪРДЕ АГРЕСИВНИ')
            print('   Няма генерирани SHORT сигнали - филтрите може да са твърде строги')
        else:
            print(f'\n⚠️  PHASE 1 SHORT IMPROVEMENTS - НУЖДА ОТ ОПТИМИЗАЦИЯ')
            print('.1f')

    except Exception as e:
        print(f'❌ SHORT Accuracy валидация - ГРЕШКА: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_short_accuracy()
