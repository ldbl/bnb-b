"""
Elliott Wave Analyzer Module - Интегриран в BNB Trading System
Анализира Elliott Wave структурите за по-добри trading сигнали
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ElliottWaveAnalyzer:
    """Elliott Wave анализатор за BNB Trading System"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.lookback_periods = config.get('elliott_wave', {}).get('lookback_periods', 50)
        self.min_wave_strength = config.get('elliott_wave', {}).get('min_wave_strength', 0.02)
        
        # Elliott Wave описания
        self.wave_descriptions = {
            1: "Wave 1 - Initial impulse (buy opportunity)",
            2: "Wave 2 - Pullback (buy on dip)",
            3: "Wave 3 - Strongest trend (hold long)",
            4: "Wave 4 - Consolidation (buy opportunity)",
            5: "Wave 5 - Final push (prepare for reversal)"
        }
        
        # Wave степени
        self.wave_degrees = {
            "SUPERCYCLE": {"min_periods": 200, "symbol": "I, II, III, IV, V"},
            "CYCLE": {"min_periods": 100, "symbol": "1, 2, 3, 4, 5"},
            "PRIMARY": {"min_periods": 50, "symbol": "(1), (2), (3), (4), (5)"},
            "INTERMEDIATE": {"min_periods": 20, "symbol": "A, B, C"},
            "MINOR": {"min_periods": 10, "symbol": "a, b, c"},
            "MINUTE": {"min_periods": 5, "symbol": "i, ii, iii, iv, v"}
        }
        
        logger.info("Elliott Wave анализатор инициализиран")
    
    def analyze_elliott_wave(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Dict:
        """
        Анализира Elliott Wave структурите
        
        Args:
            daily_df: Daily данни
            weekly_df: Weekly данни
            
        Returns:
            Dict с Elliott Wave анализа
        """
        try:
            if daily_df.empty or weekly_df.empty:
                return {'error': 'Няма данни за анализ'}
            
            # Анализираме daily данните за Elliott Wave
            daily_analysis = self._analyze_timeframe(daily_df, 'daily')
            
            # Анализираме weekly данните за по-дългосрочна перспектива
            weekly_analysis = self._analyze_timeframe(weekly_df, 'weekly')
            
            # Комбинираме анализа
            combined_analysis = self._combine_analyses(daily_analysis, weekly_analysis)
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Грешка при Elliott Wave анализ: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """Анализира конкретен timeframe"""
        try:
            # Извличаме цените
            prices = df['close'].values if 'close' in df.columns else df['Close'].values
            
            if len(prices) < 20:
                return {'error': f'Недостатъчно данни за {timeframe} анализ'}
            
            # Намираме pivot точки
            pivots = self._find_pivot_points(prices)
            
            if len(pivots) < 3:
                return {
                    'wave': 'FORMING',
                    'confidence': 20,
                    'description': f'Pattern все още се формира - нужни са повече pivot точки',
                    'timeframe': timeframe
                }
            
            # Анализираме Elliott Wave структурата
            wave_analysis = self._analyze_wave_structure(pivots, prices, timeframe)
            
            # Валидираме Elliott Wave правилата
            validation = self._validate_elliott_rules(pivots)
            
            # Изчисляваме Fibonacci проекции
            projections = self._calculate_fibonacci_projections(pivots)
            
            return {
                'wave': wave_analysis['wave'],
                'confidence': wave_analysis['confidence'],
                'description': wave_analysis['description'],
                'trend': wave_analysis['trend'],
                'degree': wave_analysis['degree'],
                'pivot_count': len(pivots),
                'validation': validation,
                'projections': projections,
                'timeframe': timeframe
            }
            
        except Exception as e:
            logger.error(f"Грешка при анализ на {timeframe}: {e}")
            return {'error': f'Грешка при {timeframe} анализ: {e}'}
    
    def _find_pivot_points(self, prices: np.ndarray, lookback: int = 2) -> List[Dict]:
        """Намира local highs и lows (pivot точки)"""
        if len(prices) < lookback * 2 + 1:
            return []
        
        pivots = []
        
        for i in range(lookback, len(prices) - lookback):
            # Проверяваме за local high
            if (prices[i] > max(prices[i-lookback:i]) and 
                prices[i] > max(prices[i+1:i+lookback+1])):
                pivots.append({
                    "type": "HIGH",
                    "price": prices[i],
                    "index": i
                })
            
            # Проверяваме за local low
            elif (prices[i] < min(prices[i-lookback:i]) and 
                  prices[i] < min(prices[i+1:i+lookback+1])):
                pivots.append({
                    "type": "LOW",
                    "price": prices[i],
                    "index": i
                })
        
        return pivots
    
    def _analyze_wave_structure(self, pivots: List[Dict], prices: np.ndarray, timeframe: str) -> Dict:
        """Анализира Elliott Wave структурата"""
        if len(pivots) < 3:
            return {
                'wave': 'FORMING',
                'confidence': 20,
                'description': 'Недостатъчно pivot точки',
                'trend': 'UNKNOWN',
                'degree': 'UNKNOWN'
            }
        
        # Определяме тренда
        trend = self._determine_trend(pivots, prices)
        
        # Броим вълните
        wave_count = self._count_waves(pivots)
        
        # Определяме степента
        degree = self._determine_wave_degree(len(prices))
        
        # Анализираме конкретната вълна
        wave_number = self._identify_current_wave(pivots, trend, wave_count)
        
        # Изчисляваме confidence
        confidence = self._calculate_wave_confidence(pivots, wave_count, degree)
        
        return {
            'wave': f'WAVE_{wave_number}',
            'confidence': confidence,
            'description': self.wave_descriptions.get(wave_number, 'Unknown wave'),
            'trend': trend,
            'degree': degree,
            'wave_count': wave_count
        }
    
    def _determine_trend(self, pivots: List[Dict], prices: np.ndarray) -> str:
        """Определя тренда"""
        if len(pivots) < 2:
            return "SIDEWAYS"
        
        # Сравняваме първата и последната pivot точка
        first_pivot = pivots[0]
        last_pivot = pivots[-1]
        
        # Проверяваме и текущата цена спрямо началната
        price_trend = prices[-1] > prices[0]
        
        if last_pivot["price"] > first_pivot["price"] and price_trend:
            return "UPTREND"
        elif last_pivot["price"] < first_pivot["price"] and not price_trend:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    
    def _count_waves(self, pivots: List[Dict]) -> int:
        """Брои Elliott Wave вълните"""
        if len(pivots) < 2:
            return 1
        
        wave_count = 1
        valid_alternations = 0
        
        for i in range(1, len(pivots)):
            if pivots[i]["type"] != pivots[i-1]["type"]:
                # Проверяваме дали това е значително движение (поне 2% промяна в цената)
                price_change = abs(pivots[i]["price"] - pivots[i-1]["price"])
                avg_price = (pivots[i]["price"] + pivots[i-1]["price"]) / 2
                change_percent = (price_change / avg_price) * 100
                
                if change_percent >= self.min_wave_strength * 100:  # Минимум 2% движение
                    wave_count += 1
                    valid_alternations += 1
        
        # Коригираме броя на вълните базирано на валидността на pattern-а
        if valid_alternations < 2:
            return 1  # Недостатъчно значителни движения
        
        return min(wave_count, 5)  # Максимум 5 вълни в impulse
    
    def _identify_current_wave(self, pivots: List[Dict], trend: str, wave_count: int) -> int:
        """Идентифицира текущата вълна"""
        if trend == "UPTREND":
            if wave_count >= 5:
                return 5  # Wave 5 - последна вълна
            elif wave_count >= 3:
                return 3  # Wave 3 - най-силната вълна
            elif wave_count >= 1:
                return 1  # Wave 1 - начална вълна
        elif trend == "DOWNTREND":
            if wave_count >= 3:
                return 3  # Wave C - последна correction вълна
            elif wave_count >= 1:
                return 1  # Wave A - начална correction вълна
        
        return wave_count
    
    def _determine_wave_degree(self, data_length: int) -> str:
        """Определя степента на вълната базирано на дължината на данните"""
        for degree, info in self.wave_degrees.items():
            if data_length >= info["min_periods"]:
                return degree
        return "MINUTE"
    
    def _calculate_wave_confidence(self, pivots: List[Dict], wave_count: int, degree: str) -> int:
        """Изчислява confidence за Elliott Wave анализа"""
        base_confidence = min(50 + (len(pivots) * 5), 90)
        
        # Коригираме за степента
        degree_modifier = 1.0
        if degree in ["SUPERCYCLE", "CYCLE"]:
            degree_modifier = 1.2
        elif degree in ["PRIMARY", "INTERMEDIATE"]:
            degree_modifier = 1.0
        else:
            degree_modifier = 0.8
        
        # Коригираме за броя на вълните
        wave_modifier = min(1.0 + (wave_count * 0.1), 1.5)
        
        final_confidence = int(base_confidence * degree_modifier * wave_modifier)
        return min(final_confidence, 95)
    
    def _validate_elliott_rules(self, pivots: List[Dict]) -> Dict:
        """Валидира Elliott Wave правилата"""
        if len(pivots) < 5:
            return {"valid": False, "violations": ["Нужни са поне 5 pivot точки"]}
        
        violations = []
        
        # Взимаме последните 5 pivot точки за 5-wave анализ
        wave_pivots = pivots[-5:] if len(pivots) >= 5 else pivots
        
        # Правило 1: Wave 2 никога не retrace-ва повече от 100% на Wave 1
        if len(wave_pivots) >= 3:
            wave1_start = wave_pivots[0]["price"]
            wave1_end = wave_pivots[1]["price"]
            wave2_end = wave_pivots[2]["price"]
            
            wave1_length = abs(wave1_end - wave1_start)
            wave2_retrace = abs(wave2_end - wave1_end)
            
            if wave2_retrace > wave1_length:
                violations.append("Wave 2 retrace-ва повече от 100% на Wave 1")
        
        # Правило 2: Wave 3 никога не е най-късата вълна
        if len(wave_pivots) >= 4:
            wave1_len = abs(wave_pivots[1]["price"] - wave_pivots[0]["price"])
            wave3_len = abs(wave_pivots[3]["price"] - wave_pivots[2]["price"])
            
            if len(wave_pivots) == 5:
                wave5_len = abs(wave_pivots[4]["price"] - wave_pivots[3]["price"])
                if wave3_len <= wave1_len and wave3_len <= wave5_len:
                    violations.append("Wave 3 е най-късата вълна")
            elif wave3_len <= wave1_len:
                violations.append("Wave 3 е по-къса от Wave 1")
        
        # Правило 3: Wave 4 не трябва да overlap-ва Wave 1 price territory
        if len(wave_pivots) == 5:
            wave1_high = max(wave_pivots[0]["price"], wave_pivots[1]["price"])
            wave1_low = min(wave_pivots[0]["price"], wave_pivots[1]["price"])
            wave4_price = wave_pivots[3]["price"]
            
            if wave1_low <= wave4_price <= wave1_high:
                violations.append("Wave 4 overlap-ва Wave 1 territory")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "confidence_modifier": max(0, 1.0 - (len(violations) * 0.2))
        }
    
    def _calculate_fibonacci_projections(self, pivots: List[Dict]) -> Dict:
        """Изчислява Fibonacci проекции за вълните"""
        if len(pivots) < 3:
            return {"target": None, "extension": None}
        
        # Използваме последните 3 pivot точки за проекция
        recent_pivots = pivots[-3:]
        
        # Изчисляваме дължината на Wave 1
        wave1_length = abs(recent_pivots[1]["price"] - recent_pivots[0]["price"])
        
        # Често срещани Fibonacci проекции
        projections = {
            "0.618": recent_pivots[-1]["price"] + (wave1_length * 0.618),
            "1.0": recent_pivots[-1]["price"] + wave1_length,
            "1.618": recent_pivots[-1]["price"] + (wave1_length * 1.618)
        }
        
        return {
            "target": round(projections["1.0"], 2),
            "extension": round(projections["1.618"], 2),
            "all_levels": {k: round(v, 2) for k, v in projections.items()}
        }
    
    def _combine_analyses(self, daily_analysis: Dict, weekly_analysis: Dict) -> Dict:
        """Комбинира daily и weekly анализа"""
        try:
            # Проверяваме за грешки
            if 'error' in daily_analysis or 'error' in weekly_analysis:
                return {
                    'error': 'Грешка в един от timeframe анализите',
                    'daily': daily_analysis,
                    'weekly': weekly_analysis
                }
            
            # Комбинираме confidence
            daily_conf = daily_analysis.get('confidence', 0)
            weekly_conf = weekly_analysis.get('confidence', 0)
            combined_confidence = int((daily_conf + weekly_conf) / 2)
            
            # Определяме основния тренд
            primary_trend = weekly_analysis.get('trend', 'UNKNOWN')
            if primary_trend == 'UNKNOWN':
                primary_trend = daily_analysis.get('trend', 'UNKNOWN')
            
            # Определяме основната вълна
            primary_wave = weekly_analysis.get('wave', 'UNKNOWN')
            if primary_wave == 'UNKNOWN':
                primary_wave = daily_analysis.get('wave', 'UNKNOWN')
            
            # Генерираме trading сигнали
            trading_signals = self._generate_trading_signals(daily_analysis, weekly_analysis)
            
            return {
                'combined_analysis': {
                    'primary_trend': primary_trend,
                    'primary_wave': primary_wave,
                    'confidence': combined_confidence,
                    'degree': weekly_analysis.get('degree', 'UNKNOWN')
                },
                'daily_analysis': daily_analysis,
                'weekly_analysis': weekly_analysis,
                'trading_signals': trading_signals,
                'elliott_rules_valid': (
                    daily_analysis.get('validation', {}).get('valid', False) and
                    weekly_analysis.get('validation', {}).get('valid', False)
                )
            }
            
        except Exception as e:
            logger.error(f"Грешка при комбиниране на анализите: {e}")
            return {'error': f'Грешка при комбиниране: {e}'}
    
    def _generate_trading_signals(self, daily_analysis: Dict, weekly_analysis: Dict) -> Dict:
        """Генерира trading сигнали базирани на Elliott Wave анализа"""
        signals = {
            'action': 'WAIT',
            'confidence': 0,
            'reason': 'Elliott Wave анализ',
            'risk_level': 'MEDIUM'
        }
        
        daily_wave = daily_analysis.get('wave', '')
        weekly_wave = weekly_analysis.get('wave', '')
        daily_trend = daily_analysis.get('trend', '')
        weekly_trend = weekly_analysis.get('trend', '')
        
        # Wave-based сигнали
        if 'WAVE_2' in daily_wave and daily_trend == 'UPTREND':
            signals.update({
                'action': 'BUY',
                'reason': 'Wave 2 pullback - добра entry точка',
                'confidence': min(daily_analysis.get('confidence', 0) + 10, 95),
                'risk_level': 'LOW'
            })
        
        elif 'WAVE_3' in daily_wave and daily_trend == 'UPTREND':
            signals.update({
                'action': 'HOLD_LONG',
                'reason': 'Wave 3 - най-силният тренд, продължавай long',
                'confidence': daily_analysis.get('confidence', 0),
                'risk_level': 'LOW'
            })
        
        elif 'WAVE_5' in daily_wave and daily_trend == 'UPTREND':
            signals.update({
                'action': 'PREPARE_SELL',
                'reason': 'Wave 5 - трендът може да свърши скоро',
                'confidence': daily_analysis.get('confidence', 0),
                'risk_level': 'HIGH'
            })
        
        elif 'WAVE_4' in daily_wave and daily_trend == 'UPTREND':
            signals.update({
                'action': 'BUY_DIP',
                'reason': 'Wave 4 consolidation - купи на dip',
                'confidence': daily_analysis.get('confidence', 0),
                'risk_level': 'MEDIUM'
            })
        
        # Correction сигнали
        elif 'CORRECTION' in weekly_wave or weekly_trend == 'DOWNTREND':
            signals.update({
                'action': 'WAIT',
                'reason': 'Correction в ход - изчакай завършването',
                'confidence': weekly_analysis.get('confidence', 0),
                'risk_level': 'HIGH'
            })
        
        # Ако няма ясен сигнал, използваме confidence
        if signals['action'] == 'WAIT':
            combined_conf = (daily_analysis.get('confidence', 0) + weekly_analysis.get('confidence', 0)) / 2
            if combined_conf > 70:
                signals['confidence'] = combined_conf
            else:
                signals['confidence'] = combined_conf
        
        return signals

if __name__ == "__main__":
    print("Elliott Wave Analyzer модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
