"""
Price Action Patterns Module
Идентифицира класически модели като double top/bottom, с потвърждение от свещни формации
Базирано на ideas файла - базирано на чиста цена, надеждно в крипто
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PriceActionPatternsAnalyzer:
    """Анализатор за Price Action Patterns"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_pattern_distance = config.get('price_patterns', {}).get('min_pattern_distance', 5)
        self.pattern_threshold = config.get('price_patterns', {}).get('pattern_threshold', 0.02)
        self.volume_confirmation = config.get('price_patterns', {}).get('volume_confirmation', True)
        self.candle_confirmation = config.get('price_patterns', {}).get('candle_confirmation', True)
        
        logger.info("Price Action Patterns анализатор инициализиран")
    
    def detect_all_patterns(self, price_data: pd.DataFrame) -> Dict:
        """
        Открива всички видове price action patterns
        
        Args:
            price_data: DataFrame с OHLCV данни
            
        Returns:
            Dict с откритите patterns
        """
        try:
            patterns = {
                'double_top': None,
                'double_bottom': None,
                'head_shoulders': None,
                'inverse_head_shoulders': None,
                'triangle': None,
                'wedge': None,
                'overall_pattern': 'NONE'
            }
            
            # 1. Double Top Pattern
            patterns['double_top'] = self._detect_double_top(price_data)
            
            # 2. Double Bottom Pattern
            patterns['double_bottom'] = self._detect_double_bottom(price_data)
            
            # 3. Head & Shoulders Pattern
            patterns['head_shoulders'] = self._detect_head_shoulders(price_data)
            
            # 4. Inverse Head & Shoulders Pattern
            patterns['inverse_head_shoulders'] = self._detect_inverse_head_shoulders(price_data)
            
            # 5. Triangle Pattern
            patterns['triangle'] = self._detect_triangle(price_data)
            
            # 6. Wedge Pattern
            patterns['wedge'] = self._detect_wedge(price_data)
            
            # 7. Определяме overall pattern
            patterns['overall_pattern'] = self._determine_overall_pattern(patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Грешка при откриване на patterns: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _detect_double_top(self, price_data: pd.DataFrame) -> Dict:
        """Открива Double Top pattern (bearish reversal)"""
        try:
            if len(price_data) < 20:
                return {'detected': False, 'confidence': 0, 'reason': 'Недостатъчно данни'}
            
            highs = price_data['high'].values if 'high' in price_data.columns else price_data['High'].values
            lows = price_data['low'].values if 'low' in price_data.columns else price_data['Low'].values
            closes = price_data['close'].values if 'close' in price_data.columns else price_data['Close'].values
            
            # Намираме пикове в high цените
            peaks = self._find_peaks(highs, 'high')
            
            if len(peaks) < 2:
                return {'detected': False, 'confidence': 0, 'reason': 'Няма достатъчно пикове'}
            
            # Проверяваме последните 2 пика за double top
            peak1_idx, peak1_price = peaks[-2]
            peak2_idx, peak2_price = peaks[-1]
            
            # Проверяваме условията за double top
            price_diff = abs(peak2_price - peak1_price) / peak1_price
            time_diff = peak2_idx - peak1_idx
            
            if (price_diff < self.pattern_threshold and  # Цените са близки
                time_diff >= self.min_pattern_distance and  # Минимално време между пикове
                peak2_idx > peak1_idx):  # Вторият пик е по-нов
                
                # Проверяваме за neckline (support level между пикове)
                neckline = self._find_neckline(price_data, peak1_idx, peak2_idx)
                
                # Проверяваме за volume confirmation
                volume_confirmed = False
                if self.volume_confirmation and 'volume' in price_data.columns:
                    volume_confirmed = self._check_volume_confirmation(price_data, peak2_idx)
                
                # Проверяваме за bearish candle confirmation
                candle_confirmed = False
                if self.candle_confirmation:
                    candle_confirmed = self._check_bearish_candle(price_data, peak2_idx)
                
                # Изчисляваме confidence
                confidence = 60  # Base confidence
                if price_diff < 0.01:  # Цените са много близки
                    confidence += 15
                if volume_confirmed:
                    confidence += 10
                if candle_confirmed:
                    confidence += 15
                
                return {
                    'detected': True,
                    'confidence': min(95, confidence),
                    'reason': f'Double Top: два пика на {peak1_price:.2f} и {peak2_price:.2f}',
                    'peak1_price': peak1_price,
                    'peak2_price': peak2_price,
                    'neckline': neckline,
                    'volume_confirmed': volume_confirmed,
                    'candle_confirmed': candle_confirmed,
                    'pattern_strength': 'STRONG' if confidence > 80 else 'MEDIUM' if confidence > 65 else 'WEAK'
                }
            
            return {'detected': False, 'confidence': 0, 'reason': 'Не отговаря на double top критериите'}
            
        except Exception as e:
            logger.error(f"Грешка при откриване на double top: {e}")
            return {'detected': False, 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _detect_double_bottom(self, price_data: pd.DataFrame) -> Dict:
        """Открива Double Bottom pattern (bullish reversal)"""
        try:
            if len(price_data) < 20:
                return {'detected': False, 'confidence': 0, 'reason': 'Недостатъчно данни'}
            
            highs = price_data['high'].values if 'high' in price_data.columns else price_data['High'].values
            lows = price_data['low'].values if 'low' in price_data.columns else price_data['Low'].values
            closes = price_data['close'].values if 'close' in price_data.columns else price_data['Close'].values
            
            # Намираме дъна в low цените
            troughs = self._find_peaks(lows, 'low')
            
            if len(troughs) < 2:
                return {'detected': False, 'confidence': 0, 'reason': 'Няма достатъчно дъна'}
            
            # Проверяваме последните 2 дъна за double bottom
            trough1_idx, trough1_price = troughs[-2]
            trough2_idx, trough2_price = troughs[-1]
            
            # Проверяваме условията за double bottom
            price_diff = abs(trough2_price - trough1_price) / trough1_price
            time_diff = trough2_idx - trough1_idx
            
            if (price_diff < self.pattern_threshold and  # Цените са близки
                time_diff >= self.min_pattern_distance and  # Минимално време между дъна
                trough2_idx > trough1_idx):  # Второто дъно е по-ново
                
                # Проверяваме за neckline (resistance level между дъна)
                neckline = self._find_neckline(price_data, trough1_idx, trough2_idx, is_resistance=True)
                
                # Проверяваме за volume confirmation
                volume_confirmed = False
                if self.volume_confirmation and 'volume' in price_data.columns:
                    volume_confirmed = self._check_volume_confirmation(price_data, trough2_idx)
                
                # Проверяваме за bullish candle confirmation
                candle_confirmed = False
                if self.candle_confirmation:
                    candle_confirmed = self._check_bullish_candle(price_data, trough2_idx)
                
                # Изчисляваме confidence
                confidence = 60  # Base confidence
                if price_diff < 0.01:  # Цените са много близки
                    confidence += 15
                if volume_confirmed:
                    confidence += 10
                if candle_confirmed:
                    confidence += 15
                
                return {
                    'detected': True,
                    'confidence': min(95, confidence),
                    'reason': f'Double Bottom: две дъна на {trough1_price:.2f} и {trough2_price:.2f}',
                    'trough1_price': trough1_price,
                    'trough2_price': trough2_price,
                    'neckline': neckline,
                    'volume_confirmed': volume_confirmed,
                    'candle_confirmed': candle_confirmed,
                    'pattern_strength': 'STRONG' if confidence > 80 else 'MEDIUM' if confidence > 65 else 'WEAK'
                }
            
            return {'detected': False, 'confidence': 0, 'reason': 'Не отговаря на double bottom критериите'}
            
        except Exception as e:
            logger.error(f"Грешка при откриване на double bottom: {e}")
            return {'detected': False, 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _detect_head_shoulders(self, price_data: pd.DataFrame) -> Dict:
        """Открива Head & Shoulders pattern (bearish reversal)"""
        try:
            if len(price_data) < 30:
                return {'detected': False, 'confidence': 0, 'reason': 'Недостатъчно данни за H&S'}
            
            highs = price_data['high'].values if 'high' in price_data.columns else price_data['High'].values
            
            # Намираме пикове
            peaks = self._find_peaks(highs, 'high')
            
            if len(peaks) < 3:
                return {'detected': False, 'confidence': 0, 'reason': 'Няма достатъчно пикове за H&S'}
            
            # Проверяваме последните 3 пика
            left_shoulder_idx, left_shoulder_price = peaks[-3]
            head_idx, head_price = peaks[-2]
            right_shoulder_idx, right_shoulder_price = peaks[-1]
            
            # Проверяваме H&S условията
            if (head_price > left_shoulder_price and  # Главата е по-висока от лявото рамо
                head_price > right_shoulder_price and  # Главата е по-висока от дясното рамо
                abs(left_shoulder_price - right_shoulder_price) / left_shoulder_price < 0.03):  # Раменете са близки
                
                # Проверяваме за neckline
                neckline = self._find_neckline(price_data, left_shoulder_idx, right_shoulder_idx)
                
                confidence = 70  # Base confidence за H&S
                
                return {
                    'detected': True,
                    'confidence': confidence,
                    'reason': f'Head & Shoulders: глава на {head_price:.2f}, рамене на {left_shoulder_price:.2f}',
                    'head_price': head_price,
                    'left_shoulder_price': left_shoulder_price,
                    'right_shoulder_price': right_shoulder_price,
                    'neckline': neckline,
                    'pattern_strength': 'STRONG'
                }
            
            return {'detected': False, 'confidence': 0, 'reason': 'Не отговаря на H&S критериите'}
            
        except Exception as e:
            logger.error(f"Грешка при откриване на Head & Shoulders: {e}")
            return {'detected': False, 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _detect_inverse_head_shoulders(self, price_data: pd.DataFrame) -> Dict:
        """Открива Inverse Head & Shoulders pattern (bullish reversal)"""
        try:
            if len(price_data) < 30:
                return {'detected': False, 'confidence': 0, 'reason': 'Недостатъчно данни за IH&S'}
            
            lows = price_data['low'].values if 'low' in price_data.columns else price_data['Low'].values
            
            # Намираме дъна
            troughs = self._find_peaks(lows, 'low')
            
            if len(troughs) < 3:
                return {'detected': False, 'confidence': 0, 'reason': 'Няма достатъчно дъна за IH&S'}
            
            # Проверяваме последните 3 дъна
            left_shoulder_idx, left_shoulder_price = troughs[-3]
            head_idx, head_price = troughs[-2]
            right_shoulder_idx, right_shoulder_price = troughs[-1]
            
            # Проверяваме IH&S условията
            if (head_price < left_shoulder_price and  # Главата е по-ниска от лявото рамо
                head_price < right_shoulder_price and  # Главата е по-ниска от дясното рамо
                abs(left_shoulder_price - right_shoulder_price) / left_shoulder_price < 0.03):  # Раменете са близки
                
                # Проверяваме за neckline
                neckline = self._find_neckline(price_data, left_shoulder_idx, right_shoulder_idx, is_resistance=True)
                
                confidence = 70  # Base confidence за IH&S
                
                return {
                    'detected': True,
                    'confidence': confidence,
                    'reason': f'Inverse H&S: глава на {head_price:.2f}, рамене на {left_shoulder_price:.2f}',
                    'head_price': head_price,
                    'left_shoulder_price': left_shoulder_price,
                    'right_shoulder_price': right_shoulder_price,
                    'neckline': neckline,
                    'pattern_strength': 'STRONG'
                }
            
            return {'detected': False, 'confidence': 0, 'reason': 'Не отговаря на IH&S критериите'}
            
        except Exception as e:
            logger.error(f"Грешка при откриване на Inverse Head & Shoulders: {e}")
            return {'detected': False, 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _detect_triangle(self, price_data: pd.DataFrame) -> Dict:
        """Открива Triangle pattern"""
        try:
            if len(price_data) < 20:
                return {'detected': False, 'confidence': 0, 'reason': 'Недостатъчно данни за triangle'}
            
            highs = price_data['high'].values if 'high' in price_data.columns else price_data['High'].values
            lows = price_data['low'].values if 'low' in price_data.columns else price_data['Low'].values
            
            # Намираме пикове и дъна
            peaks = self._find_peaks(highs, 'high')
            troughs = self._find_peaks(lows, 'low')
            
            if len(peaks) < 2 or len(troughs) < 2:
                return {'detected': False, 'confidence': 0, 'reason': 'Няма достатъчно пикове/дъна за triangle'}
            
            # Проверяваме за triangle formation
            # Това е опростена версия - в реалността трябва да се проверява за сближаващи се линии
            
            return {'detected': False, 'confidence': 0, 'reason': 'Triangle detection не е имплементиран'}
            
        except Exception as e:
            logger.error(f"Грешка при откриване на triangle: {e}")
            return {'detected': False, 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _detect_wedge(self, price_data: pd.DataFrame) -> Dict:
        """Открива Wedge pattern"""
        try:
            if len(price_data) < 20:
                return {'detected': False, 'confidence': 0, 'reason': 'Недостатъчно данни за wedge'}
            
            # Опростена версия - не е пълно имплементирана
            return {'detected': False, 'confidence': 0, 'reason': 'Wedge detection не е имплементиран'}
            
        except Exception as e:
            logger.error(f"Грешка при откриване на wedge: {e}")
            return {'detected': False, 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _find_peaks(self, data: np.ndarray, peak_type: str) -> List[Tuple[int, float]]:
        """Намира пикове в данните"""
        try:
            peaks = []
            
            if peak_type == 'high':
                for i in range(1, len(data) - 1):
                    if data[i] > data[i-1] and data[i] > data[i+1]:
                        peaks.append((i, data[i]))
            else:  # low
                for i in range(1, len(data) - 1):
                    if data[i] < data[i-1] and data[i] < data[i+1]:
                        peaks.append((i, data[i]))
            
            return peaks
            
        except Exception as e:
            logger.error(f"Грешка при намиране на пикове: {e}")
            return []
    
    def _find_neckline(self, price_data: pd.DataFrame, idx1: int, idx2: int, is_resistance: bool = False) -> float:
        """Намира neckline между два пика/дъна"""
        try:
            if idx1 >= idx2:
                return 0.0
            
            # Взимаме данните между двата пика/дъна
            between_data = price_data.iloc[idx1:idx2+1]
            
            if is_resistance:
                # За resistance neckline, търсим най-високата точка
                high_col = 'high' if 'high' in between_data.columns else 'High'
                return float(between_data[high_col].max())
            else:
                # За support neckline, търсим най-ниската точка
                low_col = 'low' if 'low' in between_data.columns else 'Low'
                return float(between_data[low_col].min())
                
        except Exception as e:
            logger.error(f"Грешка при намиране на neckline: {e}")
            return 0.0
    
    def _check_volume_confirmation(self, price_data: pd.DataFrame, pattern_idx: int) -> bool:
        """Проверява volume confirmation за pattern"""
        try:
            if 'volume' not in price_data.columns:
                return False
            
            volumes = price_data['volume'].values
            
            if pattern_idx >= len(volumes):
                return False
            
            # Проверяваме дали обемът на pattern_idx е над средния за последните 10 периода
            lookback = min(10, pattern_idx)
            recent_volumes = volumes[pattern_idx-lookback:pattern_idx]
            avg_volume = np.mean(recent_volumes)
            
            return volumes[pattern_idx] > avg_volume * 1.2
            
        except Exception as e:
            logger.error(f"Грешка при проверка на volume confirmation: {e}")
            return False
    
    def _check_bearish_candle(self, price_data: pd.DataFrame, pattern_idx: int) -> bool:
        """Проверява за bearish candle confirmation"""
        try:
            if pattern_idx >= len(price_data):
                return False
            
            candle = price_data.iloc[pattern_idx]
            open_price = candle['open'] if 'open' in candle.index else candle['Open']
            close_price = candle['close'] if 'close' in candle.index else candle['Close']
            high_price = candle['high'] if 'high' in candle.index else candle['High']
            low_price = candle['low'] if 'low' in candle.index else candle['Low']
            
            # Bearish candle: close < open
            if close_price < open_price:
                # Проверяваме за long upper shadow (resistance)
                upper_shadow = high_price - max(open_price, close_price)
                body_size = abs(close_price - open_price)
                
                return upper_shadow > body_size * 0.5
            
            return False
            
        except Exception as e:
            logger.error(f"Грешка при проверка на bearish candle: {e}")
            return False
    
    def _check_bullish_candle(self, price_data: pd.DataFrame, pattern_idx: int) -> bool:
        """Проверява за bullish candle confirmation"""
        try:
            if pattern_idx >= len(price_data):
                return False
            
            candle = price_data.iloc[pattern_idx]
            open_price = candle['open'] if 'open' in candle.index else candle['Open']
            close_price = candle['close'] if 'close' in candle.index else candle['Close']
            high_price = candle['high'] if 'high' in candle.index else candle['High']
            low_price = candle['low'] if 'low' in candle.index else candle['Low']
            
            # Bullish candle: close > open
            if close_price > open_price:
                # Проверяваме за long lower shadow (support)
                lower_shadow = min(open_price, close_price) - low_price
                body_size = abs(close_price - open_price)
                
                return lower_shadow > body_size * 0.5
            
            return False
            
        except Exception as e:
            logger.error(f"Грешка при проверка на bullish candle: {e}")
            return False
    
    def _determine_overall_pattern(self, patterns: Dict) -> str:
        """Определя overall pattern от всички открити"""
        try:
            bearish_count = 0
            bullish_count = 0
            
            # Броим bearish patterns
            if patterns.get('double_top', {}).get('detected', False):
                bearish_count += 1
            if patterns.get('head_shoulders', {}).get('detected', False):
                bearish_count += 1
            
            # Броим bullish patterns
            if patterns.get('double_bottom', {}).get('detected', False):
                bullish_count += 1
            if patterns.get('inverse_head_shoulders', {}).get('detected', False):
                bullish_count += 1
            
            # Определяме overall pattern
            if bearish_count >= 2:
                return 'STRONG_BEARISH'
            elif bearish_count == 1:
                return 'BEARISH'
            elif bullish_count >= 2:
                return 'STRONG_BULLISH'
            elif bullish_count == 1:
                return 'BULLISH'
            else:
                return 'NONE'
                
        except Exception as e:
            logger.error(f"Грешка при определяне на overall pattern: {e}")
            return 'NONE'
    
    def get_pattern_trading_signals(self, patterns: Dict) -> Dict:
        """Генерира trading сигнали базирани на patterns"""
        try:
            overall_pattern = patterns.get('overall_pattern', 'NONE')
            
            if overall_pattern == 'STRONG_BEARISH':
                return {
                    'signal': 'STRONG_SELL',
                    'confidence': 80,
                    'reason': 'Множествен bearish patterns - силна bearish сигнал',
                    'risk_level': 'HIGH'
                }
            elif overall_pattern == 'BEARISH':
                return {
                    'signal': 'SELL',
                    'confidence': 65,
                    'reason': 'Bearish pattern - умерена bearish сигнал',
                    'risk_level': 'MEDIUM'
                }
            elif overall_pattern == 'STRONG_BULLISH':
                return {
                    'signal': 'STRONG_BUY',
                    'confidence': 80,
                    'reason': 'Множествен bullish patterns - силна bullish сигнал',
                    'risk_level': 'HIGH'
                }
            elif overall_pattern == 'BULLISH':
                return {
                    'signal': 'BUY',
                    'confidence': 65,
                    'reason': 'Bullish pattern - умерена bullish сигнал',
                    'risk_level': 'MEDIUM'
                }
            else:
                return {
                    'signal': 'HOLD',
                    'confidence': 50,
                    'reason': 'Няма ясни patterns - няма сигнал',
                    'risk_level': 'LOW'
                }
                
        except Exception as e:
            logger.error(f"Грешка при генериране на pattern trading сигнали: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': f'Грешка: {e}',
                'risk_level': 'UNKNOWN'
            }

if __name__ == "__main__":
    print("Price Action Patterns анализатор за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
