# Задача за Sonnet: Semantic Fix за Signal Decision System

## Цел

Поправи семантиката на сигналната система, като запазиш 100% LONG accuracy. Разделѝ статус от числово участие (contribution), направи решенията консистентни.

## Разбивка на PR-и (малки, фокусирани промени)

### PR 1: Core Models Foundation

**Файл:** `src/bnb_trading/core/models.py`

```python
# Добави:
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

**Правило:** Ако `status != "OK"` → `contrib = 0.0`, `state = "NEUTRAL"`

---

### PR 2: Fix TREND Analyzer

**Файл:** `src/bnb_trading/analysis/trend/analyzer.py`

**Задача:**

1. Имплементирай проста HH/HL логика (последни 20 дни)
    - UP: ≥2 последователни Higher Highs & Higher Lows
    - DOWN: ≥2 последователни Lower Highs & Lower Lows
    - NEUTRAL: otherwise
2. MA наклон check (EMA50 vs EMA200)
3. Върни `ModuleResult` със:
    - `state`: "UP"/"NEUTRAL"/"DOWN"
    - `score`: 0.0-1.0 (не weight!)
    - `contrib`: score \* weight_from_config

**Тестове:** Unit test за различни market conditions

---

### PR 3: Fix Moving Averages

**Файл:** `src/bnb_trading/analysis/moving_averages.py`

**Задача:**

```python
# Проста логика:
if ema50 > ema200 and price > ema50:
    score = 0.7
    state = "UP"
elif ema50 > ema200 and price <= ema50:
    score = 0.5
    state = "NEUTRAL"
else:
    score = 0.0
    state = "DOWN"

return ModuleResult(
    status="OK",
    state=state,
    score=score,
    contrib=score * weight_ma,
    ...
)
```

---

### PR 4: Fibonacci Returns HOLD

**Файл:** `src/bnb_trading/analysis/fibonacci/`

**Задача:**

-   Fibonacci винаги връща `state="HOLD"` (не е directional)
-   `score`: 0.6-0.8 ако в top-3 retracement zones
-   `score`: 0.7 ако близо до 0.618 golden ratio
-   `score`: 0.2-0.4 за neutral zones
-   `contrib`: score \* weight_fib

---

### PR 5: Unified Decision Engine

**Файл:** `src/bnb_trading/signals/decision.py`

**Задача:**

```python
def decide_long(ctx: DecisionContext) -> DecisionResult:
    """Single source of truth for LONG decisions"""

    # 1. Health gate - critical modules must be OK
    # 2. Collect ModuleResults from all analyzers
    # 3. Weekly tails gate - if tails_pass=False → HOLD
    # 4. confidence = sum(contrib_i) for all OK modules
    # 5. if confidence >= 0.85 → LONG else HOLD
    # 6. Return detailed breakdown
```

**Важно:** Идентична функция се вика от main.py и backtester.py

---

### PR 6: Fix Output Formatting

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

### PR 7: Stabilize Problem Modules

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
3. 100% LONG accuracy остава (tails gate + 0.85 threshold)
4. `make main` показва правилно state/score/contrib/weight
5. Идентични резултати между main и backtest

### ✅ Testing:

1. Unit tests за всеки модул
2. Parity test: main vs backtest дават същия DecisionResult
3. Regression: запазена 100% LONG accuracy

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
-   **Финален backtest** - verify 100% LONG accuracy

## Команди за валидация:

```bash
# След всеки PR:
ruff check src/
python3 -m pytest tests/

# Финална проверка:
python3 run_enhanced_backtest.py
grep "LONG accuracy" data/enhanced_backtest_*.csv
```
