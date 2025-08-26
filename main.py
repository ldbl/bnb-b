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
    level=logging.ERROR,  # Променяме на ERROR за да видим само грешките
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bnb_trading.log'),
        logging.StreamHandler()  # Добавяме StreamHandler за да видим в конзолата
    ]
)

# Задаваме ERROR level за всички модули (само грешки)
for logger_name in ['__main__', 'data_fetcher', 'fibonacci', 'weekly_tails', 'indicators', 'signal_generator', 'validator', 'trend_analyzer', 'elliott_wave_analyzer', 'divergence_detector', 'moving_averages', 'price_action_patterns', 'optimal_levels', 'whale_tracker', 'ichimoku_module', 'sentiment_module']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

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

            
            # Инициализираме компонентите
            self.data_fetcher = BNBDataFetcher(self.config['data']['symbol'])
            self.signal_generator = SignalGenerator(self.config)
            self.validator = SignalValidator('data/results.csv')
            
    
            
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
    
            
            # 1. Извличаме данни
    
            data = self.data_fetcher.fetch_bnb_data(self.config['data']['lookback_days'])
            
            if not data or 'daily' not in data or 'weekly' not in data:
                raise ValueError("Неуспешно извличане на данни")
            
            daily_df = data['daily']
            weekly_df = data['weekly']
            
    
            
            # 2. Валидираме качеството на данните
            daily_quality = self.data_fetcher.validate_data_quality(daily_df)
            weekly_quality = self.data_fetcher.validate_data_quality(weekly_df)
            
            
            
            # 3. Генерираме сигнал
    
            signal = self.signal_generator.generate_signal(daily_df, weekly_df)
            
            if 'error' in signal:
                raise ValueError(f"Грешка при генериране на сигнал: {signal['error']}")
            
            # 4. Записваме сигнала
    
            self.validator.save_signal(signal)
            
            # 5. Подготвяме резултатите за показване
            results = self._prepare_results_for_display(signal, daily_df, weekly_df)
            
            # Добавяме пълния сигнал към резултатите
            results['full_signal'] = signal
            
            # Debug информация за новите анализи
            
            
            # Добавяме новите анализи от ideas файла
            if 'divergence_analysis' in signal:
                results['divergence_analysis'] = signal['divergence_analysis']
            if 'moving_averages_analysis' in signal:
                results['moving_averages_analysis'] = signal['moving_averages_analysis']
            if 'price_patterns_analysis' in signal:
                results['price_patterns_analysis'] = signal['price_patterns_analysis']
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
            print("🚀 BNB TRADING SYSTEM - ТЕКУЩ СИГНАЛ ЗА ДНЕС")
            print("="*80)
            
            # Текущ сигнал
            current_signal = results['current_signal']
            print(f"\n🎯 ТЕКУЩ СИГНАЛ ЗА ДНЕС:")
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
            
            # Divergence Analysis (НОВО от ideas файла)
            try:
                if 'divergence_analysis' in results and results['divergence_analysis']:
                    div_analysis = results['divergence_analysis']
                    if div_analysis and isinstance(div_analysis, dict) and 'error' not in div_analysis:
                        print(f"\n🔄 DIVERGENCE АНАЛИЗ:")
                        if div_analysis.get('rsi_divergence', {}).get('type') != 'NONE':
                            rsi_div = div_analysis['rsi_divergence']
                            print(f"   📊 RSI Divergence: {rsi_div['type']} (увереност: {rsi_div['confidence']:.1f}%)")
                            print(f"      Причина: {rsi_div['reason']}")

                        if div_analysis.get('macd_divergence', {}).get('type') != 'NONE':
                            macd_div = div_analysis['macd_divergence']
                            print(f"   📈 MACD Divergence: {macd_div['type']} (увереност: {macd_div['confidence']:.1f}%)")
                            print(f"      Причина: {macd_div['reason']}")

                        pv_div_data = div_analysis.get('price_volume_divergence')
                        if pv_div_data and isinstance(pv_div_data, dict) and pv_div_data.get('type') != 'NONE':
                            print(f"   📊 Price-Volume Divergence: {pv_div_data['type']} (увереност: {pv_div_data['confidence']:.1f}%)")
                            print(f"      Причина: {pv_div_data['reason']}")

                        overall_div = div_analysis.get('overall_divergence', 'NONE')
                        print(f"   🎯 Общ Divergence: {overall_div}")
            except Exception as e:
                logger.warning(f"Грешка при показване на Divergence анализ: {e}")
            
            # Moving Averages Analysis (НОВО от ideas файла)
            if 'moving_averages_analysis' in results and results['moving_averages_analysis']:
                ma_analysis = results['moving_averages_analysis']
                if ma_analysis and 'error' not in ma_analysis:
                    print(f"\n📊 MOVING AVERAGES АНАЛИЗ:")
                    crossover = ma_analysis.get('crossover_signal', {})
                    if crossover.get('signal') != 'NONE':
                        print(f"   🎯 Crossover: {crossover['signal']}")
                        print(f"      Причина: {crossover['reason']}")
                        print(f"      Увереност: {crossover['confidence']:.1f}%")
                        if 'crossover_strength' in crossover:
                            print(f"      Сила: {crossover['crossover_strength']:.2%}")
                    
                    fast_ema = ma_analysis.get('fast_ema_current')
                    slow_ema = ma_analysis.get('slow_ema_current')
                    if fast_ema and slow_ema:
                        print(f"   📈 EMA стойности:")
                        print(f"      Fast EMA (10): ${fast_ema:.2f}")
                        print(f"      Slow EMA (50): ${slow_ema:.2f}")
                        print(f"      Volume Confirmed: {'✅' if ma_analysis.get('volume_confirmed') else '❌'}")
            
            # Price Action Patterns Analysis (НОВО от ideas файла)
            if 'price_patterns_analysis' in results and results['price_patterns_analysis']:
                patterns = results['price_patterns_analysis']
                if 'error' not in patterns:
                    print(f"\n📐 PRICE ACTION PATTERNS:")
                    overall_pattern = patterns.get('overall_pattern', 'NONE')
                    print(f"   🎯 Общ Pattern: {overall_pattern}")
                    
                    if patterns.get('double_top', {}).get('detected'):
                        dt = patterns['double_top']
                        print(f"   🔴 Double Top: {dt['reason']}")
                        print(f"      Увереност: {dt['confidence']:.1f}% | Сила: {dt['pattern_strength']}")
                        print(f"      Пикове: ${dt['peak1_price']:.2f}, ${dt['peak2_price']:.2f}")
                    
                    if patterns.get('double_bottom', {}).get('detected'):
                        db = patterns['double_bottom']
                        print(f"   🟢 Double Bottom: {db['reason']}")
                        print(f"      Увереност: {db['confidence']:.1f}% | Сила: {db['pattern_strength']}")
                        print(f"      Дъна: ${db['trough1_price']:.2f}, ${db['trough2_price']:.2f}")
                    
                    if patterns.get('head_shoulders', {}).get('detected'):
                        hs = patterns['head_shoulders']
                        print(f"   🔴 Head & Shoulders: {hs['reason']}")
                        print(f"      Увереност: {hs['confidence']:.1f}%")
                        print(f"      Глава: ${hs['head_price']:.2f} | Рамене: ${hs['left_shoulder_price']:.2f}")
            
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
            
            analysis_date = results.get('analysis_date', pd.Timestamp.now())
            if analysis_date and hasattr(analysis_date, 'strftime'):
                date_str = analysis_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_str = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n⏰ Анализът е извършен на: {date_str}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Грешка при показване на резултатите: {e}")
            print(f"❌ Грешка при показване на резултатите: {e}")
    
    def display_current_signal_detailed(self, signal: Dict):
        """
        Показва детайлна информация за текущия сигнал за днес
        
        Args:
            signal: Генерираният сигнал
        """
        try:

            print("\n" + "🎯" * 20)
            print("🎯 ТЕКУЩ СИГНАЛ ЗА ДНЕС - КЛЮЧОВА ИНФОРМАЦИЯ 🎯")
            print("🎯" * 20)
            
            # Основна информация за сигнала
            print(f"\n🚀 СИГНАЛ: {signal['signal']} | Увереност: {signal.get('confidence', 0):.1f} | Приоритет: {signal['priority']}")
            print(f"💡 Причина: {signal['reason'][:100]}...")
            
            # Fibonacci анализ - само най-важното
            if 'fibonacci_analysis' in signal:
                fib_analysis = signal['fibonacci_analysis']
                current_price = fib_analysis.get('current_price', 0)
                
                # Показваме Fibonacci Extensions (цели нагоре)
                if 'fibonacci_extensions' in fib_analysis:
                    fib_extensions = fib_analysis['fibonacci_extensions']
                    if fib_extensions:
                        print(f"\n🚀 FIBONACCI EXTENSIONS (текуща цена: ${current_price:,.2f}):")
                        
                        # Сортираме extensions по разстояние от текущата цена (от най-близко до най-далечно)
                        extensions_with_distances = []
                        for level, price in fib_extensions.items():
                            distance = price - current_price
                            distance_pct = (distance / current_price) * 100
                            extensions_with_distances.append((level, price, distance, distance_pct))
                        
                        # Сортираме по разстояние (от най-близко до най-далечно)
                        extensions_with_distances.sort(key=lambda x: x[3])
                        
                        for level, price, distance, distance_pct in extensions_with_distances:
                            # Определяме типа на нивото
                            if level == 1.618:
                                level_name = f"{level*100:.1f}% (ЗЛАТНО)"
                            else:
                                level_name = f"{level*100:.1f}%"
                            
                            print(f"  {level_name:<15} ${price:8,.2f} (🔴 съпротива) +{distance_pct:5.2f}% нагоре")
                
                print(f"\n🔢 FIBONACCI RETRACEMENT (текуща цена: ${current_price:,.2f}):")
                
                if 'fibonacci_levels' in fib_analysis:
                    fib_levels = fib_analysis['fibonacci_levels']
                    
                    # Показваме само най-важните нива
                    key_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
                    
                    # Сортираме нивата по разстояние от текущата цена (от най-близко до най-далечно)
                    levels_with_distances = []
                    for level in key_levels:
                        if level in fib_levels:
                            price = fib_levels[level]
                            distance = current_price - price
                            distance_pct = (distance / current_price) * 100
                            levels_with_distances.append((level, price, distance, distance_pct))
                    
                    # Сортираме по абсолютна стойност на разстоянието (от най-близко до най-далечно)
                    levels_with_distances.sort(key=lambda x: abs(x[3]))
                    
                    for level, price, distance, distance_pct in levels_with_distances:
                        # Определяме типа на нивото
                        if level == 0.618:
                            level_name = "61.8% (ЗЛАТНО СЕЧЕНИЕ)"
                        elif level == 0.5:
                            level_name = "50.0% (ПОПУЛЯРНО)"
                        else:
                            level_name = f"{level*100:.1f}%"
                        
                        # Определяме дали е поддръжка или съпротива
                        # Ако текущата цена е НАД Fibonacci нивото, то е ПОДДРЪЖКА
                        # Ако текущата цена е ПОД Fibonacci нивото, то е СЪПРОТИВА
                        if distance > 0:
                            level_type = "🟢 поддръжка"
                            direction = "надолу"
                        else:
                            level_type = "🔴 съпротива"
                            direction = "нагоре"
                        
                        print(f"   {level_name:<20} ${price:8,.2f} ({level_type}) - {abs(distance_pct):5.2f}% {direction}")
            
            # Technical Indicators - само стойностите
            if 'indicators_signals' in signal:
                indicators = signal['indicators_signals']
                print(f"\n📊 ТЕХНИЧЕСКИ ИНДИКАТОРИ:")
                
                # RSI
                if 'rsi' in indicators:
                    rsi_value = indicators['rsi'].get('rsi_value', 0)
                    rsi_status = "🟢 oversold" if rsi_value < 30 else "🔴 overbought" if rsi_value > 70 else "🟡 неутрален"
                    print(f"   RSI: {rsi_value:5.1f} ({rsi_status})")
                
                # MACD
                if 'macd' in indicators:
                    macd_value = indicators['macd'].get('macd_value', 0)
                    macd_status = "🟢 bullish" if macd_value > 0 else "🔴 bearish"
                    print(f"   MACD: {macd_value:+8.3f} ({macd_status})")
                
                # Bollinger Bands
                if 'bollinger' in indicators:
                    bb_position = indicators['bollinger'].get('position', 0)
                    if bb_position < -0.8:
                        bb_status = "🟢 долна лента (oversold)"
                    elif bb_position > 0.8:
                        bb_status = "🔴 горна лента (overbought)"
                    else:
                        bb_status = "🟡 централна лента"
                    print(f"   Bollinger: {bb_position:+6.2f} ({bb_status})")
            
            # Weekly Tails - само основната информация
            if 'weekly_tails_analysis' in signal:
                tails_analysis = signal['weekly_tails_analysis']
                if 'tails_signal' in tails_analysis:
                    tails_signal = tails_analysis['tails_signal']
                    print(f"\n📈 WEEKLY TAILS: {tails_signal['signal']} (сила: {tails_signal.get('strength', 0):.2f})")
            
            # Fibonacci + Tails съвпадения - само топ 3
            if 'confluence_info' in signal:
                confluence = signal['confluence_info']
                if confluence.get('confluence_points'):
                    print(f"\n🎯 FIBONACCI + TAILS СЪВПАДЕНИЯ:")
                    for i, point in enumerate(confluence['confluence_points'][:3], 1):
                        print(f"   {i}. Fib {point['fib_level']*100:.1f}% + {point['tail_signal']} (сила: {point['confluence_score']:.2f})")
            
            # Optimal Levels анализ - ново!
            if 'optimal_levels_analysis' in signal:
                opt_analysis = signal['optimal_levels_analysis']
                if 'error' not in opt_analysis:
                    print(f"\n🎯 ОПТИМАЛНИ TRADING НИВА (базирани на исторически докосвания):")
                    
                    # Top Support нива
                    if 'optimal_levels' in opt_analysis and opt_analysis['optimal_levels'].get('top_support_levels'):
                        support_levels = opt_analysis['optimal_levels']['top_support_levels']
                        print(f"   🟢 TOP SUPPORT НИВА:")
                        for i, (price, touches) in enumerate(support_levels[:3], 1):
                            print(f"      {i}. ${price:6.0f} ({touches:2d} докосвания)")
                    
                    # Top Resistance нива
                    if 'optimal_levels' in opt_analysis and opt_analysis['optimal_levels'].get('top_resistance_levels'):
                        resistance_levels = opt_analysis['optimal_levels']['top_resistance_levels']
                        print(f"   🔴 TOP RESISTANCE НИВА:")
                        for i, (price, touches) in enumerate(resistance_levels[:3], 1):
                            print(f"      {i}. ${price:6.0f} ({touches:2d} докосвания)")
                    
                    # Trading препоръки
                    if 'optimal_levels' in opt_analysis:
                        try:
                            from optimal_levels import OptimalLevelsAnalyzer
                            analyzer = OptimalLevelsAnalyzer({})
                            recommendations = analyzer.get_trading_recommendations(opt_analysis['optimal_levels'])
                            if 'error' not in recommendations and 'long_strategy' in recommendations:
                                long_strat = recommendations['long_strategy']
                                print(f"   📈 LONG СТРАТЕГИЯ:")
                                print(f"      Entry: ${long_strat.get('entry_price', 0):6.0f} ({long_strat.get('entry_type', 'individual')})")
                                print(f"      Target: ${long_strat.get('target', 0):6.0f}")
                                print(f"      Risk/Reward: 1:{long_strat.get('risk_reward', 0):.1f}")
                        except:
                            pass
            
            # Elliott Wave Analysis - ново!
            if 'elliott_wave_analysis' in signal:
                elliott_analysis = signal['elliott_wave_analysis']
                if 'error' not in elliott_analysis:
                    print(f"\n🌊 ELLIOTT WAVE АНАЛИЗ (структурен анализ):")
                    
                    # Основен анализ
                    if 'combined_analysis' in elliott_analysis:
                        combined = elliott_analysis['combined_analysis']
                        print(f"   🎯 ОСНОВЕН АНАЛИЗ: {combined.get('primary_wave', 'UNKNOWN')}")
                        print(f"      Тренд: {combined.get('primary_trend', 'UNKNOWN')}")
                        print(f"      Увереност: {combined.get('confidence', 0)}%")
                        print(f"      Степен: {combined.get('degree', 'UNKNOWN')}")
                    
                    # Daily анализ
                    if 'daily_analysis' in elliott_analysis:
                        daily = elliott_analysis['daily_analysis']
                        print(f"   📅 ДНЕВЕН АНАЛИЗ: {daily.get('wave', 'UNKNOWN')}")
                        print(f"      Тренд: {daily.get('trend', 'UNKNOWN')}")
                        print(f"      Описание: {daily.get('description', '')}")
                    
                    # Weekly анализ
                    if 'weekly_analysis' in elliott_analysis:
                        weekly = elliott_analysis['weekly_analysis']
                        print(f"   📊 СЕДМИЧЕН АНАЛИЗ: {weekly.get('wave', 'UNKNOWN')}")
                        print(f"      Тренд: {weekly.get('trend', 'UNKNOWN')}")
                        print(f"      Описание: {weekly.get('description', '')}")
                    
                    # Trading сигнали
                    if 'trading_signals' in elliott_analysis:
                        signals = elliott_analysis['trading_signals']
                        print(f"   💡 TRADING СИГНАЛИ: {signals.get('action', 'UNKNOWN')}")
                        print(f"      Причина: {signals.get('reason', '')}")
                        print(f"      Ниво на риска: {signals.get('risk_level', 'UNKNOWN')}")
                    
                    # Elliott Wave правила
                    if elliott_analysis.get('elliott_rules_valid'):
                        print(f"   ✅ ELLIOTT WAVE ПРАВИЛА: Валидни")
                    else:
                        print(f"   ⚠️  ELLIOTT WAVE ПРАВИЛА: Нарушени")
            
            # Divergence Analysis (НОВО от ideas файла)
            try:
                if 'divergence_analysis' in signal:
                    div_analysis = signal['divergence_analysis']
                    if div_analysis and isinstance(div_analysis, dict) and 'error' not in div_analysis:
                        print(f"\n🔄 DIVERGENCE АНАЛИЗ:")
                        if div_analysis.get('rsi_divergence', {}).get('type') != 'NONE':
                            rsi_div = div_analysis['rsi_divergence']
                            print(f"   📊 RSI Divergence: {rsi_div['type']} (увереност: {rsi_div['confidence']:.1f}%)")
                            print(f"      Причина: {rsi_div['reason']}")

                        if div_analysis.get('macd_divergence', {}).get('type') != 'NONE':
                            macd_div = div_analysis['macd_divergence']
                            print(f"   📈 MACD Divergence: {macd_div['type']} (увереност: {macd_div['confidence']:.1f}%)")
                            print(f"      Причина: {macd_div['reason']}")

                        pv_div_data = div_analysis.get('price_volume_divergence')
                        if pv_div_data and isinstance(pv_div_data, dict) and pv_div_data.get('type') != 'NONE':
                            print(f"   📊 Price-Volume Divergence: {pv_div_data['type']} (увереност: {pv_div_data['confidence']:.1f}%)")
                            print(f"      Причина: {pv_div_data['reason']}")

                        overall_div = div_analysis.get('overall_divergence', 'NONE')
                        print(f"   🎯 Общ Divergence: {overall_div}")
                    elif div_analysis is None:
                        print(f"\n🔄 DIVERGENCE АНАЛИЗ: Недостъпен (None)")
                    else:
                        error_msg = "Unknown error"
                        if isinstance(div_analysis, dict) and 'error' in div_analysis:
                            error_msg = div_analysis['error']
                        print(f"\n🔄 DIVERGENCE АНАЛИЗ: Грешка - {error_msg}")
            except Exception as e:
                logger.warning(f"Грешка при показване на Divergence анализ: {e}")
            
            # Moving Averages Analysis (НОВО от ideas файла)
            try:
                if 'moving_averages_analysis' in signal and signal['moving_averages_analysis']:
                    ma_analysis = signal['moving_averages_analysis']
                    if ma_analysis and 'error' not in ma_analysis:
                        print(f"\n📊 MOVING AVERAGES АНАЛИЗ:")
                        crossover = ma_analysis.get('crossover_signal', {})
                        if crossover and crossover.get('signal') != 'NONE':
                            print(f"   🎯 Crossover: {crossover['signal']}")
                            print(f"      Причина: {crossover['reason']}")
                            print(f"      Увереност: {crossover['confidence']:.1f}%")
                            if 'crossover_strength' in crossover:
                                print(f"      Сила: {crossover['crossover_strength']:.2%}")

                        # EMA стойности
                        fast_ema = ma_analysis.get('fast_ema_current')
                        slow_ema = ma_analysis.get('slow_ema_current')
                        if fast_ema and slow_ema:
                            print(f"   📈 EMA стойности:")
                            print(f"      Fast EMA (10): ${fast_ema:,.2f}")
                            print(f"      Slow EMA (50): ${slow_ema:,.2f}")

                        if ma_analysis.get('volume_confirmed', False):
                            print(f"   ✅ Volume Confirmation: Да")
            except Exception as e:
                logger.warning(f"Грешка при показване на Moving Averages анализ: {e}")
            
            # Price Action Patterns Analysis (НОВО от ideas файла)
            try:
                if 'price_patterns_analysis' in signal and signal['price_patterns_analysis']:
                    patterns = signal['price_patterns_analysis']
                    if 'error' not in patterns:
                        print(f"\n📐 PRICE ACTION PATTERNS:")
                        overall_pattern = patterns.get('overall_pattern', 'NONE')
                        print(f"   🎯 Общ Pattern: {overall_pattern}")

                        if patterns.get('double_top', {}).get('detected'):
                            dt = patterns['double_top']
                            print(f"   🔴 Double Top: {dt['reason']}")
                            print(f"      Увереност: {dt['confidence']:.1f}% | Сила: {dt['pattern_strength']}")
                            print(f"      Пикове: ${dt['peak1_price']:.2f}, ${dt['peak2_price']:.2f}")

                        if patterns.get('double_bottom', {}).get('detected'):
                            db = patterns['double_bottom']
                            print(f"   🟢 Double Bottom: {db['reason']}")
                            print(f"      Увереност: {db['confidence']:.1f}% | Сила: {db['pattern_strength']}")
                            print(f"      Дъна: ${db['trough1_price']:.2f}, ${db['trough2_price']:.2f}")

                        if patterns.get('head_shoulders', {}).get('detected'):
                            hs = patterns['head_shoulders']
                            print(f"   🔴 Head & Shoulders: {hs['reason']}")
                            print(f"      Увереност: {hs['confidence']:.1f}% | Сила: {hs['pattern_strength']}")
                            print(f"      Пикове: ${hs['left_shoulder_price']:.2f}, ${hs['head_price']:.2f}, ${hs['right_shoulder_price']:.2f}")

                        if patterns.get('inverse_head_shoulders', {}).get('detected'):
                            ihs = patterns['inverse_head_shoulders']
                            print(f"   🟢 Inverse H&S: {ihs['reason']}")
                            print(f"      Увереност: {ihs['confidence']:.1f}% | Сила: {ihs['pattern_strength']}")
                            print(f"      Дъна: ${ihs['left_shoulder_price']:.2f}, ${ihs['head_price']:.2f}, ${ihs['right_shoulder_price']:.2f}")

                        if patterns.get('triangle', {}).get('detected'):
                            tri = patterns['triangle']
                            print(f"   🔺 Triangle: {tri['reason']}")
                            print(f"      Увереност: {tri['confidence']:.1f}% | Сила: {tri['pattern_strength']}")
                            print(f"      Тип: {tri['triangle_type']}")

                        if patterns.get('wedge', {}).get('detected'):
                            wedge = patterns['wedge']
                            print(f"   🔶 Wedge: {wedge['reason']}")
                            print(f"      Увереност: {wedge['confidence']:.1f}% | Сила: {wedge['pattern_strength']}")
                            print(f"      Тип: {wedge['wedge_type']}")
            except Exception as e:
                logger.warning(f"Грешка при показване на Price Action Patterns анализ: {e}")
            
            # Whale Tracker Analysis - ново!
            try:
                if 'whale_analysis' in signal and signal['whale_analysis']:
                    whale_analysis = signal['whale_analysis']
                    if whale_analysis and 'error' not in whale_analysis:
                        print(f"\n🐋 WHALE TRACKER АНАЛИЗ (институционални движения):")

                        # Whale sentiment
                        if 'sentiment' in whale_analysis:
                            sentiment = whale_analysis['sentiment']
                            print(f"   🧠 WHALE SENTIMENT: {sentiment.get('sentiment', 'UNKNOWN')}")
                            print(f"      Увереност: {sentiment.get('confidence', 0)}%")
                            print(f"      Buy/Sell Ratio: {sentiment.get('buy_ratio', 0):.1f}%/{sentiment.get('sell_ratio', 0):.1f}%")

                        # High volume periods
                        if 'high_volume_periods' in whale_analysis:
                            high_vol = whale_analysis['high_volume_periods']
                            if high_vol:
                                mega_whale_count = len([p for p in high_vol if "MEGA WHALE" in p.get("whale_signal", "")])
                                whale_count = len([p for p in high_vol if "🐳 WHALE" in p.get("whale_signal", "")])
                                print(f"   📊 WHALE АКТИВНОСТ: {len(high_vol)} сигнала")
                                print(f"      Mega Whale: {mega_whale_count} | Whale: {whale_count}")

                                # Biggest signal
                                if high_vol:
                                    biggest = max(high_vol, key=lambda x: x.get("volume_ratio", 0))
                                    print(f"      Най-голям сигнал: {biggest.get('whale_signal', 'UNKNOWN')}")
                                    print(f"         Volume: {biggest.get('volume', 0):,.0f} BNB ({biggest.get('volume_ratio', 0):.1f}x)")
            except Exception as e:
                logger.warning(f"Грешка при показване на Whale Tracker анализ: {e}")
            
            # Ichimoku Cloud Analysis - ново!
            try:
                if 'ichimoku_analysis' in signal and signal['ichimoku_analysis']:
                    ichimoku_analysis = signal['ichimoku_analysis']
                    if ichimoku_analysis and 'error' not in ichimoku_analysis:
                        print(f"\n☁️ ICHIMOKU CLOUD АНАЛИЗ (японски технически анализ):")

                        # Cloud status
                        cloud_status = ichimoku_analysis.get('cloud_status', 'UNKNOWN')
                        print(f"   ☁️ CLOUD СТАТУС: {cloud_status}")

                        # Overall trend
                        overall_trend = ichimoku_analysis.get('overall_trend', 'UNKNOWN')
                        print(f"   📈 ОБЩ ТРЕНД: {overall_trend}")

                        # Action
                        action = ichimoku_analysis.get('action', 'UNKNOWN')
                        print(f"   🎯 ДЕЙСТВИЕ: {action}")

                        # Key levels
                        if ichimoku_analysis.get('support_levels'):
                            print(f"   🛡️ SUPPORT НИВА:")
                            for level in ichimoku_analysis['support_levels'][:2]:
                                print(f"      • {level}")

                        if ichimoku_analysis.get('resistance_levels'):
                            print(f"   ⚡ RESISTANCE НИВА:")
                            for level in ichimoku_analysis['resistance_levels'][:2]:
                                print(f"      • {level}")

                        # Cloud analysis
                        current_price = ichimoku_analysis.get('current_price', 0)
                        if current_price > 0:
                            senkou_a = ichimoku_analysis.get('senkou_span_a')
                            senkou_b = ichimoku_analysis.get('senkou_span_b')
                            if senkou_a is not None and senkou_b is not None:
                                cloud_top = senkou_a or senkou_b
                                if cloud_top > 0:
                                    cloud_position = "ABOVE" if current_price > cloud_top else "BELOW" if current_price < cloud_top else "IN"
                                    cloud_distance = abs(current_price - cloud_top)
                                    cloud_distance_pct = (cloud_distance / current_price) * 100
                                    print(f"   ☁️ CLOUD АНАЛИЗ:")
                                    print(f"      Позиция: {cloud_position} облака")
                                    print(f"      Разстояние: ${cloud_distance:.2f} ({cloud_distance_pct:.1f}%)")
                                    print(f"      Cloud Top: ${cloud_top:.2f}")
            except Exception as e:
                logger.warning(f"Грешка при показване на Ichimoku анализ: {e}")
            
            # Market Sentiment Analysis - ново!
            try:
                if 'sentiment_analysis' in signal:
                    sentiment_analysis = signal['sentiment_analysis']
                    if 'error' not in sentiment_analysis:
                        print(f"\n🎭 MARKET SENTIMENT АНАЛИЗ (психология на пазара):")

                        # Overall sentiment
                        overall_sentiment = sentiment_analysis.get('overall_sentiment', 'UNKNOWN')
                        print(f"   🎯 ОБЩ SENTIMENT: {overall_sentiment}")

                        # Composite score
                        composite_score = sentiment_analysis.get('composite_score', 0)
                        print(f"   📊 COMPOSITE SCORE: {composite_score}/100")

                        # Action
                        action = sentiment_analysis.get('action', 'UNKNOWN')
                        print(f"   💡 SENTIMENT ACTION: {action}")

                        # Individual scores
                        if 'individual_scores' in sentiment_analysis:
                            scores = sentiment_analysis['individual_scores']
                            print(f"   📈 КОМПОНЕНТИ:")
                            print(f"      Fear & Greed: {scores.get('fear_greed', 0)}/100")
                            print(f"      Social Media: {scores.get('social_media', 0)}/100")
                            print(f"      News: {scores.get('news', 0)}/100")
                            print(f"      Momentum: {scores.get('momentum', 0)}/100")
            except Exception as e:
                logger.warning(f"Грешка при показване на Sentiment анализ: {e}")
            
            # Trend Analysis - ново!
            try:
                if 'trend_analysis' in signal:
                    trend_analysis = signal['trend_analysis']
                    if 'error' not in trend_analysis:
                        print(f"\n📈 TREND АНАЛИЗ (адаптивни entry стратегии):")

                        # Основен тренд
                        if 'combined_trend' in trend_analysis:
                            combined = trend_analysis['combined_trend']
                            print(f"   🎯 ОСНОВЕН ТРЕНД: {combined.get('primary_trend', 'UNKNOWN')}")
                            print(f"      Увереност: {combined.get('trend_confidence', 'UNKNOWN')}")
                            print(f"      Приключил: {'ДА' if combined.get('trend_completed') else 'НЕ'}")

                        # Дневен тренд
                        if 'daily_trend' in trend_analysis:
                            daily = trend_analysis['daily_trend']
                            print(f"   📅 ДНЕВЕН ТРЕНД: {daily.get('direction', 'UNKNOWN')} ({daily.get('strength', 'UNKNOWN')})")
                            print(f"      Промяна: {daily.get('price_change_pct', 0):+.2f}% (${daily.get('start_price', 0):.0f} → ${daily.get('end_price', 0):.0f})")

                        # Седмичен тренд
                        if 'weekly_trend' in trend_analysis:
                            weekly = trend_analysis['weekly_trend']
                            print(f"   📊 СЕДМИЧЕН ТРЕНД: {weekly.get('direction', 'UNKNOWN')} ({weekly.get('strength', 'UNKNOWN')})")
                            print(f"      Промяна: {weekly.get('price_change_pct', 0):+.2f}% (${weekly.get('start_price', 0):.0f} → ${weekly.get('end_price', 0):.0f})")

                        # Range анализ
                        if 'range_analysis' in trend_analysis:
                            range_analysis = trend_analysis['range_analysis']
                            print(f"   📏 RANGE АНАЛИЗ: {range_analysis.get('range_status', 'UNKNOWN')}")
                            print(f"      Текущ range: {range_analysis.get('current_range_pct', 0):.1f}%")
                            print(f"      Позиция в range: {range_analysis.get('range_position', 0):.1%}")

                        # Адаптивна стратегия
                        if 'adaptive_strategy' in trend_analysis:
                            strategy = trend_analysis['adaptive_strategy']
                            if 'error' not in strategy:
                                print(f"   🎯 АДАПТИВНА СТРАТЕГИЯ:")
                                if 'trend_based_entry' in strategy:
                                    entry = strategy['trend_based_entry']
                                    print(f"      Тип: {entry.get('type', 'UNKNOWN')}")
                                    print(f"      Описание: {entry.get('description', '')}")

                                if 'timing_recommendation' in strategy:
                                    timing = strategy['timing_recommendation']
                                    print(f"      Време: {timing.get('timing', 'UNKNOWN')}")
                                    print(f"      Причина: {timing.get('reason', '')}")
            except Exception as e:
                logger.warning(f"Грешка при показване на Trend анализ: {e}")
            
            # Следващи цели - само основните
            try:
                if 'next_targets' in signal:
                    next_targets = signal['next_targets']
                    if next_targets and isinstance(next_targets, dict):
                        print(f"\n🎯 СЛЕДВАЩИ ЦЕЛИ:")
                        if next_targets.get('entry_price'):
                            print(f"   Entry: ${next_targets['entry_price']:,.2f}")
                        if next_targets.get('exit_price'):
                            print(f"   Exit: ${next_targets['exit_price']:,.2f}")
            except Exception as e:
                logger.warning(f"Грешка при показване на следващи цели: {e}")
            
            analysis_date = signal.get('analysis_date', pd.Timestamp.now())
            if analysis_date and hasattr(analysis_date, 'strftime'):
                date_str = analysis_date.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
            print(f"\n⏰ Анализ: {date_str}")
            print("🎯" * 20)
            
        except Exception as e:
            logger.error(f"Грешка при показване на детайлния анализ: {e}")
            print(f"❌ Грешка при показване на детайлния анализ: {e}")
    
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
                
                analysis_date = results.get('analysis_date', pd.Timestamp.now())
                if analysis_date and hasattr(analysis_date, 'strftime'):
                    date_str = analysis_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date_str = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"Анализът е извършен на: {date_str}\n")
            
    
            
        except Exception as e:
            logger.error(f"Грешка при експортиране на резултатите: {e}")

def main():
    """Главна функция"""
    try:
        # Създаваме системата
        trading_system = BNBTradingSystem()
        
        # Изпълняваме анализа
        results = trading_system.run_analysis()
        
        if 'error' in results:
            print(f"❌ Грешка: {results['error']}")
            return
        
        # Използваме пълния сигнал с индикаторите
        if 'full_signal' in results:
            full_signal = results['full_signal']
        else:
            # Ако нямаме full_signal, трябва да го получим директно от signal_generator
            # Засега използваме current_signal
            full_signal = results['current_signal']
        
        # Показваме само красивия резултат
        trading_system.display_current_signal_detailed(full_signal)
        
        # Експортираме резултатите тихо
        trading_system.export_results(results)
        trading_system.validator.export_results_summary('data/results_summary.txt')
        
        print("\n✅ Анализът е завършен успешно!")
        print("📁 Резултатите са записани в data/ директорията")
        
    except Exception as e:
        logger.error(f"Критична грешка: {e}")
        print(f"❌ Критична грешка: {e}")
        print("Проверете лог файла 'bnb_trading.log' за повече детайли")

if __name__ == "__main__":
    main()
