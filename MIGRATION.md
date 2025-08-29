# 🔄 Migration Guide - Project Restructuring

This guide explains the migration from flat structure to modern src/ layout.

## 📁 New Project Structure

```
OLD (Root level)          →    NEW (src/ layout)
=====================================
main.py                  →    src/bnb_trading/main.py
signal_generator.py      →    src/bnb_trading/signal_generator.py
data_fetcher.py          →    src/bnb_trading/data_fetcher.py
backtester.py            →    src/bnb_trading/backtester.py
*.py (all modules)       →    src/bnb_trading/*.py
(no tests)               →    tests/ (comprehensive suite)
```

## 🛠️ Migration Steps

### 1. Files Moved to src/bnb_trading/
- All Python modules (22+ files)
- Core analysis modules
- Entry points and utilities

### 2. New Development Infrastructure
- `tests/` - Comprehensive test suite
- `pyproject.toml` - Modern Python packaging
- `requirements-dev.txt` - Development dependencies
- `.pre-commit-config.yaml` - Code quality hooks
- `.editorconfig` - Consistent coding style
- `Makefile` - Development commands
- `.github/workflows/ci.yml` - CI/CD pipeline

### 3. Enhanced Configuration
- Updated imports in all modules
- Package-level `__init__.py`
- Entry point configuration
- Test fixtures and utilities

## 🚀 Usage Changes

### Old Usage
```bash
python main.py
python signal_generator.py
python backtester.py
```

### New Usage (Recommended)
```bash
make analyze      # python main.py
make signal       # signal generation
make backtest     # backtesting
make test         # comprehensive testing
```

### Python API
```python
# Old imports
from signal_generator import SignalGenerator

# New imports  
from bnb_trading import SignalGenerator
from bnb_trading.signal_generator import SignalGenerator
```

## 📦 Installation

### Development Setup
```bash
# Install development dependencies
make dev-setup

# Or manually
pip install -r requirements-dev.txt
pip install -e .
```

### Production
```bash
pip install -r requirements.txt
pip install -e .
```

## 🧪 Testing

### New Test Infrastructure
```bash
make test           # All tests with coverage
make test-unit      # Unit tests only
make test-integration  # Integration tests
make lint           # Code quality checks
make format         # Code formatting
```

### Test Categories
- **Unit tests**: Individual module testing
- **Integration tests**: Multi-module functionality
- **Slow tests**: Full market data validation
- **API tests**: External service integration

## 🔧 Development Workflow

### Code Quality (Automated)
```bash
# Install pre-commit hooks
make pre-commit

# Manual quality checks
make format     # black + isort
make lint       # flake8 + mypy
```

### CI/CD Pipeline
- Automated testing on push/PR
- Multi-Python version testing (3.8-3.11)
- Code coverage reporting
- Security scanning with Bandit

## 📋 Cleanup Actions

### Files Kept
- `config.toml` - System configuration
- `data/` - Analysis results and backtests  
- `README.md` - Updated documentation
- `CLAUDE.md` - Development guidance
- `MODULES.md` - Technical documentation
- `TODO.md` - Development roadmap

### Files to Consider Removing
- `README_old.md` - Superseded by new README
- `codex.md` - Old documentation
- Root-level `*.py` files - Moved to src/

### Recommended Cleanup
```bash
# Remove old files (after verification)
rm README_old.md codex.md
rm *.py  # Only if src/ versions are working

# Or move to archive
mkdir archive/
mv *.py README_old.md codex.md archive/
```

## ⚠️ Important Notes

1. **Backwards Compatibility**: Old imports will break
2. **Entry Points**: Use Makefile commands or module execution
3. **Testing**: New test infrastructure provides better coverage
4. **CI/CD**: Automated quality assurance now active

## 🎯 Benefits of New Structure

- **Professional**: Modern Python package layout
- **Testable**: Comprehensive test infrastructure
- **Maintainable**: Clear separation of concerns
- **Scalable**: Easy to add new modules and tests
- **Quality**: Automated code quality checks
- **CI/CD**: Professional development workflow

## 🤝 Next Steps

1. **Verify functionality**: Run `make test` and `make analyze`
2. **Update IDE settings**: Point to src/ for imports
3. **Clean up old files**: Remove or archive as needed  
4. **Update documentation**: Ensure all references are current
5. **Train team**: New development workflow and commands