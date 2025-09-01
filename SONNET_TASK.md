# SONNET TASK: Restore 21/21 Perfect LONG System

## 🎯 OBJECTIVE

**Restore the original 21/21 perfect LONG system with 100% accuracy by applying the exact working formulas and configuration from commit 50d56367.**

**Current Status:** 12 signals, 91.7% accuracy ❌
**Target Status:** 21 signals, 100% accuracy ✅

## 📋 TASK BREAKDOWN

### **Task 1: Fix Weekly Tails Formula** 🔧

**File:** `src/bnb_trading/analysis/weekly_tails/analyzer.py`

**Current (BROKEN):**

```python
# Line ~101 in calculate_tail_strength()
tail_strength = lower_wick / body_size  # Too simplistic
```

**Replace with WORKING formula:**

```python
# ATR normalization (14-period, shifted to prevent look-ahead)
atr_w = self._calculate_atr_shifted(history_df, self.atr_period)
tail_ratio = lower_wick / max(atr_w, epsilon)

# Body control factor (smaller body = higher factor)
body_control = min(body_size / max(atr_w, epsilon), 1.0)
body_factor = 1.0 - 0.5 * body_control  # Range: 0.5 to 1.0

# Volume factor (20-period SMA, shifted to prevent look-ahead)
vol_sma = self._calculate_volume_sma_shifted(history_df, self.volume_ma_period)
volume_ratio = np.clip(volume / max(vol_sma, epsilon), 0.5, 2.0)
vol_factor = volume_ratio

# WORKING FORMULA: Final calculation
tail_strength = tail_ratio * body_factor * vol_factor
```

### **Task 2: Fix Configuration Parameters** ⚙️

**File:** `config.toml`

**Replace current values with EXACT working parameters:**

```toml
[signals]
confidence_threshold = 0.25  # CHANGE FROM 0.15

[weekly_tails]
min_tail_strength = 0.35    # CHANGE FROM 0.15
min_tail_ratio = 0.3        # CHANGE FROM 0.5
min_close_pos = 0.2         # CHANGE FROM 0.35
max_body_atr = 2.0          # CHANGE FROM 0.8

[signals.thresholds]
confidence_min = 0.85       # Keep as reference but use 0.25 in decision logic
```

### **Task 3: Fix Decision Logic** 🧠

**File:** `src/bnb_trading/analysis/weekly_tails/analyzer.py` (analyze method)

**Current (BROKEN):**

```python
# Line ~109 in calculate_tail_strength()
if dominant_tail == "lower" and is_bullish and tail_strength >= 0.15:
```

**Replace with WORKING decision logic:**

```python
# Apply ALL validation rules from original perfect system
if (dominant_tail == "lower" and
    is_bullish and
    tail_ratio >= self.min_tail_ratio and  # 0.3
    tail_strength >= self.min_tail_strength and  # 0.35
    (body_size / max(atr_w, epsilon)) <= self.max_body_atr and  # 2.0
    close_pos >= self.min_close_pos):  # 0.2
```

### **Task 4: Fix Confidence Calculation** 📊

**File:** `src/bnb_trading/analysis/weekly_tails/analyzer.py`

**Update confidence normalization:**

```python
# WORKING confidence mapping
confidence = min(tail_strength / 5.0, 1.0)  # Normalize to 0-1
```

### **Task 5: Add Missing Methods** 🔧

**File:** `src/bnb_trading/analysis/weekly_tails/analyzer.py`

**Ensure these methods exist and work correctly:**

```python
def _calculate_atr_shifted(self, df: pd.DataFrame, period: int) -> float:
    # Already exists - verify it uses .shift(1)

def _calculate_volume_sma_shifted(self, df: pd.DataFrame, period: int) -> float:
    # Already exists - verify it uses .shift(1)
```

## ✅ VALIDATION CRITERIA

### **Test Command:**

```bash
PYTHONPATH=src python3 run_enhanced_backtest.py
```

### **Expected Results:**

-   **Signals:** Exactly 21 LONG signals
-   **Accuracy:** 100% (21/21 successful)
-   **Confidence Range:** 0.251 to 0.498
-   **Signal Dates:** Must include 2024-08-05, 2024-08-12, 2024-08-19, 2024-08-26, 2024-09-02, 2024-09-09
-   **Average P&L:** ~19.68% per signal

### **Success Indicators:**

```
🎯 FINAL RESULTS:
📊 LONG Signals: 21
✅ Successful: 21
🎯 Accuracy: 100.0%
```

## 🚨 CRITICAL WARNINGS

### **DO NOT:**

1. **Change the mathematical formulas** - use EXACT formulas from documentation
2. **Modify thresholds creatively** - use EXACT values that achieved perfection
3. **Skip ATR normalization** - critical for different market regimes
4. **Remove volume weighting** - confirms unusual activity
5. **Remove look-ahead prevention** - .shift(1) is mandatory

### **DO:**

1. **Copy exact formulas** from ORIGINAL_PERFECT_SYSTEM_DOCUMENTATION.md
2. **Use exact parameters** that achieved 21/21 success
3. **Test immediately** after each change
4. **Verify signal dates** match original perfect system
5. **Stop when you reach 21/21** - don't over-optimize

## 📚 REFERENCE FILES

-   **ORIGINAL_PERFECT_SYSTEM_DOCUMENTATION.md** - Contains exact working formulas
-   **REGRESSION_ANALYSIS.md** - Shows what broke and how to fix it
-   **data/enhanced_backtest_2025-08-30.csv** - Original perfect results for validation

## 🎯 SUCCESS METRIC

**ONLY SUCCESS CRITERIA:** Achieve exactly 21 LONG signals with 100% accuracy (21/21 successful) using the exact working formulas from the documentation.

**No partial credit. No 95% accuracy. No 20/21 signals. Only perfection counts.**

---

**Priority:** 🔥 **URGENT - CRITICAL REGRESSION**
**Complexity:** 🟡 **MEDIUM** (Copy exact working implementation)
**Timeline:** ⏰ **IMMEDIATE** (Apply proven formulas, don't reinvent)
