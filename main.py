"""
BNB Trading System - Главен файл
Комбинира всички модули за генериране на Long/Short сигнали
Фокус върху Fibonacci нива и седмични опашки
"""

import pandas as pd
import numpy as np
import toml
import logging
from datetime import datetime, timedelta
import sys
import os
from typing import Dict

# Добавяме текущата директория в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import BNBDataFetcher
from signal_generator import SignalGenerator
from validator import SignalValidator

# Настройваме logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bnb_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BNBTradingSystem:
    """Главен клас на BNB Trading системата"""
    
    def __init__(self, config_file: str = 'config.toml'):
        """
        Инициализира BNB Trading системата
        
        Args:
            config_file: Път до конфигурационния файл
        """
        try:
            # Зареждаме конфигурацията
            self.config = toml.load(config_file)
            logger.info(f"Конфигурация заредена от {config_file}")
            
            # Инициализираме компонентите
            self.data_fetcher = BNBDataFetcher(self.config['data']['symbol'])
            self.signal_generator = SignalGenerator(self.config)
            self.validator = SignalValidator('data/results.csv')
            
            logger.info("BNB Trading системата инициализирана успешно")
            
        except Exception as e:
            logger.error(f"Грешка при инициализиране на системата: {e}")
            raise
    
    def run_analysis(self) -> Dict:
        """
        Изпълнява пълния анализ на BNB
        
        Returns:
            Dict с резултатите от анализа
        """
        try:
            logger.info("Започва BNB анализ...")
            
            # 1. Извличаме данни
            logger.info("Извличане на BNB данни...")
            data = self.data_fetcher.fetch_bnb_data(self.config['data']['lookback_days'])
            
            if not data or 'daily' not in data or 'weekly' not in data:
                raise ValueError("Неуспешно извличане на данни")
            
            daily_df = data['daily']
            weekly_df = data['weekly']
            
            logger.info(f"Данни извлечени: Daily={len(daily_df)} редове, Weekly={len(weekly_df)} редове")
            
            # 2. Валидираме качеството на данните
            daily_quality = self.data_fetcher.validate_data_quality(daily_df)
            weekly_quality = self.data_fetcher.validate_data_quality(weekly_df)
            
            logger.info(f"Качество на daily данните: {daily_quality['data_quality_score']:.2%}")
            logger.info(f"Качество на weekly данните: {weekly_quality['data_quality_score']:.2%}")
            
            # 3. Генерираме сигнал
            logger.info("Генериране на trading сигнал...")
            signal = self.signal_generator.generate_signal(daily_df, weekly_df)
            
            if 'error' in signal:
                raise ValueError(f"Грешка при генериране на сигнал: {signal['error']}")
            
            # 4. Записваме сигнала
            logger.info("Записване на сигнала...")
            self.validator.save_signal(signal)
            
            # 5. Подготвяме резултатите за показване
            results = self._prepare_results_for_display(signal, daily_df, weekly_df)
            
            logger.info("BNB анализ завършен успешно")
            return results
            
        except Exception as e:
            logger.error(f"Грешка при изпълнение на анализа: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _prepare_results_for_display(self, signal: Dict, daily_df: pd.DataFrame, 
                                   weekly_df: pd.DataFrame) -> Dict:
        """
        Подготвя резултатите за показване
        
        Args:
            signal: Генерираният сигнал
            daily_df: Daily данни
            weekly_df: Weekly данни
            
        Returns:
            Dict с форматирани резултати
        """
        try:
            current_price = signal.get('fibonacci_analysis', {}).get('current_price', 0)
            
            # Форматираме Fibonacci нива
            fib_levels_display = []
            if signal.get('fibonacci_analysis') and 'fibonacci_levels' in signal['fibonacci_analysis']:
                fib_levels = signal['fibonacci_analysis']['fibonacci_levels']
                for level, price in fib_levels.items():
                    distance = abs(current_price - price)
                    distance_pct = (distance / current_price) * 100
                    fib_levels_display.append({
                        'level': f"{level*100:.1f}%",
                        'price': f"${price:,.2f}",
                        'distance': f"${distance:,.2f}",
                        'distance_pct': f"{distance_pct:.2f}%"
                    })
            
            # Форматираме Weekly Tails
            tails_display = []
            if signal.get('weekly_tails_analysis') and 'tails_analysis' in signal['weekly_tails_analysis']:
                for tail in signal['weekly_tails_analysis']['tails_analysis'][:5]:  # Последните 5
                    tails_display.append({
                        'date': tail['date'].strftime('%Y-%m-%d'),
                        'type': tail['dominant_tail'],
                        'strength': f"{tail['tail_strength']:.1%}",
                        'signal': tail['signal'],
                        'price': f"${tail['close']:,.2f}"
                    })
            
            # Форматираме Fibonacci + Tails съвпадения
            confluence_display = []
            if signal.get('confluence_info') and 'confluence_points' in signal['confluence_info']:
                for point in signal['confluence_info']['confluence_points'][:3]:  # Топ 3
                    confluence_display.append({
                        'tail_date': point['tail_date'].strftime('%Y-%m-%d'),
                        'fib_level': f"{point['fib_level']*100:.1f}%",
                        'confluence_score': f"{point['confluence_score']:.2f}",
                        'signal': point['tail_signal']
                    })
            
            # Форматираме следващите цели
            next_targets_display = {}
            if signal.get('next_targets'):
                next_targets = signal['next_targets']
                if next_targets.get('entry_price'):
                    next_targets_display['entry'] = f"${next_targets['entry_price']:,.2f}"
                if next_targets.get('exit_price'):
                    next_targets_display['exit'] = f"${next_targets['exit_price']:,.2f}"
                if next_targets.get('fibonacci_levels'):
                    next_targets_display['fib_levels'] = next_targets['fibonacci_levels']
            
            # Статистика за точността
            accuracy_stats = self.validator.get_accuracy_stats(30)
            
            # Последните сигнали
            recent_signals = self.validator.get_recent_signals(20)
            recent_signals_display = []
            if not recent_signals.empty:
                for _, row in recent_signals.iterrows():
                    signal_info = {
                        'date': row['signal_date'].strftime('%Y-%m-%d'),
                        'type': row['signal_type'],
                        'price': f"${row['signal_price']:,.2f}",
                        'confidence': f"{row['confidence']:.1f}",
                        'priority': row['priority'],
                        'status': 'Валидиран' if pd.notna(row['validation_date']) else 'Очаква валидация'
                    }
                    if pd.notna(row['validation_date']):
                        signal_info['result'] = '✓' if row['success'] else '✗'
                        signal_info['pnl'] = f"{row['profit_loss_pct']:+.2f}%"
                    recent_signals_display.append(signal_info)
            
            formatted_results = {
                'current_signal': {
                    'signal': signal['signal'],
                    'confidence': f"{signal['confidence']:.1f}",
                    'priority': signal['priority'],
                    'reason': signal['reason'],
                    'risk_level': signal['risk_level']
                },
                'current_price': f"${current_price:,.2f}",
                'fibonacci_levels': fib_levels_display,
                'weekly_tails': tails_display,
                'fib_tail_confluence': confluence_display,
                'next_targets': next_targets_display,
                'accuracy_stats': accuracy_stats,
                'recent_signals': recent_signals_display,
                'analysis_date': signal.get('analysis_date', pd.Timestamp.now())
            }
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Грешка при форматиране на резултатите: {e}")
            return {'error': f'Грешка при форматиране: {e}'}
    
    def display_results(self, results: Dict):
        """
        Показва резултатите в конзолата
        
        Args:
            results: Форматираните резултати
        """
        try:
            if 'error' in results:
                print(f"❌ Грешка: {results['error']}")
                return
            
            print("\n" + "="*80)
            print("🚀 BNB TRADING SYSTEM - АНАЛИЗ РЕЗУЛТАТИ")
            print("="*80)
            
            # Текущ сигнал
            current_signal = results['current_signal']
            print(f"\n📊 ТЕКУЩ СИГНАЛ:")
            print(f"   Сигнал: {current_signal['signal']}")
            print(f"   Увереност: {current_signal['confidence']}")
            print(f"   Приоритет: {current_signal['priority']}")
            print(f"   Ниво на риска: {current_signal['risk_level']}")
            print(f"   Причина: {current_signal['reason']}")
            
            # Текуща цена
            print(f"\n💰 ТЕКУЩА ЦЕНА: {results['current_price']}")
            
            # Fibonacci нива
            if results['fibonacci_levels']:
                print(f"\n🔢 FIBONACCI НИВА:")
                print(f"   {'Ниво':<8} {'Цена':<12} {'Разстояние':<12} {'%':<8}")
                print(f"   {'-'*8} {'-'*12} {'-'*12} {'-'*8}")
                for level in results['fibonacci_levels']:
                    print(f"   {level['level']:<8} {level['price']:<12} {level['distance']:<12} {level['distance_pct']:<8}")
            
            # Weekly Tails
            if results['weekly_tails']:
                print(f"\n📈 СЕДМИЧНИ ОПАШКИ (последните 5):")
                print(f"   {'Дата':<12} {'Тип':<8} {'Сила':<8} {'Сигнал':<8} {'Цена':<12}")
                print(f"   {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*12}")
                for tail in results['weekly_tails']:
                    print(f"   {tail['date']:<12} {tail['type']:<8} {tail['strength']:<8} {tail['signal']:<8} {tail['price']:<12}")
            
            # Fibonacci + Tails съвпадения
            if results['fib_tail_confluence']:
                print(f"\n🎯 FIBONACCI + TAILS СЪВПАДЕНИЯ:")
                print(f"   {'Дата':<12} {'Fib Ниво':<10} {'Съвпадение':<12} {'Сигнал':<8}")
                print(f"   {'-'*12} {'-'*10} {'-'*12} {'-'*8}")
                for confluence in results['fib_tail_confluence']:
                    print(f"   {confluence['tail_date']:<12} {confluence['fib_level']:<10} {confluence['confluence_score']:<12} {confluence['signal']:<8}")
            
            # Следващи цели
            if results['next_targets']:
                print(f"\n🎯 СЛЕДВАЩИ ЦЕЛИ:")
                if 'entry' in results['next_targets']:
                    print(f"   Entry: {results['next_targets']['entry']}")
                if 'exit' in results['next_targets']:
                    print(f"   Exit: {results['next_targets']['exit']}")
                if 'fib_levels' in results['next_targets']:
                    for target_type, fib_level in results['next_targets']['fib_levels'].items():
                        print(f"   {target_type.capitalize()}: {fib_level}")
            
            # Статистика за точността
            if 'accuracy_stats' in results and 'error' not in results['accuracy_stats']:
                stats = results['accuracy_stats']
                print(f"\n📈 СТАТИСТИКА ЗА ТОЧНОСТТА (последните 30 дни):")
                print(f"   Обща точност: {stats['overall_accuracy']:.1f}% ({stats['successful_signals']}/{stats['total_signals']})")
                print(f"   LONG сигнали: {stats['long_signals']['accuracy']:.1f}% ({stats['long_signals']['success']}/{stats['long_signals']['total']})")
                print(f"   SHORT сигнали: {stats['short_signals']['accuracy']:.1f}% ({stats['short_signals']['success']}/{stats['short_signals']['total']})")
                print(f"   Среден P&L: {stats['avg_profit_loss_pct']:+.2f}%")
            
            # Последните сигнали
            if results['recent_signals']:
                print(f"\n📋 ПОСЛЕДНИ СИГНАЛИ (последните 20):")
                print(f"   {'Дата':<12} {'Тип':<8} {'Цена':<12} {'Увереност':<10} {'Приоритет':<10} {'Статус':<15}")
                print(f"   {'-'*12} {'-'*8} {'-'*12} {'-'*10} {'-'*10} {'-'*15}")
                for signal in results['recent_signals'][:10]:  # Показваме първите 10
                    status = signal['status']
                    if 'result' in signal:
                        status = f"{signal['result']} {signal['pnl']}"
                    print(f"   {signal['date']:<12} {signal['type']:<8} {signal['price']:<12} {signal['confidence']:<10} {signal['priority']:<10} {status:<15}")
            
            print(f"\n⏰ Анализът е извършен на: {results['analysis_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Грешка при показване на резултатите: {e}")
            print(f"❌ Грешка при показване на резултатите: {e}")
    
    def export_results(self, results: Dict, output_file: str = 'data/analysis_results.txt'):
        """
        Експортира резултатите в текстов файл
        
        Args:
            results: Резултатите за експортиране
            output_file: Име на изходния файл
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("BNB Trading System - Анализ Резултати\n")
                f.write("="*50 + "\n\n")
                
                if 'error' in results:
                    f.write(f"Грешка: {results['error']}\n")
                    return
                
                # Текущ сигнал
                current_signal = results['current_signal']
                f.write(f"ТЕКУЩ СИГНАЛ:\n")
                f.write(f"  Сигнал: {current_signal['signal']}\n")
                f.write(f"  Увереност: {current_signal['confidence']}\n")
                f.write(f"  Приоритет: {current_signal['priority']}\n")
                f.write(f"  Ниво на риска: {current_signal['risk_level']}\n")
                f.write(f"  Причина: {current_signal['reason']}\n\n")
                
                # Текуща цена
                f.write(f"ТЕКУЩА ЦЕНА: {results['current_price']}\n\n")
                
                # Fibonacci нива
                if results['fibonacci_levels']:
                    f.write("FIBONACCI НИВА:\n")
                    for level in results['fibonacci_levels']:
                        f.write(f"  {level['level']}: {level['price']} (разстояние: {level['distance']}, {level['distance_pct']})\n")
                    f.write("\n")
                
                # Weekly Tails
                if results['weekly_tails']:
                    f.write("СЕДМИЧНИ ОПАШКИ:\n")
                    for tail in results['weekly_tails']:
                        f.write(f"  {tail['date']}: {tail['type']} опашка, сила: {tail['strength']}, сигнал: {tail['signal']}, цена: {tail['price']}\n")
                    f.write("\n")
                
                # Следващи цели
                if results['next_targets']:
                    f.write("СЛЕДВАЩИ ЦЕЛИ:\n")
                    for target_type, value in results['next_targets'].items():
                        f.write(f"  {target_type}: {value}\n")
                    f.write("\n")
                
                # Статистика
                if 'accuracy_stats' in results and 'error' not in results['accuracy_stats']:
                    stats = results['accuracy_stats']
                    f.write("СТАТИСТИКА ЗА ТОЧНОСТТА:\n")
                    f.write(f"  Обща точност: {stats['overall_accuracy']:.1f}%\n")
                    f.write(f"  LONG сигнали: {stats['long_signals']['accuracy']:.1f}%\n")
                    f.write(f"  SHORT сигнали: {stats['short_signals']['accuracy']:.1f}%\n")
                    f.write(f"  Среден P&L: {stats['avg_profit_loss_pct']:+.2f}%\n\n")
                
                f.write(f"Анализът е извършен на: {results['analysis_date'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Резултати експортирани в {output_file}")
            
        except Exception as e:
            logger.error(f"Грешка при експортиране на резултатите: {e}")

def main():
    """Главна функция"""
    try:
        print("🚀 Стартиране на BNB Trading System...")
        
        # Създаваме системата
        trading_system = BNBTradingSystem()
        
        # Изпълняваме анализа
        results = trading_system.run_analysis()
        
        if 'error' in results:
            print(f"❌ Грешка: {results['error']}")
            return
        
        # Показваме резултатите
        trading_system.display_results(results)
        
        # Експортираме резултатите
        trading_system.export_results(results)
        
        # Експортираме обобщение на резултатите
        trading_system.validator.export_results_summary('data/results_summary.txt')
        
        print("\n✅ Анализът е завършен успешно!")
        print("📁 Резултатите са записани в:")
        print("   - data/analysis_results.txt")
        print("   - data/results_summary.txt")
        print("   - data/results.csv")
        
    except Exception as e:
        logger.error(f"Критична грешка: {e}")
        print(f"❌ Критична грешка: {e}")
        print("Проверете лог файла 'bnb_trading.log' за повече детайли")

if __name__ == "__main__":
    main()
