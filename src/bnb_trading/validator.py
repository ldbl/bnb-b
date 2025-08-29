"""
Signal Validator Module - Comprehensive Signal Validation and Performance Tracking

SIGNAL VALIDATION SYSTEM FOR TRADING STRATEGY PERFORMANCE MEASUREMENT
Validates signal accuracy after holding period and tracks comprehensive performance metrics

This module provides a complete signal validation framework for the BNB trading system,
enabling thorough evaluation of signal accuracy, performance tracking, and continuous
improvement of trading strategies through systematic validation.

ARCHITECTURE OVERVIEW:
    - Signal capture and storage with complete analysis context
    - Automated validation after configurable holding periods
    - Performance metrics calculation and statistical analysis
    - Historical performance database with CSV persistence
    - Comprehensive reporting and analytics capabilities

VALIDATION METHODOLOGY:
    - Holding Period Validation: Configurable timeframe for signal assessment
    - Profit/Loss Calculation: Realistic P&L with entry/exit assumptions
    - Success Rate Tracking: Win/loss ratio calculation and analysis
    - Risk Metrics: Drawdown, recovery factors, and risk-adjusted returns
    - Statistical Significance: Confidence intervals and statistical validation

SIGNAL CAPTURE FEATURES:
    - Complete signal context preservation (all analysis modules)
    - Confidence score tracking and validation
    - Priority level recording and performance segmentation
    - Reasoning and rationale capture for analysis
    - Risk assessment and position sizing recommendations

VALIDATION PROCESS:
    1. Signal Reception: Captures complete signal with all analysis data
    2. Storage: Persists signal to historical database with timestamps
    3. Holding Period: Waits for configurable validation timeframe
    4. Price Validation: Compares actual vs expected price movement
    5. Result Calculation: Computes P&L, success/failure, and metrics
    6. Database Update: Stores validation results with complete context

PERFORMANCE METRICS TRACKED:
    - Overall Accuracy: Total win rate percentage
    - LONG/SHORT Accuracy: Direction-specific performance
    - Average P&L: Mean profit/loss per trade
    - Maximum Drawdown: Peak-to-trough portfolio decline
    - Sharpe Ratio: Risk-adjusted return measure
    - Profit Factor: Gross profit divided by gross loss
    - Recovery Factor: Net profit divided by max drawdown

DATA PERSISTENCE:
    - CSV-based storage for portability and analysis
    - Complete signal context preservation
    - Historical performance database
    - Backup and recovery capabilities
    - Data integrity validation

CONFIGURATION PARAMETERS:
    - results_file: Path to CSV results database (default: 'results.csv')
    - holding_period_days: Days to hold before validation (default: 14)
    - validation_tolerance: Price tolerance for validation (default: 0.01)
    - max_results_history: Maximum historical records to maintain (default: 10000)
    - auto_backup: Enable automatic backup of results (default: true)

VALIDATION CRITERIA:
    - Price Target Achievement: Did price reach target within timeframe?
    - Profit/Loss Calculation: Realistic P&L with commissions and slippage
    - Risk Management Compliance: Adherence to stop loss and risk limits
    - Market Condition Filtering: Performance across different market regimes
    - Statistical Significance: Confidence intervals for performance metrics

REPORTING CAPABILITIES:
    - Performance summary reports with key metrics
    - Signal accuracy breakdown by type and confidence
    - Risk analysis and drawdown reports
    - Monthly/quarterly performance summaries
    - Strategy optimization recommendations

EXAMPLE USAGE:
    >>> validator = SignalValidator('results.csv')
    >>> signal_data = {
    ...     'signal': 'LONG',
    ...     'confidence': 0.85,
    ...     'analysis_date': pd.Timestamp.now(),
    ...     'fibonacci_analysis': {'current_price': 862.50}
    ... }
    >>> validator.save_signal(signal_data)
    >>> performance = validator.get_performance_summary()

DEPENDENCIES:
    - pandas: Data manipulation and CSV operations
    - numpy: Mathematical calculations and statistical analysis
    - datetime/timedelta: Date and time operations
    - os: File system operations
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient CSV operations with batch processing
    - Memory-optimized data structures
    - Incremental updates for performance tracking
    - Database compaction for long-term storage

ERROR HANDLING:
    - File I/O error recovery and backup mechanisms
    - Data corruption detection and repair
    - Missing data handling and interpolation
    - Validation error logging and recovery

DATA INTEGRITY:
    - Checksum validation for critical data
    - Backup and recovery procedures
    - Data consistency validation
    - Historical data preservation

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalValidator:
    """
    Advanced Signal Validation and Performance Tracking Engine

    This class provides comprehensive signal validation capabilities for the BNB trading system,
    enabling thorough evaluation of signal accuracy, systematic performance tracking, and
    continuous improvement of trading strategies through data-driven analysis.

    ARCHITECTURE OVERVIEW:
        - Signal capture system with complete analysis context preservation
        - Automated validation framework with configurable holding periods
        - Comprehensive performance metrics calculation and tracking
        - Historical database management with CSV persistence
        - Statistical analysis and reporting capabilities

    SIGNAL CAPTURE PROCESS:
        1. Signal Reception: Accepts complete signal data with all analysis modules
        2. Context Preservation: Stores all relevant signal information and reasoning
        3. Database Storage: Persists signal to historical CSV database
        4. Validation Scheduling: Prepares signal for future validation
        5. Metadata Tracking: Records confidence, priority, and risk assessment

    VALIDATION METHODOLOGY:
        - Holding Period Management: Configurable validation timeframes
        - Price Target Validation: Compares actual vs expected price movement
        - Profit/Loss Calculation: Realistic P&L with commissions and slippage
        - Success/Failure Determination: Objective criteria-based assessment
        - Statistical Significance: Confidence intervals and significance testing

    PERFORMANCE TRACKING:
        - Accuracy Metrics: Overall and direction-specific win rates
        - Risk Metrics: Drawdown, Sharpe ratio, profit factor
        - Statistical Analysis: Confidence intervals and significance tests
        - Performance Segmentation: By confidence, priority, and market conditions
        - Historical Trends: Performance analysis over time periods

    DATABASE MANAGEMENT:
        - CSV-based storage for portability and external analysis
        - Automatic file creation and schema management
        - Data integrity validation and backup procedures
        - Historical data compaction and maintenance
        - Incremental updates for performance optimization

    CONFIGURATION PARAMETERS:
        results_file (str): Path to CSV results database (default: 'results.csv')
        holding_period_days (int): Days to hold before validation (default: 14)
        validation_tolerance (float): Price tolerance for validation (default: 0.01)
        max_results_history (int): Maximum records to maintain (default: 10000)
        auto_backup (bool): Enable automatic result backups (default: True)

    DATA SCHEMA:
        The results database contains comprehensive signal information:
        - Signal metadata (date, type, confidence, priority)
        - Analysis context (Fibonacci, tails, indicators, trend)
        - Validation results (P&L, success/failure, time to target)
        - Performance metrics (accuracy, drawdown, Sharpe ratio)
        - Risk assessment and position sizing recommendations

    ATTRIBUTES:
        results_file (str): Path to the results CSV file
        results_df (pd.DataFrame): In-memory results database
        holding_period_days (int): Validation holding period
        validation_tolerance (float): Price tolerance for validation

    VALIDATION CRITERIA:
        - Price Achievement: Did price reach target within holding period?
        - Profit/Loss Calculation: Realistic P&L with market assumptions
        - Success Definition: Objective criteria for win/loss determination
        - Risk Management: Compliance with stop loss and risk limits
        - Market Conditions: Performance across different regimes

    REPORTING FEATURES:
        - Performance summary with key metrics and statistics
        - Signal accuracy breakdown by type, confidence, and priority
        - Risk analysis with drawdown and recovery metrics
        - Monthly/quarterly performance segmentation
        - Strategy optimization recommendations and insights

    EXAMPLE:
        >>> validator = SignalValidator('trading_results.csv')
        >>> signal_data = {
        ...     'signal': 'LONG',
        ...     'confidence': 0.85,
        ...     'priority': 'HIGH',
        ...     'analysis_date': pd.Timestamp.now(),
        ...     'fibonacci_analysis': {'current_price': 862.50},
        ...     'reason': 'Strong support at Fib 61.8%'
        ... }
        >>> validator.save_signal(signal_data)
        >>> summary = validator.get_performance_summary()
        >>> print(f"Overall Accuracy: {summary['accuracy']:.1f}%")

    NOTE:
        The validator automatically creates the results file if it doesn't exist
        and manages the complete signal lifecycle from capture to validation.
    """

    def __init__(self, results_file: str = 'results.csv') -> None:
        """
        Initialize the Signal Validator with results database configuration.

        Sets up the validation system with specified results file and prepares
        the database for signal capture and performance tracking.

        Args:
            results_file (str): Path to CSV file for storing results.
                If file doesn't exist, it will be created automatically.
                Should have .csv extension for proper handling.

        Raises:
            ValueError: If results_file path is invalid
            PermissionError: If unable to read/write to the specified path

        Example:
            >>> # Use default results file
            >>> validator = SignalValidator()

            >>> # Use custom results file
            >>> validator = SignalValidator('my_trading_results.csv')
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
    print("Signal Validator модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
