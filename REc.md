🎯 Post-Refactor Debug & Parity Implementation Plan

A) Diagnostic Plan (Root-cause Analysis)

Quick Checks Checklist

□ Config path resolution: ls -la config.toml && cat config.toml | grep threshold
□ Data validation: python -c "from bnb_trading.data.fetcher import BNBDataFetcher; f=BNBDataFetcher(); print(f.fetch_bnb_data(500)['daily'].shape)"
□ Timeframe sync: grep -r "timeframes" config.toml
□ NaN check: python -c "import pandas as pd; df=pd.read_csv('data/results.csv'); print(df.isnull().sum())"
□ Weights sum: grep -E "weight.\*=" config.toml | awk '{sum+=$3} END {print sum}'
□ Filter status: grep -E "enabled|required" config.toml

Debug Breakpoints

# Add to each stage:

logger.debug(f"[DATA] Candles: daily={len(daily_df)}, weekly={len(weekly_df)}")
logger.debug(f"[ANALYSIS] Modules: {list(analyses.keys())}, Non-HOLD: {sum(1 for a in analyses.values() if a.get('signal') != 'HOLD')}")
logger.debug(f"[SIGNALS] Confluence: long_score={long_score:.3f}, short_score={short_score:.3f}, threshold={threshold}")
logger.debug(f"[FILTERS] Applied: {filters_applied}, Passed: {filters_passed}")
logger.debug(f"[DECISION] Final: signal={signal}, confidence={confidence:.3f}, reasons={len(reasons)}")

Minimal Reproducible Case

# tests/fixtures/golden_day_2024_08_05.py

FIXTURE_DATE = "2024-08-05"
EXPECTED_SIGNAL = "LONG"
EXPECTED_CONFIDENCE = 0.375
FIXTURE_DATA = "tests/fixtures/bnb_2024_08_05.csv"

B) Unified Decision Logic

Module Structure

# src/bnb_trading/signals/decision.py

@dataclass
class DecisionContext:
daily_df: pd.DataFrame
weekly_df: pd.DataFrame
analyses: dict[str, Any]
config: dict[str, Any]

@dataclass
class DecisionResult:
signal: str # LONG/SHORT/HOLD
confidence: float
reasons: list[str]
metadata: dict[str, Any]

def decide_signal(context: DecisionContext) -> DecisionResult:
"""Single source of truth for signal decisions""" # 1. Combine signals # 2. Apply filters # 3. Validate # 4. Return decision

Migration Steps

□ Extract common logic from signal_generator.py → decision.py
□ Replace main.py: signal = decide_signal(context)
□ Replace backtester.py: signal = decide_signal(context)
□ Remove duplicate threshold checks
□ Consolidate filter application

Parity Tests

# tests/parity/test_live_vs_backtest.py

def test_identical_decisions():
context = load_fixture_context("2024-08-05")
live_result = run_live_decision(context)
backtest_result = run_backtest_decision(context)
assert live_result.signal == backtest_result.signal
assert abs(live_result.confidence - backtest_result.confidence) < 0.001

C) Main Output Improvements

Console Report Structure

═══════════════════════════════════════════════════════════
🚀 BNB TRADING SIGNAL | 2024-08-05 15:30:00 | BNB/USDT
═══════════════════════════════════════════════════════════
📊 DATA HEALTH
Daily: 500 candles | Last: $464.20 | Gap: 0
Weekly: 71 candles | Last: $458.30 | Gap: 0

🔬 ANALYSIS SNAPSHOT
RSI: 45.3 ↓ | MACD: -2.1 ↓ | BB: 0.35
Fibonacci: 38.2% | Tails: LONG | MA: Bearish

📈 CONFLUENCE MATRIX
┌─────────────┬────────┬──────┬────────┐
│ Module │ Signal │ Str │ Weight │
├─────────────┼────────┼──────┼────────┤
│ Fibonacci │ HOLD │ 0.20 │ 35% │
│ WeeklyTails │ LONG │ 0.99 │ 40% │
│ RSI │ HOLD │ 0.10 │ 8% │
└─────────────┴────────┴──────┴────────┘

