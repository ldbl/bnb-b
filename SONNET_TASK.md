# 🎯 SONNET AI ASSISTANT - Active Task Management

## Mission Statement

Continue developing the BNB trading system while maintaining **PERFECT 21/21 LONG accuracy**. Focus on quality, modularity, and regression safety.

## Current Active Task (2025-09-01)

### 🔥 PRIORITY 1: Fix Import System Issues

**Status**: IN PROGRESS ⚠️
**Started**: 2025-09-01
**Assigned**: Claude Code AI Assistant

#### What's Being Done Right Now:

1. ✅ **Removed TID252 ignore** from pyproject.toml
2. ✅ **Fixed critical signal imports**:
    - `src/bnb_trading/signals/decision.py` ✅
    - `src/bnb_trading/signals/generator.py` ✅
    - `src/bnb_trading/signals/confidence.py` ✅
    - `src/bnb_trading/signals/combiners.py` ✅
3. ✅ **Verified 21/21 signals maintained** after each change
4. 🔄 **Converting remaining 58 relative imports** to absolute imports

#### Remaining Work:

-   [ ] Fix pipeline/orchestrator.py imports (9 violations)
-   [ ] Fix pipeline/runners.py imports
-   [ ] Fix smart_short module imports (4 files)
-   [ ] Fix testing/historical module imports
-   [ ] Fix validation/protocols module imports
-   [ ] Fix utils/telemetry.py imports

#### Files with Import Issues:

```bash
# High Priority (core system files)
src/bnb_trading/pipeline/orchestrator.py (9 violations)
src/bnb_trading/pipeline/runners.py (3 violations)

# Medium Priority (testing & validation)
src/bnb_trading/testing/historical/tester.py (6 violations)
src/bnb_trading/validation/protocols/*.py (4 violations)

# Low Priority (experimental features)
src/bnb_trading/signals/smart_short/*.py (4 violations)
src/bnb_trading/utils/telemetry.py (1 violation)
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

### PRIORITY 2: Fix Failing Tests

-   **5 test files currently failing** to import
-   Fix import paths in test files
-   Ensure all tests pass with new import structure
-   Add missing test dependencies

### PRIORITY 3: Create Comprehensive Test Suite

-   Add formula protection tests
-   Add configuration integrity tests
-   Add module interface tests
-   Target: 90%+ test coverage

### PRIORITY 4: Document Sacred Formulas

-   Document weekly_tails formula (UNTOUCHABLE)
-   Document fibonacci calculations
-   Document all working thresholds and parameters
-   Create "DO NOT CHANGE" documentation

## Blocked Tasks

**None currently** - All dependencies resolved

## Recently Completed ✅

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

**Last Updated**: 2025-09-01 22:55 UTC
**Current Focus**: Import system standardization (TID252 violations)
**Next Session Goal**: Complete all import fixes, verify all tests pass
**Emergency Contact**: Run `python3 tests/test_golden_regression.py` if anything breaks
