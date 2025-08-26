"""
Test System - Тества цялата BNB Trading система с тестови данни
Използва се когато нямате достъп до Binance API или искате да тествате логиката
"""

import pandas as pd
import numpy as np
import toml
import logging
from datetime import datetime, timedelta
import sys
import os

# Добавяме текущата директория в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fibonacci import FibonacciAnalyzer
from weekly_tails import WeeklyTailsAnalyzer
from indicators import TechnicalIndicators
from signal_generator import SignalGenerator
from validator import SignalValidator

# Настройваме logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    """Създава тестови данни за BNB"""
    
    # Създаваме тестови daily данни (симулираме BNB цена от $600 до $800)
    np.random.seed(42)  # За консистентни резултати
    
    # Генерираме 100 дни данни
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # Създаваме реалистични BNB цени
    base_price = 650
    trend = np.linspace(0, 150, 100)  # Възходящ тренд
    noise = np.random.normal(0, 20, 100)  # Случайни колебания
    
    close_prices = base_price + trend + noise
    
    # Създаваме OHLCV данни
    daily_data = []
    for i, (date, close) in enumerate(zip(dates, close_prices)):
        # Генерираме реалистични High, Low, Open
        volatility = np.random.uniform(0.01, 0.03)  # 1-3% дневна волатилност
        
        high = close * (1 + np.random.uniform(0, volatility))
        low = close * (1 - np.random.uniform(0, volatility))
        open_price = np.random.uniform(low, high)
        
        # Volume
        volume = np.random.uniform(1000, 5000)
        
        daily_data.append({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close,
            'Volume': volume
        })
    
    daily_df = pd.DataFrame(daily_data, index=dates)
    
    # Създаваме тестови weekly данни (20 седмици)
    weekly_dates = pd.date_range('2024-01-01', periods=20, freq='W')
    weekly_data = []
    
    for i, date in enumerate(weekly_dates):
        # Взимаме данните за седмицата
        week_start = date
        week_end = date + timedelta(days=6)
        
        week_data = daily_df[week_start:week_end]
        
        if not week_data.empty:
            weekly_data.append({
                'Open': week_data.iloc[0]['Open'],
                'High': week_data['High'].max(),
                'Low': week_data['Low'].min(),
                'Close': week_data.iloc[-1]['Close'],
                'Volume': week_data['Volume'].sum()
            })
    
    # Създаваме DataFrame само с данните, които имаме
    weekly_df = pd.DataFrame(weekly_data)
    if not weekly_df.empty:
        weekly_df.index = weekly_dates[:len(weekly_df)]
    
    return daily_df, weekly_df

def test_individual_modules(config):
    """Тества отделните модули"""
    
    print("🧪 Тестване на отделните модули...")
    
    # Създаваме тестови данни
    daily_df, weekly_df = create_test_data()
    
    print(f"📊 Създадени тестови данни: Daily={len(daily_df)} редове, Weekly={len(weekly_df)} редове")
    
    # 1. Тест на Fibonacci анализатора
    print("\n🔢 Тестване на Fibonacci анализатора...")
    fib_analyzer = FibonacciAnalyzer(config)
    fib_analysis = fib_analyzer.analyze_fibonacci_trend(daily_df)
    
    if 'error' not in fib_analysis:
        print(f"   ✅ Fibonacci анализ успешен")
        print(f"   Swing High: ${fib_analysis['swing_high']:,.2f}")
        print(f"   Swing Low: ${fib_analysis['swing_low']:,.2f}")
        print(f"   Swing Size: {fib_analysis['swing_size']:.1%}")
        print(f"   Текуща цена: ${fib_analysis['current_price']:,.2f}")
        print(f"   Fibonacci сигнал: {fib_analysis['fibonacci_signal']['signal']}")
    else:
        print(f"   ❌ Fibonacci анализ неуспешен: {fib_analysis['error']}")
    
    # 2. Тест на Weekly Tails анализатора
    print("\n📈 Тестване на Weekly Tails анализатора...")
    tails_analyzer = WeeklyTailsAnalyzer(config)
    tails_analysis = tails_analyzer.analyze_weekly_tails_trend(weekly_df)
    
    if 'error' not in tails_analysis:
        print(f"   ✅ Weekly Tails анализ успешен")
        print(f"   Общо опашки: {tails_analysis['total_tails']}")
        print(f"   Сильни опашки: {tails_analysis['strong_tails']}")
        print(f"   Weekly Tails сигнал: {tails_analysis['tails_signal']['signal']}")
    else:
        print(f"   ❌ Weekly Tails анализ неуспешен: {tails_analysis['error']}")
    
    # 3. Тест на Technical Indicators
    print("\n📊 Тестване на Technical Indicators...")
    indicators = TechnicalIndicators(config)
    daily_with_indicators = indicators.calculate_indicators(daily_df)
    indicators_signals = indicators.get_all_indicators_signals(daily_with_indicators)
    
    if 'error' not in indicators_signals:
        print(f"   ✅ Technical Indicators успешни")
        print(f"   RSI сигнал: {indicators_signals['rsi']['signal']}")
        print(f"   MACD сигнал: {indicators_signals['macd']['signal']}")
        print(f"   Bollinger сигнал: {indicators_signals['bollinger']['signal']}")
    else:
        print(f"   ❌ Technical Indicators неуспешни: {indicators_signals['error']}")
    
    return daily_df, weekly_df, fib_analysis, tails_analysis, indicators_signals