✅ VALIDATION
Risk Filters: ✓ ATH Check ✓ Volume ✗ Regime
Confluence: 3/5 modules aligned

🎯 DECISION: LONG | Confidence: 0.445
Reason: Strong weekly tails with neutral market

⏱️ Pipeline: 1.23s | Analysis: 0.89s | Decision: 0.02s
═══════════════════════════════════════════════════════════

CLI Flags

python main.py --verbose # Full debug output
python main.py --dry-run # No trades, just signals
python main.py --save-artifacts /tmp # Save intermediate JSON
python main.py --date 2024-08-05 # Historical date
python main.py --symbol BNB/USDT # Override symbol

D) PR Plan

PR #1: Diagnostic Infrastructure

Files: signals/debug.py, utils/logger.py
□ Add structured logging with levels
□ Add guard clauses for empty data
□ Fix config path resolution
□ Add NaN/None detection
Commands: pytest tests/diagnostics && ruff check

PR #2: Unified Decision Module

Files: signals/decision.py, tests/parity/\*
□ Extract decide_signal() function
□ Migrate main.py to use it
□ Migrate backtester.py to use it
□ Add parity tests
Commands: pytest tests/parity -v && mypy src/bnb_trading/signals/decision.py

PR #3: Main UX Enhancement

Files: main.py, utils/display.py, utils/cli.py
□ Implement structured output
□ Add CLI argument parser
□ Add artifact saving
□ Add performance metrics
Commands: python main.py --dry-run --verbose

PR #4: Bug Fixes

Files: [as discovered]
□ Fix specific analysis bugs
□ Fix filter logic issues
□ Add regression tests
□ Update thresholds
Commands: pytest tests/regression && python backtester.py

PR #5: Cleanup & Documentation

Files: README.md, CLAUDE.md, TODO.md
□ Update documentation
□ Remove debug code
□ Final type hints
□ Performance optimization
Commands: mypy src/ && ruff format src/

E) Test Package

Golden Fixtures

# tests/fixtures/golden_days.py

FIXTURES = {
"bull": {"date": "2024-08-05", "expected": "LONG", "confidence": 0.375},
"bear": {"date": "2024-06-15", "expected": "SHORT", "confidence": 0.425},
"chop": {"date": "2024-07-01", "expected": "HOLD", "confidence": 0.150},
}

Test Structure

tests/
├── fixtures/
│ ├── golden_days.py
│ └── data/\*.csv
├── parity/
│ └── test_live_vs_backtest.py
├── integration/
│ └── test_full_pipeline.py
└── regression/
└── test_known_issues.py

F) TODO.md Update

# TODO.md

## 🔴 NOW (This Week)

-   [ ] Fix signal generation after refactor (no LONG/SHORT)
-   [ ] Add diagnostic logging to find root cause
-   [ ] Implement unified decision module
-   [ ] Fix confidence threshold mismatch

## 🟡 NEXT (Next Sprint)

-   [ ] Enhance main.py output with tables
-   [ ] Add CLI flags for debugging
-   [ ] Create parity test suite
-   [ ] Document signal flow

## 🟢 LATER (Backlog)

-   [ ] Performance optimization
-   [ ] ML-based confidence tuning
-   [ ] Multi-asset support
-   [ ] Real-time WebSocket feed

## ⚠️ Known Issues

-   Signal generation broken post-refactor
-   Confidence calculations inconsistent
-   Weekly data sometimes missing
-   ATH filter too aggressive

## ✅ Acceptance Criteria

-   [ ] Generates LONG/SHORT signals (not just HOLD)
-   [ ] Live matches backtest results
-   [ ] All tests green
-   [ ] Performance < 2s per signal

Execution Commands Summary

# Quick diagnosis

python -c "from bnb_trading.pipeline.orchestrator import TradingPipeline; p=TradingPipeline(); print(p.run_analysis())"

# Test parity

pytest tests/parity/test_live_vs_backtest.py::test_identical_decisions -v

# Run with debug

python main.py --verbose --save-artifacts /tmp --date 2024-08-05

# Full test suite

pytest tests/ && ruff check src/ && mypy src/
