# 🎯 MASTER PLAN: BNB Trading System Development

## Overview

This is the **single source of truth** for developing the BNB trading system while preserving the perfect **21/21 LONG accuracy** that took months to achieve.

**Golden Rule**: Any change that breaks 21/21 signals is wrong by definition.

## 📊 Current Status

-   **System**: 21/21 LONG signals, 100% accuracy ✅
-   **Average P&L**: 19.68% per signal
-   **Zero losing trades**: Perfect risk management
-   **Data source**: `data/enhanced_backtest_2025-08-30.csv`
-   **Working commit**: 50d5636

## 🔒 SACRED ELEMENTS (NEVER CHANGE)

### Core Formula (Working)

```python
# Weekly Tails Calculation - UNTOUCHABLE
tail_strength = tail_ratio * body_factor * vol_factor

# Where:
tail_ratio = lower_wick / max(atr_w, epsilon)
body_control = min(body_size / max(atr_w, epsilon), 1.0)
body_factor = 1.0 - 0.5 * body_control  # Range: 0.5 to 1.0
volume_ratio = np.clip(volume / max(vol_sma, epsilon), 0.5, 2.0)
vol_factor = volume_ratio
```

### Sacred Thresholds

```toml
[weekly_tails]
min_tail_ratio = 0.3        # DO NOT CHANGE
min_tail_strength = 0.35    # DO NOT CHANGE
min_close_pos = 0.2         # DO NOT CHANGE
max_body_atr = 2.0          # DO NOT CHANGE
```

### Sacred Config Structure

```toml
[signals]
weekly_tails_weight = 0.60  # Primary signal generator
fibonacci_weight = 0.20     # Secondary confirmation
trend_weight = 0.10         # Trend alignment
volume_weight = 0.10        # Additional confirmation
confidence_threshold = 0.25 # DO NOT CHANGE
```

### 4-Gate Validation (Proven)

```python
def validate_long_signal(candle_data):
    # Gate 1: Tail vs volatility
    if tail_ratio < 0.3: return False

    # Gate 2: Combined strength
    if tail_strength < 0.35: return False

    # Gate 3: Body size control
    if body_atr_ratio > 2.0: return False

    # Gate 4: Close position
    if close_pos < 0.2: return False

    return True  # All gates passed
```

## ✅ ALLOWED IMPROVEMENTS

### Safe Changes

-   **File organization**: Move files, rename classes
-   **Error handling**: Add try/catch, validation
-   **Logging**: Better debug output
-   **Documentation**: Comments, docstrings
-   **Test coverage**: More comprehensive tests
-   **Performance**: Optimize code (same mathematical results)
-   **Interfaces**: Add new APIs that wrap existing logic

### Improvement Examples

```python
# ✅ ALLOWED: Wrapper interface
class WeeklyTailsAnalyzer:
    def _calculate_original_formula(self, df):
        """ORIGINAL WORKING FORMULA - NEVER CHANGE"""
        # Exact calculation from commit 50d5636
        return tail_strength

    def calculate_tail_strength(self, df):
        """Public interface - delegates to protected original"""
        return self._calculate_original_formula(df)

    def analyze(self, daily_df, weekly_df):
        """NEW: ModuleResult interface wrapper"""
        result = self.calculate_tail_strength(weekly_df)
        return ModuleResult(...)  # Wrap in new format
```

## 🚨 REGRESSION PROTECTION

### Automated Testing

Every commit/PR must pass:

```bash
# Core regression test
python3 tests/test_golden_regression.py
# Must output: ✅ 21/21 signals maintained

# Full backtest verification
python3 run_enhanced_backtest.py
# Must show: LONG Signals: 21, Accuracy: 100.0%
```

### Pre-commit Hooks

Automatically runs on every commit:

-   Code formatting (ruff)
-   Type checking (mypy)
-   21/21 regression test ⭐
-   Documentation health check

### CI/CD Pipeline

GitHub Actions runs on every PR:

-   All pre-commit checks
-   Security scanning
-   **21/21 signal verification** ⭐
-   Test suite

## 🔄 DEVELOPMENT WORKFLOW

### 1. Starting New Work

```bash
# Always start from working main
git checkout main
python3 run_enhanced_backtest.py  # Verify 21/21
git checkout -b feature/your-improvement
```

### 2. Making Changes

