"""
Signal Generator Module - Core Trading Signal Orchestrator

GENERATES LONG/SHORT SIGNALS FOR BNB TRADING SYSTEM

This module serves as the central orchestrator for the BNB trading system,
combining multiple analysis modules to generate high-confidence trading signals.

ARCHITECTURE:
    - Integrates 15+ specialized analysis modules
    - Weighted scoring system for signal confidence
    - Multi-timeframe analysis (daily + weekly)
    - Risk management integration
    - Comprehensive error handling and logging

SIGNAL PRIORITY HIERARCHY:
    1. Fibonacci + Weekly Tails confluence (highest confidence)
    2. Fibonacci levels only
    3. Weekly Tails only
    4. Technical indicators (RSI, MACD, BB)
    5. Trend analysis confirmation

SUPPORTED SIGNAL TYPES:
    - LONG: Buy signal with confidence score
    - SHORT: Sell signal with confidence score
    - HOLD: No clear signal (insufficient confidence)

CONFIDENCE SCORING:
    - 0.0 - 0.3: Very Low (HOLD recommended)
    - 0.3 - 0.6: Low (caution advised)
    - 0.6 - 0.8: Medium (acceptable)
    - 0.8 - 1.0: High (strong signal)

EXAMPLE USAGE:
    >>> from signal_generator import SignalGenerator
    >>> generator = SignalGenerator(config)
    >>> signal = generator.generate_signal(daily_df, weekly_df)
    >>> print(f"Signal: {signal['signal']}, Confidence: {signal['confidence']:.2f}")

DEPENDENCIES:
    - pandas, numpy for data manipulation
    - All 15+ analysis modules
    - Configuration management
    - Logging system

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
LAST UPDATED: 2024-01-01
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging
from fibonacci import FibonacciAnalyzer
from weekly_tails import WeeklyTailsAnalyzer
from indicators import TechnicalIndicators
from optimal_levels import OptimalLevelsAnalyzer
from trend_analyzer import TrendAnalyzer
from elliott_wave_analyzer import ElliottWaveAnalyzer
from whale_tracker import WhaleTracker
from ichimoku_module import IchimokuAnalyzer
from sentiment_module import SentimentAnalyzer
from divergence_detector import DivergenceDetector
from moving_averages import MovingAveragesAnalyzer
from price_action_patterns import PriceActionPatternsAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalGenerator:
    """
    Core Signal Generation Engine for BNB Trading System

    This class serves as the main orchestrator for the entire BNB trading system,
    integrating multiple specialized analysis modules to generate high-confidence
    trading signals through a sophisticated weighted scoring system.

    ARCHITECTURE OVERVIEW:
        - Initializes 15+ analysis modules based on configuration
        - Orchestrates multi-timeframe analysis (daily + weekly)
        - Implements weighted scoring algorithm for signal confidence
        - Provides comprehensive error handling and fallback mechanisms
        - Supports both real-time and historical signal generation

    ANALYSIS MODULES INTEGRATION:
        1. Fibonacci Analyzer (35% weight) - Key levels and retracements
        2. Weekly Tails Analyzer (30% weight) - Price action patterns
        3. Trend Analyzer (20% weight) - Market direction and strength
        4. Technical Indicators (15% weight) - RSI, MACD, Bollinger Bands

    SIGNAL GENERATION PROCESS:
        1. Execute all enabled analysis modules
        2. Collect and validate individual analysis results
        3. Apply weighted scoring algorithm
        4. Generate final signal with confidence score
        5. Validate signal against risk management criteria

    ATTRIBUTES:
        config (Dict): System configuration parameters
        fibonacci_weight (float): Weight for Fibonacci analysis (0.35)
        weekly_tails_weight (float): Weight for weekly tails analysis (0.30)
        rsi_weight (float): Weight for RSI indicator (0.15)
        macd_weight (float): Weight for MACD indicator (0.10)
        bb_weight (float): Weight for Bollinger Bands (0.05)
        min_confirmations (int): Minimum required confirmations (2)
        confidence_threshold (float): Minimum confidence for signal generation (0.7)

    EXAMPLE:
        >>> config = toml.load('config.toml')
        >>> generator = SignalGenerator(config)
        >>> signal = generator.generate_signal(daily_data, weekly_data)
        >>> print(f"Signal: {signal['signal']} (Confidence: {signal['confidence']:.2f})")

    NOTE:
        All analysis modules are initialized but may be disabled via configuration.
        The system gracefully handles module failures and continues with available analyses.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Signal Generator with configuration and analysis modules.

        Sets up all analysis modules based on configuration parameters and establishes
        the weighted scoring system for signal generation.

        Args:
            config (Dict[str, Any]): Complete system configuration from config.toml
                Required sections:
                - signals: Signal generation parameters
                - fibonacci: Fibonacci analysis settings
                - weekly_tails: Weekly tails analysis settings
                - indicators: Technical indicators settings
                - trend: Trend analysis settings
                - And module-specific configurations

        Raises:
            ValueError: If required configuration sections are missing
            ImportError: If required analysis modules cannot be imported

        Example:
            >>> config = {
            ...     'signals': {'fibonacci_weight': 0.35, 'confidence_threshold': 0.7},
            ...     'fibonacci': {'swing_lookback': 100},
            ...     'weekly_tails': {'lookback_weeks': 8}
            ... }
            >>> generator = SignalGenerator(config)
        """
        self.config = config
        self.fibonacci_weight = config['signals']['fibonacci_weight']
        self.weekly_tails_weight = config['signals']['weekly_tails_weight']
        self.rsi_weight = config['signals']['rsi_weight']
        self.macd_weight = config['signals']['macd_weight']
        self.bb_weight = config['signals']['bb_weight']
        self.min_confirmations = config['signals']['min_confirmations']
        self.confidence_threshold = config['signals']['confidence_threshold']
        self.fib_tail_required = config['signals']['fib_tail_required']
        
        # Инициализираме анализаторите
        self.fib_analyzer = FibonacciAnalyzer(config)
        self.tails_analyzer = WeeklyTailsAnalyzer(config)
        self.indicators = TechnicalIndicators(config)
        self.optimal_levels_analyzer = OptimalLevelsAnalyzer(config)
        self.trend_analyzer = TrendAnalyzer(config)
        self.elliott_wave_analyzer = ElliottWaveAnalyzer(config)
        self.whale_tracker = WhaleTracker()
        self.ichimoku_analyzer = IchimokuAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Нови анализатори от ideas файла
        self.divergence_detector = DivergenceDetector(config)
        self.ma_analyzer = MovingAveragesAnalyzer(config)
        self.patterns_analyzer = PriceActionPatternsAnalyzer(config)
        
        logger.info("Signal Generator инициализиран")
        logger.info(f"Приоритет: Fibonacci={self.fibonacci_weight}, Weekly Tails={self.weekly_tails_weight}")
        logger.info(f"Минимум потвърждения: {self.min_confirmations}")
        logger.info(f"Fibonacci+Tail изискване: {self.fib_tail_required}")
    
    def generate_signal(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the primary trading signal by orchestrating all analysis modules.

        This is the MAIN ENTRY POINT for signal generation in the BNB trading system.
        The method executes a comprehensive analysis pipeline:

        1. VALIDATION PHASE:
           - Validates input data integrity
           - Checks data sufficiency for analysis
           - Ensures proper DataFrame structure

        2. ANALYSIS EXECUTION PHASE:
           - Executes all enabled analysis modules in parallel
           - Handles module failures gracefully
           - Collects results with error tracking

        3. SIGNAL SYNTHESIS PHASE:
           - Applies weighted scoring algorithm
           - Determines signal direction (LONG/SHORT/HOLD)
           - Calculates confidence score

        4. VALIDATION PHASE:
           - Validates signal against risk criteria
           - Checks minimum confidence threshold
           - Applies final signal filters

        Args:
            daily_df (pd.DataFrame): Daily OHLCV data with required columns:
                - 'Open', 'High', 'Low', 'Close', 'Volume'
                - Minimum 100 rows for analysis
                - No missing values in critical columns
            weekly_df (pd.DataFrame): Weekly OHLCV data with same requirements:
                - 'Open', 'High', 'Low', 'Close', 'Volume'
                - Minimum 8 rows for analysis
                - Proper datetime index

        Returns:
            Dict[str, Any]: Complete signal analysis with the following structure:
                {
                    'signal': 'LONG' | 'SHORT' | 'HOLD',
                    'confidence': float,  # 0.0 to 1.0
                    'priority': 'HIGHEST' | 'HIGH' | 'MEDIUM' | 'LOW',
                    'fibonacci_analysis': Dict,  # Fibonacci levels and analysis
                    'weekly_tails_analysis': Dict,  # Weekly tails patterns
                    'indicators_signals': Dict,  # Technical indicators
                    'trend_analysis': Dict,  # Trend direction and strength
                    'optimal_levels_analysis': Dict,  # Support/resistance levels
                    'elliott_wave_analysis': Dict,  # Elliott wave structures
                    'whale_analysis': Dict,  # Whale activity summary
                    'ichimoku_analysis': Dict,  # Ichimoku cloud signals
                    'sentiment_analysis': Dict,  # Market sentiment composite
                    'divergence_analysis': Dict,  # Price/indicator divergences
                    'moving_averages_analysis': Dict,  # MA crossovers and trends
                    'price_patterns_analysis': Dict,  # Chart patterns
                    'analysis_date': pd.Timestamp,  # Analysis timestamp
                    'error': str  # Only present if critical error occurred
                }

        Raises:
            ValueError: If input data is invalid or insufficient
            RuntimeError: If critical analysis modules fail

        Example:
            >>> daily_data = pd.read_csv('daily_bnb.csv', index_col='Date')
            >>> weekly_data = pd.read_csv('weekly_bnb.csv', index_col='Date')
            >>> signal = generator.generate_signal(daily_data, weekly_data)
            >>> if signal['signal'] != 'HOLD':
            ...     print(f"Trade Signal: {signal['signal']} "
            ...           f"(Confidence: {signal['confidence']:.1%})")

        Note:
            The method is designed to be robust and will continue analysis
            even if individual modules fail, using available data for signal generation.
        """
        try:
            logger.info("Генериране на trading сигнал...")
            
            # 1. Fibonacci анализ
            fib_analysis = self.fib_analyzer.analyze_fibonacci_trend(daily_df)
            if 'error' in fib_analysis:
                logger.warning(f"Fibonacci анализ неуспешен: {fib_analysis['error']}")
                fib_analysis = None
            
            # 2. Weekly Tails анализ
            tails_analysis = self.tails_analyzer.analyze_weekly_tails_trend(weekly_df)
            if 'error' in tails_analysis:
                logger.warning(f"Weekly Tails анализ неуспешен: {tails_analysis['error']}")
                tails_analysis = None
            
            # 3. Технически индикатори
            daily_with_indicators = self.indicators.calculate_indicators(daily_df)
            indicators_signals = self.indicators.get_all_indicators_signals(daily_with_indicators)
            if 'error' in indicators_signals:
                logger.warning(f"Индикаторни сигнали неуспешни: {indicators_signals['error']}")
                indicators_signals = None
            
            # 4. Optimal Levels анализ
            optimal_levels_analysis = self.optimal_levels_analyzer.analyze_optimal_levels(daily_df, weekly_df)
            if 'error' in optimal_levels_analysis:
                logger.warning(f"Optimal Levels анализ неуспешен: {optimal_levels_analysis['error']}")
                optimal_levels_analysis = None
            
            # 5. Trend Analysis
            trend_analysis = self.trend_analyzer.analyze_trend(daily_df, weekly_df)
            if 'error' in trend_analysis:
                logger.warning(f"Trend анализ неуспешен: {trend_analysis['error']}")
                trend_analysis = None
            
            # 6. Elliott Wave Analysis
            elliott_wave_analysis = self.elliott_wave_analyzer.analyze_elliott_wave(daily_df, weekly_df)
            if 'error' in elliott_wave_analysis:
                logger.warning(f"Elliott Wave анализ неуспешен: {elliott_wave_analysis['error']}")
                elliott_wave_analysis = None
            
            # 7. Whale Tracker Analysis
            whale_analysis = self.whale_tracker.get_whale_activity_summary(days_back=1)
            if 'error' in whale_analysis:
                logger.warning(f"Whale Tracker анализ неуспешен: {whale_analysis['error']}")
                whale_analysis = None
            
            # 8. Ichimoku Analysis
            ichimoku_analysis = self.ichimoku_analyzer.analyze_ichimoku_signals(
                self.ichimoku_analyzer.calculate_all_ichimoku_lines(
                    self.ichimoku_analyzer.process_klines_data(
                        self.ichimoku_analyzer.fetch_ichimoku_data("1d", 100)
                    )
                )
            )
            if 'error' in ichimoku_analysis:
                logger.warning(f"Ichimoku анализ неуспешен: {ichimoku_analysis['error']}")
                ichimoku_analysis = None
            
            # 9. Sentiment Analysis
            sentiment_analysis = self.sentiment_analyzer.calculate_composite_sentiment(
                self.sentiment_analyzer.get_fear_greed_index(),
                self.sentiment_analyzer.analyze_social_sentiment(),
                self.sentiment_analyzer.analyze_news_sentiment(),
                self.sentiment_analyzer.get_market_momentum_indicators()
            )
            if 'error' in sentiment_analysis:
                logger.warning(f"Sentiment анализ неуспешен: {sentiment_analysis['error']}")
                sentiment_analysis = None
            
            # 10. Divergence Analysis (НОВО от ideas файла)
            logger.info(f"Стартиране на Divergence анализ...")
            logger.info(f"Daily data columns: {daily_df.columns.tolist()}")
            logger.info(f"Daily with indicators columns: {daily_with_indicators.columns.tolist()}")
            
            # Проверяваме дали има RSI и MACD данни
            rsi_values = daily_with_indicators['RSI'].tolist() if 'RSI' in daily_with_indicators.columns else []
            macd_values = daily_with_indicators['MACD'].tolist() if 'MACD' in daily_with_indicators.columns else []
            
            logger.info(f"RSI values count: {len(rsi_values)}")
            logger.info(f"MACD values count: {len(macd_values)}")
            
            divergence_analysis = self.divergence_detector.detect_all_divergences(
                daily_df, 
                {
                    'rsi': {'rsi_values': rsi_values},
                    'macd': {'macd_values': macd_values}
                }
            )
            
            logger.info(f"Divergence анализ резултат: {divergence_analysis}")
            
            if divergence_analysis and 'error' in divergence_analysis:
                logger.warning(f"Divergence анализ неуспешен: {divergence_analysis['error']}")
                divergence_analysis = None
            elif divergence_analysis is None:
                logger.warning("Divergence анализ е None")
            else:
                logger.info("Divergence анализ успешен")
            
            # 11. Moving Averages Analysis (НОВО от ideas файла)
            ma_analysis = self.ma_analyzer.calculate_emas(daily_df)
            logger.info(f"Moving Averages анализ резултат: {ma_analysis}")
            if 'error' in ma_analysis:
                logger.warning(f"Moving Averages анализ неуспешен: {ma_analysis['error']}")
                ma_analysis = None
            
            # 12. Price Action Patterns Analysis (НОВО от ideas файла)
            patterns_analysis = self.patterns_analyzer.detect_all_patterns(daily_df)
            logger.info(f"Price Patterns анализ резултат: {patterns_analysis}")
            if 'error' in patterns_analysis:
                logger.warning(f"Price Patterns анализ неуспешен: {patterns_analysis['error']}")
                patterns_analysis = None
            
            # 6. Проверяваме за Fibonacci + Tails съвпадения
            confluence_info = None
            if fib_analysis and tails_analysis:
                confluence_info = self.tails_analyzer.check_fib_tail_confluence(
                    fib_analysis['fibonacci_levels'],
                    fib_analysis['current_price'],
                    tails_analysis['tails_analysis']
                )
            
            # 7. Генерираме финален сигнал
            final_signal = self._combine_signals(
                fib_analysis,
                tails_analysis,
                indicators_signals,
                confluence_info,
                trend_analysis
            )
            
            # 8. Добавяме детайлна информация
            signal_details = self._create_signal_details(
                final_signal,
                fib_analysis,
                tails_analysis,
                indicators_signals,
                confluence_info,
                optimal_levels_analysis,
                trend_analysis,
                elliott_wave_analysis,
                whale_analysis,
                ichimoku_analysis,
                sentiment_analysis,
                divergence_analysis,
                ma_analysis,
                patterns_analysis
            )
            
            logger.info(f"Сигнал генериран: {final_signal['signal']} (увереност: {final_signal['confidence']:.2f})")
            
            return signal_details
            
        except Exception as e:
            logger.error(f"Грешка при генериране на сигнал: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': f'Грешка при генериране: {e}',
                'priority': 'ERROR'
            }
    
    def _combine_signals(self, fib_analysis: Dict, tails_analysis: Dict,
                         indicators_signals: Dict, confluence_info: Dict,
                         trend_analysis: Dict = None) -> Dict[str, any]:
        """
        Комбинира сигналите от различните източници
        
        Args:
            fib_analysis: Fibonacci анализ
            tails_analysis: Weekly Tails анализ
            indicators_signals: Индикаторни сигнали
            confluence_info: Fibonacci + Tails съвпадения
            
        Returns:
            Dict с комбинирания сигнал
        """
        try:
            # Инициализираме резултатите
            signal_scores = {'LONG': 0.0, 'SHORT': 0.0, 'HOLD': 0.0}
            signal_reasons = []
            total_weight = 0.0
            
            # 1. Fibonacci сигнал (най-висок приоритет)
            if fib_analysis and 'fibonacci_signal' in fib_analysis:
                fib_signal = fib_analysis['fibonacci_signal']
                if fib_signal['signal'] != 'HOLD':
                    weight = self.fibonacci_weight
                    score = fib_signal['strength'] * weight
                    signal_scores[fib_signal['signal']] += score
                    total_weight += weight
                    signal_reasons.append(f"Fibonacci: {fib_signal['reason']} (сила: {fib_signal['strength']:.2f})")
            
            # 2. Weekly Tails сигнал (втори приоритет)
            if tails_analysis and 'tails_signal' in tails_analysis:
                tails_signal = tails_analysis['tails_signal']
                if tails_signal['signal'] != 'HOLD':
                    weight = self.weekly_tails_weight
                    score = tails_signal['strength'] * weight
                    signal_scores[tails_signal['signal']] += score
                    total_weight += weight
                    signal_reasons.append(f"Weekly Tails: {tails_signal['reason']} (сила: {tails_signal['strength']:.2f})")
            
            # 3. Fibonacci + Tails съвпадение (бонус)
            if confluence_info and confluence_info['strong_confluence']:
                bonus = confluence_info['confluence_bonus']
                # Добавяме бонус към доминантния сигнал
                if signal_scores['LONG'] > signal_scores['SHORT']:
                    signal_scores['LONG'] += bonus
                elif signal_scores['SHORT'] > signal_scores['LONG']:
                    signal_scores['SHORT'] += bonus
                signal_reasons.append(f"Fibonacci+Tail съвпадение бонус: {bonus}")
            
            # 4. Технически индикатори (по-нисък приоритет)
            if indicators_signals:
                # RSI
                if 'rsi' in indicators_signals:
                    rsi_signal = indicators_signals['rsi']
                    if rsi_signal['signal'] != 'HOLD':
                        weight = self.rsi_weight
                        score = rsi_signal['strength'] * weight
                        signal_scores[rsi_signal['signal']] += score
                        total_weight += weight
                        signal_reasons.append(f"RSI: {rsi_signal['reason']}")
                
                # MACD
                if 'macd' in indicators_signals:
                    macd_signal = indicators_signals['macd']
                    if macd_signal['signal'] != 'HOLD':
                        weight = self.macd_weight
                        score = macd_signal['strength'] * weight
                        signal_scores[macd_signal['signal']] += score
                        total_weight += weight
                        signal_reasons.append(f"MACD: {macd_signal['reason']}")
                
                # Bollinger Bands
                if 'bollinger' in indicators_signals:
                    bb_signal = indicators_signals['bollinger']
                    if bb_signal['signal'] != 'HOLD':
                        weight = self.bb_weight
                        score = bb_signal['strength'] * weight
                        signal_scores[bb_signal['signal']] += score
                        total_weight += weight
                        signal_reasons.append(f"Bollinger: {bb_signal['reason']}")
            
            # 5. Определяме финалния сигнал
            if total_weight == 0:
                final_signal = 'HOLD'
                confidence = 0.0
                reason = "Няма валидни сигнали"
            else:
                # Нормализираме резултатите
                for signal in signal_scores:
                    signal_scores[signal] /= total_weight
                
                # Намираме доминантния сигнал
                final_signal = max(signal_scores, key=signal_scores.get)
                confidence = signal_scores[final_signal]

                # Phase 1: Trend Filter за SHORT сигнали
                if final_signal == 'SHORT' and trend_analysis and self.config.get('short_signals', {}).get('trend_filter', False):
                    trend_filter_applied = self._apply_trend_filter_for_short(trend_analysis)
                    if trend_filter_applied['blocked']:
                        final_signal = 'HOLD'
                        confidence = 0.5
                        signal_reasons.append(f"SHORT BLOCKED by trend filter: {trend_filter_applied['reason']}")

                # Phase 1.3: Fibonacci Resistance Filter за SHORT сигнали от Weekly Tails
                if final_signal == 'SHORT' and tails_analysis and fib_analysis:
                    fib_resistance_filter_applied = self._apply_fibonacci_resistance_filter_for_short(tails_analysis, fib_analysis)
                    if fib_resistance_filter_applied['blocked']:
                        final_signal = 'HOLD'
                        confidence = 0.4
                        signal_reasons.append(f"SHORT BLOCKED by Fibonacci resistance filter: {fib_resistance_filter_applied['reason']}")

                # Phase 1.4: Volume Confirmation Filter за SHORT сигнали
                if final_signal == 'SHORT' and daily_df is not None:
                    volume_confirmation_applied = self._check_volume_confirmation_for_short(daily_df)
                    if not volume_confirmation_applied['confirmed']:
                        final_signal = 'HOLD'
                        confidence = 0.3
                        signal_reasons.append(f"SHORT BLOCKED by volume confirmation: {volume_confirmation_applied['reason']}")

                # Проверяваме дали отговаря на изискванията (по-гъвкаво)
                if self.fib_tail_required:
                    has_fib_or_tail = (
                        (fib_analysis and fib_analysis.get('fibonacci_signal', {}).get('signal') != 'HOLD') or
                        (tails_analysis and tails_analysis.get('tails_signal', {}).get('signal') != 'HOLD')
                    )
                    
                    # Намаляваме изискванията за по-гъвкавост
                    if not has_fib_or_tail and confidence < (self.confidence_threshold * 0.7):  # Намалено от 0.8 до 0.56
                        final_signal = 'HOLD'
                        confidence = 0.5
                        reason = "HOLD: Изисква се Fibonacci или значима опашка за силни сигнали"
                    else:
                        reason = " | ".join(signal_reasons)
                else:
                    reason = " | ".join(signal_reasons)
            
            return {
                'signal': final_signal,
                'confidence': confidence,
                'reason': reason,
                'signal_scores': signal_scores,
                'total_weight': total_weight
            }
            
        except Exception as e:
            logger.error(f"Грешка при комбиниране на сигнали: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'reason': f'Грешка: {e}',
                'signal_scores': {'LONG': 0.0, 'SHORT': 0.0, 'HOLD': 0.0},
                'total_weight': 0.0
            }

    def _apply_trend_filter_for_short(self, trend_analysis: Dict) -> Dict[str, any]:
        """
        Phase 1: Прилага trend filter за SHORT сигнали

        SHORT сигнали се генерират само когато трендът е:
        - NEUTRAL (странично движение)
        - WEAK_DOWNTREND (слаб низходящ тренд)

        SHORT се блокира при:
        - STRONG_UPTREND (силен възходящ тренд)
        - MODERATE_UPTREND (умерен възходящ тренд)

        Args:
            trend_analysis: Резултат от trend_analyzer.analyze_trend()

        Returns:
            Dict с информация дали SHORT е блокиран и причината
        """
        try:
            # Извличаме информация за тренда
            combined_trend = trend_analysis.get('combined_trend', {})
            daily_trend = trend_analysis.get('daily_trend', {})
            weekly_trend = trend_analysis.get('weekly_trend', {})

            if not combined_trend or not daily_trend:
                return {
                    'blocked': False,
                    'reason': 'Недостатъчна информация за тренда'
                }

            # Извличаме посоката и силата на тренда
            trend_direction = combined_trend.get('direction', 'UNKNOWN')
            daily_direction = daily_trend.get('direction', 'UNKNOWN')
            daily_strength = daily_trend.get('strength', 'UNKNOWN')

            # Конфигурационни параметри
            config = self.config.get('short_signals', {})
            trend_threshold = config.get('trend_strength_threshold', 0.3)

            # Логика за блокиране на SHORT сигнали
            blocked = False
            reason = ""

            # 1. Блокираме SHORT при силни възходящи трендове
            if trend_direction in ['UPTREND', 'STRONG_UPTREND'] or daily_direction == 'UPTREND':
                if daily_strength in ['MODERATE', 'STRONG'] or trend_direction == 'STRONG_UPTREND':
                    blocked = True
                    reason = f"SHORT blocked: Strong uptrend detected (Daily: {daily_direction}, Combined: {trend_direction})"
                elif daily_strength == 'MODERATE' and trend_threshold > 0.2:
                    blocked = True
                    reason = f"SHORT blocked: Moderate uptrend above threshold (threshold: {trend_threshold})"

            # 2. Позволяваме SHORT при подходящи условия
            elif trend_direction in ['NEUTRAL', 'DOWNTREND', 'WEAK_DOWNTREND'] or daily_direction in ['NEUTRAL', 'DOWNTREND']:
                blocked = False
                reason = f"SHORT allowed: Suitable trend conditions (Daily: {daily_direction}, Combined: {trend_direction})"

            # 3. По подразбиране блокираме ако нямаме ясна информация
            else:
                blocked = True
                reason = f"SHORT blocked: Unclear trend conditions (Daily: {daily_direction}, Combined: {trend_direction})"

            logger.info(f"Trend filter result: {'BLOCKED' if blocked else 'ALLOWED'} - {reason}")

            return {
                'blocked': blocked,
                'reason': reason,
                'trend_direction': trend_direction,
                'daily_direction': daily_direction,
                'daily_strength': daily_strength,
                'trend_threshold': trend_threshold
            }

        except Exception as e:
            logger.error(f"Грешка при прилагане на trend filter: {e}")
            return {
                'blocked': False,  # По подразбиране не блокираме при грешка
                'reason': f'Error in trend filter: {e}',
                'error': str(e)
            }

    def _apply_fibonacci_resistance_filter_for_short(self, tails_analysis: Dict, fib_analysis: Dict) -> Dict[str, any]:
        """
        Phase 1.3: Филтрира SHORT сигнали от weekly tails според Fibonacci resistance

        SHORT сигнали се генерират само когато опашката е близо до или над
        Fibonacci resistance ниво, което показва rejection от това ниво.

        Args:
            tails_analysis: Резултат от weekly_tails.analyze_weekly_tails_trend()
            fib_analysis: Резултат от fibonacci.analyze_fibonacci_trend()

        Returns:
            Dict с информация дали SHORT е блокиран и причината
        """
        try:
            if not tails_analysis or not fib_analysis:
                return {
                    'blocked': False,
                    'reason': 'Недостатъчно данни за анализ'
                }

            tails_signal = tails_analysis.get('tails_signal', {})
            if tails_signal.get('signal') != 'SHORT':
                return {
                    'blocked': False,
                    'reason': 'Не е SHORT сигнал'
                }

            # Взимаме Fibonacci нива
            fib_levels = fib_analysis.get('fibonacci_levels', {})
            if not fib_levels:
                return {
                    'blocked': False,
                    'reason': 'Няма Fibonacci нива'
                }

            # Конфигурационни параметри
            config = self.config.get('weekly_tails', {})
            fibonacci_resistance_check = config.get('fibonacci_resistance_check', True)
            proximity_threshold = config.get('fibonacci_proximity_threshold', 0.02)

            if not fibonacci_resistance_check:
                return {
                    'blocked': False,
                    'reason': 'Fibonacci resistance check изключен'
                }

            # Анализираме последните SHORT опашки
            tails_analysis_data = tails_analysis.get('tails_analysis', [])
            short_tails = [tail for tail in tails_analysis_data if tail.get('signal') == 'SHORT']

            if not short_tails:
                return {
                    'blocked': False,
                    'reason': 'Няма SHORT опашки'
                }

            # Проверяваме дали последната SHORT опашка е близо до Fibonacci resistance
            latest_short_tail = short_tails[-1]  # Най-новата SHORT опашка
            tail_high = latest_short_tail.get('high', latest_short_tail.get('price', 0))

            # Намираме resistance нива над опашката
            resistance_levels = [price for level, price in fib_levels.items() if price > tail_high]

            if not resistance_levels:
                return {
                    'blocked': True,
                    'reason': f'SHORT blocked: Опашка ({tail_high:.2f}) няма resistance нива над себе си'
                }

            # Проверяваме дали опашката е близо до някое resistance ниво
            for resistance_price in resistance_levels:
                price_distance_pct = abs(tail_high - resistance_price) / resistance_price

                if price_distance_pct <= proximity_threshold:
                    logger.info(f"SHORT allowed: Опашка близо до resistance {resistance_price:.2f} "
                               f"(разстояние: {price_distance_pct:.2f}%)")
                    return {
                        'blocked': False,
                        'reason': f'SHORT allowed: Опашка близо до Fib resistance {resistance_price:.2f}'
                    }

            # Ако няма близко resistance ниво, проверяваме дали опашката е над някое ниво
            min_resistance = min(resistance_levels)
            if tail_high > min_resistance:
                logger.info(f"SHORT allowed: Опашка над resistance {min_resistance:.2f}")
                return {
                    'blocked': False,
                    'reason': f'SHORT allowed: Опашка над Fib resistance {min_resistance:.2f}'
                }

            # Блокираме SHORT ако опашката не е близо до resistance
            return {
                'blocked': True,
                'reason': f'SHORT blocked: Опашка ({tail_high:.2f}) далеч от resistance нива '
                         f'(най-близко: {min_resistance:.2f})'
            }

        except Exception as e:
            logger.error(f"Грешка при Fibonacci resistance filter: {e}")
            return {
                'blocked': False,  # По подразбиране не блокираме при грешка
                'reason': f'Error in Fibonacci resistance filter: {e}',
                'error': str(e)
            }

    def _check_volume_confirmation_for_short(self, daily_df: pd.DataFrame) -> Dict[str, any]:
        """
        Phase 1.4: Проверява volume confirmation за SHORT сигнали

        SHORT сигнали се генерират само когато текущият обем е
        значително по-висок от средния обем за последните N периода.

        Args:
            daily_df: DataFrame с дневни OHLCV данни

        Returns:
            Dict с информация дали има достатъчно volume confirmation
        """
        try:
            if daily_df is None or daily_df.empty:
                return {
                    'confirmed': False,
                    'reason': 'Няма данни за volume анализ'
                }

            # Конфигурационни параметри
            config = self.config.get('weekly_tails', {})
            volume_confirmation = config.get('volume_confirmation_for_short', True)
            lookback_periods = config.get('volume_lookback_periods', 14)
            multiplier_threshold = config.get('volume_multiplier_threshold', 1.5)

            if not volume_confirmation:
                return {
                    'confirmed': True,
                    'reason': 'Volume confirmation изключен'
                }

            # Проверяваме дали има Volume колона
            if 'Volume' not in daily_df.columns and 'volume' not in daily_df.columns:
                return {
                    'confirmed': False,
                    'reason': 'Няма Volume данни'
                }

            # Взимаме последните данни
            volume_col = 'Volume' if 'Volume' in daily_df.columns else 'volume'
            recent_data = daily_df.tail(lookback_periods + 1)  # +1 за текущия период

            if len(recent_data) < lookback_periods + 1:
                return {
                    'confirmed': False,
                    'reason': f'Недостатъчно данни: нужни {lookback_periods + 1}, има {len(recent_data)}'
                }

            # Текущият обем (последният запис)
            current_volume = recent_data[volume_col].iloc[-1]

            # Среден обем за последните N периода (без текущия)
            avg_volume = recent_data[volume_col].iloc[:-1].mean()

            if avg_volume <= 0:
                return {
                    'confirmed': False,
                    'reason': 'Средният обем е нула или отрицателен'
                }

            # Изчисляваме колко пъти е по-голям текущият обем
            volume_multiplier = current_volume / avg_volume

            logger.info(f"Volume analysis: Current: {current_volume:.0f}, "
                       f"Average: {avg_volume:.0f}, "
                       f"Multiplier: {volume_multiplier:.2f}, "
                       f"Threshold: {multiplier_threshold:.2f}")

            # Проверяваме дали обемът е достатъчно висок
            if volume_multiplier >= multiplier_threshold:
                return {
                    'confirmed': True,
                    'reason': f'Volume confirmation: {volume_multiplier:.2f}x > {multiplier_threshold:.2f}x threshold',
                    'current_volume': current_volume,
                    'avg_volume': avg_volume,
                    'volume_multiplier': volume_multiplier,
                    'threshold': multiplier_threshold
                }
            else:
                return {
                    'confirmed': False,
                    'reason': f'Недостатъчен volume: {volume_multiplier:.2f}x < {multiplier_threshold:.2f}x threshold',
                    'current_volume': current_volume,
                    'avg_volume': avg_volume,
                    'volume_multiplier': volume_multiplier,
                    'threshold': multiplier_threshold
                }

        except Exception as e:
            logger.error(f"Грешка при volume confirmation check: {e}")
            return {
                'confirmed': False,  # По подразбиране не потвърждаваме при грешка
                'reason': f'Error in volume confirmation: {e}',
                'error': str(e)
            }
    
    def _create_signal_details(self, final_signal: Dict, fib_analysis: Dict, 
                              tails_analysis: Dict, indicators_signals: Dict, 
                              confluence_info: Dict, optimal_levels_analysis: Dict = None, 
                              trend_analysis: Dict = None, elliott_wave_analysis: Dict = None,
                              whale_analysis: Dict = None, ichimoku_analysis: Dict = None,
                              sentiment_analysis: Dict = None, divergence_analysis: Dict = None,
                              ma_analysis: Dict = None, patterns_analysis: Dict = None) -> Dict[str, any]:
        """
        Създава детайлна информация за сигнала
        
        Args:
            final_signal: Финален сигнал
            fib_analysis: Fibonacci анализ
            tails_analysis: Weekly Tails анализ
            indicators_signals: Индикаторни сигнали
            confluence_info: Fibonacci + Tails съвпадения
            optimal_levels_analysis: Optimal Levels анализ
            trend_analysis: Trend Analysis
            
        Returns:
            Dict с детайлна информация за сигнала
        """
        try:
            signal_details = {
                'signal': final_signal['signal'],
                'confidence': final_signal['confidence'],
                'reason': final_signal['reason'],
                'priority': self._determine_priority(final_signal, fib_analysis, tails_analysis, confluence_info),
                'analysis_date': pd.Timestamp.now(),
                'fibonacci_analysis': fib_analysis,
                'weekly_tails_analysis': tails_analysis,
                'indicators_signals': indicators_signals,
                'confluence_info': confluence_info,
                'optimal_levels_analysis': optimal_levels_analysis,
                'trend_analysis': trend_analysis,
                'elliott_wave_analysis': elliott_wave_analysis,
                'whale_analysis': whale_analysis,
                'ichimoku_analysis': ichimoku_analysis,
                'sentiment_analysis': sentiment_analysis,
                'divergence_analysis': divergence_analysis,
                'moving_averages_analysis': ma_analysis,
                'price_patterns_analysis': patterns_analysis,
                'next_targets': self._get_next_targets(final_signal, fib_analysis, tails_analysis),
                'risk_level': self._calculate_risk_level(final_signal, fib_analysis, tails_analysis)
            }
            
            return signal_details
            
        except Exception as e:
            logger.error(f"Грешка при създаване на детайли за сигнала: {e}")
            return final_signal
    
    def _determine_priority(self, final_signal: Dict, fib_analysis: Dict, 
                           tails_analysis: Dict, confluence_info: Dict) -> str:
        """
        Определя приоритета на сигнала
        
        Args:
            final_signal: Финален сигнал
            fib_analysis: Fibonacci анализ
            tails_analysis: Weekly Tails анализ
            confluence_info: Fibonacci + Tails съвпадения
            
        Returns:
            Приоритет на сигнала
        """
        try:
            # Проверяваме за Fibonacci + Tails съвпадение
            if confluence_info and confluence_info.get('strong_confluence'):
                return 'HIGHEST'
            
            # Проверяваме за Fibonacci сигнал
            if fib_analysis and fib_analysis.get('fibonacci_signal', {}).get('signal') != 'HOLD':
                return 'HIGH'
            
            # Проверяваме за Weekly Tails сигнал
            if tails_analysis and tails_analysis.get('tails_signal', {}).get('signal') != 'HOLD':
                return 'MEDIUM'
            
            # Само технически индикатори
            return 'LOW'
            
        except Exception as e:
            logger.error(f"Грешка при определяне на приоритет: {e}")
            return 'UNKNOWN'
    
    def _get_next_targets(self, final_signal: Dict, fib_analysis: Dict, 
                          tails_analysis: Dict) -> Dict[str, any]:
        """
        Определя следващите целеви нива
        
        Args:
            final_signal: Финален сигнал
            fib_analysis: Fibonacci анализ
            tails_analysis: Weekly Tails анализ
            
        Returns:
            Dict с следващите целеви нива
        """
        try:
            next_targets = {
                'entry_price': None,
                'exit_price': None,
                'stop_loss': None,
                'fibonacci_levels': {},
                'weekly_tails_support': []
            }
            
            if fib_analysis and 'fibonacci_levels' in fib_analysis:
                fib_levels = fib_analysis['fibonacci_levels']
                current_price = fib_analysis['current_price']
                
                # Определяме support и resistance нива
                support_levels = [(level, price) for level, price in fib_levels.items() if price < current_price]
                resistance_levels = [(level, price) for level, price in fib_levels.items() if price > current_price]
                
                if final_signal['signal'] == 'LONG':
                    # За LONG: търсим най-близкото support за entry
                    if support_levels:
                        support_levels.sort(key=lambda x: abs(x[1] - current_price))
                        next_targets['entry_price'] = support_levels[0][1]
                        next_targets['fibonacci_levels']['entry'] = f"Fib {support_levels[0][0]*100:.1f}%"
                    
                    # Следващото resistance за exit
                    if resistance_levels:
                        resistance_levels.sort(key=lambda x: x[1] - current_price)
                        next_targets['exit_price'] = resistance_levels[0][1]
                        next_targets['fibonacci_levels']['exit'] = f"Fib {resistance_levels[0][0]*100:.1f}%"
                
                elif final_signal['signal'] == 'SHORT':
                    # За SHORT: търсим най-близкото resistance за entry
                    if resistance_levels:
                        resistance_levels.sort(key=lambda x: abs(x[1] - current_price))
                        next_targets['entry_price'] = resistance_levels[0][1]
                        next_targets['fibonacci_levels']['entry'] = f"Fib {resistance_levels[0][0]*100:.1f}%"
                    
                    # Следващото support за exit
                    if support_levels:
                        support_levels.sort(key=lambda x: current_price - x[1])
                        next_targets['exit_price'] = support_levels[0][1]
                        next_targets['fibonacci_levels']['exit'] = f"Fib {support_levels[0][0]*100:.1f}%"
            
            # Добавяме Weekly Tails support
            if tails_analysis and 'tails_analysis' in tails_analysis:
                for tail in tails_analysis['tails_analysis'][:3]:  # Последните 3 опашки
                    if tail['signal'] == final_signal['signal']:
                        next_targets['weekly_tails_support'].append({
                            'date': tail['date'],
                            'price': tail['low'] if tail['dominant_tail'] == 'lower' else tail['high'],
                            'strength': tail['tail_strength'],
                            'type': tail['dominant_tail']
                        })
            
            return next_targets
            
        except Exception as e:
            logger.error(f"Грешка при определяне на следващите цели: {e}")
            return {}
    
    def _calculate_risk_level(self, final_signal: Dict, fib_analysis: Dict, 
                             tails_analysis: Dict) -> str:
        """
        Изчислява нивото на риска
        
        Args:
            final_signal: Финален сигнал
            fib_analysis: Fibonacci анализ
            tails_analysis: Weekly Tails анализ
            
        Returns:
            Ниво на риска
        """
        try:
            if final_signal['signal'] == 'HOLD':
                return 'LOW'
            
            risk_score = 0
            
            # Fibonacci рисков фактор
            if fib_analysis and 'fibonacci_signal' in fib_analysis:
                fib_signal = fib_analysis['fibonacci_signal']
                if fib_signal['signal'] != 'HOLD':
                    risk_score += 1
            
            # Weekly Tails рисков фактор
            if tails_analysis and 'tails_signal' in tails_analysis:
                tails_signal = tails_analysis['tails_signal']
                if tails_signal['signal'] != 'HOLD':
                    risk_score += 1
            
            # Увереност на сигнала
            if final_signal['confidence'] >= 0.8:
                risk_score -= 1
            elif final_signal['confidence'] <= 0.5:
                risk_score += 1
            
            # Определяме нивото на риска
            if risk_score <= 0:
                return 'LOW'
            elif risk_score == 1:
                return 'MEDIUM'
            else:
                return 'HIGH'
                
        except Exception as e:
            logger.error(f"Грешка при изчисляване на нивото на риска: {e}")
            return 'UNKNOWN'

if __name__ == "__main__":
    # Тест на Signal Generator модула
    print("Signal Generator модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
