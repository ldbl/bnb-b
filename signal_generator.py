"""
Signal Generator Module - Генерира Long/Short сигнали за BNB trading
Комбинира Fibonacci, седмични опашки и технически индикатори
Приоритет: Fib+Tail > само Fib > само Tail > RSI/MACD/BB
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
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
    """Клас за генериране на trading сигнали"""
    
    def __init__(self, config: Dict):
        """
        Инициализира генератора на сигнали
        
        Args:
            config: Конфигурационни параметри
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
    
    def generate_signal(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Dict[str, any]:
        """
        Генерира основен trading сигнал
        
        Args:
            daily_df: Daily OHLCV данни
            weekly_df: Weekly OHLCV данни
            
        Returns:
            Dict с генерирания сигнал
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
            if 'error' in ma_analysis:
                logger.warning(f"Moving Averages анализ неуспешен: {ma_analysis['error']}")
                ma_analysis = None
            
            # 12. Price Action Patterns Analysis (НОВО от ideas файла)
            patterns_analysis = self.patterns_analyzer.detect_all_patterns(daily_df)
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
                confluence_info
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
                         indicators_signals: Dict, confluence_info: Dict) -> Dict[str, any]:
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
