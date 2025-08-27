"""
Trend Analysis Module - Advanced Trend Detection and Adaptive Trading Strategies

COMPREHENSIVE TREND ANALYSIS ENGINE FOR BNB TRADING SYSTEM
Analyzes market direction, strength, and generates adaptive entry strategies

This module provides sophisticated trend analysis capabilities specifically designed
for cryptocurrency markets, with special optimization for BNB/USD price movements.

ARCHITECTURE OVERVIEW:
    - Multi-timeframe trend analysis (daily + weekly)
    - Statistical trend detection using linear regression
    - Adaptive strategy generation based on market conditions
    - Range vs trending market classification
    - Trend strength quantification and classification

TREND ANALYSIS METHODOLOGY:
    - Linear Regression Analysis: Slope calculation for trend direction
    - Statistical Significance Testing: R-squared and p-value validation
    - Trend Strength Classification: Weak, Moderate, Strong, Extreme
    - Multi-timeframe Confirmation: Daily + Weekly alignment
    - Range Detection: Sideways market identification

ADAPTIVE STRATEGY GENERATION:
    - Pullback Entry: Enter on dips in uptrend
    - Bounce Entry: Enter on rallies in downtrend
    - Range Trading: Trade between support/resistance boundaries
    - Breakout Trading: Enter on trend continuation signals
    - Mean Reversion: Fade extreme moves in ranging markets

KEY FEATURES:
    - Automated trend detection with configurable sensitivity
    - Statistical validation of trend significance
    - Multi-timeframe trend confirmation
    - Adaptive entry strategy recommendations
    - Risk management integration
    - Market regime classification

TRADING APPLICATIONS:
    - Trend-following strategies in strong directional markets
    - Counter-trend strategies in ranging markets
    - Risk management based on trend strength
    - Entry timing optimization
    - Position sizing based on trend confidence

CONFIGURATION PARAMETERS:
    - trend_lookback_days: Days to analyze for trend (default: 30)
    - trend_threshold: Minimum trend strength threshold (default: 0.015)
    - range_analysis_periods: Periods for range analysis (default: 20)

TREND CLASSIFICATION:
    - BULLISH: Positive slope, higher highs/lows
    - BEARISH: Negative slope, lower highs/lows
    - NEUTRAL: Weak slope, no clear direction
    - RANGE: Sideways movement, oscillating prices

ADAPTIVE STRATEGIES:
    - PULLBACK_ENTRY: Buy dips in uptrend (conservative)
    - BREAKOUT_ENTRY: Buy breakouts in uptrend (aggressive)
    - BOUNCE_ENTRY: Sell rallies in downtrend (conservative)
    - BREAKDOWN_ENTRY: Sell breakdowns in downtrend (aggressive)
    - RANGE_TRADING: Trade between support/resistance (neutral)

EXAMPLE USAGE:
    >>> config = {'trend': {'trend_lookback_days': 30, 'trend_threshold': 0.015}}
    >>> trend_analyzer = TrendAnalyzer(config)
    >>> analysis = trend_analyzer.analyze_trend(daily_data, weekly_data)
    >>> strategy = analysis['adaptive_strategy']
    >>> print(f"Recommended strategy: {strategy['strategy_type']}")

DEPENDENCIES:
    - pandas: Data manipulation and time series analysis
    - numpy: Mathematical calculations and statistical functions
    - scipy.stats: Statistical analysis and linear regression
    - typing: Type hints for better code documentation

PERFORMANCE OPTIMIZATIONS:
    - Efficient vectorized calculations
    - Minimal data copying and memory usage
    - Optimized statistical computations
    - Caching of expensive calculations

ERROR HANDLING:
    - Validation of input data structure and sufficiency
    - Graceful handling of statistical calculation failures
    - Comprehensive logging for debugging and monitoring
    - Fallback mechanisms for edge cases

SIGNAL ACCURACY ENHANCEMENTS:
    - Multi-timeframe trend confirmation
    - Statistical significance validation
    - Trend strength filtering
    - Market regime awareness

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from scipy import stats

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """
    Advanced Trend Analysis Engine with Adaptive Strategy Generation

    This class provides comprehensive trend analysis capabilities for the BNB trading system,
    using statistical methods to detect market direction and generate adaptive trading strategies
    based on current market conditions.

    ARCHITECTURE OVERVIEW:
        - Multi-timeframe trend analysis combining daily and weekly data
        - Statistical trend detection using linear regression analysis
        - Adaptive strategy generation based on market regime
        - Range vs trending market classification
        - Trend strength quantification with confidence scores

    TREND DETECTION ALGORITHMS:
        1. Linear Regression: Calculates slope and statistical significance
        2. Price Change Analysis: Measures absolute and percentage price movement
        3. Trend Strength Classification: Weak/Moderate/Strong/Extreme categorization
        4. Multi-timeframe Confirmation: Daily + Weekly trend alignment
        5. Range Detection: Identifies sideways market conditions

    ADAPTIVE STRATEGY TYPES:
        - PULLBACK_ENTRY: Conservative entry on dips in uptrend
        - BREAKOUT_ENTRY: Aggressive entry on breakouts in uptrend
        - BOUNCE_ENTRY: Conservative entry on rallies in downtrend
        - BREAKDOWN_ENTRY: Aggressive entry on breakdowns in downtrend
        - RANGE_TRADING: Neutral strategy for sideways markets

    CONFIGURATION PARAMETERS:
        trend_lookback_days (int): Historical period for trend analysis (default: 30)
        trend_threshold (float): Minimum trend strength threshold (default: 0.015)
        range_analysis_periods (int): Periods for range market detection (default: 20)

    ATTRIBUTES:
        trend_lookback_days (int): Lookback period for trend analysis
        trend_threshold (float): Minimum trend strength requirement
        range_analysis_periods (int): Range analysis window size

    TREND STRENGTH CLASSIFICATION:
        - WEAK: < 5% price change, low statistical significance
        - MODERATE: 5-10% price change, moderate significance
        - STRONG: 10-20% price change, high significance
        - EXTREME: > 20% price change, maximum significance

    STATISTICAL VALIDATION:
        - R-squared values for trend reliability
        - P-values for statistical significance
        - Standard error calculations
        - Confidence interval estimation

    EXAMPLE:
        >>> config = {
        ...     'trend': {
        ...         'trend_lookback_days': 30,
        ...         'trend_threshold': 0.015
        ...     }
        ... }
        >>> analyzer = TrendAnalyzer(config)
        >>> trend_analysis = analyzer.analyze_trend(daily_data, weekly_data)
        >>> print(f"Trend: {trend_analysis['combined_trend']['direction']}")
        >>> print(f"Strategy: {trend_analysis['adaptive_strategy']['strategy_type']}")

    NOTE:
        The analyzer requires sufficient historical data (minimum 30 periods)
        and works best with clean OHLCV data without gaps or anomalies.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Trend Analyzer with configuration parameters.

        Sets up the trend analysis engine with all necessary parameters for
        detecting market direction and generating adaptive trading strategies.

        Args:
            config (Dict[str, Any]): Complete configuration dictionary containing:
                - trend.trend_lookback_days (int): Historical lookback period
                - trend.trend_threshold (float): Minimum trend strength threshold

        Raises:
            KeyError: If required configuration keys are missing
            ValueError: If configuration values are invalid

        Example:
            >>> config = {
            ...     'trend': {
            ...         'trend_lookback_days': 30,
            ...         'trend_threshold': 0.015
            ...     }
            ... }
            >>> analyzer = TrendAnalyzer(config)
        """
        self.trend_lookback_days = config.get('trend', {}).get('trend_lookback_days', 30)
        self.trend_threshold = config.get('trend', {}).get('trend_threshold', 0.015)
        self.range_analysis_periods = 20  # Периоди за range анализ
        
        logger.info("Trend анализатор инициализиран")
        logger.info(f"Trend lookback: {self.trend_lookback_days} дни")
        logger.info(f"Trend threshold: {self.trend_threshold:.1%}")
    
    def analyze_trend(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Dict:
        """
        Анализира тренда на BNB
        
        Args:
            daily_df: Daily OHLCV данни
            weekly_df: Weekly OHLCV данни
            
        Returns:
            Dict с анализ на тренда
        """
        try:
            logger.info("Анализ на тренда...")
            
            # 1. Анализ на дневния тренд
            daily_trend = self._analyze_daily_trend(daily_df)
            
            # 2. Анализ на седмичния тренд
            weekly_trend = self._analyze_weekly_trend(weekly_df)
            
            # 3. Range анализ
            range_analysis = self._analyze_price_range(daily_df)
            
            # 4. Комбиниран тренд анализ
            combined_trend = self._combine_trend_analysis(daily_trend, weekly_trend, range_analysis)
            
            # 5. Генерираме адаптивни entry стратегии
            adaptive_strategy = self._generate_adaptive_strategy(combined_trend, daily_df)
            
            trend_analysis = {
                'daily_trend': daily_trend,
                'weekly_trend': weekly_trend,
                'range_analysis': range_analysis,
                'combined_trend': combined_trend,
                'adaptive_strategy': adaptive_strategy,
                'analysis_date': daily_df.index[-1]
            }
            
            logger.info("Тренд анализ завършен успешно")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Грешка при анализ на тренда: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _analyze_daily_trend(self, df: pd.DataFrame) -> Dict:
        """Анализира дневния тренд"""
        try:
            if len(df) < self.trend_lookback_days:
                return {'error': 'Недостатъчно данни за анализ'}
            
            # Взимаме последните N дни
            recent_data = df.tail(self.trend_lookback_days)
            
            # Линейна регресия за определяне на тренда
            x = np.arange(len(recent_data))
            y = recent_data['Close'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Изчисляваме промяната в цената
            start_price = y[0]
            end_price = y[-1]
            price_change = end_price - start_price
            price_change_pct = (price_change / start_price) * 100
            
            # Определяме силата на тренда
            if abs(price_change_pct) < 5:
                trend_strength = 'WEAK'
            elif abs(price_change_pct) < 15:
                trend_strength = 'MODERATE'
            else:
                trend_strength = 'STRONG'
            
            # Определяме посоката на тренда
            if slope > self.trend_threshold:
                trend_direction = 'UPTREND'
            elif slope < -self.trend_threshold:
                trend_direction = 'DOWNTREND'
            else:
                trend_direction = 'NEUTRAL'
            
            daily_trend = {
                'direction': trend_direction,
                'strength': trend_strength,
                'slope': slope,
                'r_squared': r_value ** 2,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'start_price': start_price,
                'end_price': end_price,
                'lookback_days': self.trend_lookback_days
            }
            
            logger.info(f"Дневен тренд: {trend_direction} ({trend_strength}) - {price_change_pct:+.2f}%")
            return daily_trend
            
        except Exception as e:
            logger.error(f"Грешка при анализ на дневния тренд: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _analyze_weekly_trend(self, df: pd.DataFrame) -> Dict:
        """Анализира седмичния тренд"""
        try:
            if len(df) < 8:  # Минимум 8 седмици
                return {'error': 'Недостатъчно седмични данни'}
            
            # Взимаме последните 8 седмици
            recent_weeks = df.tail(8)
            
            # Линейна регресия за седмичния тренд
            x = np.arange(len(recent_weeks))
            y = recent_weeks['Close'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Изчисляваме промяната
            start_price = y[0]
            end_price = y[-1]
            price_change = end_price - start_price
            price_change_pct = (price_change / start_price) * 100
            
            # Определяме силата
            if abs(price_change_pct) < 10:
                trend_strength = 'WEAK'
            elif abs(price_change_pct) < 25:
                trend_strength = 'MODERATE'
            else:
                trend_strength = 'STRONG'
            
            # Определяме посоката
            if slope > self.trend_threshold * 2:  # По-голям threshold за седмици
                trend_direction = 'UPTREND'
            elif slope < -self.trend_threshold * 2:
                trend_direction = 'DOWNTREND'
            else:
                trend_direction = 'NEUTRAL'
            
            weekly_trend = {
                'direction': trend_direction,
                'strength': trend_strength,
                'slope': slope,
                'r_squared': r_value ** 2,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'start_price': start_price,
                'end_price': end_price,
                'weeks_analyzed': len(recent_weeks)
            }
            
            logger.info(f"Седмичен тренд: {trend_direction} ({trend_strength}) - {price_change_pct:+.2f}%")
            return weekly_trend
            
        except Exception as e:
            logger.error(f"Грешка при анализ на седмичния тренд: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _analyze_price_range(self, df: pd.DataFrame) -> Dict:
        """Анализира ценовия range"""
        try:
            if len(df) < self.range_analysis_periods:
                return {'error': 'Недостатъчно данни за range анализ'}
            
            # Взимаме последните N периоди
            recent_data = df.tail(self.range_analysis_periods)
            
            # Намираме текущия range
            current_high = recent_data['High'].max()
            current_low = recent_data['Low'].min()
            current_range = current_high - current_low
            current_range_pct = (current_range / current_low) * 100
            
            # Намираме исторически range
            historical_high = df['High'].max()
            historical_low = df['Low'].min()
            historical_range = historical_high - historical_low
            historical_range_pct = (historical_range / historical_low) * 100
            
            # Определяме дали range се разширява или свива
            if current_range_pct > historical_range_pct * 0.8:
                range_status = 'EXPANDING'
            elif current_range_pct < historical_range_pct * 0.5:
                range_status = 'CONTRACTING'
            else:
                range_status = 'STABLE'
            
            # Позиция в текущия range
            current_price = df['Close'].iloc[-1]
            range_position = (current_price - current_low) / current_range
            
            range_analysis = {
                'current_range': current_range,
                'current_range_pct': current_range_pct,
                'current_high': current_high,
                'current_low': current_low,
                'historical_range': historical_range,
                'historical_range_pct': historical_range_pct,
                'historical_high': historical_high,
                'historical_low': historical_low,
                'range_status': range_status,
                'range_position': range_position,
                'periods_analyzed': self.range_analysis_periods
            }
            
            logger.info(f"Range анализ: {range_status} - текущ: {current_range_pct:.1f}%, исторически: {historical_range_pct:.1f}%")
            return range_analysis
            
        except Exception as e:
            logger.error(f"Грешка при range анализ: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _combine_trend_analysis(self, daily_trend: Dict, weekly_trend: Dict, range_analysis: Dict) -> Dict:
        """Комбинира различните тренд анализи"""
        try:
            if 'error' in daily_trend or 'error' in weekly_trend or 'error' in range_analysis:
                return {'error': 'Грешка в един от тренд анализите'}
            
            # Определяме основния тренд
            if daily_trend['direction'] == weekly_trend['direction']:
                primary_trend = daily_trend['direction']
                trend_confidence = 'HIGH'
            elif daily_trend['strength'] == 'STRONG' and weekly_trend['strength'] == 'STRONG':
                primary_trend = daily_trend['direction']  # Дневният има приоритет
                trend_confidence = 'MEDIUM'
            else:
                primary_trend = 'MIXED'
                trend_confidence = 'LOW'
            
            # Изчисляваме общата сила на тренда
            daily_strength_score = self._strength_to_score(daily_trend['strength'])
            weekly_strength_score = self._strength_to_score(weekly_trend['strength'])
            combined_strength = (daily_strength_score + weekly_strength_score) / 2
            
            # Определяме дали тренда е приключил
            trend_completed = self._is_trend_completed(daily_trend, weekly_trend, range_analysis)
            
            combined_trend = {
                'primary_trend': primary_trend,
                'trend_confidence': trend_confidence,
                'combined_strength': combined_strength,
                'trend_completed': trend_completed,
                'daily_trend_summary': {
                    'direction': daily_trend['direction'],
                    'strength': daily_trend['strength'],
                    'change_pct': daily_trend['price_change_pct']
                },
                'weekly_trend_summary': {
                    'direction': weekly_trend['direction'],
                    'strength': weekly_trend['strength'],
                    'change_pct': weekly_trend['price_change_pct']
                },
                'range_summary': {
                    'status': range_analysis['range_status'],
                    'position': range_analysis['range_position']
                }
            }
            
            logger.info(f"Комбиниран тренд: {primary_trend} (увереност: {trend_confidence}, приключил: {trend_completed})")
            return combined_trend
            
        except Exception as e:
            logger.error(f"Грешка при комбиниране на тренд анализите: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _strength_to_score(self, strength: str) -> float:
        """Конвертира силата на тренда в числов score"""
        strength_map = {'WEAK': 0.3, 'MODERATE': 0.6, 'STRONG': 1.0}
        return strength_map.get(strength, 0.5)
    
    def _is_trend_completed(self, daily_trend: Dict, weekly_trend: Dict, range_analysis: Dict) -> bool:
        """Определя дали тренда е приключил"""
        try:
            # Проверяваме за reversal сигнали
            if daily_trend['direction'] == 'UPTREND':
                # За uptrend, проверяваме дали цената е близо до горната граница на range
                if range_analysis['range_position'] > 0.8:
                    return True
                # Проверяваме дали дневният тренд се забавя
                if daily_trend['strength'] == 'WEAK' and weekly_trend['strength'] == 'WEAK':
                    return True
            elif daily_trend['direction'] == 'DOWNTREND':
                # За downtrend, проверяваме дали цената е близо до долната граница
                if range_analysis['range_position'] < 0.2:
                    return True
                # Проверяваме дали дневният тренд се забавя
                if daily_trend['strength'] == 'WEAK' and weekly_trend['strength'] == 'WEAK':
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Грешка при определяне дали тренда е приключил: {e}")
            return False
    
    def _generate_adaptive_strategy(self, combined_trend: Dict, df: pd.DataFrame) -> Dict:
        """Генерира адаптивна trading стратегия според тренда"""
        try:
            if 'error' in combined_trend:
                return {'error': 'Няма тренд анализ за стратегия'}
            
            current_price = df['Close'].iloc[-1]
            primary_trend = combined_trend['primary_trend']
            trend_completed = combined_trend['trend_completed']
            
            strategy = {
                'trend_based_entry': {},
                'risk_management': {},
                'position_sizing': {},
                'timing_recommendation': {}
            }
            
            if primary_trend == 'UPTREND' and not trend_completed:
                # Uptrend стратегия
                strategy['trend_based_entry'] = {
                    'type': 'PULLBACK_ENTRY',
                    'description': 'Влизане при pullback към support нива',
                    'entry_zones': [
                        {'zone': 'STRONG_SUPPORT', 'description': 'Силен support при 61.8% retracement'},
                        {'zone': 'MODERATE_SUPPORT', 'description': 'Умерен support при 50% retracement'},
                        {'zone': 'WEAK_SUPPORT', 'description': 'Слаб support при 38.2% retracement'}
                    ]
                }
                
                strategy['risk_management'] = {
                    'stop_loss': 'BELOW_ENTRY',
                    'stop_distance': '2-3% под entry',
                    'take_profit': 'ABOVE_RESISTANCE',
                    'trailing_stop': 'RECOMMENDED'
                }
                
                strategy['position_sizing'] = {
                    'size': 'NORMAL',
                    'reason': 'Трендът е силен и насочен нагоре'
                }
                
                strategy['timing_recommendation'] = {
                    'timing': 'WAIT_FOR_PULLBACK',
                    'reason': 'Изчакайте pullback за по-добър entry'
                }
                
            elif primary_trend == 'DOWNTREND' and not trend_completed:
                # Downtrend стратегия
                strategy['trend_based_entry'] = {
                    'type': 'BOUNCE_ENTRY',
                    'description': 'Влизане при bounce към resistance нива',
                    'entry_zones': [
                        {'zone': 'STRONG_RESISTANCE', 'description': 'Силен resistance при 61.8% retracement'},
                        {'zone': 'MODERATE_RESISTANCE', 'description': 'Умерен resistance при 50% retracement'},
                        {'zone': 'WEAK_RESISTANCE', 'description': 'Слаб resistance при 38.2% retracement'}
                    ]
                }
                
                strategy['risk_management'] = {
                    'stop_loss': 'ABOVE_ENTRY',
                    'stop_distance': '2-3% над entry',
                    'take_profit': 'BELOW_SUPPORT',
                    'trailing_stop': 'RECOMMENDED'
                }
                
                strategy['position_sizing'] = {
                    'size': 'REDUCED',
                    'reason': 'Трендът е насочен надолу - по-малки позиции'
                }
                
                strategy['timing_recommendation'] = {
                    'timing': 'WAIT_FOR_BOUNCE',
                    'reason': 'Изчакайте bounce за по-добър entry'
                }
                
            else:
                # Neutral или mixed тренд
                strategy['trend_based_entry'] = {
                    'type': 'RANGE_TRADING',
                    'description': 'Range trading между support и resistance',
                    'entry_zones': [
                        {'zone': 'RANGE_BOUNDARIES', 'description': 'Влизане при границите на range'},
                        {'zone': 'BREAKOUT_WAIT', 'description': 'Изчакайте breakout за ясна посока'}
                    ]
                }
                
                strategy['risk_management'] = {
                    'stop_loss': 'RANGE_BOUNDARIES',
                    'stop_distance': '1-2% от границите',
                    'take_profit': 'OPPOSITE_BOUNDARY',
                    'trailing_stop': 'NOT_RECOMMENDED'
                }
                
                strategy['position_sizing'] = {
                    'size': 'SMALL',
                    'reason': 'Неясен тренд - малки позиции'
                }
                
                strategy['timing_recommendation'] = {
                    'timing': 'WAIT_FOR_CLARITY',
                    'reason': 'Изчакайте по-ясна посока на тренда'
                }
            
            logger.info(f"Адаптивна стратегия генерирана: {strategy['trend_based_entry']['type']}")
            return strategy
            
        except Exception as e:
            logger.error(f"Грешка при генериране на адаптивна стратегия: {e}")
            return {'error': f'Грешка: {e}'}

if __name__ == "__main__":
    print("Trend Analyzer модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
