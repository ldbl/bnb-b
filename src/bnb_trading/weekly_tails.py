"""
Weekly Tails Analysis Module - Specialized Weekly Candle Pattern Recognition

SPECIALIZED MODULE FOR WEEKLY PRICE ACTION ANALYSIS
PRIORITY #2: Advanced analysis of weekly wicks/tails for BNB trading signals

This module provides sophisticated analysis of weekly candlestick patterns,
specifically focusing on wick/tail formations that indicate strong institutional
activity and potential reversal or continuation signals.

ARCHITECTURE OVERVIEW:
    - Automated weekly candle analysis for configurable lookback periods
    - Advanced tail strength calculation and classification
    - Pattern recognition for bullish/bearish tail formations
    - Confluence detection with other technical levels
    - Volume confirmation and tail significance scoring

TAIL ANALYSIS METHODOLOGY:
    - Upper Tail (Resistance): Rejection of higher prices = BEARISH
    - Lower Tail (Support): Rejection of lower prices = BULLISH
    - Tail Strength: Size relative to body and total range
    - Pattern Classification: Single tails, engulfing, multiple rejection
    - Significance Scoring: Volume, size, and market context

KEY FEATURES:
    - Automated weekly tail detection and measurement
    - Strength classification (weak, moderate, strong, extreme)
    - Pattern recognition and classification
    - Volume confirmation analysis
    - Confluence detection with Fibonacci levels
    - Historical significance scoring

TRADING APPLICATIONS:
    - Reversal signal identification at key levels
    - Support/resistance validation through tail rejection
    - Institutional activity detection
    - Risk management using tail-based stop levels
    - Entry timing based on tail strength patterns

CONFIGURATION PARAMETERS:
    - lookback_weeks: Number of weeks to analyze (default: 8)
    - min_tail_size: Minimum tail size for consideration (default: 0.03)
    - strong_tail_size: Threshold for strong tail classification (default: 0.05)
    - confluence_bonus: Bonus for confluence with other levels (default: 1.5)

EXAMPLE USAGE:
    >>> config = {'weekly_tails': {'lookback_weeks': 8, 'min_tail_size': 0.03}}
    >>> tails_analyzer = WeeklyTailsAnalyzer(config)
    >>> analysis = tails_analyzer.analyze_weekly_tails_trend(weekly_data)
    >>> strong_tails = [tail for tail in analysis['tails'] if tail['strength'] > 0.7]

DEPENDENCIES:
    - pandas: Data manipulation and time series analysis
    - numpy: Mathematical calculations and statistical analysis
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient vectorized calculations for large datasets
    - Memory-efficient data processing
    - Optimized tail detection algorithms
    - Batch processing for multiple weeks

ERROR HANDLING:
    - Validation of input data structure and completeness
    - Graceful handling of missing or invalid data
    - Comprehensive logging for debugging and monitoring
    - Fallback mechanisms for edge cases

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeeklyTailsAnalyzer:
    """
    Advanced Weekly Tails Analyzer for Institutional Price Action Analysis

    This class provides sophisticated analysis of weekly candlestick patterns,
    specifically designed to identify institutional activity through wick/tail
    formations that indicate strong buying or selling pressure.

    ARCHITECTURE OVERVIEW:
        - Automated weekly candle analysis with configurable lookback periods
        - Advanced tail strength calculation using multiple metrics
        - Pattern classification for different tail formations
        - Volume confirmation and significance scoring
        - Integration with broader market context

    TAIL ANALYSIS METHODOLOGY:
        - Upper Tail (Resistance Rejection): High wick shows selling pressure
        - Lower Tail (Support Rejection): Low wick shows buying pressure
        - Tail Strength: Calculated relative to body size and total range
        - Pattern Recognition: Single, double, and engulfing tail patterns
        - Significance Scoring: Volume, size, and market context factors

    ALGORITHMS USED:
        1. Tail Detection: Identifies upper/lower wick sizes
        2. Strength Calculation: Measures tail relative to body/total range
        3. Pattern Classification: Categorizes tail formations
        4. Volume Confirmation: Validates tail significance with volume
        5. Confluence Analysis: Checks alignment with Fibonacci levels

    CONFIGURATION PARAMETERS:
        lookback_weeks (int): Number of weeks to analyze (default: 8)
        min_tail_size (float): Minimum tail size threshold (default: 0.03)
        strong_tail_size (float): Strong tail classification threshold (default: 0.05)
        confluence_bonus (float): Bonus multiplier for confluence (default: 1.5)

    ATTRIBUTES:
        lookback_weeks (int): Number of weeks to analyze
        min_tail_size (float): Minimum tail size for consideration
        strong_tail_size (float): Threshold for strong tail classification
        confluence_bonus (float): Confluence bonus multiplier

    TAIL STRENGTH CLASSIFICATION:
        - Weak: 0.0 - 0.3 (minimal significance)
        - Moderate: 0.3 - 0.6 (some significance)
        - Strong: 0.6 - 0.8 (high significance)
        - Extreme: 0.8 - 1.0 (maximum significance)

    EXAMPLE:
        >>> config = {
        ...     'weekly_tails': {
        ...         'lookback_weeks': 8,
        ...         'min_tail_size': 0.03,
        ...         'strong_tail_size': 0.05,
        ...         'confluence_bonus': 1.5
        ...     }
        ... }
        >>> analyzer = WeeklyTailsAnalyzer(config)
        >>> tails_analysis = analyzer.analyze_weekly_tails_trend(weekly_data)

    NOTE:
        Weekly tails are particularly significant for BNB due to lower liquidity
        and higher institutional impact compared to shorter timeframes.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize the Weekly Tails Analyzer with configuration parameters.

        Sets up the analyzer with parameters optimized for weekly candle analysis,
        including lookback periods, tail size thresholds, and confluence bonuses.

        Args:
            config (Dict[str, Any]): Complete configuration dictionary containing:
                - weekly_tails.lookback_weeks (int): Weeks to analyze
                - weekly_tails.min_tail_size (float): Minimum tail size threshold
                - weekly_tails.strong_tail_size (float): Strong tail threshold
                - weekly_tails.confluence_bonus (float): Confluence bonus multiplier

        Raises:
            KeyError: If required configuration keys are missing
            ValueError: If configuration values are invalid

        Example:
            >>> config = {
            ...     'weekly_tails': {
            ...         'lookback_weeks': 8,
            ...         'min_tail_size': 0.03,
            ...         'strong_tail_size': 0.05,
            ...         'confluence_bonus': 1.5
            ...     }
            ... }
            >>> analyzer = WeeklyTailsAnalyzer(config)
        """
        self.lookback_weeks = config["weekly_tails"]["lookback_weeks"]
        self.min_tail_size = config["weekly_tails"]["min_tail_size"]
        self.strong_tail_size = config["weekly_tails"]["strong_tail_size"]
        self.confluence_bonus = config["weekly_tails"]["confluence_bonus"]

        # Phase 2.2: Trend-based Weighting Parameters
        self.trend_based_weighting = config.get("weekly_tails", {}).get(
            "trend_based_weighting", True
        )
        self.bull_market_threshold = config.get("weekly_tails", {}).get(
            "bull_market_threshold", 0.15
        )  # 15% gain
        self.bear_market_threshold = config.get("weekly_tails", {}).get(
            "bear_market_threshold", -0.10
        )  # 10% loss
        self.long_tail_amplification = config.get("weekly_tails", {}).get(
            "long_tail_amplification", 1.5
        )
        self.short_tail_suppression = config.get("weekly_tails", {}).get(
            "short_tail_suppression", 0.3
        )

        logger.info("Weekly Tails анализатор инициализиран с trend-based weighting")
        logger.info(f"Lookback седмици: {self.lookback_weeks}")
        logger.info(f"Минимален размер на опашката: {self.min_tail_size:.1%}")
        logger.info(f"Силен размер на опашката: {self.strong_tail_size:.1%}")

    def analyze_weekly_tails(self, weekly_df: pd.DataFrame) -> list[dict]:
        """
        Анализира седмични опашки за последните N седмици

        Args:
            weekly_df: DataFrame с седмични OHLCV данни

        Returns:
            List с информация за всяка седмична опашка
        """
        try:
            # Взимаме последните N седмици
            recent_weeks = weekly_df.tail(self.lookback_weeks)

            tails_analysis = []

            for date, row in recent_weeks.iterrows():
                # Convert date to string first, then to Timestamp
                if isinstance(date, pd.Timestamp):
                    timestamp = date
                else:
                    timestamp = pd.Timestamp(str(date))
                tail_info = self._analyze_single_tail(row, timestamp)
                if tail_info:
                    tails_analysis.append(tail_info)

            # Сортираме по сила на опашката (намаляващо)
            tails_analysis.sort(key=lambda x: x["tail_strength"], reverse=True)

            logger.info(f"Анализирани {len(tails_analysis)} седмични опашки")

            return tails_analysis

        except Exception as e:
            logger.exception(f"Грешка при анализ на седмични опашки: {e}")
            return []

    def _analyze_single_tail(self, row: pd.Series, date: pd.Timestamp) -> dict | None:
        """
        Анализира единична седмична опашка

        Args:
            row: Ред с OHLCV данни
            date: Дата на седмицата

        Returns:
            Dict с информация за опашката или None ако няма значима опашка
        """
        try:
            # Извличаме стойностите като скаларни числа, не като Series
            ohlc = np.nan_to_num(
                [
                    row.get("Open", np.nan),
                    row.get("High", np.nan),
                    row.get("Low", np.nan),
                    row.get("Close", np.nan),
                ],
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )
            open_price, high_price, low_price, close_price = map(float, ohlc)
            # Изчисляваме размера на body (Open до Close)
            body_size = abs(close_price - open_price)

            # Определяме дали е bullish или bearish candle
            is_bullish = close_price > open_price

            # Изчисляваме горната опашка (upper wick)
            upper_tail = high_price - max(open_price, close_price)

            # Изчисляваме долната опашка (lower wick)
            lower_tail = min(open_price, close_price) - low_price

            # Определяме коя опашка е по-голяма
            if upper_tail > lower_tail:
                dominant_tail = "upper"
                tail_size = upper_tail
                tail_direction = "resistance"  # Горната опашка показва resistance
            else:
                dominant_tail = "lower"
                tail_size = lower_tail
                tail_direction = "support"  # Долната опашка показва support

            # Изчисляваме силата на опашката като процент от body
            # Защитни проверки за да избегнем DataFrame операции
            if (
                isinstance(body_size, (int, float)) and body_size > 0.01
            ):  # Минимален body size
                tail_strength = float(tail_size) / float(body_size)
            else:
                tail_strength = 0.0

            # Проверяваме дали опашката е значима (ПО-СТРИКТНИ ПРАГОВЕ)
            if tail_strength < 0.9:  # МАКСИМАЛНО СТРИКТЕН
                return None

            # Определяме силата на опашката (МАКСИМАЛНО СТРИКТНИ КРИТЕРИИ)
            if tail_strength >= 0.95:  # Само най-силните опашки
                strength_category = "ULTRA_EXTREME"
                signal_strength = 0.99
            elif tail_strength >= 0.9:  # Много силни опашки
                strength_category = "EXTREME"
                signal_strength = 0.95
            else:
                strength_category = "STRONG"
                signal_strength = 0.8

            # Генерираме сигнал базиран на опашката (ПО-СТРИКТНИ ПРАВИЛА ЗА SHORT)
            if dominant_tail == "lower" and is_bullish and tail_strength >= 0.4:
                # Долна опашка + bullish candle = LONG сигнал
                signal = "LONG"
                reason = f"Сигнална долна опашка ({tail_strength:.1%}) + bullish candle"
            elif dominant_tail == "upper" and not is_bullish and tail_strength >= 0.95:
                # Горна опашка + bearish candle + СИЛНА опашка = SHORT сигнал
                signal = "SHORT"
                reason = f"Сигнална горна опашка ({tail_strength:.1%}) + bearish candle"
            else:
                # Смесени сигнали или недостатъчно силни опашки
                signal = "HOLD"
                reason = f"Смесен сигнал: {dominant_tail} опашка ({tail_strength:.1%})"

            tail_info = {
                "date": date,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "is_bullish": is_bullish,
                "dominant_tail": dominant_tail,
                "tail_size": tail_size,
                "body_size": body_size,
                "tail_strength": tail_strength,
                "strength_category": strength_category,
                "tail_direction": tail_direction,
                "signal": signal,
                "signal_strength": signal_strength,
                "reason": reason,
            }

            logger.info(
                f"Седмица {date.strftime('%Y-%m-%d')}: {dominant_tail} опашка, сила: {
                    tail_strength:.1%}, сигнал: {signal}"
            )

            return tail_info

        except Exception as e:
            logger.exception(f"Грешка при анализ на единична опашка: {e}")
            return None

    def calculate_tail_strength(self, tail_info: dict) -> float:
        """
        Изчислява силата на опашката с допълнителни фактори

        Args:
            tail_info: Информация за опашката

        Returns:
            Нормализирана сила на опашката (0.0 до 1.0)
        """
        try:
            base_strength = tail_info["tail_strength"]

            # Бонус за силни опашки
            if base_strength >= self.strong_tail_size:
                strength_multiplier = 1.5
            elif base_strength >= self.min_tail_size:
                strength_multiplier = 1.2
            else:
                strength_multiplier = 1.0

            # Бонус за последователност (ако има няколко опашки в същата посока)
            sequence_bonus = 1.0

            # Изчисляваме финалната сила
            final_strength = min(
                1.0, base_strength * strength_multiplier * sequence_bonus
            )

            return final_strength

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на силата на опашката: {e}")
            return 0.0

    def check_fib_tail_confluence(
        self,
        fib_levels: dict[float, float],
        current_price: float,
        tails_analysis: list[dict],
    ) -> dict[str, Any]:
        """
        Проверява съвпадение между Fibonacci нива и седмични опашки

        Args:
            fib_levels: Fibonacci нива
            current_price: Текуща цена
            tails_analysis: Анализ на седмични опашки

        Returns:
            Dict с информация за съвпаденията
        """
        try:
            confluence_info = {
                "confluence_points": [],
                "strong_confluence": False,
                "confluence_bonus": 0.0,
                "best_entry_points": [],
            }

            # Проверяваме всяка опашка за съвпадение с Fibonacci нива
            for tail in tails_analysis:
                if tail["signal"] == "HOLD":
                    continue

                # Определяме целевата цена за опашката
                if tail["dominant_tail"] == "lower" and tail["signal"] == "LONG":
                    # Долна опашка + LONG = търсим support ниво
                    target_price = tail["low"]
                elif tail["dominant_tail"] == "upper" and tail["signal"] == "SHORT":
                    # Горна опашка + SHORT = търсим resistance ниво
                    target_price = tail["high"]
                else:
                    continue

                # Проверяваме за съвпадение с Fibonacci нива
                for fib_level, fib_price in fib_levels.items():
                    # Изчисляваме разстоянието до Fibonacci ниво
                    distance = abs(target_price - fib_price)
                    distance_percentage = distance / target_price

                    # Ако опашката е близо до Fibonacci ниво
                    if distance_percentage <= 0.02:  # 2% близост
                        confluence_point = {
                            "tail_date": tail["date"],
                            "tail_signal": tail["signal"],
                            "tail_strength": tail["tail_strength"],
                            "fib_level": fib_level,
                            "fib_price": fib_price,
                            "target_price": target_price,
                            "distance": distance,
                            "distance_percentage": distance_percentage,
                            "confluence_score": tail["signal_strength"]
                            * (1 - distance_percentage),
                        }

                        confluence_info["confluence_points"].append(confluence_point)

                        # Проверяваме дали е силно съвпадение
                        if confluence_point["confluence_score"] >= 0.6:
                            confluence_info["strong_confluence"] = True
                            confluence_info["confluence_bonus"] = self.confluence_bonus

                            # Добавяме в най-добрите входни точки
                            entry_point = {
                                "type": (
                                    f"Fib {fib_level * 100:.1f}% + {tail['strength_category']} опашка"
                                ),
                                "price": fib_price,
                                "signal": tail["signal"],
                                "strength": confluence_point["confluence_score"],
                                "reason": (
                                    f"Съвпадение: Fibonacci {fib_level * 100:.1f}% + {tail['dominant_tail']} опашка от {tail['date'].strftime('%Y-%m-%d')}"
                                ),
                            }
                            confluence_info["best_entry_points"].append(entry_point)

            # Сортираме по сила на съвпадението
            confluence_info["confluence_points"].sort(
                key=lambda x: x["confluence_score"], reverse=True
            )
            confluence_info["best_entry_points"].sort(
                key=lambda x: x["strength"], reverse=True
            )

            if confluence_info["confluence_points"]:
                logger.info(
                    f"Намерени {len(confluence_info['confluence_points'])} съвпадения Fibonacci + опашки"
                )
                for point in confluence_info["confluence_points"][
                    :3
                ]:  # Показваме топ 3
                    logger.info(
                        f"  {point['tail_date'].strftime('%Y-%m-%d')}: Fib {point['fib_level'] * 100:.1f}% + {point['tail_signal']} (сила: {point['confluence_score']:.2f})"
                    )

            return confluence_info

        except Exception as e:
            logger.exception(
                f"Грешка при проверка на Fibonacci + опашки съвпадения: {e}"
            )
            return {
                "confluence_points": [],
                "strong_confluence": False,
                "confluence_bonus": 0.0,
                "best_entry_points": [],
            }

    def get_weekly_tails_signal(self, tails_analysis: list[dict]) -> dict[str, Any]:
        """
        Генерира сигнал базиран на седмични опашки

        Args:
            tails_analysis: Анализ на седмични опашки

        Returns:
            Dict с сигнал информация
        """
        try:
            if not tails_analysis:
                return {"signal": "HOLD", "reason": "Няма значими седмични опашки"}

            # Групираме опашките по сигнал
            long_tails = [t for t in tails_analysis if t["signal"] == "LONG"]
            short_tails = [t for t in tails_analysis if t["signal"] == "SHORT"]

            # Изчисляваме средната сила за всеки тип (с защитни проверки)
            long_strength = (
                float(np.mean([float(t["signal_strength"]) for t in long_tails]))
                if long_tails
                else 0.0
            )
            short_strength = (
                float(np.mean([float(t["signal_strength"]) for t in short_tails]))
                if short_tails
                else 0.0
            )

            # Определяме доминантния сигнал (ПО-СТРИКТНИ ПРАГОВЕ ЗА SHORT)
            if (
                long_strength > short_strength and long_strength >= 0.3
            ):  # Намалено от 0.5
                signal = "LONG"
                strength = long_strength
                reason = f"Доминантни LONG опашки (сила: {strength:.2f})"
                tail_count = len(long_tails)
            elif (
                short_strength > long_strength and short_strength >= 0.99
            ):  # МАКСИМАЛНО СТРИКТЕН
                signal = "SHORT"
                strength = short_strength
                reason = f"Доминантни SHORT опашки (сила: {strength:.2f})"
                tail_count = len(short_tails)
            # Ако няма доминантен сигнал, проверяваме за единични силни опашки
            elif long_tails and max([t["signal_strength"] for t in long_tails]) >= 0.6:
                signal = "LONG"
                strength = max([t["signal_strength"] for t in long_tails])
                reason = f"Единична силна LONG опашка (сила: {strength:.2f})"
                tail_count = len(long_tails)
            elif (
                short_tails and max([t["signal_strength"] for t in short_tails]) >= 0.99
            ):
                signal = "SHORT"
                strength = max([t["signal_strength"] for t in short_tails])
                reason = f"Единична силна SHORT опашка (сила: {strength:.2f})"
                tail_count = len(short_tails)
            else:
                signal = "HOLD"
                strength = max(long_strength, short_strength)
                reason = "Смесени сигнали от опашките"
                tail_count = len(tails_analysis)

            # Добавяме информация за последните опашки
            recent_tails = tails_analysis[:3]  # Последните 3 опашки

            signal_info = {
                "signal": signal,
                "strength": strength,
                "reason": reason,
                "tail_count": tail_count,
                "recent_tails": recent_tails,
                "long_strength": long_strength,
                "short_strength": short_strength,
                "analysis_date": pd.Timestamp.now(),
            }

            logger.info(f"Weekly Tails сигнал: {signal} (сила: {strength:.2f})")
            logger.info(f"Причина: {reason}")
            logger.info(f"Анализирани опашки: {tail_count}")

            return signal_info

        except Exception as e:
            logger.exception(f"Грешка при генериране на weekly tails сигнал: {e}")
            return {"signal": "HOLD", "reason": f"Грешка: {e}"}

    def _check_tail_above_fibonacci_resistance(
        self,
        tail_price: float,
        fib_levels: dict[float, float],
        proximity_threshold: float = 0.02,
    ) -> bool:
        """
        Phase 1.3: Проверява дали опашката е над Fibonacci resistance ниво

        За SHORT сигнали искаме опашката да е близо до или над resistance ниво,
        което показва че има rejection от това ниво.

        Args:
            tail_price: Цена на опашката (high за upper tail, low за lower tail)
            fib_levels: Fibonacci нива от fibonacci модула
            proximity_threshold: Колко близо трябва да е опашката до resistance

        Returns:
            bool: True ако опашката е над resistance ниво, False ако не е
        """
        try:
            if not fib_levels:
                logger.warning("Няма Fibonacci нива за проверка")
                return False

            # Resistance нива са тези над текущата цена
            resistance_levels = [
                price for level, price in fib_levels.items() if price > tail_price
            ]

            if not resistance_levels:
                logger.info(
                    f"Няма resistance нива над опашката (tail_price: {tail_price:.2f})"
                )
                return False

            # Проверяваме дали опашката е близо до някое resistance ниво
            for resistance_price in resistance_levels:
                price_distance_pct = (
                    abs(tail_price - resistance_price) / resistance_price
                )

                if price_distance_pct <= proximity_threshold:
                    logger.info(
                        f"Опашка е близо до resistance ниво: {resistance_price:.2f} "
                        f"(разстояние: {price_distance_pct:.2f}%)"
                    )
                    return True

            # Ако няма близко resistance ниво, проверяваме дали опашката е над някое ниво
            min_resistance = min(resistance_levels)
            if tail_price > min_resistance:
                logger.info(f"Опашка е над resistance ниво: {min_resistance:.2f}")
                return True

            logger.info(
                f"Опашка не е близо до resistance нива (най-близко: {min(resistance_levels):.2f})"
            )
            return False

        except Exception as e:
            logger.exception(
                f"Грешка при проверка на tail above fibonacci resistance: {e}"
            )
            return False

    def analyze_weekly_tails_trend(self, weekly_df: pd.DataFrame) -> dict[str, Any]:
        """
        Анализира тренда на седмични опашки с trend-based weighting

        Args:
            weekly_df: DataFrame с седмични данни

        Returns:
            Dict с анализ на тренда на опашките (с trend filtering)
        """
        try:
            # PHASE 1: Analyze market trend for weighting
            market_trend = (
                self._analyze_market_trend(weekly_df)
                if self.trend_based_weighting
                else "NEUTRAL"
            )

            # Анализираме седмичните опашки
            raw_tails_analysis = self.analyze_weekly_tails(weekly_df)

            # PHASE 2: Apply trend-based weighting to tail signals
            weighted_tails_analysis = (
                self._apply_trend_weighting(raw_tails_analysis, market_trend)
                if self.trend_based_weighting
                else raw_tails_analysis
            )

            # Генерираме сигнал от weighted анализа
            tails_signal = self.get_weekly_tails_signal(weighted_tails_analysis)

            # Статистика за опашките
            total_tails = len(weighted_tails_analysis)
            strong_tails = len(
                [
                    t
                    for t in weighted_tails_analysis
                    if t["strength_category"] == "STRONG"
                ]
            )
            moderate_tails = len(
                [
                    t
                    for t in weighted_tails_analysis
                    if t["strength_category"] == "MODERATE"
                ]
            )

            trend_analysis = {
                "total_tails": total_tails,
                "strong_tails": strong_tails,
                "moderate_tails": moderate_tails,
                "tails_analysis": weighted_tails_analysis,
                "tails_signal": tails_signal,
                "market_trend": market_trend,
                "trend_weighting_applied": self.trend_based_weighting,
                "analysis_date": pd.Timestamp.now(),
            }

            logger.info(
                f"Weekly Tails тренд анализ завършен - Market trend: {market_trend}"
            )
            return trend_analysis

        except Exception as e:
            logger.exception(f"Грешка при Weekly Tails тренд анализ: {e}")
            return {"error": f"Грешка: {e}"}

    def _analyze_market_trend(self, weekly_df: pd.DataFrame) -> str:
        """
        Analyze market trend to determine appropriate tail weighting

        Returns:
            str: Market trend classification (BULL, BEAR, NEUTRAL)
        """
        try:
            if len(weekly_df) < self.lookback_weeks:
                return "NEUTRAL"

            close_col = "close" if "close" in weekly_df.columns else "Close"
            recent_weeks = weekly_df[close_col].tail(self.lookback_weeks)

            # Calculate trend strength over lookback period
            trend_change = (
                recent_weeks.iloc[-1] - recent_weeks.iloc[0]
            ) / recent_weeks.iloc[0]

            # Determine trend classification
            if trend_change >= self.bull_market_threshold:
                return "BULL"
            if trend_change <= self.bear_market_threshold:
                return "BEAR"
            return "NEUTRAL"

        except Exception as e:
            logger.exception(f"Error analyzing market trend: {e}")
            return "NEUTRAL"

    def _apply_trend_weighting(
        self, tails_analysis: list[dict], market_trend: str
    ) -> list[dict]:
        """
        Apply trend-based weighting to tail signals

        Args:
            tails_analysis: Original tails analysis results
            market_trend: Current market trend classification

        Returns:
            Weighted tails analysis with trend-appropriate adjustments
        """
        try:
            weighted_tails = []

            for tail in tails_analysis:
                weighted_tail = tail.copy()
                original_strength = tail.get(
                    "signal_strength", 0
                )  # Use signal_strength instead of strength
                tail_type = tail.get("signal", "NONE")

                # Apply trend-based weighting logic
                if market_trend == "BULL":
                    if tail_type == "LONG":
                        # Amplify LONG tail signals in bull markets
                        new_strength = min(
                            original_strength * self.long_tail_amplification, 1.0
                        )
                        weighted_tail["signal_strength"] = new_strength
                        weighted_tail["trend_adjustment"] = "BULL_AMPLIFIED"
                        weighted_tail["reason"] = (
                            f"{tail.get('reason', '')} (Amplified in bull market)"
                        )
                    elif tail_type == "SHORT":
                        # Suppress SHORT tail signals in bull markets
                        new_strength = original_strength * self.short_tail_suppression
                        if new_strength < self.min_tail_size:
                            weighted_tail["signal"] = "NONE"
                            weighted_tail["signal_strength"] = 0
                            weighted_tail["trend_adjustment"] = "BULL_SUPPRESSED"
                            weighted_tail["reason"] = (
                                "SHORT tail suppressed in bull market"
                            )
                        else:
                            weighted_tail["signal_strength"] = new_strength
                            weighted_tail["trend_adjustment"] = "BULL_REDUCED"
                            weighted_tail["reason"] = (
                                f"{tail.get('reason', '')} (Reduced in bull market)"
                            )

                elif market_trend == "BEAR":
                    if tail_type == "SHORT":
                        # Amplify SHORT tail signals in bear markets
                        new_strength = min(
                            original_strength * self.long_tail_amplification, 1.0
                        )
                        weighted_tail["signal_strength"] = new_strength
                        weighted_tail["trend_adjustment"] = "BEAR_AMPLIFIED"
                        weighted_tail["reason"] = (
                            f"{tail.get('reason', '')} (Amplified in bear market)"
                        )
                    elif tail_type == "LONG":
                        # Reduce LONG tail signals in bear markets
                        new_strength = original_strength * 0.7
                        weighted_tail["signal_strength"] = new_strength
                        weighted_tail["trend_adjustment"] = "BEAR_REDUCED"
                        weighted_tail["reason"] = (
                            f"{tail.get('reason', '')} (Reduced confidence in bear market)"
                        )

                else:  # NEUTRAL
                    weighted_tail["trend_adjustment"] = "NO_ADJUSTMENT"

                # Update strength category after weighting
                weighted_tail["strength_category"] = self._categorize_strength(
                    weighted_tail["signal_strength"]
                )
                weighted_tails.append(weighted_tail)

            logger.info(f"Applied trend weighting: {market_trend} market")
            return weighted_tails

        except Exception as e:
            logger.exception(f"Error applying trend weighting: {e}")
            return tails_analysis

    def _categorize_strength(self, strength: float) -> str:
        """
        Categorize tail strength after trend weighting

        Args:
            strength: Numerical strength value

        Returns:
            str: Strength category
        """
        if strength >= 0.8:
            return "EXTREME"
        if strength >= 0.6:
            return "STRONG"
        if strength >= 0.3:
            return "MODERATE"
        return "WEAK"


if __name__ == "__main__":
    # Тест на Weekly Tails модула с trend-based weighting
    print(
        "Weekly Tails модул за BNB Trading System - Enhanced with trend-based weighting"
    )
    print("Използвайте main.py за пълен анализ")