```bash
# Make your changes
python3 tests/test_golden_regression.py  # Must pass
git add -A
git commit -m "Description"  # Pre-commit runs automatically
```

### 3. Creating PR

```bash
git push -u origin feature/your-improvement
gh pr create --title "Description" --body "
## Regression Test Results
\`\`\`
$(python3 run_enhanced_backtest.py | grep -E 'LONG Signals|Accuracy')
\`\`\`
✅ 21/21 signals maintained
"
```

### 4. PR Requirements

Every PR must include:

-   Screenshot of backtest results
-   Confirmation: "21/21 signals maintained ✅"
-   All CI checks passing
-   Code review approval

## 📁 PROJECT STRUCTURE

### Essential Files Only

```
/
├── MASTER_PLAN.md          # This guide
├── CLAUDE.md               # AI development instructions
├── README.md               # Public documentation
├── MODULES.md              # Technical API reference
├── config.toml             # Sacred configuration
├── src/bnb_trading/        # Source code
├── tests/                  # Test suite
├── data/                   # Results and datasets
└── docs/archive/           # Old documentation
```

### Key Components

-   **`src/bnb_trading/weekly_tails.py`**: Contains working formula
-   **`src/bnb_trading/signals/decision.py`**: Signal generation logic
-   **`config.toml`**: Sacred thresholds and weights
-   **`data/enhanced_backtest_2025-08-30.csv`**: Golden 21/21 dataset
-   **`tests/test_golden_regression.py`**: Core protection test

## 🎯 DEVELOPMENT PHASES

### Phase 1: Foundation (COMPLETED ✅)

-   [x] 21/21 LONG accuracy achieved
-   [x] Perfect system preserved and documented
-   [x] Regression protection implemented
-   [x] Clean documentation structure

### Phase 2: Safe Improvements (NEXT)

-   [ ] Add ModuleResult wrapper interfaces
-   [ ] Improve error handling and logging
-   [ ] Add comprehensive test coverage
-   [ ] Implement feature flags for experiments

### Phase 3: Architecture Enhancement (FUTURE)

-   [ ] Modular signal generators
-   [ ] Plugin architecture
-   [ ] Real-time monitoring
-   [ ] SHORT signal development (75%+ target)

### Phase 4: Production (FUTURE)

-   [ ] Live trading interface
-   [ ] Risk management system
-   [ ] Portfolio optimization
-   [ ] Performance monitoring

## 🚨 EMERGENCY PROCEDURES

### If Regression Detected

```bash
# 1. Immediate rollback
git reset --hard HEAD~1

# 2. Investigate
git diff HEAD~1 HEAD -- src/bnb_trading/
git diff HEAD~1 HEAD -- config.toml

# 3. Fix and verify
python3 tests/test_golden_regression.py  # Must pass
git commit -m "Fix regression"
```

### If System Completely Broken

```bash
# Return to last known working state
git checkout 50d5636  # Known working commit
python3 run_enhanced_backtest.py  # Should show 21/21

# Create recovery branch from working state
git checkout -b recovery/restore-working-system
```

## 📈 SUCCESS METRICS

### Must Maintain (Non-negotiable)

-   ✅ 21/21 LONG signals
-   ✅ 100% accuracy
-   ✅ ~20% average P&L
-   ✅ Zero losing trades

### Can Improve

-   Code quality and maintainability
-   Test coverage and reliability
-   Development velocity
-   Documentation clarity
-   Error handling robustness

## 🏆 CORE PRINCIPLES

1. **Preserve Perfection**: The 21/21 system is mathematically perfect for our dataset
2. **Improve Gradually**: Add features without breaking existing functionality
3. **Test Everything**: Every change must pass regression tests
4. **Document Changes**: Clear commit messages and PR descriptions
5. **Review Carefully**: Two-person review for any core logic changes

## 🚀 QUICK REFERENCE

### Daily Commands

```bash
# Verify system health
python3 run_enhanced_backtest.py | grep -E "LONG Signals|Accuracy"

# Run regression test
python3 tests/test_golden_regression.py

# Run full test suite
pytest tests/ -v
```

### Sacred Files

-   `src/bnb_trading/weekly_tails.py` (formula)
-   `src/bnb_trading/signals/decision.py` (logic)
-   `config.toml` (thresholds)
-   `data/enhanced_backtest_2025-08-30.csv` (golden dataset)

Remember: **Any change that breaks 21/21 accuracy is wrong, not the system.**