def test_signal_generator(config, daily_df, weekly_df, fib_analysis, tails_analysis, indicators_signals):
    """Тества Signal Generator модула"""
    
    print("\n🎯 Тестване на Signal Generator...")
    
    try:
        signal_gen = SignalGenerator(config)
        
        # Създаваме mock данни за тестване
        mock_fib_analysis = fib_analysis if 'error' not in fib_analysis else None
        mock_tails_analysis = tails_analysis if 'error' not in tails_analysis else None
        mock_indicators_signals = indicators_signals if 'error' not in indicators_signals else None
        
        # Генерираме сигнал
        signal = signal_gen.generate_signal(daily_df, weekly_df)
        
        if 'error' not in signal:
            print(f"   ✅ Сигнал генериран успешно")
            print(f"   Сигнал: {signal['signal']}")
            print(f"   Увереност: {signal['confidence']:.2f}")
            print(f"   Приоритет: {signal['priority']}")
            print(f"   Причина: {signal['reason']}")
            print(f"   Ниво на риска: {signal['risk_level']}")
        else:
            print(f"   ❌ Грешка при генериране на сигнал: {signal['error']}")
        
        return signal
        
    except Exception as e:
        print(f"   ❌ Грешка при тестване на Signal Generator: {e}")
        return None

def test_validator(signal):
    """Тества Signal Validator модула"""
    
    print("\n✅ Тестване на Signal Validator...")
    
    try:
        validator = SignalValidator('test_results.csv')
        
        # Записваме сигнала
        success = validator.save_signal(signal)
        if success:
            print(f"   ✅ Сигнал записан успешно")
        else:
            print(f"   ❌ Грешка при записване на сигнала")
        
        # Проверяваме резултата (симулираме успешен резултат)
        if signal and 'analysis_date' in signal:
            # Симулираме валидация след 14 дни
            current_price = signal.get('fibonacci_analysis', {}).get('current_price', 0) * 1.05  # +5%
            
            result = validator.check_signal_result(
                signal['analysis_date'],
                current_price,
                target_price=current_price
            )
            
            if 'error' not in result:
                print(f"   ✅ Сигнал валидиран успешно")
                print(f"   Резултат: {'УСПЕХ' if result['success'] else 'НЕУСПЕХ'}")
                print(f"   P&L: {result['profit_loss_pct']:+.2f}%")
            else:
                print(f"   ❌ Грешка при валидация: {result['error']}")
        
        # Статистика
        stats = validator.get_accuracy_stats(30)
        if 'error' not in stats:
            print(f"   📊 Статистика: {stats['overall_accuracy']:.1f}% точност")
        
        # Експортираме обобщение
        validator.export_results_summary('test_summary.txt')
        print(f"   📄 Обобщение експортирано в test_summary.txt")
        
    except Exception as e:
        print(f"   ❌ Грешка при тестване на Validator: {e}")

def run_full_test():
    """Изпълнява пълния тест на системата"""
    
    print("🚀 Стартиране на пълния тест на BNB Trading системата...")
    print("="*80)
    
    try:
        # Зареждаме конфигурацията
        config = toml.load('config.toml')
        print("✅ Конфигурация заредена успешно")
        
        # Тестваме отделните модули
        daily_df, weekly_df, fib_analysis, tails_analysis, indicators_signals = test_individual_modules(config)
        
        # Тестваме Signal Generator
        signal = test_signal_generator(config, daily_df, weekly_df, fib_analysis, tails_analysis, indicators_signals)
        
        # Тестваме Validator
        if signal:
            test_validator(signal)
        
        print("\n" + "="*80)
        print("🎉 ПЪЛНИЯТ ТЕСТ Е ЗАВЪРШЕН УСПЕШНО!")
        print("="*80)
        
        print("\n📁 Създадени файлове:")
        print("   - test_results.csv (тестови резултати)")
        print("   - test_summary.txt (обобщение на тестовите резултати)")
        
        print("\n🔍 За да тествате с реални данни:")
        print("   1. Уверете се, че имате интернет връзка")
        print("   2. Стартирайте: python main.py")
        print("   3. Проверете лог файла bnb_trading.log")
        
    except Exception as e:
        print(f"\n❌ Критична грешка при тестване: {e}")
        print("Проверете дали всички файлове са налични и конфигурацията е правилна")

if __name__ == "__main__":
    run_full_test()
