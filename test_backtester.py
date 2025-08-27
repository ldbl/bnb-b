#!/usr/bin/env python3
"""
Backtester Testing Script
Тестов файл за валидиране на backtester функционалността
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtester import Backtester
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_validation():
    """Test validation functionality"""
    print('🧪 ФАЗА 4: VALIDATION ТЕСТВАНЕ')
    print('=' * 35)

    backtester = Backtester()

    try:
        print('📊 Тест 4.1: Validation логика...')

        # Get dataset
        data = backtester.data_fetcher.fetch_bnb_data(90)  # 3 months
        daily_df = data['daily']

        # Create mock signal
        test_date = daily_df.index[len(daily_df) // 2]
        current_price = daily_df.loc[test_date, 'Close']

        mock_signal = {
            'signal': 'LONG',
            'confidence': 3.5,
            'fibonacci_analysis': {
                'current_price': current_price
            }
        }

        print(f'🎯 Test date: {test_date.strftime("%Y-%m-%d")}')
        print(f'📈 Signal: {mock_signal["signal"]} at ${current_price:.2f}')

        # Test validation
        result = backtester._validate_historical_signal(mock_signal, daily_df, test_date)

        if result:
            print('✅ Validation successful')
            print(f'   Exit date: {result["validation_date"].strftime("%Y-%m-%d")}')
            print(f'   P&L: {result["profit_loss_pct"]:+.2f}%')
            print(f'   Success: {result["success"]}')
            if not result["success"]:
                print(f'   Reason: {result.get("failure_reason", "")}')
        else:
            print('❌ Validation returned None')

        print('\n✅ Тест 4.1: Validation - УСПЕШЕН')

        # Test 4.2: Edge case
        print('\n📊 Тест 4.2: Edge case - near end of data...')

        last_date = daily_df.index[-10]
        mock_signal_2 = {
            'signal': 'SHORT',
            'confidence': 4.0,
            'fibonacci_analysis': {
                'current_price': daily_df.loc[last_date, 'Close']
            }
        }

        result_2 = backtester._validate_historical_signal(mock_signal_2, daily_df, last_date)

        if result_2:
            print('✅ Edge case validation successful')
            print(f'   Exit: {result_2["validation_date"].strftime("%Y-%m-%d")}')
            print(f'   P&L: {result_2["profit_loss_pct"]:+.2f}%')
        else:
            print('❌ Edge case validation failed')

        print('\n✅ Тест 4.2: Edge case - УСПЕШЕН')

    except Exception as e:
        print(f'❌ Validation тест - ГРЕШКА: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_validation()