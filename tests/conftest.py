"""
Pytest configuration and shared fixtures for BNB Trading System tests.

This file provides common test fixtures and configuration that can be used
across all test modules in the suite.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def test_config():
    """Standard test configuration for all modules."""
    return {
        'data': {
            'symbol': 'BNB/USDT',
            'lookback_days': 500,
            'timeframes': ['1d', '1w']
        },
        'signals': {
            'fibonacci_weight': 0.35,
            'weekly_tails_weight': 0.40,
            'ma_weight': 0.10,
            'rsi_weight': 0.08,
            'macd_weight': 0.07,
            'bb_weight': 0.00,
            'min_confirmations': 1,
            'confidence_threshold': 0.8
        },
        'indicators': {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2.0,
            'atr_period': 14
        },
        'fibonacci': {
            'lookback_days': 90,
            'min_swing_strength': 0.02,
            'proximity_threshold': 0.01
        },
        'weekly_tails': {
            'min_tail_ratio': 0.3,
            'volume_confirmation': True,
            'confluence_bonus': 0.15
        },
        'smart_short': {
            'enabled': True,
            'min_ath_distance_pct': 5.0,
            'max_ath_distance_pct': 25.0,
            'bull_market_block': True,
            'min_confluence_score': 3,
            'min_risk_reward_ratio': 1.5
        },
        'elliott_wave': {
            'lookback_periods': 50,
            'min_wave_strength': 0.02,
            'trend_momentum_filter': True,
            'momentum_threshold': 0.7
        },
        'divergence': {
            'min_peak_distance': 5,
            'min_peak_prominence': 0.02,
            'lookback_periods': 20,
            'trend_filter_enabled': True,
            'bull_market_threshold': 0.1,
            'bear_market_threshold': -0.05
        }
    }


@pytest.fixture(scope="function")
def sample_ohlcv_data():
    """Generate sample OHLCV data for testing."""
    np.random.seed(42)  # For reproducible tests
    
    # Create 200 days of sample data
    dates = pd.date_range(start='2024-01-01', periods=200, freq='D')
    
    # Generate realistic price data with trend
    base_price = 500
    trend = np.linspace(0, 100, 200)  # Upward trend
    noise = np.random.normal(0, 20, 200)  # Price volatility
    
    prices = base_price + trend + noise
    
    data = {
        'Open': prices * (1 + np.random.uniform(-0.02, 0.02, 200)),
        'High': prices * (1 + np.random.uniform(0.01, 0.05, 200)),
        'Low': prices * (1 + np.random.uniform(-0.05, -0.01, 200)),
        'Close': prices,
        'Volume': np.random.uniform(1000000, 10000000, 200)
    }
    
    df = pd.DataFrame(data, index=dates)
    
    # Ensure High >= Open, Close and Low <= Open, Close
    df['High'] = df[['Open', 'Close', 'High']].max(axis=1)
    df['Low'] = df[['Open', 'Close', 'Low']].min(axis=1)
    
    return df


@pytest.fixture(scope="function") 
def sample_weekly_data(sample_ohlcv_data):
    """Convert daily data to weekly format."""
    weekly = sample_ohlcv_data.resample('W').agg({
        'Open': 'first',
        'High': 'max', 
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    return weekly


@pytest.fixture(scope="function")
def bull_market_data():
    """Generate sample data representing a bull market."""
    np.random.seed(123)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    # Strong upward trend
    base_prices = np.linspace(400, 800, 100)  # 100% gain
    noise = np.random.normal(0, 10, 100)
    prices = base_prices + noise
    
    data = {
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, 100)),
        'High': prices * (1 + np.random.uniform(0.005, 0.03, 100)),
        'Low': prices * (1 + np.random.uniform(-0.03, -0.005, 100)),
        'Close': prices,
        'Volume': np.random.uniform(2000000, 8000000, 100)
    }
    
    df = pd.DataFrame(data, index=dates)
    df['High'] = df[['Open', 'Close', 'High']].max(axis=1)
    df['Low'] = df[['Open', 'Close', 'Low']].min(axis=1)
    
    return df


@pytest.fixture(scope="function")
def bear_market_data():
    """Generate sample data representing a bear market."""
    np.random.seed(456)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    # Strong downward trend
    base_prices = np.linspace(600, 300, 100)  # 50% decline
    noise = np.random.normal(0, 15, 100)
    prices = base_prices + noise
    
    data = {
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, 100)),
        'High': prices * (1 + np.random.uniform(0.005, 0.02, 100)),
        'Low': prices * (1 + np.random.uniform(-0.04, -0.005, 100)),
        'Close': prices,
        'Volume': np.random.uniform(1500000, 6000000, 100)
    }
    
    df = pd.DataFrame(data, index=dates)
    df['High'] = df[['Open', 'Close', 'High']].max(axis=1)
    df['Low'] = df[['Open', 'Close', 'Low']].min(axis=1)
    
    return df


@pytest.fixture
def mock_config_file(tmp_path, test_config):
    """Create a temporary config.toml file for testing."""
    import toml
    
    config_file = tmp_path / "test_config.toml"
    config_file.write_text(toml.dumps(test_config))
    
    return str(config_file)


# Pytest markers for different test types
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests requiring market data")
    config.addinivalue_line("markers", "api: Tests requiring API access")