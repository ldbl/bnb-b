"""
Test suite for SignalGenerator module

Tests the core signal generation logic including:
- Signal combination and weighting
- Confidence calculations
- Market regime handling
- Integration between analysis modules
"""

import os
import sys
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bnb_trading.signal_generator import SignalGenerator


class TestSignalGenerator:
    """Test cases for SignalGenerator class."""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "signals": {
                "fibonacci_weight": 0.35,
                "weekly_tails_weight": 0.40,
                "ma_weight": 0.10,
                "rsi_weight": 0.08,
                "macd_weight": 0.07,
                "bb_weight": 0.00,
                "confidence_threshold": 0.8,
            },
            "indicators": {
                "rsi_period": 14,
                "rsi_overbought": 70,
                "rsi_oversold": 30,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "bb_period": 20,
                "bb_std": 2.0,
                "atr_period": 14,
            },
        }

    @pytest.fixture
    def sample_data(self):
        """Sample OHLCV data for testing."""
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        data = {
            "Open": np.random.uniform(500, 600, 100),
            "High": np.random.uniform(550, 650, 100),
            "Low": np.random.uniform(450, 550, 100),
            "Close": np.random.uniform(500, 600, 100),
            "Volume": np.random.uniform(1000000, 5000000, 100),
        }
        return pd.DataFrame(data, index=dates)

    def test_signal_generator_initialization(self, sample_config):
        """Test SignalGenerator initialization."""
        generator = SignalGenerator(sample_config)

        assert generator.config == sample_config
        assert generator.fibonacci_weight == 0.35
        assert generator.weekly_tails_weight == 0.40
        assert generator.confidence_threshold == 0.8

    def test_generate_signal_with_valid_data(self, sample_config, sample_data):
        """Test signal generation with valid data."""
        generator = SignalGenerator(sample_config)
        daily_df = sample_data
        weekly_df = sample_data.resample("W").agg(
            {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
        )

        # Mock analysis modules to return predictable results
        with patch.multiple(
            generator,
            fibonacci_analyzer=Mock(),
            weekly_tails_analyzer=Mock(),
            indicators=Mock(),
            trend_analyzer=Mock(),
        ):

            generator.fibonacci_analyzer.analyze_fibonacci_trend.return_value = {
                "signal": "LONG",
                "confidence": 0.8,
                "reason": "Test fibonacci signal",
            }

            generator.weekly_tails_analyzer.analyze_weekly_tails.return_value = {
                "signal": "LONG",
                "confidence": 0.9,
                "reason": "Test weekly tails signal",
            }

            generator.indicators.get_all_indicators_signals.return_value = {
                "rsi": {"signal": "LONG", "strength": 0.7},
                "macd": {"signal": "LONG", "strength": 0.8},
                "bollinger": {"signal": "HOLD", "strength": 0.5},
            }

            result = generator.generate_signal(daily_df, weekly_df)

            assert "signal" in result
            assert "confidence" in result
            assert "reason" in result
            assert result["signal"] in ["LONG", "SHORT", "HOLD"]

    def test_signal_combination_logic(self, sample_config):
        """Test signal combination and weighting logic."""
        SignalGenerator(sample_config)

        analyses = {
            "fibonacci": {"signal": "LONG", "confidence": 0.8},
            "weekly_tails": {"signal": "LONG", "confidence": 0.9},
            "indicators": {
                "rsi": {"signal": "LONG", "strength": 0.7},
                "macd": {"signal": "SHORT", "strength": 0.6},
            },
        }

        # Test internal signal combination method
        # Note: This would require making _combine_signals public or using property access
        # For now, we test through the main generate_signal method

    def test_confidence_calculation(self, sample_config):
        """Test confidence score calculation."""
        SignalGenerator(sample_config)

        # Test high confidence scenario
        high_conf_analyses = {
            "fibonacci": {"signal": "LONG", "confidence": 0.9},
            "weekly_tails": {"signal": "LONG", "confidence": 0.85},
            "indicators": {
                "rsi": {"signal": "LONG", "strength": 0.8},
                "macd": {"signal": "LONG", "strength": 0.7},
            },
        }

        # Low confidence scenario
        low_conf_analyses = {
            "fibonacci": {"signal": "LONG", "confidence": 0.5},
            "weekly_tails": {"signal": "SHORT", "confidence": 0.4},
            "indicators": {
                "rsi": {"signal": "HOLD", "strength": 0.3},
                "macd": {"signal": "HOLD", "strength": 0.2},
            },
        }

        # These would need access to internal methods or integration testing

    @pytest.mark.integration
    def test_full_analysis_pipeline(self, sample_config, sample_data):
        """Integration test for full analysis pipeline."""
        SignalGenerator(sample_config)

        # Test with real analysis modules (requires more setup)
        # This is marked as integration test and can be run separately

    def test_error_handling(self, sample_config):
        """Test error handling with invalid data."""
        generator = SignalGenerator(sample_config)

        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        result = generator.generate_signal(empty_df, empty_df)

        assert "error" in result

        # Test with invalid config
        invalid_config = {}
        with pytest.raises((KeyError, ValueError)):
            SignalGenerator(invalid_config)
