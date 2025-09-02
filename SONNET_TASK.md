# 🎯 SONNET AI ASSISTANT - Active Task Management

## Mission Statement

Continue developing the BNB trading system while maintaining **PERFECT 21/21 LONG accuracy**. Focus on quality, modularity, and regression safety.

## Current Active Task (2025-09-03)

### 🔥 PRIORITY 1: CI/CD Pipeline Issues

**Status**: PARTIALLY RESOLVED ⚠️
**Started**: 2025-09-02
**Completed**: 2025-09-03
**Assigned**: Claude Code AI Assistant

#### What Was Accomplished:

1. ✅ **CRITICAL FIX**: Added missing `src/bnb_trading/data/` package to git

    - Root cause: Directory was excluded by .gitignore
    - Solution: Added exception for code directory in .gitignore
    - Impact: CI can now find all required modules

2. ✅ **Fixed regression test**:

    - Changed from `make backtest` to `run_enhanced_backtest.py`
    - Added timeout configuration via BNB_TEST_TIMEOUT_SECONDS
    - Enhanced error diagnostics with head+tail output
    - Combined STDOUT+STDERR parsing for robustness

3. ✅ **Added CI debugging**:

    - Installed tree command for structure visualization
    - Added pre/post backtest debugging sections
    - Enhanced file structure analysis

4. ⚠️ **Binance API Geo-blocking Issue**:
    - Discovered: GitHub Actions IPs are blocked by Binance
    - Attempted: Cached data solution (reverted - needs more work)
    - Current: Temporarily disabled Binance-dependent tests in CI

### 🔥 PRIORITY 2: Fix Import System Issues

**Status**: COMPLETED ✅
**Started**: 2025-09-01
**Completed**: 2025-09-02
**Assigned**: Claude Code AI Assistant

#### What Was Accomplished:

1. ✅ **Removed TID252 ignore** from pyproject.toml
2. ✅ **Fixed ALL 62 relative imports** to absolute imports
3. ✅ **Fixed all critical signal imports**
4. ✅ **Fixed all test imports** - 43/43 tests now passing
5. ✅ **Verified 21/21 signals maintained** throughout

#### ALL Import Issues RESOLVED:

```bash
# ✅ ALL 62 import violations fixed across:
- pipeline/orchestrator.py ✅
- pipeline/runners.py ✅
- testing/historical/tester.py ✅
- validation/protocols/*.py ✅
- signals/smart_short/*.py ✅
- utils/telemetry.py ✅
- And 30+ other files ✅
```

#### Safety Checks After Each Change:

```bash
# MANDATORY - Run after every import fix
python3 tests/test_golden_regression.py
# Must show: ✅ 21/21 signals maintained

# Optional - Check for new import issues
ruff check src/ --select TID252
```

## Next Tasks (Priority Order)

### PRIORITY 1: Resolve Binance API Geo-blocking in CI

-   **Current Issue**: GitHub Actions IPs blocked by Binance
-   Implement proper cached/mock data solution
-   Consider alternative CI providers (self-hosted runners)
-   Add fallback mechanisms for API failures

### PRIORITY 2: Create Comprehensive Test Suite

-   Add formula protection tests
-   Add configuration integrity tests
-   Add module interface tests
-   Target: 90%+ test coverage

### PRIORITY 3: Document Sacred Formulas

-   Document weekly_tails formula (UNTOUCHABLE)
-   Document fibonacci calculations
-   Document all working thresholds and parameters
-   Create "DO NOT CHANGE" documentation

## Blocked Tasks

**None currently** - All dependencies resolved

## Recently Completed ✅

### 2025-09-03

-   ✅ **CRITICAL**: Added missing `src/bnb_trading/data/` package to git
-   ✅ Fixed regression test to use proper backtest script
-   ✅ Enhanced CI debugging with tree command
-   ✅ Identified and documented Binance API geo-blocking issue
-   ⚠️ Temporarily disabled Binance-dependent CI tests

### 2025-09-02

-   ✅ Fixed ALL 62 relative import violations
-   ✅ Fixed all test imports (43/43 tests passing)
-   ✅ Completed Phase 1.1 of import system standardization

### 2025-09-01

-   ✅ Enhanced CLAUDE.md with MASTER_PLAN.md rules
-   ✅ Fixed CI regression (Ubuntu import issues)
-   ✅ Created hardway/ backup directory
-   ✅ Created TODO.md and SONNET_TASK.md files
-   ✅ Started systematic import fixes

### Previous Sessions

-   ✅ Achieved 21/21 LONG accuracy (100% success rate)
-   ✅ Fixed all linting errors (0 violations)
-   ✅ Implemented modular architecture
-   ✅ Created regression protection tests

## Quality Gates & Requirements

### Before Making ANY Code Changes:

1. **Read CLAUDE.md** - Understand sacred elements and rules
2. **Check current branch** - Never work directly on main
3. **Verify 21/21 baseline** - Run regression test first
4. **Create backup** - Save working state before changes

### After Making Code Changes:

1. **Run regression test** - `python3 tests/test_golden_regression.py`
2. **Check import violations** - `ruff check src/ --select TID252`
3. **Verify all tests pass** - Fix any broken test imports
4. **Run linting** - `ruff check && ruff format`

### Before Committing:

1. **All import issues resolved** - Zero TID252 violations
2. **All tests passing** - No import errors in test suite
3. **21/21 signals verified** - Regression test passes
4. **Clean working tree** - No untracked changes

## Communication Protocols

### When Task is Completed:

1. **Update this file** - Mark task as completed
2. **Update TODO.md** - Move to next phase
3. **Run full validation** - Complete test suite
4. **Create summary** - What was accomplished

### When Issues Arise:

1. **Document the issue** - What went wrong
2. **Revert if needed** - Restore working state
3. **Analyze root cause** - Why did it happen
4. **Update prevention** - How to avoid in future

### When Switching Context:

1. **Save current state** - Document progress
2. **Note any blockers** - Dependencies or issues
3. **Update priority** - Reassess task importance
4. **Clean handoff** - Clear next steps

## System Health Status

### Core System: ✅ HEALTHY

-   21/21 LONG signals maintained
-   100% accuracy preserved
-   Zero regression detected
-   All critical paths functional

### Development Environment: ⚠️ NEEDS ATTENTION

-   Import system needs standardization
-   Some tests failing to import
-   CI/CD hooks need adjustment
-   Documentation needs updates

### Code Quality: 🔄 IN PROGRESS

-   Linting: Clean (0 errors)
-   Type hints: Partial coverage
-   Tests: Limited coverage
-   Documentation: Being updated

---

**Last Updated**: 2025-09-03 02:30 UTC
**Current Focus**: Resolving CI/CD Binance API geo-blocking issue
**Next Session Goal**: Create comprehensive test suite (Phase 1.2)
**Emergency Contact**: Run `python3 tests/test_golden_regression.py` if anything breaks
