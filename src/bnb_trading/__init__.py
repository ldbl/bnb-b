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

# Core modules - using new modular structure
try:
    from .backtester import Backtester
except ImportError:
    # Backtester will be imported on demand to avoid circular import issues
    Backtester = None

from .data.fetcher import BNBDataFetcher
from .divergence_detector import DivergenceDetector
from .elliott_wave_analyzer import ElliottWaveAnalyzer

# Analysis modules
from .fibonacci import FibonacciAnalyzer
from .indicators import TechnicalIndicators

# Pipeline architecture
from .pipeline.orchestrator import TradingPipeline
from .pipeline.runners import PipelineRunner

# Signal generation - using new modular structure
from .signals.generator import SignalGenerator
from .signals.smart_short.generator import SmartShortSignalGenerator
from .trend_analyzer import TrendAnalyzer
from .weekly_tails import WeeklyTailsAnalyzer

__all__ = [
    "BNBDataFetcher",
    "DivergenceDetector",
    "ElliottWaveAnalyzer",
    "FibonacciAnalyzer",
    "PipelineRunner",
    "SignalGenerator",
    "SmartShortSignalGenerator",
    "TechnicalIndicators",
    "TradingPipeline",
    "TrendAnalyzer",
    "WeeklyTailsAnalyzer",
]

# Add Backtester to __all__ if successfully imported
if Backtester is not None:
    __all__.append("Backtester")
