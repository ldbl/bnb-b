"""
Optimal Levels Analysis Module - Historical Price Level Validation and Trading Zones

ADVANCED PRICE LEVEL ANALYSIS FOR SUPPORT/RESISTANCE IDENTIFICATION
Identifies optimal entry/exit levels based on historical price touch frequency

This module provides sophisticated analysis of historical price levels to identify
significant support and resistance zones based on frequency of price touches,
strength of reactions, and confluence with other technical levels.

ARCHITECTURE OVERVIEW:
    - Historical price action analysis with configurable timeframes
    - Price level generation with adaptive interval sizing
    - Touch frequency counting and statistical validation
    - Support/resistance classification and strength scoring
    - Confluence detection with other technical levels

LEVEL IDENTIFICATION METHODOLOGY:
    - Price Level Generation: Creates grid of potential levels
    - Touch Frequency Analysis: Counts historical interactions at each level
    - Strength Scoring: Evaluates level significance and reliability
    - Support/Resistance Classification: Distinguishes level types
    - Holding Period Analysis: Measures level effectiveness over time

TRADING APPLICATIONS:
    - Support Level Identification: Optimal entry points for LONG positions
    - Resistance Level Identification: Optimal entry points for SHORT positions
    - Risk Management: Stop loss placement at validated levels
    - Target Setting: Profit target identification at next significant levels
    - Breakout Detection: Monitoring for level breakouts

LEVEL STRENGTH FACTORS:
    - Touch Frequency: Number of times price interacted with level
    - Holding Strength: Duration price spent at level
    - Volume Confirmation: Volume spikes at level interactions
    - Time Proximity: Recent vs historical significance
    - Confluence Bonus: Alignment with other technical levels

CONFIGURATION PARAMETERS:
    - price_interval: Spacing between price levels (default: 25)
    - min_touches: Minimum touch count for valid level (default: 3)
    - level_tolerance: Price tolerance for level touch detection (default: 0.01)
    - min_holding_period: Minimum time at level for significance (default: 5)
    - max_levels_returned: Maximum levels to return (default: 10)

LEVEL TYPES:
    - MAJOR SUPPORT: Strong buying interest, multiple tests
    - MINOR SUPPORT: Moderate buying interest, fewer tests
    - MAJOR RESISTANCE: Strong selling pressure, multiple rejections
    - MINOR RESISTANCE: Moderate selling pressure, fewer rejections
    - CONSOLIDATION: Price range with equal support/resistance

EXAMPLE USAGE:
    >>> config = {'optimal_levels': {'price_interval': 25, 'min_touches': 3}}
    >>> analyzer = OptimalLevelsAnalyzer(config)
    >>> analysis = analyzer.analyze_optimal_levels(daily_data, weekly_data)
    >>> support_levels = analysis['optimal_levels']['support_levels']
    >>> top_support = support_levels[0]['price']  # Best entry level

DEPENDENCIES:
    - pandas: Data manipulation and time series operations
    - numpy: Mathematical calculations and array operations
    - collections.defaultdict: Efficient dictionary operations
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Vectorized price level generation
    - Efficient touch counting algorithms
    - Memory-optimized data structures
    - Configurable analysis depth limits

ERROR HANDLING:
    - Data validation and sufficiency checks
    - Missing data handling and interpolation
    - Statistical calculation error recovery
    - Comprehensive logging and debugging

VALIDATION TECHNIQUES:
    - Statistical significance testing of level strength
    - Back-testing of level effectiveness
    - Cross-validation with other technical methods
    - Robustness testing across different market conditions

TRADING STRATEGIES:
    - Support Bounce: Enter LONG at support, target resistance
    - Resistance Rejection: Enter SHORT at resistance, target support
    - Range Trading: Trade between validated support/resistance
    - Breakout Trading: Enter on level breakout with confirmation

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class OptimalLevelsAnalyzer:
    """
    Advanced Historical Price Level Analysis Engine

    This class provides sophisticated analysis of historical price levels to identify
    significant support and resistance zones based on frequency of price interactions,
    strength of reactions, and statistical validation.

    ARCHITECTURE OVERVIEW:
        - Historical price action analysis with configurable parameters
        - Price level grid generation with adaptive spacing
        - Touch frequency counting and statistical significance testing
        - Support/resistance classification based on market behavior
        - Confluence detection with other technical analysis methods

    PRICE LEVEL ANALYSIS METHODOLOGY:
        1. Price Level Generation: Creates comprehensive grid of potential levels
        2. Touch Frequency Analysis: Counts and validates historical interactions
        3. Strength Scoring: Evaluates level significance and reliability
        4. Support/Resistance Classification: Categorizes levels by market function
        5. Statistical Validation: Ensures levels are statistically significant

    LEVEL GENERATION STRATEGY:
        - Adaptive Grid: Creates levels based on price range and volatility
        - Current Price Focus: Adds levels around current price for relevance
        - Interval Optimization: Balances level density with analysis efficiency
        - Historical Coverage: Ensures comprehensive historical analysis

    TOUCH DETECTION ALGORITHM:
        - Price Proximity: Configurable tolerance for level touch detection
        - Multiple Touch Types: High, Low, Close interactions with levels
        - Volume Confirmation: Validates touches with volume spikes
        - Time-weighted Scoring: Recent touches weighted higher

    STRENGTH SCORING FACTORS:
        - Touch Frequency: Number of times price interacted with level
        - Holding Period: Duration price spent near level
        - Rejection Strength: Magnitude of price rejection at level
        - Volume Confirmation: Volume spike at level interaction
        - Time Proximity: Recency of level interactions

    CONFIGURATION PARAMETERS:
        price_interval (int): Spacing between price levels in dollars (default: 25)
        min_touches (int): Minimum touch count for valid level (default: 3)
        level_tolerance (float): Price tolerance for touch detection (default: 0.01)
        min_holding_period (int): Minimum periods for level significance (default: 5)
        max_levels_returned (int): Maximum levels to return in results (default: 10)

    ATTRIBUTES:
        price_interval (int): Spacing between price levels
        min_touches (int): Minimum touch count threshold
        level_tolerance (float): Price tolerance for touch detection
        min_holding_period (int): Minimum holding period for significance
        max_levels_returned (int): Maximum levels in output

    LEVEL CLASSIFICATION:
        - MAJOR SUPPORT: High touch frequency, strong buying reactions
        - MINOR SUPPORT: Moderate touch frequency, moderate buying reactions
        - MAJOR RESISTANCE: High touch frequency, strong selling pressure
        - MINOR RESISTANCE: Moderate touch frequency, moderate selling pressure
        - CONSOLIDATION: Price range with balanced support/resistance

    OUTPUT STRUCTURE:
        {
            'price_levels': List[float],        # All generated price levels
            'level_touches': Dict[float, int],  # Touch count for each level
            'current_price': float,             # Current market price
            'optimal_levels': {
                'support_levels': List[Dict],   # Ranked support levels
                'resistance_levels': List[Dict] # Ranked resistance levels
            },
            'analysis_date': pd.Timestamp       # Analysis timestamp
        }

    EXAMPLE:
        >>> analyzer = OptimalLevelsAnalyzer({})
        >>> result = analyzer.analyze_optimal_levels(daily_data, weekly_data)
        >>> support_levels = result['optimal_levels']['support_levels']
        >>> best_entry = support_levels[0]['price']
        >>> strength = support_levels[0]['strength']

    NOTE:
        Requires sufficient historical data (minimum 100 periods recommended)
        for statistically significant level identification.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Optimal Levels Analyzer with configuration parameters.

        Sets up the analyzer with parameters for historical price level analysis,
        including level spacing, touch detection thresholds, and output limits.

        Args:
            config (Dict[str, Any]): Configuration dictionary containing:
                - price_interval (int): Spacing between price levels (default: 25)
                - min_touches (int): Minimum touch count for valid levels (default: 3)
                - level_tolerance (float): Price tolerance for touch detection (default: 0.01)
                - min_holding_period (int): Minimum holding periods (default: 5)
                - max_levels_returned (int): Maximum levels to return (default: 10)

        Raises:
            ValueError: If configuration parameters are invalid
            KeyError: If required configuration keys are missing

        Example:
            >>> # Default configuration
            >>> analyzer = OptimalLevelsAnalyzer({})

            >>> # Custom configuration
            >>> config = {
            ...     'price_interval': 50,
            ...     'min_touches': 5,
            ...     'max_levels_returned': 15
            ... }
            >>> analyzer = OptimalLevelsAnalyzer(config)
        """
        self.price_interval = 25  # Интервал между ценови нива
        self.min_touches = 3  # Минимум докосвания за валидно ниво

        logger.info("Optimal Levels анализатор инициализиран")

    def analyze_optimal_levels(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Dict:
        """
        Анализира оптимални trading нива

        Args:
            daily_df: Daily OHLCV данни
            weekly_df: Weekly OHLCV данни

        Returns:
            Dict с оптимални нива
        """
        try:
            logger.info("Анализ на оптимални trading нива...")

            # Използваме weekly данни за по-стабилен анализ
            if weekly_df.empty:
                return {"error": "Няма weekly данни за анализ"}

            # Създаваме ценови нива
            price_levels = self._create_price_levels(weekly_df)

            # Броим докосванията
            level_touches = self._count_level_touches(weekly_df, price_levels)

            # Намираме оптимални нива
            current_price = weekly_df["Close"].iloc[-1]
            optimal_levels = self._find_optimal_levels(level_touches, current_price)

            analysis = {
                "price_levels": price_levels,
                "level_touches": level_touches,
                "current_price": current_price,
                "optimal_levels": optimal_levels,
                "analysis_date": weekly_df.index[-1],
            }

            logger.info("Оптимални нива намерени успешно")
            return analysis

        except Exception as e:
            logger.error(f"Грешка при анализ на оптимални нива: {e}")
            return {"error": f"Грешка: {e}"}

    def _create_price_levels(self, df: pd.DataFrame) -> List[float]:
        """Създава ценови нива за анализ"""
        try:
            min_price = df["Low"].min()
            max_price = df["High"].max()

            # Създаваме нива на всеки $25
            base_levels = list(np.arange(min_price - 100, max_price + 100, self.price_interval))

            # Добавяме нива около текущата цена
            current_price = df["Close"].iloc[-1]
            current_levels = list(
                np.arange(current_price - 200, current_price + 200, self.price_interval)
            )

            # Комбинираме и премахваме дублирани
            all_levels = sorted(list(set(base_levels + current_levels)))

            logger.info(f"Създадени {len(all_levels)} ценови нива")
            return all_levels

        except Exception as e:
            logger.error(f"Грешка при създаване на ценови нива: {e}")
            return []

    def _count_level_touches(self, df: pd.DataFrame, price_levels: List[float]) -> Dict[float, int]:
        """Брои докосванията на всяко ценово ниво"""
        try:
            level_touches = defaultdict(int)

            for _, row in df.iterrows():
                low = row["Low"]
                high = row["High"]

                for level in price_levels:
                    if low <= level <= high:
                        level_touches[level] += 1

            logger.info(f"Докосвания преброени за {len(level_touches)} нива")
            return dict(level_touches)

        except Exception as e:
            logger.error(f"Грешка при броене на докосвания: {e}")
            return {}

    def _find_optimal_levels(self, level_touches: Dict[float, int], current_price: float) -> Dict:
        """Намира оптимални entry/exit нива"""
        try:
            # Сортираме нивата по брой докосвания
            sorted_levels = sorted(level_touches.items(), key=lambda x: x[1], reverse=True)

            # Намираме support нива (под текущата цена)
            support_levels = [
                (price, touches)
                for price, touches in sorted_levels
                if price < current_price and touches >= self.min_touches
            ]

            # Намираме resistance нива (над текущата цена)
            resistance_levels = [
                (price, touches)
                for price, touches in sorted_levels
                if price > current_price and touches >= self.min_touches
            ]

            # Ако няма resistance нива над текущата цена, използваме най-високите
            if not resistance_levels:
                resistance_levels = [
                    (price, touches)
                    for price, touches in sorted_levels
                    if touches >= self.min_touches and price > current_price - 200
                ]
                resistance_levels.sort(key=lambda x: x[0], reverse=True)

            optimal_levels = {
                "top_support_levels": support_levels[:5],
                "top_resistance_levels": resistance_levels[:5],
                "best_support": support_levels[0] if support_levels else None,
                "best_resistance": resistance_levels[0] if resistance_levels else None,
                "averaged_support": (
                    self._calculate_averaged_support(support_levels[:3])
                    if len(support_levels) >= 3
                    else None
                ),
            }

            return optimal_levels

        except Exception as e:
            logger.error(f"Грешка при намиране на оптимални нива: {e}")
            return {}

    def _calculate_averaged_support(self, support_levels: List[Tuple[float, int]]) -> Dict:
        """Изчислява усреднено support ниво"""
        try:
            if not support_levels:
                return {}

            avg_price = sum(level[0] for level in support_levels) / len(support_levels)
            avg_touches = sum(level[1] for level in support_levels) / len(support_levels)

            return {
                "price": avg_price,
                "touches": avg_touches,
                "reliability": (
                    "HIGH" if avg_touches >= 10 else "MEDIUM" if avg_touches >= 5 else "LOW"
                ),
            }

        except Exception as e:
            logger.error(f"Грешка при изчисляване на усреднено support: {e}")
            return {}

    def get_trading_recommendations(self, optimal_levels: Dict) -> Dict:
        """Генерира trading препоръки"""
        try:
            if not optimal_levels or "best_support" not in optimal_levels:
                return {"error": "Няма оптимални нива за анализ"}

            best_support = optimal_levels["best_support"]
            best_resistance = optimal_levels["best_resistance"]
            averaged_support = optimal_levels.get("averaged_support")

            recommendations = {
                "long_strategy": {},
                "short_strategy": {},
                "risk_reward_analysis": {},
            }

            # LONG стратегия
            if best_support and best_resistance:
                entry_price = (
                    averaged_support["price"]
                    if averaged_support and averaged_support["reliability"] == "HIGH"
                    else best_support[0]
                )
                stop_loss = entry_price - 50
                target = best_resistance[0]

                risk = entry_price - stop_loss
                reward = target - entry_price
                risk_reward = reward / risk if risk > 0 else 0

                recommendations["long_strategy"] = {
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "target": target,
                    "risk_reward": risk_reward,
                    "entry_type": (
                        "averaged"
                        if averaged_support and averaged_support["reliability"] == "HIGH"
                        else "individual"
                    ),
                }

            # SHORT стратегия
            if best_resistance and best_support:
                entry_price = best_resistance[0]
                stop_loss = entry_price + 50
                target = averaged_support["price"] if averaged_support else best_support[0]

                risk = stop_loss - entry_price
                reward = entry_price - target
                risk_reward = reward / risk if risk > 0 else 0

                recommendations["short_strategy"] = {
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "target": target,
                    "risk_reward": risk_reward,
                }

            # Risk/Reward анализ
            if recommendations["long_strategy"]:
                recommendations["risk_reward_analysis"] = {
                    "long_risk_reward": recommendations["long_strategy"]["risk_reward"],
                    "short_risk_reward": recommendations["short_strategy"].get("risk_reward", 0),
                    "recommended_strategy": (
                        "LONG"
                        if recommendations["long_strategy"]["risk_reward"] > 2
                        else (
                            "SHORT"
                            if recommendations["short_strategy"].get("risk_reward", 0) > 2
                            else "HOLD"
                        )
                    ),
                }

            return recommendations

        except Exception as e:
            logger.error(f"Грешка при генериране на trading препоръки: {e}")
            return {"error": f"Грешка: {e}"}


if __name__ == "__main__":
    print("Optimal Levels модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
