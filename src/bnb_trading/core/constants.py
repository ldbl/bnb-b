"""Constants for BNB Trading System."""

# Signal Types
SIGNAL_LONG = "LONG"
SIGNAL_SHORT = "SHORT"
SIGNAL_HOLD = "HOLD"

# Market Regimes
REGIME_STRONG_BULL = "STRONG_BULL"
REGIME_MODERATE_BULL = "MODERATE_BULL"
REGIME_WEAK_BULL = "WEAK_BULL"
REGIME_NEUTRAL = "NEUTRAL"
REGIME_BEAR = "BEAR"

# Timeframes
TIMEFRAME_1D = "1d"
TIMEFRAME_1W = "1w"
TIMEFRAMES = [TIMEFRAME_1D, TIMEFRAME_1W]

# Fibonacci Levels
FIBONACCI_RETRACEMENT_LEVELS: list[float] = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
FIBONACCI_EXTENSION_LEVELS: list[float] = [1.0, 1.272, 1.414, 1.618, 2.0, 2.618]

# Fibonacci Signal Strengths
FIB_STRONG_LONG_STRENGTH = 0.8  # 38.2% level
FIB_MEDIUM_LONG_STRENGTH = 0.6  # Other levels
FIB_STRONG_SHORT_STRENGTH = 0.8  # 61.8% level
FIB_MEDIUM_SHORT_STRENGTH = 0.7  # Other levels
FIB_HOLD_STRENGTH = 0.3
FIB_WEAK_STRENGTH = 0.2

# Technical Indicator Thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Volume Thresholds
VOLUME_SPIKE_THRESHOLD = 1.5  # 1.5x average volume

# Weekly Tail Thresholds
STRONG_TAIL_SIZE = 0.05  # 5% of candle body

# Market Regime Thresholds
BULL_MARKET_THRESHOLD_12M = 0.50  # 50% gain over 12 months
MODERATE_BULL_CORRECTION_REQ = 0.15  # 15% correction required
WEAK_BULL_CORRECTION_REQ = 0.08  # 8% correction required

# ATH Distance Thresholds
ATH_PROXIMITY_MIN = 0.05  # 5% from ATH
ATH_PROXIMITY_MAX = 0.25  # 25% from ATH

# Risk Management
DEFAULT_STOP_LOSS_PCT = 0.08  # 8% stop loss
MIN_RISK_REWARD_RATIO = 1.5  # Minimum 1.5:1 risk/reward

# File Paths
RESULTS_CSV_PATH = "data/results.csv"
BACKTEST_RESULTS_PATH = "data/backtest_results.txt"
ANALYSIS_RESULTS_PATH = "data/analysis_results.txt"
LOG_FILE_PATH = "bnb_trading.log"

# Analysis Module Names
MODULE_FIBONACCI = "fibonacci"
MODULE_WEEKLY_TAILS = "weekly_tails"
MODULE_MOVING_AVERAGES = "moving_averages"
MODULE_RSI = "rsi"
MODULE_MACD = "macd"
MODULE_BOLLINGER = "bollinger"
MODULE_TREND = "trend"
MODULE_DIVERGENCE = "divergence"
MODULE_ELLIOTT_WAVE = "elliott_wave"
MODULE_ICHIMOKU = "ichimoku"
MODULE_WHALE = "whale"
MODULE_SENTIMENT = "sentiment"
MODULE_PRICE_ACTION = "price_action"
MODULE_OPTIMAL_LEVELS = "optimal_levels"
