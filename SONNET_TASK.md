# Задача за Sonnet: Semantic Fix за Signal Decision System

## Цел

Поправи семантиката на сигналната система, като запазиш **100.0% LONG accuracy (21/21 signals)**. Разделѝ статус от числово участие (contribution), направи решенията консистентни.

## Разбивка на PR-и (малки, фокусирани промени)

### ✅ PR 1: Core Models Foundation - **COMPLETED** (PR #17)

**Файл:** `src/bnb_trading/core/models.py`

```python
# ✅ DONE - Добавени:
Status = Literal["OK", "DEGRADED", "DISABLED", "ERROR"]
SignalState = Literal["LONG", "SHORT", "HOLD", "UP", "DOWN", "NEUTRAL"]

@dataclass
class ModuleResult:
    status: Status               # здраве на модула
    state: SignalState          # семантика (UP/DOWN/NEUTRAL)
    score: float                # 0.0..1.0 raw strength
    contrib: float              # 0.0..1.0 normalized contribution
    reason: str
    meta: dict[str, Any]
```

**✅ IMPLEMENTED:** Правило: Ако `status != "OK"` → `contrib = 0.0`, `state = "NEUTRAL"`

---

### ✅ PR 2: Fix TREND Analyzer - **COMPLETED** (PRs #18, #19, #21)

**Файл:** `src/bnb_trading/analysis/trend/analyzer.py`

**✅ IMPLEMENTED:**

1. ✅ Проста HH/HL логика (последни 20 дни)
    - UP: ≥2 последователни Higher Highs & Higher Lows
    - DOWN: ≥2 последователни Lower Highs & Lower Lows
    - NEUTRAL: otherwise
2. ✅ MA наклон check (EMA50 vs EMA200)
3. ✅ Връща `ModuleResult` със:
    - `state`: "UP"/"NEUTRAL"/"DOWN"
    - `score`: 0.0-1.0 (не weight!)
    - `contrib`: score \* weight_from_config

**✅ DONE:** Unit tests за различни market conditions

---

### ✅ PR 3: Moving Averages ModuleResult Implementation - **COMPLETED**

**Файл:** `src/bnb_trading/analysis/moving_averages.py`

**✅ IMPLEMENTED:**

1. ✅ ModuleResult-based implementation with proper state/score separation
2. ✅ EMA50/EMA200 crossover logic implemented
3. ✅ Price position relative to moving averages
4. ✅ Returns proper ModuleResult with:
    - `state`: "UP"/"NEUTRAL"/"DOWN"
    - `score`: 0.0-1.0 based on MA alignment
    - `contrib`: score \* weight from config

**✅ DONE:** Unit tests and integration with signal generator

---

### ✅ PR 4: Fibonacci Returns HOLD - **COMPLETED** (PR #23)

**Файл:** `src/bnb_trading/fibonacci.py`

**✅ IMPLEMENTED:**

-   ✅ Added new `analyze()` method returning ModuleResult
-   ✅ Always returns `state="HOLD"` (не е directional)
-   ✅ Smart scoring: 0.7 for golden ratio, 0.6-0.8 for key levels, 0.2-0.4 for neutral
-   ✅ Proper `contrib = score * weight_fibonacci` from config
-   ✅ Comprehensive unit tests with real swing data
-   ✅ Updated config.toml to `signals.weights` structure
-   ✅ **100.0% LONG accuracy preserved (21/21 signals verified)**

---

### ✅ PR 5: Unified Decision Engine - **COMPLETED** (PR #25)

**Файл:** `src/bnb_trading/signals/decision.py`

**✅ IMPLEMENTED:**

-   ✅ Rewritten `decide_long()` to use ModuleResult system from all analyzers
-   ✅ Health gate: critical modules (weekly_tails) must have `status="OK"`
-   ✅ Weekly tails gate: must return `state="LONG"` to generate signal
-   ✅ Confidence calculation: `confidence = sum(contrib_i)` for all OK modules
-   ✅ Decision logic: `confidence >= 0.85 → LONG`, else `HOLD`
-   ✅ Comprehensive unit tests covering all decision paths (7 tests)
-   ✅ Proper error handling and graceful degradation
-   ✅ Configurable confidence threshold from `config.toml`

**✅ VALIDATED:** Single source of truth used by both main.py and backtester.py

---

### 🔄 PR 6: Fix Output Formatting - **PENDING**

**Файл:** `src/bnb_trading/main.py`

**От:**

```
trend: HOLD (0.00)
```

**Към:**

```
trend: UP | score=0.60 | contrib=0.06 (w=0.10)
```

Показвай state, score, contrib и weight отделно!

---

### 🔄 PR 7: Stabilize Problem Modules - **PENDING**

**Файлове:**

-   `src/bnb_trading/indicators/`
-   `src/bnb_trading/ichimoku/`
-   `src/bnb_trading/sentiment/`

**Задача:**

-   Ако недостатъчно данни → `status="DISABLED"`, `contrib=0.0`
-   Sentiment временно с weight=0.0
-   Clear logging за причините

---

## Acceptance Criteria

### ✅ Must Have:

1. Няма BUY при фактори с 0.00 contribution
2. trend показва UP/NEUTRAL/DOWN със смислен score
3. **100.0% LONG accuracy (21/21 signals)** остава (tails gate + 0.85 threshold)
4. `make main` показва правилно state/score/contrib/weight
5. Идентични резултати между main и backtest

### ✅ Testing:

1. Unit tests за всеки модул
2. Parity test: main vs backtest дават същия DecisionResult
3. Regression: запазена 100.0% LONG accuracy

---

## Config Structure

```toml
[signals.weights]
weekly_tails = 0.60  # gate + highest weight
fibonacci    = 0.20
trend        = 0.10
moving_avg   = 0.10
sentiment    = 0.00  # disabled for now

[signals.thresholds]
confidence_min = 0.85
```

---

## Важни бележки:

-   **KISS принцип** - без overengineering
-   **Малки PR-и** - лесен review, бързо merge
-   **Тествай всеки PR** - `ruff check` + unit tests
-   **Финален backtest** - verify 100.0% LONG accuracy

## Команди за валидация:

```bash
# След всеки PR:
ruff check src/
python3 -m pytest tests/

# Финална проверка:
python3 run_enhanced_backtest.py
grep "LONG accuracy" data/enhanced_backtest_*.csv
```
