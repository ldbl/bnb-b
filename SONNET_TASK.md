# SONNET_TASK.md - Testing Strategy Plan Needed

## ✅ SEMANTIC FIXES COMPLETED (PRs 1-5)

**100.0% LONG accuracy preserved (21/21 signals) ✅**

-   ✅ PR 1: Core Models Foundation (ModuleResult system)
-   ✅ PR 2: TREND Analyzer with HH/HL logic
-   ✅ PR 3: Moving Averages ModuleResult implementation
-   ✅ PR 4: Fibonacci returns HOLD (non-directional)
-   ✅ PR 5: Unified Decision Engine with configurable critical_modules

**All 9 decision tests pass, mypy clean, ruff clean ✅**

---

## 🎯 ARCHITECT TASK: Design Testing Strategy

@code-architect - Based on ideas.md recommendations, we need a detailed testing strategy plan:

### Current Testing State:

-   Unit tests coverage: <5% (needs improvement)
-   Only decision.py has comprehensive tests (9 tests)
-   No integration tests for full pipeline
-   No regression tests for 100% LONG accuracy validation
-   No performance benchmarks

### 🔑 KEY QUESTIONS for @code-architect:

#### 1. **Test Structure** - how to organize test files

-   Should we mirror src/bnb_trading structure in tests/?
-   Naming conventions for test files and test methods?
-   Where to place fixtures and test data?
-   How to organize shared utilities?

#### 2. **Coverage Strategy** - which modules are priority for tests

-   Target coverage percentage for each module type?
-   Which modules are highest priority for unit tests?
-   Integration test strategy for signal pipeline?
-   How to test complex interactions between modules?

#### 3. **Data Strategy** - real data or synthetic test data

-   Use real historical market data or synthetic test data?
-   How to handle API dependencies in tests (mock vs real)?
-   Test data versioning and management strategy?
-   How to ensure test reproducibility?

#### 4. **Regression Testing** - how to automatically validate 21/21 LONG signals

-   Automated way to validate 21/21 LONG signals preserved?
-   Performance regression tests for analysis speed?
-   How to test across different market conditions?
-   CI/CD integration for regression validation?

#### 5. **Testing Architecture** - base classes, fixtures, utilities

-   Test base classes and common utilities structure?
-   Parameterized tests for different configurations?
-   Testing strategy for the refactored architecture from ideas.md?
-   Mock strategies for external dependencies?

### 📋 DELIVERABLE NEEDED:

**Please provide specific detailed plan for implementing Phase 2 from ideas.md:**

> "Phase 2 (Essential - Week 2): Testing Infrastructure
>
> 1. Comprehensive unit and integration test suite
> 2. Regression testing for signal accuracy
> 3. Performance benchmarking"

### 🎯 EXPECTED OUTPUT:

Detailed plan with:

1. **File structure** - exact directories and naming patterns
2. **Priority matrix** - which tests to implement first
3. **Data management** - fixtures, test data, mocking strategy
4. **Regression pipeline** - automated validation process
5. **Architecture patterns** - base classes, utilities, helpers

---

## 📋 IMPLEMENTATION SEQUENCE AFTER TESTING PLAN:

1. **Phase 1:** Implement comprehensive testing (based on architect plan)
2. **Phase 2:** Execute ideas.md architecture refactor
3. **Phase 3:** Fix output formatting and stabilize remaining modules

**All changes must preserve 100.0% LONG accuracy (21/21 signals) ✅**
