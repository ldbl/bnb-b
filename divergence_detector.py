"""
Divergence Detection Module
Открива bullish/bearish divergence между цената и индикаторите
Базирано на ideas файла - прост и ефективен метод
"""

import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DivergenceDetector:
    """Открива divergence между цената и технически индикатори"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_peak_distance = config.get('divergence', {}).get('min_peak_distance', 5)
        self.min_peak_prominence = config.get('divergence', {}).get('min_peak_prominence', 0.02)
        self.lookback_periods = config.get('divergence', {}).get('lookback_periods', 20)
        
        logger.info("Divergence Detector инициализиран")
    
    def detect_all_divergences(self, price_data: pd.DataFrame, indicators_data: Dict) -> Dict:
        """
        Открива всички видове divergence
        
        Args:
            price_data: DataFrame с OHLCV данни
            indicators_data: Dict с RSI, MACD, и други индикатори
            
        Returns:
            Dict с откритите divergence
        """
        try:
            divergences = {
                'rsi_divergence': None,
                'macd_divergence': None,
                'price_volume_divergence': None,
                'overall_divergence': 'NONE'
            }
            
            # 1. RSI Divergence
            if 'rsi' in indicators_data:
                rsi_values = indicators_data['rsi'].get('rsi_values', [])
                if len(rsi_values) > 0:
                    divergences['rsi_divergence'] = self._detect_rsi_divergence(
                        price_data, rsi_values
                    )
            
            # 2. MACD Divergence
            if 'macd' in indicators_data:
                macd_values = indicators_data['macd'].get('macd_values', [])
                if len(macd_values) > 0:
                    divergences['macd_divergence'] = self._detect_macd_divergence(
                        price_data, macd_values
                    )
            
            # 3. Price vs Volume Divergence
            if 'volume' in price_data.columns:
                divergences['price_volume_divergence'] = self._detect_price_volume_divergence(
                    price_data
                )
            
            # 4. Определяме overall divergence
            divergences['overall_divergence'] = self._determine_overall_divergence(divergences)
            
            return divergences
            
        except Exception as e:
            logger.error(f"Грешка при откриване на divergence: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _detect_rsi_divergence(self, price_data: pd.DataFrame, rsi_values: List[float]) -> Dict:
        """Открива RSI divergence"""
        try:
            if len(price_data) < self.lookback_periods or len(rsi_values) < self.lookback_periods:
                return {'type': 'NONE', 'confidence': 0, 'reason': 'Недостатъчно данни'}
            
            # Извличаме последните lookback_periods данни
            recent_prices = price_data['close'].tail(self.lookback_periods).values if 'close' in price_data.columns else price_data['Close'].tail(self.lookback_periods).values
            recent_rsi = rsi_values[-self.lookback_periods:]
            
            # Намираме пикове в цената
            price_peaks = self._find_peaks(recent_prices, 'high')
            price_troughs = self._find_peaks(recent_prices, 'low')
            
            # Намираме пикове в RSI
            rsi_peaks = self._find_peaks(recent_rsi, 'high')
            rsi_troughs = self._find_peaks(recent_rsi, 'low')
            
            # Проверяваме за bearish divergence (цена нов връх, RSI по-нисък връх)
            bearish_div = self._check_bearish_divergence(price_peaks, rsi_peaks, recent_prices, recent_rsi, 'rsi')
            
            # Проверяваме за bullish divergence (цена ново дъно, RSI по-високо дъно)
            bullish_div = self._check_bullish_divergence(price_troughs, rsi_troughs, recent_prices, recent_rsi, 'rsi')
            
            if bearish_div['detected']:
                return {
                    'type': 'BEARISH',
                    'confidence': bearish_div['confidence'],
                    'reason': 'Цена прави нов връх, но RSI не (bearish divergence)',
                    'price_peak': bearish_div['price_peak'],
                    'rsi_peak': bearish_div['rsi_peak']
                }
            elif bullish_div['detected']:
                return {
                    'type': 'BULLISH',
                    'confidence': bullish_div['confidence'],
                    'reason': 'Цена прави ново дъно, но RSI не (bullish divergence)',
                    'price_trough': bullish_div['price_trough'],
                    'rsi_trough': bullish_div['rsi_trough']
                }
            else:
                return {'type': 'NONE', 'confidence': 0, 'reason': 'Няма divergence'}
                
        except Exception as e:
            logger.error(f"Грешка при RSI divergence анализ: {e}")
            return {'type': 'NONE', 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _detect_macd_divergence(self, price_data: pd.DataFrame, macd_values: List[float]) -> Dict:
        """Открива MACD divergence"""
        try:
            if len(price_data) < self.lookback_periods or len(macd_values) < self.lookback_periods:
                return {'type': 'NONE', 'confidence': 0, 'reason': 'Недостатъчно данни'}
            
            # Извличаме последните lookback_periods данни
            recent_prices = price_data['close'].tail(self.lookback_periods).values if 'close' in price_data.columns else price_data['Close'].tail(self.lookback_periods).values
            recent_macd = macd_values[-self.lookback_periods:]
            
            # Намираме пикове в цената
            price_peaks = self._find_peaks(recent_prices, 'high')
            price_troughs = self._find_peaks(recent_prices, 'low')
            
            # Намираме пикове в MACD
            macd_peaks = self._find_peaks(recent_macd, 'high')
            macd_troughs = self._find_peaks(recent_macd, 'low')
            
            # Проверяваме за bearish divergence
            bearish_div = self._check_bearish_divergence(price_peaks, macd_peaks, recent_prices, recent_macd, 'macd')
            
            # Проверяваме за bullish divergence
            bullish_div = self._check_bullish_divergence(price_troughs, macd_troughs, recent_prices, recent_macd, 'macd')
            
            if bearish_div['detected']:
                return {
                    'type': 'BEARISH',
                    'confidence': bearish_div['confidence'],
                    'reason': 'Цена прави нов връх, но MACD не (bearish divergence)',
                    'price_peak': bearish_div['price_peak'],
                    'macd_peak': bearish_div['indicator_peak']
                }
            elif bullish_div['detected']:
                return {
                    'type': 'BULLISH',
                    'confidence': bullish_div['confidence'],
                    'reason': 'Цена прави ново дъно, но MACD не (bullish divergence)',
                    'price_trough': bullish_div['price_trough'],
                    'macd_trough': bullish_div['indicator_trough']
                }
            else:
                return {'type': 'NONE', 'confidence': 0, 'reason': 'Няма divergence'}
                
        except Exception as e:
            logger.error(f"Грешка при MACD divergence анализ: {e}")
            return {'type': 'NONE', 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _detect_price_volume_divergence(self, price_data: pd.DataFrame) -> Dict:
        """Открива divergence между цената и обема"""
        try:
            if len(price_data) < self.lookback_periods:
                return {'type': 'NONE', 'confidence': 0, 'reason': 'Недостатъчно данни'}
            
            # Извличаме последните lookback_periods данни
            recent_prices = price_data['close'].tail(self.lookback_periods).values if 'close' in price_data.columns else price_data['Close'].tail(self.lookback_periods).values
            recent_volumes = price_data['volume'].tail(self.lookback_periods).values
            
            # Намираме пикове в цената
            price_peaks = self._find_peaks(recent_prices, 'high')
            price_troughs = self._find_peaks(recent_prices, 'low')
            
            # Намираме пикове в обема
            volume_peaks = self._find_peaks(recent_volumes, 'high')
            volume_troughs = self._find_peaks(recent_volumes, 'low')
            
            # Проверяваме за bearish divergence (цена нов връх, обем по-нисък)
            bearish_div = self._check_bearish_divergence(price_peaks, volume_peaks, recent_prices, recent_volumes)
            
            # Проверяваме за bullish divergence (цена ново дъно, обем по-висок)
            bullish_div = self._check_bullish_divergence(price_troughs, volume_troughs, recent_prices, recent_volumes)
            
            if bearish_div['detected']:
                return {
                    'type': 'BEARISH',
                    'confidence': bearish_div['confidence'],
                    'reason': 'Цена прави нов връх, но обемът не (bearish divergence)',
                    'price_peak': bearish_div['price_peak'],
                    'volume_peak': bearish_div['indicator_peak']
                }
            elif bullish_div['detected']:
                return {
                    'type': 'BULLISH',
                    'confidence': bullish_div['confidence'],
                    'reason': 'Цена прави ново дъно, но обемът не (bullish divergence)',
                    'price_trough': bullish_div['price_trough'],
                    'volume_trough': bullish_div['indicator_trough']
                }
            else:
                return {'type': 'NONE', 'confidence': 0, 'reason': 'Няма divergence'}
                
        except Exception as e:
            logger.error(f"Грешка при Price-Volume divergence анализ: {e}")
            return {'type': 'NONE', 'confidence': 0, 'reason': f'Грешка: {e}'}
    
    def _find_peaks(self, data: np.ndarray, peak_type: str) -> List[Tuple[int, float]]:
        """Намира пикове в данните използвайки scipy.signal.find_peaks"""
        try:
            # Конвертираме в numpy array ако не е
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            if peak_type == 'high':
                peaks, properties = find_peaks(
                    data, 
                    distance=self.min_peak_distance,
                    prominence=self.min_peak_prominence * np.max(data)
                )
            else:  # low
                peaks, properties = find_peaks(
                    -data,  # Инвертираме за да намерим дъна
                    distance=self.min_peak_distance,
                    prominence=self.min_peak_prominence * np.max(data)
                )
            
            # Връщаме (индекс, стойност) двойки
            return [(int(peak), float(data[peak])) for peak in peaks]
            
        except Exception as e:
            logger.error(f"Грешка при намиране на пикове: {e}")
            return []
    
    def _check_bearish_divergence(self, price_peaks: List[Tuple[int, float]], 
                                 indicator_peaks: List[Tuple[int, float]],
                                 prices: np.ndarray, indicators: np.ndarray, 
                                 indicator_type: str = 'generic') -> Dict:
        """Проверява за bearish divergence"""
        try:
            if len(price_peaks) < 2 or len(indicator_peaks) < 2:
                return {'detected': False, 'confidence': 0}
            
            # Взимаме последните 2 пика
            price_peak1, price_peak2 = price_peaks[-2], price_peaks[-1]
            indicator_peak1, indicator_peak2 = indicator_peaks[-2], indicator_peaks[-1]
            
            # Проверяваме за bearish divergence
            # Цена прави нов връх (price_peak2 > price_peak1)
            # Но индикаторът не (indicator_peak2 < indicator_peak1)
            if (price_peak2[1] > price_peak1[1] and 
                indicator_peak2[1] < indicator_peak1[1]):
                
                # Изчисляваме confidence базирано на силата на divergence
                price_change = (price_peak2[1] - price_peak1[1]) / price_peak1[1]
                indicator_change = abs(indicator_peak2[1] - indicator_peak1[1]) / abs(indicator_peak1[1])
                
                confidence = min(95, 50 + (price_change + indicator_change) * 100)
                
                # Връщаме правилните ключове според типа на индикатора
                result = {
                    'detected': True,
                    'confidence': confidence,
                    'price_peak': price_peak2[1]
                }
                
                if indicator_type == 'rsi':
                    result['rsi_peak'] = indicator_peak2[1]
                elif indicator_type == 'macd':
                    result['macd_peak'] = indicator_peak2[1]
                else:
                    result['indicator_peak'] = indicator_peak2[1]
                
                return result
            
            return {'detected': False, 'confidence': 0}
            
        except Exception as e:
            logger.error(f"Грешка при проверка за bearish divergence: {e}")
            return {'detected': False, 'confidence': 0}
    
    def _check_bullish_divergence(self, price_troughs: List[Tuple[int, float]], 
                                 indicator_troughs: List[Tuple[int, float]],
                                 prices: np.ndarray, indicators: np.ndarray,
                                 indicator_type: str = 'generic') -> Dict:
        """Проверява за bullish divergence"""
        try:
            if len(price_troughs) < 2 or len(indicator_troughs) < 2:
                return {'detected': False, 'confidence': 0}
            
            # Взимаме последните 2 дъна
            price_trough1, price_trough2 = price_troughs[-2], price_troughs[-1]
            indicator_trough1, indicator_trough2 = indicator_troughs[-2], indicator_troughs[-1]
            
            # Проверяваме за bullish divergence
            # Цена прави ново дъно (price_trough2 < price_trough1)
            # Но индикаторът не (indicator_trough2 > indicator_trough1)
            if (price_trough2[1] < price_trough1[1] and 
                indicator_trough2[1] > indicator_trough1[1]):
                
                # Изчисляваме confidence базирано на силата на divergence
                price_change = abs(price_trough2[1] - price_trough1[1]) / abs(price_trough1[1])
                indicator_change = (indicator_trough2[1] - indicator_trough1[1]) / abs(indicator_trough1[1])
                
                confidence = min(95, 50 + (price_change + indicator_change) * 100)
                
                # Връщаме правилните ключове според типа на индикатора
                result = {
                    'detected': True,
                    'confidence': confidence,
                    'price_trough': price_trough2[1]
                }
                
                if indicator_type == 'rsi':
                    result['rsi_trough'] = indicator_trough2[1]
                elif indicator_type == 'macd':
                    result['macd_trough'] = indicator_trough2[1]
                else:
                    result['indicator_trough'] = indicator_trough2[1]
                
                return result
            
            return {'detected': False, 'confidence': 0}
            
        except Exception as e:
            logger.error(f"Грешка при проверка за bullish divergence: {e}")
            return {'detected': False, 'confidence': 0}
    
    def _determine_overall_divergence(self, divergences: Dict) -> str:
        """Определя overall divergence от всички открити"""
        try:
            bearish_count = 0
            bullish_count = 0
            
            # Броим bearish divergence
            for key, div in divergences.items():
                if key != 'overall_divergence' and div and div.get('type') == 'BEARISH':
                    bearish_count += 1
                elif key != 'overall_divergence' and div and div.get('type') == 'BULLISH':
                    bullish_count += 1
            
            # Определяме overall divergence
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
            logger.error(f"Грешка при определяне на overall divergence: {e}")
            return 'NONE'
    
    def get_divergence_trading_signals(self, divergences: Dict) -> Dict:
        """Генерира trading сигнали базирани на divergence"""
        try:
            overall_div = divergences.get('overall_divergence', 'NONE')
            
            if overall_div == 'STRONG_BEARISH':
                return {
                    'signal': 'STRONG_SELL',
                    'confidence': 85,
                    'reason': 'Множествен bearish divergence - силна bearish сигнал',
                    'risk_level': 'HIGH'
                }
            elif overall_div == 'BEARISH':
                return {
                    'signal': 'SELL',
                    'confidence': 70,
                    'reason': 'Bearish divergence - умерена bearish сигнал',
                    'risk_level': 'MEDIUM'
                }
            elif overall_div == 'STRONG_BULLISH':
                return {
                    'signal': 'STRONG_BUY',
                    'confidence': 85,
                    'reason': 'Множествен bullish divergence - силна bullish сигнал',
                    'risk_level': 'HIGH'
                }
            elif overall_div == 'BULLISH':
                return {
                    'signal': 'BUY',
                    'confidence': 70,
                    'reason': 'Bullish divergence - умерена bullish сигнал',
                    'risk_level': 'MEDIUM'
                }
            else:
                return {
                    'signal': 'HOLD',
                    'confidence': 50,
                    'reason': 'Няма divergence - няма ясен сигнал',
                    'risk_level': 'LOW'
                }
                
        except Exception as e:
            logger.error(f"Грешка при генериране на divergence trading сигнали: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': f'Грешка: {e}',
                'risk_level': 'UNKNOWN'
            }

if __name__ == "__main__":
    print("Divergence Detector модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
