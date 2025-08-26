"""
Signal Validator Module - Проверява точността на сигналите след 2 седмици
Записва всички сигнали и резултати в CSV файл за анализ
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalValidator:
    """Клас за валидация на trading сигнали"""
    
    def __init__(self, results_file: str = 'results.csv'):
        """
        Инициализира валидатора на сигнали
        
        Args:
            results_file: Файл за записване на резултатите
        """
        self.results_file = results_file
        self.results_df = self._load_or_create_results()
        
        logger.info(f"Signal Validator инициализиран. Резултати: {results_file}")
    
    def _load_or_create_results(self) -> pd.DataFrame:
        """
        Зарежда съществуващи резултати или създава нов файл
        
        Returns:
            DataFrame с резултатите
        """
        try:
            if os.path.exists(self.results_file):
                df = pd.read_csv(self.results_file)
                df['signal_date'] = pd.to_datetime(df['signal_date'])
                df['validation_date'] = pd.to_datetime(df['validation_date'])
                logger.info(f"Заредени {len(df)} съществуващи резултата")
                return df
            else:
                # Създаваме нов DataFrame
                columns = [
                    'signal_date', 'signal_type', 'signal_price', 'confidence', 'priority',
                    'fibonacci_level', 'weekly_tail_strength', 'reason', 'risk_level',
                    'validation_date', 'validation_price', 'profit_loss', 'profit_loss_pct',
                    'success', 'failure_reason', 'days_to_target', 'target_reached'
                ]
                df = pd.DataFrame(columns=columns)
                logger.info("Създаден нов файл за резултати")
                return df
                
        except Exception as e:
            logger.error(f"Грешка при зареждане на резултати: {e}")
            # Създаваме празен DataFrame
            columns = [
                'signal_date', 'signal_type', 'signal_price', 'confidence', 'priority',
                'fibonacci_level', 'weekly_tail_strength', 'reason', 'risk_level',
                'validation_date', 'validation_price', 'profit_loss', 'profit_loss_pct',
                'success', 'failure_reason', 'days_to_target', 'target_reached'
            ]
            return pd.DataFrame(columns=columns)
    
    def save_signal(self, signal_data: Dict) -> bool:
        """
        Записва нов сигнал в резултатите
        
        Args:
            signal_data: Данни за сигнала
            
        Returns:
            True ако е записан успешно
        """
        try:
            # Извличаме данните от сигнала
            signal_date = signal_data.get('analysis_date', pd.Timestamp.now())
            signal_type = signal_data.get('signal', 'HOLD')
            signal_price = signal_data.get('fibonacci_analysis', {}).get('current_price', 0)
            confidence = signal_data.get('confidence', 0.0)
            priority = signal_data.get('priority', 'UNKNOWN')
            
            # Fibonacci информация
            fib_level = 'N/A'
            if signal_data.get('fibonacci_analysis') and 'fibonacci_signal' in signal_data['fibonacci_analysis']:
                fib_signal = signal_data['fibonacci_analysis']['fibonacci_signal']
                if fib_signal.get('signal') != 'HOLD':
                    fib_level = f"Fib {fib_signal.get('strength', 0):.1f}"
            
            # Weekly Tails информация
            tail_strength = 'N/A'
            if signal_data.get('weekly_tails_analysis') and 'tails_signal' in signal_data['weekly_tails_analysis']:
                tails_signal = signal_data['weekly_tails_analysis']['tails_signal']
                if tails_signal.get('signal') != 'HOLD':
                    tail_strength = f"{tails_signal.get('strength', 0):.1f}"
            
            reason = signal_data.get('reason', 'Няма причина')
            risk_level = signal_data.get('risk_level', 'UNKNOWN')
            
            # Създаваме нов ред
            new_row = {
                'signal_date': signal_date,
                'signal_type': signal_type,
                'signal_price': signal_price,
                'confidence': confidence,
                'priority': priority,
                'fibonacci_level': fib_level,
                'weekly_tail_strength': tail_strength,
                'reason': reason,
                'risk_level': risk_level,
                'validation_date': pd.NaT,
                'validation_price': np.nan,
                'profit_loss': np.nan,
                'profit_loss_pct': np.nan,
                'success': np.nan,
                'failure_reason': '',
                'days_to_target': np.nan,
                'target_reached': False
            }
            
            # Добавяме в DataFrame
            self.results_df = pd.concat([self.results_df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Записваме в файл
            self._save_results()
            
            logger.info(f"Сигнал записан: {signal_type} на {signal_date.strftime('%Y-%m-%d')} при ${signal_price:,.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Грешка при записване на сигнал: {e}")
            return False
    
    def check_signal_result(self, signal_date: pd.Timestamp, current_price: float, 
                           target_price: Optional[float] = None) -> Dict[str, any]:
        """
        Проверява резултата на сигнал след 2 седмици
        
        Args:
            signal_date: Дата на сигнала
            current_price: Текуща цена за валидация
            target_price: Целева цена (ако е зададена)
            
        Returns:
            Dict с резултата от валидацията
        """
        try:
            # Намираме сигнала в резултатите
            signal_mask = self.results_df['signal_date'] == signal_date
            if not signal_mask.any():
                return {'error': f'Сигнал за {signal_date.strftime("%Y-%m-%d")} не е намерен'}
            
            signal_idx = signal_mask.idxmax()
            signal_row = self.results_df.loc[signal_idx]
            
            # Проверяваме дали вече е валидиран
            if pd.notna(signal_row['validation_date']):
                return {'error': f'Сигналът вече е валидиран на {signal_row["validation_date"].strftime("%Y-%m-%d")}'}
            
            # Изчисляваме резултата
            signal_price = signal_row['signal_price']
            signal_type = signal_row['signal_type']
            
            if signal_type == 'HOLD':
                return {'error': 'HOLD сигналите не се валидират'}
            
            # Изчисляваме P&L
            if signal_type == 'LONG':
                profit_loss = current_price - signal_price
                profit_loss_pct = (profit_loss / signal_price) * 100
            elif signal_type == 'SHORT':
                profit_loss = signal_price - current_price
                profit_loss_pct = (profit_loss / signal_price) * 100
            else:
                return {'error': f'Неизвестен тип сигнал: {signal_type}'}
            
            # Определяме успеха
            success = profit_loss > 0
            
            # Проверяваме дали е достигната целевата цена
            target_reached = False
            if target_price:
                if signal_type == 'LONG':
                    target_reached = current_price >= target_price
                elif signal_type == 'SHORT':
                    target_reached = current_price <= target_price
            
            # Изчисляваме дни до валидацията
            days_to_target = (pd.Timestamp.now() - signal_date).days
            
            # Определяме причината за неуспех (ако има такъв)
            failure_reason = ''
            if not success:
                if signal_type == 'LONG':
                    failure_reason = f"Цената падна от ${signal_price:,.2f} до ${current_price:,.2f}"
                elif signal_type == 'SHORT':
                    failure_reason = f"Цената се повиши от ${signal_price:,.2f} до ${current_price:,.2f}"
            
            # Обновяваме резултата
            self.results_df.loc[signal_idx, 'validation_date'] = pd.Timestamp.now()
            self.results_df.loc[signal_idx, 'validation_price'] = current_price
            self.results_df.loc[signal_idx, 'profit_loss'] = profit_loss
            self.results_df.loc[signal_idx, 'profit_loss_pct'] = profit_loss_pct
            self.results_df.loc[signal_idx, 'success'] = success
            self.results_df.loc[signal_idx, 'failure_reason'] = failure_reason
            self.results_df.loc[signal_idx, 'days_to_target'] = days_to_target
            self.results_df.loc[signal_idx, 'target_reached'] = target_reached
            
            # Записваме обновените резултати
            self._save_results()
            
            validation_result = {
                'signal_date': signal_date,
                'signal_type': signal_type,
                'signal_price': signal_price,
                'current_price': current_price,
                'profit_loss': profit_loss,
                'profit_loss_pct': profit_loss_pct,
                'success': success,
                'failure_reason': failure_reason,
                'days_to_target': days_to_target,
                'target_reached': target_reached
            }
            
            logger.info(f"Сигнал валидиран: {signal_type} на {signal_date.strftime('%Y-%m-%d')}")
            logger.info(f"Резултат: {'УСПЕХ' if success else 'НЕУСПЕХ'} ({profit_loss_pct:+.2f}%)")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Грешка при валидация на сигнал: {e}")
            return {'error': f'Грешка: {e}'}
    
    def get_accuracy_stats(self, lookback_days: int = 30) -> Dict[str, any]:
        """
        Връща статистика за точността на сигналите
        
        Args:
            lookback_days: Брой дни за lookback
            
        Returns:
            Dict с статистика за точността
        """
        try:
            # Филтрираме по период
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=lookback_days)
            recent_signals = self.results_df[
                (self.results_df['signal_date'] >= cutoff_date) & 
                (pd.notna(self.results_df['validation_date']))
            ].copy()
            
            if recent_signals.empty:
                return {'error': f'Няма валидирани сигнали за последните {lookback_days} дни'}
            
            # Обща статистика
            total_signals = len(recent_signals)
            successful_signals = len(recent_signals[recent_signals['success'] == True])
            accuracy = (successful_signals / total_signals) * 100 if total_signals > 0 else 0
            
            # Статистика по тип сигнал
            long_signals = recent_signals[recent_signals['signal_type'] == 'LONG']
            short_signals = recent_signals[recent_signals['signal_type'] == 'SHORT']
            
            long_accuracy = 0
            if len(long_signals) > 0:
                long_success = len(long_signals[long_signals['success'] == True])
                long_accuracy = (long_success / len(long_signals)) * 100
            
            short_accuracy = 0
            if len(short_signals) > 0:
                short_success = len(short_signals[short_signals['success'] == True])
                short_accuracy = (short_success / len(short_signals)) * 100
            
            # Статистика по приоритет
            priority_stats = {}
            for priority in recent_signals['priority'].unique():
                if pd.notna(priority):
                    priority_signals = recent_signals[recent_signals['priority'] == priority]
                    priority_success = len(priority_signals[priority_signals['success'] == True])
                    priority_accuracy = (priority_success / len(priority_signals)) * 100 if len(priority_signals) > 0 else 0
                    priority_stats[priority] = {
                        'total': len(priority_signals),
                        'success': priority_success,
                        'accuracy': priority_accuracy
                    }
            
            # Среден P&L
            avg_profit_loss = recent_signals['profit_loss_pct'].mean()
            avg_profit_loss_success = recent_signals[recent_signals['success'] == True]['profit_loss_pct'].mean()
            avg_profit_loss_failure = recent_signals[recent_signals['success'] == False]['profit_loss_pct'].mean()
            
            stats = {
                'period_days': lookback_days,
                'total_signals': total_signals,
                'successful_signals': successful_signals,
                'overall_accuracy': accuracy,
                'long_signals': {
                    'total': len(long_signals),
                    'success': len(long_signals[long_signals['success'] == True]) if len(long_signals) > 0 else 0,
                    'accuracy': long_accuracy
                },
                'short_signals': {
                    'total': len(short_signals),
                    'success': len(short_signals[short_signals['success'] == True]) if len(short_signals) > 0 else 0,
                    'accuracy': short_accuracy
                },
                'priority_stats': priority_stats,
                'avg_profit_loss_pct': avg_profit_loss,
                'avg_profit_loss_success_pct': avg_profit_loss_success,
                'avg_profit_loss_failure_pct': avg_profit_loss_failure,
                'analysis_date': pd.Timestamp.now()
            }
            
            logger.info(f"Статистика за точността: {accuracy:.1f}% ({successful_signals}/{total_signals})")
            return stats
            
        except Exception as e:
            logger.error(f"Грешка при изчисляване на статистиката: {e}")
            return {'error': f'Грешка: {e}'}
    
    def get_recent_signals(self, count: int = 20) -> pd.DataFrame:
        """
        Връща последните N сигнала
        
        Args:
            count: Брой сигнала за връщане
            
        Returns:
            DataFrame с последните сигнали
        """
        try:
            # Сортираме по дата на сигнала (намаляващо)
            sorted_results = self.results_df.sort_values('signal_date', ascending=False)
            
            # Връщаме последните N
            recent_signals = sorted_results.head(count)
            
            logger.info(f"Върнати последните {len(recent_signals)} сигнала")
            return recent_signals
            
        except Exception as e:
            logger.error(f"Грешка при извличане на последните сигнали: {e}")
            return pd.DataFrame()
    
    def _save_results(self) -> bool:
        """
        Записва резултатите в CSV файл
        
        Returns:
            True ако е записан успешно
        """
        try:
            self.results_df.to_csv(self.results_file, index=False)
            logger.info(f"Резултати записани в {self.results_file}")
            return True
        except Exception as e:
            logger.error(f"Грешка при записване на резултати: {e}")
            return False
    
    def export_results_summary(self, output_file: str = 'results_summary.txt') -> bool:
        """
        Експортира обобщение на резултатите в текстов файл
        
        Args:
            output_file: Име на изходния файл
            
        Returns:
            True ако е експортиран успешно
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("BNB Trading System - Обобщение на резултатите\n")
                f.write("=" * 50 + "\n\n")
                
                # Обща статистика
                total_signals = len(self.results_df)
                validated_signals = len(self.results_df[pd.notna(self.results_df['validation_date'])])
                
                f.write(f"Общо сигнали: {total_signals}\n")
                f.write(f"Валидирани сигнали: {validated_signals}\n")
                f.write(f"Очакващи валидация: {total_signals - validated_signals}\n\n")
                
                if validated_signals > 0:
                    # Статистика за валидираните сигнали
                    recent_stats = self.get_accuracy_stats(30)
                    if 'error' not in recent_stats:
                        f.write("Статистика за последните 30 дни:\n")
                        f.write(f"  Обща точност: {recent_stats['overall_accuracy']:.1f}%\n")
                        f.write(f"  LONG сигнали: {recent_stats['long_signals']['accuracy']:.1f}%\n")
                        f.write(f"  SHORT сигнали: {recent_stats['short_signals']['accuracy']:.1f}%\n")
                        f.write(f"  Среден P&L: {recent_stats['avg_profit_loss_pct']:+.2f}%\n\n")
                    
                    # Последните сигнали
                    recent_signals = self.get_recent_signals(10)
                    if not recent_signals.empty:
                        f.write("Последните 10 сигнала:\n")
                        f.write("-" * 80 + "\n")
                        for _, row in recent_signals.iterrows():
                            signal_info = f"{row['signal_date'].strftime('%Y-%m-%d')} | {row['signal_type']} | ${row['signal_price']:,.2f}"
                            if pd.notna(row['validation_date']):
                                result = "✓" if row['success'] else "✗"
                                pnl = f"{row['profit_loss_pct']:+.2f}%"
                                signal_info += f" | {result} | {pnl}"
                            else:
                                signal_info += " | Очаква валидация"
                            f.write(f"{signal_info}\n")
                
                f.write(f"\nГенерирано на: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Обобщение експортирано в {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Грешка при експортиране на обобщение: {e}")
            return False

