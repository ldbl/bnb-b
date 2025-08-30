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

try:
    from .data.fetcher import BNBDataFetcher
except ImportError:
    # BNBDataFetcher will be imported on demand to avoid CI import issues
    BNBDataFetcher = None

try:
    from .divergence_detector import DivergenceDetector
except ImportError:
    DivergenceDetector = None

try:
    from .elliott_wave_analyzer import ElliottWaveAnalyzer
except ImportError:
    ElliottWaveAnalyzer = None

# Analysis modules
try:
    from .fibonacci import FibonacciAnalyzer
except ImportError:
    FibonacciAnalyzer = None

try:
    from .indicators import TechnicalIndicators
except ImportError:
    TechnicalIndicators = None

# Pipeline architecture
try:
    from .pipeline.orchestrator import TradingPipeline
except ImportError:
    TradingPipeline = None

try:
    from .pipeline.runners import PipelineRunner
except ImportError:
    PipelineRunner = None

# Signal generation - using new modular structure
try:
    from .signals.generator import SignalGenerator
except ImportError:
    SignalGenerator = None

try:
    from .signals.smart_short.generator import SmartShortSignalGenerator
except ImportError:
    SmartShortSignalGenerator = None

try:
    from .trend_analyzer import TrendAnalyzer
except ImportError:
    TrendAnalyzer = None

try:
    from .weekly_tails import WeeklyTailsAnalyzer
except ImportError:
    WeeklyTailsAnalyzer = None

# Build __all__ list dynamically based on successful imports
__all__ = []

# Add modules to __all__ if successfully imported
if BNBDataFetcher is not None:
    __all__.append("BNBDataFetcher")
if Backtester is not None:
    __all__.append("Backtester")
if DivergenceDetector is not None:
    __all__.append("DivergenceDetector")
if ElliottWaveAnalyzer is not None:
    __all__.append("ElliottWaveAnalyzer")
if FibonacciAnalyzer is not None:
    __all__.append("FibonacciAnalyzer")
if PipelineRunner is not None:
    __all__.append("PipelineRunner")
if SignalGenerator is not None:
    __all__.append("SignalGenerator")
if SmartShortSignalGenerator is not None:
    __all__.append("SmartShortSignalGenerator")
if TechnicalIndicators is not None:
    __all__.append("TechnicalIndicators")
if TradingPipeline is not None:
    __all__.append("TradingPipeline")
if TrendAnalyzer is not None:
    __all__.append("TrendAnalyzer")
if WeeklyTailsAnalyzer is not None:
    __all__.append("WeeklyTailsAnalyzer")
