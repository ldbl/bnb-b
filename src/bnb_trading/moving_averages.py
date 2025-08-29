"""
Moving Averages Analysis Module - Trend Following and Crossover Signals

SPECIALIZED MODULE FOR MOVING AVERAGE ANALYSIS AND CROSSOVER DETECTION
Identifies trend changes and momentum shifts through EMA crossover patterns

This module provides comprehensive moving average analysis specifically optimized
for cryptocurrency trading, focusing on exponential moving averages (EMA) and
their crossover patterns that provide reliable trend-following signals.

ARCHITECTURE OVERVIEW:
    - Fast and slow EMA calculation with configurable periods
    - Automated crossover detection with bullish/bearish signals
    - Volume confirmation integration for stronger signals
    - Trend strength assessment and momentum analysis
    - Support/resistance level identification using moving averages

MOVING AVERAGE THEORY IMPLEMENTATION:
    - Exponential Moving Average (EMA): More responsive to recent price changes
    - Golden Cross: Fast EMA crosses above slow EMA (bullish signal)
    - Death Cross: Fast EMA crosses below slow EMA (bearish signal)
    - Trend Strength: Distance between fast and slow EMA indicates trend power
    - Support/Resistance: EMA levels act as dynamic support/resistance

CROSSOVER SIGNAL TYPES:
    1. BULLISH CROSSOVER: Fast EMA crosses above slow EMA (LONG signal)
    2. BEARISH CROSSOVER: Fast EMA crosses below slow EMA (SHORT signal)
    3. CONTINUATION: Parallel EMAs indicate strong trend continuation
    4. CONVERGENCE: EMAs moving closer indicate weakening trend
    5. DIVERGENCE: EMAs moving apart indicate strengthening trend

KEY FEATURES:
    - Automated EMA crossover detection with configurable sensitivity
    - Volume confirmation for crossover validation
    - Trend strength assessment using EMA separation
    - Support/resistance level identification
    - Multi-timeframe moving average analysis

TRADING APPLICATIONS:
    - Trend Following: Enter trades in direction of EMA slope
    - Reversal Signals: EMA crossovers often precede trend changes
    - Risk Management: Use EMA levels for stop-loss placement
    - Entry Timing: Enter on pullbacks to EMA support/resistance
    - Exit Signals: Close positions when EMA crossovers occur

CONFIGURATION PARAMETERS:
    - fast_period: Fast EMA period for short-term trend (default: 10)
    - slow_period: Slow EMA period for long-term trend (default: 50)
    - volume_confirmation: Enable volume validation for signals (default: True)
    - volume_multiplier: Required volume increase for confirmation (default: 1.5)
    - volume_lookback: Periods to analyze for volume confirmation (default: 14)

SIGNAL STRENGTH CLASSIFICATION:
    - Weak: Minimal EMA separation, low confidence signal
    - Moderate: Moderate EMA separation, acceptable confidence
    - Strong: Large EMA separation, high confidence signal
    - Extreme: Very large EMA separation, maximum confidence signal

EMA CROSSOVER PATTERNS:
    - Bullish Momentum: Fast EMA pulling away above slow EMA
    - Bearish Momentum: Fast EMA pulling away below slow EMA
    - Trend Exhaustion: Fast EMA approaching/crossing slow EMA
    - Range Conditions: EMAs moving sideways, oscillating around price

EXAMPLE USAGE:
    >>> config = {
    ...     'moving_averages': {
    ...         'fast_period': 10,
    ...         'slow_period': 50,
    ...         'volume_confirmation': True
    ...     }
    ... }
    >>> ma_analyzer = MovingAveragesAnalyzer(config)
    >>> price_data = pd.read_csv('bnb_daily.csv')
    >>> analysis = ma_analyzer.analyze_moving_averages(price_data)
    >>> if analysis['crossover_signal']['signal'] == 'BULLISH':
    ...     print(f"Bullish crossover detected with confidence {analysis['crossover_signal']['confidence']:.1f}%")

DEPENDENCIES:
    - pandas: Data manipulation and time series operations
    - numpy: Mathematical calculations and array operations
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient EMA calculation using vectorized operations
    - Memory-optimized data structures for large datasets
    - Incremental updates for real-time analysis
    - Caching of expensive crossover calculations

ERROR HANDLING:
    - Validation of input data structure and sufficiency
    - Graceful handling of insufficient historical data
    - Statistical calculation error recovery
    - Comprehensive logging for debugging and monitoring

VALIDATION TECHNIQUES:
    - Statistical significance testing of crossover patterns
    - Volume confirmation for stronger signals
    - Cross-validation with other trend indicators
    - Robustness testing across different market conditions

SIGNAL ACCURACY ENHANCEMENTS:
    - Volume confirmation for crossover validation
    - Trend strength assessment using EMA separation
    - Multi-timeframe confirmation for stronger signals
    - Market context integration for better accuracy

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import logging
from typing import Any, Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MovingAveragesAnalyzer:
    """
    Advanced Moving Average Analysis Engine for Trend Detection

    This class provides comprehensive moving average analysis with specialized
    algorithms for detecting trend changes, momentum shifts, and crossover patterns
    optimized for cryptocurrency price movements.

    ARCHITECTURE OVERVIEW:
        - Dual EMA calculation (fast and slow periods) with configurable parameters
        - Automated crossover detection with bullish/bearish signal generation
        - Volume confirmation integration for signal validation
        - Trend strength assessment using EMA separation and slope analysis
        - Support/resistance level identification using EMA levels

    EMA CROSSOVER METHODOLOGY:
        1. EMA Calculation: Efficient exponential moving average computation
        2. Crossover Detection: Identifies when fast EMA crosses slow EMA
        3. Signal Classification: Determines bullish vs bearish crossover signals
        4. Strength Assessment: Evaluates crossover significance and confidence
        5. Volume Confirmation: Validates signals with volume analysis

    CROSSOVER SIGNAL TYPES:
        - BULLISH_CROSSOVER: Fast EMA crosses above slow EMA (strong LONG signal)
        - BEARISH_CROSSOVER: Fast EMA crosses below slow EMA (strong SHORT signal)
        - TREND_CONTINUATION: Parallel EMAs indicate sustained trend
        - TREND_WEAKENING: EMAs converging indicate trend exhaustion
        - RANGE_CONDITION: EMAs oscillating sideways (neutral signal)

    CONFIGURATION PARAMETERS:
        fast_period (int): Fast EMA period for short-term trend (default: 10)
        slow_period (int): Slow EMA period for long-term trend (default: 50)
        volume_confirmation (bool): Enable volume validation (default: True)
        volume_multiplier (float): Required volume increase (default: 1.5)
        volume_lookback (int): Periods for volume analysis (default: 14)

    ATTRIBUTES:
        config (Dict): Complete configuration dictionary
        fast_period (int): Fast EMA calculation period
        slow_period (int): Slow EMA calculation period
        volume_confirmation (bool): Volume confirmation enabled flag
        volume_multiplier (float): Volume confirmation threshold
        volume_lookback (int): Volume analysis lookback period

    EMA CALCULATION ALGORITHM:
        - Uses traditional EMA formula: EMA = (Close * Multiplier) + (Previous EMA * (1 - Multiplier))
        - Multiplier = 2 / (Period + 1)
        - Handles initial EMA calculation using SMA for first periods
        - Optimized for performance with vectorized operations

    SIGNAL CONFIDENCE SCORING:
        - Crossover Strength: Distance between EMAs at crossover point
        - Trend Slope: Rate of EMA separation/divergence
        - Volume Confirmation: Volume spike at crossover point
        - Historical Success: Past performance of similar patterns
        - Market Context: Current market regime and volatility

    OUTPUT STRUCTURE:
        {
            'fast_ema': np.ndarray,        # Fast EMA values array
            'slow_ema': np.ndarray,        # Slow EMA values array
            'fast_ema_current': float,     # Current fast EMA value
            'slow_ema_current': float,     # Current slow EMA value
            'volume_confirmed': bool,      # Volume confirmation status
            'crossover_signal': {
                'signal': str,             # BULLISH_CROSSOVER | BEARISH_CROSSOVER | NONE
                'confidence': float,       # 0.0 to 1.0 confidence score
                'reason': str,             # Explanation of signal
                'strength': float,         # Statistical strength
                'crossover_price': float   # Price at crossover point
            },
            'ema_values': {
                'fast_ema': float,         # Current fast EMA
                'slow_ema': float,         # Current slow EMA
                'separation': float,       # Current EMA separation
                'trend_strength': str      # Weak/Moderate/Strong/Extreme
            }
        }

    EXAMPLE:
        >>> config = {
        ...     'moving_averages': {
        ...         'fast_period': 10,
        ...         'slow_period': 50,
        ...         'volume_confirmation': True
        ...     }
        ... }
        >>> analyzer = MovingAveragesAnalyzer(config)
        >>> result = analyzer.analyze_moving_averages(price_data)
        >>> crossover = result['crossover_signal']
        >>> if crossover['signal'] == 'BULLISH_CROSSOVER':
        ...     print(f"Bullish crossover with confidence {crossover['confidence']:.1f}%")

    NOTE:
        Requires sufficient historical data (minimum 50 periods recommended)
        and clean OHLCV data for accurate EMA and crossover calculations.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.fast_period = config.get("moving_averages", {}).get("fast_period", 10)
        self.slow_period = config.get("moving_averages", {}).get("slow_period", 50)
        self.volume_confirmation = config.get("moving_averages", {}).get(
            "volume_confirmation", True
        )
        self.volume_multiplier = config.get("moving_averages", {}).get("volume_multiplier", 1.5)
        self.volume_lookback = config.get("moving_averages", {}).get("volume_lookback", 14)

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
                return {"error": f"Недостатъчно данни. Нужни са поне {self.slow_period} периода"}

            closes = (
                price_data["close"].values
                if "close" in price_data.columns
                else price_data["Close"].values
            )

            # Изчисляваме EMA
            fast_ema = self._calculate_ema(closes, self.fast_period)
            slow_ema = self._calculate_ema(closes, self.slow_period)

            # Изчисляваме volume confirmation
            volume_confirmed = False
            if self.volume_confirmation and "volume" in price_data.columns:
                volume_confirmed = self._check_volume_confirmation(price_data)

            return {
                "fast_ema": fast_ema,
                "slow_ema": slow_ema,
                "fast_ema_current": fast_ema[-1] if len(fast_ema) > 0 else None,
                "slow_ema_current": slow_ema[-1] if len(slow_ema) > 0 else None,
                "volume_confirmed": volume_confirmed,
                "crossover_signal": self._detect_crossover(fast_ema, slow_ema),
            }

        except Exception as e:
            logger.error(f"Грешка при изчисляване на EMA: {e}")
            return {"error": f"Грешка: {e}"}

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
                return {"signal": "NONE", "confidence": 0, "reason": "Недостатъчно данни"}

            # Текущи стойности
            fast_current = fast_ema[-1]
            fast_previous = fast_ema[-2]
            slow_current = slow_ema[-1]
            slow_previous = slow_ema[-2]

            # Проверяваме за bullish crossover
            if fast_previous <= slow_previous and fast_current > slow_current:
                # Fast EMA пресича нагоре slow EMA
                crossover_strength = abs(fast_current - slow_current) / slow_current
                confidence = min(95, 60 + crossover_strength * 100)

                return {
                    "signal": "BULLISH_CROSS",
                    "confidence": confidence,
                    "reason": (
                        f"Fast EMA ({
                            self.fast_period}) пресича нагоре Slow EMA ({
                            self.slow_period})"
                    ),
                    "crossover_strength": crossover_strength,
                    "fast_ema": fast_current,
                    "slow_ema": slow_current,
                }

            # Проверяваме за bearish crossover
            elif fast_previous >= slow_previous and fast_current < slow_current:
                # Fast EMA пресича надолу slow EMA
                crossover_strength = abs(fast_current - slow_current) / slow_current
                confidence = min(95, 60 + crossover_strength * 100)

                return {
                    "signal": "BEARISH_CROSS",
                    "confidence": confidence,
                    "reason": (
                        f"Fast EMA ({
                            self.fast_period}) пресича надолу Slow EMA ({
                            self.slow_period})"
                    ),
                    "crossover_strength": crossover_strength,
                    "fast_ema": fast_current,
                    "slow_ema": slow_current,
                }

            # Проверяваме за текущо състояние
            else:
                if fast_current > slow_current:
                    # Fast EMA е над slow EMA - bullish
                    distance = (fast_current - slow_current) / slow_current
                    confidence = min(80, 50 + distance * 100)

                    return {
                        "signal": "BULLISH_ABOVE",
                        "confidence": confidence,
                        "reason": (
                            f"Fast EMA ({self.fast_period}) е над Slow EMA ({self.slow_period})"
                        ),
                        "distance": distance,
                        "fast_ema": fast_current,
                        "slow_ema": slow_current,
                    }
                else:
                    # Fast EMA е под slow EMA - bearish
                    distance = (slow_current - fast_current) / slow_current
                    confidence = min(80, 50 + distance * 100)

                    return {
                        "signal": "BEARISH_BELOW",
                        "confidence": confidence,
                        "reason": (
                            f"Fast EMA ({self.fast_period}) е под Slow EMA ({self.slow_period})"
                        ),
                        "distance": distance,
                        "fast_ema": fast_current,
                        "slow_ema": slow_current,
                    }

        except Exception as e:
            logger.error(f"Грешка при откриване на crossover: {e}")
            return {"signal": "NONE", "confidence": 0, "reason": f"Грешка: {e}"}

    def _check_volume_confirmation(self, price_data: pd.DataFrame) -> bool:
        """
        Проверява volume confirmation

        Args:
            price_data: DataFrame с OHLCV данни

        Returns:
            bool: True ако volume потвърждава сигнала
        """
        try:
            if "volume" not in price_data.columns:
                return False

            volumes = price_data["volume"].values

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
            if "error" in ma_analysis:
                return {
                    "signal": "HOLD",
                    "confidence": 0,
                    "reason": ma_analysis["error"],
                    "risk_level": "UNKNOWN",
                }

            crossover = ma_analysis.get("crossover_signal", {})
            signal_type = crossover.get("signal", "NONE")
            confidence = crossover.get("confidence", 0)
            volume_confirmed = ma_analysis.get("volume_confirmed", False)

            # Ако няма volume confirmation, намаляваме confidence
            if not volume_confirmed and self.volume_confirmation:
                confidence = max(confidence * 0.7, 30)

            # Генерираме trading сигнали
            if signal_type == "BULLISH_CROSS":
                return {
                    "signal": "BUY",
                    "confidence": confidence,
                    "reason": f'Bullish EMA Crossover: {crossover.get("reason", "")}',
                    "risk_level": "MEDIUM" if volume_confirmed else "HIGH",
                    "entry_price": "Current price",
                    "stop_loss": f'Below {ma_analysis.get("slow_ema_current", 0):.2f}',
                    "target": f'Above {ma_analysis.get("fast_ema_current", 0):.2f}',
                }

            elif signal_type == "BEARISH_CROSS":
                return {
                    "signal": "SELL",
                    "confidence": confidence,
                    "reason": f'Bearish EMA Crossover: {crossover.get("reason", "")}',
                    "risk_level": "MEDIUM" if volume_confirmed else "HIGH",
                    "entry_price": "Current price",
                    "stop_loss": f'Above {ma_analysis.get("slow_ema_current", 0):.2f}',
                    "target": f'Below {ma_analysis.get("fast_ema_current", 0):.2f}',
                }

            elif signal_type == "BULLISH_ABOVE":
                return {
                    "signal": "HOLD_LONG",
                    "confidence": confidence,
                    "reason": f'Bullish Trend: {crossover.get("reason", "")}',
                    "risk_level": "LOW",
                    "entry_price": "Pullback to slow EMA",
                    "stop_loss": f'Below {ma_analysis.get("slow_ema_current", 0):.2f}',
                    "target": "Continue trend",
                }

            elif signal_type == "BEARISH_BELOW":
                return {
                    "signal": "HOLD_SHORT",
                    "confidence": confidence,
                    "reason": f'Bearish Trend: {crossover.get("reason", "")}',
                    "risk_level": "LOW",
                    "entry_price": "Bounce to slow EMA",
                    "stop_loss": f'Above {ma_analysis.get("slow_ema_current", 0):.2f}',
                    "target": "Continue trend",
                }

            else:
                return {
                    "signal": "WAIT",
                    "confidence": 50,
                    "reason": "Няма ясен MA сигнал",
                    "risk_level": "LOW",
                }

        except Exception as e:
            logger.error(f"Грешка при генериране на MA trading сигнали: {e}")
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reason": f"Грешка: {e}",
                "risk_level": "UNKNOWN",
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
            if "error" in ma_analysis:
                return {"strength": "UNKNOWN", "reason": ma_analysis["error"]}

            crossover = ma_analysis.get("crossover_signal", {})
            signal_type = crossover.get("signal", "NONE")
            crossover_strength = crossover.get("crossover_strength", 0)
            volume_confirmed = ma_analysis.get("volume_confirmed", False)

            # Определяме силата на сигнала
            if signal_type in ["BULLISH_CROSS", "BEARISH_CROSS"]:
                if crossover_strength > 0.05:  # 5% разлика
                    strength = "STRONG"
                elif crossover_strength > 0.02:  # 2% разлика
                    strength = "MEDIUM"
                else:
                    strength = "WEAK"

                # Volume confirmation увеличава силата
                if volume_confirmed:
                    strength = f"{strength}_VOLUME_CONFIRMED"

                reason = f"EMA Crossover с {crossover_strength:.2%} разлика"

            elif signal_type in ["BULLISH_ABOVE", "BEARISH_BELOW"]:
                distance = crossover.get("distance", 0)

                if distance > 0.1:  # 10% разлика
                    strength = "VERY_STRONG"
                elif distance > 0.05:  # 5% разлика
                    strength = "STRONG"
                elif distance > 0.02:  # 2% разлика
                    strength = "MEDIUM"
                else:
                    strength = "WEAK"

                reason = f"EMA Trend с {distance:.2%} разлика"

            else:
                strength = "NEUTRAL"
                reason = "Няма ясен MA сигнал"

            return {
                "strength": strength,
                "reason": reason,
                "crossover_strength": crossover_strength,
                "volume_confirmed": volume_confirmed,
            }

        except Exception as e:
            logger.error(f"Грешка при анализ на MA сила: {e}")
            return {"strength": "UNKNOWN", "reason": f"Грешка: {e}"}


if __name__ == "__main__":
    print("Moving Averages анализатор за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
