# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular BNB/USDT swing trading system that uses advanced technical analysis to generate high-confidence trading signals. The system combines 22+ specialized analysis modules with weighted scoring to achieve current performance of 59.7% overall accuracy, with 63.3% LONG accuracy and 46.2% SHORT accuracy over an 18-month backtest period.

### Key Architecture Principles

-   **Modular design**: Each indicator/analysis in separate Python files
-   **Configuration-driven**: All parameters managed in `config.toml`
-   **Real-time data**: Live Binance API integration via CCXT
-   **Comprehensive validation**: Historical backtesting with 14-day holding periods

## Essential Commands

### Development & Testing

```bash
# Run main trading analysis (primary entry point)
python3 main.py

# Generate current trading signal
python3 signal_generator.py

# Run comprehensive backtesting (18-month validation)
python3 backtester.py

# Run specific module tests
python3 test_enhanced_short_generator.py
python3 test_trend_analyzer.py

# Install dependencies
pip install -r requirements.txt
```

### Performance & Validation Commands

```bash
# View latest backtest results
cat data/backtest_results.txt

# Check current system performance
tail -20 data/backtest_results.txt

# Monitor system logs
tail -f bnb_trading.log
```

### Configuration & Data Analysis

```bash
# View analysis summary and results
cat data/results_summary.txt
cat data/analysis_results.txt

# Check historical signal database
head -10 data/results.csv

# Validate configuration syntax
python3 -c "import toml; print('Config valid:'), toml.load('config.toml')"
```

### Configuration Management

```bash
# View current configuration
cat config.toml

# Check key configuration sections
grep -A 5 "\[signals\]" config.toml
grep -A 5 "\[smart_short\]" config.toml
grep -A 5 "\[long_signals\]" config.toml
```

## Core System Architecture

### Primary Entry Points

-   **`main.py`**: Complete trading system orchestrator and primary entry point
-   **`signal_generator.py`**: Central signal generation engine combining all analysis modules
-   **`backtester.py`**: Historical validation engine with 18-month backtesting capability

### Data Layer

-   **`data_fetcher.py`**: Binance API integration with CCXT, handles multiple timeframes (1d, 1w)
-   **`config.toml`**: Single source of truth for all system parameters and weights

### Core Analysis Modules (22+ specialized analyzers)

**Primary Signal Generators**:

-   **`fibonacci.py`**: Fibonacci retracement/extension analysis (35% weight)
-   **`weekly_tails.py`**: Weekly wick/tail pattern analysis (40% weight - enhanced)
-   **`smart_short_generator.py`**: Specialized SHORT signal generation with market regime filtering

**Supporting Analysis**:

-   **`trend_analyzer.py`**: Multi-timeframe trend detection with 90-180 day analysis
-   **`multi_timeframe_analyzer.py`**: Cross-timeframe signal confirmation (current error: status key validation)
-   **`moving_averages.py`**: MA crossover analysis (10% weight - reduced)
-   **`indicators.py`**: RSI/MACD/Bollinger Bands via TA-Lib (combined 15% weight)

**Advanced Components**: `divergence_detector.py`, `elliott_wave_analyzer.py`, `ichimoku_module.py`, `whale_tracker.py`, `sentiment_module.py`, `price_action_patterns.py`, `optimal_levels.py`

> **📚 For detailed module documentation, API reference, and technical specifications, see `MODULES.md`**

### Validation & Testing

-   **`validator.py`**: Signal validation and performance tracking
-   **`validation_protocol.py`**: Validation rules and metrics
-   **`historical_tester.py`**: Historical performance analysis

## Signal Generation Logic

### Signal Hierarchy & Weights (from config.toml - Updated)

1. **Fibonacci Analysis**: 35% weight - Primary support/resistance signals
2. **Weekly Tails Analysis**: 40% weight - Enhanced for LONG signal accuracy
3. **Moving Averages**: 10% weight - Crossover confirmation (reduced)
4. **Technical Indicators**: 15% weight total - RSI (8%), MACD (7%), BB (0% - filter only)
5. **Smart SHORT Generator**: Market regime intelligent filtering

