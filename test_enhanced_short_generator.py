#!/usr/bin/env python3
"""
Test script for enhanced smart short generator with market regime blocking
"""

import sys
sys.path.append('.')

from smart_short_generator import SmartShortSignalGenerator
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_strong_bull_scenario():
    """Create test data simulating STRONG_BULL market (88% yearly gain)"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    num_days = len(dates)
    np.random.seed(42)
    
    # Strong bull market simulation
    base_price = 464
    daily_growth = (1.88) ** (1/num_days) - 1  # 88% yearly
    
    prices = [base_price]
    for i in range(1, num_days):
        daily_change = daily_growth + np.random.normal(0, 0.015)  
        new_price = prices[-1] * (1 + daily_change)
        prices.append(new_price)
    
    # Create realistic OHLCV data with technical indicators
    high_prices = [p * (1 + abs(np.random.normal(0, 0.008))) for p in prices]
    low_prices = [p * (1 - abs(np.random.normal(0, 0.008))) for p in prices]
    volumes = np.random.randint(2000000, 8000000, num_days)
    
    # Add ATH tracking
    ath_values = []
    current_ath = base_price
    for price in prices:
        if price > current_ath:
            current_ath = price
        ath_values.append(current_ath)
    
    # Calculate ATH distance
    ath_distances = [((ath - price) / ath) * 100 for price, ath in zip(prices, ath_values)]
    
    # Add technical indicators (simplified)
    rsi_values = np.random.normal(65, 8, num_days)  # Bull market RSI
    rsi_values = np.clip(rsi_values, 0, 100)
    
    df = pd.DataFrame({
        'Open': prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': prices,
        'Volume': volumes,
        'ATH': ath_values,
        'ATH_Distance_Pct': ath_distances,
        'Near_ATH': [d < 10 for d in ath_distances],
        'RSI': rsi_values
    }, index=dates)
    
    # Weekly data
    weekly_df = df.resample('W').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min', 
        'Close': 'last',
        'Volume': 'sum'
    })
    
    return df, weekly_df

def create_moderate_bull_scenario():
    """Create MODERATE_BULL scenario with 25% from ATH"""
    df, weekly_df = create_strong_bull_scenario()
    
    # Simulate correction - reduce prices by 25% from ATH
    correction_factor = 0.75
    final_ath = df['ATH'].max()
    corrected_price = final_ath * correction_factor
    
    # Adjust last 30 days to simulate correction
    df.loc[df.index[-30:], 'Close'] = corrected_price
    df.loc[df.index[-30:], 'ATH_Distance_Pct'] = 25.0
    
    return df, weekly_df

def test_enhanced_short_generator():
    """Test the enhanced short generator with different market regimes"""
    
    print("🧪 Testing Enhanced Smart Short Generator")
    print("=" * 50)
    
    # Configuration
    config = {
        'trend': {'trend_lookback_days': 30, 'trend_threshold': 0.015},
        'smart_short': {
            'min_ath_distance_pct': 5.0,
            'max_ath_distance_pct': 30.0,
            'min_confluence_score': 2,
            'min_risk_reward_ratio': 1.5,
            'max_stop_loss_pct': 5.0,
            'bull_market_block': True
        }
    }
    
    # Initialize generator
    generator = SmartShortSignalGenerator(config)
    
    # Test 1: STRONG_BULL market (should block SHORT signals)
    print("\n🔴 TEST 1: STRONG_BULL Market (88% gain, near ATH)")
    print("-" * 40)
    
    bull_df, bull_weekly = create_strong_bull_scenario()
    bull_signals = generator.generate_short_signals(bull_df, bull_weekly)
    
    print(f"STRONG_BULL signals generated: {len(bull_signals)}")
    print(f"Expected: 0 (should be blocked)")
    print(f"Final price: ${bull_df['Close'].iloc[-1]:.2f}")
    print(f"Total gain: {((bull_df['Close'].iloc[-1] / bull_df['Close'].iloc[0]) - 1) * 100:.1f}%")
    print(f"ATH distance: {bull_df['ATH_Distance_Pct'].iloc[-1]:.1f}%")
    
    # Test 2: MODERATE_BULL with correction (should allow some SHORT signals)  
    print("\n🟡 TEST 2: MODERATE_BULL Market (25% correction)")
    print("-" * 40)
    
    moderate_df, moderate_weekly = create_moderate_bull_scenario()
    moderate_signals = generator.generate_short_signals(moderate_df, moderate_weekly)
    
    print(f"MODERATE_BULL signals generated: {len(moderate_signals)}")
    print(f"Expected: >0 (should allow with 25% ATH distance)")
    print(f"ATH distance: {moderate_df['ATH_Distance_Pct'].iloc[-1]:.1f}%")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 30)
    
    # Test results validation
    strong_bull_blocked = len(bull_signals) == 0
    moderate_bull_allowed = len(moderate_signals) > 0
    
    if strong_bull_blocked:
        print("✅ STRONG_BULL blocking: SUCCESS")
    else:
        print(f"❌ STRONG_BULL blocking: FAILED ({len(bull_signals)} signals generated)")
        
    if moderate_bull_allowed:
        print("✅ MODERATE_BULL allowance: SUCCESS") 
    else:
        print("❌ MODERATE_BULL allowance: FAILED (0 signals generated)")
    
    # Overall result
    both_tests_passed = strong_bull_blocked and moderate_bull_allowed
    
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if both_tests_passed else '❌ FAILED'}")
    
    if both_tests_passed:
        print("🎉 Enhanced SHORT generator correctly blocks signals in STRONG_BULL!")
        print("💡 System now prevents SHORT losses in sustained bull markets")
    else:
        print("⚠️  Enhanced SHORT generator needs further adjustments")
    
    return both_tests_passed

if __name__ == "__main__":
    test_enhanced_short_generator()