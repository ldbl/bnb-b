"""
Moving Averages Module
Открива реверсали чрез пресичане на краткосрочна и дългосрочна EMA
Базирано на ideas файла - прост и ефективен за крипто
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MovingAveragesAnalyzer:
    """Анализатор за Moving Average Crossovers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.fast_period = config.get('moving_averages', {}).get('fast_period', 10)
        self.slow_period = config.get('moving_averages', {}).get('slow_period', 50)
        self.volume_confirmation = config.get('moving_averages', {}).get('volume_confirmation', True)
        self.volume_multiplier = config.get('moving_averages', {}).get('volume_multiplier', 1.5)
        self.volume_lookback = config.get('moving_averages', {}).get('volume_lookback', 14)
        
        logger.info("Moving Averages анализатор инициализиран")
    
    def calculate_emas(self, price_data: pd.DataFrame) -> Dict:
        """
        Изчислява Exponential Moving Averages
        
        Args:
            price_data: DataFrame с OHLCV данни
            
        Returns:
            Dict с EMA стойности
        """
        try:
            if len(price_data) < self.slow_period:
                return {'error': f'Недостатъчно данни. Нужни са поне {self.slow_period} периода'}
            
            closes = price_data['close'].values if 'close' in price_data.columns else price_data['Close'].values
            
            # Изчисляваме EMA
            fast_ema = self._calculate_ema(closes, self.fast_period)
            slow_ema = self._calculate_ema(closes, self.slow_period)
            
            # Изчисляваме volume confirmation
            volume_confirmed = False
            if self.volume_confirmation and 'volume' in price_data.columns:
                volume_confirmed = self._check_volume_confirmation(price_data)
            
            return {
                'fast_ema': fast_ema,
                'slow_ema': slow_ema,
                'fast_ema_current': fast_ema[-1] if len(fast_ema) > 0 else None,
                'slow_ema_current': slow_ema[-1] if len(slow_ema) > 0 else None,
                'volume_confirmed': volume_confirmed,
                'crossover_signal': self._detect_crossover(fast_ema, slow_ema)
            }
            
        except Exception as e:
            logger.error(f"Грешка при изчисляване на EMA: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Изчислява Exponential Moving Average"""
        try:
            if len(prices) < period:
                return np.array([])
            
            # Изчисляваме SMA за първите period периода
            sma = np.mean(prices[:period])
            
            # Multiplier за EMA
            multiplier = 2 / (period + 1)
            
            # Инициализираме EMA масива
            ema = np.zeros(len(prices))
            ema[period - 1] = sma
            
            # Изчисляваме EMA за останалите периоди
            for i in range(period, len(prices)):
                ema[i] = (prices[i] * multiplier) + (ema[i - 1] * (1 - multiplier))
            
            return ema
            
        except Exception as e:
            logger.error(f"Грешка при изчисляване на EMA: {e}")
            return np.array([])
    
    def _detect_crossover(self, fast_ema: np.ndarray, slow_ema: np.ndarray) -> Dict:
        """
        Открива crossover между fast и slow EMA
        
        Args:
            fast_ema: Fast EMA стойности
            slow_ema: Slow EMA стойности
            
        Returns:
            Dict с crossover сигнала
        """
        try:
            if len(fast_ema) < 2 or len(slow_ema) < 2:
                return {'signal': 'NONE', 'confidence': 0, 'reason': 'Недостатъчно данни'}
            
            # Текущи стойности
            fast_current = fast_ema[-1]
            fast_previous = fast_ema[-2]
            slow_current = slow_ema[-1]
            slow_previous = slow_ema[-2]
            
            # Проверяваме за bullish crossover
            if (fast_previous <= slow_previous and fast_current > slow_current):
                # Fast EMA пресича нагоре slow EMA
                crossover_strength = abs(fast_current - slow_current) / slow_current
                confidence = min(95, 60 + crossover_strength * 100)
                
                return {
                    'signal': 'BULLISH_CROSS',
                    'confidence': confidence,
                    'reason': f'Fast EMA ({self.fast_period}) пресича нагоре Slow EMA ({self.slow_period})',
                    'crossover_strength': crossover_strength,
                    'fast_ema': fast_current,
                    'slow_ema': slow_current
                }
            
            # Проверяваме за bearish crossover
            elif (fast_previous >= slow_previous and fast_current < slow_current):
                # Fast EMA пресича надолу slow EMA
                crossover_strength = abs(fast_current - slow_current) / slow_current
                confidence = min(95, 60 + crossover_strength * 100)
                
                return {
                    'signal': 'BEARISH_CROSS',
                    'confidence': confidence,
                    'reason': f'Fast EMA ({self.fast_period}) пресича надолу Slow EMA ({self.slow_period})',
                    'crossover_strength': crossover_strength,
                    'fast_ema': fast_current,
                    'slow_ema': slow_current
                }
            
            # Проверяваме за текущо състояние
            else:
                if fast_current > slow_current:
                    # Fast EMA е над slow EMA - bullish
                    distance = (fast_current - slow_current) / slow_current
                    confidence = min(80, 50 + distance * 100)
                    
                    return {
                        'signal': 'BULLISH_ABOVE',
                        'confidence': confidence,
                        'reason': f'Fast EMA ({self.fast_period}) е над Slow EMA ({self.slow_period})',
                        'distance': distance,
                        'fast_ema': fast_current,
                        'slow_ema': slow_current
                    }
                else:
                    # Fast EMA е под slow EMA - bearish
                    distance = (slow_current - fast_current) / slow_current
                    confidence = min(80, 50 + distance * 100)
                    
                    return {
                        'signal': 'BEARISH_BELOW',
                        'confidence': confidence,
                        'reason': f'Fast EMA ({self.fast_period}) е под Slow EMA ({self.slow_period})',
                        'distance': distance,
                        'fast_ema': fast_current,
                        'slow_ema': slow_current
                    }
                    
        except Exception as e:
            logger.error(f"Грешка при откриване на crossover: {e}")
            return {'signal': 'NONE', 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _check_volume_confirmation(self, price_data: pd.DataFrame) -> bool:
        """
        Проверява volume confirmation
        
        Args:
            price_data: DataFrame с OHLCV данни
            
        Returns:
            bool: True ако volume потвърждава сигнала
        """
        try:
            if 'volume' not in price_data.columns:
                return False
            
            volumes = price_data['volume'].values
            
            if len(volumes) < self.volume_lookback:
                return False
            
            # Изчисляваме среден обем за последните volume_lookback периода
            recent_volumes = volumes[-self.volume_lookback:]
            avg_volume = np.mean(recent_volumes)
            
            # Проверяваме дали текущият обем е над средния
            current_volume = volumes[-1]
            volume_threshold = avg_volume * self.volume_multiplier
            
            return current_volume > volume_threshold
            
        except Exception as e:
            logger.error(f"Грешка при проверка на volume confirmation: {e}")
            return False
    
    def get_ma_trading_signals(self, ma_analysis: Dict) -> Dict:
        """
        Генерира trading сигнали базирани на Moving Averages
        
        Args:
            ma_analysis: Резултат от calculate_emas
            
        Returns:
            Dict с trading сигнали
        """
        try:
            if 'error' in ma_analysis:
                return {
                    'signal': 'HOLD',
                    'confidence': 0,
                    'reason': ma_analysis['error'],
                    'risk_level': 'UNKNOWN'
                }
            
            crossover = ma_analysis.get('crossover_signal', {})
            signal_type = crossover.get('signal', 'NONE')
            confidence = crossover.get('confidence', 0)
            volume_confirmed = ma_analysis.get('volume_confirmed', False)
            
            # Ако няма volume confirmation, намаляваме confidence
            if not volume_confirmed and self.volume_confirmation:
                confidence = max(confidence * 0.7, 30)
            
            # Генерираме trading сигнали
            if signal_type == 'BULLISH_CROSS':
                return {
                    'signal': 'BUY',
                    'confidence': confidence,
                    'reason': f'Bullish EMA Crossover: {crossover.get("reason", "")}',
                    'risk_level': 'MEDIUM' if volume_confirmed else 'HIGH',
                    'entry_price': 'Current price',
                    'stop_loss': f'Below {ma_analysis.get("slow_ema_current", 0):.2f}',
                    'target': f'Above {ma_analysis.get("fast_ema_current", 0):.2f}'
                }
            
            elif signal_type == 'BEARISH_CROSS':
                return {
                    'signal': 'SELL',
                    'confidence': confidence,
                    'reason': f'Bearish EMA Crossover: {crossover.get("reason", "")}',
                    'risk_level': 'MEDIUM' if volume_confirmed else 'HIGH',
                    'entry_price': 'Current price',
                    'stop_loss': f'Above {ma_analysis.get("slow_ema_current", 0):.2f}',
                    'target': f'Below {ma_analysis.get("fast_ema_current", 0):.2f}'
                }
            
            elif signal_type == 'BULLISH_ABOVE':
                return {
                    'signal': 'HOLD_LONG',
                    'confidence': confidence,
                    'reason': f'Bullish Trend: {crossover.get("reason", "")}',
                    'risk_level': 'LOW',
                    'entry_price': 'Pullback to slow EMA',
                    'stop_loss': f'Below {ma_analysis.get("slow_ema_current", 0):.2f}',
                    'target': 'Continue trend'
                }
            
            elif signal_type == 'BEARISH_BELOW':
                return {
                    'signal': 'HOLD_SHORT',
                    'confidence': confidence,
                    'reason': f'Bearish Trend: {crossover.get("reason", "")}',
                    'risk_level': 'LOW',
                    'entry_price': 'Bounce to slow EMA',
                    'stop_loss': f'Above {ma_analysis.get("slow_ema_current", 0):.2f}',
                    'target': 'Continue trend'
                }
            
            else:
                return {
                    'signal': 'WAIT',
                    'confidence': 50,
                    'reason': 'Няма ясен MA сигнал',
                    'risk_level': 'LOW'
                }
                
        except Exception as e:
            logger.error(f"Грешка при генериране на MA trading сигнали: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': f'Грешка: {e}',
                'risk_level': 'UNKNOWN'
            }
    
    def analyze_ma_strength(self, ma_analysis: Dict) -> Dict:
        """
        Анализира силата на Moving Average сигнала
        
        Args:
            ma_analysis: Резултат от calculate_emas
            
        Returns:
            Dict с анализ на силата
        """
        try:
            if 'error' in ma_analysis:
                return {'strength': 'UNKNOWN', 'reason': ma_analysis['error']}
            
            crossover = ma_analysis.get('crossover_signal', {})
            signal_type = crossover.get('signal', 'NONE')
            crossover_strength = crossover.get('crossover_strength', 0)
            volume_confirmed = ma_analysis.get('volume_confirmed', False)
            
            # Определяме силата на сигнала
            if signal_type in ['BULLISH_CROSS', 'BEARISH_CROSS']:
                if crossover_strength > 0.05:  # 5% разлика
                    strength = 'STRONG'
                elif crossover_strength > 0.02:  # 2% разлика
                    strength = 'MEDIUM'
                else:
                    strength = 'WEAK'
                
                # Volume confirmation увеличава силата
                if volume_confirmed:
                    strength = f"{strength}_VOLUME_CONFIRMED"
                
                reason = f"EMA Crossover с {crossover_strength:.2%} разлика"
                
            elif signal_type in ['BULLISH_ABOVE', 'BEARISH_BELOW']:
                distance = crossover.get('distance', 0)
                
                if distance > 0.1:  # 10% разлика
                    strength = 'VERY_STRONG'
                elif distance > 0.05:  # 5% разлика
                    strength = 'STRONG'
                elif distance > 0.02:  # 2% разлика
                    strength = 'MEDIUM'
                else:
                    strength = 'WEAK'
                
                reason = f"EMA Trend с {distance:.2%} разлика"
                
            else:
                strength = 'NEUTRAL'
                reason = 'Няма ясен MA сигнал'
            
            return {
                'strength': strength,
                'reason': reason,
                'crossover_strength': crossover_strength,
                'volume_confirmed': volume_confirmed
            }
            
        except Exception as e:
            logger.error(f"Грешка при анализ на MA сила: {e}")
            return {'strength': 'UNKNOWN', 'reason': f'Грешка: {e}'}

if __name__ == "__main__":
    print("Moving Averages анализатор за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