### Signal Types

-   **LONG**: Buy signals (**Target: 85%+ accuracy, 1:4 risk/reward**)
-   **SHORT**: Sell signals (**Target: 75%+ accuracy, 1:3 risk/reward**)
-   **HOLD**: Insufficient confidence signals (below target thresholds)

### Market Regime Intelligence

The system includes sophisticated market regime detection:

-   **STRONG_BULL**: Blocks SHORT signals when 12-month returns > 50%
-   **MODERATE_BULL**: Strict SHORT filtering with 15% correction requirements
-   **NEUTRAL/BEAR**: Full SHORT signal capability enabled

## Configuration Management

### Core Configuration Sections

```toml
[data]
symbol = "BNB/USDT"
lookback_days = 500
timeframes = ["1d", "1w"]

[signals]
fibonacci_weight = 0.35      # Primary support/resistance
weekly_tails_weight = 0.40   # Enhanced for LONG accuracy
ma_weight = 0.10             # Moving averages (reduced)
rsi_weight = 0.08            # RSI (reduced)
macd_weight = 0.07           # MACD (reduced)
bb_weight = 0.00             # Bollinger Bands (filter only)
min_confirmations = 1        # Reduced requirements
confidence_threshold = 0.8   # Increased for quality

[smart_short]
enabled = true
min_ath_distance_pct = 5.0
bull_market_block = true

[long_signals]
ema_confirmation = true
volume_confirmation_enabled = true
confidence_threshold_high = 5.0
```

### Key Parameter Categories

-   **Signal weights**: Control influence of each analysis module
-   **Market regime filters**: Prevent inappropriate signals in bull/bear markets
-   **Risk management**: Stop-loss percentages, position sizing rules
-   **Technical thresholds**: RSI levels, MACD periods, Fibonacci proximity

## Development Guidelines

### Code Standards (from .cursor/rules/agent.mdc)

-   **Python 3.8+** with comprehensive type hints
-   **Pandas/NumPy** for data manipulation, **CCXT** for API integration
-   **TA-Lib** for technical indicators
-   Handle NaN values with `np.nan_to_num()`
-   Comprehensive logging for all operations
-   Try/catch blocks for API calls
-   Save results to CSV for analysis tracking

### Critical Development Rules

-   **Never hardcode test data** - always use real Binance API data
-   **All parameters in config.toml** - no hardcoded values in Python files
-   **main.py is the only entry point** for production usage
-   **Comprehensive error handling** required for all modules
-   **Type hints mandatory** for all function signatures
-   **Handle NaN values** with `np.nan_to_num()` - avoid data quality issues
-   **Log all operations** - comprehensive logging for debugging and analysis
-   **Save results to CSV** - track all signals and performance data

### Testing Philosophy

-   **Real data only**: No mock or simulated data for validation
-   **18-month backtesting**: Full historical validation required
-   **Walk-forward testing**: Chronological signal generation
-   **14-day holding periods**: Realistic trade duration for validation
-   **Post-enhancement testing**: Always run 18-month backtest after each enhancement and save results with enhancement description to track regression

## Performance Targets & Current Status

### Current Performance Status ✅ (Updated 2025-08-29)

-   **Overall Accuracy**: 59.7% (37/62 signals) - Latest 18-month backtest (+4.4% improvement)
-   **LONG Accuracy**: 63.3% (49 signals) - Improved bull market performance
-   **SHORT Accuracy**: 46.2% (13 signals) - Enhanced filtering reducing false signals
-   **Average P&L**: +2.21% per signal (improved from +0.93%)
-   **Market Regime Detection**: STRONG_BULL recognition working (Phase 1 complete)
-   **Backtest Period**: 2024-03-07 to 2025-08-29 (540 days, 77 weeks)
-   **Long Tail Reversal Pattern**: Documented in TODO.md:81-100 for implementation

