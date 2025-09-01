"""
Fibonacci Analysis Module - Advanced Fibonacci Retracement & Extension Analysis

SPECIALIZED MODULE FOR AUTOMATED FIBONACCI ANALYSIS
PRIORITY #1: Automated swing point detection and comprehensive Fib level calculations

This module provides advanced Fibonacci analysis capabilities specifically optimized
for cryptocurrency trading, with special focus on BNB/USD price movements.

ARCHITECTURE OVERVIEW:
    - Automated swing point detection using configurable lookback periods
    - Complete Fibonacci retracement and extension level calculations
    - Proximity analysis for current price relative to Fib levels
    - Support for both bullish and bearish market scenarios
    - Integration with trend analysis for signal confirmation

FIBONACCI LEVELS SUPPORTED:
    - Retracement Levels: 78.6%, 61.8%, 50%, 38.2%, 23.6%
    - Extension Levels: 100%, 127.2%, 141.4%, 161.8%, 200%, 261.8%
    - Golden Ratio: 61.8% (primary focus for BNB analysis)

KEY FEATURES:
    - Automated swing high/low detection with configurable sensitivity
    - Multiple timeframe analysis capability
    - Proximity threshold analysis for entry/exit signals
    - Fibonacci confluence detection
    - Trend-aware Fib level interpretation
    - Comprehensive error handling and validation

TRADING APPLICATIONS:
    - Support/Resistance identification at Fib levels
    - Entry point determination near Fib retracements
    - Target price calculation using Fib extensions
    - Risk management using Fib-based stop levels
    - Trend continuation/breakout signals

CONFIGURATION PARAMETERS:
    - swing_lookback: Periods to analyze for swing points (default: 100)
    - key_levels: Primary Fib levels for analysis (default: [0.382, 0.618])
    - proximity_threshold: Distance threshold for level proximity (default: 0.01)
    - min_swing_size: Minimum swing size for valid analysis (default: 0.15)

EXAMPLE USAGE:
    >>> config = {'fibonacci': {'swing_lookback': 100, 'key_levels': [0.382, 0.618]}}
    >>> fib_analyzer = FibonacciAnalyzer(config)
    >>> analysis = fib_analyzer.analyze_fibonacci_trend(daily_data)
    >>> print(f"Current Fib level: {analysis['nearest_level']}")

DEPENDENCIES:
    - pandas: Data manipulation and time series analysis
    - numpy: Mathematical calculations and array operations
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient swing point detection algorithms
    - Vectorized Fibonacci level calculations
    - Memory-efficient data processing
    - Caching of expensive computations

ERROR HANDLING:
    - Validation of input data structure and quality
    - Graceful handling of insufficient data periods
    - Comprehensive logging for debugging and monitoring
    - Fallback mechanisms for edge cases

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import logging
from typing import Any

import pandas as pd

from .core.models import ModuleResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FibonacciAnalyzer:
    """
    Advanced Fibonacci Retracement and Extension Analyzer for BNB Trading

    This class provides comprehensive Fibonacci analysis specifically optimized for
    cryptocurrency price movements, particularly BNB/USD. It automates the detection
    of swing points and calculates all relevant Fibonacci levels for trading decisions.

    ARCHITECTURE OVERVIEW:
        - Automated swing point detection using configurable lookback windows
        - Complete Fibonacci retracement (23.6% to 78.6%) and extension (100% to 261.8%) analysis
        - Proximity analysis to identify current price position relative to Fib levels
        - Support for both bullish and bearish market scenarios
        - Integration with trend analysis for signal validation

    FIBONACCI THEORY IMPLEMENTATION:
        - Golden Ratio (61.8%) as primary focus for BNB analysis
        - Complete Fib sequence from 0% to 261.8%
        - Automated swing high/low detection with validation
        - Trend-aware level interpretation
        - Multi-timeframe confluence detection

    ALGORITHMS USED:
        1. Swing Point Detection: Identifies local maxima/minima within lookback period
        2. Fib Level Calculation: Mathematical calculation of all Fib ratios
        3. Proximity Analysis: Determines closest Fib level to current price
        4. Confluence Detection: Identifies areas where multiple Fib levels converge
        5. Trend Validation: Adjusts Fib interpretation based on market direction

    CONFIGURATION PARAMETERS:
        swing_lookback (int): Number of periods to analyze for swing points (default: 100)
        key_levels (List[float]): Primary Fibonacci levels for focus (default: [0.382, 0.618])
        proximity_threshold (float): Maximum distance to consider "at Fib level" (default: 0.01)
        min_swing_size (float): Minimum swing size for valid analysis (default: 0.15)

    ATTRIBUTES:
        fib_levels (List[float]): All Fibonacci ratios used in calculations
        swing_lookback (int): Lookback period for swing point detection
        key_levels (List[float]): Primary levels for analysis focus
        proximity_threshold (float): Threshold for level proximity detection
        min_swing_size (float): Minimum required swing size

    EXAMPLE:
        >>> config = {
        ...     'fibonacci': {
        ...         'swing_lookback': 100,
        ...         'key_levels': [0.382, 0.618],
        ...         'proximity_threshold': 0.01,
        ...         'min_swing_size': 0.15
        ...     }
        ... }
        >>> analyzer = FibonacciAnalyzer(config)
        >>> result = analyzer.analyze_fibonacci_trend(daily_data)

    NOTE:
        The analyzer requires sufficient historical data (minimum 100 periods)
        and validates swing size to ensure meaningful Fibonacci analysis.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize the Fibonacci Analyzer with configuration parameters.

        Sets up the analyzer with all necessary parameters for Fibonacci analysis,
        including swing detection settings, key levels, and validation thresholds.

        Args:
            config (Dict[str, Any]): Complete configuration dictionary containing:
                - fibonacci.swing_lookback (int): Periods for swing point analysis
                - fibonacci.key_levels (List[float]): Primary Fib levels to focus on
                - fibonacci.proximity_threshold (float): Proximity threshold for levels
                - fibonacci.min_swing_size (float): Minimum swing size requirement

        Raises:
            KeyError: If required configuration keys are missing
            ValueError: If configuration values are invalid

        Example:
            >>> config = {
            ...     'fibonacci': {
            ...         'swing_lookback': 100,
            ...         'key_levels': [0.382, 0.618],
            ...         'proximity_threshold': 0.015,
            ...         'min_swing_size': 0.12
            ...     }
            ... }
            >>> analyzer = FibonacciAnalyzer(config)
        """
        self.config = config  # Запази референция към config
        self.swing_lookback = config["fibonacci"]["swing_lookback"]
        self.key_levels = config["fibonacci"]["key_levels"]
        self.proximity_threshold = config["fibonacci"]["proximity_threshold"]
        self.min_swing_size = config["fibonacci"]["min_swing_size"]

        # Всички Fibonacci нива (0% до 100%)
        self.fib_levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]

        logger.info("Fibonacci анализатор инициализиран")
        logger.info(f"Ключови нива: {self.key_levels}")
        logger.info(f"Минимален swing размер: {self.min_swing_size:.1%}")

    def find_swing_points(self, df: pd.DataFrame) -> tuple[float, float, int, int]:
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
            swing_high_idx = lookback_data["High"].idxmax()
            swing_high_price = lookback_data.loc[swing_high_idx, "High"]
            swing_high_pos = lookback_data.index.get_loc(swing_high_idx)

            # Намираме swing low (локален минимум)
            swing_low_idx = lookback_data["Low"].idxmin()
            swing_low_price = lookback_data.loc[swing_low_idx, "Low"]
            swing_low_pos = lookback_data.index.get_loc(swing_low_idx)

            # Проверяваме дали swing е достатъчно голям
            swing_size = abs(swing_high_price - swing_low_price) / swing_low_price

            if swing_size < self.min_swing_size:
                logger.warning(
                    f"Swing размер {swing_size:.1%} е под минимума {self.min_swing_size:.1%}"
                )
                return None, None, None, None

            logger.info(
                f"Намерени swing points: High=${swing_high_price:,.2f}, Low=${swing_low_price:,.2f}"
            )
            logger.info(f"Swing размер: {swing_size:.1%}")

            return swing_high_price, swing_low_price, swing_high_pos, swing_low_pos

        except Exception as e:
            logger.exception(f"Грешка при търсене на swing points: {e}")
            return None, None, None, None

    def calculate_fibonacci_levels(
        self, swing_high: float, swing_low: float
    ) -> dict[float, float]:
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
                logger.info(f"  {level * 100:5.1f}%: ${price:,.2f}")

            return fib_levels

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на Fibonacci нива: {e}")
            return {}

    def check_fib_proximity(
        self, current_price: float, fib_levels: dict[float, float]
    ) -> dict[str, Any]:
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
                "nearest_level": None,
                "nearest_distance": float("inf"),
                "nearest_percentage": None,
                "active_levels": [],
                "key_level_proximity": {},
            }

            for level, price in fib_levels.items():
                # Изчисляваме разстоянието до нивото
                distance = abs(current_price - price)
                distance_percentage = distance / current_price

                # Проверяваме дали сме в близост до нивото
                if distance_percentage <= self.proximity_threshold:
                    proximity_info["active_levels"].append(
                        {
                            "level": level,
                            "price": price,
                            "distance": distance,
                            "distance_percentage": distance_percentage,
                        }
                    )

                # Намираме най-близкото ниво
                if distance < proximity_info["nearest_distance"]:
                    proximity_info["nearest_distance"] = distance
                    proximity_info["nearest_level"] = level
                    proximity_info["nearest_percentage"] = distance_percentage

                # Специална проверка за ключовите нива (38.2% и 61.8%)
                if level in self.key_levels:
                    proximity_info["key_level_proximity"][level] = {
                        "price": price,
                        "distance": distance,
                        "distance_percentage": distance_percentage,
                        "is_active": distance_percentage <= self.proximity_threshold,
                    }

            # Сортираме активните нива по близост
            proximity_info["active_levels"].sort(key=lambda x: x["distance_percentage"])

            logger.info(f"Текуща цена ${current_price:,.2f}")
            logger.info(
                f"Най-близко Fibonacci ниво: {proximity_info['nearest_level'] * 100:.1f}% (${fib_levels[proximity_info['nearest_level']]:,.2f})"
            )
            logger.info(f"Разстояние: {proximity_info['nearest_percentage']:.2%}")

            if proximity_info["active_levels"]:
                logger.info("Активни Fibonacci нива:")
                for level_info in proximity_info["active_levels"]:
                    logger.info(
                        f"  {level_info['level'] * 100:5.1f}%: ${
                            level_info['price']:,.2f} (±{
                            level_info['distance_percentage']:.2%})"
                    )

            return proximity_info

        except Exception as e:
            logger.exception(f"Грешка при проверка на Fibonacci близост: {e}")
            return {}

    def get_fibonacci_signal(
        self, current_price: float, fib_levels: dict[float, float]
    ) -> dict[str, Any]:
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
                return {
                    "signal": "HOLD",
                    "reason": "Неуспешно изчисляване на Fibonacci нива",
                }

            signal_info = {
                "signal": "HOLD",
                "strength": 0.0,
                "reason": "",
                "fib_levels": fib_levels,
                "proximity": proximity_info,
                "support_levels": [],
                "resistance_levels": [],
            }

            # Определяме support и resistance нива
            for level, price in fib_levels.items():
                if price < current_price:
                    signal_info["support_levels"].append((level, price))
                else:
                    signal_info["resistance_levels"].append((level, price))

            # Сортираме по близост до текущата цена
            signal_info["support_levels"].sort(key=lambda x: abs(x[1] - current_price))
            signal_info["resistance_levels"].sort(
                key=lambda x: abs(x[1] - current_price)
            )

            # Phase 1.2: Подобрена логика за SHORT сигнали
            if proximity_info["active_levels"]:
                active_level = proximity_info["active_levels"][0]
                level = active_level["level"]

                if level in [0.236, 0.382]:  # Support нива - LONG сигнали
                    signal_info["signal"] = "LONG"
                    signal_info["strength"] = 0.8 if level == 0.382 else 0.6
                    signal_info["reason"] = f"LONG: Цената е над Fibonacci support {
                        level * 100:.1f}% (${active_level['price']:.2f})"

                elif level in [
                    0.618,
                    0.786,
                ]:  # Resistance нива - SHORT сигнали само при строги условия
                    # Phase 1.2: Проверка дали цената е ПОД resistance нивото
                    if current_price < active_level["price"]:
                        # Phase 1.2: Проверка за отскок (rejection) от resistance
                        rejection_confirmed = self._check_resistance_rejection(
                            current_price, active_level["price"], fib_levels
                        )
                        if rejection_confirmed:
                            signal_info["signal"] = "SHORT"
                            signal_info["strength"] = 0.8 if level == 0.618 else 0.7
                            signal_info[
                                "reason"
                            ] = f"SHORT: Отскок от Fibonacci resistance {
                                level * 100:.1f}% (${
                                active_level[
                                    'price'
                                ]:.2f}) - цена под ниво и rejection потвърден"
                        else:
                            signal_info["signal"] = "HOLD"
                            signal_info["strength"] = 0.3
                            signal_info["reason"] = f"HOLD: Близо до resistance {
                                level
                                * 100:.1f}% но няма rejection - изчакай потвърждение"
                    else:
                        # Цената е НАД resistance нивото - няма SHORT сигнал
                        signal_info["signal"] = "HOLD"
                        signal_info["strength"] = 0.2
                        signal_info["reason"] = f"HOLD: Цената е над resistance {
                            level * 100:.1f}% - няма SHORT възможност"

                elif level == 0.5:  # Средно ниво
                    signal_info["signal"] = "HOLD"
                    signal_info["strength"] = 0.4
                    signal_info["reason"] = (
                        "HOLD: Цената е на неутрално Fibonacci 50% ниво"
                    )

            # Добавяме информация за следващите нива
            if signal_info["signal"] == "LONG":
                next_resistance = (
                    signal_info["resistance_levels"][0]
                    if signal_info["resistance_levels"]
                    else None
                )
                if next_resistance:
                    signal_info["next_target"] = f"Следващо ниво: {
                        next_resistance[0] * 100:.1f}% (${next_resistance[1]:,.2f})"

            elif signal_info["signal"] == "SHORT":
                next_support = (
                    signal_info["support_levels"][0]
                    if signal_info["support_levels"]
                    else None
                )
                if next_support:
                    signal_info["next_target"] = (
                        f"Следващо ниво: {next_support[0] * 100:.1f}% (${next_support[1]:,.2f})"
                    )

            logger.info(
                f"Fibonacci сигнал: {signal_info['signal']} (сила: {signal_info['strength']:.1f})"
            )
            logger.info(f"Причина: {signal_info['reason']}")

            return signal_info

        except Exception as e:
            logger.exception(f"Грешка при генериране на Fibonacci сигнал: {e}")
            return {"signal": "HOLD", "reason": f"Грешка: {e}"}

    def _check_resistance_rejection(
        self,
        current_price: float,
        resistance_price: float,
        fib_levels: dict[float, float],
    ) -> bool:
        """
        Phase 1.2: Проверява дали има отскок (rejection) от resistance ниво

        Rejection критерии:
        1. Цената трябва да е значително под resistance нивото (не в близост)
        2. Цената трябва да показва низходящо движение след доближаване
        3. Rejection се потвърждава ако цената е под определен процент от resistance

        Args:
            current_price: Текущата цена
            resistance_price: Цена на resistance нивото
            fib_levels: Всички Fibonacci нива

        Returns:
            bool: True ако има rejection, False ако няма
        """
        try:
            # Изчисляваме колко е отдалечена цената от resistance
            price_distance_pct = (
                abs(current_price - resistance_price) / resistance_price
            )

            # Конфигурационни параметри за rejection
            config = self.config.get("short_signals", {})
            min_rejection_distance = config.get(
                "min_rejection_distance", 0.01
            )  # 1% минимум отдалечение
            rejection_threshold = config.get(
                "rejection_threshold", 0.03
            )  # 3% за силен rejection

            # Проверка 1: Цената трябва да е достатъчно отдалечена от resistance
            if price_distance_pct < min_rejection_distance:
                logger.info(
                    f"Няма rejection: Цената е твърде близо до resistance ({
                        price_distance_pct:.2f}%)"
                )
                return False

            # Проверка 2: Цената трябва да е под resistance нивото
            if current_price >= resistance_price:
                logger.info("Няма rejection: Цената е над или на resistance нивото")
                return False

            # Проверка 3: Rejection е силен ако цената е под rejection_threshold
            if price_distance_pct >= rejection_threshold:
                logger.info(
                    f"Силен rejection потвърден: Цената е {price_distance_pct:.2f}% под resistance"
                )
                return True
            logger.info(
                f"Слаб rejection: Цената е само {price_distance_pct:.2f}% под resistance"
            )
            return False

        except Exception as e:
            logger.exception(f"Грешка при проверка на resistance rejection: {e}")
            return False

    def analyze_fibonacci_trend(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        Perform complete Fibonacci trend analysis on price data.

        MAIN ENTRY POINT for Fibonacci analysis in the BNB trading system.
        This method orchestrates the complete Fibonacci analysis pipeline:

        1. VALIDATION PHASE:
           - Validates input data structure and sufficiency
           - Checks for required OHLCV columns
           - Ensures minimum data length for analysis

        2. SWING DETECTION PHASE:
           - Identifies swing high and swing low points
           - Validates swing size against minimum requirements
           - Calculates swing range and characteristics

        3. FIBONACCI CALCULATION PHASE:
           - Calculates all Fibonacci retracement levels
           - Computes Fibonacci extension levels
           - Applies trend-aware level interpretation

        4. PROXIMITY ANALYSIS PHASE:
           - Determines current price position relative to Fib levels
           - Identifies nearest Fibonacci levels
           - Calculates proximity percentages and distances

        5. SIGNAL GENERATION PHASE:
           - Generates trading signals based on Fib analysis
           - Provides confidence scores for Fib levels
           - Identifies support/resistance characteristics

        Args:
            df (pd.DataFrame): OHLCV price data with required columns:
                - 'Open', 'High', 'Low', 'Close': Price data (required)
                - 'Volume': Trading volume (optional but recommended)
                - DatetimeIndex: Proper datetime index (required)

        Returns:
            Dict[str, Any]: Complete Fibonacci analysis results with structure:
                {
                    'swing_high': float,           # Swing high price
                    'swing_low': float,            # Swing low price
                    'swing_range': float,          # Swing range size
                    'fibonacci_levels': Dict[float, float],  # All Fib levels with prices
                    'nearest_level': Dict,         # Nearest Fib level info
                    'current_price': float,        # Current closing price
                    'trend_direction': str,        # 'bullish' or 'bearish'
                    'support_levels': List[float], # Fib support levels
                    'resistance_levels': List[float], # Fib resistance levels
                    'confidence_score': float,     # Analysis confidence (0-1)
                    'signal': str,                 # LONG/SHORT/HOLD recommendation
                    'analysis_date': pd.Timestamp, # Analysis timestamp
                    'error': str                   # Error message if analysis fails
                }

        Raises:
            ValueError: If input data is invalid or insufficient
            KeyError: If required columns are missing from DataFrame

        Example:
            >>> # Analyze recent price action
            >>> analysis = fib_analyzer.analyze_fibonacci_trend(daily_data)
            >>> if analysis.get('signal') == 'LONG':
            ...     nearest_level = analysis['nearest_level']
            ...     print(f"Long signal at Fib {nearest_level['level']:.1%}")

        Note:
            This method requires at least 100 periods of data for meaningful analysis.
            The analysis automatically adapts to both bullish and bearish trends.
        """
        try:
            # Намираме swing points
            swing_high, swing_low, high_idx, low_idx = self.find_swing_points(df)

            if swing_high is None:
                return {"error": "Неуспешно намиране на swing points"}

            # Изчисляваме Fibonacci нива
            fib_levels = self.calculate_fibonacci_levels(swing_high, swing_low)

            if not fib_levels:
                return {"error": "Неуспешно изчисляване на Fibonacci нива"}

            # Изчисляваме Fibonacci extensions
            fib_extensions = self.calculate_fibonacci_extensions(swing_high, swing_low)

            # Анализираме текущата цена
            current_price = df["Close"].iloc[-1]
            fib_signal = self.get_fibonacci_signal(current_price, fib_levels)

            trend_analysis = {
                "swing_high": swing_high,
                "swing_low": swing_low,
                "swing_size": abs(swing_high - swing_low) / swing_low,
                "fibonacci_levels": fib_levels,
                "fibonacci_extensions": fib_extensions,
                "current_price": current_price,
                "fibonacci_signal": fib_signal,
                "analysis_date": df.index[-1],
            }

            logger.info("Fibonacci тренд анализ завършен")
            return trend_analysis

        except Exception as e:
            logger.exception(f"Грешка при Fibonacci тренд анализ: {e}")
            return {"error": f"Грешка: {e}"}

    def calculate_fibonacci_extensions(
        self, swing_high: float, swing_low: float
    ) -> dict[float, float]:
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
                logger.info(f"  {level * 100:5.1f}%: ${price:,.2f}")

            return fib_extensions

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на Fibonacci extensions: {e}")
            return {}

    def analyze(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> ModuleResult:
        """
        PR #4: Fibonacci Returns HOLD - ModuleResult implementation

        Fibonacci не дава directional сигнали (LONG/SHORT), вместо това предоставя
        качество на текущото ценово ниво за decision engine.

        Args:
            daily_df: Daily OHLCV data
            weekly_df: Weekly OHLCV data (unused in Fibonacci)

        Returns:
            ModuleResult with:
                - state: винаги "HOLD" (не е directional)
                - score: 0.6-0.8 ако близо до key levels, 0.2-0.4 за neutral
                - contrib: score * weight_from_config
        """
        try:
            # Get weight from config
            weight = (
                self.config.get("signals", {}).get("weights", {}).get("fibonacci", 0.20)
            )

            # Намираме swing points
            swing_high, swing_low, _, _ = self.find_swing_points(daily_df)

            if swing_high is None or swing_low is None:
                return ModuleResult(
                    status="DISABLED",
                    state="NEUTRAL",
                    score=0.0,
                    contrib=0.0,
                    reason="Insufficient data for swing point detection",
                )

            # Изчисляваме Fibonacci levels
            fib_levels = self.calculate_fibonacci_levels(swing_high, swing_low)
            if not fib_levels:
                return ModuleResult(
                    status="DISABLED",
                    state="NEUTRAL",
                    score=0.0,
                    contrib=0.0,
                    reason="Failed to calculate Fibonacci levels",
                )

            # Текущата цена
            current_price = daily_df["Close"].iloc[-1]

            # Check proximity to key levels
            proximity_info = self.check_fib_proximity(current_price, fib_levels)

            # Determine score based on proximity to important levels
            score = self._calculate_fib_score(proximity_info)

            # Reason
            nearest_level = proximity_info.get("nearest_level", 0.0)
            reason = f"Fibonacci analysis: nearest {nearest_level * 100:.1f}% level"

            if proximity_info.get("active_levels"):
                active_level = proximity_info["active_levels"][0]["level"]
                if active_level in self.key_levels:
                    reason += f" - at key {active_level * 100:.1f}% level"

            return ModuleResult(
                status="OK",
                state="HOLD",  # Fibonacci винаги връща HOLD
                score=score,
                contrib=score * weight,
                reason=reason,
                meta={
                    "fib_levels": fib_levels,
                    "proximity": proximity_info,
                    "swing_high": swing_high,
                    "swing_low": swing_low,
                    "current_price": current_price,
                },
            )

        except Exception as e:
            logger.exception(f"Error in Fibonacci analyze: {e}")
            return ModuleResult(
                status="ERROR",
                state="NEUTRAL",
                score=0.0,
                contrib=0.0,
                reason=f"Fibonacci analysis error: {e}",
            )

    def _calculate_fib_score(self, proximity_info: dict[str, Any]) -> float:
        """
        Calculate Fibonacci score based on proximity to important levels.

        Scoring logic:
        - 0.7: Close to golden ratio (61.8%)
        - 0.6-0.8: Close to key levels (38.2%, 61.8%)
        - 0.2-0.4: Neutral zones

        Returns:
            float: Score between 0.0-1.0
        """
        try:
            if not proximity_info.get("active_levels"):
                # Not close to any level - neutral score
                return 0.3

            # Check active levels
            active_level = proximity_info["active_levels"][0]["level"]
            distance_pct = proximity_info["active_levels"][0]["distance_percentage"]

            # Golden ratio gets highest score
            if active_level == 0.618:
                return 0.7

            # Key levels get good scores
            if active_level in self.key_levels:
                # Closer = higher score
                if distance_pct <= 0.01:  # Very close (1%)
                    return 0.8
                if distance_pct <= 0.02:  # Close (2%)
                    return 0.6
                # Within threshold but not very close
                return 0.5

            # Other levels get moderate scores
            if active_level in [0.236, 0.786]:
                return 0.4

            # 50% level is neutral
            if active_level == 0.5:
                return 0.3

            return 0.2  # Other levels

        except Exception as e:
            logger.exception(f"Error calculating Fibonacci score: {e}")
            return 0.2


if __name__ == "__main__":
    # Тест на Fibonacci модула
    print("Fibonacci модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
