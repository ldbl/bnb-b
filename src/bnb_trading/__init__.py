"""
BNB Trading System - Advanced Technical Analysis for Cryptocurrency Trading

A comprehensive trading system combining 22+ specialized analysis modules
with weighted scoring to generate high-confidence trading signals.

Current Performance:
- Overall Accuracy: 59.7% (37/62 signals)
- LONG Accuracy: 63.3% (49 signals)
- SHORT Accuracy: 46.2% (13 signals)

Author: BNB Trading System Team
Version: 2.1.0
"""

__version__ = "2.1.0"
__author__ = "BNB Trading System Team"

# Core modules
from .signal_generator import SignalGenerator
from .data_fetcher import BNBDataFetcher
from .backtester import Backtester

# Analysis modules
from .fibonacci import FibonacciAnalyzer
from .weekly_tails import WeeklyTailsAnalyzer
from .indicators import TechnicalIndicators
from .trend_analyzer import TrendAnalyzer
from .elliott_wave_analyzer import ElliottWaveAnalyzer
from .divergence_detector import DivergenceDetector
from .smart_short_generator import SmartShortSignalGenerator

__all__ = [
    'SignalGenerator',
    'BNBDataFetcher', 
    'Backtester',
    'FibonacciAnalyzer',
    'WeeklyTailsAnalyzer',
    'TechnicalIndicators',
    'TrendAnalyzer',
    'ElliottWaveAnalyzer',
    'DivergenceDetector',
    'SmartShortSignalGenerator'
]