### Development Priorities

1. **LONG Signal Enhancement**: **CRITICAL** - Improve from 63.3% to **85%+ target accuracy**
2. **SHORT Signal Quality**: **CRITICAL** - Improve from 46.2% to **75%+ target accuracy**
3. ✅ **Divergence Detection Enhanced**: **COMPLETED** - Added trend-strength filter to prevent false signals in bull markets
4. ✅ **Weekly Tails Enhancement**: **COMPLETED** - Added trend-based weighting (1.5x LONG/0.3x SHORT in bull markets)
5. ✅ **Elliott Wave Enhancement**: **COMPLETED** - Added trend momentum filter to prevent false Wave 5 completion signals in bull markets
6. ✅ **Multi-timeframe Error Fix**: **COMPLETED** - Fixed status key validation error in multi_timeframe_analyzer.py
7. **Bull Market Filter**: Potential new module for sustained bull run detection
8. **Time-based Exit Strategy**: Implement realistic correction targets (10-20%)

> **⚠️ Performance Gap Alert**: Current accuracy is significantly below target requirements
>
> -   LONG: 63.3% vs 85%+ target (21.7 percentage point gap)
> -   SHORT: 46.2% vs 75%+ target (29 percentage point gap)

## Trading Signal Success Philosophy

### LONG Signals Success Criteria

-   **Target Accuracy: 85%+** - Minimum acceptable accuracy (risk/reward 1:4)
-   **Profit Factor > 2.0** - High efficiency requirement
-   **Max Drawdown < 10%** - Controlled risk exposure
-   **Trend alignment**: Follow bull market momentum
-   **Volume confirmation**: Enhanced filtering for quality entries

### SHORT Signals Success Criteria

-   **Target Accuracy: 75%+** - Minimum acceptable accuracy (risk/reward 1:3)
-   **Profit Factor > 1.0** - Gross profit exceeds gross loss
-   **Max Drawdown < 10%** - Controlled volatility exposure
-   **Market regime awareness**: Only trade SHORT in appropriate conditions
-   **Quality over quantity**: Better 1 winning SHORT than 100 losing ones

## Important Files & Locations

### Documentation

-   **`MODULES.md`**: 📚 **Complete technical documentation** - Detailed API reference, module specifications, and usage examples
-   **`README.md`**: Comprehensive system overview in Bulgarian
-   **`TODO.md`**: Current development priorities and analysis results
-   **`.cursor/rules/agent.mdc`**: 🎯 **Project rules and trading philosophy** - Core principles, success criteria, and quality standards

> **⚠️ Documentation Maintenance**: Both `CLAUDE.md` and `MODULES.md` must be kept synchronized
>
> -   **CLAUDE.md**: Update when system architecture, performance, or development priorities change
> -   **MODULES.md**: Update when adding/modifying modules, API changes, or technical specifications change
> -   **Cross-references**: Ensure both files reference each other and maintain consistent information

## 📍 Code References & Key Function Locations

### Core Signal Generation

-   **Main confidence scoring**: `signal_generator.py:234` - \_calculate_confidence()
-   **Signal combination logic**: `signal_generator.py:189` - \_combine_signals()
-   **LONG signal validation**: `signal_generator.py:156` - \_validate_signal()

### Analysis Modules (High Priority for LONG Enhancement)

-   **Fibonacci confluence detection**: `fibonacci.py:156` - find_price_proximity()
-   **Fibonacci retracement calculation**: `fibonacci.py:89` - calculate_fib_levels()
-   **Weekly tails strength calculation**: `weekly_tails.py:123` - calculate_tail_strength()
-   **Long Tail Reversal Pattern**: `weekly_tails.py:67` - classify_tail_pattern()
-   **Multi-timeframe alignment**: `multi_timeframe_analyzer.py:145` - analyze_multi_timeframe_alignment()

