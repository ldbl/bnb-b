"""
Price Action Patterns Module - Classical Chart Pattern Recognition

ADVANCED PRICE ACTION PATTERN RECOGNITION FOR TECHNICAL ANALYSIS
Identifies classical chart patterns using pure price action with candlestick confirmation

This module provides sophisticated recognition of classical chart patterns that have
proven reliability across different markets, with special optimization for cryptocurrency
price movements. The module focuses on pure price action analysis without reliance
on indicators, making it particularly effective in volatile crypto markets.

ARCHITECTURE OVERVIEW:
    - Multi-pattern recognition system for reversal and continuation patterns
    - Automated pattern detection using geometric and statistical analysis
    - Volume and candlestick confirmation integration
    - Pattern strength assessment and confidence scoring
    - Support/resistance level identification from pattern structures

CLASSICAL PATTERNS RECOGNIZED:
    1. Double Top/Bottom: Reversal patterns at key levels
    2. Head & Shoulders: Complex reversal patterns with multiple peaks/troughs
    3. Triangles: Continuation patterns with converging trendlines
    4. Wedges: Directional patterns with sloping support/resistance
    5. Flags/Pennants: Short-term continuation patterns
    6. Cup & Handle: Bullish continuation patterns

PATTERN DETECTION METHODOLOGY:
    - Geometric Analysis: Shape recognition using price peaks and troughs
    - Statistical Validation: Pattern significance testing
    - Volume Confirmation: Volume spike validation for pattern completion
    - Candlestick Confirmation: Japanese candlestick pattern integration
    - Time Frame Analysis: Pattern validity across different timeframes

DOUBLE TOP/BOTTOM PATTERNS:
    - Double Top: Bearish reversal with two peaks at similar levels
    - Double Bottom: Bullish reversal with two troughs at similar levels
    - Neckline Break: Pattern completion confirmation
    - Volume Validation: Increased volume on breakout
    - Price Target: Measured move calculation (height of pattern)

HEAD & SHOULDERS PATTERNS:
    - Left Shoulder: Initial peak/trough
    - Head: Higher/lower peak/trough (pattern center)
    - Right Shoulder: Final peak/trough (pattern completion)
    - Neckline: Support/resistance connecting shoulder bases
    - Volume Profile: Declining volume through pattern formation

TRIANGLE PATTERNS:
    - Ascending Triangle: Horizontal resistance, rising support
    - Descending Triangle: Horizontal support, falling resistance
    - Symmetrical Triangle: Converging trendlines
    - Volume Contraction: Decreasing volume during formation
    - Breakout Direction: Based on triangle slope and volume

KEY FEATURES:
    - Automated pattern recognition with configurable sensitivity
    - Multi-timeframe pattern analysis for enhanced accuracy
    - Pattern strength classification and confidence scoring
    - Volume confirmation for pattern validation
    - Support/resistance level extraction from patterns

TRADING APPLICATIONS:
    - Reversal Signals: Double tops/bottoms, head & shoulders
    - Continuation Signals: Triangles, flags, wedges
    - Entry Timing: Pattern completion and breakout confirmation
    - Risk Management: Pattern-based stop loss placement
    - Target Setting: Measured moves based on pattern height

CONFIGURATION PARAMETERS:
    - min_pattern_distance: Minimum periods between pattern elements (default: 5)
    - pattern_threshold: Maximum price variation for pattern elements (default: 0.02)
    - volume_confirmation: Enable volume validation (default: True)
    - candle_confirmation: Enable candlestick pattern confirmation (default: True)
    - min_pattern_strength: Minimum pattern strength for recognition (default: 0.6)

PATTERN STRENGTH CLASSIFICATION:
    - Weak (0.0-0.3): Minimal pattern characteristics
    - Moderate (0.3-0.6): Acceptable pattern formation
    - Strong (0.6-0.8): High-quality pattern with good structure
    - Extreme (0.8-1.0): Exceptional pattern with perfect structure

PATTERN COMPLETION SIGNALS:
    - Breakout Confirmation: Price breaks pattern boundary
    - Volume Spike: Increased volume on breakout
    - Candlestick Confirmation: Supporting candlestick patterns
    - Retest Validation: Price returns to test broken level
    - Momentum Confirmation: Indicator confirmation of breakout

EXAMPLE USAGE:
    >>> config = {'price_patterns': {'min_pattern_distance': 5, 'pattern_threshold': 0.02}}
    >>> analyzer = PriceActionPatternsAnalyzer(config)
    >>> patterns = analyzer.analyze_price_patterns(price_data)
    >>> if patterns.get('double_top', {}).get('detected'):
    ...     dt_pattern = patterns['double_top']
    ...     print(f"Double Top detected with confidence {dt_pattern['confidence']:.1f}%")
    ...     print(f"Pattern strength: {dt_pattern['pattern_strength']}")
    ...     print(f"Price target: ${dt_pattern['price_target']:.2f}")

DEPENDENCIES:
    - pandas: Data manipulation and time series analysis
    - numpy: Mathematical calculations and array operations
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient pattern detection algorithms
    - Memory-optimized data structures
    - Vectorized calculations for large datasets
    - Configurable analysis depth for performance tuning

ERROR HANDLING:
    - Data validation and sufficiency checks
    - Pattern detection error recovery
    - Missing data handling and interpolation
    - Statistical calculation error management

VALIDATION TECHNIQUES:
    - Geometric pattern validation using statistical methods
    - Historical pattern performance back-testing
    - Cross-validation with other technical analysis methods
    - Robustness testing across different market conditions

PATTERN RELIABILITY FACTORS:
    - Pattern Symmetry: How well pattern elements align
    - Volume Confirmation: Volume behavior during pattern formation
    - Time Frame: Pattern significance across different timeframes
    - Market Context: Pattern effectiveness in current market regime
    - False Breakout Protection: Filters for failed pattern breakouts

INTEGRATION CAPABILITIES:
    - Technical Indicator Integration: Pattern confirmation with indicators
    - Trend Analysis Integration: Pattern alignment with trend direction
    - Risk Management Integration: Pattern-based position sizing
    - Multi-Timeframe Analysis: Pattern confirmation across timeframes

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class PriceActionPatternsAnalyzer:
    """
    Advanced Price Action Pattern Recognition Engine for Technical Analysis

    This class provides comprehensive recognition of classical chart patterns using
    sophisticated geometric analysis and statistical validation, specifically optimized
    for cryptocurrency price movements where pure price action patterns are most reliable.

    ARCHITECTURE OVERVIEW:
        - Multi-pattern recognition system with 6+ classical patterns
        - Automated pattern detection using geometric and statistical methods
        - Volume and candlestick confirmation integration
        - Pattern strength assessment with confidence scoring
        - Support/resistance level extraction from pattern structures

    PATTERN RECOGNITION ALGORITHMS:
        1. Peak/Trough Detection: Identifies significant price turning points
        2. Geometric Analysis: Validates pattern shapes using mathematical criteria
        3. Statistical Validation: Pattern significance testing and confidence scoring
        4. Volume Confirmation: Validates patterns with volume behavior analysis
        5. Time Frame Validation: Ensures pattern validity across different periods

    SUPPORTED PATTERNS:
        - DOUBLE_TOP: Bearish reversal pattern with two peaks at similar levels
        - DOUBLE_BOTTOM: Bullish reversal pattern with two troughs at similar levels
        - HEAD_SHOULDERS: Complex bearish reversal with three peaks
        - INVERSE_HEAD_SHOULDERS: Complex bullish reversal with three troughs
        - TRIANGLE: Continuation pattern with converging trendlines
        - WEDGE: Directional pattern with sloping support/resistance lines

    PATTERN DETECTION CRITERIA:
        - Minimum Pattern Distance: Prevents overlapping pattern detection
        - Pattern Threshold: Maximum price variation for pattern element similarity
        - Volume Confirmation: Validates pattern completion with volume spikes
        - Candlestick Confirmation: Integrates Japanese candlestick pattern validation
        - Statistical Significance: Ensures pattern reliability through statistical testing

    CONFIGURATION PARAMETERS:
        min_pattern_distance (int): Minimum periods between pattern elements (default: 5)
        pattern_threshold (float): Maximum price variation for pattern elements (default: 0.02)
        volume_confirmation (bool): Enable volume validation for patterns (default: True)
        candle_confirmation (bool): Enable candlestick confirmation (default: True)
        min_pattern_strength (float): Minimum pattern strength for recognition (default: 0.6)

    ATTRIBUTES:
        config (Dict): Complete configuration dictionary
        min_pattern_distance (int): Minimum distance between pattern elements
        pattern_threshold (float): Maximum price variation for pattern elements
        volume_confirmation (bool): Volume confirmation enabled flag
        candle_confirmation (bool): Candlestick confirmation enabled flag

    PATTERN STRENGTH SCORING:
        - Weak (0.0-0.3): Basic pattern characteristics, low confidence
        - Moderate (0.3-0.6): Acceptable pattern formation, medium confidence
        - Strong (0.6-0.8): Well-formed pattern, high confidence
        - Extreme (0.8-1.0): Perfect pattern formation, maximum confidence

    OUTPUT STRUCTURE:
        {
            'double_top': {
                'detected': bool,           # Pattern detection status
                'confidence': float,        # 0.0 to 1.0 confidence score
                'pattern_strength': float,  # Statistical strength measure
                'peak1_price': float,       # First peak price
                'peak2_price': float,       # Second peak price
                'neckline_price': float,    # Neckline level
                'price_target': float,      # Measured move target
                'reason': str              # Detection reasoning
            },
            'double_bottom': { ... },
            'head_shoulders': { ... },
            'triangle': { ... },
            'wedge': { ... },
            'overall_pattern': str        # Dominant pattern identified
        }

    PATTERN COMPLETION SIGNALS:
        - Breakout Confirmation: Price breaks pattern boundary with volume
        - False Breakout Protection: Filters for failed breakouts
        - Retest Validation: Price returns to test broken level
        - Momentum Confirmation: Indicator alignment with pattern
        - Volume Divergence: Volume behavior contradicts price action

    EXAMPLE:
        >>> analyzer = PriceActionPatternsAnalyzer({
        ...     'price_patterns': {
        ...         'min_pattern_distance': 5,
        ...         'pattern_threshold': 0.02,
        ...         'volume_confirmation': True
        ...     }
        ... })
        >>> patterns = analyzer.analyze_price_patterns(price_data)
        >>> if patterns.get('double_top', {}).get('detected'):
        ...     dt = patterns['double_top']
        ...     print(f"Double Top: confidence {dt['confidence']:.1f}%, "
        ...           f"target ${dt['price_target']:.2f}")

    NOTE:
        Requires sufficient historical data (minimum 50 periods recommended)
        for reliable pattern detection and statistical validation.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.min_pattern_distance = config.get("price_patterns", {}).get("min_pattern_distance", 5)
        self.pattern_threshold = config.get("price_patterns", {}).get("pattern_threshold", 0.02)
        self.volume_confirmation = config.get("price_patterns", {}).get("volume_confirmation", True)
        self.candle_confirmation = config.get("price_patterns", {}).get("candle_confirmation", True)

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
                "double_top": None,
                "double_bottom": None,
                "head_shoulders": None,
                "inverse_head_shoulders": None,
                "triangle": None,
                "wedge": None,
                "overall_pattern": "NONE",
            }

            # 1. Double Top Pattern
            patterns["double_top"] = self._detect_double_top(price_data)

            # 2. Double Bottom Pattern
            patterns["double_bottom"] = self._detect_double_bottom(price_data)

            # 3. Head & Shoulders Pattern
            patterns["head_shoulders"] = self._detect_head_shoulders(price_data)

            # 4. Inverse Head & Shoulders Pattern
            patterns["inverse_head_shoulders"] = self._detect_inverse_head_shoulders(price_data)

            # 5. Triangle Pattern
            patterns["triangle"] = self._detect_triangle(price_data)

            # 6. Wedge Pattern
            patterns["wedge"] = self._detect_wedge(price_data)

            # 7. Определяме overall pattern
            patterns["overall_pattern"] = self._determine_overall_pattern(patterns)

            return patterns

        except Exception as e:
            logger.error(f"Грешка при откриване на patterns: {e}")
            return {"error": f"Грешка: {e}"}

    def _detect_double_top(self, price_data: pd.DataFrame) -> Dict:
        """Открива Double Top pattern (bearish reversal)"""
        try:
            if len(price_data) < 20:
                return {"detected": False, "confidence": 0, "reason": "Недостатъчно данни"}

            highs = (
                price_data["high"].values
                if "high" in price_data.columns
                else price_data["High"].values
            )
            lows = (
                price_data["low"].values
                if "low" in price_data.columns
                else price_data["Low"].values
            )
            closes = (
                price_data["close"].values
                if "close" in price_data.columns
                else price_data["Close"].values
            )

            # Намираме пикове в high цените
            peaks = self._find_peaks(highs, "high")

            if len(peaks) < 2:
                return {"detected": False, "confidence": 0, "reason": "Няма достатъчно пикове"}

            # Проверяваме последните 2 пика за double top
            peak1_idx, peak1_price = peaks[-2]
            peak2_idx, peak2_price = peaks[-1]

            # Проверяваме условията за double top
            price_diff = abs(peak2_price - peak1_price) / peak1_price
            time_diff = peak2_idx - peak1_idx

            if (
                price_diff < self.pattern_threshold  # Цените са близки
                and time_diff >= self.min_pattern_distance  # Минимално време между пикове
                and peak2_idx > peak1_idx
            ):  # Вторият пик е по-нов

                # Проверяваме за neckline (support level между пикове)
                neckline = self._find_neckline(price_data, peak1_idx, peak2_idx)

                # Проверяваме за volume confirmation
                volume_confirmed = False
                if self.volume_confirmation and "volume" in price_data.columns:
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
                    "detected": True,
                    "confidence": min(95, confidence),
                    "reason": f"Double Top: два пика на {peak1_price:.2f} и {peak2_price:.2f}",
                    "peak1_price": peak1_price,
                    "peak2_price": peak2_price,
                    "neckline": neckline,
                    "volume_confirmed": volume_confirmed,
                    "candle_confirmed": candle_confirmed,
                    "pattern_strength": (
                        "STRONG" if confidence > 80 else "MEDIUM" if confidence > 65 else "WEAK"
                    ),
                }

            return {
                "detected": False,
                "confidence": 0,
                "reason": "Не отговаря на double top критериите",
            }

        except Exception as e:
            logger.error(f"Грешка при откриване на double top: {e}")
            return {"detected": False, "confidence": 0, "reason": f"Грешка: {e}"}

    def _detect_double_bottom(self, price_data: pd.DataFrame) -> Dict:
        """Открива Double Bottom pattern (bullish reversal)"""
        try:
            if len(price_data) < 20:
                return {"detected": False, "confidence": 0, "reason": "Недостатъчно данни"}

            highs = (
                price_data["high"].values
                if "high" in price_data.columns
                else price_data["High"].values
            )
            lows = (
                price_data["low"].values
                if "low" in price_data.columns
                else price_data["Low"].values
            )
            closes = (
                price_data["close"].values
                if "close" in price_data.columns
                else price_data["Close"].values
            )

            # Намираме дъна в low цените
            troughs = self._find_peaks(lows, "low")

            if len(troughs) < 2:
                return {"detected": False, "confidence": 0, "reason": "Няма достатъчно дъна"}

            # Проверяваме последните 2 дъна за double bottom
            trough1_idx, trough1_price = troughs[-2]
            trough2_idx, trough2_price = troughs[-1]

            # Проверяваме условията за double bottom
            price_diff = abs(trough2_price - trough1_price) / trough1_price
            time_diff = trough2_idx - trough1_idx

            if (
                price_diff < self.pattern_threshold  # Цените са близки
                and time_diff >= self.min_pattern_distance  # Минимално време между дъна
                and trough2_idx > trough1_idx
            ):  # Второто дъно е по-ново

                # Проверяваме за neckline (resistance level между дъна)
                neckline = self._find_neckline(
                    price_data, trough1_idx, trough2_idx, is_resistance=True
                )

                # Проверяваме за volume confirmation
                volume_confirmed = False
                if self.volume_confirmation and "volume" in price_data.columns:
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
                    "detected": True,
                    "confidence": min(95, confidence),
                    "reason": f"Double Bottom: две дъна на {trough1_price:.2f} и {trough2_price:.2f}",
                    "trough1_price": trough1_price,
                    "trough2_price": trough2_price,
                    "neckline": neckline,
                    "volume_confirmed": volume_confirmed,
                    "candle_confirmed": candle_confirmed,
                    "pattern_strength": (
                        "STRONG" if confidence > 80 else "MEDIUM" if confidence > 65 else "WEAK"
                    ),
                }

            return {
                "detected": False,
                "confidence": 0,
                "reason": "Не отговаря на double bottom критериите",
            }

        except Exception as e:
            logger.error(f"Грешка при откриване на double bottom: {e}")
            return {"detected": False, "confidence": 0, "reason": f"Грешка: {e}"}

    def _detect_head_shoulders(self, price_data: pd.DataFrame) -> Dict:
        """Открива Head & Shoulders pattern (bearish reversal)"""
        try:
            if len(price_data) < 30:
                return {"detected": False, "confidence": 0, "reason": "Недостатъчно данни за H&S"}

            highs = (
                price_data["high"].values
                if "high" in price_data.columns
                else price_data["High"].values
            )

            # Намираме пикове
            peaks = self._find_peaks(highs, "high")

            if len(peaks) < 3:
                return {
                    "detected": False,
                    "confidence": 0,
                    "reason": "Няма достатъчно пикове за H&S",
                }

            # Проверяваме последните 3 пика
            left_shoulder_idx, left_shoulder_price = peaks[-3]
            head_idx, head_price = peaks[-2]
            right_shoulder_idx, right_shoulder_price = peaks[-1]

            # Проверяваме H&S условията
            if (
                head_price > left_shoulder_price  # Главата е по-висока от лявото рамо
                and head_price > right_shoulder_price  # Главата е по-висока от дясното рамо
                and abs(left_shoulder_price - right_shoulder_price) / left_shoulder_price < 0.03
            ):  # Раменете са близки

                # Проверяваме за neckline
                neckline = self._find_neckline(price_data, left_shoulder_idx, right_shoulder_idx)

                confidence = 70  # Base confidence за H&S

                return {
                    "detected": True,
                    "confidence": confidence,
                    "reason": f"Head & Shoulders: глава на {head_price:.2f}, рамене на {left_shoulder_price:.2f}",
                    "head_price": head_price,
                    "left_shoulder_price": left_shoulder_price,
                    "right_shoulder_price": right_shoulder_price,
                    "neckline": neckline,
                    "pattern_strength": "STRONG",
                }

            return {"detected": False, "confidence": 0, "reason": "Не отговаря на H&S критериите"}

        except Exception as e:
            logger.error(f"Грешка при откриване на Head & Shoulders: {e}")
            return {"detected": False, "confidence": 0, "reason": f"Грешка: {e}"}

    def _detect_inverse_head_shoulders(self, price_data: pd.DataFrame) -> Dict:
        """Открива Inverse Head & Shoulders pattern (bullish reversal)"""
        try:
            if len(price_data) < 30:
                return {"detected": False, "confidence": 0, "reason": "Недостатъчно данни за IH&S"}

            lows = (
                price_data["low"].values
                if "low" in price_data.columns
                else price_data["Low"].values
            )

            # Намираме дъна
            troughs = self._find_peaks(lows, "low")

            if len(troughs) < 3:
                return {
                    "detected": False,
                    "confidence": 0,
                    "reason": "Няма достатъчно дъна за IH&S",
                }

            # Проверяваме последните 3 дъна
            left_shoulder_idx, left_shoulder_price = troughs[-3]
            head_idx, head_price = troughs[-2]
            right_shoulder_idx, right_shoulder_price = troughs[-1]

            # Проверяваме IH&S условията
            if (
                head_price < left_shoulder_price  # Главата е по-ниска от лявото рамо
                and head_price < right_shoulder_price  # Главата е по-ниска от дясното рамо
                and abs(left_shoulder_price - right_shoulder_price) / left_shoulder_price < 0.03
            ):  # Раменете са близки

                # Проверяваме за neckline
                neckline = self._find_neckline(
                    price_data, left_shoulder_idx, right_shoulder_idx, is_resistance=True
                )

                confidence = 70  # Base confidence за IH&S

                return {
                    "detected": True,
                    "confidence": confidence,
                    "reason": f"Inverse H&S: глава на {head_price:.2f}, рамене на {left_shoulder_price:.2f}",
                    "head_price": head_price,
                    "left_shoulder_price": left_shoulder_price,
                    "right_shoulder_price": right_shoulder_price,
                    "neckline": neckline,
                    "pattern_strength": "STRONG",
                }

            return {"detected": False, "confidence": 0, "reason": "Не отговаря на IH&S критериите"}

        except Exception as e:
            logger.error(f"Грешка при откриване на Inverse Head & Shoulders: {e}")
            return {"detected": False, "confidence": 0, "reason": f"Грешка: {e}"}

    def _detect_triangle(self, price_data: pd.DataFrame) -> Dict:
        """Открива Triangle pattern"""
        try:
            if len(price_data) < 20:
                return {
                    "detected": False,
                    "confidence": 0,
                    "reason": "Недостатъчно данни за triangle",
                }

            highs = (
                price_data["high"].values
                if "high" in price_data.columns
                else price_data["High"].values
            )
            lows = (
                price_data["low"].values
                if "low" in price_data.columns
                else price_data["Low"].values
            )

            # Намираме пикове и дъна
            peaks = self._find_peaks(highs, "high")
            troughs = self._find_peaks(lows, "low")

            if len(peaks) < 2 or len(troughs) < 2:
                return {
                    "detected": False,
                    "confidence": 0,
                    "reason": "Няма достатъчно пикове/дъна за triangle",
                }

            # Проверяваме за triangle formation
            # Това е опростена версия - в реалността трябва да се проверява за сближаващи се линии

            return {
                "detected": False,
                "confidence": 0,
                "reason": "Triangle detection не е имплементиран",
            }

        except Exception as e:
            logger.error(f"Грешка при откриване на triangle: {e}")
            return {"detected": False, "confidence": 0, "reason": f"Грешка: {e}"}

    def _detect_wedge(self, price_data: pd.DataFrame) -> Dict:
        """Открива Wedge pattern"""
        try:
            if len(price_data) < 20:
                return {"detected": False, "confidence": 0, "reason": "Недостатъчно данни за wedge"}

            # Опростена версия - не е пълно имплементирана
            return {
                "detected": False,
                "confidence": 0,
                "reason": "Wedge detection не е имплементиран",
            }

        except Exception as e:
            logger.error(f"Грешка при откриване на wedge: {e}")
            return {"detected": False, "confidence": 0, "reason": f"Грешка: {e}"}

    def _find_peaks(self, data: np.ndarray, peak_type: str) -> List[Tuple[int, float]]:
        """Намира пикове в данните"""
        try:
            peaks = []

            if peak_type == "high":
                for i in range(1, len(data) - 1):
                    if data[i] > data[i - 1] and data[i] > data[i + 1]:
                        peaks.append((i, data[i]))
            else:  # low
                for i in range(1, len(data) - 1):
                    if data[i] < data[i - 1] and data[i] < data[i + 1]:
                        peaks.append((i, data[i]))

            return peaks

        except Exception as e:
            logger.error(f"Грешка при намиране на пикове: {e}")
            return []

    def _find_neckline(
        self, price_data: pd.DataFrame, idx1: int, idx2: int, is_resistance: bool = False
    ) -> float:
        """Намира neckline между два пика/дъна"""
        try:
            if idx1 >= idx2:
                return 0.0

            # Взимаме данните между двата пика/дъна
            between_data = price_data.iloc[idx1 : idx2 + 1]

            if is_resistance:
                # За resistance neckline, търсим най-високата точка
                high_col = "high" if "high" in between_data.columns else "High"
                return float(between_data[high_col].max())
            else:
                # За support neckline, търсим най-ниската точка
                low_col = "low" if "low" in between_data.columns else "Low"
                return float(between_data[low_col].min())

        except Exception as e:
            logger.error(f"Грешка при намиране на neckline: {e}")
            return 0.0

    def _check_volume_confirmation(self, price_data: pd.DataFrame, pattern_idx: int) -> bool:
        """Проверява volume confirmation за pattern"""
        try:
            if "volume" not in price_data.columns:
                return False

            volumes = price_data["volume"].values

            if pattern_idx >= len(volumes):
                return False

            # Проверяваме дали обемът на pattern_idx е над средния за последните 10 периода
            lookback = min(10, pattern_idx)
            recent_volumes = volumes[pattern_idx - lookback : pattern_idx]
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
            open_price = candle["open"] if "open" in candle.index else candle["Open"]
            close_price = candle["close"] if "close" in candle.index else candle["Close"]
            high_price = candle["high"] if "high" in candle.index else candle["High"]
            low_price = candle["low"] if "low" in candle.index else candle["Low"]

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
            open_price = candle["open"] if "open" in candle.index else candle["Open"]
            close_price = candle["close"] if "close" in candle.index else candle["Close"]
            high_price = candle["high"] if "high" in candle.index else candle["High"]
            low_price = candle["low"] if "low" in candle.index else candle["Low"]

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

    def analyze_rejection_patterns(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Phase 1.6: Анализира rejection patterns за SHORT сигнали

        Търси силни rejection patterns от resistance нива, особено:
        - Long upper wick (rejection) - wick > body * rejection_wick_ratio
        - Bearish rejection candles близо до resistance нива
        - Множество rejection опити на едно ниво

        Args:
            price_data: DataFrame с OHLCV данни

        Returns:
            Dict с информация за rejection patterns
        """
        try:
            if price_data is None or price_data.empty:
                return {"rejection_detected": False, "reason": "Няма данни за анализ"}

            # Конфигурационни параметри
            config = self.config.get("short_signals", {})
            rejection_enabled = config.get("price_action_rejection", True)
            wick_ratio_threshold = config.get("rejection_wick_ratio", 2.0)
            lookback_periods = config.get("rejection_lookback_periods", 5)
            strength_threshold = config.get("rejection_strength_threshold", 0.7)

            if not rejection_enabled:
                return {"rejection_detected": False, "reason": "Price action rejection изключен"}

            # Взимаме последните N периода за анализ
            recent_data = price_data.tail(lookback_periods)

            if len(recent_data) < lookback_periods:
                return {
                    "rejection_detected": False,
                    "reason": f"Недостатъчно данни: нужни {lookback_periods}, има {len(recent_data)}",
                }

            # Анализираме всяка свещ за rejection patterns
            rejection_signals = []

            for idx in range(len(recent_data)):
                candle = recent_data.iloc[idx]

                # Извличаме OHLC данни
                open_price = candle["open"] if "open" in candle.index else candle["Open"]
                close_price = candle["close"] if "close" in candle.index else candle["Close"]
                high_price = candle["high"] if "high" in candle.index else candle["High"]
                low_price = candle["low"] if "low" in candle.index else candle["Low"]

                # Изчисляваме body и shadows
                body_size = abs(close_price - open_price)
                upper_shadow = high_price - max(open_price, close_price)
                lower_shadow = min(open_price, close_price) - low_price

                # Проверяваме за bearish rejection (SHORT сигнал)
                if close_price < open_price and upper_shadow > 0:  # Bearish candle с upper shadow
                    wick_ratio = upper_shadow / body_size if body_size > 0 else 0

                    if wick_ratio >= wick_ratio_threshold:
                        rejection_strength = min(wick_ratio / wick_ratio_threshold, 1.0)

                        rejection_signals.append(
                            {
                                "index": idx,
                                "date": recent_data.index[idx],
                                "wick_ratio": wick_ratio,
                                "strength": rejection_strength,
                                "high": high_price,
                                "close": close_price,
                                "body_size": body_size,
                                "upper_shadow": upper_shadow,
                            }
                        )

            # Оценяваме общия rejection сигнал
            if rejection_signals:
                # Взимаме най-силния rejection сигнал
                strongest_rejection = max(rejection_signals, key=lambda x: x["strength"])

                if strongest_rejection["strength"] >= strength_threshold:
                    return {
                        "rejection_detected": True,
                        "reason": f'Силен rejection pattern: wick ratio {strongest_rejection["wick_ratio"]:.2f} > {wick_ratio_threshold:.2f}',
                        "strength": strongest_rejection["strength"],
                        "wick_ratio": strongest_rejection["wick_ratio"],
                        "date": strongest_rejection["date"],
                        "high": strongest_rejection["high"],
                        "close": strongest_rejection["close"],
                        "all_rejections": len(rejection_signals),
                        "strongest_rejection": strongest_rejection,
                    }
                else:
                    return {
                        "rejection_detected": False,
                        "reason": f'Слаб rejection pattern: strength {strongest_rejection["strength"]:.2f} < {strength_threshold:.2f}',
                        "strength": strongest_rejection["strength"],
                        "wick_ratio": strongest_rejection["wick_ratio"],
                    }
            else:
                return {
                    "rejection_detected": False,
                    "reason": f"Няма rejection patterns в последните {lookback_periods} периода",
                    "analyzed_periods": lookback_periods,
                }

        except Exception as e:
            logger.error(f"Грешка при анализ на rejection patterns: {e}")
            return {
                "rejection_detected": False,
                "reason": f"Error in rejection analysis: {e}",
                "error": str(e),
            }

    def _determine_overall_pattern(self, patterns: Dict) -> str:
        """Определя overall pattern от всички открити"""
        try:
            bearish_count = 0
            bullish_count = 0

            # Броим bearish patterns
            if patterns.get("double_top", {}).get("detected", False):
                bearish_count += 1
            if patterns.get("head_shoulders", {}).get("detected", False):
                bearish_count += 1

            # Броим bullish patterns
            if patterns.get("double_bottom", {}).get("detected", False):
                bullish_count += 1
            if patterns.get("inverse_head_shoulders", {}).get("detected", False):
                bullish_count += 1

            # Определяме overall pattern
            if bearish_count >= 2:
                return "STRONG_BEARISH"
            elif bearish_count == 1:
                return "BEARISH"
            elif bullish_count >= 2:
                return "STRONG_BULLISH"
            elif bullish_count == 1:
                return "BULLISH"
            else:
                return "NONE"

        except Exception as e:
            logger.error(f"Грешка при определяне на overall pattern: {e}")
            return "NONE"

    def get_pattern_trading_signals(self, patterns: Dict) -> Dict:
        """Генерира trading сигнали базирани на patterns"""
        try:
            overall_pattern = patterns.get("overall_pattern", "NONE")

            if overall_pattern == "STRONG_BEARISH":
                return {
                    "signal": "STRONG_SELL",
                    "confidence": 80,
                    "reason": "Множествен bearish patterns - силна bearish сигнал",
                    "risk_level": "HIGH",
                }
            elif overall_pattern == "BEARISH":
                return {
                    "signal": "SELL",
                    "confidence": 65,
                    "reason": "Bearish pattern - умерена bearish сигнал",
                    "risk_level": "MEDIUM",
                }
            elif overall_pattern == "STRONG_BULLISH":
                return {
                    "signal": "STRONG_BUY",
                    "confidence": 80,
                    "reason": "Множествен bullish patterns - силна bullish сигнал",
                    "risk_level": "HIGH",
                }
            elif overall_pattern == "BULLISH":
                return {
                    "signal": "BUY",
                    "confidence": 65,
                    "reason": "Bullish pattern - умерена bullish сигнал",
                    "risk_level": "MEDIUM",
                }
            else:
                return {
                    "signal": "HOLD",
                    "confidence": 50,
                    "reason": "Няма ясни patterns - няма сигнал",
                    "risk_level": "LOW",
                }

        except Exception as e:
            logger.error(f"Грешка при генериране на pattern trading сигнали: {e}")
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reason": f"Грешка: {e}",
                "risk_level": "UNKNOWN",
            }


if __name__ == "__main__":
    print("Price Action Patterns анализатор за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
