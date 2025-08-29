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
        
        # НОВИ ПАРАМЕТРИ ЗА ДЪЛГОСРОЧЕН АНАЛИЗ
        self.long_term_lookback_days = 180  # 6 месеца дългосрочен анализ
        self.medium_term_lookback_days = 90  # 3 месеца средносрочен анализ
        self.bull_market_threshold = 50.0   # 50%+ за STRONG_BULL
        self.sustained_bull_months = 12     # 12 месеца за sustained bull
        
        logger.info("Trend анализатор инициализиран")
        logger.info(f"Short-term lookback: {self.trend_lookback_days} дни")
        logger.info(f"Medium-term lookback: {self.medium_term_lookback_days} дни") 
        logger.info(f"Long-term lookback: {self.long_term_lookback_days} дни")
        logger.info(f"Trend threshold: {self.trend_threshold:.1%}")
        logger.info(f"Bull market threshold: {self.bull_market_threshold:.1f}%")
    
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
            
            # 1. Анализ на дневния тренд (краткосрочен)
            daily_trend = self._analyze_daily_trend(daily_df)
            
            # 2. Анализ на седмичния тренд
            weekly_trend = self._analyze_weekly_trend(weekly_df)
            
            # 3. НОВИ: Средносрочен и дългосрочен анализ
            medium_term_trend = self._analyze_medium_term_trend(daily_df)
            long_term_trend = self._analyze_long_term_trend(daily_df)
            
            # 4. Range анализ
            range_analysis = self._analyze_price_range(daily_df)
            
            # 5. НОВИ: Market regime detection
            market_regime = self._detect_market_regime(daily_df, medium_term_trend, long_term_trend)
            
            # 6. Комбиниран тренд анализ (обновен)
            combined_trend = self._combine_trend_analysis(daily_trend, weekly_trend, medium_term_trend, long_term_trend, range_analysis, market_regime)
            
            # 5. Генерираме адаптивни entry стратегии
            adaptive_strategy = self._generate_adaptive_strategy(combined_trend, daily_df)
            
            trend_analysis = {
                'daily_trend': daily_trend,
                'weekly_trend': weekly_trend,
                'medium_term_trend': medium_term_trend,
                'long_term_trend': long_term_trend,
                'market_regime': market_regime,
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
    
    def _combine_trend_analysis(self, daily_trend: Dict, weekly_trend: Dict, medium_term_trend: Dict, long_term_trend: Dict, range_analysis: Dict, market_regime: Dict) -> Dict:
        """Комбинира различните тренд анализи с нов дългосрочен анализ"""
        try:
            if ('error' in daily_trend or 'error' in weekly_trend or 'error' in range_analysis or 
                'error' in medium_term_trend or 'error' in long_term_trend):
                return {'error': 'Грешка в един от тренд анализите'}
            
            # НОВА ЛОГИКА: Приоритизираме дългосрочния тренд
            long_direction = long_term_trend['direction']
            medium_direction = medium_term_trend['direction'] 
            daily_direction = daily_trend['direction']
            
            # Определяме основния тренд базирано на дългосрочен анализ
            if long_direction == medium_direction == daily_direction:
                primary_trend = long_direction
                trend_confidence = 'VERY_HIGH'
            elif long_direction == medium_direction:
                primary_trend = long_direction  # Дългосрочният и средносрочният са по-важни
                trend_confidence = 'HIGH'
            elif long_direction == daily_direction:
                primary_trend = long_direction  # Дългосрочният е най-важен
                trend_confidence = 'HIGH'
            elif medium_direction == daily_direction:
                primary_trend = medium_direction  # Краткосрочна доминация
                trend_confidence = 'MEDIUM'
            else:
                primary_trend = 'MIXED'
                trend_confidence = 'LOW'
            
            # ENHANCED: Включваме market regime в анализа
            regime_adjusted_trend = primary_trend
            if market_regime['regime'] == 'STRONG_BULL':
                # В STRONG_BULL, дори MIXED става UPTREND
                if primary_trend in ['MIXED', 'NEUTRAL']:
                    regime_adjusted_trend = 'UPTREND (STRONG)'
                elif primary_trend == 'UPTREND':
                    regime_adjusted_trend = 'UPTREND (STRONG)'
                # DOWNTREND остава, но с предупреждение
                elif primary_trend == 'DOWNTREND':
                    regime_adjusted_trend = 'DOWNTREND (AGAINST_REGIME)'
            
            # Изчисляваме общата сила на тренда (обновено)
            daily_strength = self._strength_to_score(daily_trend['strength'])
            weekly_strength = self._strength_to_score(weekly_trend['strength'])
            medium_strength = self._strength_to_score(medium_term_trend['strength'])
            long_strength = self._strength_to_score(long_term_trend['strength'])
            
            # Тегловен average с приоритет на дългосрочния
            combined_strength = (
                daily_strength * 0.1 + 
                weekly_strength * 0.2 + 
                medium_strength * 0.3 + 
                long_strength * 0.4
            )
            
            # Определяме дали тренда е приключил (обновено)
            trend_completed = self._is_trend_completed_enhanced(daily_trend, weekly_trend, medium_term_trend, long_term_trend, range_analysis, market_regime)
            
            combined_trend = {
                'primary_trend': primary_trend,
                'regime_adjusted_trend': regime_adjusted_trend,
                'trend_confidence': trend_confidence,
                'combined_strength': combined_strength,
                'trend_completed': trend_completed,
                'market_regime': market_regime['regime'],
                'regime_confidence': market_regime['confidence'],
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
                'medium_term_summary': {
                    'direction': medium_term_trend['direction'],
                    'strength': medium_term_trend['strength'],
                    'change_pct': medium_term_trend['price_change_pct']
                },
                'long_term_summary': {
                    'direction': long_term_trend['direction'],
                    'strength': long_term_trend['strength'],
                    'change_pct': long_term_trend['price_change_pct']
                },
                'range_summary': {
                    'status': range_analysis['range_status'],
                    'position': range_analysis['range_position']
                }
            }
            
            logger.info(f"Комбиниран тренд: {regime_adjusted_trend} (увереност: {trend_confidence}, приключил: {trend_completed})")
            logger.info(f"Market Regime: {market_regime['regime']} ({market_regime['confidence']:.2f})")
            return combined_trend
            
        except Exception as e:
            logger.error(f"Грешка при комбиниране на тренд анализите: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _strength_to_score(self, strength: str) -> float:
        """Конвертира силата на тренда в числов score"""
        strength_map = {'WEAK': 0.3, 'MODERATE': 0.6, 'STRONG': 1.0}
        return strength_map.get(strength, 0.5)
    
    def _is_trend_completed_enhanced(self, daily_trend: Dict, weekly_trend: Dict, medium_term_trend: Dict, long_term_trend: Dict, range_analysis: Dict, market_regime: Dict) -> bool:
        """Определя дали тренда е приключил (enhanced version)"""
        try:
            # В STRONG_BULL режим, тренда почти никога не е "приключил"
            if market_regime['regime'] == 'STRONG_BULL' and market_regime['confidence'] > 0.7:
                # STRONG_BULL продължава освен при екстремни условия
                if range_analysis['range_position'] > 0.95:  # Много близо до ATH
                    return daily_trend['strength'] == 'WEAK' and weekly_trend['strength'] == 'WEAK'
                else:
                    return False  # STRONG_BULL продължава
            
            # За другите режими използваме стандартна логика
            if long_term_trend['direction'] == 'UPTREND':
                # За uptrend, проверяваме дали има признаци на изчерпване
                if range_analysis['range_position'] > 0.8:
                    # Трите timeframe-а показват слабост?
                    weak_signals = 0
                    if daily_trend['strength'] == 'WEAK': weak_signals += 1
                    if weekly_trend['strength'] == 'WEAK': weak_signals += 1  
                    if medium_term_trend['strength'] == 'WEAK': weak_signals += 1
                    
                    return weak_signals >= 2  # Поне 2 от 3 timeframe-а са слаби
                    
            elif long_term_trend['direction'] == 'DOWNTREND':
                # За downtrend, проверяваме за bottom сигнали
                if range_analysis['range_position'] < 0.2:
                    weak_signals = 0
                    if daily_trend['strength'] == 'WEAK': weak_signals += 1
                    if weekly_trend['strength'] == 'WEAK': weak_signals += 1
                    if medium_term_trend['strength'] == 'WEAK': weak_signals += 1
                    
                    return weak_signals >= 2
            
            return False
            
        except Exception as e:
            logger.error(f"Грешка при определяне дали тренда е приключил: {e}")
            return False

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

    def _analyze_medium_term_trend(self, df: pd.DataFrame) -> Dict:
        """Анализира средносрочния тренд (90 дни)"""
        try:
            if len(df) < self.medium_term_lookback_days:
                return {'error': f'Недостатъчно данни за средносрочен анализ (нужни: {self.medium_term_lookback_days})'}
            
            # Взимаме последните 90 дни
            recent_data = df.tail(self.medium_term_lookback_days)
            
            # Линейна регресия
            x = np.arange(len(recent_data))
            y = recent_data['Close'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Изчисляваме промяната в цената
            start_price = y[0]
            end_price = y[-1]
            price_change = end_price - start_price
            price_change_pct = (price_change / start_price) * 100
            
            # Определяме силата на тренда (по-високи прагове за по-дълъг период)
            if abs(price_change_pct) < 15:
                trend_strength = 'WEAK'
            elif abs(price_change_pct) < 35:
                trend_strength = 'MODERATE'
            elif abs(price_change_pct) < 60:
                trend_strength = 'STRONG'
            else:
                trend_strength = 'EXTREME'
            
            # Определяме посоката на тренда (по-голям threshold за по-дълъг период)
            threshold = self.trend_threshold * 3  # 3x по-голям threshold за 90 дни
            if slope > threshold:
                trend_direction = 'UPTREND'
            elif slope < -threshold:
                trend_direction = 'DOWNTREND'
            else:
                trend_direction = 'NEUTRAL'
            
            medium_trend = {
                'direction': trend_direction,
                'strength': trend_strength,
                'slope': slope,
                'r_squared': r_value ** 2,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'start_price': start_price,
                'end_price': end_price,
                'lookback_days': self.medium_term_lookback_days,
                'significance': 'HIGH' if p_value < 0.01 else 'MEDIUM' if p_value < 0.05 else 'LOW'
            }
            
            logger.info(f"Средносрочен тренд (90d): {trend_direction} ({trend_strength}) - {price_change_pct:+.2f}%")
            return medium_trend
            
        except Exception as e:
            logger.error(f"Грешка при анализ на средносрочния тренд: {e}")
            return {'error': f'Грешка: {e}'}

    def _analyze_long_term_trend(self, df: pd.DataFrame) -> Dict:
        """Анализира дългосрочния тренд (180 дни)"""
        try:
            if len(df) < self.long_term_lookback_days:
                return {'error': f'Недостатъчно данни за дългосрочен анализ (нужни: {self.long_term_lookback_days})'}
            
            # Взимаме последните 180 дни
            recent_data = df.tail(self.long_term_lookback_days)
            
            # Линейна регресия
            x = np.arange(len(recent_data))
            y = recent_data['Close'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Изчисляваме промяната в цената
            start_price = y[0]
            end_price = y[-1]
            price_change = end_price - start_price
            price_change_pct = (price_change / start_price) * 100
            
            # Определяме силата на тренда (още по-високи прагове за 180 дни)
            if abs(price_change_pct) < 25:
                trend_strength = 'WEAK'
            elif abs(price_change_pct) < 50:
                trend_strength = 'MODERATE'
            elif abs(price_change_pct) < 100:
                trend_strength = 'STRONG'
            else:
                trend_strength = 'EXTREME'
            
            # Определяме посоката на тренда (още по-голям threshold за 180 дни)
            threshold = self.trend_threshold * 5  # 5x по-голям threshold за 180 дни
            if slope > threshold:
                trend_direction = 'UPTREND'
            elif slope < -threshold:
                trend_direction = 'DOWNTREND'
            else:
                trend_direction = 'NEUTRAL'
            
            long_trend = {
                'direction': trend_direction,
                'strength': trend_strength,
                'slope': slope,
                'r_squared': r_value ** 2,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'start_price': start_price,
                'end_price': end_price,
                'lookback_days': self.long_term_lookback_days,
                'significance': 'HIGH' if p_value < 0.001 else 'MEDIUM' if p_value < 0.01 else 'LOW'
            }
            
            logger.info(f"Дългосрочен тренд (180d): {trend_direction} ({trend_strength}) - {price_change_pct:+.2f}%")
            return long_trend
            
        except Exception as e:
            logger.error(f"Грешка при анализ на дългосрочния тренд: {e}")
            return {'error': f'Грешка: {e}'}

    def _detect_market_regime(self, df: pd.DataFrame, medium_trend: Dict, long_trend: Dict) -> Dict:
        """Определя market regime базирано на дългосрочния анализ"""
        try:
            if 'error' in medium_trend or 'error' in long_trend:
                return {'regime': 'UNKNOWN', 'confidence': 0.0, 'reason': 'Недостатъчни данни'}
            
            # Анализираме 12-месечен период за sustained bull detection
            yearly_data = df.tail(365) if len(df) >= 365 else df
            yearly_change_pct = ((yearly_data['Close'].iloc[-1] / yearly_data['Close'].iloc[0]) - 1) * 100
            
            medium_change = medium_trend['price_change_pct']
            long_change = long_trend['price_change_pct']
            
            # STRONG_BULL критерии - ключово за SHORT блокиране
            if (long_change > self.bull_market_threshold and 
                medium_change > 20 and 
                yearly_change_pct > 60):
                regime = 'STRONG_BULL'
                confidence = min(0.9, (long_change / 100) + (yearly_change_pct / 200))
                reason = f'Sustained bull run: 6м {long_change:+.1f}%, 3м {medium_change:+.1f}%, 12м {yearly_change_pct:+.1f}%'
                
            # MODERATE_BULL
            elif (long_change > 25 and medium_change > 10):
                regime = 'MODERATE_BULL'
                confidence = min(0.8, (long_change / 60) + (medium_change / 40))
                reason = f'Moderate bull: 6м {long_change:+.1f}%, 3м {medium_change:+.1f}%'
                
            # WEAK_BULL
            elif (long_change > 10 and medium_change > 5):
                regime = 'WEAK_BULL'
                confidence = 0.6
                reason = f'Weak bull: 6м {long_change:+.1f}%, 3м {medium_change:+.1f}%'
                
            # BEAR MARKET
            elif (long_change < -20 and medium_change < -10):
                regime = 'BEAR'
                confidence = min(0.9, abs(long_change / 50) + abs(medium_change / 30))
                reason = f'Bear market: 6м {long_change:+.1f}%, 3м {medium_change:+.1f}%'
                
            # CORRECTION
            elif (long_change > 0 and medium_change < -10):
                regime = 'CORRECTION'
                confidence = 0.7
                reason = f'Correction phase: 6м {long_change:+.1f}%, но 3м {medium_change:+.1f}%'
                
            # NEUTRAL/RANGE
            else:
                regime = 'NEUTRAL'
                confidence = 0.5
                reason = f'Neutral range: 6м {long_change:+.1f}%, 3м {medium_change:+.1f}%'
            
            market_regime = {
                'regime': regime,
                'confidence': confidence,
                'reason': reason,
                'yearly_change_pct': yearly_change_pct,
                'long_term_change_pct': long_change,
                'medium_term_change_pct': medium_change,
                'bull_market_duration_months': self._estimate_bull_duration(df) if 'BULL' in regime else 0
            }
            
            logger.info(f"Market Regime: {regime} (confidence: {confidence:.2f}) - {reason}")
            return market_regime
            
        except Exception as e:
            logger.error(f"Грешка при определяне на market regime: {e}")
            return {'regime': 'UNKNOWN', 'confidence': 0.0, 'reason': f'Грешка: {e}'}

    def _estimate_bull_duration(self, df: pd.DataFrame) -> int:
        """Оценява продължителността на bull market в месеци"""
        try:
            # Търсим последния значителен bottom (20%+ спад от предишен връх)
            if len(df) < 60:  # Минимум 2 месеца данни
                return 0
                
            # Работим назад във времето
            current_price = df['Close'].iloc[-1]
            months_back = 0
            
            for i in range(30, min(len(df), 547)):  # До 18 месеца назад
                past_price = df['Close'].iloc[-(i)]
                price_increase = ((current_price / past_price) - 1) * 100
                
                if price_increase < 20:  # Не е значителен bull run
                    break
                    
                months_back = i // 30  # Конвертираме дни в месеци
                
            return months_back
            
        except Exception as e:
            logger.error(f"Грешка при оценка на bull duration: {e}")
            return 0

if __name__ == "__main__":
    print("Trend Analyzer модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