### Market Intelligence & Filtering

-   **Market regime detection**: `smart_short_generator.py:89` - \_analyze_market_regime()
-   **Bull market filtering**: `smart_short_generator.py:234` - \_validate_short_confluence()
-   **Trend analysis**: `trend_analyzer.py:78` - analyze_trend()
-   **Volume confirmation**: `indicators.py:123` - get_volume_signals()

### Configuration & Parameters

-   **Signal weights configuration**: `config.toml:133-141` - [signals] section
-   **LONG signal parameters**: `config.toml:148-151` - [long_signals] section
-   **Market regime thresholds**: `config.toml:143-146` - [smart_short] section

### Testing & Validation

-   **Backtesting engine**: `backtester.py:67` - \_execute_backtest()
-   **Signal validation**: `validator.py:45` - validate_signal()
-   **Performance metrics**: `backtester.py:234` - calculate_performance_metrics()

### Data & Error Handling Patterns

-   **Error handling for weekly_tails**: weekly_tails.py:ERROR "Error applying trend weighting: 'strength'"
-   **Error handling for divergence**: divergence_detector.py:ERROR "'str' object has no attribute 'get'"
-   **Data fetcher NaN handling**: `data_fetcher.py:123` - validate_data_quality()

### Data & Results

-   **`data/backtest_results.txt`**: 18-month performance analysis
-   **`data/analysis_results.txt`**: Complete analysis reports
-   **`data/results.csv`**: Historical signal database
-   **`bnb_trading.log`**: System operation logs

### Dependencies

-   **`requirements.txt`**: Python package dependencies
-   Key packages: pandas, numpy, ccxt, ta-lib, toml, matplotlib, seaborn, scipy

## Market Context & Risk Management

### Market Context (18-month Analysis Period)

-   **Bull Market Period**: 2024-03-07 to 2025-08-29 (540 days)
-   **Price Appreciation**: Sustained bull run with 87%+ gains
-   **SHORT Challenge**: Resistance levels became support in persistent uptrend
-   **Key Insight**: Market regime intelligence more important than signal generation
-   **System Evolution**: Enhanced STRONG_BULL detection (Phase 1) completed
-   **Performance**: Average +7.40% per winning signal, -7.06% per losing signal

### System Safeguards

-   **ATH Proximity Filtering**: Prevent inappropriate SHORT signals near all-time highs
-   **Volume Divergence Detection**: Multiple confirmation requirements
-   **Time-based Exit Strategy**: Realistic holding period validation
-   **Market Regime Blocking**: Automatic SHORT disabling in strong bull markets

## System Status Summary

This system represents a sophisticated trading system with:

-   **18-month backtesting validation** (540 days of market data)
-   **22+ specialized analysis modules** with weighted scoring
-   **Market regime intelligence** preventing inappropriate SHORT signals in bull markets
-   **Current accuracy**: 59.7% overall (63.3% LONG, 46.2% SHORT)
-   **Active development**: Multi-timeframe error fix and LONG signal enhancement priority
-   **Production-ready**: Comprehensive error handling and real-time Binance API integration

**Next Development Phase**: **Critical accuracy improvement required**

-   **LONG signals**: From 63.3% to 85%+ (minimum 1:4 risk/reward ratio)
-   **SHORT signals**: From 46.2% to 75%+ (minimum 1:3 risk/reward ratio)
-   **Focus**: Enhanced filtering, confluence requirements, and signal quality over quantity
-   Винаги обновявай @MODULES.md и @CLAUDE.md ако е необходимо. Винаги тествай с 18 след имплементация на нова функционалност . Сремим се към над 85% точнос на сигналите.
-   запомни го след промени всички необходими файлове се обновяват @TODO.md @MODULES.md @CLAUDE.md . Пуска се тест с 18 месечни данни и резултата се записва.
