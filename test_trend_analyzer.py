#!/usr/bin/env python3
"""
Test script for enhanced trend analyzer
"""

import sys
sys.path.append('.')

from trend_analyzer import TrendAnalyzer
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_enhanced_trend_analyzer():
    """Test the enhanced trend analyzer with simulated bull market data"""
    
    # Създаваме тестови данни за 365 дни (имитираме 18-месечен bull run)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    num_days = len(dates)
    np.random.seed(42)

    # Имитираме bull market с общ ръст от 87%
    base_price = 464
    daily_growth = (1.87) ** (1/num_days) - 1  # 87% за всички дни

    prices = [base_price]
    for i in range(1, num_days):
        # Добавяме volatility
        daily_change = daily_growth + np.random.normal(0, 0.02)  
        new_price = prices[-1] * (1 + daily_change)
        prices.append(new_price)

    # Създаваме DataFrame
    test_data = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, num_days)
    }, index=dates)

    # Weekly данни (просто resample)
    weekly_data = test_data.resample('W').agg({
        'Open': 'first',
        'High': 'max', 
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })

    # Конфигурация
    config = {'trend': {'trend_lookback_days': 30, 'trend_threshold': 0.015}}

    # Тестваме
    analyzer = TrendAnalyzer(config)
    result = analyzer.analyze_trend(test_data, weekly_data)

    print('=== ENHANCED TREND ANALYZER TEST ===')
    print(f"Final price: ${prices[-1]:.2f} (from ${prices[0]:.2f})")
    print(f"Total return: {((prices[-1]/prices[0])-1)*100:+.1f}%")
    print()
    
    if 'error' in result:
        print(f"ERROR: {result['error']}")
        return
        
    print(f"Market Regime: {result['market_regime']['regime']}")
    print(f"Regime Confidence: {result['market_regime']['confidence']:.2f}")
    print(f"Regime Reason: {result['market_regime']['reason']}")
    print()
    print(f"Long-term trend: {result['long_term_trend']['direction']} ({result['long_term_trend']['strength']})")
    print(f"Long-term change: {result['long_term_trend']['price_change_pct']:+.1f}%")
    print()
    print(f"Combined trend: {result['combined_trend']['regime_adjusted_trend']}")
    print(f"Trend confidence: {result['combined_trend']['trend_confidence']}")
    
    # Тестваме дали правилно разпознава STRONG_BULL
    expected_regime = 'STRONG_BULL'
    actual_regime = result['market_regime']['regime']
    
    print()
    print("=== TEST RESULTS ===")
    if actual_regime == expected_regime:
        print("✅ SUCCESS: Correctly identified STRONG_BULL market")
    else:
        print(f"❌ FAILED: Expected {expected_regime}, got {actual_regime}")
        
    # Проверяваме confidence
    if result['market_regime']['confidence'] > 0.7:
        print("✅ SUCCESS: High confidence in regime detection")
    else:
        print(f"⚠️  WARNING: Low confidence ({result['market_regime']['confidence']:.2f})")

if __name__ == "__main__":
    test_enhanced_trend_analyzer()