"""
Backtesting Module - Анализира последните 18 месеца и показва точността на сигналите
Проверява дали сигналите са били коректни (цената се е вдигнала/спуснала през следващите 2 седмици)
"""

import pandas as pd
import numpy as np
import toml
import logging
from datetime import datetime, timedelta
import sys
import os
from typing import Dict, List

# Добавяме текущата директория в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import BNBDataFetcher
from fibonacci import FibonacciAnalyzer
from weekly_tails import WeeklyTailsAnalyzer
from indicators import TechnicalIndicators
from signal_generator import SignalGenerator

# Настройваме logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Backtester:
    """Клас за backtesting на BNB Trading системата"""
    
    def __init__(self, config_file: str = 'config.toml'):
        """
        Инициализира backtester-а
        
        Args:
            config_file: Път до конфигурационния файл
        """
        try:
            # Зареждаме конфигурацията
            self.config = toml.load(config_file)
            logger.info(f"Конфигурация заредена от {config_file}")
            
            # Инициализираме компонентите
            self.data_fetcher = BNBDataFetcher(self.config['data']['symbol'])
            self.fib_analyzer = FibonacciAnalyzer(self.config)
            self.tails_analyzer = WeeklyTailsAnalyzer(self.config)
            self.indicators = TechnicalIndicators(self.config)
            self.signal_generator = SignalGenerator(self.config)
            
            logger.info("Backtester инициализиран успешно")
            
        except Exception as e:
            logger.error(f"Грешка при инициализиране на backtester: {e}")
            raise
    
    def run_backtest(self, months: int = 18) -> Dict:
        """
        Изпълнява backtest за последните N месеца
        
        Args:
            months: Брой месеци за backtesting
            
        Returns:
            Dict с резултатите от backtest-а
        """
        try:
            logger.info(f"Стартиране на backtest за последните {months} месеца...")
            
            # Изчисляваме дни за lookback
            lookback_days = months * 30
            
            # Извличаме данни
            logger.info(f"Извличане на {lookback_days} дни данни...")
            data = self.data_fetcher.fetch_bnb_data(lookback_days)
            
            if not data or 'daily' not in data or 'weekly' not in data:
                raise ValueError("Неуспешно извличане на данни")
            
            daily_df = data['daily']
            weekly_df = data['weekly']
            
            logger.info(f"Данни извлечени: Daily={len(daily_df)} редове, Weekly={len(weekly_df)} редове")
            
            # Изпълняваме backtest
            backtest_results = self._execute_backtest(daily_df, weekly_df)
            
            logger.info("Backtest завършен успешно")
            return backtest_results
            
        except Exception as e:
            logger.error(f"Грешка при изпълнение на backtest: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _execute_backtest(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Dict:
        """
        Изпълнява backtest логиката
        
        Args:
            daily_df: Daily данни
            weekly_df: Weekly данни
            
        Returns:
            Dict с резултатите от backtest-а
        """
        try:
            # Намираме начална дата за backtest (18 месеца назад)
            end_date = daily_df.index[-1]
            start_date = end_date - pd.Timedelta(days=18*30)
            
            # Филтрираме данните за backtest периода
            backtest_daily = daily_df[start_date:end_date]
            backtest_weekly = weekly_df[start_date:end_date]
            
            logger.info(f"Backtest период: {start_date.strftime('%Y-%m-%d')} до {end_date.strftime('%Y-%m-%d')}")
            
            # Генерираме сигнали за всеки ден (или седмица)
            signals = []
            
            # Генерираме сигнали на седмична база за по-ефективност
            for i in range(len(backtest_weekly) - 8):  # -8 за да имаме достатъчно данни за анализ
                current_date = backtest_weekly.index[i]
                
                # Взимаме данните до текущата дата
                current_daily = backtest_daily[:current_date]
                current_weekly = backtest_weekly[:i+1]
                
                if len(current_daily) < 100 or len(current_weekly) < 8:
                    continue
                
                try:
                    # Генерираме сигнал за текущата дата
                    signal = self._generate_historical_signal(current_daily, current_weekly, current_date)
                    
                    if signal and signal['signal'] != 'HOLD':
                        # Проверяваме резултата след 2 седмици
                        result = self._validate_historical_signal(signal, backtest_daily, current_date)
                        
                        if result:
                            signals.append({
                                'date': current_date,
                                'signal': signal,
                                'result': result
                            })
                            
                            logger.info(f"Сигнал {current_date.strftime('%Y-%m-%d')}: {signal['signal']} - {'УСПЕХ' if result['success'] else 'НЕУСПЕХ'}")
                
                except Exception as e:
                    logger.warning(f"Грешка при генериране на сигнал за {current_date}: {e}")
                    continue
            
            # Анализираме резултатите
            analysis = self._analyze_backtest_results(signals)
            
            return {
                'signals': signals,
                'analysis': analysis,
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_days': len(backtest_daily),
                    'total_weeks': len(backtest_weekly)
                }
            }
            
        except Exception as e:
            logger.error(f"Грешка при изпълнение на backtest логиката: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _generate_historical_signal(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame, date: pd.Timestamp) -> Dict:
        """
        Генерира сигнал за историческа дата
        
        Args:
            daily_df: Daily данни до датата
            weekly_df: Weekly данни до датата
            date: Дата за генериране на сигнал
            
        Returns:
            Dict с генерирания сигнал
        """
        try:
            # Генерираме сигнал
            signal = self.signal_generator.generate_signal(daily_df, weekly_df)
            
            if 'error' in signal:
                return None
            
            return signal
            
        except Exception as e:
            logger.error(f"Грешка при генериране на исторически сигнал: {e}")
            return None
    
    def _validate_historical_signal(self, signal: Dict, daily_df: pd.DataFrame, signal_date: pd.Timestamp) -> Dict:
        """
        Валидира исторически сигнал след 2 седмици
        
        Args:
            signal: Генерираният сигнал
            daily_df: Daily данни
            signal_date: Дата на сигнала
            
        Returns:
            Dict с резултата от валидацията
        """
        try:
            # Намираме цената на сигнала
            signal_price = signal.get('fibonacci_analysis', {}).get('current_price', 0)
            if signal_price == 0:
                return None
            
            # Намираме цената след 2 седмици
            validation_date = signal_date + pd.Timedelta(days=14)
            
            # Търсим най-близката дата след 2 седмици
            future_data = daily_df[daily_df.index > signal_date]
            if future_data.empty:
                return None
            
            # Взимаме цената след 2 седмици (или най-близката налична)
            target_data = future_data[future_data.index >= validation_date]
            if target_data.empty:
                # Ако няма данни точно след 2 седмици, взимаме последните налични
                target_data = future_data.tail(1)
            
            validation_price = target_data.iloc[-1]['Close']
            validation_date_actual = target_data.index[-1]
            
            # Изчисляваме резултата
            signal_type = signal['signal']
            
            if signal_type == 'LONG':
                profit_loss = validation_price - signal_price
                profit_loss_pct = (profit_loss / signal_price) * 100
                success = profit_loss > 0
            elif signal_type == 'SHORT':
                profit_loss = signal_price - validation_price
                profit_loss_pct = (profit_loss / signal_price) * 100
                success = profit_loss > 0
            else:
                return None
            
            # Изчисляваме дни до валидацията
            days_to_target = (validation_date_actual - signal_date).days
            
            # Определяме причината за неуспех (ако има такъв)
            failure_reason = ''
            if not success:
                if signal_type == 'LONG':
                    failure_reason = f"Цената падна от ${signal_price:,.2f} до ${validation_price:,.2f}"
                elif signal_type == 'SHORT':
                    failure_reason = f"Цената се повиши от ${signal_price:,.2f} до ${validation_price:,.2f}"
            
            return {
                'signal_date': signal_date,
                'validation_date': validation_date_actual,
                'signal_price': signal_price,
                'validation_price': validation_price,
                'profit_loss': profit_loss,
                'profit_loss_pct': profit_loss_pct,
                'success': success,
                'failure_reason': failure_reason,
                'days_to_target': days_to_target
            }
            
        except Exception as e:
            logger.error(f"Грешка при валидация на исторически сигнал: {e}")
            return None
    
    def _analyze_backtest_results(self, signals: List[Dict]) -> Dict:
        """
        Анализира резултатите от backtest-а
        
        Args:
            signals: Списък с сигнали и резултати
            
        Returns:
            Dict с анализ на резултатите
        """
        try:
            if not signals:
                return {'error': 'Няма сигнали за анализ'}
            
            # Обща статистика
            total_signals = len(signals)
            successful_signals = len([s for s in signals if s['result']['success']])
            accuracy = (successful_signals / total_signals) * 100 if total_signals > 0 else 0
            
            # Статистика по тип сигнал
            long_signals = [s for s in signals if s['signal']['signal'] == 'LONG']
            short_signals = [s for s in signals if s['signal']['signal'] == 'SHORT']
            
            long_accuracy = 0
            if long_signals:
                long_success = len([s for s in long_signals if s['result']['success']])
                long_accuracy = (long_success / len(long_signals)) * 100
            
            short_accuracy = 0
            if short_signals:
                short_success = len([s for s in short_signals if s['result']['success']])
                short_accuracy = (short_success / len(short_signals)) * 100
            
            # Статистика по приоритет
            priority_stats = {}
            for signal_data in signals:
                priority = signal_data['signal']['priority']
                if priority not in priority_stats:
                    priority_stats[priority] = {'total': 0, 'success': 0}
                
                priority_stats[priority]['total'] += 1
                if signal_data['result']['success']:
                    priority_stats[priority]['success'] += 1
            
            # Изчисляваме точност по приоритет
            for priority in priority_stats:
                total = priority_stats[priority]['total']
                success = priority_stats[priority]['success']
                priority_stats[priority]['accuracy'] = (success / total) * 100 if total > 0 else 0
            
            # Среден P&L
            all_pnl = [s['result']['profit_loss_pct'] for s in signals]
            avg_profit_loss = np.mean(all_pnl) if all_pnl else 0
            
            successful_pnl = [s['result']['profit_loss_pct'] for s in signals if s['result']['success']]
            avg_profit_loss_success = np.mean(successful_pnl) if successful_pnl else 0
            
            failed_pnl = [s['result']['profit_loss_pct'] for s in signals if not s['result']['success']]
            avg_profit_loss_failure = np.mean(failed_pnl) if failed_pnl else 0
            
            # Най-добри и най-лоши сигнали
            best_signals = sorted(signals, key=lambda x: x['result']['profit_loss_pct'], reverse=True)[:5]
            worst_signals = sorted(signals, key=lambda x: x['result']['profit_loss_pct'])[:5]
            
            analysis = {
                'total_signals': total_signals,
                'successful_signals': successful_signals,
                'overall_accuracy': accuracy,
                'long_signals': {
                    'total': len(long_signals),
                    'success': len([s for s in long_signals if s['result']['success']]),
                    'accuracy': long_accuracy
                },
                'short_signals': {
                    'total': len(short_signals),
                    'success': len([s for s in short_signals if s['result']['success']]),
                    'accuracy': short_accuracy
                },
                'priority_stats': priority_stats,
                'avg_profit_loss_pct': avg_profit_loss,
                'avg_profit_loss_success_pct': avg_profit_loss_success,
                'avg_profit_loss_failure_pct': avg_profit_loss_failure,
                'best_signals': best_signals,
                'worst_signals': worst_signals,
                'analysis_date': pd.Timestamp.now()
            }
            
            logger.info(f"Backtest анализ: {accuracy:.1f}% точност ({successful_signals}/{total_signals})")
            return analysis
            
        except Exception as e:
            logger.error(f"Грешка при анализ на backtest резултатите: {e}")
            return {'error': f'Грешка: {e}'}
    
    def export_backtest_results(self, results: Dict, output_file: str = 'data/backtest_results.txt'):
        """
        Експортира резултатите от backtest-а в текстов файл
        
        Args:
            results: Резултатите от backtest-а
            output_file: Име на изходния файл
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("BNB Trading System - Backtest Резултати (18 месеца)\n")
                f.write("=" * 60 + "\n\n")
                
                if 'error' in results:
                    f.write(f"Грешка: {results['error']}\n")
                    return
                
                # Период на backtest-а
                period = results['period']
                f.write(f"ПЕРИОД НА BACKTEST:\n")
                f.write(f"  От: {period['start_date'].strftime('%Y-%m-%d')}\n")
                f.write(f"  До: {period['end_date'].strftime('%Y-%m-%d')}\n")
                f.write(f"  Общо дни: {period['total_days']}\n")
                f.write(f"  Общо седмици: {period['total_weeks']}\n\n")
                
                # Анализ на резултатите
                analysis = results['analysis']
                f.write("АНАЛИЗ НА РЕЗУЛТАТИТЕ:\n")
                f.write(f"  Общо сигнали: {analysis['total_signals']}\n")
                f.write(f"  Успешни сигнали: {analysis['successful_signals']}\n")
                f.write(f"  Обща точност: {analysis['overall_accuracy']:.1f}%\n\n")
                
                # Статистика по тип сигнал
                f.write("СТАТИСТИКА ПО ТИП СИГНАЛ:\n")
                f.write(f"  LONG сигнали: {analysis['long_signals']['accuracy']:.1f}% ({analysis['long_signals']['success']}/{analysis['long_signals']['total']})\n")
                f.write(f"  SHORT сигнали: {analysis['short_signals']['accuracy']:.1f}% ({analysis['short_signals']['success']}/{analysis['short_signals']['total']})\n\n")
                
                # P&L статистика по тип сигнал
                if analysis['long_signals']['total'] > 0:
                    long_pnl = [s['result']['profit_loss_pct'] for s in results['signals'] if s['signal']['signal'] == 'LONG']
                    long_avg_pnl = np.mean(long_pnl) if long_pnl else 0
                    long_success_pnl = [s['result']['profit_loss_pct'] for s in results['signals'] if s['signal']['signal'] == 'LONG' and s['result']['success']]
                    long_success_avg_pnl = np.mean(long_success_pnl) if long_success_pnl else 0
                    f.write("P&L СТАТИСТИКА - LONG СИГНАЛИ:\n")
                    f.write(f"  Среден P&L: {long_avg_pnl:+.2f}%\n")
                    f.write(f"  Среден P&L (успешни): {long_success_avg_pnl:+.2f}%\n")
                    f.write(f"  Брой сигнали: {analysis['long_signals']['total']}\n\n")
                
                if analysis['short_signals']['total'] > 0:
                    short_pnl = [s['result']['profit_loss_pct'] for s in results['signals'] if s['signal']['signal'] == 'SHORT']
                    short_avg_pnl = np.mean(short_pnl) if short_pnl else 0
                    short_success_pnl = [s['result']['profit_loss_pct'] for s in results['signals'] if s['signal']['signal'] == 'SHORT' and s['result']['success']]
                    short_success_avg_pnl = np.mean(short_success_pnl) if short_success_pnl else 0
                    f.write("P&L СТАТИСТИКА - SHORT СИГНАЛИ:\n")
                    f.write(f"  Среден P&L: {short_avg_pnl:+.2f}%\n")
                    f.write(f"  Среден P&L (успешни): {short_success_avg_pnl:+.2f}%\n")
                    f.write(f"  Брой сигнали: {analysis['short_signals']['total']}\n\n")
                
                # Статистика по приоритет
                f.write("СТАТИСТИКА ПО ПРИОРИТЕТ:\n")
                for priority, stats in analysis['priority_stats'].items():
                    f.write(f"  {priority}: {stats['accuracy']:.1f}% ({stats['success']}/{stats['total']})\n")
                f.write("\n")
                
                # P&L статистика
                f.write("P&L СТАТИСТИКА:\n")
                f.write(f"  Среден P&L: {analysis['avg_profit_loss_pct']:+.2f}%\n")
                f.write(f"  Среден P&L (успешни): {analysis['avg_profit_loss_success_pct']:+.2f}%\n")
                f.write(f"  Среден P&L (неуспешни): {analysis['avg_profit_loss_failure_pct']:+.2f}%\n\n")
                
                # Най-добри сигнали
                f.write("НАЙ-ДОБРИ СИГНАЛИ:\n")
                f.write("-" * 80 + "\n")
                for i, signal_data in enumerate(analysis['best_signals'], 1):
                    signal = signal_data['signal']
                    result = signal_data['result']
                    f.write(f"{i}. {signal_data['date'].strftime('%Y-%m-%d')} | {signal['signal']} | ${signal['fibonacci_analysis']['current_price']:,.2f} | {result['profit_loss_pct']:+.2f}%\n")
                f.write("\n")
                
                # Най-лоши сигнали
                f.write("НАЙ-ЛОШИ СИГНАЛИ:\n")
                f.write("-" * 80 + "\n")
                for i, signal_data in enumerate(analysis['worst_signals'], 1):
                    signal = signal_data['signal']
                    result = signal_data['result']
                    f.write(f"{i}. {signal_data['date'].strftime('%Y-%m-%d')} | {signal['signal']} | ${signal['fibonacci_analysis']['current_price']:,.2f} | {result['profit_loss_pct']:+.2f}%\n")
                f.write("\n")
                
                # Детайлни резултати
                f.write("ДЕТАЙЛНИ РЕЗУЛТАТИ:\n")
                f.write("=" * 80 + "\n")
                for signal_data in results['signals']:
                    signal = signal_data['signal']
                    result = signal_data['result']
                    
                    f.write(f"Дата: {signal_data['date'].strftime('%Y-%m-%d')}\n")
                    f.write(f"Сигнал: {signal['signal']} (увереност: {signal['confidence']:.2f})\n")
                    f.write(f"Приоритет: {signal['priority']}\n")
                    f.write(f"Цена: ${signal['fibonacci_analysis']['current_price']:,.2f}\n")
                    f.write(f"Резултат: {'УСПЕХ' if result['success'] else 'НЕУСПЕХ'} ({result['profit_loss_pct']:+.2f}%)\n")
                    f.write(f"Валидация: {result['validation_date'].strftime('%Y-%m-%d')} (${result['validation_price']:,.2f})\n")
                    if result['failure_reason']:
                        f.write(f"Причина за неуспех: {result['failure_reason']}\n")
                    f.write("-" * 40 + "\n\n")
                
                f.write(f"Генерирано на: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Backtest резултати експортирани в {output_file}")
            
        except Exception as e:
            logger.error(f"Грешка при експортиране на backtest резултатите: {e}")

def main():
    """Главна функция за backtesting"""
    try:
        print("🚀 Стартиране на Backtesting за последните 18 месеца...")
        
        # Създаваме backtester-а
        backtester = Backtester()
        
        # Изпълняваме backtest
        results = backtester.run_backtest(18)
        
        if 'error' in results:
            print(f"❌ Грешка: {results['error']}")
            return
        
        # Показваме резултатите
        analysis = results['analysis']
        print(f"\n📊 BACKTEST РЕЗУЛТАТИ (18 месеца):")
        print(f"   Общо сигнали: {analysis['total_signals']}")
        print(f"   Успешни сигнали: {analysis['successful_signals']}")
        print(f"   Обща точност: {analysis['overall_accuracy']:.1f}%")
        print(f"   LONG сигнали: {analysis['long_signals']['accuracy']:.1f}%")
        print(f"   SHORT сигнали: {analysis['short_signals']['accuracy']:.1f}%")
        print(f"   Среден P&L: {analysis['avg_profit_loss_pct']:+.2f}%")
        
        # Експортираме резултатите
        backtester.export_backtest_results(results, 'data/backtest_results.txt')
        
        print(f"\n✅ Backtest завършен успешно!")
        print(f"📁 Резултатите са записани в data/backtest_results.txt")
        
    except Exception as e:
        logger.error(f"Критична грешка: {e}")
        print(f"❌ Критична грешка: {e}")

if __name__ == "__main__":
    main()
