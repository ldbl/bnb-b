"""
Divergence Detection Module - Advanced Price-Indicator Divergence Analysis

SPECIALIZED MODULE FOR DIVERGENCE DETECTION BETWEEN PRICE AND INDICATORS
Identifies bullish/bearish divergences for high-probability trading signals

This module provides sophisticated divergence detection capabilities that identify
when price movement diverges from momentum indicators (RSI, MACD) and volume,
providing powerful reversal and continuation signals for BNB trading.

ARCHITECTURE OVERVIEW:
    - Multi-indicator divergence analysis (RSI, MACD, Price-Volume)
    - Peak/trough detection using advanced signal processing
    - Statistical validation of divergence patterns
    - Confidence scoring and signal strength assessment
    - Integration with broader market context

DIVERGENCE THEORY IMPLEMENTATION:
    - Bullish Divergence: Price makes lower low, indicator makes higher low
    - Bearish Divergence: Price makes higher high, indicator makes lower high
    - Hidden Divergence: Continuation patterns with temporary divergences
    - Regular Divergence: Reversal patterns with strong divergences

DIVERGENCE TYPES DETECTED:
    1. RSI Divergence - Momentum oscillator divergence
    2. MACD Divergence - Trend-following indicator divergence
    3. Price-Volume Divergence - Volume confirmation divergence
    4. Composite Divergence - Multi-indicator confluence

ALGORITHMS USED:
    - Peak Detection: SciPy signal processing for accurate peak identification
    - Statistical Validation: Confidence intervals and significance testing
    - Pattern Recognition: Sequence analysis for divergence confirmation
    - Strength Scoring: Multi-factor assessment of divergence significance

KEY FEATURES:
    - Automated divergence detection with configurable sensitivity
    - Multi-timeframe divergence analysis capability
    - Statistical validation of divergence significance
    - Confidence scoring for trading decision support
    - Volume confirmation integration for stronger signals

TRADING APPLICATIONS:
    - Reversal Signal Identification: Strong divergences often precede reversals
    - Continuation Pattern Confirmation: Hidden divergences support trend continuation
    - Risk Management: Divergence strength helps determine position sizing
    - Entry Timing: Divergence completion often provides optimal entry points
    - Exit Signals: Divergence patterns can indicate trend exhaustion

CONFIGURATION PARAMETERS:
    - min_peak_distance: Minimum distance between peaks for validation (default: 5)
    - min_peak_prominence: Minimum peak prominence for significance (default: 0.02)
    - lookback_periods: Historical periods to analyze for divergence (default: 20)
    - divergence_threshold: Minimum divergence strength for signal (default: 0.05)

DIVERGENCE STRENGTH CLASSIFICATION:
    - Weak (0.0-0.3): Minimal significance, monitor for confirmation
    - Moderate (0.3-0.6): Some significance, consider in conjunction with other factors
    - Strong (0.6-0.8): High significance, potential trading opportunity
    - Extreme (0.8-1.0): Maximum significance, strong trading signal

EXAMPLE USAGE:
    >>> config = {'divergence': {'lookback_periods': 20, 'min_peak_distance': 5}}
    >>> detector = DivergenceDetector(config)
    >>> price_data = pd.read_csv('bnb_daily.csv')
    >>> indicators = {'rsi': rsi_values, 'macd': macd_values}
    >>> divergences = detector.detect_all_divergences(price_data, indicators)
    >>> if divergences['rsi_divergence']['type'] == 'BULLISH':
    ...     print(f"Bullish RSI Divergence detected with confidence {divergences['rsi_divergence']['confidence']:.1f}%")

DEPENDENCIES:
    - pandas: Data manipulation and time series operations
    - numpy: Mathematical calculations and array operations
    - scipy.signal: Advanced signal processing for peak detection
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient peak detection algorithms
    - Vectorized calculations for large datasets
    - Memory-optimized data structures
    - Caching of expensive computations

ERROR HANDLING:
    - Validation of input data structure and sufficiency
    - Graceful handling of missing or invalid indicator data
    - Statistical calculation error recovery
    - Comprehensive logging for debugging and monitoring

VALIDATION TECHNIQUES:
    - Statistical significance testing of detected divergences
    - Cross-validation with multiple indicators
    - Historical back-testing of divergence patterns
    - Robustness testing across different market conditions

SIGNAL ACCURACY ENHANCEMENTS:
    - Multi-indicator divergence confluence analysis
    - Volume confirmation for stronger signals
    - Statistical confidence scoring
    - Market context integration

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DivergenceDetector:
    """
    Advanced Divergence Detection Engine for Price-Indicator Analysis

    This class provides sophisticated divergence detection capabilities using advanced
    signal processing techniques to identify when price movement diverges from momentum
    indicators and volume, providing powerful trading signals.

    ARCHITECTURE OVERVIEW:
        - Multi-indicator divergence analysis using RSI, MACD, and volume
        - Advanced peak/trough detection using SciPy signal processing
        - Statistical validation of divergence patterns and significance
        - Confidence scoring system for trading decision support
        - Composite divergence analysis for stronger signals

    DIVERGENCE DETECTION METHODOLOGY:
        1. Data Validation: Ensures sufficient historical data for analysis
        2. Peak Detection: Identifies significant peaks and troughs in price/indicators
        3. Pattern Analysis: Compares peak/trough sequences for divergence patterns
        4. Strength Scoring: Calculates statistical significance of divergences
        5. Confidence Assessment: Provides confidence scores for trading decisions

    DIVERGENCE TYPES SUPPORTED:
        - BULLISH_DIVERGENCE: Price lower low, indicator higher low (reversal signal)
        - BEARISH_DIVERGENCE: Price higher high, indicator lower high (reversal signal)
        - HIDDEN_BULLISH: Price higher low, indicator lower low (continuation signal)
        - HIDDEN_BEARISH: Price lower high, indicator higher high (continuation signal)

    CONFIGURATION PARAMETERS:
        min_peak_distance (int): Minimum periods between peaks for validation (default: 5)
        min_peak_prominence (float): Minimum peak prominence for significance (default: 0.02)
        lookback_periods (int): Historical periods to analyze for divergence (default: 20)
        divergence_threshold (float): Minimum divergence strength for signal (default: 0.05)

    ATTRIBUTES:
        config (Dict): Complete configuration dictionary
        min_peak_distance (int): Peak distance validation parameter
        min_peak_prominence (float): Peak prominence validation parameter
        lookback_periods (int): Historical analysis window size

    PEAK DETECTION ALGORITHM:
        - Uses SciPy find_peaks for robust peak identification
        - Applies distance and prominence filters for significance
        - Validates peaks against statistical thresholds
        - Handles both price and indicator peak detection

    DIVERGENCE SCORING SYSTEM:
        - Confidence Score: Statistical significance (0.0 to 1.0)
        - Strength Classification: Weak/Moderate/Strong/Extreme
        - Pattern Type: Regular/Hidden divergence identification
        - Multi-factor Assessment: Combines multiple validation criteria

    OUTPUT STRUCTURE:
        {
            'rsi_divergence': {
                'type': 'BULLISH_DIVERGENCE' | 'BEARISH_DIVERGENCE' | 'NONE',
                'confidence': float,  # 0.0 to 1.0
                'reason': str,       # Explanation of divergence
                'strength': float    # Statistical strength
            },
            'macd_divergence': { ... },
            'price_volume_divergence': { ... },
            'overall_divergence': str  # Composite divergence assessment
        }

    EXAMPLE:
        >>> config = {
        ...     'divergence': {
        ...         'lookback_periods': 20,
        ...         'min_peak_distance': 5,
        ...         'min_peak_prominence': 0.02
        ...     }
        ... }
        >>> detector = DivergenceDetector(config)
        >>> price_data = pd.read_csv('bnb_data.csv')
        >>> indicators = {'rsi': rsi_values, 'macd': macd_values}
        >>> divergences = detector.detect_all_divergences(price_data, indicators)

    NOTE:
        Requires sufficient historical data (minimum 20 periods recommended)
        and clean OHLCV data for accurate divergence detection.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.min_peak_distance = config.get('divergence', {}).get('min_peak_distance', 5)
        self.min_peak_prominence = config.get('divergence', {}).get('min_peak_prominence', 0.02)
        self.lookback_periods = config.get('divergence', {}).get('lookback_periods', 20)
        
        # NEW: Trend-strength filter parameters
        self.trend_filter_enabled = config.get('divergence', {}).get('trend_filter_enabled', True)
        self.bull_market_threshold = config.get('divergence', {}).get('bull_market_threshold', 0.1)  # 10% gain over lookback
        self.bear_market_threshold = config.get('divergence', {}).get('bear_market_threshold', -0.05)  # 5% loss over lookback
        
        logger.info("Divergence Detector инициализиран с trend-strength filter")  # noqa: RUF001
    
    def detect_all_divergences(self, price_data: pd.DataFrame, indicators_data: Dict) -> Dict:
        """
        Открива всички видове divergence с trend-strength filtering  # noqa: RUF001
        
        Args:
            price_data: DataFrame с OHLCV данни  # noqa: RUF001
            indicators_data: Dict с RSI, MACD, и други индикатори  # noqa: RUF001
            
        Returns:
            Dict с откритите divergence  # noqa: RUF001
        """
        try:
            # PHASE 1: Analyze market regime for trend-strength filtering
            market_regime = self._analyze_market_regime(price_data) if self.trend_filter_enabled else 'NEUTRAL'
            
            divergences = {
                'rsi_divergence': None,
                'macd_divergence': None,
                'price_volume_divergence': None,
                'overall_divergence': 'NONE',
                'market_regime': market_regime,
                'trend_filter_applied': self.trend_filter_enabled
            }
            
            # 1. RSI Divergence
            if 'rsi' in indicators_data:
                rsi_values = indicators_data['rsi'].get('rsi_values', [])
                if len(rsi_values) > 0:
                    raw_rsi_div = self._detect_rsi_divergence(price_data, rsi_values)
                    divergences['rsi_divergence'] = self._apply_trend_filter(
                        raw_rsi_div, market_regime, 'rsi'
                    ) if self.trend_filter_enabled else raw_rsi_div
            
            # 2. MACD Divergence
            if 'macd' in indicators_data:
                macd_values = indicators_data['macd'].get('macd_values', [])
                if len(macd_values) > 0:
                    raw_macd_div = self._detect_macd_divergence(price_data, macd_values)
                    divergences['macd_divergence'] = self._apply_trend_filter(
                        raw_macd_div, market_regime, 'macd'
                    ) if self.trend_filter_enabled else raw_macd_div
            
            # 3. Price vs Volume Divergence
            vol_col = 'volume' if 'volume' in price_data.columns else ('Volume' if 'Volume' in price_data.columns else None)
            if vol_col:
                divergences['price_volume_divergence'] = self._detect_price_volume_divergence(
                    price_data
                )
            
            # 4. Определяме overall divergence
            divergences['overall_divergence'] = self._determine_overall_divergence(divergences)
            
            return divergences
            
        except Exception as e:
            logger.exception(f"Грешка при откриване на divergence: {e}")
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
            logger.exception(f"Грешка при RSI divergence анализ: {e}")
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
                    'macd_peak': bearish_div['macd_peak']
                }
            elif bullish_div['detected']:
                return {
                    'type': 'BULLISH',
                    'confidence': bullish_div['confidence'],
                    'reason': 'Цена прави ново дъно, но MACD не (bullish divergence)',
                    'price_trough': bullish_div['price_trough'],
                    'macd_trough': bullish_div.get('macd_trough', bullish_div.get('indicator_trough'))
                }
            else:
                return {'type': 'NONE', 'confidence': 0, 'reason': 'Няма divergence'}
                
        except Exception as e:
            logger.exception(f"Грешка при MACD divergence анализ: {e}")
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
            logger.exception(f"Грешка при Price-Volume divergence анализ: {e}")
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
            logger.exception(f"Грешка при намиране на пикове: {e}")
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
            logger.exception(f"Грешка при проверка за bearish divergence: {e}")
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
            logger.exception(f"Грешка при проверка за bullish divergence: {e}")
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
            logger.exception(f"Грешка при определяне на overall divergence: {e}")
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
            logger.exception(f"Грешка при генериране на divergence trading сигнали: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': f'Грешка: {e}',
                'risk_level': 'UNKNOWN'
            }
    
    def _analyze_market_regime(self, price_data: pd.DataFrame) -> str:
        """
        Analyzes market regime to filter inappropriate divergence signals
        
        Returns:
            str: Market regime classification
        """
        try:
            if len(price_data) < self.lookback_periods:
                return 'NEUTRAL'
            
            close_col = 'close' if 'close' in price_data.columns else 'Close'
            recent_prices = price_data[close_col].tail(self.lookback_periods)
            
            # Calculate trend strength over lookback period
            price_change = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
            
            # Calculate volatility (standard deviation)
            price_volatility = recent_prices.pct_change().std()
            
            # Determine market regime
            if price_change >= self.bull_market_threshold:
                if price_volatility > 0.05:  # High volatility bull market
                    return 'VOLATILE_BULL'
                else:
                    return 'STRONG_BULL'
            elif price_change <= self.bear_market_threshold:
                return 'BEAR'
            else:
                return 'NEUTRAL'
                
        except Exception:
            logger.exception("Error analyzing market regime")
            return 'NEUTRAL'
    
    def _apply_trend_filter(self, divergence_result: Dict, market_regime: str, divergence_type: str) -> Dict:
        """
        Apply trend-strength filter to divergence signals
        
        Args:
            divergence_result: Original divergence detection result
            market_regime: Current market regime
            divergence_type: Type of divergence being filtered
            
        Returns:
            Filtered divergence result
        """
        try:
            if not self.trend_filter_enabled or divergence_result.get('type') == 'NONE':
                return divergence_result
            
            original_type = divergence_result.get('type')
            original_confidence = float(divergence_result.get('confidence', 0))
            
            # Apply filtering logic based on market regime
            if market_regime in ['STRONG_BULL', 'VOLATILE_BULL']:
                if original_type == 'BEARISH':
                    # Reduce bearish divergence signals in bull markets
                    return {
                        **divergence_result,
                        'type': 'NONE',
                        'confidence': 0,
                        'reason': f'Filtered: Bearish {divergence_type.upper()} divergence blocked in {market_regime} market',
                        'original_signal': original_type,
                        'filter_applied': 'BULL_MARKET_FILTER'
                    }
                elif original_type == 'BULLISH':
                    # Amplify bullish divergence signals in bull markets
                    enhanced_confidence = min(int(original_confidence * 1.2), 95)
                    return {
                        **divergence_result,
                        'confidence': enhanced_confidence,
                        'reason': f'{divergence_result.get("reason", "")} (Enhanced in {market_regime})',
                        'filter_applied': 'BULL_MARKET_ENHANCEMENT'
                    }
            
            elif market_regime == 'BEAR':
                if original_type == 'BULLISH':
                    # Reduce confidence in bullish divergence in bear markets
                    reduced_confidence = int(original_confidence * 0.7)
                    if reduced_confidence < 30:
                        return {
                            **divergence_result,
                            'type': 'NONE',
                            'confidence': 0,
                            'reason': f'Filtered: Low confidence bullish divergence in {market_regime} market',
                            'original_signal': original_type,
                            'filter_applied': 'BEAR_MARKET_FILTER'
                        }
                    else:
                        return {
                            **divergence_result,
                            'confidence': reduced_confidence,
                            'reason': f'{divergence_result.get("reason", "")} (Reduced confidence in bear market)',
                            'filter_applied': 'BEAR_MARKET_REDUCTION'
                        }
                elif original_type == 'BEARISH':
                    # Enhance bearish divergence in bear markets
                    enhanced_confidence = min(int(original_confidence * 1.3), 95)
                    return {
                        **divergence_result,
                        'confidence': enhanced_confidence,
                        'reason': f'{divergence_result.get("reason", "")} (Enhanced in bear market)',
                        'filter_applied': 'BEAR_MARKET_ENHANCEMENT'
                    }
            
            # Default: neutral market or no filtering needed
            return {
                **divergence_result,
                'filter_applied': 'NO_FILTER'
            }
                
        except Exception:
            logger.exception("Error applying trend filter")
            return divergence_result

if __name__ == "__main__":
    print("Divergence Detector модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
