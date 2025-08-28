#!/usr/bin/env python3
"""
🧠 SmartShortSignalGenerator - Интелигентна SHORT Сигнал Генерация
===================================================================

Този модул имплементира context-aware SHORT signal generation система
с фокус върху качество над количество. Всяка SHORT сигнал преминава
през 7-layer validation преди да бъде одобрен.

Author: Stanislav Nedelchev
Date: 2025-08-28
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ShortSignalCandidate:
    """Кандидат за SHORT сигнал с всички анализи"""
    timestamp: pd.Timestamp
    price: float
    confidence: float
    reasons: List[str]
    confluence_score: int
    risk_reward_ratio: float
    stop_loss_price: float
    take_profit_price: float
    market_regime: str
    ath_distance_pct: float
    volume_divergence: bool
    timeframe_alignment: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for signal processing"""
        return {
            'timestamp': self.timestamp,
            'price': self.price,
            'confidence': self.confidence,
            'reasons': self.reasons,
            'confluence_score': self.confluence_score,
            'risk_reward_ratio': self.risk_reward_ratio,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'market_regime': self.market_regime,
            'ath_distance_pct': self.ath_distance_pct,
            'volume_divergence': self.volume_divergence,
            'timeframe_alignment': self.timeframe_alignment
        }


class MarketRegimeDetector:
    """
    Детектор за пазарни режими - основата за SHORT решения
    """

    def __init__(self):
        self.regime_thresholds = {
            'STRONG_BULL': {'trend_strength': 2.0, 'volume_trend': 'increasing'},
            'MODERATE_BULL': {'trend_strength': 1.0, 'volume_trend': 'stable'},
            'NEUTRAL': {'trend_strength': 0.2, 'volume_trend': 'any'},
            'MODERATE_BEAR': {'trend_strength': -1.0, 'volume_trend': 'decreasing'},
            'STRONG_BEAR': {'trend_strength': -2.0, 'volume_trend': 'decreasing'}
        }

    def detect_market_regime(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Детектира текущия пазарен режим базирано на:
        - Trend strength (daily & weekly)
        - Volume trends
        - ATH proximity
        - RSI levels
        """

        try:
            # Daily trend analysis
            daily_trend = self._calculate_trend_strength(daily_df, 'Close', 20)
            daily_volume_trend = self._analyze_volume_trend(daily_df, 20)

            # Weekly trend analysis
            weekly_trend = self._calculate_trend_strength(weekly_df, 'Close', 4) if weekly_df is not None else 0
            weekly_volume_trend = self._analyze_volume_trend(weekly_df, 4) if weekly_df is not None else 'unknown'

            # ATH proximity
            current_price = daily_df['Close'].iloc[-1]
            ath_price = daily_df['ATH'].max()
            ath_distance_pct = ((ath_price - current_price) / ath_price) * 100

            # RSI levels
            rsi_current = daily_df['RSI'].iloc[-1] if 'RSI' in daily_df.columns else 50

            # Determine regime
            regime = self._classify_regime(
                daily_trend, weekly_trend,
                daily_volume_trend, weekly_volume_trend,
                ath_distance_pct, rsi_current
            )

            return {
                'regime': regime,
                'daily_trend': daily_trend,
                'weekly_trend': weekly_trend,
                'daily_volume_trend': daily_volume_trend,
                'weekly_volume_trend': weekly_volume_trend,
                'ath_distance_pct': ath_distance_pct,
                'rsi_current': rsi_current,
                'short_signals_allowed': self._are_short_signals_allowed(regime, ath_distance_pct),
                'confidence': self._calculate_regime_confidence(daily_trend, weekly_trend)
            }

        except Exception as e:
            logger.error(f"Грешка при market regime detection: {e}")
            return {
                'regime': 'UNKNOWN',
                'error': str(e),
                'short_signals_allowed': False,
                'confidence': 0.0
            }

    def _calculate_trend_strength(self, df: pd.DataFrame, column: str, lookback: int) -> float:
        """Изчислява сила на тренда (от -3 до +3)"""
        try:
            # Check if column exists with different case
            if column not in df.columns:
                # Try with capitalized first letter
                column = column.capitalize()
                if column not in df.columns:
                    logger.error(f"Колона {column} не е намерена в DataFrame")
                    return 0.0

            prices = df[column].tail(lookback)
            if len(prices) < lookback:
                return 0.0

            # Linear regression slope normalized
            x = np.arange(len(prices))
            slope = np.polyfit(x, prices, 1)[0]

            # Normalize by price volatility
            price_std = prices.std()
            if price_std == 0:
                return 0.0

            normalized_slope = slope / price_std

            # Clamp between -3 and +3
            return max(-3.0, min(3.0, normalized_slope))

        except Exception as e:
            logger.error(f"Грешка при trend strength calculation: {e}")
            return 0.0

    def _analyze_volume_trend(self, df: pd.DataFrame, lookback: int) -> str:
        """Анализира тренда на обема"""
        try:
            if 'volume' not in df.columns:
                return 'unknown'

            volumes = df['Volume'].tail(lookback)
            if len(volumes) < lookback:
                return 'unknown'

            # Simple trend analysis
            first_half = volumes[:lookback//2].mean()
            second_half = volumes[lookback//2:].mean()

            ratio = second_half / first_half if first_half > 0 else 1.0

            if ratio > 1.2:
                return 'increasing'
            elif ratio < 0.8:
                return 'decreasing'
            else:
                return 'stable'

        except Exception as e:
            logger.error(f"Грешка при volume trend analysis: {e}")
            return 'unknown'

    def _classify_regime(self, daily_trend: float, weekly_trend: float,
                        daily_volume: str, weekly_volume: str,
                        ath_distance: float, rsi: float) -> str:
        """Класифицира пазарния режим"""

        # Strong bull signals
        if (daily_trend > 1.5 and weekly_trend > 1.0 and
            ath_distance < 5.0 and rsi > 70):
            return 'STRONG_BULL'

        # Moderate bull
        elif (daily_trend > 0.8 and weekly_trend > 0.5 and
              ath_distance < 15.0 and rsi > 60):
            return 'MODERATE_BULL'

        # Neutral
        elif (abs(daily_trend) < 0.5 and abs(weekly_trend) < 0.5 and
              40 <= rsi <= 60):
            return 'NEUTRAL'

        # Moderate bear
        elif (daily_trend < -0.8 and weekly_trend < -0.5 and
              ath_distance > 10.0 and rsi < 40):
            return 'MODERATE_BEAR'

        # Strong bear
        elif (daily_trend < -1.5 and weekly_trend < -1.0 and
              ath_distance > 20.0 and rsi < 30):
            return 'STRONG_BEAR'

        else:
            return 'NEUTRAL'

    def _are_short_signals_allowed(self, regime: str, ath_distance: float) -> bool:
        """Определя дали SHORT сигнали са позволени"""
        # Never allow SHORT in strong bull markets
        if regime == 'STRONG_BULL':
            return False

        # Allow SHORT only if close to ATH (within 20%)
        if ath_distance > 20.0:
            return False

        # Allow in moderate bull, neutral, and bear markets
        return regime in ['MODERATE_BULL', 'NEUTRAL', 'MODERATE_BEAR', 'STRONG_BEAR']

    def _calculate_regime_confidence(self, daily_trend: float, weekly_trend: float) -> float:
        """Изчислява увереността в regime detection"""
        # Higher confidence when daily and weekly trends align
        alignment = 1.0 - abs(daily_trend - weekly_trend) / 6.0  # Max difference is 6
        strength = min(abs(daily_trend), abs(weekly_trend)) / 3.0  # Max strength is 3

        return min(1.0, (alignment + strength) / 2.0)


class SmartShortSignalGenerator:
    """
    Основен клас за интелигентна SHORT сигнал генерация
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация на Smart SHORT Generator

        Args:
            config: Конфигурация от config.toml
        """
        self.config = config
        self.market_detector = MarketRegimeDetector()

        # SHORT specific thresholds
        self.short_thresholds = {
            'min_ath_distance_pct': 5.0,      # Minimum distance from ATH for SHORT
            'max_ath_distance_pct': 25.0,     # Maximum distance from ATH for SHORT
            'min_confluence_score': 3,         # Minimum confluence requirements
            'min_risk_reward_ratio': 1.5,     # Minimum R:R ratio
            'max_stop_loss_pct': 5.0,         # Maximum stop loss percentage
            'volume_divergence_required': True,
            'timeframe_alignment_required': True
        }

        logger.info("🧠 SmartShortSignalGenerator инициализиран")

    def generate_short_signals(self, daily_df: pd.DataFrame,
                             weekly_df: Optional[pd.DataFrame] = None) -> List[ShortSignalCandidate]:
        """
        Основен метод за генерация на SHORT сигнали

        Args:
            daily_df: Daily timeframe data
            weekly_df: Weekly timeframe data (optional)

        Returns:
            List of validated SHORT signal candidates
        """

        logger.info("🎯 Започвам SHORT сигнал анализ...")

        candidates = []

        try:
            # Step 1: Market Regime Detection
            market_regime = self.market_detector.detect_market_regime(daily_df, weekly_df)

            if not market_regime['short_signals_allowed']:
                logger.info(f"🚫 SHORT сигнали блокирани: {market_regime['regime']} regime")
                return []

            logger.info(f"📊 Market Regime: {market_regime['regime']} (confidence: {market_regime['confidence']:.2f})")

            # Step 2: Scan for potential SHORT setups
            potential_setups = self._scan_for_short_setups(daily_df)

            logger.info(f"🔍 Намерени {len(potential_setups)} потенциални SHORT setups")

            # Step 3: Validate each setup through 7-layer validation
            for setup in potential_setups:
                candidate = self._validate_short_setup(setup, daily_df, weekly_df, market_regime)
                if candidate:
                    candidates.append(candidate)

            logger.info(f"✅ Генерирани {len(candidates)} валидни SHORT сигнали")

            # Step 4: Sort by quality (confidence and confluence)
            candidates.sort(key=lambda x: (x.confidence, x.confluence_score), reverse=True)

            return candidates[:10]  # Return top 10 candidates

        except Exception as e:
            logger.error(f"❌ Грешка при SHORT сигнал генерация: {e}")
            return []

    def _scan_for_short_setups(self, daily_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Сканира за потенциални SHORT setups базирано на:
        - Price action patterns
        - Technical indicators
        - Volume analysis
        """

        setups = []

        try:
            # Look for SHORT setups in recent candles
            lookback_period = 20

            for i in range(lookback_period, len(daily_df)):
                candle_data = daily_df.iloc[i]

                # Check for bearish price action
                if self._is_bearish_price_action(daily_df.iloc[i-lookback_period:i+1]):
                    setup = {
                        'timestamp': candle_data.name,
                        'price': candle_data['Close'],
                        'index': i,
                        'pattern_type': 'bearish_price_action'
                    }
                    setups.append(setup)

                # Check for overbought RSI
                if (hasattr(candle_data, 'RSI') and
                    candle_data['RSI'] > 75 and
                    candle_data['Close'] > candle_data['Open']):  # Shooting star like

                    setup = {
                        'timestamp': candle_data.name,
                        'price': candle_data['Close'],
                        'index': i,
                        'pattern_type': 'overbought_rsi'
                    }
                    setups.append(setup)

        except Exception as e:
            logger.error(f"Грешка при scanning for SHORT setups: {e}")

        return setups

    def _is_bearish_price_action(self, candles_df: pd.DataFrame) -> bool:
        """Проверява за bearish price action patterns"""
        try:
            if len(candles_df) < 5:
                return False

            # Check for shooting star pattern
            last_candle = candles_df.iloc[-1]
            body_size = abs(last_candle['Close'] - last_candle['Open'])
            upper_wick = last_candle['High'] - max(last_candle['Close'], last_candle['Open'])
            lower_wick = min(last_candle['Close'], last_candle['Open']) - last_candle['Low']

            # Shooting star: small body, long upper wick, small lower wick
            if (upper_wick > body_size * 2 and
                lower_wick < body_size * 0.5 and
                upper_wick > lower_wick * 2):
                return True

            return False

        except Exception as e:
            logger.error(f"Грешка при bearish price action check: {e}")
            return False

    def _validate_short_setup(self, setup: Dict[str, Any], daily_df: pd.DataFrame,
                            weekly_df: Optional[pd.DataFrame],
                            market_regime: Dict[str, Any]) -> Optional[ShortSignalCandidate]:
        """
        7-Layer Validation за SHORT setup:

        1. Market Regime Check ✅
        2. ATH Proximity Validation
        3. Volume Divergence Confirmation
        4. Technical Indicators Alignment
        5. Timeframe Alignment Check
        6. Risk/Reward Assessment
        7. Confluence Scoring
        """

        try:
            reasons = []
            confluence_score = 0

            # Layer 1: Market Regime Check ✅ (already passed)

            # Layer 2: ATH Proximity Validation
            current_price = setup['price']
            ath_price = daily_df['ATH'].max()
            ath_distance_pct = ((ath_price - current_price) / ath_price) * 100

            if (ath_distance_pct < self.short_thresholds['min_ath_distance_pct'] or
                ath_distance_pct > self.short_thresholds['max_ath_distance_pct']):
                return None

            reasons.append(f"ATH distance: {ath_distance_pct:.1f}%")
            confluence_score += 1

            # Layer 3: Volume Divergence Confirmation
            volume_divergence = self._check_volume_divergence(daily_df, setup['index'])
            if self.short_thresholds['volume_divergence_required'] and not volume_divergence:
                return None

            if volume_divergence:
                reasons.append("Bearish volume divergence confirmed")
                confluence_score += 1

            # Layer 4: Technical Indicators Alignment
            indicators_aligned = self._check_technical_alignment(daily_df, setup['index'])
            if not indicators_aligned['aligned']:
                return None

            reasons.extend(indicators_aligned['reasons'])
            confluence_score += len(indicators_aligned['reasons'])

            # Layer 5: Timeframe Alignment Check
            timeframe_aligned = self._check_timeframe_alignment(daily_df, weekly_df, setup['index'])
            if self.short_thresholds['timeframe_alignment_required'] and not timeframe_aligned:
                return None

            if timeframe_aligned:
                reasons.append("Multi-timeframe alignment confirmed")
                confluence_score += 1

            # Layer 6: Risk/Reward Assessment
            risk_reward = self._calculate_risk_reward(setup['price'], daily_df, setup['index'])
            if risk_reward < self.short_thresholds['min_risk_reward_ratio']:
                return None

            reasons.append(f"Risk/Reward: 1:{risk_reward:.1f}")

            # Layer 7: Final Confluence Check
            if confluence_score < self.short_thresholds['min_confluence_score']:
                return None

            # Calculate confidence based on confluence and market conditions
            confidence = min(0.95, confluence_score / 7.0 * market_regime['confidence'])

            # Calculate stop loss and take profit
            stop_loss_price = setup['price'] * (1 + self.short_thresholds['max_stop_loss_pct'] / 100)
            take_profit_price = setup['price'] * (1 - (risk_reward * self.short_thresholds['max_stop_loss_pct'] / 100))

            return ShortSignalCandidate(
                timestamp=setup['timestamp'],
                price=setup['price'],
                confidence=confidence,
                reasons=reasons,
                confluence_score=confluence_score,
                risk_reward_ratio=risk_reward,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                market_regime=market_regime['regime'],
                ath_distance_pct=ath_distance_pct,
                volume_divergence=volume_divergence,
                timeframe_alignment=timeframe_aligned
            )

        except Exception as e:
            logger.error(f"Грешка при SHORT setup validation: {e}")
            return None

    def _check_volume_divergence(self, df: pd.DataFrame, index: int) -> bool:
        """Проверява за bearish volume divergence"""
        try:
            lookback = 10

            if index < lookback:
                return False

            # Price trend (should be up for bearish divergence)
            price_start = df['Close'].iloc[index-lookback]
            price_end = df['Close'].iloc[index]
            price_trend = (price_end - price_start) / price_start

            # Volume trend (should be down for bearish divergence)
            volume_start = df['Volume'].iloc[index-lookback:index-lookback+5].mean()
            volume_end = df['Volume'].iloc[index-5:index].mean()
            volume_trend = (volume_end - volume_start) / volume_start if volume_start > 0 else 0

            # Bearish divergence: price up, volume down
            return price_trend > 0.02 and volume_trend < -0.1

        except Exception as e:
            logger.error(f"Грешка при volume divergence check: {e}")
            return False

    def _check_technical_alignment(self, df: pd.DataFrame, index: int) -> Dict[str, Any]:
        """Проверява alignment на technical indicators"""
        try:
            reasons = []
            aligned_signals = 0

            # RSI check
            if 'RSI' in df.columns and df['RSI'].iloc[index] > 70:
                reasons.append("RSI overbought")
                aligned_signals += 1

            # MACD check
            if ('MACD' in df.columns and 'MACD_Signal' in df.columns and
                df['MACD'].iloc[index] < df['MACD_Signal'].iloc[index]):
                reasons.append("MACD bearish crossover")
                aligned_signals += 1

            # Bollinger Bands check
            if ('BB_Upper' in df.columns and 'BB_Lower' in df.columns and
                df['Close'].iloc[index] > df['BB_Upper'].iloc[index] * 0.98):  # Near upper band
                reasons.append("Near upper Bollinger Band")
                aligned_signals += 1

            return {
                'aligned': aligned_signals >= 2,  # At least 2 indicators aligned
                'reasons': reasons
            }

        except Exception as e:
            logger.error(f"Грешка при technical alignment check: {e}")
            return {'aligned': False, 'reasons': []}

    def _check_timeframe_alignment(self, daily_df: pd.DataFrame,
                                 weekly_df: Optional[pd.DataFrame], index: int) -> bool:
        """Проверява multi-timeframe alignment"""
        try:
            # Daily weakness check
            daily_trend = self.market_detector._calculate_trend_strength(daily_df, 'Close', 5)
            daily_weakness = daily_trend < -0.5

            if not daily_weakness:
                return False

            # Weekly neutrality check (if weekly data available)
            if weekly_df is not None and len(weekly_df) > 0:
                weekly_trend = self.market_detector._calculate_trend_strength(weekly_df, 'Close', 2)
                weekly_neutral = abs(weekly_trend) < 0.8
                return daily_weakness and weekly_neutral
            else:
                return daily_weakness

        except Exception as e:
            logger.error(f"Грешка при timeframe alignment check: {e}")
            return False

    def _calculate_risk_reward(self, entry_price: float, df: pd.DataFrame, index: int) -> float:
        """Изчислява Risk/Reward ratio за SHORT позиция"""
        try:
            # Stop loss based on recent volatility
            stop_distance_pct = self.short_thresholds['max_stop_loss_pct']

            # Take profit based on technical levels
            # Look for support levels or Fibonacci retracements
            lookback = min(20, index)
            recent_lows = df['Low'].iloc[index-lookback:index]

            # Target profit at 50% retracement of recent range
            recent_range = df['High'].iloc[index-lookback:index].max() - recent_lows.min()
            target_price = entry_price - (recent_range * 0.5)

            risk = entry_price * (stop_distance_pct / 100)
            reward = entry_price - target_price

            return reward / risk if risk > 0 else 0

        except Exception as e:
            logger.error(f"Грешка при risk/reward calculation: {e}")
            return 0


# Utility functions for integration
def create_short_signal_dict(candidate: ShortSignalCandidate) -> Dict[str, Any]:
    """Convert ShortSignalCandidate to signal dictionary"""
    signal_dict = candidate.to_dict()
    signal_dict.update({
        'signal': 'SHORT',
        'type': 'smart_short',
        'quality_score': candidate.confluence_score,
        'entry_price': candidate.price,
        'exit_plan': {
            'stop_loss': candidate.stop_loss_price,
            'take_profit': candidate.take_profit_price,
            'risk_reward_ratio': candidate.risk_reward_ratio
        }
    })
    return signal_dict


if __name__ == "__main__":
    # Quick test of the SmartShortSignalGenerator
    print("🧠 SmartShortSignalGenerator - Тест на функционалността")

    # This would normally be called from the main system
    print("✅ SmartShortSignalGenerator модул зареден успешно")
    print("🎯 Готов за интеграция в основната система!")