if __name__ == "__main__":
    # Тест на Signal Validator модула
    validator = SignalValidator('test_results.csv')
    
    # Създаваме тестови сигнал
    test_signal = {
        'signal': 'LONG',
        'confidence': 0.8,
        'reason': 'Тестов сигнал',
        'analysis_date': pd.Timestamp.now(),
        'fibonacci_analysis': {
            'current_price': 600.0,
            'fibonacci_signal': {'signal': 'LONG', 'strength': 0.8}
        },
        'weekly_tails_analysis': {
            'tails_signal': {'signal': 'LONG', 'strength': 0.7}
        },
        'priority': 'HIGH',
        'risk_level': 'MEDIUM'
    }
    
    # Записваме сигнала
    success = validator.save_signal(test_signal)
    print(f"Сигнал записан: {success}")
    
    # Проверяваме резултата след 2 седмици (симулираме)
    validation_date = test_signal['analysis_date'] + pd.Timedelta(days=14)
    current_price = 650.0  # Симулираме успешен LONG
    
    result = validator.check_signal_result(
        test_signal['analysis_date'], 
        current_price, 
        target_price=650.0
    )
    
    if 'error' not in result:
        print(f"Валидация: {result['signal_type']} на {result['signal_date'].strftime('%Y-%m-%d')}")
        print(f"Резултат: {'УСПЕХ' if result['success'] else 'НЕУСПЕХ'} ({result['profit_loss_pct']:+.2f}%)")
    
    # Статистика
    stats = validator.get_accuracy_stats(30)
    if 'error' not in stats:
        print(f"\nСтатистика: {stats['overall_accuracy']:.1f}% точност")
    
    # Експортираме обобщение
    validator.export_results_summary('test_summary.txt')
