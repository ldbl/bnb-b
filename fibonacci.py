"""
Fibonacci Module - СПЕЦИАЛЕН модул за Fibonacci retracement изчисления
ПРИОРИТЕТ №1: Автоматично намиране на swing points и изчисляване на всички Fib нива
Фокус върху 61.8% и 38.2% като най-важни нива за BNB
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FibonacciAnalyzer:
    """Клас за Fibonacci retracement анализ на BNB"""
    
    def __init__(self, config: Dict):
        """
        Инициализира Fibonacci анализатора
        
        Args:
            config: Конфигурационни параметри
        """
        self.swing_lookback = config['fibonacci']['swing_lookback']
        self.key_levels = config['fibonacci']['key_levels']
        self.proximity_threshold = config['fibonacci']['proximity_threshold']
        self.min_swing_size = config['fibonacci']['min_swing_size']
        
        # Всички Fibonacci нива (0% до 100%)
        self.fib_levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        
        logger.info("Fibonacci анализатор инициализиран")
        logger.info(f"Ключови нива: {self.key_levels}")
        logger.info(f"Минимален swing размер: {self.min_swing_size:.1%}")
    
    def find_swing_points(self, df: pd.DataFrame) -> Tuple[float, float, int, int]:
        """
        Намира последния swing high и swing low
        
        Args:
            df: DataFrame с OHLCV данни
            
        Returns:
            Tuple: (swing_high_price, swing_low_price, high_index, low_index)
        """
        try:
            # Използваме последните N периоди за търсене на swing points
            lookback_data = df.tail(self.swing_lookback)
            
            # Намираме swing high (локален максимум)
            swing_high_idx = lookback_data['High'].idxmax()
            swing_high_price = lookback_data.loc[swing_high_idx, 'High']
            swing_high_pos = lookback_data.index.get_loc(swing_high_idx)
            
            # Намираме swing low (локален минимум)
            swing_low_idx = lookback_data['Low'].idxmin()
            swing_low_price = lookback_data.loc[swing_low_idx, 'Low']
            swing_low_pos = lookback_data.index.get_loc(swing_low_idx)
            
            # Проверяваме дали swing е достатъчно голям
            swing_size = abs(swing_high_price - swing_low_price) / swing_low_price
            
            if swing_size < self.min_swing_size:
                logger.warning(f"Swing размер {swing_size:.1%} е под минимума {self.min_swing_size:.1%}")
                return None, None, None, None
            
            logger.info(f"Намерени swing points: High=${swing_high_price:,.2f}, Low=${swing_low_price:,.2f}")
            logger.info(f"Swing размер: {swing_size:.1%}")
            
            return swing_high_price, swing_low_price, swing_high_pos, swing_low_pos
            
        except Exception as e:
            logger.error(f"Грешка при търсене на swing points: {e}")
            return None, None, None, None
    
    def calculate_fibonacci_levels(self, swing_high: float, swing_low: float) -> Dict[float, float]:
        """
        Изчислява всички Fibonacci retracement нива
        
        Args:
            swing_high: Цена на swing high
            swing_low: Цена на swing low
            
        Returns:
            Dict с Fibonacci нива и съответните цени
        """
        try:
            if swing_high is None or swing_low is None:
                return {}
            
            # Изчисляваме разликата между swing high и low
            price_range = swing_high - swing_low
            
            # Изчисляваме всички Fibonacci нива
            fib_levels = {}
            for level in self.fib_levels:
                if level == 0.0:
                    fib_levels[level] = swing_low  # 0% = swing low
                elif level == 1.0:
                    fib_levels[level] = swing_high  # 100% = swing high
                else:
                    # Retracement нива: swing_low + (level * price_range)
                    fib_levels[level] = swing_low + (level * price_range)
            
            logger.info("Fibonacci нива изчислени:")
            for level, price in fib_levels.items():
                logger.info(f"  {level*100:5.1f}%: ${price:,.2f}")
            
            return fib_levels
            
        except Exception as e:
            logger.error(f"Грешка при изчисляване на Fibonacci нива: {e}")
            return {}
    
    def check_fib_proximity(self, current_price: float, fib_levels: Dict[float, float]) -> Dict[str, any]:
        """
        Проверява дали текущата цена е близо до Fibonacci ниво
        
        Args:
            current_price: Текущата цена на BNB
            fib_levels: Dict с Fibonacci нива
            
        Returns:
            Dict с информация за близостта до Fibonacci нива
        """
        try:
            proximity_info = {
                'nearest_level': None,
                'nearest_distance': float('inf'),
                'nearest_percentage': None,
                'active_levels': [],
                'key_level_proximity': {}
            }
            
            for level, price in fib_levels.items():
                # Изчисляваме разстоянието до нивото
                distance = abs(current_price - price)
                distance_percentage = distance / current_price
                
                # Проверяваме дали сме в близост до нивото
                if distance_percentage <= self.proximity_threshold:
                    proximity_info['active_levels'].append({
                        'level': level,
                        'price': price,
                        'distance': distance,
                        'distance_percentage': distance_percentage
                    })
                
                # Намираме най-близкото ниво
                if distance < proximity_info['nearest_distance']:
                    proximity_info['nearest_distance'] = distance
                    proximity_info['nearest_level'] = level
                    proximity_info['nearest_percentage'] = distance_percentage
                
                # Специална проверка за ключовите нива (38.2% и 61.8%)
                if level in self.key_levels:
                    proximity_info['key_level_proximity'][level] = {
                        'price': price,
                        'distance': distance,
                        'distance_percentage': distance_percentage,
                        'is_active': distance_percentage <= self.proximity_threshold
                    }
            
            # Сортираме активните нива по близост
            proximity_info['active_levels'].sort(key=lambda x: x['distance_percentage'])
            
            logger.info(f"Текуща цена ${current_price:,.2f}")
            logger.info(f"Най-близко Fibonacci ниво: {proximity_info['nearest_level']*100:.1f}% (${fib_levels[proximity_info['nearest_level']]:,.2f})")
            logger.info(f"Разстояние: {proximity_info['nearest_percentage']:.2%}")
            
            if proximity_info['active_levels']:
                logger.info("Активни Fibonacci нива:")
                for level_info in proximity_info['active_levels']:
                    logger.info(f"  {level_info['level']*100:5.1f}%: ${level_info['price']:,.2f} (±{level_info['distance_percentage']:.2%})")
            
            return proximity_info
            
        except Exception as e:
            logger.error(f"Грешка при проверка на Fibonacci близост: {e}")
            return {}
    
    def get_fibonacci_signal(self, current_price: float, fib_levels: Dict[float, float]) -> Dict[str, any]:
        """
        Генерира Fibonacci сигнал базиран на текущата цена
        
        Args:
            current_price: Текущата цена на BNB
            fib_levels: Dict с Fibonacci нива
            
        Returns:
            Dict с Fibonacci сигнал информация
        """
        try:
            proximity_info = self.check_fib_proximity(current_price, fib_levels)
            
            if not proximity_info:
                return {'signal': 'HOLD', 'reason': 'Неуспешно изчисляване на Fibonacci нива'}
            
            signal_info = {
                'signal': 'HOLD',
                'strength': 0.0,
                'reason': '',
                'fib_levels': fib_levels,
                'proximity': proximity_info,
                'support_levels': [],
                'resistance_levels': []
            }
            
            # Определяме support и resistance нива
            for level, price in fib_levels.items():
                if price < current_price:
                    signal_info['support_levels'].append((level, price))
                else:
                    signal_info['resistance_levels'].append((level, price))
            
            # Сортираме по близост до текущата цена
            signal_info['support_levels'].sort(key=lambda x: abs(x[1] - current_price))
            signal_info['resistance_levels'].sort(key=lambda x: abs(x[1] - current_price))
            
            # Генерираме сигнал базиран на Fibonacci нива
            if proximity_info['active_levels']:
                active_level = proximity_info['active_levels'][0]
                level = active_level['level']
                
                if level in [0.236, 0.382]:  # Support нива
                    signal_info['signal'] = 'LONG'
                    signal_info['strength'] = 0.8 if level == 0.382 else 0.6
                    signal_info['reason'] = f"Цената е на Fibonacci support {level*100:.1f}%"
                elif level in [0.618, 0.786]:  # Resistance нива
                    signal_info['signal'] = 'SHORT'
                    signal_info['strength'] = 0.8 if level == 0.618 else 0.6
                    signal_info['reason'] = f"Цената е на Fibonacci resistance {level*100:.1f}%"
                elif level == 0.5:  # Средно ниво
                    signal_info['signal'] = 'HOLD'
                    signal_info['strength'] = 0.4
                    signal_info['reason'] = "Цената е на Fibonacci 50% ниво"
            
            # Добавяме информация за следващите нива
            if signal_info['signal'] == 'LONG':
                next_resistance = signal_info['resistance_levels'][0] if signal_info['resistance_levels'] else None
                if next_resistance:
                    signal_info['next_target'] = f"Следващо ниво: {next_resistance[0]*100:.1f}% (${next_resistance[1]:,.2f})"
            
            elif signal_info['signal'] == 'SHORT':
                next_support = signal_info['support_levels'][0] if signal_info['support_levels'] else None
                if next_support:
                    signal_info['next_target'] = f"Следващо ниво: {next_support[0]*100:.1f}% (${next_support[1]:,.2f})"
            
            logger.info(f"Fibonacci сигнал: {signal_info['signal']} (сила: {signal_info['strength']:.1f})")
            logger.info(f"Причина: {signal_info['reason']}")
            
            return signal_info
            
        except Exception as e:
            logger.error(f"Грешка при генериране на Fibonacci сигнал: {e}")
            return {'signal': 'HOLD', 'reason': f'Грешка: {e}'}
    
    def analyze_fibonacci_trend(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Анализира Fibonacci тренд за цялата история
        
        Args:
            df: DataFrame с исторически данни
            
        Returns:
            Dict с Fibonacci тренд анализ
        """
        try:
            # Намираме swing points
            swing_high, swing_low, high_idx, low_idx = self.find_swing_points(df)
            
            if swing_high is None:
                return {'error': 'Неуспешно намиране на swing points'}
            
            # Изчисляваме Fibonacci нива
            fib_levels = self.calculate_fibonacci_levels(swing_high, swing_low)
            
            if not fib_levels:
                return {'error': 'Неуспешно изчисляване на Fibonacci нива'}
            
            # Изчисляваме Fibonacci extensions
            fib_extensions = self.calculate_fibonacci_extensions(swing_high, swing_low)
            
            # Анализираме текущата цена
            current_price = df['Close'].iloc[-1]
            fib_signal = self.get_fibonacci_signal(current_price, fib_levels)
            
            trend_analysis = {
                'swing_high': swing_high,
                'swing_low': swing_low,
                'swing_size': abs(swing_high - swing_low) / swing_low,
                'fibonacci_levels': fib_levels,
                'fibonacci_extensions': fib_extensions,
                'current_price': current_price,
                'fibonacci_signal': fib_signal,
                'analysis_date': df.index[-1]
            }
            
            logger.info("Fibonacci тренд анализ завършен")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Грешка при Fibonacci тренд анализ: {e}")
            return {'error': f'Грешка: {e}'}
    
    def calculate_fibonacci_extensions(self, swing_high: float, swing_low: float) -> Dict[float, float]:
        """
        Изчислява Fibonacci extension нива за целите нагоре
        
        Args:
            swing_high: Цена на swing high
            swing_low: Цена на swing low
            
        Returns:
            Dict с Fibonacci extension нива и съответните цени
        """
        try:
            if swing_high is None or swing_low is None:
                return {}
            
            # Изчисляваме разликата между swing high и low
            price_range = swing_high - swing_low
            
            # Extension нива (над 100%)
            extension_levels = [1.0, 1.272, 1.414, 1.618, 2.0, 2.618]
            
            # Изчисляваме extension нива
            fib_extensions = {}
            for level in extension_levels:
                # Extension: swing_low + (level * price_range)
                fib_extensions[level] = swing_low + (level * price_range)
            
            logger.info("Fibonacci extension нива изчислени:")
            for level, price in fib_extensions.items():
                logger.info(f"  {level*100:5.1f}%: ${price:,.2f}")
            
            return fib_extensions
            
        except Exception as e:
            logger.error(f"Грешка при изчисляване на Fibonacci extensions: {e}")
            return {}

if __name__ == "__main__":
    # Тест на Fibonacci модула
    print("Fibonacci модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
