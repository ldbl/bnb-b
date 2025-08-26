"""
Optimal Levels Module - Намира оптимални entry/exit нива базирани на най-много докосвания
Интегриран в основната BNB Trading система
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class OptimalLevelsAnalyzer:
    """Анализатор за оптимални trading нива базирани на исторически докосвания"""
    
    def __init__(self, config: Dict):
        """
        Инициализира анализатора
        
        Args:
            config: Конфигурационни параметри
        """
        self.price_interval = 25  # Интервал между ценови нива
        self.min_touches = 3      # Минимум докосвания за валидно ниво
        
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
                return {'error': 'Няма weekly данни за анализ'}
            
            # Създаваме ценови нива
            price_levels = self._create_price_levels(weekly_df)
            
            # Броим докосванията
            level_touches = self._count_level_touches(weekly_df, price_levels)
            
            # Намираме оптимални нива
            current_price = weekly_df['Close'].iloc[-1]
            optimal_levels = self._find_optimal_levels(level_touches, current_price)
            
            analysis = {
                'price_levels': price_levels,
                'level_touches': level_touches,
                'current_price': current_price,
                'optimal_levels': optimal_levels,
                'analysis_date': weekly_df.index[-1]
            }
            
            logger.info("Оптимални нива намерени успешно")
            return analysis
            
        except Exception as e:
            logger.error(f"Грешка при анализ на оптимални нива: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _create_price_levels(self, df: pd.DataFrame) -> List[float]:
        """Създава ценови нива за анализ"""
        try:
            min_price = df['Low'].min()
            max_price = df['High'].max()
            
            # Създаваме нива на всеки $25
            base_levels = list(np.arange(min_price - 100, max_price + 100, self.price_interval))
            
            # Добавяме нива около текущата цена
            current_price = df['Close'].iloc[-1]
            current_levels = list(np.arange(current_price - 200, current_price + 200, self.price_interval))
            
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
                low = row['Low']
                high = row['High']
                
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
            support_levels = [(price, touches) for price, touches in sorted_levels 
                             if price < current_price and touches >= self.min_touches]
            
            # Намираме resistance нива (над текущата цена)
            resistance_levels = [(price, touches) for price, touches in sorted_levels 
                               if price > current_price and touches >= self.min_touches]
            
            # Ако няма resistance нива над текущата цена, използваме най-високите
            if not resistance_levels:
                resistance_levels = [(price, touches) for price, touches in sorted_levels 
                                   if touches >= self.min_touches and price > current_price - 200]
                resistance_levels.sort(key=lambda x: x[0], reverse=True)
            
            optimal_levels = {
                'top_support_levels': support_levels[:5],
                'top_resistance_levels': resistance_levels[:5],
                'best_support': support_levels[0] if support_levels else None,
                'best_resistance': resistance_levels[0] if resistance_levels else None,
                'averaged_support': self._calculate_averaged_support(support_levels[:3]) if len(support_levels) >= 3 else None
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
                'price': avg_price,
                'touches': avg_touches,
                'reliability': 'HIGH' if avg_touches >= 10 else 'MEDIUM' if avg_touches >= 5 else 'LOW'
            }
            
        except Exception as e:
            logger.error(f"Грешка при изчисляване на усреднено support: {e}")
            return {}
    
    def get_trading_recommendations(self, optimal_levels: Dict) -> Dict:
        """Генерира trading препоръки"""
        try:
            if not optimal_levels or 'best_support' not in optimal_levels:
                return {'error': 'Няма оптимални нива за анализ'}
            
            best_support = optimal_levels['best_support']
            best_resistance = optimal_levels['best_resistance']
            averaged_support = optimal_levels.get('averaged_support')
            
            recommendations = {
                'long_strategy': {},
                'short_strategy': {},
                'risk_reward_analysis': {}
            }
            
            # LONG стратегия
            if best_support and best_resistance:
                entry_price = averaged_support['price'] if averaged_support and averaged_support['reliability'] == 'HIGH' else best_support[0]
                stop_loss = entry_price - 50
                target = best_resistance[0]
                
                risk = entry_price - stop_loss
                reward = target - entry_price
                risk_reward = reward / risk if risk > 0 else 0
                
                recommendations['long_strategy'] = {
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'target': target,
                    'risk_reward': risk_reward,
                    'entry_type': 'averaged' if averaged_support and averaged_support['reliability'] == 'HIGH' else 'individual'
                }
            
            # SHORT стратегия
            if best_resistance and best_support:
                entry_price = best_resistance[0]
                stop_loss = entry_price + 50
                target = averaged_support['price'] if averaged_support else best_support[0]
                
                risk = stop_loss - entry_price
                reward = entry_price - target
                risk_reward = reward / risk if risk > 0 else 0
                
                recommendations['short_strategy'] = {
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'target': target,
                    'risk_reward': risk_reward
                }
            
            # Risk/Reward анализ
            if recommendations['long_strategy']:
                recommendations['risk_reward_analysis'] = {
                    'long_risk_reward': recommendations['long_strategy']['risk_reward'],
                    'short_risk_reward': recommendations['short_strategy'].get('risk_reward', 0),
                    'recommended_strategy': 'LONG' if recommendations['long_strategy']['risk_reward'] > 2 else 'SHORT' if recommendations['short_strategy'].get('risk_reward', 0) > 2 else 'HOLD'
                }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Грешка при генериране на trading препоръки: {e}")
            return {'error': f'Грешка: {e}'}

if __name__ == "__main__":
    print("Optimal Levels модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
