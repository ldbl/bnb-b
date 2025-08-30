# 🚀 BNB Trading System v2.1.0

Advanced Technical Analysis System for BNB/USDT Trading with 22+ Specialized Analysis Modules

[![CI/CD Pipeline](https://github.com/ldbl/bnb-b/actions/workflows/ci.yml/badge.svg)](https://github.com/ldbl/bnb-b/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ldbl/bnb-b/branch/main/graph/badge.svg)](https://codecov.io/gh/ldbl/bnb-b)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📈 Current Performance

-   **Overall Accuracy**: 59.7% (37/62 signals) - Latest 18-month backtest
-   **LONG Accuracy**: 63.3% (49 signals) - Enhanced performance
-   **SHORT Accuracy**: 46.2% (13 signals) - Market regime filtering active
-   **Average P&L**: +2.21% per signal
-   **Backtest Period**: 540 days (2024-03-07 to 2025-08-29)

## 🏗️ Architecture

### Modern Project Structure

```
bnb-b/
├── src/bnb_trading/          # Main package source code
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Primary entry point
│   ├── signal_generator.py   # Core signal generation
│   ├── data_fetcher.py       # Binance API integration
│   ├── backtester.py         # Historical validation
│   └── ...                   # 22+ analysis modules
├── tests/                    # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py           # Shared test fixtures
│   ├── test_signal_generator.py
│   └── ...                   # Module-specific tests
├── data/                     # Analysis results and backtests
├── .github/workflows/        # CI/CD automation
├── config.toml               # System configuration
├── pyproject.toml            # Modern Python packaging
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
└── Makefile                  # Development commands
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ldbl/bnb-b.git
cd bnb-b

# Set up development environment
make dev-setup

# Or manual installation
pip install -r requirements-dev.txt
pip install -e .
```

### Basic Usage

```bash
# Generate current trading signal
make signal

# Run comprehensive analysis
make analyze

# Execute 18-month backtest
make backtest

# Run all tests
make test
```

### Python API

```python
from bnb_trading import SignalGenerator, BNBDataFetcher
import toml

# Load configuration
config = toml.load('config.toml')

# Initialize components
data_fetcher = BNBDataFetcher(config)
signal_gen = SignalGenerator(config)

# Fetch data and generate signals
daily_data, weekly_data = data_fetcher.get_current_data()
signal = signal_gen.generate_signal(daily_data, weekly_data)

print(f"Signal: {signal['signal']}")
print(f"Confidence: {signal['confidence']:.1%}")
print(f"Reasoning: {signal['reason']}")
```

## 🔧 Development

### Prerequisites

-   Python 3.13+
-   TA-Lib technical analysis library
-   Make (for development commands)

### Development Workflow

```bash
# Format code
make format

# Run linting
make lint

# Run tests with coverage
make test

# Run specific test categories
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-slow        # Tests requiring market data
```

### Pre-commit Hooks

Automatic code quality checks on every commit:

```bash
# Install hooks
make pre-commit

# Manual run
pre-commit run --all-files
```

## 📊 Core Modules

### 🎯 Signal Generation Engine

-   **SignalGenerator**: Orchestrates 22+ analysis modules with weighted scoring
-   **Multi-timeframe Analysis**: Daily and weekly data correlation
-   **Market Regime Intelligence**: STRONG_BULL detection and SHORT blocking

### 📈 Technical Analysis Modules

-   **Fibonacci Analysis** (35% weight): Support/resistance levels
-   **Weekly Tails Analysis** (40% weight): Wick pattern analysis
-   **Technical Indicators** (15% weight): RSI, MACD, Bollinger Bands
-   **Moving Averages** (10% weight): Trend confirmation
-   **Elliott Wave Analysis**: Wave structure and completion signals
-   **Divergence Detection**: Price-momentum divergence analysis
-   **Smart SHORT Generator**: Market regime-aware SHORT signals

### 🛡️ Risk Management

-   **Market Regime Detection**: Bull/Bear/Neutral classification
-   **ATH Proximity Filtering**: Prevents risky SHORT signals
-   **Volume Confirmation**: Enhanced signal validation
-   **Time-based Validation**: Realistic holding periods

## 🧪 Testing

### Test Categories

-   **Unit Tests**: Individual module testing
-   **Integration Tests**: Multi-module interaction testing
-   **Slow Tests**: Full market data validation
-   **API Tests**: External data source testing

### Running Tests

```bash
# All tests with coverage
pytest tests/ --cov=src/bnb_trading --cov-report=html

# Specific markers
pytest -m "unit"           # Unit tests only
pytest -m "integration"    # Integration tests only
pytest -m "slow"          # Market data tests
```

## 📈 Configuration

The system is fully configurable via `config.toml`:

```toml
[data]
symbol = "BNB/USDT"
lookback_days = 500
timeframes = ["1d", "1w"]

[signals]
fibonacci_weight = 0.35      # Primary analysis weight
weekly_tails_weight = 0.40   # Enhanced for LONG accuracy
confidence_threshold = 0.8   # Quality control

[smart_short]
enabled = true
bull_market_block = true     # Safety in bull markets
min_ath_distance_pct = 5.0   # Risk management
```

## 🔄 CI/CD Pipeline

Automated testing and quality checks:

-   **Python Testing**: 3.13
-   **Code Quality**: Black, isort, flake8, mypy
-   **Security Scanning**: Bandit security analysis
-   **Test Coverage**: Comprehensive coverage reporting
-   **Integration Testing**: Full system validation

## 📚 Documentation

-   **[CLAUDE.md](CLAUDE.md)**: Development guide and system overview
-   **[MODULES.md](MODULES.md)**: Detailed technical documentation
-   **[TODO.md](TODO.md)**: Development roadmap and priorities

## 🎯 Performance Targets

### Current vs Target Performance

| Metric            | Current | Target     | Status         |
| ----------------- | ------- | ---------- | -------------- |
| LONG Accuracy     | 63.3%   | 85%+       | 🚧 In Progress |
| SHORT Accuracy    | 46.2%   | 75%+       | 🚧 In Progress |
| Overall Accuracy  | 59.7%   | 80%+       | 🚧 In Progress |
| Risk/Reward Ratio | 1:2.1   | 1:4 (LONG) | 🚧 Improving   |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run quality checks: `make ci-test`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Standards

-   **Code Quality**: Black formatting, flake8 linting, mypy type checking
-   **Testing**: Minimum 80% test coverage required
-   **Documentation**: Comprehensive docstrings and examples
-   **Type Safety**: Full type hints for all public APIs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Cryptocurrency trading involves substantial risk of loss. Never trade with money you cannot afford to lose. Past performance does not guarantee future results.

## 🙏 Acknowledgments

-   **TA-Lib**: Technical Analysis Library
-   **CCXT**: Cryptocurrency Exchange Trading Library
-   **Pandas**: Data analysis and manipulation
-   **NumPy**: Numerical computing

---

_For detailed technical documentation, see [MODULES.md](MODULES.md)_
_For development guidance, see [CLAUDE.md](CLAUDE.md)_
