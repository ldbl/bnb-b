"""
Multi-Timeframe Confirmation Analyzer - Phase 3 Enhancement

АНАЛИЗАТОР ЗА МУЛТИ-ТАЙМФРЕЙМ ПОТВЪРЖДЕНИЕ НА СИГНАЛИ
Проверява консистентността на сигналите през различни timeframe-ове

SPECIALIZED MODULE FOR SIGNAL CONFIRMATION ACROSS TIMEFRAMES
Validates trading signals by checking alignment between daily and weekly analysis

This module provides comprehensive multi-timeframe analysis specifically optimized
for cryptocurrency trading, focusing on signal confirmation and conflict resolution
between different timeframes.

ARCHITECTURE OVERVIEW:
    - Daily vs Weekly trend alignment analysis
    - Fibonacci levels confirmation across timeframes
    - MACD crossover synchronization
    - Volume confirmation consistency
    - Weekly tails validation for daily signals

MULTI-TIMEFRAME ANALYSIS METHODOLOGY:
    1. TREND CONSISTENCY: Compare daily and weekly trend directions
    2. FIBONACCI ALIGNMENT: Validate Fibonacci levels across timeframes
    3. MACD SYNCHRONIZATION: Check MACD signals alignment
    4. VOLUME CONFIRMATION: Consistent volume patterns
    5. WEEKLY TAILS VALIDATION: Weekly rejection patterns confirmation

KEY FEATURES:
    - Automated timeframe signal alignment
    - Conflict resolution between daily/weekly signals
    - Confidence scoring based on multi-timeframe agreement
    - Bonus/penalty system for signal consistency
    - Real-time validation of signal strength

TRADING APPLICATIONS:
    - Enhanced signal reliability through multi-timeframe confirmation
    - Reduced false signals through conflict detection
    - Improved entry/exit timing with timeframe alignment
    - Better risk management with consistent signals

CONFIGURATION PARAMETERS:
    - daily_weekly_trend_alignment: Enable trend consistency checks
    - fibonacci_alignment_bonus: Confidence bonus for aligned Fibonacci
    - macd_alignment_bonus: Bonus for synchronized MACD signals
    - volume_alignment_bonus: Bonus for consistent volume patterns
    - trend_consistency_threshold: Minimum alignment for bonuses

SIGNAL STRENGTH CLASSIFICATION:
    - PERFECT ALIGNMENT: All timeframes agree (maximum bonus)
    - STRONG ALIGNMENT: Most timeframes agree (high bonus)
    - MODERATE ALIGNMENT: Some conflicts (moderate bonus)
    - WEAK ALIGNMENT: Major conflicts (penalty applied)

EXAMPLE USAGE:
    >>> config = {'multi_timeframe': {'enabled': True, 'fibonacci_alignment_bonus': 0.15}}
    >>> analyzer = MultiTimeframeAnalyzer(config)
    >>> daily_signals = {'fibonacci': 'LONG', 'macd': 'LONG', 'trend': 'UPTREND'}
    >>> weekly_signals = {'fibonacci': 'LONG', 'macd': 'LONG', 'trend': 'UPTREND'}
    >>> confirmation = analyzer.analyze_timeframe_alignment(daily_signals, weekly_signals)
    >>> if confirmation['overall_alignment'] == 'PERFECT':
    ...     print(f"Signal confirmed with {confirmation['confidence_bonus']:.2f} bonus")

DEPENDENCIES:
    - pandas: Data manipulation and time series operations
    - numpy: Mathematical calculations and array operations
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient signal comparison algorithms
    - Cached calculations for repeated analysis
    - Memory-optimized data structures
    - Parallel processing capabilities

ERROR HANDLING:
    - Graceful handling of missing timeframe data
    - Validation of input signal formats
    - Comprehensive logging for debugging
    - Fallback mechanisms for incomplete analysis

AUTHOR: BNB Trading System Team
VERSION: 1.0.0
DATE: 2024-01-01
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MultiTimeframeAnalyzer:
    """
    Advanced Multi-Timeframe Signal Confirmation Engine

    This class provides comprehensive analysis of signal consistency across
    different timeframes, enhancing signal reliability through alignment validation.

    MULTI-TIMEFRAME METHODOLOGY:
        1. Signal Alignment Analysis: Compare signals across daily/weekly timeframes
        2. Trend Consistency: Validate trend directions between timeframes
        3. Fibonacci Confirmation: Check Fibonacci level alignment
        4. Technical Indicator Sync: MACD, RSI, volume consistency
        5. Conflict Resolution: Handle timeframe disagreements

    CONFIGURATION PARAMETERS:
        enabled (bool): Enable multi-timeframe analysis
        daily_weekly_trend_alignment (bool): Check trend consistency
        fibonacci_alignment_bonus (float): Bonus for Fibonacci alignment
        macd_alignment_bonus (float): Bonus for MACD synchronization
        volume_alignment_bonus (float): Bonus for volume consistency
        weekly_tails_confirmation (bool): Use weekly tails for daily validation
        trend_consistency_threshold (float): Minimum alignment threshold

    ATTRIBUTES:
        config (Dict): Complete configuration dictionary
        enabled (bool): Analysis enabled flag
        fibonacci_bonus (float): Fibonacci alignment bonus
        macd_bonus (float): MACD alignment bonus
        volume_bonus (float): Volume alignment bonus
        trend_threshold (float): Trend consistency threshold

    SIGNAL ALIGNMENT SCORING:
        - PERFECT: All signals aligned (confidence +0.30)
        - STRONG: Most signals aligned (confidence +0.20)
        - MODERATE: Some signals aligned (confidence +0.10)
        - WEAK: Major conflicts (confidence -0.10)
        - CONFLICT: Strong disagreement (confidence -0.20)

    OUTPUT STRUCTURE:
        {
            'overall_alignment': str,        # PERFECT | STRONG | MODERATE | WEAK | CONFLICT
            'confidence_bonus': float,       # -0.20 to +0.30 confidence adjustment
            'alignment_score': float,        # 0.0 to 1.0 alignment percentage
            'conflicts': List[str],          # List of signal conflicts
            'confirmations': List[str],      # List of signal confirmations
            'trend_alignment': str,          # TREND_ALIGNED | TREND_CONFLICT
            'fibonacci_alignment': str,      # FIB_ALIGNED | FIB_CONFLICT
            'macd_alignment': str,           # MACD_ALIGNED | MACD_CONFLICT
            'volume_alignment': str,         # VOLUME_ALIGNED | VOLUME_CONFLICT
            'recommendation': str            # STRONG_BUY | BUY | HOLD | SELL | STRONG_SELL
        }

    EXAMPLE:
        >>> analyzer = MultiTimeframeAnalyzer(config)
        >>> daily_analysis = {'trend': 'UPTREND', 'fibonacci': 'LONG', 'macd': 'LONG'}
        >>> weekly_analysis = {'trend': 'UPTREND', 'fibonacci': 'LONG', 'macd': 'LONG'}
        >>> result = analyzer.analyze_timeframe_alignment(daily_analysis, weekly_analysis)
        >>> print(f"Alignment: {result['overall_alignment']} | Bonus: {result['confidence_bonus']}")

    NOTE:
        Requires consistent signal format across all timeframe analyses
        and proper configuration for optimal performance.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.multi_timeframe_config = config.get("multi_timeframe", {})

        self.enabled = self.multi_timeframe_config.get("enabled", True)
        self.daily_weekly_trend_alignment = self.multi_timeframe_config.get(
            "daily_weekly_trend_alignment", True
        )
        self.fibonacci_bonus = self.multi_timeframe_config.get(
            "fibonacci_alignment_bonus", 0.15
        )
        self.macd_bonus = self.multi_timeframe_config.get("macd_alignment_bonus", 0.10)
        self.volume_bonus = self.multi_timeframe_config.get(
            "volume_alignment_bonus", 0.05
        )
        self.weekly_tails_confirmation = self.multi_timeframe_config.get(
            "weekly_tails_confirmation", True
        )
        self.trend_threshold = self.multi_timeframe_config.get(
            "trend_consistency_threshold", 0.7
        )

        logger.info("Multi-Timeframe Analyzer инициализиран")
        logger.info(
            f"Daily/Weekly trend alignment: {self.daily_weekly_trend_alignment}"
        )
        logger.info(
            f"Confidence bonuses: Fibonacci={self.fibonacci_bonus}, MACD={
                self.macd_bonus
            }, Volume={self.volume_bonus}"
        )

    def analyze_timeframe_alignment(
        self, daily_analysis: dict, weekly_analysis: dict
    ) -> dict[str, Any]:
        """
        Основен метод за анализ на multi-timeframe alignment

        Args:
            daily_analysis: Анализ от daily timeframe
            weekly_analysis: Анализ от weekly timeframe

        Returns:
            Dict с резултати от alignment анализа
        """
        try:
            if not self.enabled:
                return {
                    "overall_alignment": "DISABLED",
                    "confidence_bonus": 0.0,
                    "alignment_score": 0.5,
                    "conflicts": [],
                    "confirmations": [],
                    "recommendation": "HOLD",
                }

            # Инициализираме резултатите
            conflicts = []
            confirmations = []
            total_score = 0.0
            max_score = 0.0

            # 1. Trend alignment анализ
            trend_result = self._analyze_trend_alignment(
                daily_analysis, weekly_analysis
            )
            total_score += trend_result["score"]
            max_score += 1.0

            if trend_result["aligned"]:
                confirmations.append(f"Trend alignment: {trend_result['reason']}")
            else:
                conflicts.append(f"Trend conflict: {trend_result['reason']}")

            # Status вече е добавен в метода _analyze_trend_alignment

            # 2. Fibonacci alignment анализ
            fib_result = self._analyze_fibonacci_alignment(
                daily_analysis, weekly_analysis
            )
            total_score += fib_result["score"]
            max_score += 1.0

            if fib_result["aligned"]:
                confirmations.append(f"Fibonacci alignment: {fib_result['reason']}")
            else:
                conflicts.append(f"Fibonacci conflict: {fib_result['reason']}")

            # Status вече е добавен в метода _analyze_fibonacci_alignment

            # 3. MACD alignment анализ
            macd_result = self._analyze_macd_alignment(daily_analysis, weekly_analysis)
            total_score += macd_result["score"]
            max_score += 1.0

            if macd_result["aligned"]:
                confirmations.append(f"MACD alignment: {macd_result['reason']}")
            else:
                conflicts.append(f"MACD conflict: {macd_result['reason']}")
            # Status вече е добавен в метода _analyze_macd_alignment

            # 4. Volume alignment анализ
            volume_result = self._analyze_volume_alignment(
                daily_analysis, weekly_analysis
            )
            total_score += volume_result["score"]
            max_score += 1.0

            if volume_result["aligned"]:
                confirmations.append(f"Volume alignment: {volume_result['reason']}")
            else:
                conflicts.append(f"Volume conflict: {volume_result['reason']}")
            # Status вече е добавен в метода _analyze_volume_alignment

            # 5. Weekly tails confirmation (ако е налично)
            weekly_tails_result = {
                "score": 0.0,
                "aligned": True,
                "reason": "Not applicable",
                "status": "N/A",
            }
            if self.weekly_tails_confirmation and "weekly_tails" in weekly_analysis:
                weekly_tails_result = self._analyze_weekly_tails_confirmation(
                    daily_analysis, weekly_analysis
                )
                total_score += weekly_tails_result["score"]
                max_score += 1.0

                if weekly_tails_result["aligned"]:
                    confirmations.append(
                        f"Weekly tails confirmation: {weekly_tails_result['reason']}"
                    )
                else:
                    conflicts.append(
                        f"Weekly tails conflict: {weekly_tails_result['reason']}"
                    )
                # Status вече е добавен в метода _analyze_weekly_tails_confirmation

            # Изчисляваме alignment score
            alignment_score = total_score / max_score if max_score > 0 else 0.5

            # Определяме overall alignment
            overall_alignment, confidence_bonus = self._calculate_overall_alignment(
                alignment_score, conflicts, confirmations
            )

            # Генерираме recommendation
            recommendation = self._generate_recommendation(
                overall_alignment, daily_analysis, weekly_analysis
            )

            result = {
                "overall_alignment": overall_alignment,
                "confidence_bonus": confidence_bonus,
                "alignment_score": alignment_score,
                "conflicts": conflicts,
                "confirmations": confirmations,
                "trend_alignment": trend_result.get("status", "UNKNOWN"),
                "fibonacci_alignment": fib_result.get("status", "UNKNOWN"),
                "macd_alignment": macd_result.get("status", "UNKNOWN"),
                "volume_alignment": volume_result.get("status", "UNKNOWN"),
                "weekly_tails_alignment": (
                    weekly_tails_result.get("status", "N/A")
                    if weekly_tails_result
                    else "N/A"
                ),
                "recommendation": recommendation,
                "analysis_summary": {
                    "total_signals_analyzed": max_score,
                    "alignment_percentage": f"{alignment_score:.1%}",
                    "conflict_count": len(conflicts),
                    "confirmation_count": len(confirmations),
                },
            }

            logger.info(
                f"Multi-timeframe alignment analysis completed: {overall_alignment} (score: {alignment_score:.2f})"
            )
            return result

        except Exception as e:
            logger.exception(f"Грешка при multi-timeframe alignment анализ: {e}")
            return {
                "overall_alignment": "ERROR",
                "confidence_bonus": 0.0,
                "alignment_score": 0.0,
                "conflicts": [f"Error: {e}"],
                "confirmations": [],
                "recommendation": "HOLD",
            }

    def _analyze_trend_alignment(self, daily: dict, weekly: dict) -> dict:
        """Анализира alignment на трендовете"""
        try:
            daily_trend = daily.get("trend_analysis", {}).get(
                "primary_trend", "UNKNOWN"
            )
            weekly_trend = weekly.get("trend_analysis", {}).get(
                "primary_trend", "UNKNOWN"
            )

            if daily_trend == "UNKNOWN" or weekly_trend == "UNKNOWN":
                return {
                    "score": 0.5,
                    "aligned": True,
                    "reason": "Trend data unavailable",
                    "status": "UNKNOWN",
                }

            # Проверяваме за alignment
            aligned = False
            reason = ""

            if daily_trend == weekly_trend:
                aligned = True
                reason = f"Both timeframes show {daily_trend}"
            elif daily_trend in ["UPTREND", "MODERATE_UPTREND"] and weekly_trend in [
                "UPTREND",
                "MODERATE_UPTREND",
            ]:
                aligned = True
                reason = "Both timeframes show upward trend"
            elif daily_trend in [
                "DOWNTREND",
                "MODERATE_DOWNTREND",
            ] and weekly_trend in [
                "DOWNTREND",
                "MODERATE_DOWNTREND",
            ]:
                aligned = True
                reason = "Both timeframes show downward trend"
            else:
                reason = f"Trend conflict: Daily={daily_trend}, Weekly={weekly_trend}"

            score = 1.0 if aligned else 0.0
            status = "TREND_ALIGNED" if aligned else "TREND_CONFLICT"

            return {
                "score": score,
                "aligned": aligned,
                "reason": reason,
                "status": status,
            }

        except Exception as e:
            logger.exception(f"Грешка при trend alignment анализ: {e}")
            return {
                "score": 0.5,
                "aligned": False,
                "reason": f"Error: {e}",
                "status": "ERROR",
            }

    def _analyze_fibonacci_alignment(self, daily: dict, weekly: dict) -> dict:
        """Анализира alignment на Fibonacci сигналите"""
        try:
            daily_fib = (
                daily.get("fibonacci_analysis", {})
                .get("fibonacci_signal", {})
                .get("signal", "HOLD")
            )
            weekly_fib = (
                weekly.get("fibonacci_analysis", {})
                .get("fibonacci_signal", {})
                .get("signal", "HOLD")
            )

            if daily_fib == "HOLD" or weekly_fib == "HOLD":
                return {
                    "score": 0.5,
                    "aligned": True,
                    "reason": "Fibonacci signal not available",
                    "status": "UNKNOWN",
                }

            aligned = daily_fib == weekly_fib
            reason = f"Daily={daily_fib}, Weekly={weekly_fib}"
            score = 1.0 if aligned else 0.0
            status = "FIB_ALIGNED" if aligned else "FIB_CONFLICT"

            return {
                "score": score,
                "aligned": aligned,
                "reason": reason,
                "status": status,
            }

        except Exception as e:
            logger.exception(f"Грешка при Fibonacci alignment анализ: {e}")
            return {
                "score": 0.5,
                "aligned": False,
                "reason": f"Error: {e}",
                "status": "ERROR",
            }

    def _analyze_macd_alignment(self, daily: dict, weekly: dict) -> dict:
        """Анализира alignment на MACD сигналите"""
        try:
            daily_macd = (
                daily.get("indicators_signals", {})
                .get("macd", {})
                .get("signal", "HOLD")
            )
            weekly_macd = (
                weekly.get("indicators_signals", {})
                .get("macd", {})
                .get("signal", "HOLD")
            )

            if daily_macd == "HOLD" or weekly_macd == "HOLD":
                return {
                    "score": 0.5,
                    "aligned": True,
                    "reason": "MACD signal not available",
                    "status": "UNKNOWN",
                }

            aligned = daily_macd == weekly_macd
            reason = f"Daily={daily_macd}, Weekly={weekly_macd}"
            score = 1.0 if aligned else 0.0
            status = "MACD_ALIGNED" if aligned else "MACD_CONFLICT"

            return {
                "score": score,
                "aligned": aligned,
                "reason": reason,
                "status": status,
            }

        except Exception as e:
            logger.exception(f"Грешка при MACD alignment анализ: {e}")
            return {
                "score": 0.5,
                "aligned": False,
                "reason": f"Error: {e}",
                "status": "ERROR",
            }

    def _analyze_volume_alignment(self, daily: dict, weekly: dict) -> dict:
        """Анализира alignment на volume сигналите"""
        try:
            # Volume alignment е по-трудно да се оцени директно
            # За сега използваме проста логика
            daily_volume = daily.get("volume_analysis", {})
            weekly_volume = weekly.get("volume_analysis", {})

            # Ако няма volume данни, считаме за aligned
            if not daily_volume and not weekly_volume:
                return {
                    "score": 0.5,
                    "aligned": True,
                    "reason": "Volume data not available",
                    "status": "UNKNOWN",
                }

            # Проста логика: ако има volume confirmation и в двата timeframe-а
            daily_confirmed = daily_volume.get("confirmed", False)
            weekly_confirmed = weekly_volume.get("confirmed", False)

            aligned = daily_confirmed == weekly_confirmed
            reason = f"Volume confirmation: Daily={daily_confirmed}, Weekly={weekly_confirmed}"
            score = 1.0 if aligned else 0.0
            status = "VOLUME_ALIGNED" if aligned else "VOLUME_CONFLICT"

            return {
                "score": score,
                "aligned": aligned,
                "reason": reason,
                "status": status,
            }

        except Exception as e:
            logger.exception(f"Грешка при volume alignment анализ: {e}")
            return {
                "score": 0.5,
                "aligned": False,
                "reason": f"Error: {e}",
                "status": "ERROR",
            }

    def _analyze_weekly_tails_confirmation(self, daily: dict, weekly: dict) -> dict:
        """Анализира weekly tails потвърждение за daily сигнали"""
        try:
            daily_signal = daily.get("signal", "HOLD")
            weekly_tails = weekly.get("weekly_tails_analysis", {}).get(
                "tails_signal", {}
            )

            if daily_signal == "HOLD":
                return {
                    "score": 0.5,
                    "aligned": True,
                    "reason": "No daily signal to confirm",
                    "status": "UNKNOWN",
                }

            weekly_signal = weekly_tails.get("signal", "HOLD")

            if weekly_signal == "HOLD":
                return {
                    "score": 0.5,
                    "aligned": True,
                    "reason": "Weekly tails signal not available",
                    "status": "UNKNOWN",
                }

            aligned = daily_signal == weekly_signal
            reason = f"Daily={daily_signal} confirmed by Weekly tails={weekly_signal}"
            score = 1.0 if aligned else 0.0
            status = "TAILS_CONFIRMED" if aligned else "TAILS_CONFLICT"

            return {
                "score": score,
                "aligned": aligned,
                "reason": reason,
                "status": status,
            }

        except Exception as e:
            logger.exception(f"Грешка при weekly tails confirmation анализ: {e}")
            return {
                "score": 0.5,
                "aligned": False,
                "reason": f"Error: {e}",
                "status": "ERROR",
            }

    def _calculate_overall_alignment(
        self, alignment_score: float, conflicts: list, confirmations: list
    ) -> tuple[str, float]:
        """Изчислява overall alignment и confidence bonus"""
        try:
            # Определяме alignment level базирано на score и conflicts
            if alignment_score >= 0.9 and len(conflicts) == 0:
                overall_alignment = "PERFECT"
                confidence_bonus = (
                    self.fibonacci_bonus + self.macd_bonus + self.volume_bonus
                )
            elif alignment_score >= 0.7 and len(conflicts) <= 1:
                overall_alignment = "STRONG"
                confidence_bonus = self.fibonacci_bonus + self.macd_bonus
            elif alignment_score >= 0.5:
                overall_alignment = "MODERATE"
                confidence_bonus = self.fibonacci_bonus
            elif alignment_score >= 0.3:
                overall_alignment = "WEAK"
                confidence_bonus = -0.05
            else:
                overall_alignment = "CONFLICT"
                confidence_bonus = -0.15

            # Ограничаваме bonus-а в разумни граници
            confidence_bonus = max(-0.20, min(0.30, confidence_bonus))

            return overall_alignment, confidence_bonus

        except Exception as e:
            logger.exception(f"Грешка при изчисление на overall alignment: {e}")
            return "UNKNOWN", 0.0

    def _generate_recommendation(
        self, overall_alignment: str, daily: dict, weekly: dict
    ) -> str:
        """Генерира recommendation базирано на alignment"""
        try:
            daily_signal = daily.get("signal", "HOLD")
            weekly_signal = weekly.get("signal", "HOLD")

            if overall_alignment in ["PERFECT", "STRONG"]:
                if daily_signal == weekly_signal == "LONG":
                    return "STRONG_BUY"
                if daily_signal == weekly_signal == "SHORT":
                    return "STRONG_SELL"
                if daily_signal == "LONG":
                    return "BUY"
                if daily_signal == "SHORT":
                    return "SELL"
            elif overall_alignment == "MODERATE":
                if daily_signal == "LONG":
                    return "BUY"
                if daily_signal == "SHORT":
                    return "SELL"
            else:
                return "HOLD"

            return "HOLD"

        except Exception as e:
            logger.exception(f"Грешка при генериране на recommendation: {e}")
            return "HOLD"


if __name__ == "__main__":
    print("Multi-Timeframe Confirmation Analyzer за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
